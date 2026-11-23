#!/usr/bin/env python3
"""inbox-triage engine. Standard library only. Deterministic: the agent fetches mail with
its Gmail MCP, writes normalized threads to JSON, and this script decides the buckets,
runs the follow-up clock, dedupes by message id, and persists state BEFORE any notice.

Commands
  classify  --config C --threads T --state S [--now ISO] --out PLAN
  commit    --config C --plan PLAN --state S --digest-out FILE  (persist first, then digest)
  commitment add|done|list --state S [--text ..] [--who ..] [--due YYYY-MM-DD] [--id ..]
  draft     --state S --thread ID [--draft-id ..] [--kind reply|nudge] [--check]
State lives in state.json; every commit/draft also rewrites WAITING-AND-PROMISES.md beside it.

Thread JSON (a list):
  {"thread_id": "...", "subject": "...", "labels": [...],
   "messages": [{"id": "...", "from": "a@example.com", "from_name": "Ann", "to": [...],
                 "cc": [...], "date": "2026-09-22T22:04:47Z", "labels": [...],
                 "snippet": "..."}]}
"""
import argparse, datetime as dt, json, os, re, tempfile

UTC = dt.timezone.utc


def load(path, default):
    if not path or not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_atomic(path, data):
    d = os.path.dirname(os.path.abspath(path))
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp-", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def parse_ts(s):
    t = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    return t if t.tzinfo else t.replace(tzinfo=UTC)


def tz_of(cfg):
    """Owner's local time zone. Prefer an IANA name ("timezone": "America/Los_Angeles") so
    daylight saving is handled; a fixed "utc_offset_hours" is legacy and drifts an hour twice
    a year."""
    name = cfg.get("timezone") or ("" if "utc_offset_hours" in cfg else "America/Los_Angeles")
    if name:
        try:
            from zoneinfo import ZoneInfo
            return ZoneInfo(name)
        except Exception:
            pass
    return dt.timezone(dt.timedelta(hours=cfg.get("utc_offset_hours", -8)))


def business_days_between(start, end, tz, holidays=()):
    """Whole business days elapsed, in the owner's local time.
    Sent Tue 3pm -> 1 at Wed 3pm, 2 at Thu 3pm. Weekends and holidays do not count."""
    if end <= start:
        return 0
    cur, e, hol = start.astimezone(tz), end.astimezone(tz), set(holidays or [])
    days = 0
    while True:
        nxt = cur + dt.timedelta(days=1)
        while nxt.weekday() >= 5 or nxt.date().isoformat() in hol:
            nxt += dt.timedelta(days=1)
        if nxt > e:
            return days
        days += 1
        cur = nxt


def addr(x):
    m = re.search(r"[\w.+'-]+@[\w.-]+", x or "")
    return m.group(0).lower() if m else (x or "").lower()


def matches(a, patterns):
    a = addr(a)
    dom = a.split("@")[-1]
    for p in patterns or []:
        p = p.lower().strip()
        if not p:
            continue
        if "*" in p:
            if re.fullmatch(re.escape(p).replace(r"\*", ".*"), a):
                return True
        elif p.startswith("@"):
            if a.endswith(p):
                return True
        elif a == p or dom == p:
            return True
    return False


def vip_tier(a, cfg):
    for tier in ("tier1", "tier2", "tier3"):
        for entry in cfg.get("vip", {}).get(tier, []):
            if matches(a, entry.get("emails", [])):
                return tier, entry.get("name", "")
    return None, ""


TIER_RANK = {"tier1": 0, "tier2": 1, "tier3": 2}

# Escalation: an unanswered inbound that was already reported once still comes back, at most
# once a day, when any of these hold, so an important reply is never deduped away.
ASK_RX = re.compile(
    r"\b((?:a|another|quick|phone) (?:quick )?call\b(?! to action)|call (?:me|you)\b|"
    r"(?:on|over|a|quick) zoom\b|meet(?:ing)? (?:up|with you|for coffee|on|this|next|tomorrow|today)\b|"
    r"can we (?:meet|talk|chat|connect)\b|get together|hop on\b|time to (?:talk|meet|connect|chat)|"
    r"are you (?:free|available)|your availability|"
    r"(?:schedule|set up) (?:a|some) (?:time|call|meeting))", re.I)
