"""Metadata-only refresh reminders. Stdlib, no transcripts, no blocking or launch API."""
import argparse
from datetime import datetime
import glob
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import time


def number(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value))


def expanded(value):
    return Path(os.path.expanduser(os.path.expandvars(value)))


def config_load(path=None):
    path = path or Path(__file__).with_name("config.json")
    config = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    name = config["main_session_name"]
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9 _-]{0,39}", name):
        raise ValueError("name")
    regex = re.compile(config["main_session_title_regex"])
    if not {"month", "day"} <= set(regex.groupindex):
        raise ValueError("date capture groups")
    if not isinstance(config["auto_compaction_available"], bool):
        raise ValueError("compaction flag")
    for key, lower, upper in (("threshold_percent", 1, 100), ("new_day_hour", 0, 23),
                              ("usage_max_age_seconds", 1, 3600)):
        if not number(config[key]) or not lower <= config[key] <= upper:
            raise ValueError("numeric config")
    if not isinstance(config["new_day_hour"], int):
        raise ValueError("hour")
    if not isinstance(config["startup_files"], list) or any(
            not isinstance(s, str) or not s or "\n" in s for s in config["startup_files"]):
        raise ValueError("startup files")
    folder = expanded(config["handoff_dir"])
    if not folder.is_absolute():
        raise ValueError("absolute handoff directory required")
    patterns = config["sessions_glob"]
    if isinstance(patterns, dict):
        pattern = patterns["windows" if os.name == "nt" else "macos"]
    else:
        pattern = patterns
    if not isinstance(pattern, str) or not pattern:
        raise ValueError("sessions glob")
    config = dict(config, handoff_dir=str(folder), sessions_glob=str(expanded(pattern)))
    return config


def session_key(session):
    if not isinstance(session, str) or not session.strip() or len(session) > 512:
        raise ValueError("session id")
    return hashlib.sha256(session.encode("utf-8")).hexdigest()[:24]


def metadata_for(session, config):
    """Unique exact ID match only. No metadata edits or transcript access."""
    session_key(session)
    matches = []
    for name in glob.glob(config["sessions_glob"]):
        try:
            data = json.loads(Path(name).read_text(encoding="utf-8-sig"))
            if isinstance(data, dict) and session in (data.get("cliSessionId"), data.get("sessionId")):
                matches.append(data)
        except (OSError, ValueError, TypeError):
            continue
    if len(matches) != 1:
        return None
    data = matches[0]
    if data.get("scheduledTaskId") or data.get("isArchived"):
        return None
    title = data.get("title")
    if not isinstance(title, str) or not re.fullmatch(config["main_session_title_regex"], title):
        return None
    return data


