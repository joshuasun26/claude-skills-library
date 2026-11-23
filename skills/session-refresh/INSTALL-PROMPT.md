# Paste this into Claude Code

Install the supplied `session-refresh` skill as an upgrade from `session-handoff-60` or an older handoff setup. Read its SKILL.md first. This is local setup only. Never send anything, publish, deploy or change account/security permissions.

Inspect the installed Claude Code version, actual model ID/context window, Python 3.9+ interpreter, and effective settings scopes first. Find the current old skill paths, hooks and status line. Read the old hook scripts before deciding which entries belong to them. Use normal settings files and native app tools. Keep all unrelated configuration.

Prepare the complete proposed settings in memory and show the user a focused diff **before writing settings**. Redact any unrelated sensitive values from the display. Back up every settings file you will change, locally alongside it with a timestamped suffix. Do not print or copy credentials into the skill, handoff, logs or a shared backup. Do not write malformed JSON or overwrite changes made after your read; re-read before writing. Use a structural merge, then validate and read back the targeted keys.

Copy `session-refresh/` to the user's own skills directory and configure its `scripts/config.json`. Keep both scripts and config together. Resolve `~`, `%USERPROFILE%` and shell variables to absolute paths before writing hook commands. Do not use another person's username or machine paths. A Mac directory containing `Application Support` needs quoting in a command, though the JSON glob is a plain string. Windows hook commands can use quoted forward-slash paths.

Use these locations:

| Item | Windows | Mac |
|---|---|---|
| Skill | `%USERPROFILE%/.claude/skills/session-refresh/` | `~/.claude/skills/session-refresh/` |
| User settings | `%USERPROFILE%/.claude/settings.json` | `~/.claude/settings.json` |
| Project local settings | `<project>/.claude/settings.local.json` | `<project>/.claude/settings.local.json` |
| Session metadata glob example | `%APPDATA%/Claude/claude-code-sessions/*/*/local_*.json` | `~/Library/Application Support/Claude/claude-code-sessions/*/*/local_*.json` |

Check which glob actually finds metadata on this installation without displaying its contents. Verify a unique ID match and a title matching the configured date regex. Do not turn every session into the main session as a workaround. Do not read transcripts. If the app metadata differs, report the specific unsupported mapping; in-place `/compact` with a handoff remains usable.

For the upgrade:

1. Remove only old `Stop` and `UserPromptSubmit` command handlers that ran the inspected old handoff gauge, including `--stop` variants. Remove or replace any already-installed duplicate of these new handlers. If a group also contains unrelated commands, keep those commands and group properties. Do not remove an entire hook event to replace one command. Preserve unrelated PreCompact and SessionStart hooks as well. Leave no old launcher active.
2. Keep the old skill files as a local backup and record their paths. Move the superseded skill folders outside the active `skills` search path so both old/new instructions cannot activate together. Inspect before moving, avoid overwrites, and keep a reversible map. Replace old active startup instructions about percentage-based new sessions, hour titles and handoff-launch tasks with this skill's in-place/daily behavior. If an existing scheduled task specifically launches old handoff sessions, list it and disable only that confirmed launcher within the user's setup authorization. Never create a replacement task. Leave normal reminders intact.
3. Set the configured main name, date regex with `month` and `day` capture groups, dedicated handoff directory, and actual startup files. Create the handoff directory. Date-only title example: `Main 11-19`. If you choose `Desk`, change both name and regex. The scripts expand the config's Windows/Mac glob examples automatically. An explicit string `sessions_glob` is also supported.
4. Add the merged hooks and status line below, replacing the sample paths with the discovered interpreter and copied script paths. If a status line already has other information, preserve it using its existing extension mechanism or a small local wrapper that also invokes `context_gauge.py --statusline` on the same stdin. Do not silently discard it. Running the gauge is required to cache fallback usage. No Stop entry is installed.
5. In the narrowest appropriate settings scope, merge `modelSettings.<actual-model-id>.autoCompactWindow`. For a confirmed 1M window use 300000. For other windows compute about 30%, check the installed supported range and startup footprint, and report any necessary adjustment. The documented range is 100000 to 1000000 tokens; 60k for a 200k window cannot be installed as written. Check environment/CLI/policy overrides. If unsupported, leave out the setting and set config `auto_compaction_available` false, with fallback `threshold_percent` 50. Otherwise keep that flag true. Do not write a guessed model ID or apply the setting globally without explaining its scope.

Windows merged-settings example, assuming Python is on PATH (otherwise use its full quoted path). Replace `YOUR-USER` before use:

```json
{
  "hooks": {
    "UserPromptSubmit": [{"hooks": [{"type": "command", "timeout": 10, "command": "python -I -B \"C:/Users/YOUR-USER/.claude/skills/session-refresh/scripts/context_gauge.py\""}]}],
    "PreCompact": [{"hooks": [{"type": "command", "timeout": 10, "command": "python -I -B \"C:/Users/YOUR-USER/.claude/skills/session-refresh/scripts/refresh_hook.py\" --precompact"}]}],
    "SessionStart": [{"matcher": "compact|clear", "hooks": [{"type": "command", "timeout": 10, "command": "python -I -B \"C:/Users/YOUR-USER/.claude/skills/session-refresh/scripts/refresh_hook.py\" --sessionstart"}]}]
  },
  "statusLine": {"type": "command", "command": "python -I -B \"C:/Users/YOUR-USER/.claude/skills/session-refresh/scripts/context_gauge.py\" --statusline"},
  "modelSettings": {"YOUR-ACTUAL-MODEL-ID": {"autoCompactWindow": 300000}}
}
```

Mac uses the same JSON shape. Replace the four command values with these, using the real interpreter and home directory:

```text
"/usr/bin/python3" -I -B "/Users/YOUR-USER/.claude/skills/session-refresh/scripts/context_gauge.py"
"/usr/bin/python3" -I -B "/Users/YOUR-USER/.claude/skills/session-refresh/scripts/refresh_hook.py" --precompact
"/usr/bin/python3" -I -B "/Users/YOUR-USER/.claude/skills/session-refresh/scripts/refresh_hook.py" --sessionstart
"/usr/bin/python3" -I -B "/Users/YOUR-USER/.claude/skills/session-refresh/scripts/context_gauge.py" --statusline
```

Verify that this Python actually exists and meets the version requirement. Those are shell command values; escape their quotes when inserting into JSON. The samples are fragments to merge, never replacements for the full settings file.

After showing the diff and making the backed-up local installation, validate JSON, inspect `/hooks` or restart the scratch session as the installed app requires, and name/pin the main session with today's real date. Save the initial handoff. Test the scripts with metadata/usage fixtures first. Then in a scratch Desktop session test `/compact`, and `/clear` only after saving: it should re-read the handoff, keep the title, list and deduplicate crons, and say `Refreshed in place.` Check pin and Remote Control state. Do not describe live UI behavior as tested until observed. Do not start sessions from a phone, Remote Control, cron, Stop or peer turn. A locally typed message must begin the turn; mid-turn steering does not qualify.

Keep a short installation receipt: paths changed, backup paths, focused settings diff, effective model/window/compaction point, configured main-session mapping, tests actually run and any unsupported feature. No secrets or message contents. Never claim success from a dry run alone.

Rollback: remove only the new commands, restore only the changed status-line and model value from the backup, and restore the old skill folders if requested. Retain handoffs and unrelated later edits. Do not re-enable obsolete scheduled launchers automatically.