COUNSEL_RX = re.compile(r"(\besq\b|\battorneys?\b|\blaw (?:firm|office|group)\b|\bcounsel\b)", re.I)
COUNSEL_LABEL_RX = re.compile(r"(law|legal|lawfirm|lawgroup|lawoffices?|attorneys?|esq)$", re.I)
NOT_COUNSEL_LABELS = {"outlaw", "inlaw", "bylaw", "claw", "illegal", "paralegal"}
BLOCK_START_RX = re.compile(r"^\s*(from:|on .{3,200} wrote:|-+ ?original message|_{5,})", re.I)
BLOCK_FIELD_RX = re.compile(r"^\s*(from|sent|date|to|cc|subject):", re.I)
SIGNATURE_RX = re.compile(r"^(sent from my \w+|get outlook for \w+)", re.I)


def _norm(line):
    return re.sub(r"\s+", " ", re.sub(r"^[>\s]+", "", line)).strip().lower()


def _header_lines(lines):
    """Indexes of quote-header lines: a From:/'On .. wrote:' start plus the Sent/To/Cc/Subject
    fields directly under it. A sender's own 'Date: Tuesday works' line is NOT a header."""
    hdr = set()
    for i, ln in enumerate(lines):
        if not BLOCK_START_RX.match(ln):
            continue
        if ln.strip().lower().startswith("from:") and not any(
                re.match(r"^\s*(sent|date):", x, re.I) for x in lines[i + 1:i + 4]):
            continue
        hdr.add(i)
        j = i + 1
        while j < len(lines) and BLOCK_FIELD_RX.match(lines[j]):
            hdr.add(j)
            j += 1
    return hdr


def owner_text(body):
    """The owner's own words in a message: everything above the first quote header."""
    lines = (body or "").splitlines()
    hdr = _header_lines(lines)
    cut = min(hdr) if hdr else len(lines)
    return "\n".join(ln for ln in lines[:cut] if not ln.lstrip().startswith(">"))


def extract_new_text(body, prior_texts):
    """Lines in a reply that the owner did not write, wherever they sit, including text typed
    INSIDE the quoted copy of the owner's email (inline replies, often in ALL CAPS). Header
    lines, signatures and lines that only repeat earlier messages are dropped. Comparison
    ignores case, whitespace and leading '>' quote marks; long lines also count as repeats
    when a client re-wrapped them."""
    seen, joined = set(), []
    for p in prior_texts or []:
        for ln in (p or "").splitlines():
            n = _norm(ln)
            if n:
                seen.add(n)
                joined.append(n)
    flat = " ".join(joined)
    lines = (body or "").splitlines()
    hdr = _header_lines(lines)
    out = []
    for i, ln in enumerate(lines):
        n = _norm(ln)
        if not n or i in hdr or n in seen or SIGNATURE_RX.match(n):
            continue
        if len(n) >= (8 if ln.lstrip().startswith(">") else 20) and n in flat:
            continue
        out.append(ln.strip().lstrip(">").strip())
    return "\n".join(out)


def inline_reply(body, new_text):
    """True when some of the new text sits BELOW the first quote header, i.e. the sender
    typed the answer inside the quoted copy. Snippets and quote-strippers miss these."""
    lines = (body or "").splitlines()
    hdr = _header_lines(lines)
    if not hdr or not new_text:
        return False
    below = {_norm(ln) for ln in lines[min(hdr) + 1:]}
    return any(_norm(n) in below for n in new_text.splitlines())


def is_counsel(sender, name, cfg):
    if matches(sender, cfg.get("counsel", [])):
        return True
    labels = sender.split("@")[-1].lower().split(".")[:-1]
    if any(COUNSEL_LABEL_RX.search(l) and l not in NOT_COUNSEL_LABELS for l in labels):
        return True
    return bool(COUNSEL_RX.search(name or ""))


def escalation_reasons(msgs, last, labels, sender, cfg, now, mine):
    why = []
    if is_counsel(sender, last.get("from_name", ""), cfg):
        why.append("counsel")
    prior_mine = [m for m in msgs[:-1] if mine(m)]
    if prior_mine:
        p = prior_mine[-1]
        if ASK_RX.search(owner_text(p.get("body")) if p.get("body") else p.get("snippet", "")):
            why.append("you asked for a call/meeting")
    age_h = (now - parse_ts(last["date"])).total_seconds() / 3600
    if "UNREAD" in labels and "IMPORTANT" in labels and age_h >= 24:
        why.append(f"unread+important {int(age_h // 24)}d")
    return why


COMMIT_RX = re.compile(
    r"\b(i'?ll|i will|i'?m going to|will send|will get back|will follow up|"
    r"will have (?:it|that)|i can get you)\b[^.?!\n]{3,120}", re.I)


