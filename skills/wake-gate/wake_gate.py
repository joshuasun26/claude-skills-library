#!/usr/bin/env python3
"""wake_gate.py - only wake the AI when something real arrives.

A free script does the waiting. Your AI job (Claude Code, Codex, any script) runs only
when a watcher finds something new. No model is called on a check that finds nothing.

Watchers live in a JSON config (see watchers.example.json). Three kinds:
  gmail   - a Gmail search query (same syntax as the Gmail search box). Read-only.
  folder  - new files landing in a folder (e.g. a scanner, a Downloads drop, a synced Drive folder).
  url     - a public web page changes, or starts containing a phrase you care about.

Usage:
  python wake_gate.py --config watchers.json            # run every enabled watcher once
  python wake_gate.py --config watchers.json --dry-run  # show what would fire, run nothing
  python wake_gate.py --config watchers.json --only invoices

Schedule it every 5-10 minutes with Task Scheduler (Windows) or cron (Mac/Linux).

When a watcher fires, its "on_hit" command runs with these environment variables:
  WAKE_GATE_NAME   the watcher name
  WAKE_GATE_COUNT  how many new items
  WAKE_GATE_ITEMS  path to a JSON file listing the new items (id, title, detail)
If the command fails, the items are NOT marked handled, so the next run retries.
Each watcher remembers what it already handled (~/.wake-gate/<name>.json), so one item fires once.

Standard library only. Python 3.9+.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

STATE_DIR = Path.home() / ".wake-gate"
DEFAULT_GMAIL_CREDS = Path.home() / ".wake-gate-gmail.json"


# ---------- watchers: each returns a list of {"id", "title", "detail"} ----------

def check_gmail(w: dict) -> list[dict]:
    creds_path = Path(os.path.expanduser(w.get("creds", str(DEFAULT_GMAIL_CREDS))))
    c = json.loads(creds_path.read_text(encoding="utf-8"))
    body = urllib.parse.urlencode({
        "client_id": c["client_id"], "client_secret": c["client_secret"],
        "refresh_token": c["refresh_token"], "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request(c.get("token_uri", "https://oauth2.googleapis.com/token"), data=body)
    with urllib.request.urlopen(req, timeout=30) as r:
        token = json.loads(r.read())["access_token"]
    hdr = {"Authorization": f"Bearer {token}"}
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages?" + urllib.parse.urlencode(
        {"q": w["query"], "maxResults": int(w.get("max", 20))})
    with urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=30) as r:
        ids = [m["id"] for m in json.loads(r.read()).get("messages", [])]
    out = []
    for mid in ids:
        u = (f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{mid}?format=metadata"
             "&metadataHeaders=From&metadataHeaders=Subject")
        with urllib.request.urlopen(urllib.request.Request(u, headers=hdr), timeout=30) as r:
            m = json.loads(r.read())
        h = {x["name"]: x["value"] for x in m.get("payload", {}).get("headers", [])}
        out.append({"id": mid, "title": h.get("Subject", ""), "detail": h.get("From", "")})
    return out


def check_folder(w: dict) -> list[dict]:
    folder = Path(os.path.expanduser(w["path"]))
    pattern = w.get("pattern", "*")
    out = []
    for p in sorted(folder.iterdir()):
        if p.is_file() and fnmatch.fnmatch(p.name.lower(), pattern.lower()):
            st = p.stat()
            out.append({"id": f"{p.name}|{st.st_size}|{int(st.st_mtime)}",
                        "title": p.name, "detail": str(p)})
    return out


def check_url(w: dict) -> list[dict]:
    req = urllib.request.Request(w["url"], headers={"User-Agent": "wake-gate/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        text = r.read().decode("utf-8", errors="replace")
    phrase = w.get("contains")
    if phrase:
        if phrase.lower() not in text.lower():
            return []
        return [{"id": f"contains:{phrase}", "title": f"Page now contains '{phrase}'", "detail": w["url"]}]
    digest = hashlib.sha256(text.encode()).hexdigest()[:16]
    return [{"id": f"hash:{digest}", "title": "Page changed", "detail": w["url"]}]


CHECKS = {"gmail": check_gmail, "folder": check_folder, "url": check_url}


# ---------- plumbing ----------

def in_active_hours(w: dict) -> bool:
    hours = w.get("active_hours")  # e.g. "08-21"
    if not hours:
        return True
    start, end = (int(x) for x in hours.split("-"))
    return start <= dt.datetime.now().hour < end


def run_watcher(w: dict, dry_run: bool) -> int:
    name = w["name"]
    if not in_active_hours(w):
        print(f"[{name}] outside active hours, skipped")
        return 0
    state_file = STATE_DIR / f"{name}.json"
    first_run = not state_file.exists()
    seen = set(json.loads(state_file.read_text())["seen"]) if not first_run else set()

    try:
        items = CHECKS[w["type"]](w)
    except KeyError:
        print(f"[{name}] unknown type '{w.get('type')}' (use gmail, folder or url)", file=sys.stderr)
        return 2
    except Exception as e:  # expired login, network, missing folder
        print(f"[{name}] check failed: {e}", file=sys.stderr)
        return 2

    new = [i for i in items if i["id"] not in seen]
    # First run records what is already there as the baseline and does not fire, so an
    # existing backlog never triggers a flood. Set "fire_on_first_run": true to override.
    new_baseline = first_run and not w.get("fire_on_first_run", False) and not (
        w["type"] == "url" and w.get("contains"))

    if not new or new_baseline:
        print(f"[{name}] nothing new" + (" (baseline saved)" if new_baseline else ""))
        if not dry_run:
            seen.update(i["id"] for i in items)
            state_file.write_text(json.dumps({"seen": sorted(seen)[-2000:]}))
        return 0

    for i in new:
        print(f"[{name}] NEW | {i['title']} | {i['detail']}")
    if dry_run:
        print(f"[{name}] dry run: would run on_hit for {len(new)} item(s)")
        return 0

    cmd = w.get("on_hit")
    if cmd:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(new, f, indent=2)
            items_path = f.name
        env = dict(os.environ, WAKE_GATE_NAME=name, WAKE_GATE_COUNT=str(len(new)), WAKE_GATE_ITEMS=items_path)
        # Same command works on Windows and Mac/Linux: expand ~/ and the items variable here.
        cmd = cmd.replace("~/", str(Path.home()).replace("\\", "/") + "/")
        for token in ("$WAKE_GATE_ITEMS", "%WAKE_GATE_ITEMS%"):
            cmd = cmd.replace(token, items_path)
        rc = subprocess.call(cmd, shell=True, env=env)
        if rc != 0:
            print(f"[{name}] on_hit failed (rc={rc}); will retry next run", file=sys.stderr)
            return rc
    seen.update(i["id"] for i in new)
    state_file.write_text(json.dumps({"seen": sorted(seen)[-2000:]}))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Only wake the AI when something real arrives.")
    ap.add_argument("--config", required=True, type=Path)
    ap.add_argument("--only", help="run just this watcher name")
    ap.add_argument("--dry-run", action="store_true", help="show what would fire; run nothing, save nothing")
    a = ap.parse_args()

    cfg = json.loads(a.config.read_text(encoding="utf-8"))
    STATE_DIR.mkdir(exist_ok=True)
    worst = 0
    for w in cfg.get("watchers", []):
        if not w.get("enabled", True) or (a.only and w["name"] != a.only):
            continue
        worst = max(worst, run_watcher(w, a.dry_run))
    return worst


if __name__ == "__main__":
    sys.exit(main())
