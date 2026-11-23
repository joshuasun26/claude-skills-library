# Claude Skills Library

Practical Claude Code skills from a working real estate and mortgage AI setup. Each one is a folder you drop into `~/.claude/skills/`. Take the ones you want and leave the rest.

**Browse the catalog:** https://joshuasun26.github.io/claude-skills-library/

Every skill here is drafts-first. None of them sends an email, posts, publishes or spends money on its own. Where a skill can act, it stops and asks you first.

## Start here for an always-on machine

If you are setting up a computer that stays on and runs Claude all day, install these first:

1. **`session-refresh`** keeps one main session alive all day by compacting in place and re-reading a saved handoff. Pick this one if you often drive Claude from your phone.
   *Or* **`session-handoff-60`**, which starts a fresh session at 60% context instead. Install one of the two, not both. They use the same hook slot.
2. **`mac-mini-station-setup`** walks you through never-sleep settings, Remote Control and remote desktop, one step at a time. It is written for macOS.
3. **`gauntlet-loop`** gets a second model to challenge anything important before it goes out.

## Install

**Mac or Linux**, one skill or several:

```bash
git clone https://github.com/joshuasun26/claude-skills-library.git
cd claude-skills-library
./install.sh gauntlet-loop fact-check
```

**Windows PowerShell:**

```powershell
git clone https://github.com/joshuasun26/claude-skills-library.git
cd claude-skills-library
.\install.ps1 gauntlet-loop fact-check
```

