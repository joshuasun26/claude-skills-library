"""60% context handoff hook for Claude Code. Standard library only; never logs content.

See ../SKILL.md for what it does and how to install it. All personal settings live in
context_gauge_config.json next to this file.
"""
import argparse
from datetime import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile


def number(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and value >= 0)


def usage_total(usage):
    if not isinstance(usage, dict) or not number(usage.get("input_tokens")):
        return None
    values = [usage.get(key, 0) for key in
              ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")]
    return sum(values) if all(number(value) for value in values) else None


def last_usage(path):
    """Stream JSONL, retaining only usage/model from the LAST assistant record."""
    latest = None
    with Path(path).open(encoding="utf-8-sig") as stream:
        for line in stream:
            try:
                record = json.loads(line)
            except (ValueError, TypeError):
                continue
            if isinstance(record, dict) and record.get("type") == "assistant":
                message = record.get("message")
                latest = ((usage_total(message.get("usage")), message.get("model"))
                          if isinstance(message, dict) else (None, None))
    return latest


def config_load(path):
    config = {"threshold_percent": 60, "repeat_percent": 10, "model_windows": {},
              "handoff_dir": str(Path.home() / "handoffs"),
              "main_session_name": "Main",
              "main_session_title_regex": r"^Main \d{1,2}-\d{1,2}\b",
              "all_sessions_are_main": False,
              "sessions_glob": os.path.expandvars(
                  r"%APPDATA%\Claude\claude-code-sessions\*\*\local_*.json")}
    if path is None:
        candidate = Path(__file__).resolve().with_name("context_gauge_config.json")
        path = candidate if candidate.exists() else None
    if path is not None:
        with Path(path).open(encoding="utf-8-sig") as stream:
            supplied = json.load(stream)
        if not isinstance(supplied, dict):
            raise ValueError("config")
        config.update(supplied)
    threshold, repeat = config["threshold_percent"], config["repeat_percent"]
    windows = config["model_windows"]
    if (not number(threshold) or not 0 < threshold <= 100 or
            not number(repeat) or repeat <= 0 or not isinstance(windows, dict) or
            any(not isinstance(key, str) or not number(value) or value <= 0
                for key, value in windows.items())):
        raise ValueError("config")
    return config


def window_for(model, config, total=0):
    if not isinstance(model, str) or not model.strip():
        return None
    default = (1_000_000 if model.endswith("[1m]") or re.match(r"claude-(opus|sonnet|fable)-5", model)
               else 200_000)
    window = config["model_windows"].get(model, default)
    # A too-small window guess on a 1M-token model would show a false high percent.
    return 1_000_000 if total > window else window


CONFIG = {}


def session_title(cli_session):
    """Desktop-app title for a CLI session id ('' when unknown). Reads metadata only."""
    import glob
    for name in glob.glob(CONFIG.get("sessions_glob") or ""):
        try:
            with open(name, encoding="utf-8") as stream:
                data = json.load(stream)
        except (OSError, ValueError):
            continue
        if isinstance(data, dict) and data.get("cliSessionId") == cli_session:
            return str(data.get("title") or "")
    return ""


def is_chief_of_staff(title):
    """True for the main session this rule protects (set by name in the config)."""
    if CONFIG.get("all_sessions_are_main"):
        return True
    return bool(re.match(CONFIG.get("main_session_title_regex") or r"^Main ", title or ""))


def handoff_written_since(timestamp):
    try:
        folder = Path(CONFIG.get("handoff_dir") or Path.home() / "handoffs")
        return any(f.stat().st_mtime >= timestamp for f in folder.glob("HANDOFF-*.md"))
    except OSError:
        return False


def state_name(session):
    if not isinstance(session, str) or not session.strip() or len(session) > 512:
        return None
    clean = re.sub(r"[^A-Za-z0-9_-]", "_", session)[:100]
    reserved = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
                *(f"LPT{i}" for i in range(1, 10))}
    if clean == session and clean.upper() not in reserved:
        return clean + ".json"
    # Prefix also prevents Windows device names such as CON from becoming filenames.
    digest = hashlib.sha256(session.encode("utf-8")).hexdigest()[:16]
    return "session-" + clean + "-" + digest + ".json"


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".context-", suffix=".tmp", delete=False) as stream:
            name = stream.name
            json.dump(data, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if name is not None and os.path.exists(name):
            os.unlink(name)


def reminder(percent, now=None):
    now = now or datetime.now().astimezone()
    hour = now.hour % 12 or 12
    part = "AM" if now.hour < 12 else "PM"
    folder = CONFIG.get("handoff_dir") or str(Path.home() / "handoffs")
    name = CONFIG.get("main_session_name") or "Main"
    return (
        f"CONTEXT AT {percent:.0f}% (60% handoff rule). Do this NOW, before other work: "
        f"1) Write {folder}/HANDOFF-{now:%Y-%m-%d}-{now:%H%M}.md: work in flight with file paths, "
        "background jobs and where their results land, scheduled/cron jobs to recreate with their full "
        "prompts, decisions waiting on the user, anything sent since the last handoff, rules learned. "
        f"2) Start a fresh session (start_session, fresh context) titled '{name} {now.month}-{now.day} "
        f"{hour}{part}'. Its brief: read that handoff by absolute path, recreate the cron jobs, continue the work. "
        "3) If it started: pin the new session and unpin this one. "
        "4) If starting a session is refused (for example from a phone), create a one-time scheduled task "
        "one minute from now with the same brief. "
        "5) Tell the user in one line, with the link. Never ask them to start it. "
        "This repeats every turn until a HANDOFF file is written."
    )


def hook(payload, config, state_dir, stop_mode=False):
    if not isinstance(payload, dict):
        return None
    name = state_name(payload.get("session_id"))
    transcript = payload.get("transcript_path")
    if name is None or not isinstance(transcript, str) or not transcript:
        return None
    latest = last_usage(transcript)
    if latest is None or latest[0] is None:
        return None
    total, model = latest
    window = window_for(model, config, total)
    if window is None:
        return None
    percent = total * 100 / window
    threshold, repeat = config["threshold_percent"], config["repeat_percent"]
    path = Path(state_dir) / name
    previous, state = None, {}
    if path.exists():
        with path.open(encoding="utf-8") as stream:
            state = json.load(stream)
        if not isinstance(state, dict):
            raise ValueError("state")
        previous = state.get("last_warned_bucket")
        if previous is not None and not number(previous):
            raise ValueError("state")
        # A model switch, window change or compaction below threshold re-arms the gauge.
        if (state.get("context_window") != window or state.get("model") != model
                or percent < threshold):
            previous = None
    bucket = (threshold + math.floor((percent - threshold) / repeat) * repeat
              if percent >= threshold else None)
    title = state.get("title") or session_title(payload.get("session_id"))
    cos = is_chief_of_staff(title)
    crossed_at = state.get("crossed_at") if previous is not None else None
    if bucket is not None and crossed_at is None:
        crossed_at = datetime.now().timestamp()
    done = bool(cos and crossed_at and handoff_written_since(crossed_at))
    # Chief-of-staff sessions get the reminder every turn until a handoff file exists.
    notify = bucket is not None and ((cos and not done) or previous is None or previous < bucket)
    # Persist metrics and the session title, never content or paths.
    atomic_write(path, {"current_tokens": total, "model": model, "context_window": window,
                        "percent": percent, "title": title, "chief_of_staff": cos,
                        "crossed_at": crossed_at, "handoff_done": done,
                        "last_warned_bucket": bucket if notify else previous})
    if stop_mode:
        # Stop hook: hold a CoS turn open once so the handoff happens before it goes idle.
        if not cos or done or bucket is None or payload.get("stop_hook_active"):
            return None
        return {"decision": "block", "reason": reminder(percent)}
    if not notify:
        return None
    return {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                   "additionalContext": reminder(percent)}}


def statusline(payload):
    if not isinstance(payload, dict):
        return None
    context = payload.get("context_window")
    if not isinstance(context, dict):
        return None
    percent = context.get("used_percentage")
    if not number(percent):
        total = usage_total(context.get("current_usage"))
        window = context.get("context_window_size")
        if total is None or not number(window) or window <= 0:
            return None
        percent = total * 100 / window
    return f"Context {percent:.0f}%"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--state-dir", type=Path, default=Path(__file__).resolve().parent / "context_state")
    parser.add_argument("--statusline", action="store_true")
    parser.add_argument("--stop", action="store_true", help="Stop-hook mode for overdue CoS handoffs")
    args = parser.parse_args(argv)
    try:
        payload = json.load(sys.stdin)
        if args.statusline:
            result = statusline(payload)  # No config or state reads/writes in this mode.
            if result is not None:
                print(result)
        else:
            CONFIG.update(config_load(args.config))
            result = hook(payload, CONFIG, args.state_dir, stop_mode=args.stop)
            if result is not None:
                print(json.dumps(result))
    except (OSError, ValueError, TypeError, OverflowError):
        print("context_gauge: skipped unavailable or invalid input/state", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
