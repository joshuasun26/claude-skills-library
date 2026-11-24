"""send_check.py - mechanical pre-send checks for the send-critic skill.

Standard library only, Python 3.9+. It never sends anything and never decides the verdict.

  python send_check.py scan  DRAFT [--attached FILE ...] [--config PATH]
  python send_check.py dupe  DRAFT --to ADDR [--to ADDR ...] [--subject TEXT] [--config PATH]
  python send_check.py optout --to ADDR [--to ADDR ...] [--config PATH]
  python send_check.py log   DRAFT --to ADDR [--channel email|text] [--subject TEXT] [--ref ID] [--config PATH]

DRAFT is a UTF-8 text file, or "-" to read standard input.
Exit codes: 0 nothing flagged, 1 something to look at, 2 usage or file error.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXAMPLE_CONFIG = HERE.parent / "config" / "send-critic.example.json"
USER_CONFIG = Path("~/.claude/send-critic/config.json")

DEFAULTS = {
    "banned_words": [],
    "allow_em_dash": False,
    "max_exclamations": 1,
    "allow_emoji": False,
    "account_digit_run": 8,
    "optout_file": "~/.claude/send-critic/optouts.txt",
    "send_log": "~/.claude/send-critic/send-log.jsonl",
    "dupe_window_days": 14,
}

EM_DASH = "\u2014"
EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\u2600-\u27bf\u2b00-\u2bff\ufe0f\u200d]"
)
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
# A run of digits, allowing single spaces or dashes between groups (card numbers, account numbers).
DIGIT_RUN_RE = re.compile(r"(?<![\d-])\d(?:[ -]?\d){5,}(?![\d-])")
# Dates and year ranges that look like digit runs but are not account numbers.
DATE_LIKE_RE = re.compile(r"\d{4}-\d{1,2}-\d{1,2}|\d{1,2}-\d{1,2}-\d{2,4}|\d{4} ?- ?\d{4}")
ZIP4_RE = re.compile(r"\d{5}-\d{4}")
EMAIL_RE = re.compile(r"[\w.+'-]+@[\w-]+(?:\.[\w-]+)+")
ATTACH_RE = re.compile(
    r"\b(attached|attachments?|attach|attaching|enclosed|please find|see the (?:attached|enclosed))\b", re.I
)
PLACEHOLDER_RE = re.compile(
    r"\[[A-Za-z][A-Za-z .'/-]{0,30}\]|\{\{?\s*\w+\s*\}?\}|<insert[^>]*>|\bTODO\b|\bTBD\b|\bXXX+\b",
    re.I,
)
# Curly quotes folded to straight ones so "I'm" in a config matches a curly "I'm" in a draft.
QUOTE_FOLD = {0x2018: "'", 0x2019: "'", 0x201C: '"', 0x201D: '"'}


def expand(p):
    return Path(os.path.expandvars(str(p))).expanduser()


def load_config(path=None):
    cfg = dict(DEFAULTS)
    if path:
        src = expand(path)
        if not src.is_file():
            raise SystemExit(f"error: config not found: {src}")
    else:
        src = expand(USER_CONFIG)
        if not src.is_file():
            src = EXAMPLE_CONFIG
    if src.is_file():
        try:
            cfg.update(json.loads(src.read_text(encoding="utf-8")))
        except (ValueError, OSError) as e:
            raise SystemExit(f"error: cannot read config {src}: {e}")
    cfg["_source"] = str(src)
    return cfg


def read_draft(arg):
    if arg == "-":
        data = sys.stdin.buffer.read()
    else:
        p = expand(arg)
        if not p.is_file():
            raise SystemExit(f"error: draft not found: {p}")
        data = p.read_bytes()
    return data.decode("utf-8-sig", errors="replace")


def fold_quotes(text):
    return text.translate(QUOTE_FOLD)


def read_text_file(p):
    """Read a file the user keeps by hand. Handles a UTF-8 BOM and UTF-16 (Excel 'Unicode Text')."""
    data = p.read_bytes()
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return data.decode("utf-16", errors="replace")
    return data.decode("utf-8-sig", errors="replace")


def normalize_text(text):
    text = fold_quotes(text).lower().replace("\r\n", "\n")
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())


def short_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def normalize_addr(addr):
    a = addr.strip()
    m = EMAIL_RE.search(a)
    if m:
        return m.group(0).lower()
    digits = re.sub(r"\D", "", a)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    return digits or a.lower()


def split_to(values):
    out = []
    for v in values or []:
        out += [normalize_addr(x) for x in re.split(r"[,;]", v) if x.strip()]
    return sorted(set(out))


def line_of(text, index):
    return text.count("\n", 0, index) + 1


def scan(text, cfg, attached=None):
    """Return (flags, notes). Each item is a plain-English string."""
    flags, notes = [], []
    lower = fold_quotes(text).lower()

    for word in cfg.get("banned_words", []):
        w = " ".join(fold_quotes(str(word)).split())
        if not w:
            continue
        body = r"\s+".join(re.escape(part) for part in w.lower().split(" "))
        pat = re.compile(r"(?<!\w)" + body + r"(?!\w)")
        for m in pat.finditer(lower):
            flags.append(f"banned word '{w}' at line {line_of(text, m.start())}")

    if not cfg.get("allow_em_dash", False):
        n = text.count(EM_DASH)
        if n:
            flags.append(f"{n} em dash(es); first at line {line_of(text, text.index(EM_DASH))}")

    bangs = text.count("!")
    limit = int(cfg.get("max_exclamations", 1))
    if bangs > limit:
        flags.append(f"{bangs} exclamation marks (limit {limit})")

    if not cfg.get("allow_emoji", False):
        found = EMOJI_RE.findall(text)
        if found:
            flags.append(f"{len(found)} emoji character(s)")

    for m in SSN_RE.finditer(text):
        flags.append(f"looks like a Social Security number at line {line_of(text, m.start())}")
    run = int(cfg.get("account_digit_run", 8))
    for m in DIGIT_RUN_RE.finditer(text):
        g = m.group(0)
        if SSN_RE.fullmatch(g) or DATE_LIKE_RE.fullmatch(g):
            continue
        digits = re.sub(r"\D", "", g)
        if len(digits) < run:
            continue
        where = f"line {line_of(text, m.start())}"
        if ZIP4_RE.fullmatch(g):
            notes.append(f"ZIP+4-shaped number at {where}; confirm it is a ZIP code")
        elif len(digits) == 10 or (len(digits) == 11 and digits.startswith("1")):
            notes.append(f"phone-shaped number at {where}; confirm it is meant to be shared")
        else:
            flags.append(f"{len(digits)}-digit number at {where}; could be an account, card or ID number")

    for m in PLACEHOLDER_RE.finditer(text):
        flags.append(f"unfilled placeholder '{m.group(0)}' at line {line_of(text, m.start())}")

    attached = [a for a in (attached or []) if a]
    mentions = ATTACH_RE.search(text)
    if mentions and not attached:
        flags.append(f"body mentions '{mentions.group(0)}' at line {line_of(text, mentions.start())} but nothing is attached")
    if attached and not mentions:
        notes.append("files are attached but the body never mentions them; make sure that is intended")
    for a in attached:
        p = expand(a)
        if not p.is_file():
            flags.append(f"attachment not found on disk: {a}")
        elif p.stat().st_size == 0:
            flags.append(f"attachment is empty: {a}")
    return flags, notes


def read_log(cfg):
    p = expand(cfg["send_log"])
    rows = []
    if p.is_file():
        for line in read_text_file(p).splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if not isinstance(row, dict):
                continue
            to = row.get("to") or []
            if isinstance(to, str):
                to = [to]
            row["to"] = [normalize_addr(x) for x in to if isinstance(x, str)]
            rows.append(row)
    return rows


def parse_ts(s):
    if isinstance(s, str) and s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        t = dt.datetime.fromisoformat(s)
    except (TypeError, ValueError):
        return None
    if t.tzinfo is None:
        t = t.replace(tzinfo=dt.timezone.utc)
    return t


def dupe_check(text, to, cfg, subject=None, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    body_h = short_hash(normalize_text(text))
    window = dt.timedelta(days=float(cfg.get("dupe_window_days", 14)))
    flags, notes = [], []
    for row in read_log(cfg):
        ts = parse_ts(row.get("ts"))
        overlap = sorted(set(row.get("to", [])) & set(to))
        if not overlap or ts is None or now - ts > window:
            continue
        when = row.get("ts")
        if row.get("hash") == body_h:
            flags.append(f"same message already sent to {', '.join(overlap)} at {when}")
        elif subject and row.get("subject_hash") == short_hash(normalize_text(subject)):
            flags.append(f"same subject already sent to {', '.join(overlap)} at {when}; check it is not a repeat")
        elif now - ts <= dt.timedelta(hours=24):
            notes.append(f"you messaged {', '.join(overlap)} at {when}; make sure this is not a repeat")
    return flags, notes


def optout_check(to, cfg):
    p = expand(cfg["optout_file"])
    if not p.is_file():
        return [f"opt-out list not found at {p}; cannot confirm anyone's opt-out status"], []
    listed = set()
    # One email or phone per line works, and so does a CSV export: every cell is checked.
    for line in read_text_file(p).splitlines():
        line = line.split("#", 1)[0]
        for cell in re.split(r"[,;\t]", line):
            cell = cell.strip().strip('"').strip()
            if not cell:
                continue
            emails = EMAIL_RE.findall(cell)
            if emails:
                listed.update(e.lower() for e in emails)
                continue
            n = normalize_addr(cell)
            if n.isdigit() and len(n) >= 7 and not DATE_LIKE_RE.fullmatch(cell):
                listed.add(n)
    hits = [t for t in to if t in listed]
    return [f"{h} is on the opt-out list" for h in hits], []


def log_send(text, to, cfg, channel="email", subject=None, ref=None, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    row = {
        "ts": now.isoformat(timespec="seconds"),
        "channel": channel,
        "to": to,
        "hash": short_hash(normalize_text(text)),
        "subject_hash": short_hash(normalize_text(subject)) if subject else None,
        "ref": ref,
    }
    p = expand(cfg["send_log"])
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row) + "\n")
    return row


def report(title, flags, notes):
    print(f"{title}: {'FLAGGED' if flags else 'CLEAN'}")
    for f in flags:
        print(f"  FLAG  {f}")
    for n in notes:
        print(f"  NOTE  {n}")
    return 1 if flags else 0


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"error: {message}", file=sys.stderr)
        raise SystemExit(2)


def main(argv=None):
    ap = Parser(description="Mechanical pre-send checks for send-critic. Never sends.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("draft")
    s.add_argument("--attached", action="append", default=[])
    d = sub.add_parser("dupe")
    d.add_argument("draft")
    d.add_argument("--to", action="append", required=True)
    d.add_argument("--subject")
    o = sub.add_parser("optout")
    o.add_argument("--to", action="append", required=True)
    lg = sub.add_parser("log")
    lg.add_argument("draft")
    lg.add_argument("--to", action="append", required=True)
    lg.add_argument("--channel", default="email", choices=["email", "text", "other"])
    lg.add_argument("--subject")
    lg.add_argument("--ref")
    for p in (s, d, o, lg):
        p.add_argument("--config")
    args = ap.parse_args(argv)

    try:
        cfg = load_config(args.config)
        if args.cmd == "scan":
            return report("scan", *scan(read_draft(args.draft), cfg, args.attached))
        to = split_to(args.to)
        if not to:
            print("error: --to is empty", file=sys.stderr)
            return 2
        if args.cmd == "dupe":
            return report("duplicate check", *dupe_check(read_draft(args.draft), to, cfg, args.subject))
        if args.cmd == "optout":
            return report("opt-out check", *optout_check(to, cfg))
        row = log_send(read_draft(args.draft), to, cfg, args.channel, args.subject, args.ref)
        print(f"logged: {json.dumps(row)}")
        return 0
    except SystemExit as e:
        if isinstance(e.code, str):
            print(e.code, file=sys.stderr)
            return 2
        raise
    except (OSError, UnicodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
