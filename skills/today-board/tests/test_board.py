"""Run: python tests/test_board.py   (standard library only, uses a temp folder)"""
import contextlib, io, json, os, sys, tempfile, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import board  # noqa: E402


def run(*args):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        try:
            code = board.main(list(args))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
            out.write(str(e.code))
    return code, out.getvalue()


class BoardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.f = str(Path(self.tmp.name) / "TODAY.json")
        self.assertEqual(run("--file", self.f, "init")[0], 0)

    def tearDown(self):
        self.tmp.cleanup()

    def data(self):
        return json.loads(Path(self.f).read_text(encoding="utf-8"))

    def test_add_check_uncheck(self):
        run("--file", self.f, "add", "Call", "the", "plumber", "--group", "Home", "--due", "Fri")
        items = [it for g in self.data()["groups"] for it in g["items"]]
        self.assertEqual(items[0]["text"], "Call the plumber")
        self.assertEqual(items[0]["due"], "Fri")
        self.assertEqual(run("--file", self.f, "check", "plumber")[0], 0)
        self.assertTrue([it for g in self.data()["groups"] for it in g["items"]][0]["done"])
        self.assertEqual(run("--file", self.f, "uncheck", "PLUMBER")[0], 0)
        self.assertFalse([it for g in self.data()["groups"] for it in g["items"]][0]["done"])

    def test_duplicate_add_is_ignored(self):
        run("--file", self.f, "add", "Book dentist")
        run("--file", self.f, "add", "book dentist")
        self.assertEqual(sum(len(g["items"]) for g in self.data()["groups"]), 1)

    def test_ambiguous_check_changes_nothing(self):
        run("--file", self.f, "add", "Email the printer")
        run("--file", self.f, "add", "Email the venue")
        code, out = run("--file", self.f, "check", "email")
        self.assertEqual(code, 2)
        self.assertIn("more than one", out)
        self.assertFalse(any(it["done"] for g in self.data()["groups"] for it in g["items"]))
        self.assertEqual(run("--file", self.f, "check", "nothing like this")[0], 2)

    def test_refuses_secrets(self):
        fake_key = "sk-" + "A1b2C3d4" * 3          # built at runtime, never a real key
        for bad in ("wifi password: hunter22", "use " + fake_key, "card 4111 1111 1111 1111", "ssn is 123-45-6789"):
            code, out = run("--file", self.f, "add", bad)
            self.assertNotEqual(code, 0, bad)
            self.assertIn("Refused", out)
        for flags in (["--due", "password: hunter22"], ["--link", "https://site.example/?token=abc123"],
                      ["--note", "pin is 4455"], ["--group", "api key: " + fake_key]):
            code, out = run("--file", self.f, "add", "Harmless text", *flags)
            self.assertNotEqual(code, 0, flags)
        self.assertEqual(sum(len(g["items"]) for g in self.data()["groups"]), 0)
        self.assertEqual(run("--file", self.f, "add", "Pin the poster up, then token of thanks to the team")[0], 0)

    def test_bad_json_is_a_clear_error(self):
        Path(self.f).write_text("{not json", encoding="utf-8")
        code, out = run("--file", self.f, "list")
        self.assertEqual(code, 1)
        self.assertIn("not valid JSON", out)

    def test_check_already_done_is_noop(self):
        run("--file", self.f, "add", "Water plants")
        run("--file", self.f, "check", "Water")
        item = self.data()["groups"][0]["items"][0]
        code, out = run("--file", self.f, "check", item["id"])
        self.assertEqual(code, 0)
        self.assertIn("already done", out)
        self.assertEqual(self.data()["groups"][0]["items"][0]["done_at"], item["done_at"])

    def test_link_must_be_https(self):
        code, _ = run("--file", self.f, "add", "Read this", "--link", "javascript:alert(1)")
        self.assertNotEqual(code, 0)

    def test_clear_done_archives(self):
        run("--file", self.f, "add", "One")
        run("--file", self.f, "add", "Two")
        run("--file", self.f, "check", "One")
        run("--file", self.f, "clear-done")
        texts = [it["text"] for g in self.data()["groups"] for it in g["items"]]
        self.assertEqual(texts, ["Two"])
        arch = list((Path(self.tmp.name) / "archive").glob("*.json"))
        self.assertEqual(json.loads(arch[0].read_text(encoding="utf-8"))[0]["text"], "One")

    def test_today_section_and_render_escapes(self):
        src = Path(self.tmp.name) / "top-section-input.json"
        src.write_text(json.dumps({"events": [{"time": "9 AM", "title": "</script><b>standup</b>", "extra": "dropped"}],
                                   "only_you": [{"text": "Sign the lease"}], "waiting": []}), encoding="utf-8")
        self.assertEqual(run("--file", self.f, "today", str(src))[0], 0)
        t = self.data()["today"]
        self.assertEqual(t["events"][0], {"time": "9 AM", "title": "</script><b>standup</b>"})
        out = Path(self.tmp.name) / "board.html"
        self.assertEqual(run("--file", self.f, "render", "--out", str(out))[0], 0)
        html = out.read_text(encoding="utf-8")
        block = html.split('id="board-data">', 1)[1].split("</script>", 1)[0]
        self.assertNotIn("<", block)                       # embedded data cannot break out of its script tag
        self.assertEqual(json.loads(block)["today"]["only_you"][0]["text"], "Sign the lease")
        self.assertTrue(html.startswith("<!doctype html>"))

    def test_sample_init(self):
        self.assertEqual(run("--file", self.f, "init", "--sample", "--force")[0], 0)
        self.assertIn("example", self.data()["note"].lower())
        code, out = run("--file", self.f, "list")
        self.assertEqual(code, 0)
        self.assertIn("4 open", out)

    def test_atomic_write_leaves_no_temp_files(self):
        run("--file", self.f, "add", "Something")
        self.assertEqual([p.name for p in Path(self.tmp.name).glob(".today-*")], [])


    def test_top_title_secret_refused_without_mutation(self):
        before = Path(self.f).read_bytes()
        src = Path(self.tmp.name) / "top-section-input.json"
        src.write_text(json.dumps({"title": "password: fictional", "events": []}), encoding="utf-8")
        code, out = run("--file", self.f, "today", str(src))
        self.assertEqual(code, 1)
        self.assertIn("Refused", out)
        self.assertEqual(Path(self.f).read_bytes(), before)

    def test_each_add_field_secret_refused_without_mutation(self):
        before = Path(self.f).read_bytes()
        for field, value in (("due", "password: fictional"), ("link", "https://x.example/?token=abc123"),
                             ("group", "password: fictional"), ("note", "pin: 1234")):
            with self.subTest(field=field):
                code, out = run("--file", self.f, "add", "Read article", "--" + field, value)
                self.assertEqual(code, 1)
                self.assertIn("Refused", out)
                self.assertEqual(Path(self.f).read_bytes(), before)

    def test_artifact_archive_workflow_contract(self):
        skill = (HERE.parent / "SKILL.md").read_text(encoding="utf-8")
        template = (HERE.parent / "templates" / "board.html").read_text(encoding="utf-8")
        self.assertIn("col.where('status', '!=', 'archived').onSnapshot", template)
        self.assertNotIn("col.onSnapshot", template)
        self.assertIn('where: [["status", "!=", "archived"]]', skill)
        self.assertIn('where: [["status", "==", "archived"]]', skill)
        for phrase in ("follow every `next_cursor`", "Finish reading all pages before writing", "older than 30 days",
                       "at most 50", "valid `done_at`", "Re-read on version conflicts"):
            self.assertIn(phrase, skill)
        self.assertNotIn('`delete` each item whose `status` is `done`', skill)


if __name__ == "__main__":
    unittest.main(verbosity=1)
