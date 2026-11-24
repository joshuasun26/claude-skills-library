"""Tests for send_check.py. Run from the skill folder:  python -B tests/test_send_check.py
Uses temporary folders only. All names and numbers are fictional."""
import datetime as dt
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import send_check as sc  # noqa: E402

CARD = "4111" + " 1111" * 3
PHONE = "555" + "0100" + "123"


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.cfg = dict(sc.DEFAULTS)
        self.cfg.update({
            "banned_words": ["honestly", "circling back"],
            "send_log": str(self.dir / "send-log.jsonl"),
            "optout_file": str(self.dir / "optouts.txt"),
        })

    def tearDown(self):
        self.tmp.cleanup()

    def draft(self, text, name="draft.txt"):
        p = self.dir / name
        p.write_text(text, encoding="utf-8")
        return str(p)

    def run_main(self, argv):
        out, err = io.StringIO(), io.StringIO()
        cfg_path = self.dir / "config.json"
        cfg_path.write_text(json.dumps(self.cfg), encoding="utf-8")
        with redirect_stdout(out), redirect_stderr(err):
            try:
                code = sc.main(argv + ["--config", str(cfg_path)])
            except SystemExit as e:
                code = e.code
        return code, out.getvalue(), err.getvalue()


class ScanTests(Base):
    def test_clean_draft(self):
        flags, notes = sc.scan("Hi Priya, thanks for the note. See you Tuesday.", self.cfg)
        self.assertEqual(flags, [])

    def test_banned_word_whole_word_only(self):
        flags, _ = sc.scan("Honestly, this works.", self.cfg)
        self.assertTrue(any("honestly" in f for f in flags))
        flags, _ = sc.scan("We are dishonestlyish testing.", self.cfg)
        self.assertFalse(any("honestly" in f for f in flags))

    def test_banned_phrase(self):
        flags, _ = sc.scan("Just circling back on this.", self.cfg)
        self.assertTrue(any("circling back" in f for f in flags))

    def test_em_dash_and_toggle(self):
        text = "The plan \u2014 as promised \u2014 is ready."
        flags, _ = sc.scan(text, self.cfg)
        self.assertTrue(any("em dash" in f for f in flags))
        self.cfg["allow_em_dash"] = True
        flags, _ = sc.scan(text, self.cfg)
        self.assertFalse(any("em dash" in f for f in flags))

    def test_exclamation_limit(self):
        self.assertEqual(sc.scan("Congrats!", self.cfg)[0], [])
        flags, _ = sc.scan("Congrats! Great news! Talk soon!", self.cfg)
        self.assertTrue(any("exclamation" in f for f in flags))

    def test_emoji(self):
        flags, _ = sc.scan("See you soon \U0001F600", self.cfg)
        self.assertTrue(any("emoji" in f for f in flags))

    def test_card_and_ssn(self):
        flags, _ = sc.scan(f"Card {CARD} and SSN 123-45-6789", self.cfg)
        self.assertTrue(any("16-digit" in f for f in flags))
        self.assertTrue(any("Social Security" in f for f in flags))

    def test_phone_is_note_not_flag(self):
        flags, notes = sc.scan(f"Call me at {PHONE}.", self.cfg)
        self.assertEqual(flags, [])
        self.assertTrue(any("phone-shaped" in n for n in notes))

    def test_dates_not_flagged(self):
        flags, _ = sc.scan("Closing is 2026-11-23, payment due 12/01/2026.", self.cfg)
        self.assertEqual(flags, [])

    def test_placeholder(self):
        flags, _ = sc.scan("Hi [Name], see you {{date}}. TODO add link", self.cfg)
        self.assertEqual(len([f for f in flags if "placeholder" in f]), 3)

    def test_attachment_mentioned_but_missing(self):
        flags, _ = sc.scan("Attached is the proposal.", self.cfg)
        self.assertTrue(any("nothing is attached" in f for f in flags))

    def test_attachment_present_and_missing_file(self):
        real = self.dir / "proposal.pdf"
        real.write_bytes(b"%PDF fictional")
        flags, _ = sc.scan("Attached is the proposal.", self.cfg, [str(real)])
        self.assertEqual(flags, [])
        flags, _ = sc.scan("Attached is the proposal.", self.cfg, [str(self.dir / "nope.pdf")])
        self.assertTrue(any("not found" in f for f in flags))

    def test_attached_but_not_mentioned_is_note(self):
        real = self.dir / "a.pdf"
        real.write_bytes(b"x")
        flags, notes = sc.scan("Hi Marcus, quick update.", self.cfg, [str(real)])
        self.assertEqual(flags, [])
        self.assertTrue(notes)


