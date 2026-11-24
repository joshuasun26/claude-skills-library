# Today board

`today-board` | Inbox and daily rhythm

One private page with today's calls, the few things only you can do, who you are waiting on, and a to-do list whose checks stay put on every device. Claude updates it when you say add X or check off X.

| | |
|---|---|
| **What** | One private page with today's calls, the few things only you can do, who you are waiting on, and a to-do list whose checks stay put on every device. Claude updates it when you say add X or check off X. |
| **When** | Every morning, after an inbox triage, and whenever you add or finish a to-do. |
| **Who it is for** | Anyone who wants one screen to open first thing every morning |
| **Needs** | Claude Code, A claude.ai account for the private Artifact page, or Python 3.9+ for the local HTML fallback |
| **Customize** | Name the board and choose Artifact or Offline mode at setup; the choice is saved in ~/.today-board/config.json. |

## Install

Mac or Linux:
```bash
curl -fsSL https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.sh | bash -s -- today-board
```

Windows PowerShell:
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.ps1))) today-board
```

Or by hand: copy this `today-board` folder into `~/.claude/skills/` so you have `~/.claude/skills/today-board/SKILL.md`. On Windows `~` is your user folder (`%USERPROFILE%`). Then start a new Claude Code session.

## Try it

> Use today-board. Make me a Today board, add 'call the inspector' and 'send the CMA', then show me the link.

## Files

- `SKILL.md`
- `examples/TODAY.example.json`
- `scripts/board.py`
- `templates/board.html`
- `tests/test_board.py`

Full instructions live in [SKILL.md](SKILL.md). Back to the [library](../../README.md).
