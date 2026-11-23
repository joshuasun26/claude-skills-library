"""Run: python tests/test_triage.py   (no dependencies)
Reproduces the two failure shapes this skill was built to catch:
  1. You sent an email, nobody answered, and a triage that only reads UNREAD inbound
     mail never sees it (the "waiting on them" miss).
  2. Someone replied on a thread you started, you glanced at it on your phone, it lost
     UNREAD, and the reply vanished from every later run (the "they replied" miss).
"""
import datetime as dt, json, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import triage  # noqa: E402

CFG = {
    "owner_emails": ["owner@example.com"],
    "timezone": "America/Los_Angeles",
    "followup_business_days": 2,
    "vip": {"tier1": [{"name": "Lender partner", "emails": ["@lender.example"]}]},
    "noise": {"from_patterns": ["noreply@*"], "labels": ["CATEGORY_PROMOTIONS"]},
    "never_nudge": [],
}

THREADS = [
    {   # 1. owner sent Tue 3:04pm PT, then forwarded it to a third person; no reply
        "thread_id": "t-waiting", "subject": "following up, and two asks",
        "messages": [
            {"id": "m1", "from": "owner@example.com", "to": ["partner@org.example", "assistant@org.example"],
             "date": "2026-09-22T22:00:00Z", "labels": ["SENT"], "snippet": "Thank you. Two asks. I'll send the deck Friday."},
            {"id": "m2", "from": "owner@example.com", "to": ["friend@other.example"],
             "date": "2026-09-22T22:45:00Z", "labels": ["SENT"], "snippet": "Fwd"},
        ]},
    {   # 2. VIP replied on owner's thread, already READ (no UNREAD label)
        "thread_id": "t-replied", "subject": "checking in",
        "messages": [
            {"id": "m3", "from": "owner@example.com", "to": ["sam@lender.example"],
             "date": "2026-09-21T20:20:00Z", "labels": ["SENT"], "snippet": "can you send me"},
            {"id": "m4", "from": "Sam <sam@lender.example>", "to": ["owner@example.com"],
             "date": "2026-09-22T00:25:00Z", "labels": ["INBOX", "IMPORTANT"], "snippet": "Sure. Leads..."},
        ]},
    {   # 3. reply where owner is only cc'd
        "thread_id": "t-cc", "subject": "intro",
        "messages": [
            {"id": "m5", "from": "owner@example.com", "to": ["client@x.example"], "cc": ["sam@lender.example"],
             "date": "2026-09-20T18:00:00Z", "labels": ["SENT"], "snippet": "meet Sam"},
            {"id": "m6", "from": "client@x.example", "to": ["sam@lender.example"], "cc": ["owner@example.com"],
             "date": "2026-09-23T18:00:00Z", "labels": ["INBOX"], "snippet": "thanks, call at 5?"},
        ]},
    {   # 4. noise
        "thread_id": "t-noise", "subject": "digest",
        "messages": [{"id": "m7", "from": "noreply@news.example", "to": ["owner@example.com"],
                      "date": "2026-09-24T14:00:00Z", "labels": ["UNREAD", "INBOX"], "snippet": "digest"}]},
    {   # 5. sent yesterday: clock not due yet
        "thread_id": "t-fresh", "subject": "quick q",
        "messages": [{"id": "m8", "from": "owner@example.com", "to": ["agent@y.example"],
                      "date": "2026-09-23T20:00:00Z", "labels": ["SENT"], "snippet": "quick q"}]},
]

NOW = dt.datetime(2026, 9, 24, 22, 30, tzinfo=dt.timezone.utc)  # Thu 3:30pm PT


def run():
    tmp = tempfile.mkdtemp()
    state_p, digest_p = os.path.join(tmp, "state.json"), os.path.join(tmp, "digest.txt")
    plan = triage.classify(CFG, THREADS, {}, NOW)
    ids = lambda k: [i["thread_id"] for i in plan[k]]
    assert ids("waiting_due") == ["t-waiting"], plan["waiting_due"]
    w = plan["waiting_due"][0]
    assert w["business_days"] == 2 and w["waiting_on_message_id"] == "m1", w
    assert "partner@org.example" in w["to"]
    assert "t-replied" in ids("they_replied") and "t-cc" in ids("they_replied")
    assert plan["they_replied"][0]["tier"] == "tier1"          # VIP sorts first
    assert ids("noise") == ["t-noise"]
    assert ids("waiting_not_due") == ["t-fresh"]
    assert any("send the deck" in c["text"] for c in plan["commitments_found"])
    assert plan["urgent"], "tier1 reply must be flagged urgent"

    # persist-before-notify and dedupe by message id
    text = triage.commit(plan, {}, state_p, digest_p, CFG)
    assert "REPLIED" in text and "NO REPLY 2 biz days" in text, text
    state = json.load(open(state_p, encoding="utf-8"))
    assert "msg:m4" in state["notified"] and "nudge:t-waiting:m1" in state["notified"]
    plan2 = triage.classify(CFG, THREADS, state, NOW)
    assert not plan2["they_replied"] and not plan2["waiting_due"], "second run must be silent"
    assert triage.digest_text(plan2, CFG) == ""

    assert "t-waiting" in state["waiting"] and "t-fresh" in state["waiting"]
    md = open(os.path.join(tmp, "WAITING-AND-PROMISES.md"), encoding="utf-8").read()
    assert "Waiting on them" in md and "send the deck" in md, md

    # weekend math: Fri 4pm send is 1 business day old on Mon 4pm+, 2 on Tue
    tz = triage.tz_of(CFG)
    fri = dt.datetime(2026, 9, 25, 23, 0, tzinfo=dt.timezone.utc)
    assert triage.business_days_between(fri, fri + dt.timedelta(days=3, minutes=5), tz) == 1
    assert triage.business_days_between(fri, fri + dt.timedelta(days=4, minutes=5), tz) == 2
    counsel_inline_regression()
    dst_regression()
    print("all tests passed")