def classify(cfg, threads, state, now):
    owners = {o.lower() for o in cfg["owner_emails"]}
    tz = tz_of(cfg)
    fdays = cfg.get("followup_business_days", 2)
    window = cfg.get("waiting_window_days", 21)
    hol = cfg.get("holidays", [])
    notified = set(state.get("notified", {}))
    suppressed = cfg.get("suppress", [])
    noise_from = cfg.get("noise", {}).get("from_patterns", [])
    noise_labels = set(cfg.get("noise", {}).get("labels", []))
    no_nudge = cfg.get("never_nudge", [])
    plan = {"generated": now.isoformat(), "they_replied": [], "needs_reply": [],
            "waiting_due": [], "waiting_not_due": [], "cc_fyi": [], "noise": [],
            "suppressed": [], "duplicates": [], "still_open": [], "commitments_found": []}
    resurfaced = state.get("resurfaced", {})
    today = now.astimezone(tz).date().isoformat()

    for t in threads:
        msgs = sorted(t.get("messages", []), key=lambda m: parse_ts(m["date"]))
        if not msgs:
            continue

        def mine(m):
            return addr(m.get("from")) in owners

        last = msgs[-1]
        base = {"thread_id": t["thread_id"], "subject": t.get("subject") or last.get("subject", ""),
                "last_message_id": last["id"], "last_date": last["date"]}

        for m in msgs:
            if mine(m):
                for hit in COMMIT_RX.finditer(m.get("snippet", "")):
                    plan["commitments_found"].append({
                        "key": f"commit:{m['id']}:{hit.start()}", "thread_id": t["thread_id"],
                        "to": [addr(x) for x in m.get("to", [])], "text": hit.group(0).strip(),
                        "date": m["date"]})

        if mine(last):
            # WAITING ON THEM. The clock starts at the first owner message after the last
            # inbound one, so a later forward or self-note does not reset it.
            last_in = max((i for i, m in enumerate(msgs) if not mine(m)), default=-1)
            first_out = msgs[last_in + 1]
            ext = [addr(x) for x in first_out.get("to", []) + first_out.get("cc", [])
                   if addr(x) not in owners]
            ext = [x for x in ext if not (matches(x, suppressed) or matches(x, noise_from)
                                          or matches(x, no_nudge))]
            if not ext or (now - parse_ts(first_out["date"])).days > window:
                continue
            tiers = [vip_tier(x, cfg) for x in ext]
            best = min(tiers, key=lambda tv: TIER_RANK.get(tv[0], 9))
            age = business_days_between(parse_ts(first_out["date"]), now, tz, hol)
            item = dict(base, kind="waiting", to=ext, since=first_out["date"],
                        business_days=age, tier=best[0], vip_name=best[1],
                        waiting_on_message_id=first_out["id"],
                        dedupe_key=f"nudge:{t['thread_id']}:{first_out['id']}")
            if age < fdays:
                plan["waiting_not_due"].append(item)
            elif item["dedupe_key"] in notified:
                plan["duplicates"].append(item)
            else:
                plan["waiting_due"].append(item)
            continue

        sender = addr(last.get("from"))
        if matches(sender, suppressed):
            plan["suppressed"].append(dict(base, sender=sender))
            continue
        tier, vname = vip_tier(sender, cfg)
        labels = set(last.get("labels", [])) | set(t.get("labels", []))
        if not tier and (matches(sender, noise_from) or labels & noise_labels):
            plan["noise"].append(dict(base, sender=sender))
            continue

        to_me = any(addr(x) in owners for x in last.get("to", []))
        cc_me = any(addr(x) in owners for x in last.get("cc", []))
        item = dict(base, sender=sender, sender_name=last.get("from_name", ""), tier=tier,
                    vip_name=vname, addressed="to" if to_me else ("cc" if cc_me else "bcc/list"),
                    unread="UNREAD" in labels, snippet=last.get("snippet", "")[:300],
                    dedupe_key=f"msg:{last['id']}")
        item["new_text"], item["inline_reply"] = "", None    # None = no body was supplied
        if last.get("body"):
            new = extract_new_text(last["body"], [m.get("body") or m.get("snippet", "")
                                                  for m in msgs[:-1]])
            item["new_text"] = new[:1500]
            item["inline_reply"] = inline_reply(last["body"], new)
        if item["dedupe_key"] in notified:
            first = (state.get("notified", {}).get(item["dedupe_key"]) or {}).get("at")
            first_day = parse_ts(first).astimezone(tz).date().isoformat() if first else ""
            why = escalation_reasons(msgs, last, labels, sender, cfg, now, mine)
            if (why and first_day != today
                    and resurfaced.get(item["dedupe_key"]) != today):
                # Reported before, still unanswered, and it matters: bring it back once a day
                # until the owner replies. Dedupe must never bury these.
                item.update(kind="still_open", reasons=why,
                            age_days=(now - parse_ts(last["date"])).days)
                plan["still_open"].append(item)
            else:
                plan["duplicates"].append(item)
        elif any(mine(m) for m in msgs):
            # THEY REPLIED on a thread the owner wrote in. Read status is irrelevant,
            # and a cc-only reply still counts when the owner started or joined the thread.
            item["kind"] = "they_replied"
            plan["they_replied" if (to_me or tier or cfg.get("cc_replies_count", True))
                 else "cc_fyi"].append(item)
        elif to_me or tier:
            item["kind"] = "needs_reply"
            plan["needs_reply"].append(item)
        else:
            item["kind"] = "cc_fyi"
            plan["cc_fyi"].append(item)

    for k in ("they_replied", "needs_reply", "waiting_due", "still_open"):
        plan[k].sort(key=lambda i: (TIER_RANK.get(i.get("tier"), 9), i["last_date"]))
    known = set(state.get("commitments", {}))
    plan["commitments_found"] = [c for c in plan["commitments_found"] if c["key"] not in known]
    plan["urgent"] = [i["dedupe_key"] for k in ("they_replied", "needs_reply", "waiting_due")
                      for i in plan[k] if i.get("tier") == "tier1"]
    return plan


