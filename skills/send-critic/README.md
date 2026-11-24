# Send critic

`send-critic` | Quality gates

A separate agent checks an important email or text before it goes out: answers the latest message, right recipients, facts, attachments, private info, promises, duplicates and text opt-outs. Returns PASS, FIX or HOLD. Never sends.

| | |
|---|---|
| **What** | A separate agent checks an important email or text before it goes out: answers the latest message, right recipients, facts, attachments, private info, promises, duplicates and text opt-outs. Returns PASS, FIX or HOLD. Never sends. |
| **When** | Before any client, partner, group, money, legal or deal message goes out. |
| **Who it is for** | Anyone sending money, deal, legal or group messages |
| **Needs** | Claude Code, Python 3.9+, A subagent or second model for the independent read |
| **Customize** | Answer the one-time setup (high-stakes list, never-send info, banned words, opt-out list, send log); saved to ~/.claude/send-critic/config.json. |

## Install

Mac or Linux:
```bash
curl -fsSL https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.sh | bash -s -- send-critic
```

Windows PowerShell:
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.ps1))) send-critic
```

Or by hand: copy this `send-critic` folder into `~/.claude/skills/` so you have `~/.claude/skills/send-critic/SKILL.md`. On Windows `~` is your user folder (`%USERPROFILE%`). Then start a new Claude Code session.

## Try it

> Use send-critic on this reply before I send it. Check the whole thread.

## Files

- `SKILL.md`
- `config/send-critic.example.json`
- `scripts/send_check.py`
- `tests/test_send_check.py`

Full instructions live in [SKILL.md](SKILL.md). Back to the [library](../../README.md).