# Fixture (fictional): the owner asked a law office for a call; the reply was typed in
# ALL CAPS INSIDE the quoted copy of the owner's email, so the snippet shows only the quoted
# header. A triage that trusts the snippet reports it once with nothing new, then dedupes it.
OWNER_ASK = ("Hi Jordan,\n\nThanks for the notes you sent over last week. They helped a lot.\n\n"
             "Could we schedule a call this week? Tuesday or Wednesday morning would work on my side.\n\n"
             "Best,\nOwner")
COUNSEL_BODY = ("EXAMPLE LAW OFFICE\n\nOWNER:\n\nFrom: Owner <owner@example.com>\n"
                "Sent: Thursday, November 5, 2026 5:00 PM\nTo: Jordan Doe <jordan@doelaw.example>\n"
                "Subject: Re: follow-up questions\n\nhi jordan,\n\nThanks for the notes you sent over last "
                "week. They helped a lot.\n\nCould we schedule a call this week? Tuesday or Wednesday morning "
                "would work on my side.\n\nI CAN TALK THIS AFTERNOON. CALL ME AT (555) 010-0199.\n\nJORDAN\n\n"
                "Best,\nOwner")
COUNSEL_THREAD = {
    "thread_id": "t-counsel", "subject": "follow-up questions",
    "messages": [
        {"id": "d1", "from": "owner@example.com", "to": ["jordan@doelaw.example"],
         "date": "2026-11-06T01:00:00Z", "labels": ["SENT"], "snippet": OWNER_ASK[:180], "body": OWNER_ASK},
        {"id": "d2", "from": "Jordan Doe <jordan@doelaw.example>", "from_name": "Jordan Doe",
         "to": ["owner@example.com"], "date": "2026-11-06T14:00:00Z",
         "labels": ["UNREAD", "IMPORTANT", "INBOX"],
         "snippet": "EXAMPLE LAW OFFICE OWNER: From: Owner Sent: Thursday",
         "body": COUNSEL_BODY},
    ]}


