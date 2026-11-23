---
name: session-handoff-60
description: Keeps your main Claude Code session from running out of memory. When the main session's context reaches 60%, Claude writes a handoff file, starts a fresh session that picks up where it left off, pins the new one and unpins the old one. Use when someone says "set up the 60% handoff", "auto-restart my main session", "my session keeps running out of context", "install the handoff skill", or when a 60% CONTEXT reminder appears.
---

# 60% session handoff

## The problem it solves
A long Claude Code session slowly fills its context window. Past about 60%, answers get slower, costlier and less sharp, and at 100% the session compacts and forgets details. People keep one "main" session open all day (a chief-of-staff or command-center chat), so this hits them the hardest.

## What it does
1. A small Python hook checks how full the session's context is on every message (free, no AI call).
2. At 60% in your **main** session, it tells Claude to stop and do the handoff first:
   - write `HANDOFF-YYYY-MM-DD-HHMM.md`: work in flight, background jobs and where results land, scheduled jobs to recreate, decisions waiting on you, what was sent, rules learned
   - start a fresh session named like `Main 11-7 2PM` that reads that file and carries on
   - pin the new session and unpin the old one
   - if starting a session is blocked (for example from a phone), schedule a one-time task a minute out that opens it
3. A Stop hook holds the turn open once, so the session cannot go idle without doing the handoff.
4. A status line shows `Context 42%` at the bottom of the screen.

Other sessions only get a reminder every 10 points past 60%. Nothing is ever deleted.

## Install (about 5 minutes)
Needs Python 3.9+ and the Claude Code desktop app (for session start/pin tools).

1. Copy `scripts/context_gauge.py` and `scripts/context_gauge_config.json` to `~/.claude/hooks/`.
2. Edit `context_gauge_config.json`:
   - `handoff_dir`: a folder for handoff files (create it).
   - `main_session_name`: what you call your main session, for example `Main` or `Desk`.
   - `main_session_title_regex`: matches that name plus a date, for example `^Desk \\d{1,2}-\\d{1,2}\\b`.
   - Set `all_sessions_are_main` to `true` if you want every session handled.
   - On Mac, add `"sessions_glob": "~/Library/Application Support/Claude/claude-code-sessions/*/*/local_*.json"` (expand `~` to your home path). Without the right path the hook cannot read session titles, so set `all_sessions_are_main` to `true`.
3. Add this to `~/.claude/settings.json` (use your own Python path):
```json
{
  "hooks": {
    "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "python -I -B ~/.claude/hooks/context_gauge.py", "timeout": 15}]}],
    "Stop": [{"hooks": [{"type": "command", "command": "python -I -B ~/.claude/hooks/context_gauge.py --stop", "timeout": 15}]}]
  },
  "statusLine": {"type": "command", "command": "python -I -B ~/.claude/hooks/context_gauge.py --statusline"}
}
```
4. Name your main session to match (for example `Main 11-7 9AM`) and pin it.
5. Test: send any message. The status line should show `Context N%`.

## When the reminder fires (instructions for Claude)
Do the five steps in the reminder before anything else, in order. Write the handoff file first, so nothing is lost if the start fails. Session-only cron jobs die with the old session, so copy their full prompts into the handoff and recreate them in the new session. Tell the user one line with the new session's link. Do not ask them to start it.

## Safety
- Standard library only. It reads token counts and session titles, never message content, and writes only small state files next to the script.
- If anything goes wrong it fails open: it prints a short note and lets your message through.
