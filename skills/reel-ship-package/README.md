# Reel ship package

`reel-ship-package` | Content and video

An eight-point checklist that turns a finished render into a postable package: size-safe video, caption, thumbnail, audio options, fact check, faces and permission.

| | |
|---|---|
| **What** | An eight-point checklist that turns a finished render into a postable package: size-safe video, caption, thumbnail, audio options, fact check, faces and permission. |
| **When** | The moment a reel finishes rendering. |
| **Who it is for** | Anyone making short vertical videos |
| **Needs** | Claude Code, FFmpeg for compression |
| **Customize** | Set your delivery channel's file limit and your thumbnail template. |

## Install

Mac or Linux:
```bash
curl -fsSL https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.sh | bash -s -- reel-ship-package
```

Windows PowerShell:
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.ps1))) reel-ship-package
```

Or by hand: copy this `reel-ship-package` folder into `~/.claude/skills/` so you have `~/.claude/skills/reel-ship-package/SKILL.md`. On Windows `~` is your user folder (`%USERPROFILE%`). Then start a new Claude Code session.

## Try it

> Package this reel and tell me what is still missing.

## Files

- `SKILL.md`

Full instructions live in [SKILL.md](SKILL.md). Back to the [library](../../README.md).
