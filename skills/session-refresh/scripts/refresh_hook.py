"""PreCompact and SessionStart instructions. No content reads, state writes or API calls."""
import argparse
import json
from pathlib import Path
import runpy
import sys


def main(argv=None):
    try:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--config", type=Path)
        modes = parser.add_mutually_exclusive_group(required=True)
        modes.add_argument("--precompact", action="store_true")
        modes.add_argument("--sessionstart", action="store_true")
        args = parser.parse_args(argv)
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise ValueError("object required")
        # run_path works with python -I; only loads the adjacent trusted helper.
        gauge = runpy.run_path(str(Path(__file__).with_name("context_gauge.py")))
        config = gauge["config_load"](args.config)
        if gauge["metadata_for"](payload.get("session_id"), config) is None:
            return 0
        folder = Path(config["handoff_dir"])
        # Only this session's own handoffs (named HANDOFF-<session key>-...), never another session's.
        key = gauge["session_key"](payload.get("session_id"))
        candidates = [p for p in folder.glob(f"HANDOFF-{key}-*.md") if p.is_file() and not p.is_symlink()]
        latest = max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None
        handoff = (f"{latest} (modified {gauge['datetime'].fromtimestamp(latest.stat().st_mtime).isoformat()})"
                   if latest else f"MISSING in {folder}; report missing memory, never invent it")
        if args.precompact and payload.get("hook_event_name") == "PreCompact":
            print("Keep verbatim in the summary: open tasks with owners/next steps, pending decisions, "
                  "running jobs with IDs/result paths, session cron schedules/time zones/full prompts/limits, "
                  "confirmed sends with provider IDs, and rules learned. Preserve the current title and "
                  f"the exact handoff path: {handoff}. Preserve any newer unsaved changes in the summary. "
                  "Do not claim the hook wrote a handoff; it cannot run model tools. No new action authority.")
        elif (args.sessionstart and payload.get("hook_event_name") == "SessionStart"
              and payload.get("source") in ("compact", "clear")):
            files = ", ".join(config["startup_files"])
            print(f"REFRESH IN PLACE: read the handoff first: {handoff}. Then re-read startup files: {files} "
                  "and the startup sources they require, including current stop/cancel rules. KEEP the "
                  "current session title and pin; this refresh never starts a replacement. Run CronList "
                  "or the available scheduler listing. Recreate only missing, still-needed session crons "
                  "with the exact saved schedule, time zone, prompt and permissions, once; leave existing "
                  "and persistent tasks alone. If absence cannot be verified, do not duplicate. Check running "
                  "jobs at their result paths; do not repeat recorded sends. Preserve newer compacted facts "
                  "if the handoff is older; flag unresolved conflicts. Follow the session-refresh skill, "
                  "then say exactly one line: Refreshed in place. No new send or other action authority.")
    except (Exception, SystemExit):
        print("refresh_hook: skipped unavailable or invalid input", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