No git? Each skill page on the [catalog site](https://joshuasun26.github.io/claude-skills-library/) has a one-line install command you can copy. Prefer to do it by hand? Copy a folder from `skills/` into `~/.claude/skills/` so you end up with `~/.claude/skills/<skill-name>/SKILL.md`. On Windows, `~` is your user folder (`%USERPROFILE%`).

The installers only copy skill folders. If you already have a skill with the same name, it is moved to `~/.claude/skills-backups/` first. They never touch `settings.json` or your hooks. The two session skills need one more step, which Claude does with you and shows you the settings diff before writing.

Start a new Claude Code session after installing, then ask for the skill by name or just describe the job.

## Catalog

<!-- catalog:begin -->
| Skill | What it does | Who it is for | Install (Mac/Linux) |
|---|---|---|---|
| **Always-on and sessions** | | | |
| [`session-handoff-60`](skills/session-handoff-60/) (start here) | When your main Claude Code session hits 60% context, Claude writes a handoff file, opens a fresh session that carries on, and pins it. | Anyone who keeps one main session open all day | `./install.sh session-handoff-60` |
| [`session-refresh`](skills/session-refresh/) (start here) | Keeps one visible main session all day. Claude compacts in place at about 30% of the window, re-reads your handoff, and starts one fresh dated session each morning. | Always-on machines and people who drive Claude from their phone | `./install.sh session-refresh` |
| [`mac-mini-station-setup`](skills/mac-mini-station-setup/) (start here) | Walks you through turning a Mac into an always-on AI station one step at a time: never sleep, Remote Control, Chrome Remote Desktop, working folder, screenshot shortcut. | Anyone setting up a home or office Mac that stays on | `./install.sh mac-mini-station-setup` |
| [`wake-gate`](skills/wake-gate/) | A free script watches Gmail, a folder or a web page and only wakes an AI job when something new arrives, so you stop paying a model to poll. | Anyone automating on incoming email, files or page changes | `./install.sh wake-gate` |
| **Inbox and daily rhythm** | | | |
| [`inbox-triage`](skills/inbox-triage/) | Who replied, what needs an answer, who owes you a reply after two business days (with a drafted nudge), and what you promised. Drafts only, never sends. | Anyone with a busy Gmail inbox | `./install.sh inbox-triage` |
| [`reading-desk`](skills/reading-desk/) | A calm separate session that shows a numbered list of what needs you and walks through it one item at a time, waiting for next. | Anyone who avoids a long list of emails or reports | `./install.sh reading-desk` |
| [`daily-brief`](skills/daily-brief/) | A morning brief from your calendar, recent email and dated industry news, with a week-ahead on Monday and a next-week plan on Friday. Read and draft only. | Loan officers and realtors, easy to adapt to any field | `./install.sh daily-brief` |
| [`voice-profile`](skills/voice-profile/) | Builds a profile of how you write from 100 to 200 of your sent emails, then drafts new messages that sound like you. | Anyone who wants drafts that do not sound like AI | `./install.sh voice-profile` |
| **Quality gates** | | | |
| [`gauntlet-loop`](skills/gauntlet-loop/) (start here) | One model builds, a second model blind-compares it against a real named reference, and you loop until ours wins. Hard stop at three rounds. | Anyone whose flyer, email or video has to be excellent, not decent | `./install.sh gauntlet-loop` |
| [`research-gauntlet`](skills/research-gauntlet/) | Two or three models research the same question independently, then a skeptical critic attacks the merged answer before you act on it. | Anyone making a costly decision from research | `./install.sh research-gauntlet` |
| [`fact-check`](skills/fact-check/) | Checks every number, date, name and claim in outbound content against a source opened this session before it ships, with a claim table and a running ledger. | Anyone who sends numbers to clients, partners or followers | `./install.sh fact-check` |
| [`carousel-readability`](skills/carousel-readability/) | A fresh critic judges every slide the way a viewer sees it, as a phone thumbnail at a glance: text size, overlap, contrast and spacing. | Anyone posting Instagram carousels or text-on-image slides | `./install.sh carousel-readability` |
| **Content and video** | | | |
| [`yt-brief`](skills/yt-brief/) | Pulls a YouTube video's real transcript with a free script and briefs it in two minutes of reading, with a verdict on whether to act on it. | Anyone who gets sent videos to watch | `./install.sh yt-brief` |
| [`reel-ship-package`](skills/reel-ship-package/) | An eight-point checklist that turns a finished render into a postable package: size-safe video, caption, thumbnail, audio options, fact check, faces and permission. | Anyone making short vertical videos | `./install.sh reel-ship-package` |
| [`clips-to-reel`](skills/clips-to-reel/) | Turns a folder of event clips into a 15 to 30 second vertical reel with licensed music and captions using FFmpeg, with a local preview and export checks. | Anyone with event footage and no editor | `./install.sh clips-to-reel` |
| **Realtor and loan officer kit** | | | |
| [`open-house-flyer`](skills/open-house-flyer/) | Builds a sourced open-house flyer in the realtor's chosen style from permitted listing photos and facts, with print and phone exports. | Realtors and the loan officers who support them | `./install.sh open-house-flyer` |
| [`realtor-showcase-page`](skills/realtor-showcase-page/) | A mobile one-page get-to-know-your-agent site plus a QR for the flyer, from approved realtor facts, photos and public contact details. | Realtors and the loan officers who support them | `./install.sh realtor-showcase-page` |
| [`comment-to-dm-funnel`](skills/comment-to-dm-funnel/) | Stages an Instagram comment keyword to DM link to landing-page capture flow for a CRM that supports it, with consent and duplicate-send checks. | Anyone running comment-a-keyword calls to action | `./install.sh comment-to-dm-funnel` |
| [`browser-agent-tasks`](skills/browser-agent-tasks/) | Prepares supervised browser workflows in Claude in Chrome for comps, CRM changes, pricing, letter drafts and reconciliation, with you approving each step. | Loan officers and realtors, adaptable to any back-office work | `./install.sh browser-agent-tasks` |
| [`daily-outreach`](skills/daily-outreach/) | A four-a-day relationship habit: two sphere contacts and two realtors, with call templates and one-minute after-call notes. Draft only. | Loan officers and realtors building referral relationships | `./install.sh daily-outreach` |
<!-- catalog:end -->

## Getting updates

This repo is the one place these skills live now. To update, `git pull` and run the installer again for the skills you use. Your previous copy is saved in `~/.claude/skills-backups/`. See [CHANGELOG.md](CHANGELOG.md) for what changed.

## Ground rules every skill follows

- Drafts, never sends. You press send.
- No passwords, tokens or keys in files, commands or chat.
- Facts need a source opened in the session. Unknowns stay in [brackets].
- Review loops are capped, so nothing runs forever on your usage.

## License

MIT, see [LICENSE](LICENSE). One exception: `gauntlet-loop` is adapted from a CC BY 4.0 original, so its attribution travels with it. See [NOTICE.md](NOTICE.md).

Made by Joshua Sun with Claude Code. Questions or ideas: open an issue.