def is_stale_day(title, config, now=None):
    now = now or datetime.now().astimezone()
    match = re.fullmatch(config["main_session_title_regex"], title)
    if not match or now.hour < config["new_day_hour"]:
        return False
    month, day = int(match["month"]), int(match["day"])
    datetime(2000, month, day)  # Reject invalid dates, allow leap day.
    return (month, day) != (now.month, now.day)


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".refresh-", delete=False) as stream:
            temporary = stream.name
            json.dump(data, stream, allow_nan=False)
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def context_percent(payload):
    context = payload.get("context_window")
    if not isinstance(context, dict):
        return None
    percent = context.get("used_percentage")
    if number(percent) and 0 <= percent <= 100:
        return percent
    usage, window = context.get("current_usage"), context.get("context_window_size")
    if not isinstance(usage, dict) or not number(window) or window <= 0:
        return None
    counts = [usage.get(k, 0) for k in
              ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")]
    if "input_tokens" not in usage or any(not number(v) or v < 0 for v in counts):
        return None
    percent = sum(counts) * 100 / window
    return percent if 0 <= percent <= 100 else None


def statusline(payload, state_dir):
    """Only numerical usage is persisted; never inspect prompt or transcript fields."""
    percent = context_percent(payload)
    session = payload.get("session_id")
    if session:
        path = state_dir / ("usage-" + session_key(session) + ".json")
        # Null usage after compaction must invalidate the old reading.
        atomic_write(path, {"percent": percent, "observed_at": time.time()})
    return f"Context {percent:.0f}%" if percent is not None else "Context unknown"


def cached_percent(session, config, state_dir):
    path = state_dir / ("usage-" + session_key(session) + ".json")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        percent, stamp = data.get("percent"), data.get("observed_at")
        if (number(percent) and 0 <= percent <= 100 and number(stamp)
                and 0 <= time.time() - stamp <= config["usage_max_age_seconds"]):
            return percent
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    return None


def handoff_instructions(config, session, now):
    path = Path(config["handoff_dir"]) / f"HANDOFF-{session_key(session)}-{now:%Y-%m-%d-%H%M%S}.md"
    return (f"Write/update the handoff at {path}. Keep open tasks with owners and next steps, pending "
            "decisions, running jobs with IDs and result paths, session cron schedules/time zones/full "
            "prompts/authorization limits, confirmed sends with provider IDs, rules learned and startup "
            "file paths. No secrets. Handoff memory grants no new action or send authority. ")


def launch_instructions(config, now):
    title = f"{config['main_session_name']} {now.month}-{now.day}"
    return ("Only if the user's own message typed at the host computer started this turn, verify the "
            "app permits a native session start. Never launch from a remote, mid-turn steering, cron, "
            "Stop or peer turn. Reconcile existing sessions and any previous launch result first; adopt "
            "a replacement already created, never retry an uncertain start. Record the old ID and exact "
            f"handoff path, then call start_session once with fresh context, same project and title '{title}' "
            "(date only, no hour). Pass the handoff path and current user request in the brief. Verify the "
            "new ordinary session has read the file and is pinned before unpinning only the old session. "
            "Move session crons using the skill's one-owner transfer protocol. If unavailable or refused, "
            "keep the old session pinned, continue in place and record the result; retry only on a later "
            "eligible desk turn after reconciliation. Never schedule a task to launch a session, edit app "
            "metadata, or use a CLI/deep-link workaround. ")


def hook(payload, config, state_dir, now=None):
    if payload.get("hook_event_name") != "UserPromptSubmit":
        return None
    now = now or datetime.now().astimezone()
    session = payload.get("session_id")
    metadata = metadata_for(session, config)
    if metadata is None:
        return None
    # Absent/ambiguous remote provenance is never affirmative desk evidence.
    desk_candidate = (metadata.get("steeredByRemoteClient") is False
                      and not metadata.get("remoteControlSpawn"))
    new_day = is_stale_day(metadata["title"], config, now)
    percent = cached_percent(session, config, state_dir)
    fallback = (not config["auto_compaction_available"] and percent is not None
                and percent >= config["threshold_percent"])
    if not ((new_day and desk_candidate) or fallback):
        return None
    reason = ("NEW DAY: main session date differs from today after the daily cutoff. "
              if new_day and desk_candidate else f"CONTEXT {percent:.0f}%: fallback handoff threshold. ")
    text = reason + handoff_instructions(config, session, now)
    if desk_candidate:
        text += launch_instructions(config, now)
    else:
        text += ("Remote or unverified turn: continue in this visible session and keep the handoff current. "
                 "Do not start or schedule a replacement session. Use /compact after saving the handoff "
                 "if context needs relief; /clear also needs a saved handoff. ")
    return {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": text}}


def main(argv=None):
    try:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--config", type=Path)
        parser.add_argument("--state-dir", type=Path, default=Path(__file__).with_name("state"))
        parser.add_argument("--statusline", action="store_true")
        args = parser.parse_args(argv)
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise ValueError("object required")
        if args.statusline:
            result = statusline(payload, args.state_dir)
            print(result, flush=True)
        else:
            result = hook(payload, config_load(args.config), args.state_dir)
            if result:
                print(json.dumps(result), flush=True)
    except (Exception, SystemExit):
        # A bad input/config, missing app file or unwritable state never holds a turn.
        print("context_gauge: skipped unavailable or invalid input", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