class DupeOptoutLogTests(Base):
    def test_log_then_dupe(self):
        text = "Hi Priya,\n\nThe proposal is ready."
        to = sc.split_to(["Priya@Example.com"])
        sc.log_send(text, to, self.cfg, subject="Proposal")
        flags, _ = sc.dupe_check("hi priya the proposal is ready", to, self.cfg)
        self.assertTrue(any("same message" in f for f in flags))
        flags, _ = sc.dupe_check("Different text", sc.split_to(["marcus@example.com"]), self.cfg)
        self.assertEqual(flags, [])

    def test_same_subject_flag_and_recent_note(self):
        to = ["priya@example.com"]
        sc.log_send("First version", to, self.cfg, subject="Proposal")
        flags, _ = sc.dupe_check("Second version", to, self.cfg, subject="proposal")
        self.assertTrue(any("same subject" in f for f in flags))
        flags, notes = sc.dupe_check("Third version", to, self.cfg)
        self.assertEqual(flags, [])
        self.assertTrue(any("not a repeat" in n for n in notes))

    def test_dupe_window(self):
        to = ["priya@example.com"]
        old = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=30)
        sc.log_send("Same text", to, self.cfg, now=old)
        flags, notes = sc.dupe_check("Same text", to, self.cfg)
        self.assertEqual((flags, notes), ([], []))

    def test_log_has_no_body(self):
        sc.log_send("Secret body words", ["priya@example.com"], self.cfg)
        raw = Path(self.cfg["send_log"]).read_text(encoding="utf-8")
        self.assertNotIn("Secret", raw)

    def test_phone_normalization(self):
        self.assertEqual(sc.normalize_addr("+1 555 0100 123"), PHONE)
        self.assertEqual(sc.normalize_addr("1" + PHONE), PHONE)

    def test_optout(self):
        flags, _ = sc.optout_check([PHONE], self.cfg)
        self.assertTrue(any("not found" in f for f in flags))
        Path(self.cfg["optout_file"]).write_text(f"# people who asked not to be texted\n1{PHONE}\n", encoding="utf-8")
        flags, _ = sc.optout_check([PHONE], self.cfg)
        self.assertTrue(any("opt-out list" in f for f in flags))
        flags, _ = sc.optout_check(["5550100999"], self.cfg)
        self.assertEqual(flags, [])


class CliTests(Base):
    def test_exit_codes(self):
        code, out, _ = self.run_main(["scan", self.draft("Hi Priya, see you Tuesday.")])
        self.assertEqual(code, 0)
        self.assertIn("CLEAN", out)
        code, out, _ = self.run_main(["scan", self.draft("Honestly, attached.")])
        self.assertEqual(code, 1)

    def test_missing_draft_is_usage_error(self):
        code, _, err = self.run_main(["scan", str(self.dir / "missing.txt")])
        self.assertEqual(code, 2)
        self.assertIn("not found", err)

    def test_bad_args(self):
        code, _, _ = self.run_main(["dupe", self.draft("x")])
        self.assertEqual(code, 2)

    def test_log_and_dupe_cli(self):
        d = self.draft("Hi Marcus, the dates work.")
        code, out, _ = self.run_main(["log", d, "--to", "marcus@example.com", "--ref", "fictional-1"])
        self.assertEqual(code, 0)
        code, out, _ = self.run_main(["dupe", d, "--to", "MARCUS@example.com"])
        self.assertEqual(code, 1)
        self.assertIn("already sent", out)

    def test_utf8_bom_draft(self):
        p = self.dir / "bom.txt"
        p.write_bytes("\ufeffHi Priya, see you Tuesday.".encode("utf-8"))
        code, _, _ = self.run_main(["scan", str(p)])
        self.assertEqual(code, 0)


