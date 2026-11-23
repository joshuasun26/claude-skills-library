# Wake gate

`wake-gate` | Always-on and sessions

A free script watches Gmail, a folder or a web page and only wakes an AI job when something new arrives, so you stop paying a model to poll.

| | |
|---|---|
| **What** | A free script watches Gmail, a folder or a web page and only wakes an AI job when something new arrives, so you stop paying a model to poll. |
| **When** | You want a job to run on new email or new files without burning usage on empty checks. |
| **Who it is for** | Anyone automating on incoming email, files or page changes |
| **Needs** | Python 3.9+, Task Scheduler or cron, Google OAuth client for Gmail watchers |
| **Customize** | Copy watchers.example.json to watchers.json and set one watcher per trigger. |

## Install

Mac or Linux:
```bash
curl -fsSL https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.sh | bash -s -- wake-gate
```

Windows PowerShell:
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.ps1))) wake-gate
```

Or by hand: copy this `wake-gate` folder into `~/.claude/skills/` so you have `~/.claude/skills/wake-gate/SKILL.md`. On Windows `~` is your user folder (`%USERPROFILE%`). Then start a new Claude Code session.

## Try it

> Set up a wake gate that runs my triage only when a new email from my escrow officer arrives.

## Files

- `SETUP.md`
- `SKILL.md`
- `setup_gmail_oauth.py`
- `wake_gate.py`
- `watchers.example.json`
- `watchers.inbox.example.json`

Full instructions live in [SKILL.md](SKILL.md). Back to the [library](../../README.md).
