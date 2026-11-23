# Session refresh (compact in place)

`session-refresh` | Always-on and sessions

Keeps one visible main session all day. Claude compacts in place at about 30% of the window, re-reads your handoff, and starts one fresh dated session each morning.

| | |
|---|---|
| **What** | Keeps one visible main session all day. Claude compacts in place at about 30% of the window, re-reads your handoff, and starts one fresh dated session each morning. |
| **When** | You want the main session to survive all day without new sessions piling up in the sidebar. |
| **Who it is for** | Always-on machines and people who drive Claude from their phone |
| **Needs** | Claude Code, Python 3.9+, Desktop app for daily starts and pins |
| **Customize** | Edit scripts/config.json and the autoCompactWindow value in settings. INSTALL-PROMPT.md walks Claude through it. |
| **Pick one** | Do not install alongside `session-handoff-60`. Both manage the same context hooks. |

## Install

Mac or Linux:
```bash
curl -fsSL https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.sh | bash -s -- session-refresh
```

Windows PowerShell:
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.ps1))) session-refresh
```

Or by hand: copy this `session-refresh` folder into `~/.claude/skills/` so you have `~/.claude/skills/session-refresh/SKILL.md`. On Windows `~` is your user folder (`%USERPROFILE%`). Then start a new Claude Code session.

## Try it

> Read session-refresh/SKILL.md and INSTALL-PROMPT.md. Install it, back up my settings and show me the diff first.

## Files

- `INSTALL-PROMPT.md`
- `SKILL.md`
- `scripts/config.json`
- `scripts/context_gauge.py`
- `scripts/refresh_hook.py`

Full instructions live in [SKILL.md](SKILL.md). Back to the [library](../../README.md).
