# Wake Gate: only wake the AI when something real arrives

**The idea in one line:** let a free script do the waiting, and only spend AI usage when there is real work.

Asking an AI agent to "check my inbox every 10 minutes" spends model usage on every single check, including the hundreds that find nothing. Wake Gate flips that. A small Python script does the checking for free, and your AI job (Claude Code, Codex, or any script) runs only when something new actually lands.

## What it watches
- **Gmail:** any Gmail search, like `subject:invoice has:attachment`. Read-only access: it can see mail, it cannot send, delete or change anything.
- **A folder:** new files landing somewhere (scans, downloads, a synced Drive folder).
- **A web page:** the page changes, or starts containing a phrase you care about.

## Set it up
1. Install Python 3.9 or newer. No extra packages needed.
2. Copy `watchers.example.json` to `watchers.json` and edit it. Each watcher has a `name`, a `type`, what to look for, and an `on_hit` command.
3. Gmail only (a one-time login, separate from any Gmail connection inside Claude). In Google Cloud Console (console.cloud.google.com):
   1. Create or pick a project.
   2. APIs & Services, Library, **Gmail API**, Enable.
   3. Google Auth Platform (OAuth consent screen): Get started, app name, your email, Audience **External**, Create.
   4. Data Access, Add or remove scopes, "Manually add scopes": paste the full `https://www.googleapis.com/auth/gmail.readonly`, Add, Update, Save.
   5. Audience, Test users, add the Gmail address you are watching.
   6. Clients, Create client, **Desktop app**, Create, **Download JSON**.
   Then run `python setup_gmail_oauth.py --creds-file path/to/client_secret.json`, click Continue past "Google hasn't verified this app" (normal for your own private app), then Allow. It saves `~/.wake-gate-gmail.json`. Treat that file like a password.
4. Test without running anything: `python wake_gate.py --config watchers.json --dry-run`
5. Schedule it every 1 to 10 minutes:
   - **Windows:** Task Scheduler, daily trigger repeating every 10 minutes. Action: Program/script = the full path to `pythonw.exe` (run `where pythonw` to find it). Add arguments = `"C:\full\path\to\wake-gate\wake_gate.py" --config "C:\full\path\to\wake-gate\watchers.json"`. Start in = the wake-gate folder. Right-click the task, Run, and check that the log updated before you call it done.
   - **Mac/Linux:** `*/10 * * * * python3 /path/to/wake_gate.py --config /path/to/watchers.json`

## How it behaves
- Each watcher remembers what it already handled, so one email or file fires once.
- If your `on_hit` command fails, nothing is marked handled and the next run retries.
- `on_hit` gets `WAKE_GATE_NAME`, `WAKE_GATE_COUNT` and `WAKE_GATE_ITEMS` (a JSON file of the new items).
- `active_hours` like `"07-21"` keeps a watcher quiet overnight.
- The first run only records what is already there, so an old backlog does not trigger anything. Set `"fire_on_first_run": true` to change that.
- `~/` and `$WAKE_GATE_ITEMS` in `on_hit` work on Windows too; Wake Gate fills them in.
- If `on_hit` runs `claude -p`, Claude runs with no tools unless you allow them. Add `--allowedTools` with what the job needs (for example the Gmail draft tool), or call a script like Inbox Triage's `run_headless.py`, which sets this for you.

## Good rules
- Keep searches narrow (sender plus subject plus `newer_than:`) so the AI only wakes for real work.
- Anything that **sends** (email, text) should go through an approval step. Let the AI draft, you send.
- Never paste passwords or keys into the config. Point to files by path.
- Gmail logins in Google's "Testing" mode expire every 7 days. If you see `invalid_grant`, re-run the setup script.

Using Claude Code? Drop this folder into `~/.claude/skills/wake-gate/` and say "set up a wake gate for my invoices." The SKILL.md walks Claude through it.

Part of the [Claude Skills Library](https://github.com/joshuasun26/claude-skills-library). Free to use and adapt under the MIT license.
