---
name: session-refresh
description: Set up or use in-place Claude Code context refresh, restore a main session after compact or clear, and start one fresh daily desktop session. Use for upgrades from session-handoff-60 or older handoff setups, context refresh reminders, or requests to install this workflow.
---

# Session refresh

Keep one visible main session through the day. Claude Code summarizes its context at about 30% of the window, then re-reads your saved handoff. On your first message that starts a turn at the host computer after 4 AM, yesterday's main session hands off to today's. New sessions use date-only titles such as `Main 11-19`. Refreshing in place keeps the existing title.

Context percentage measures this conversation's working memory. It is separate from your plan's usage allowance. The thresholds below are chosen margins, with no promised savings or guarantee that summaries preserve every detail.

## Install in about five minutes

Needs Python 3.9+ and Claude Code. Automatic daily starts and pins require the Desktop app's supported session tools. Terminal-only sessions can refresh in place; they do not get automatic sidebar starts or pins.

1. Copy this `session-refresh` folder into your skills folder. Windows: `%USERPROFILE%\.claude\skills\session-refresh\`. Mac: `~/.claude/skills/session-refresh/`. Keep both scripts and `config.json` together under `scripts/`.
2. Tell Claude: **"Read session-refresh/SKILL.md and the supplied INSTALL-PROMPT.md. Upgrade my old handoff setup. Back up settings, show me the settings diff before writing, and keep unrelated hooks."** If the installer prompt is beside the downloaded folder, give its full path. That prompt includes settings examples for both systems.
3. Set `scripts/config.json`: your main session name and date regex, a dedicated absolute handoff directory, startup files, and your Desktop sessions glob. Defaults use `Main`, `~/.claude/handoffs/main`, and Windows/Mac glob examples. `~` and environment variables expand inside config; command paths in settings must be fully resolved. Check the actual metadata location on your installation. Keep named regex groups `month` and `day`. For `Desk`, use `^Desk (?P<month>\d{1,2})-(?P<day>\d{1,2})$`.
4. For a verified 1,000,000-token window, set `modelSettings.<actual-model-id>.autoCompactWindow` to `300000`. For another window, start with `0.30 × window size`, then check the installed version's allowed range and your startup context size. A 200k window gives 60k mathematically, which falls below the documented 100k setting minimum. Use a supported minimum if useful or use the fallback below. Never claim an unsupported value is installed. Overrides and higher-priority settings can change the effective value. This setting applies to every session of that model within its settings scope, not just the main session.
5. Name and pin the main session, for example `Main 11-19`. Tell it once: **"Use session-refresh. Keep my handoff current, refresh in place during the day, and start today's dated main session on my first eligible desk turn after 4 AM. Keep the Context N% status line."** Save an initial handoff and test `/compact` in a scratch session before relying on automatic compaction. Save before trying `/clear`.

## During the day: instructions for Claude

Keep a compact handoff current after meaningful progress and before deliberate `/compact` or `/clear`. Use the configured directory and a file name `HANDOFF-<source-session-hash>-YYYY-MM-DD-HHMMSS.md`; the gauge's reminder supplies an exact path when it runs. Store the source session ID inside the handoff so a future transfer can identify its owner. This directory is dedicated to this main workflow, never a mix of unrelated projects.

Keep these items, with exact identifiers and paths where available:

- Open tasks, each owner, state and next step.
- Pending decisions or approvals, with the user's exact constraints.
- Running jobs, each ID, owner and result path. Refresh does not cancel them.
- Session crons: full prompt, schedule, time zone, next due time, ID, owner, authorization limits and expiry. List persistent schedules separately.
- Confirmed sends or completed external actions, with provider IDs; mark uncertain outcomes as unconfirmed and reconcile them before retrying.
- Rules learned, startup file paths, current session ID/title, and one concrete next step.

Keep secrets out. Use facts and paths, not transcript dumps. A hook cannot ask the model to write a handoff before compaction begins. The PreCompact hook supplies preservation instructions to the summarizer; it does not create the file. Keep unsaved updates verbatim in the compaction summary too.

After compact or clear, the SessionStart hook tells you to re-read the saved handoff and startup files, keep the title and pin, check running jobs, list crons, and recreate only missing session crons once. Check schedule, prompt, owner, time zone, next run, expiry and permission limits. Leave persistent schedules and existing crons alone. If you cannot verify absence, do not create another copy. A stale handoff must not override newer summary facts or current stop orders. Report missing memory without guessing. When restored, say one line: **Refreshed in place.**

Do not start another session because context reached 50% when `auto_compaction_available` is true. Remote and phone turns stay in place, including across dates, until an eligible message begins a turn at the host computer.

## Today's fresh session

The UserPromptSubmit gauge checks a uniquely matched, ordinary main-session metadata record. After 4 AM local time, a title date different from today prompts a daily handoff on a possible desk turn. It needs `steeredByRemoteClient: false` explicitly; missing metadata or unknown remote state never counts as proof of a desk turn. These Desktop fields and file locations can vary. Claude must still verify the user's own locally typed message began the current turn, rather than arriving mid-turn or through a peer, cron or other automation. The app's eligibility check is authoritative.

1. Save the handoff and current request. Record the source session ID and any replacement ID. Check the live session list and any earlier start result so you can adopt an existing replacement instead of launching twice.
2. If eligible, call the native `start_session` tool once, fresh context, same project, date-only title such as `Main 11-19`. Give it the exact absolute handoff path, startup instructions and the user's current request. Never put the hour in the title.
3. Verify the new ordinary session read the handoff. Pin it and verify the pin before unpinning only the source session. On failure keep or restore the old pin, report which step failed and continue there. Record a successful replacement ID immediately; reconcile an uncertain start before any retry.
4. Transfer session crons with one owner, using the protocol below. Report the new title and handoff path in one line. Continue the current request there.

If starting is unavailable or refused, continue in the old visible session. Leave its title unchanged until an actual replacement exists. Retry only on a later eligible desk turn after reconciliation. Never create a scheduled task to perform a handoff, edit app metadata, fake keyboard input or use a CLI/deep link to defeat a refusal. Scheduled runs do not provide the ordinary visible, pinnable session this workflow needs.

For a daily or fallback transfer, the old session owns each session-cron move. First verify the new session has scheduling tools and the full prompt/schedule. Then cancel the old instance and verify cancellation; mark that item RELEASED in the handoff. Only then may the new session create one replacement and record its ID and next run as RECREATED. If cancellation or readiness is uncertain, retain the original and create nothing. If the old session ended and the scheduler confirms its item is gone, record that evidence before recreating it. Report any coverage gap. Never move persistent schedules or expired tasks.

## Fallback when the compaction setting is unavailable

Set `auto_compaction_available` to `false` only after verifying the installed version or model cannot use the setting. `threshold_percent` defaults to **50** and is only the fallback handoff threshold, not the auto-compaction percentage. The status-line script stores the latest numerical usage per session; UserPromptSubmit uses a reading no older than five minutes. It never opens transcripts. Missing or stale usage is unknown, not 0%. Ask for `/context` if a manual decision is needed.

At or above 50%, write the handoff first. On an eligible desk turn use the same verified transfer above. On remote or unverified turns keep working in place; use `/compact` after saving if relief is needed. `/clear` also needs a saved handoff. No Stop hook holds turns, no scheduled launcher, and no repeated launch attempts on remote turns. This fallback is the only automatic exception to one new session per day.

## Safety and limits

- The scripts use only Python's standard library. They parse the event envelope but never inspect prompt, message, custom-instruction or summary fields, and never open transcript paths or handoff contents. They read session metadata, file names/timestamps and numeric usage. The gauge writes small numeric state files under `scripts/state/`; the refresh hook writes nothing. Claude, separately, reads and writes the authorized handoff.
- Scripts emit instructions only. They never start sessions, send messages, publish, spend, modify settings, manipulate pins or edit app state themselves. Handoffs and restored crons do not expand earlier authorization.
- Invalid input, missing metadata/config or permission errors fail open with exit 0 and a generic diagnostic containing no payload. Unknown session identity is skipped rather than borrowing another session's handoff.
- `/clear` can change the CLI ID before Desktop metadata catches up. If no unique metadata match exists, the hook skips. Give Claude the saved handoff path manually if needed, then verify the mapping. Test pin, connection and cron behavior on your version; those UI outcomes are not guaranteed by Python tests.
- Roll back by removing only this package's hook entries and status-line command and restoring the previous compaction value from the backup. Keep saved handoffs. Do not overwrite unrelated later settings with an old whole-file backup.

Reference, checked 2026-11-18: [hooks](https://code.claude.com/docs/en/hooks), [settings](https://code.claude.com/docs/en/settings-reference), [status line](https://code.claude.com/docs/en/statusline).