def counsel_inline_regression():
    tmp = tempfile.mkdtemp()
    state_p, digest_p = os.path.join(tmp, "state.json"), os.path.join(tmp, "digest.txt")
    fri = dt.datetime(2026, 11, 6, 16, 5, tzinfo=dt.timezone.utc)      # Fri 8:05 AM PT run
    plan = triage.classify(CFG, [COUNSEL_THREAD], {}, fri)
    item = plan["they_replied"][0]
    # 1. the reply typed inside the quote is found, case differences ignored
    assert "I CAN TALK THIS AFTERNOON" in item["new_text"], item["new_text"]
    assert "(555) 010-0199" in item["new_text"]
    assert "schedule a call" not in item["new_text"].lower(), "owner's own text leaked in"
    assert item["inline_reply"], "snippet hides the reply; must be flagged inline"
    triage.commit(plan, {}, state_p, digest_p, CFG)
    state = json.load(open(state_p, encoding="utf-8"))

    # 2. same day, later run: already reported, so silent (the no-repeat rule holds)
    later = triage.classify(CFG, [COUNSEL_THREAD], state, fri + dt.timedelta(hours=8))
    assert not later["still_open"] and later["duplicates"], later

    # 3. Monday run, still unanswered and UNREAD: it MUST come back, with all three reasons
    mon = dt.datetime(2026, 11, 9, 16, 5, tzinfo=dt.timezone.utc)
    plan3 = triage.classify(CFG, [COUNSEL_THREAD], state, mon)
    assert [i["thread_id"] for i in plan3["still_open"]] == ["t-counsel"], plan3
    why = plan3["still_open"][0]["reasons"]
    assert "counsel" in why and "you asked for a call/meeting" in why
    assert any(r.startswith("unread+important") for r in why), why
    assert "STILL OPEN 3d" in triage.digest_text(plan3, CFG)
    triage.commit(plan3, state, state_p, digest_p, CFG)
    state = json.load(open(state_p, encoding="utf-8"))
    # 4. at most once a day, then again tomorrow
    assert not triage.classify(CFG, [COUNSEL_THREAD], state, mon + dt.timedelta(hours=4))["still_open"]
    assert triage.classify(CFG, [COUNSEL_THREAD], state, mon + dt.timedelta(days=1))["still_open"]

    # 5. once the owner replies, it stops
    answered = json.loads(json.dumps(COUNSEL_THREAD))
    answered["messages"].append({"id": "d3", "from": "owner@example.com", "to": ["jordan@doelaw.example"],
                                 "date": "2026-11-09T17:00:00Z", "labels": ["SENT"], "snippet": "Tuesday works"})
    p5 = triage.classify(CFG, [answered], state, mon + dt.timedelta(days=1))
    assert not p5["still_open"] and not p5["they_replied"]

    # 6. ordinary non-counsel reply, read, no ask: reported once, never nags
    plain = {"thread_id": "t-plain", "subject": "thanks", "messages": [
        {"id": "p1", "from": "owner@example.com", "to": ["a@b.example"], "date": "2026-11-05T18:00:00Z",
         "labels": ["SENT"], "snippet": "Here is the flyer."},
        {"id": "p2", "from": "a@b.example", "to": ["owner@example.com"], "date": "2026-11-06T18:00:00Z",
         "labels": ["INBOX"], "snippet": "Thanks!"}]}
    st = {"notified": {"msg:p2": {"at": "2026-11-06T19:00:00+00:00", "bucket": "they_replied",
                                  "thread_id": "t-plain"}}}
    assert not triage.classify(CFG, [plain], st, mon)["still_open"]

    # 7. edge cases for the counsel and ask detectors
    for dom in ("lawnpros.example", "outlaw.example", "clawmachine.example", "lawson-fin.example",
                "jesquire.example", "illegalsoft.example"):
        assert not triage.is_counsel(f"x@{dom}", "", CFG), dom
    for dom in ("doelaw.example", "doe-law.example", "roelegal.example", "acmelawgroup.example"):
        assert triage.is_counsel(f"x@{dom}", "", CFG), dom
    assert not triage.is_counsel("legal@vendor.example", "", CFG)
    assert triage.is_counsel("x@firm.example", "Jane Roe, Esq.", CFG)
    for no in ("Is the product available in blue?", "Great call to action", "New Zoom lens"):
        assert not triage.ASK_RX.search(no), no
    for yes in ("Can we meet Tuesday?", "Could we schedule a call?", "can we talk this week",
                "Would you have time for another quick call?", "Are you free Monday?"):
        assert triage.ASK_RX.search(yes), yes
    quoted_ask = "Thanks!\n\nOn Mon, Nov 2 Owner wrote:\n> Are you free Monday for a quick call?"
    assert not triage.ASK_RX.search(triage.owner_text(quoted_ask))
    nt = triage.extract_new_text("Date: Tuesday works\nY\nSent from my iPhone", ["see you"])
    assert "Date: Tuesday works" in nt and "Y" in nt.splitlines() and "iPhone" not in nt, nt
    rewrapped = triage.extract_new_text(
        "Got it.\n> Thanks for the notes you sent over last week. They\n> helped a lot.",
        [OWNER_ASK])
    assert rewrapped == "Got it.", rewrapped



def dst_regression():
    """DST ended Sun 2026-11-01. A fixed -7 offset put 11:30 PM PST Sunday on Monday."""
    tz = triage.tz_of(CFG)
    sun_late = dt.datetime(2026, 11, 2, 7, 30, tzinfo=dt.timezone.utc)   # Sun 11/1 11:30 PM PST
    assert sun_late.astimezone(tz).date().isoformat() == "2026-11-01"
    legacy = triage.tz_of({"utc_offset_hours": -7})
    assert sun_late.astimezone(legacy).date().isoformat() == "2026-11-02"   # the old bug
    summer = dt.datetime(2026, 7, 1, 6, 30, tzinfo=dt.timezone.utc)      # Tue 6/30 11:30 PM PDT
    assert summer.astimezone(tz).date().isoformat() == "2026-06-30"
    # business days across the change: Fri 10/30 3 PM PDT -> Tue 11/3 3:05 PM PST = 2
    fri = dt.datetime(2026, 10, 30, 22, 0, tzinfo=dt.timezone.utc)
    tue = dt.datetime(2026, 11, 3, 23, 5, tzinfo=dt.timezone.utc)
    assert triage.business_days_between(fri, tue, tz) == 2
    # once-a-day resurfacing uses the local date: Sun 11:30 PM and Mon 8 AM are two days
    st = {"notified": {"msg:d2": {"at": "2026-11-06T16:05:00+00:00", "bucket": "they_replied",
                                  "thread_id": "t-counsel"}},
          "resurfaced": {"msg:d2": "2026-11-08"}}
    p_sun = triage.classify(CFG, [COUNSEL_THREAD], st, dt.datetime(2026, 11, 9, 7, 30, tzinfo=dt.timezone.utc))
    assert not p_sun["still_open"], "Sun 11:30 PM PST is still 11/8 locally"
    p_mon = triage.classify(CFG, [COUNSEL_THREAD], st, dt.datetime(2026, 11, 9, 16, 0, tzinfo=dt.timezone.utc))
    assert p_mon["still_open"]


if __name__ == "__main__":
    run()
