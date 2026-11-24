# Changelog

All notable changes to this library. Dates are when the change landed here.

## 1.2.0 (2026-11-24)

- New `today-board`: a private one-screen Today board (calls, only-you items, waiting-on, to-do list) published as a claude.ai Artifact with checks saved across devices, or a local HTML page offline. Refuses secrets in any field; done items archive after 30 days.
- New `send-critic`: an independent agent checks an important email or text before it goes out and returns PASS, FIX or HOLD. Helper script scans for private info, banned words, duplicates and text opt-outs (plain list or CSV). A PASS is never permission to send.

## 1.1.0 (2026-11-23)

- New `claude-brain-team`: Claude coordinates a team of other models you already have (Muse by Meta as a free default worker, plus ChatGPT or Codex, Gemini, Grok). Setup interview saves team.json; numbered task files and RESULTs on Slack or a free shared folder; `board.py` refuses to close a task without evidence and keeps private work away from workers not cleared for it. New category: AI teams and delegation.

## 1.0.2 (2026-11-23)

- `session-refresh` is now the recommended main-session routine (compact in place at about 30%, fresh session daily). `session-handoff-60` is marked older and is no longer a start-here pick.
- `yt-brief`: new Step 4, act on it. Saves every transcript, rates the tools a video mentions, safety-checks anything it links before install, and ends with a reuse block.

## 1.0.1 (2026-11-23)

Fixes from the launch-day reviews.
- Install: one-line installs (no git) are now the main path. Piped installs always download from GitHub. Windows clone command works with the default script policy. Installers warn when both session skills are picked, print full post-install paths, dedupe names, report failures and clean up temp files.
- `session-handoff-60`: no scheduled-task fallback when a new session cannot start.
- `session-refresh`: restores only the current session's own handoff file.
- `reel-ship-package`: delivery needs your OK on destination and files.
- `inbox-triage`: clear error (and `pip install tzdata` tip) when a time zone cannot load.
- `wake-gate`: Task Scheduler setup uses full paths.
- Site: Start here link, plain pick-one guidance, Python note, Windows note for the station guide.

## 1.0.0 (2026-11-23)

First public release. One repo replaces the zip files that used to be sent around.

**Always-on and sessions**
- `session-handoff-60`: 60% context handoff to a fresh pinned session.
- `session-refresh`: in-place compaction with handoff restore and one dated session per day. Includes INSTALL-PROMPT.md for upgrades from older handoff setups.
- `mac-mini-station-setup`: guided always-on Mac setup with the printable GUIDE.md.
- `wake-gate`: free Gmail, folder and web-page watchers that wake an AI job only when needed.

**Inbox and daily rhythm**
- `inbox-triage`, `reading-desk`, `daily-brief`, `voice-profile`.

**Quality gates**
- `gauntlet-loop` (bounded to three rounds, CC BY 4.0 attribution kept), `research-gauntlet`, `fact-check`, `carousel-readability`.

**Content and video**
- `yt-brief`, `reel-ship-package`, `clips-to-reel`.

**Realtor and loan officer kit**
- `open-house-flyer`, `realtor-showcase-page`, `comment-to-dm-funnel`, `browser-agent-tasks`, `daily-outreach`.

**Tooling**
- `install.sh` and `install.ps1` copy skills and back up any existing copy outside the skills folder.
- `tools/build_catalog.py` regenerates every README and the catalog site from `catalog.json`.
- Catalog site in `docs/` (GitHub Pages).
