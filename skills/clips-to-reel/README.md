# Clips to reel

`clips-to-reel` | Content and video

Turns a folder of event clips into a 15 to 30 second vertical reel with licensed music and captions using FFmpeg, with a local preview and export checks.

| | |
|---|---|
| **What** | Turns a folder of event clips into a 15 to 30 second vertical reel with licensed music and captions using FFmpeg, with a local preview and export checks. |
| **When** | After an event, open house or meetup. |
| **Who it is for** | Anyone with event footage and no editor |
| **Needs** | Claude Code, FFmpeg and FFprobe |
| **Customize** | Change the beat length and caption style in SKILL.md. |

## Install

Mac or Linux:
```bash
curl -fsSL https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.sh | bash -s -- clips-to-reel
```

Windows PowerShell:
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.ps1))) clips-to-reel
```

Or by hand: copy this `clips-to-reel` folder into `~/.claude/skills/` so you have `~/.claude/skills/clips-to-reel/SKILL.md`. On Windows `~` is your user folder (`%USERPROFILE%`). Then start a new Claude Code session.

## Try it

> Use clips-to-reel on this folder. Make a 20-second vertical draft. Keep it local.

## Files

- `SKILL.md`

Full instructions live in [SKILL.md](SKILL.md). Back to the [library](../../README.md).
