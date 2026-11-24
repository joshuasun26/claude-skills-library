"""Today Board, offline mode. Standard-library Python 3.9+, any OS.

Keeps the board in one JSON file (default ~/.today-board/TODAY.json, or set TODAY_BOARD_FILE)
and renders it to a self-contained HTML page you open in a browser.

  python board.py init [--sample]           create the file (with fictional example data)
  python board.py add "Call the plumber" [--group Home] [--note ...] [--due "Fri"] [--link https://...]
  python board.py check "plumber"           mark done (match by id or words); uncheck works the same
  python board.py list [--all] [--json]     open items by group (--all includes done)
  python board.py clear-done                move done items to archive/YYYY-MM-DD.json
  python board.py today today.json          replace the top section (events, only_you, waiting)
  python board.py render [--out board.html] write the offline page

Exit codes: 0 ok, 1 error, 2 no match or more than one match (nothing changed).
"""
import argparse, datetime as dt, hashlib, json, os, re, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "templates" / "board.html"
SECRET = re.compile(
    r"(password|passwd|passcode|\bpin\b|api[ _-]?key|secret|token|bearer|ssn|social security)\s*(?:is\s+|[:=#]\s*)\S"
    r"|\b(sk-[A-Za-z0-9]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,}|xox[bpa]-[\w-]{10,})"
    r"|\b\d{3}-\d{2}-\d{4}\b|\b(?:\d[ -]?){13,19}\b", re.I)
TODAY_KEYS = {"events": ("time", "title", "where"), "only_you": ("text", "why"), "waiting": ("who", "what", "since")}


def board_path(arg=None):
    return Path(arg or os.environ.get("TODAY_BOARD_FILE") or Path.home() / ".today-board" / "TODAY.json")


def now_iso():
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def load(path):
    if not path.exists():
        raise SystemExit(f"No board at {path}. Run: python board.py init")
    data = read_json(path)
    if not isinstance(data, dict):
        raise SystemExit(f"{path} is not a board file (expected a JSON object).")
    data.setdefault("groups", [])
    data.setdefault("today", {})
    return data


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"{path} is not valid JSON (line {e.lineno}). Fix it, or restore a copy from the archive folder.")


