# Fact check

`fact-check` | Quality gates

Checks every number, date, name and claim in outbound content against a source opened this session before it ships, with a claim table and a running ledger.

| | |
|---|---|
| **What** | Checks every number, date, name and claim in outbound content against a source opened this session before it ships, with a claim table and a running ledger. |
| **When** | Before any email, caption, flyer or report with a fact in it goes out. |
| **Who it is for** | Anyone who sends numbers to clients, partners or followers |
| **Needs** | Claude Code or Claude app |
| **Customize** | List your own systems of record in the sources section. |

## Install

Mac or Linux:
```bash
curl -fsSL https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.sh | bash -s -- fact-check
```

Windows PowerShell:
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.ps1))) fact-check
```

Or by hand: copy this `fact-check` folder into `~/.claude/skills/` so you have `~/.claude/skills/fact-check/SKILL.md`. On Windows `~` is your user folder (`%USERPROFILE%`). Then start a new Claude Code session.

## Try it

> Fact check this newsletter before I send it.

## Files

- `SKILL.md`

Full instructions live in [SKILL.md](SKILL.md). Back to the [library](../../README.md).
