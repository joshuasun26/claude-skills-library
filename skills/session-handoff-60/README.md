# 60% session handoff (older, use session-refresh)

`session-handoff-60` | Always-on and sessions

Older approach, kept for setups that cannot compact in place. At 60% context Claude writes a handoff file, opens a fresh session and pins it. Most people should install session-refresh instead.

| | |
|---|---|
| **What** | Older approach, kept for setups that cannot compact in place. At 60% context Claude writes a handoff file, opens a fresh session and pins it. Most people should install session-refresh instead. |
| **When** | You have a long-running main chat that gets slow or forgetful by afternoon. |
| **Who it is for** | Anyone who keeps one main session open all day |
| **Needs** | Claude Code desktop app, Python 3.9+ |
| **Customize** | Edit scripts/context_gauge_config.json: threshold, handoff folder, main session name. |
| **Pick one** | Do not install alongside `session-refresh`. Both manage the same context hooks. |

## Install

Mac or Linux:
```bash
curl -fsSL https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.sh | bash -s -- session-handoff-60
```

Windows PowerShell:
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.ps1))) session-handoff-60
```

Or by hand: copy this `session-handoff-60` folder into `~/.claude/skills/` so you have `~/.claude/skills/session-handoff-60/SKILL.md`. On Windows `~` is your user folder (`%USERPROFILE%`). Then start a new Claude Code session.

## Try it

> Set up the 60% handoff for my main session called Main.

## Files

- `SKILL.md`
- `scripts/context_gauge.py`
- `scripts/context_gauge_config.json`

Full instructions live in [SKILL.md](SKILL.md). Back to the [library](../../README.md).
