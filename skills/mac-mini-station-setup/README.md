# Always-on Mac station

`mac-mini-station-setup` | Always-on and sessions

Walks you through turning a Mac into an always-on AI station one step at a time: never sleep, Remote Control, Chrome Remote Desktop, working folder, screenshot shortcut.

| | |
|---|---|
| **What** | Walks you through turning a Mac into an always-on AI station one step at a time: never sleep, Remote Control, Chrome Remote Desktop, working folder, screenshot shortcut. |
| **When** | You are setting up a machine Claude can work on while you are away. |
| **Who it is for** | Anyone setting up a home or office Mac that stays on |
| **Needs** | macOS, Claude desktop app |
| **Customize** | GUIDE.md is the printable checklist. Rename the example working folder to yours. |

## Install

Mac or Linux:
```bash
curl -fsSL https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.sh | bash -s -- mac-mini-station-setup
```

Windows PowerShell:
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.ps1))) mac-mini-station-setup
```

Or by hand: copy this `mac-mini-station-setup` folder into `~/.claude/skills/` so you have `~/.claude/skills/mac-mini-station-setup/SKILL.md`. On Windows `~` is your user folder (`%USERPROFILE%`). Then start a new Claude Code session.

## Try it

> Walk me through the Mac mini setup.

## Files

- `GUIDE.md`
- `SKILL.md`

Full instructions live in [SKILL.md](SKILL.md). Back to the [library](../../README.md).
