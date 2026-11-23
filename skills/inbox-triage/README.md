# Inbox triage

`inbox-triage` | Inbox and daily rhythm

Who replied, what needs an answer, who owes you a reply after two business days (with a drafted nudge), and what you promised. Drafts only, never sends.

| | |
|---|---|
| **What** | Who replied, what needs an answer, who owes you a reply after two business days (with a drafted nudge), and what you promised. Drafts only, never sends. |
| **When** | Two or three times a day, by hand or on a schedule. |
| **Who it is for** | Anyone with a busy Gmail inbox |
| **Needs** | Claude Code, Python 3.9+, Gmail access |
| **Customize** | Copy config/triage-config.example.json and follow SETUP.md. |

## Install

Mac or Linux:
```bash
curl -fsSL https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.sh | bash -s -- inbox-triage
```

Windows PowerShell:
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.ps1))) inbox-triage
```

Or by hand: copy this `inbox-triage` folder into `~/.claude/skills/` so you have `~/.claude/skills/inbox-triage/SKILL.md`. On Windows `~` is your user folder (`%USERPROFILE%`). Then start a new Claude Code session.

## Try it

> Triage my inbox. Who replied, who owes me a reply, and what did I promise?

## Files

- `SETUP.md`
- `SKILL.md`
- `config/triage-config.example.json`
- `scripts/__pycache__/run_headless.cpython-312.pyc`
- `scripts/__pycache__/triage.cpython-312.pyc`
- `scripts/run_headless.py`
- `scripts/triage.py`
- `tests/test_triage.py`

Full instructions live in [SKILL.md](SKILL.md). Back to the [library](../../README.md).
