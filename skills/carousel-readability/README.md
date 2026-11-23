# Carousel readability

`carousel-readability` | Quality gates

A fresh critic judges every slide the way a viewer sees it, as a phone thumbnail at a glance: text size, overlap, contrast and spacing.

| | |
|---|---|
| **What** | A fresh critic judges every slide the way a viewer sees it, as a phone thumbnail at a glance: text size, overlap, contrast and spacing. |
| **When** | Before every carousel ships, and after every resize. |
| **Who it is for** | Anyone posting Instagram carousels or text-on-image slides |
| **Needs** | Rendered PNG slides, A subagent or second model |
| **Customize** | Update the starting floors table with sizes that test well for your fonts. |

## Install

Mac or Linux:
```bash
curl -fsSL https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.sh | bash -s -- carousel-readability
```

Windows PowerShell:
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.ps1))) carousel-readability
```

Or by hand: copy this `carousel-readability` folder into `~/.claude/skills/` so you have `~/.claude/skills/carousel-readability/SKILL.md`. On Windows `~` is your user folder (`%USERPROFILE%`). Then start a new Claude Code session.

## Try it

> Run carousel-readability on these five slides.

## Files

- `SKILL.md`

Full instructions live in [SKILL.md](SKILL.md). Back to the [library](../../README.md).
