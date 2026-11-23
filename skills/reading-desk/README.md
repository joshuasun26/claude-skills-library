# Reading desk

`reading-desk` | Inbox and daily rhythm

A calm separate session that shows a numbered list of what needs you and walks through it one item at a time, waiting for next.

| | |
|---|---|
| **What** | A calm separate session that shows a numbered list of what needs you and walks through it one item at a time, waiting for next. |
| **When** | After triage, or whenever a batch of reading has piled up. |
| **Who it is for** | Anyone who avoids a long list of emails or reports |
| **Needs** | Claude Code or Claude app |
| **Customize** | Change the list location and ordering rules in SKILL.md. |

## Install

Mac or Linux:
```bash
curl -fsSL https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.sh | bash -s -- reading-desk
```

Windows PowerShell:
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.ps1))) reading-desk
```

Or by hand: copy this `reading-desk` folder into `~/.claude/skills/` so you have `~/.claude/skills/reading-desk/SKILL.md`. On Windows `~` is your user folder (`%USERPROFILE%`). Then start a new Claude Code session.

## Try it

> Start a reading desk from my last triage.

## Files

- `PHONE-DICTATION.md`
- `READING-MODES.md`
- `SKILL.md`

Full instructions live in [SKILL.md](SKILL.md). Back to the [library](../../README.md).
