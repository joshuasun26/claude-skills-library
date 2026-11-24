# Claude brain team

`claude-brain-team` | AI teams and delegation

Claude is the brain and coordinator; any mix of other models you already have (Muse by Meta, ChatGPT or Codex, Gemini, Grok) does the work. Numbered task files, evidence-checked results, and a list so nothing goes quiet.

| | |
|---|---|
| **What** | Claude is the brain and coordinator; any mix of other models you already have (Muse by Meta, ChatGPT or Codex, Gemini, Grok) does the work. Numbered task files, evidence-checked results, and a list so nothing goes quiet. |
| **When** | You want to hand research, drafts or code to other models while Claude plans, routes and checks the work. |
| **Who it is for** | Anyone who uses more than one AI app and wants them working as one team |
| **Needs** | Claude Code, Python 3.9+, Slack, or a free synced folder (Google Drive, Dropbox or OneDrive) |
| **Customize** | Answer the one-time setup interview; Claude saves your tools, privacy limits and routing in team.json in your board folder. |

## Install

Mac or Linux:
```bash
curl -fsSL https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.sh | bash -s -- claude-brain-team
```

Windows PowerShell:
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.ps1))) claude-brain-team
```

Or by hand: copy this `claude-brain-team` folder into `~/.claude/skills/` so you have `~/.claude/skills/claude-brain-team/SKILL.md`. On Windows `~` is your user folder (`%USERPROFILE%`). Then start a new Claude Code session.

## Try it

> Use claude-brain-team. Run the setup interview, then have Muse research five free tools for my task and check what it brings back.

## Files

- `SKILL.md`
- `scripts/board.py`
- `team.example.json`
- `tests/test_board.py`

Full instructions live in [SKILL.md](SKILL.md). Back to the [library](../../README.md).
