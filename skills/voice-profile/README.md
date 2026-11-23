# Voice profile

`voice-profile` | Inbox and daily rhythm

Builds a profile of how you write from 100 to 200 of your sent emails, then drafts new messages that sound like you.

| | |
|---|---|
| **What** | Builds a profile of how you write from 100 to 200 of your sent emails, then drafts new messages that sound like you. |
| **When** | Once to build it, then every time another skill drafts in your name. |
| **Who it is for** | Anyone who wants drafts that do not sound like AI |
| **Needs** | Claude with Gmail access, or pasted redacted samples |
| **Customize** | Edit the approved profile any time you notice a word you would never use. |

## Install

Mac or Linux:
```bash
curl -fsSL https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.sh | bash -s -- voice-profile
```

Windows PowerShell:
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.ps1))) voice-profile
```

Or by hand: copy this `voice-profile` folder into `~/.claude/skills/` so you have `~/.claude/skills/voice-profile/SKILL.md`. On Windows `~` is your user folder (`%USERPROFILE%`). Then start a new Claude Code session.

## Try it

> Use voice-profile on my last 150 sent emails. Build a redacted profile. Send nothing.

## Files

- `SKILL.md`

Full instructions live in [SKILL.md](SKILL.md). Back to the [library](../../README.md).