def digest_text(plan, cfg, limit=900):
    name = cfg.get("assistant_name", "Inbox")
    lines = [f"[{name}] {plan['generated'][:16].replace('T', ' ')} UTC"]

    def who(i):
        return (i.get("vip_name") or i.get("sender_name") or i.get("sender")
                or ", ".join(i.get("to", [])))

    for i in plan.get("still_open", []):
        lines.append(f"STILL OPEN {i['age_days']}d ({', '.join(i['reasons'])}): {who(i)} - "
                     f"{i['subject'][:40]}")
    for i in plan["they_replied"]:
        lines.append(f"REPLIED: {who(i)} - {i['subject'][:50]}")
    for i in plan["needs_reply"]:
        lines.append(f"NEW: {who(i)} - {i['subject'][:50]}")
    for i in plan["waiting_due"]:
        lines.append(f"NO REPLY {i['business_days']} biz days: {who(i)} - {i['subject'][:45]}")
    for c in plan["commitments_found"]:
        lines.append(f"YOU SAID: {c['text'][:60]}")
    if len(lines) == 1:
        return ""
    out, total = [], 0
    for n, ln in enumerate(lines):
        if total + len(ln) + 1 > limit - 30:
            out.append(f"+{len(lines) - n} more in the full digest")
            break
        out.append(ln)
        total += len(ln) + 1
    return "\n".join(out)


def commit(plan, state, state_path, digest_path, cfg):
    stamp = plan.get("generated") or dt.datetime.now(UTC).isoformat()  # run time, not wall clock
    n = state.setdefault("notified", {})
    for k in ("they_replied", "needs_reply", "waiting_due"):
        for i in plan[k]:
            n[i["dedupe_key"]] = {"at": stamp, "bucket": k, "thread_id": i["thread_id"]}
    rs = state.setdefault("resurfaced", {})
    tz = tz_of(cfg)
    for i in plan.get("still_open", []):
        rs[i["dedupe_key"]] = parse_ts(stamp).astimezone(tz).date().isoformat()
    for k in [k for k in rs if k not in n]:      # pruned with notified (45 days)
        del rs[k]
    cm = state.setdefault("commitments", {})
    for x in plan["commitments_found"]:
        cm[x["key"]] = dict(x, status="open", logged=stamp)
    cutoff = parse_ts(stamp) - dt.timedelta(days=45)
    for k in [k for k, v in n.items() if parse_ts(v["at"]) < cutoff]:
        del n[k]
    state["waiting"] = {i["thread_id"]: {k: i[k] for k in ("subject", "to", "since",
                        "business_days", "waiting_on_message_id", "tier")}
                        for i in plan["waiting_due"] + plan["waiting_not_due"]}
    state["last_commit"] = stamp
    save_atomic(state_path, state)       # 1. durable state first
    export_md(state, os.path.join(os.path.dirname(os.path.abspath(state_path)), "WAITING-AND-PROMISES.md"))
    text = digest_text(plan, cfg)        # 2. only then the notice text
    with open(digest_path, "w", encoding="utf-8") as f:
        f.write(text)
    return text


