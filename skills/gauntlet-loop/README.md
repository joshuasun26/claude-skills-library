# Gauntlet loop

`gauntlet-loop` | Quality gates

One model builds, a second model blind-compares it against a real named reference, and you loop until ours wins. Hard stop at three rounds.

| | |
|---|---|
| **What** | One model builds, a second model blind-compares it against a real named reference, and you loop until ours wins. Hard stop at three rounds. |
| **When** | The piece matters enough that one good pass is not enough. |
| **Who it is for** | Anyone whose flyer, email or video has to be excellent, not decent |
| **Needs** | A second model you can paste into, or a second agent |
| **Customize** | Name your own reference artifact each run. |
| **License** | CC BY 4.0 (adapted from RoboNuggets). See SKILL.md for attribution. |

## Install

Mac or Linux:
```bash
curl -fsSL https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.sh | bash -s -- gauntlet-loop
```

Windows PowerShell:
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.ps1))) gauntlet-loop
```

Or by hand: copy this `gauntlet-loop` folder into `~/.claude/skills/` so you have `~/.claude/skills/gauntlet-loop/SKILL.md`. On Windows `~` is your user folder (`%USERPROFILE%`). Then start a new Claude Code session.

## Try it

> Use gauntlet-loop on this email against [named reference]. Stop after three rounds.

## Files

- `SKILL.md`

Full instructions live in [SKILL.md](SKILL.md). Back to the [library](../../README.md).
