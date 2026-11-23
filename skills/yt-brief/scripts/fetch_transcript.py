#!/usr/bin/env python3
"""Fetch a YouTube transcript + metadata and print clean text.

Usage:
    python fetch_transcript.py <url-or-video-id> [--out DIR]

Prints a header block (title, channel, date, duration, url) followed by the
de-duplicated transcript text. Auto-generated captions arrive as rolling
VTT cues where each cue repeats the tail of the previous one; this strips
that repetition so the model reads clean prose instead of stutter.
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

# Descriptions routinely carry emoji; on Windows the default cp1252 stdout
# raises UnicodeEncodeError and kills the run. Force UTF-8 and never die on
# a character we cannot map.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:  # pragma: no cover - Python < 3.7
    pass


def video_id(s):
    """Pull the 11-char video id out of any YouTube URL form."""
    s = s.strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", s):
        return s
    m = re.search(r"(?:v=|youtu\.be/|/shorts/|/embed/|/live/)([A-Za-z0-9_-]{11})", s)
    if not m:
        sys.exit(f"Could not find a video id in: {s}")
    return m.group(1)


def download(vid, outdir):
    cmd = [
        "yt-dlp",
        "--skip-download",
        "--write-auto-subs",
        "--write-subs",
        # NOT "en.*": that glob also matches auto-TRANSLATED tracks like
        # "en-en-CA" ("English from English (Canada)"), which are redundant and
        # routinely 429. One throttled track aborts the whole download. Naming
        # the three real English tracks keeps the request small and the run alive.
        "--sub-lang", "en,en-orig,en-US",
        "--sub-format", "vtt",
        "--write-info-json",
        "--quiet", "--no-warnings",
        "-o", os.path.join(outdir, "%(id)s.%(ext)s"),
        f"https://www.youtube.com/watch?v={vid}",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"(yt-dlp failed, falling back to youtube_transcript_api: "
              f"{r.stderr.strip().splitlines()[-1] if r.stderr.strip() else r.returncode})",
              file=sys.stderr)
        return False
    return True


def fallback(vid):
    """yt-dlp 429s often; youtube_transcript_api hits a different endpoint and
    usually still works. Still pure Python, no AI.
    Title/channel come from the public oEmbed endpoint."""
    import urllib.request
    try:
        with urllib.request.urlopen(
                f"https://www.youtube.com/oembed?url=https://youtu.be/{vid}&format=json",
                timeout=20) as resp:
            meta = json.load(resp)
    except Exception:
        meta = {}
    print(f"TITLE:    {meta.get('title', 'unknown')}")
    print(f"CHANNEL:  {meta.get('author_name', 'unknown')}")
    print("UPLOADED: unknown (fallback)")
    print("DURATION: unknown (fallback)")
    print("VIEWS:    unknown (fallback)")
    print(f"URL:      https://www.youtube.com/watch?v={vid}")
    print("\n--- TRANSCRIPT (youtube_transcript_api fallback; no description) ---")
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        segs = YouTubeTranscriptApi().fetch(vid)
        print(re.sub(r"\s+", " ", " ".join(s.text for s in segs)).strip())
    except Exception as e:
        sys.exit(f"Both yt-dlp and youtube_transcript_api failed: {e}\n"
                 "Try again later or from another network (never transcribe with a model).")


TAG = re.compile(r"<[^>]+>")
CUE = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{3}\s+-->")


def parse_vtt(path):
    """VTT -> list of lines, with rolling-caption duplication removed."""
    lines = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if not line.strip():
                continue
            if line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
                continue
            if CUE.search(line):
                continue
            line = TAG.sub("", line).strip()
            line = line.replace("&nbsp;", " ").replace("&amp;", "&")
            line = line.replace("&#39;", "'").replace("&quot;", '"')
            line = line.replace("&lt;", "<").replace("&gt;", ">")
            if not line:
                continue
            # Rolling captions repeat the previous cue's text verbatim.
            if lines and (line == lines[-1] or line in lines[-1]):
                continue
            lines.append(line)
    return lines


def stitch(lines):
    """Join lines, dropping any prefix a line shares with what came before."""
    text = ""
    for line in lines:
        if not text:
            text = line
            continue
        # Trim the longest suffix of `text` that prefixes `line`.
        overlap = 0
        for n in range(min(len(line), 200), 3, -1):
            if text.endswith(line[:n]):
                overlap = n
                break
        text += line[overlap:] if overlap else " " + line
    return re.sub(r"\s+", " ", text).strip()


def pick_sub(outdir, vid):
    """Prefer a manual English track over the auto-generated one."""
    cands = glob.glob(os.path.join(outdir, f"{vid}*.vtt"))
    if not cands:
        return None
    manual = [c for c in cands if "-orig" not in c and ".en." in c]
    return (manual or cands)[0]


def hhmmss(seconds):
    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        return "unknown"
    return f"{seconds // 3600:d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--out", default=None, help="keep downloads in this dir")
    args = ap.parse_args()

    vid = video_id(args.url)
    tmp = args.out or tempfile.mkdtemp(prefix="ytbrief-")
    os.makedirs(tmp, exist_ok=True)
    if not download(vid, tmp):
        fallback(vid)
        return

    info = {}
    info_path = os.path.join(tmp, f"{vid}.info.json")
    if os.path.exists(info_path):
        with open(info_path, encoding="utf-8") as fh:
            info = json.load(fh)

    print(f"TITLE:    {info.get('title', 'unknown')}")
    print(f"CHANNEL:  {info.get('uploader', 'unknown')}")
    print(f"UPLOADED: {info.get('upload_date', 'unknown')}")
    print(f"DURATION: {hhmmss(info.get('duration'))}")
    print(f"VIEWS:    {info.get('view_count', 'unknown')}")
    print(f"URL:      https://www.youtube.com/watch?v={vid}")

    desc = (info.get("description") or "").strip()
    if desc:
        print("\n--- DESCRIPTION ---")
        print(desc[:2000])

    sub = pick_sub(tmp, vid)
    print("\n--- TRANSCRIPT ---")
    if not sub:
        print("(no captions available for this video)")
        return
    print(stitch(parse_vtt(sub)))


if __name__ == "__main__":
    main()
