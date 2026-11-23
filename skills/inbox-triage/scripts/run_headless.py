#!/usr/bin/env python3
"""Run the triage headless with the Claude CLI, on a fixed model and effort, from an OS
scheduler (Windows Task Scheduler, cron, launchd). Use this instead of an app-scheduled task
when you need a guaranteed model/effort or the app scheduler is unreliable: app scheduled
tasks cannot pin a model, and they stop firing when the desktop app hangs.

  python run_headless.py --config ~/.inbox-triage/config.json [--prompt-file FILE] [--dry-run]

Reads config["run"]: model, effort, timeout_minutes, allowed_tools, disallowed_tools,
log_dir, cwd. A lock file prevents overlapping runs. Metered API keys are stripped from the
environment so the run bills the signed-in subscription.
"""
import argparse, datetime as dt, json, os, shutil, subprocess, sys

DEFAULT_PROMPT = ("Run the inbox-triage skill now, end to end, following its SKILL.md exactly. "
                  "Drafts only. Never send, forward or reply. Persist state before any notice.")

DEFAULT_ALLOWED = ["Read", "Write", "Glob", "Grep", "Bash(python *)", "Skill",
                   "mcp__claude_ai_Gmail__search_threads", "mcp__claude_ai_Gmail__get_thread",
                   "mcp__claude_ai_Gmail__list_drafts", "mcp__claude_ai_Gmail__create_draft"]
DEFAULT_DISALLOWED = ["mcp__claude_ai_Gmail__send_message", "mcp__claude_ai_Gmail__reply",
                      "mcp__claude_ai_Gmail__forward", "mcp__claude_ai_Gmail__trash_thread",
                      "mcp__claude_ai_Gmail__trash_message", "mcp__claude_ai_Gmail__delete_draft",
                      # add the send tools of any other mail connector you use here
                      ]


def find_claude():
    for p in (shutil.which("claude"), os.path.expandvars(r"%APPDATA%\npm\claude.cmd"),
              os.path.expanduser("~/.local/bin/claude")):
        if p and os.path.exists(p):
            return p
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--prompt-file")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    cfg = json.load(open(os.path.expanduser(a.config), encoding="utf-8"))
    run = cfg.get("run", {})
    log_dir = os.path.expanduser(run.get("log_dir", "~/.inbox-triage/runs"))
    os.makedirs(log_dir, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d-%H%M")
    lock = os.path.join(log_dir, "run.lock")
    if os.path.exists(lock):
        age_min = (dt.datetime.now().timestamp() - os.path.getmtime(lock)) / 60
        if age_min < run.get("timeout_minutes", 25) + 5:
            print("another run holds the lock; exiting")
            return 3  # non-zero so a Wake Gate trigger retries next time
        os.remove(lock)  # stale lock from a crashed run

    prompt = open(a.prompt_file, encoding="utf-8").read() if a.prompt_file else DEFAULT_PROMPT
    claude = find_claude()
    cmd = [claude or "claude", "-p", "--output-format", "json",
           "--model", run.get("model", "claude-opus-5-5"),
           "--effort", run.get("effort", "medium"),
           "--allowedTools", ",".join(run.get("allowed_tools", DEFAULT_ALLOWED)),
           "--disallowedTools", ",".join(run.get("disallowed_tools", DEFAULT_DISALLOWED))]
    if a.dry_run or not claude:
        print(("CLI NOT FOUND. " if not claude else "") + " ".join(cmd[:8]) + " ...")
        return 0 if claude else 2

    env = dict(os.environ, PYTHONUTF8="1")
    for k in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"):
        env.pop(k, None)
    open(lock, "w").write(stamp)
    t0 = dt.datetime.now()
    try:
        res = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8",
                             errors="replace", env=env,
                             cwd=os.path.expanduser(run.get("cwd", "~")),
                             timeout=60 * run.get("timeout_minutes", 25))
        out, rc = res.stdout or "", res.returncode
    except subprocess.TimeoutExpired:
        out, rc = "TIMEOUT", 124
    finally:
        os.remove(lock)
    secs = int((dt.datetime.now() - t0).total_seconds())
    with open(os.path.join(log_dir, f"{stamp}-result.json"), "w", encoding="utf-8") as f:
        f.write(out)
    with open(os.path.join(log_dir, "runs.log"), "a", encoding="utf-8") as f:
        f.write(f"{stamp} rc={rc} secs={secs} model={run.get('model')} effort={run.get('effort')}\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