def export_md(state, path):
    """Human-readable mirror of state, rewritten every commit, so any later session (or a
    person) can pick up the thread without replaying the run."""
    L = [f"# Inbox triage: open loops (as of {state.get('last_commit', '')[:16]} UTC)", ""]
    L.append("## Waiting on them")
    for tid, w in sorted(state.get("waiting", {}).items(), key=lambda kv: kv[1]["since"]):
        L.append(f"- {', '.join(w['to'])} | {w['subject']} | sent {w['since'][:10]} | "
                 f"{w['business_days']} business days | thread {tid}")
    L += ["", "## Commitments (open)"]
    for k, c in state.get("commitments", {}).items():
        if c.get("status") == "open":
            L.append(f"- {c['text']} | to {', '.join(c.get('to') or [])} | "
                     f"{(c.get('date') or c.get('logged', ''))[:10]} | due {c.get('due') or '-'} | {k}")
    L += ["", "## Drafts written (one per thread, ever)"]
    for tid, d in state.get("drafts", {}).items():
        L.append(f"- thread {tid} | draft {d.get('draft_id', '')} | {d.get('created', '')[:10]} | {d.get('kind', '')}")
    save_text(path, "\n".join(L) + "\n")


def save_text(path, text):
    d = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp-", suffix=".md")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("classify")
    for x in ("--config", "--threads", "--state", "--out"):
        a.add_argument(x, required=True)
    a.add_argument("--now")
    b = sub.add_parser("commit")
    for x in ("--config", "--plan", "--state", "--digest-out"):
        b.add_argument(x, required=True)
    c = sub.add_parser("commitment")
    c.add_argument("action", choices=["add", "done", "list"])
    c.add_argument("--state", required=True)
    for x in ("--text", "--who", "--due", "--id"):
        c.add_argument(x)
    d = sub.add_parser("draft")
    d.add_argument("--state", required=True)
    d.add_argument("--thread", required=True)
    d.add_argument("--draft-id", default="")
    d.add_argument("--kind", default="reply")
    d.add_argument("--check", action="store_true", help="exit 3 if this thread already has a draft")
    args = ap.parse_args()

    if args.cmd == "classify":
        cfg, threads, state = load(args.config, None), load(args.threads, []), load(args.state, {})
        now = parse_ts(args.now) if args.now else dt.datetime.now(UTC)
        plan = classify(cfg, threads, state, now)
        save_atomic(args.out, plan)
        print(json.dumps({k: len(v) for k, v in plan.items() if isinstance(v, list)}))
    elif args.cmd == "commit":
        cfg, plan, state = load(args.config, None), load(args.plan, None), load(args.state, {})
        text = commit(plan, state, args.state, args.digest_out, cfg)
        print(text if text else "(nothing new - send no notice)")
    elif args.cmd == "draft":
        state = load(args.state, {})
        drafts = state.setdefault("drafts", {})
        if args.check:
            if args.thread in drafts:
                print(json.dumps(drafts[args.thread]))
                return 3
            print("none")
            return 0
        drafts[args.thread] = {"draft_id": args.draft_id, "kind": args.kind,
                               "created": dt.datetime.now(UTC).isoformat()}
        save_atomic(args.state, state)
        export_md(state, os.path.join(os.path.dirname(os.path.abspath(args.state)), "WAITING-AND-PROMISES.md"))
        print("ok")
    else:
        state = load(args.state, {})
        cm = state.setdefault("commitments", {})
        now = dt.datetime.now(UTC)
        if args.action == "add":
            key = f"manual:{now.strftime('%Y%m%d%H%M%S')}"
            cm[key] = {"key": key, "text": args.text, "to": [args.who or ""], "due": args.due,
                       "status": "open", "logged": now.isoformat()}
            save_atomic(args.state, state)
            print(key)
        elif args.action == "done":
            cm[args.id]["status"] = "done"
            save_atomic(args.state, state)
            print("ok")
        else:
            for k, v in cm.items():
                if v.get("status") == "open":
                    print(f"{k} | due {v.get('due') or '-'} | {', '.join(v.get('to') or [])} | {v['text']}")


if __name__ == "__main__":
    raise SystemExit(main() or 0)
