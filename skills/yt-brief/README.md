# YouTube brief

`yt-brief` | Content and video

Pulls a YouTube video's real transcript with a free script and briefs it in two minutes of reading, with a verdict on whether to act on it.

| | |
|---|---|
| **What** | Pulls a YouTube video's real transcript with a free script and briefs it in two minutes of reading, with a verdict on whether to act on it. |
| **When** | You paste a YouTube link with no instructions. |
| **Who it is for** | Anyone who gets sent videos to watch |
| **Needs** | Python 3.9+, pip install yt-dlp youtube-transcript-api |
| **Customize** | Tell it what your work is so the verdict is about you. |

## Install

Mac or Linux:
```bash
curl -fsSL https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.sh | bash -s -- yt-brief
```

Windows PowerShell:
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.ps1))) yt-brief
```

Or by hand: copy this `yt-brief` folder into `~/.claude/skills/` so you have `~/.claude/skills/yt-brief/SKILL.md`. On Windows `~` is your user folder (`%USERPROFILE%`). Then start a new Claude Code session.

## Try it

> Brief me on this: [YouTube link]

## Files

- `SKILL.md`
- `scripts/fetch_transcript.py`

Full instructions live in [SKILL.md](SKILL.md). Back to the [library](../../README.md).