def write_atomic(path, text):
    """Write a temp file in the same folder, then rename it over the old one."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".today-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        for attempt in range(3):
            try:
                os.replace(tmp, path)
                return
            except PermissionError:      # Windows: another program has the file open for a moment
                if attempt == 2:
                    raise
                time.sleep(0.3)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def save(path, data):
    data["updated_at"] = now_iso()
    write_atomic(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def refuse_secrets(*texts):
    for t in texts:
        if t and SECRET.search(str(t)):
            raise SystemExit("Refused: that looks like a password, key, card or ID number. Keep those in a password manager, "
                             "not on the board. If it is not a secret, reword it (for example, leave out the number).")


def new_id(text):
    stamp = dt.datetime.now().strftime("%Y%m%d%H%M%S%f")
    return "t-" + hashlib.sha1((stamp + text).encode("utf-8")).hexdigest()[:10]


def all_items(data):
    for g in data["groups"]:
        for it in g.get("items", []):
            yield g, it


def find(data, query, want_done):
    q = query.strip().lower()
    exact = [(g, it) for g, it in all_items(data) if it.get("id") == query]
    if exact:
        return exact
    return [(g, it) for g, it in all_items(data) if q in (it.get("text") or "").lower() and bool(it.get("done")) == want_done]


def cmd_init(a):
    p = board_path(a.file)
    if p.exists() and not a.force:
        raise SystemExit(f"{p} already exists. Use --force to replace it.")
    data = {"date": dt.date.today().isoformat(), "today": {}, "groups": [{"name": "To-do", "items": []}]}
    if a.sample:
        data = json.loads((HERE.parent / "examples" / "TODAY.example.json").read_text(encoding="utf-8"))
    save(p, data)
    print(f"created {p}")


def cmd_add(a):
    p = board_path(a.file)
    data = load(p)
    text = " ".join(a.text).strip()
    if not text:
        raise SystemExit("Nothing to add.")
    refuse_secrets(text, a.note, a.due, a.link, a.group)
    if a.link and not a.link.startswith("https://"):
        raise SystemExit("Links must start with https://")
    grp = next((g for g in data["groups"] if g["name"].lower() == a.group.lower()), None)
    if grp is None:
        grp = {"name": a.group, "items": []}
        data["groups"].append(grp)
    dup = [it for it in grp["items"] if not it.get("done") and (it.get("text") or "").lower() == text.lower()]
    if dup:
        print(f"already on the board: {dup[0]['text']}")
        return
    it = {"id": new_id(text), "text": text, "done": False, "done_at": None}
    for k in ("note", "due", "link"):
        if getattr(a, k):
            it[k] = getattr(a, k)
    grp["items"].append(it)
    save(p, data)
    print(f"added to {grp['name']}: {text}")


def _set_done(a, done):
    p = board_path(a.file)
    data = load(p)
    hits = find(data, " ".join(a.query), want_done=not done)
    if len(hits) != 1:
        print("no match" if not hits else "more than one match, be more specific:")
        for g, it in hits:
            print(f"  [{it['id']}] {g['name']}: {it['text']}")
        return 2
    g, it = hits[0]
    if bool(it.get("done")) == done:
        print(("already done: " if done else "already open: ") + it["text"])
        return 0
    it["done"], it["done_at"] = done, (now_iso() if done else None)
    save(p, data)
    print(("checked off: " if done else "reopened: ") + it["text"])
    return 0


def cmd_list(a):
    data = load(board_path(a.file))
    if a.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return
    t = data.get("today", {})
    for key, label in (("events", "Calls and events"), ("only_you", "Only you"), ("waiting", "Waiting on")):
        rows = t.get(key) or []
        if rows:
            print(label)
            for r in rows:
                print("  - " + " | ".join(str(r[f]) for f in TODAY_KEYS[key] if r.get(f)))
    n = 0
    for g in data["groups"]:
        rows = [it for it in g.get("items", []) if a.all or not it.get("done")]
        if rows:
            print(g["name"])
            for it in rows:
                n += not it.get("done")
                extra = f"  ({it['due']})" if it.get("due") else ""
                print(f"  [{'x' if it.get('done') else ' '}] {it['text']}{extra}")
    print(f"{n} open")


def cmd_clear(a):
    p = board_path(a.file)
    data = load(p)
    moved = []
    for g in data["groups"]:
        moved += [dict(it, group=g["name"]) for it in g.get("items", []) if it.get("done")]
        g["items"] = [it for it in g.get("items", []) if not it.get("done")]
    if not moved:
        print("nothing done to clear")
        return
    arch = p.parent / "archive" / f"{dt.date.today().isoformat()}.json"
    old = read_json(arch) if arch.exists() else []
    write_atomic(arch, json.dumps(old + moved, indent=2, ensure_ascii=False) + "\n")
    save(p, data)
    print(f"moved {len(moved)} done item(s) to {arch}")


def cmd_today(a):
    p = board_path(a.file)
    data = load(p)
    src = read_json(a.source)
    if not isinstance(src, dict):
        raise SystemExit("The top-section file must be a JSON object with events, only_you and waiting lists.")
    refuse_secrets(src.get("title"))
    out = {"title": str(src["title"])} if src.get("title") else {}
    for key, fields in TODAY_KEYS.items():
        rows = []
        for r in src.get(key) or []:
            if not isinstance(r, dict):
                raise SystemExit(f"Each row in {key} must be an object with fields {', '.join(fields)}.")
            row = {f: str(r[f]) for f in fields if r.get(f)}
            refuse_secrets(*row.values())
            rows.append(row)
        out[key] = rows
    out["updated_at"] = now_iso()
    data["today"] = out
    save(p, data)
    print("top section updated: " + ", ".join(f"{len(out[k])} {k}" for k in TODAY_KEYS))


def render(data, template=TEMPLATE):
    html = Path(template).read_text(encoding="utf-8")
    blob = json.dumps({"today": data.get("today", {}), "groups": data.get("groups", [])}, ensure_ascii=False)
    blob = blob.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    marker = '<script type="application/json" id="board-data">{}</script>'
    if marker not in html:
        raise SystemExit("template is missing the board-data block")
    page = html.replace(marker, f'<script type="application/json" id="board-data">{blob}</script>')
    head, sep, body = page.partition("</style>")
    if not sep:
        head, body = "", page
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            + head + sep + "\n</head><body>\n" + body.lstrip() + "\n</body></html>\n")


def cmd_render(a):
    p = board_path(a.file)
    out = Path(a.out) if a.out else p.parent / "board.html"
    write_atomic(out, render(load(p)))
    print(f"wrote {out}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Today Board offline mode")
    ap.add_argument("--file", help="board file (default ~/.today-board/TODAY.json or $TODAY_BOARD_FILE)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("init"); s.add_argument("--sample", action="store_true"); s.add_argument("--force", action="store_true"); s.set_defaults(fn=cmd_init)
    s = sub.add_parser("add"); s.add_argument("text", nargs="+"); s.add_argument("--group", default="To-do")
    s.add_argument("--note"); s.add_argument("--due"); s.add_argument("--link"); s.set_defaults(fn=cmd_add)
    s = sub.add_parser("check"); s.add_argument("query", nargs="+"); s.set_defaults(fn=lambda a: _set_done(a, True))
    s = sub.add_parser("uncheck"); s.add_argument("query", nargs="+"); s.set_defaults(fn=lambda a: _set_done(a, False))
    s = sub.add_parser("list"); s.add_argument("--all", action="store_true"); s.add_argument("--json", action="store_true"); s.set_defaults(fn=cmd_list)
    s = sub.add_parser("clear-done"); s.set_defaults(fn=cmd_clear)
    s = sub.add_parser("today"); s.add_argument("source", help="JSON file with events, only_you, waiting"); s.set_defaults(fn=cmd_today)
    s = sub.add_parser("render"); s.add_argument("--out"); s.set_defaults(fn=cmd_render)
    a = ap.parse_args(argv)
    return a.fn(a) or 0


if __name__ == "__main__":
    sys.exit(main())
