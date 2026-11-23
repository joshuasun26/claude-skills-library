# Changelog

All notable changes to this library. Dates are when the change landed here.

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
