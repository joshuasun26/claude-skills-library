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
HERE="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || true)"
if [ -n "$HERE" ] && [ -d "$HERE/skills" ]; then
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
for NAME in "$@"; do
  case "$NAME" in
    */*|.*|"") echo "Skipping invalid name: $NAME"; continue ;;
  esac
  if [ ! -f "$SRC/$NAME/SKILL.md" ]; then
    echo "Not found: $NAME  (run with --list to see names)"
    continue
  fi
  if [ -e "$DEST/$NAME" ]; then
    mkdir -p "$BACKUP"
    mv "$DEST/$NAME" "$BACKUP/$NAME-$STAMP"
    echo "Kept your old copy at $BACKUP/$NAME-$STAMP"
  fi
  cp -R "$SRC/$NAME" "$DEST/$NAME"
  echo "Installed $NAME -> $DEST/$NAME"
  case "$NAME" in
    session-handoff-60|session-refresh)
      echo "  Next: open Claude Code and say: Read $NAME/SKILL.md and finish the install. Show me the settings diff first." ;;
  esac
done
echo "Done. Start a new Claude Code session to load new skills."
