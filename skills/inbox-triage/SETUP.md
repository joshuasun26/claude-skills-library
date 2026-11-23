# Inbox Triage: setup guide

## 1. Connect Gmail to Claude

**Claude desktop or claude.ai (easiest):**
1. Settings, then Connectors. Find **Gmail** and click Connect.
2. Sign in with the email account you actually work from. If you use two (personal
   Gmail plus a brokerage Google Workspace address), connect the one where clients write, and
   list both in `owner_emails` so mail you send from either one counts as yours.
3. Approve the permissions Google shows. The skill needs to read mail and create drafts.
   It never uses send.
4. Test it in a new chat: "Search my Gmail for `in:sent newer_than:3d` and list the subjects."
   If you get subjects back, the connector works.

**Claude Code:** run `claude mcp list` to confirm a Gmail server is connected. If you
use Claude Code only, connect Gmail in claude.ai first; connectors on the account
carry over to Claude Code sessions signed in to the same account.

**Workspace (brokerage) accounts:** some brokerages block third-party apps. If Google says
the app is blocked, your Workspace admin has to allow it. Do not work around it by
forwarding mail to a personal account.

## 2. Create the config

Run these from the `inbox-triage` skill folder (for example `~/.claude/skills/inbox-triage`).

```
mkdir ~/.inbox-triage
cp config/triage-config.example.json ~/.inbox-triage/config.json
```

Fill it in field by field:

| Field | What to ask |
|---|---|
| `owner_emails` | Every address you send from. |
| `timezone` | Your IANA time zone, for example `America/Los_Angeles`. Daylight saving is handled for you. On Windows, run `pip install tzdata` once so Python has the time zone data; triage stops with a clear message if the zone cannot load. (Older configs with `utc_offset_hours` still work but drift an hour twice a year.) |
| `followup_business_days` | How long before a quiet person gets a nudge? Default 2. |
| `vip.tier1` | Who must never wait? (broker, lender partner, top clients in escrow). These trigger a text. |
| `vip.tier2` | Who matters this week? (active buyers and sellers, escrow, title). Always in the digest. |
| `vip.tier3` | Sphere and referral partners. Surfaced, never urgent. |
| `never_nudge` | Anyone you never want an automatic nudge drafted for. |
| `suppress` | Senders you never want to see. |
| `noise.from_patterns` | Newsletters and tools that fill the inbox. Start with the defaults. |
| `notify.channel` | sms, telegram, email-to-self, or none. Use whatever notification tool you already have connected. |
| `voice` | Paste two of your real emails and write the greeting, sign-off and nudge template in your words. |

Leave `send_rules.auto_send` at `false`.

## 3. First run, watched

Say "triage my inbox" and review every bucket. Expect to move two or three
people between tiers. Edit the config, not the skill.

Run the self-test once to confirm Python works on your machine:
```
python scripts/triage.py --help
python tests/test_triage.py
```

## 4. Schedule it

Default model: **Opus 5.5 at medium effort**, set in the config as `run.model` and `run.effort`.

**Recommended: an OS-scheduled headless run.** Desktop-app scheduled tasks cannot pin a model
or an effort level, and they stop firing if the app hangs. `scripts/run_headless.py` runs the
Claude CLI with `--model` and `--effort` taken from `config.run`. It also holds a lock so runs
never overlap, blocks the named Gmail send tools (check the names match your connector with step 2), and logs to `~/.inbox-triage/runs/runs.log`.

1. Confirm the CLI is installed and signed in to your own subscription:
   `claude --version`.
2. Confirm the CLI can see Gmail. Connectors on the claude.ai account carry over to it:
   `claude -p --model claude-opus-5-5 --effort medium "List your tool names that contain search_threads. Do not call any tool."`
   The answer must name a Gmail `search_threads` tool.
3. Windows (Task Scheduler): make one task per time slot (8:00, 12:00 and 17:00), weekdays only.
   - The action is: run `python.exe`.
   - The arguments are: `"C:\Users\<you>\.claude\skills\inbox-triage\scripts\run_headless.py" --config "C:\Users\<you>\.inbox-triage\config.json"`.
   - Tick "Run task as soon as possible after a scheduled start is missed."
4. Mac or Linux: add this line with `crontab -e`:
   `0 8,12,17 * * 1-5 python3 ~/.claude/skills/inbox-triage/scripts/run_headless.py --config ~/.inbox-triage/config.json`.
5. To change the model or effort later, edit `run.model` / `run.effort` in the config.
   Nothing else needs to change.
6. Pick ONE trigger: this schedule, OR Wake Gate (runs triage only when new mail arrives). Not both. Two triggers means duplicate runs.

**Alternative (simpler, less reliable):** a Claude desktop scheduled task with the prompt
"Run the inbox-triage skill." It runs on the app's current default model, and nothing in the
task can change that.

At the one-week follow-up, check two things:
- `~/.inbox-triage/runs/runs.log` has a line for every scheduled slot.
- `last_commit` in `state.json` is recent.

A schedule that silently stops firing is a common failure. If the model name or the `--effort` flag stops working after a Claude update, change `run.model` / `run.effort` in the config.

## 5. Privacy

- Mail content stays in your own Claude account and your own machine.
- `state.json` stores message ids, thread ids and short commitment sentences, never full
  email bodies. Delete the folder to reset.
- Nothing in this skill sends email, and nothing leaves the machine except the digest
  you chose to receive.
