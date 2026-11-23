#!/usr/bin/env bash
# Install one or more skills from the Claude Skills Library into ~/.claude/skills/.
#
#   ./install.sh gauntlet-loop fact-check        # from a cloned copy of this repo
#   ./install.sh --list                          # show available skills
#   curl -fsSL https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.sh | bash -s -- gauntlet-loop
#
# It only copies skill folders. It never edits settings.json, hooks, or anything else.
# An existing skill with the same name is moved to ~/.claude/skills-backups/<name>-<timestamp> first,
# outside the skills folder so Claude does not load two copies.
set -euo pipefail

REPO="joshuasun26/claude-skills-library"
BRANCH="main"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
BACKUP="$HOME/.claude/skills-backups"

if [ $# -eq 0 ]; then
  echo "Usage: install.sh <skill-name> [more-skill-names]   or   install.sh --list"
  exit 1
fi

SRC=""
HERE=""
# Only trust a local skills/ folder when this script is a real file (not piped from curl).
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
  HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || true)"
fi
if [ -n "$HERE" ] && [ -d "$HERE/skills" ] && [ "$HERE/skills" != "$DEST" ]; then
  SRC="$HERE/skills"
else
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT
  echo "Downloading $REPO ($BRANCH)..."
  curl -fsSL "https://codeload.github.com/$REPO/tar.gz/refs/heads/$BRANCH" | tar -xz -C "$TMP"
  SRC="$(find "$TMP" -mindepth 2 -maxdepth 2 -type d -name skills | head -n 1)"
fi

if [ "$1" = "--list" ]; then
  ls -1 "$SRC"
  exit 0
fi

mkdir -p "$DEST"
STAMP="$(date +%Y%m%d-%H%M%S)"
INSTALLED=0; FAILED=0; SEEN=" "
for NAME in "$@"; do
  case "$SEEN" in *" $NAME "*) continue ;; esac
  SEEN="$SEEN$NAME "
  case "$NAME" in
    */*|.*|"") echo "Skipping invalid name: $NAME"; FAILED=$((FAILED+1)); continue ;;
  esac
  if [ ! -f "$SRC/$NAME/SKILL.md" ]; then
    echo "Not found: $NAME  (run with --list to see names)"
    FAILED=$((FAILED+1)); continue
  fi
  case "$NAME" in
    session-refresh) OTHER=session-handoff-60 ;;
    session-handoff-60) OTHER=session-refresh ;;
    *) OTHER="" ;;
  esac
  if [ -n "$OTHER" ] && { [ -e "$DEST/$OTHER" ] || case "$SEEN" in *" $OTHER "*) true ;; *) false ;; esac; }; then
    echo "Note: $NAME and $OTHER are pick-one. Use only one; remove the other from $DEST before finishing setup."
  fi
  if [ -e "$DEST/$NAME" ]; then
    mkdir -p "$BACKUP"
    mv "$DEST/$NAME" "$BACKUP/$NAME-$STAMP"
    echo "Kept your old copy at $BACKUP/$NAME-$STAMP"
  fi
  cp -R "$SRC/$NAME" "$DEST/$NAME"
  echo "Installed $NAME -> $DEST/$NAME"
  INSTALLED=$((INSTALLED+1))
  if [ -n "$OTHER" ]; then
    EXTRA=""; [ -f "$DEST/$NAME/INSTALL-PROMPT.md" ] && EXTRA=" and $DEST/$NAME/INSTALL-PROMPT.md"
    echo "  Next: open Claude Code and say: Read $DEST/$NAME/SKILL.md$EXTRA and finish the install. Back up my settings and show me the diff first."
  fi
done
if [ "$INSTALLED" -gt 0 ]; then
  echo "Done: $INSTALLED installed. Start a new Claude Code session to load new skills."
else
  echo "Nothing was installed."
fi
[ "$FAILED" -eq 0 ] && [ "$INSTALLED" -gt 0 ]
