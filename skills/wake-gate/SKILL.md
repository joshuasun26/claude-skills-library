---
name: wake-gate
description: Set up a free watcher that checks Gmail, a folder, or a web page on a schedule and only wakes an AI job (Claude, Codex, a script) when something new and real arrives. Use when someone wants automation triggered by incoming email, new files, or a page change without paying for an AI model to poll. Trigger on "wake gate", "watch my inbox for", "only run when", "trigger on new email", "stop polling".
---

# Wake Gate

Let a free script do the waiting, and only spend AI usage when there is something to do.

## Steps
1. Ask what should trigger the job (an email search, a folder, or a web page) and what the job should do when it fires. One watcher per trigger.
2. Copy `watchers.example.json` to `watchers.json` next to `wake_gate.py` and fill in the watchers. Keep Gmail queries narrow: sender, subject words, `newer_than:`.
3. Gmail watchers need a one-time login. Walk the user through the steps in the header of `setup_gmail_oauth.py`, then have THEM run it and click Allow. You cannot click Allow for them. Never print, copy or share the saved login file.
4. Run `python wake_gate.py --config watchers.json --dry-run` and show the user what would fire.
5. Help them schedule it every 5 to 10 minutes (Task Scheduler on Windows, cron on Mac/Linux). See SETUP.md.

## Rules
- Read-only by design. Any `on_hit` job that sends email or texts must draft for approval, not send.
- Never put tokens or passwords in the config, a command line, or chat. Reference files by path.
- If a check logs `invalid_grant`, the Gmail login expired (7-day limit in Google's Testing mode). Re-run setup. The login file is `~/.wake-gate-gmail.json`.