class CriticRegressionTests(Base):
    def test_optout_csv_and_display_email(self):
        Path(self.cfg["optout_file"]).write_text("6265550123,Pat Lee,2026-01-02\nPat Lee <pat@example.com>\n", encoding="utf-8")
        code, out, err = self.run_main(["optout", "--to", "626-555-0123", "--to", "pat@example.com"])
        self.assertEqual(code, 1, err)
        self.assertIn("6265550123 is on", out)
        self.assertIn("pat@example.com is on", out)

    def test_display_email_log_matches_bare_address(self):
        sc.log_send("Proposal ready", sc.split_to(["Priya Shah <priya@example.com>"]), self.cfg)
        flags, _ = sc.dupe_check("Proposal ready", sc.split_to(["priya@example.com"]), self.cfg)
        self.assertTrue(any("same message" in f for f in flags))

    def test_each_review_date_and_zip_shape(self):
        for text in ("Meet 2026-11-23 at 10", "on 11-23-2026", "between 2020-2025"):
            with self.subTest(text=text):
                self.assertEqual(sc.scan(text, self.cfg)[0], [])
        flags, notes = sc.scan("ZIP 90210-1234", self.cfg)
        self.assertEqual(flags, [])
        self.assertTrue(any("ZIP+4" in n for n in notes))
        self.assertTrue(sc.scan(CARD, self.cfg)[0])

    def test_utf16_optouts_and_utf8_bom(self):
        p = Path(self.cfg["optout_file"])
        for encoding in ("utf-16", "utf-8-sig"):
            with self.subTest(encoding=encoding):
                p.write_bytes("Pat Lee <pat@example.com>".encode(encoding))
                code, out, err = self.run_main(["optout", "--to", "pat@example.com"])
                self.assertEqual(code, 1, err)
                self.assertIn("is on the opt-out list", out)
                self.assertNotIn("Traceback", err)

    def test_cp1252_log_does_not_crash_or_hide_duplicate(self):
        row = {"ts": dt.datetime.now(dt.timezone.utc).isoformat(), "to": ["pat@example.com"],
               "hash": sc.short_hash(sc.normalize_text("Ready")), "ref": "caf\u00e9"}
        Path(self.cfg["send_log"]).write_bytes((json.dumps(row, ensure_ascii=False) + "\n").encode("cp1252"))
        code, out, err = self.run_main(["dupe", self.draft("Ready"), "--to", "pat@example.com"])
        self.assertEqual(code, 1, err)
        self.assertIn("same message", out)
        self.assertNotIn("Traceback", err)

    def test_remaining_unicode_error_is_file_error(self):
        from unittest.mock import patch
        with patch.object(sc, "optout_check", side_effect=UnicodeError("bad encoding")):
            code, out, err = self.run_main(["optout", "--to", "pat@example.com"])
        self.assertEqual(code, 2)
        self.assertNotIn("Traceback", err)

    def test_source_and_approval_contract(self):
        skill = (Path(__file__).resolve().parent.parent / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("do not pass them to `fact-check`", skill)
        self.assertIn("Memory, summaries and earlier sessions never qualify", skill)
        self.assertIn("A PASS is never a yes", skill)
        self.assertNotIn("they will not read first", skill)


if __name__ == "__main__":
    unittest.main(verbosity=1)
