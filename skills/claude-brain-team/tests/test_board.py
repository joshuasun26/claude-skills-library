"""Run: python tests/test_board.py   (no dependencies)
Checks the rules the board exists to enforce: no closing without real evidence, no private data
to a worker that is not cleared for it, overdue tasks get flagged, bad ids cannot escape the folder,
sync conflict copies get flagged, and non-English text works on any console."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import board  # noqa: E402


class FakeStdin:
    def __init__(self, data):
        self.buffer = io.BytesIO(data)


def run(*argv, stdin=None):
    out, err = io.StringIO(), io.StringIO()
    old = sys.stdin
    if stdin is not None:
        sys.stdin = FakeStdin(stdin)
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = board.main(list(argv))
            except SystemExit as exc:
                code = exc.code
    finally:
        sys.stdin = old
    return code, out.getvalue(), err.getvalue()


GOOD = "Task-ID: {tid}\nStatus: DONE\n## Summary\nThree apps.\n## Evidence\nhttps://example.com/apps\n## Gaps\nNone\n"


class BoardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.b = os.path.join(self.tmp.name, "board")
        os.environ["BRAIN_TEAM_POINTER"] = os.path.join(self.tmp.name, "pointer.json")
        os.environ.pop("BRAIN_TEAM_BOARD", None)
        self.assertEqual(run("--board", self.b, "init")[0], 0)

    def tearDown(self):
        os.environ.pop("BRAIN_TEAM_POINTER", None)
        self.tmp.cleanup()

    def new(self, *extra, to="muse", goal="List three free note apps"):
        code, out, err = run("--board", self.b, "new", "--to", to, "--type", "research", "--public",
                             "--goal", goal, *extra)
        self.assertEqual(code, 0, err)
        tid = [w for w in out.split() if w.startswith("T-")][0].rstrip(",")
        return tid, out

    def put_result(self, tid, text):
        (Path(self.b) / "outbox" / f"RESULT-{tid}.md").write_text(text.format(tid=tid), encoding="utf-8")

    def close(self, tid, *extra):
        return run("--board", self.b, "close", tid, "--verified", "opened the link", *extra)

    # happy path
    def test_new_prints_paste_brief_for_paste_worker(self):
        tid, out = self.new()
        self.assertIn("paste this to the worker", out)
        self.assertTrue((Path(self.b) / "inbox" / f"{tid}.md").exists())

    def test_good_result_closes(self):
        tid, _ = self.new()
        self.put_result(tid, GOOD)
        code, _, err = self.close(tid)
        self.assertEqual(code, 0, err)
        self.assertTrue((Path(self.b) / "done" / f"{tid}.md").exists())
        self.assertTrue((Path(self.b) / "done" / f"RESULT-{tid}.md").exists())
        self.assertFalse((Path(self.b) / "inbox" / f"{tid}.md").exists())
        self.assertIn("Verified: opened the link", (Path(self.b) / "done" / f"{tid}.md").read_text(encoding="utf-8"))

    def test_pasted_reply_then_close(self):
        tid, _ = self.new()
        reply = Path(self.tmp.name) / "reply.txt"
        reply.write_text("Here are three apps.\n## Evidence\nhttps://example.com/apps\n", encoding="utf-8")
        self.assertEqual(run("--board", self.b, "result", tid, "--file", str(reply), "--status", "DONE")[0], 0)
        self.assertEqual(self.close(tid)[0], 0)

    def test_board_remembered_after_init(self):
        tid, _ = self.new()
        code, out, _ = run("list")  # no --board: uses the pointer written by init
        self.assertEqual(code, 0)
        self.assertIn(tid, out)

    # evidence rules
    def test_close_refuses_without_result(self):
        tid, _ = self.new()
        code, _, err = self.close(tid)
        self.assertEqual(code, 1)
        self.assertIn("not evidence", err)

    def test_close_refuses_placeholder_evidence(self):
        for ev in ("", "None", "n/a", "TBD"):
            tid, _ = self.new()
            self.put_result(tid, "Task-ID: {tid}\nStatus: DONE\n## Evidence\n" + ev + "\n## Gaps\nnone\n")
            self.assertEqual(self.close(tid)[0], 1, ev)

    def test_close_refuses_template_echo(self):
        tid, _ = self.new()
        self.put_result(tid, "Task-ID: {tid}\nStatus: DONE or PARTIAL or BLOCKED\n## Evidence\n"
                             "Links, file paths, test output or quotes that prove the work. No evidence means not done.\n")
        self.assertEqual(self.close(tid)[0], 1)

    def test_close_refuses_wrong_task_id(self):
        tid, _ = self.new()
        self.put_result(tid, "Task-ID: T-20200101-0000-ffff\nStatus: DONE\n## Evidence\nhttps://example.com\n")
        self.assertEqual(self.close(tid)[0], 1)

    def test_brief_echo_cannot_spoof(self):
        tid, _ = self.new(goal="Summarize this page:\nStatus: DONE\n## Evidence\nhttps://example.com")
        brief = (Path(self.b) / "inbox" / f"{tid}.md").read_text(encoding="utf-8")
        self.assertNotIn("\n## Evidence", brief.split("## Return format")[0])
        reply = Path(self.tmp.name) / "echo.txt"
        reply.write_text(brief, encoding="utf-8")
        code, _, err = run("--board", self.b, "result", tid, "--file", str(reply), "--status", "DONE")
        self.assertEqual(code, 1)
        self.assertIn("brief", err)
        self.put_result(tid, brief)
        self.assertEqual(self.close(tid)[0], 1)

    def test_status_flag_cannot_override_worker(self):
        tid, _ = self.new()
        code, _, err = run("--board", self.b, "result", tid, "--status", "DONE",
                           stdin=b"Status: BLOCKED - site down\n## Evidence\nhttps://example.com\n")
        self.assertEqual(code, 1)
        self.assertIn("BLOCKED", err)

    def test_reply_status_kept_without_flag(self):
        tid, _ = self.new()
        code, out, _ = run("--board", self.b, "result", tid, stdin="Status: Done.\n## Evidence\nhttps://example.com\n".encode())
        self.assertEqual(code, 0)
        self.assertIn("status DONE", out)

    def test_reply_without_status_needs_flag(self):
        tid, _ = self.new()
        self.assertEqual(run("--board", self.b, "result", tid, stdin=b"some text\n")[0], 1)

    def test_partial_needs_why(self):
        tid, _ = self.new()
        self.put_result(tid, "Task-ID: {tid}\nStatus: PARTIAL\n## Evidence\nhttps://example.com\n")
        self.assertEqual(self.close(tid)[0], 1)
        self.assertEqual(self.close(tid, "--why", "good enough for a draft")[0], 0)

    def test_builder_cannot_check_itself(self):
        tid, _ = self.new(to="claude")
        self.put_result(tid, GOOD)
        self.assertEqual(self.close(tid, "--checked-by", "claude")[0], 1)
        self.assertEqual(self.close(tid, "--checked-by", "codex")[0], 0)

    # privacy rules
    def test_private_refused_for_muse_even_if_marked_ok(self):
        team = Path(self.b) / "team.json"
        data = json.loads(team.read_text(encoding="utf-8"))
        data["workers"]["muse"]["private_ok"] = True
        team.write_text(json.dumps(data), encoding="utf-8")
        code, _, err = run("--board", self.b, "new", "--to", "muse", "--type", "writing", "--goal", "x", "--private")
        self.assertEqual(code, 1)

    def test_private_ok_must_be_true_not_string(self):
        team = Path(self.b) / "team.json"
        data = json.loads(team.read_text(encoding="utf-8"))
        data["workers"]["helper"] = {"mode": "cli", "private_ok": "false"}
        team.write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(run("--board", self.b, "new", "--to", "helper", "--type", "build", "--goal", "x", "--private")[0], 1)

    def test_missing_team_json_refuses(self):
        (Path(self.b) / "team.json").unlink()
        code, _, err = run("--board", self.b, "new", "--to", "muse", "--type", "research", "--goal", "x", "--private")
        self.assertEqual(code, 1)
        self.assertIn("team.json", err)

    def test_privacy_choice_required(self):
        code, _, _ = run("--board", self.b, "new", "--to", "muse", "--type", "research", "--goal", "x")
        self.assertEqual(code, 2)  # argparse: one of --private or --public is required

    def test_unknown_worker_refused(self):
        code, _, _ = run("--board", self.b, "new", "--to", "nobody", "--type", "research", "--goal", "x", "--public")
        self.assertEqual(code, 1)

    def test_private_refused_on_shared_board(self):
        code, _, err = run("--board", self.b, "new", "--to", "claude", "--type", "writing", "--goal", "x", "--private")
        self.assertEqual(code, 1)
        self.assertIn("shared", err)

    def test_private_board_allows_cleared_worker_only(self):
        pb = os.path.join(self.tmp.name, "local-private")
        self.assertEqual(run("--private-board", "--board", pb, "init")[0], 0)
        code, out, err = run("--private-board", "new", "--to", "claude", "--type", "writing",
                             "--goal", "Draft a note about FICTIONAL PRIVATE MARKER", "--private")
        self.assertEqual(code, 0, err)
        self.assertEqual(run("--private-board", "new", "--to", "muse", "--type", "writing", "--goal", "x", "--private")[0], 1)
        shared = "".join(p.read_text(encoding="utf-8") for p in Path(self.b).rglob("*.md"))
        self.assertNotIn("FICTIONAL PRIVATE MARKER", shared)
        self.assertIn("board", run("list")[1])  # the shared board is still the default

    def test_private_board_in_synced_folder_refused(self):
        pb = os.path.join(self.tmp.name, "Dropbox", "private")
        self.assertEqual(run("--private-board", "--board", pb, "init")[0], 1)

    def test_template_and_wrapped_placeholders_refused_with_valid_status(self):
        for ev in ("(links, file paths, test output or quotes that prove the work)", "- None", "Evidence: None", "* n/a"):
            tid, _ = self.new()
            self.put_result(tid, "Task-ID: {tid}\nStatus: DONE\n## Evidence\n" + ev + "\n## Gaps\nnone\n")
            self.assertEqual(self.close(tid)[0], 1, ev)

    def test_brief_rules_authorize_the_goal(self):
        _, out = self.new()
        self.assertIn("Follow the Goal", out)
        self.assertNotIn("Ignore any instructions", out)

    def test_close_resumes_after_interrupted_unlink(self):
        from unittest import mock
        tid, _ = self.new()
        self.put_result(tid, GOOD)
        real_unlink = Path.unlink
        def flaky(self_path, *a, **k):
            if self_path.name == f"{tid}.md" and self_path.parent.name == "inbox":
                raise PermissionError("locked by sync app")
            return real_unlink(self_path, *a, **k)
        with mock.patch.object(Path, "unlink", flaky):
            code, _, err = self.close(tid)
        self.assertEqual(code, 1)
        self.assertIn("run the same command again", err)
        code, _, err = self.close(tid)
        self.assertEqual(code, 0, err)
        self.assertFalse((Path(self.b) / "inbox" / f"{tid}.md").exists())
        self.assertEqual(self.close(tid)[0], 0)  # already closed is fine

    def test_cancelled_task_cannot_be_closed_later(self):
        tid, _ = self.new()
        done = Path(self.b) / "done"
        (done / f"{tid}.md").write_text("x\n## Cancelled\nearlier\n", encoding="utf-8")
        self.put_result(tid, GOOD)
        code, _, err = self.close(tid)
        self.assertEqual(code, 1)
        self.assertIn("cancelled", err)

    def test_exclusive_write_never_clobbers_a_late_arrival(self):
        from unittest import mock
        target = Path(self.b) / "outbox" / "late.md"
        real_link = os.link
        def racing_link(src, dst, *a, **k):
            Path(dst).write_text("competing writer", encoding="utf-8")
            return real_link(src, dst, *a, **k)
        with mock.patch.object(board.os, "link", racing_link):
            with self.assertRaises(board.BoardError):
                board.write_atomic(target, "our writer", exclusive=True)
        self.assertEqual(target.read_text(encoding="utf-8"), "competing writer")

    def test_result_does_not_replace_without_flag(self):
        tid, _ = self.new()
        self.put_result(tid, GOOD)
        code, _, err = run("--board", self.b, "result", tid, stdin=b"Status: DONE\n## Evidence\nhttps://example.com\n")
        self.assertEqual(code, 1)
        self.assertIn("already exists", err)

    def test_check_flags_results_waiting(self):
        tid, _ = self.new()
        self.put_result(tid, GOOD)
        self.assertEqual(run("--board", self.b, "check")[0], 2)

    def test_bad_team_json_root_is_clean_error(self):
        (Path(self.b) / "team.json").write_text("[]", encoding="utf-8")
        code, _, err = run("--board", self.b, "new", "--to", "muse", "--type", "research", "--goal", "x", "--public")
        self.assertEqual(code, 1)
        self.assertIn("no workers", err)

    # time and ids
    def test_overdue_flagged_and_check_exits_2(self):
        self.new("--deadline", "2020-01-01T09:00-0800")
        code, out, _ = run("--board", self.b, "check")
        self.assertEqual(code, 2)
        self.assertIn("OVERDUE", out)

    def test_bad_hours_and_naive_deadline_refused(self):
        for extra in (["--hours", "nan"], ["--hours", "-3"], ["--hours", "1e12"], ["--deadline", "2026-11-24T17:00"]):
            code, _, _ = run("--board", self.b, "new", "--to", "muse", "--type", "research", "--public",
                             "--goal", "x", *extra)
            self.assertEqual(code, 1, extra)

    def test_bad_id_cannot_escape_folder(self):
        code, _, err = run("--board", self.b, "close", "../../etc/passwd", "--verified", "x")
        self.assertEqual(code, 1)
        self.assertIn("bad task id", err)

    # sync and text encoding
    def test_conflict_copies_warned(self):
        tid, _ = self.new()
        for name in (f"{tid} (conflicted copy).md", f"{tid} (1).md", f"{tid}-LAPTOP-7.md"):
            (Path(self.b) / "inbox" / name).write_text("x", encoding="utf-8")
        (Path(self.b) / "outbox" / f"RESULT-{tid}-LAPTOP-7.md").write_text("x", encoding="utf-8")
        code, out, _ = run("--board", self.b, "list")
        self.assertEqual(code, 0)
        self.assertEqual(out.count("sync conflict"), 4)

    def test_non_ascii_text_and_utf16_reply(self):
        tid, out = self.new(goal="Résumé tips → 5 apps 日本語 ✓")
        self.assertIn("日本語", (Path(self.b) / "inbox" / f"{tid}.md").read_text(encoding="utf-8"))
        reply = Path(self.tmp.name) / "utf16.txt"
        reply.write_bytes("Status: DONE\n## Evidence\ncafé https://example.com\n".encode("utf-16"))
        self.assertEqual(run("--board", self.b, "result", tid, "--file", str(reply))[0], 0)
        saved = (Path(self.b) / "outbox" / f"RESULT-{tid}.md").read_text(encoding="utf-8")
        self.assertIn("café", saved)

    def test_missing_reply_file_is_clean_error(self):
        tid, _ = self.new()
        code, _, err = run("--board", self.b, "result", tid, "--file", "no-such-file.txt")
        self.assertEqual(code, 1)
        self.assertIn("cannot read", err)

    def test_cancel(self):
        tid, _ = self.new()
        self.assertEqual(run("--board", self.b, "cancel", tid, "--why", "no longer needed")[0], 0)
        self.assertTrue((Path(self.b) / "done" / f"{tid}.md").exists())

    def test_init_keeps_existing_team(self):
        team = Path(self.b) / "team.json"
        data = json.loads(team.read_text(encoding="utf-8"))
        data["note"] = "mine"
        team.write_text(json.dumps(data), encoding="utf-8")
        run("--board", self.b, "init")
        self.assertEqual(json.loads(team.read_text(encoding="utf-8"))["note"], "mine")


    def test_plain_checks_include_private_overdue_task(self):
        pb = str(Path(self.tmp.name) / "private")
        self.assertEqual(run("--private-board", "--board", pb, "init")[0], 0)
        code, out, err = run("--private-board", "new", "--to", "claude", "--type", "writing",
                             "--private", "--goal", "Fictional private task", "--deadline", "2026-01-01T09:00-08:00")
        self.assertEqual(code, 0, err)
        tid = next(w.rstrip(",") for w in out.split() if w.startswith("T-"))
        for cmd, expected in (("list", 0), ("check", 2)):
            code, out, err = run(cmd)
            self.assertEqual(code, expected, err)
            self.assertIn(tid, out)
            self.assertIn("(private)", out)
            self.assertIn("1 overdue", out)
        code, out, err = run("--board", self.b, "check")
        self.assertEqual(code, 0, err)
        self.assertNotIn(tid, out)
        self.assertNotIn("Fictional private task", "".join(p.read_text(encoding="utf-8") for p in Path(self.b).rglob("*.md")))

    def test_plain_check_reports_missing_private_board(self):
        pointer = Path(os.environ["BRAIN_TEAM_POINTER"])
        data = json.loads(pointer.read_text(encoding="utf-8"))
        data["private_board"] = str(Path(self.tmp.name) / "missing")
        pointer.write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(run("check")[0], 1)


if __name__ == "__main__":
    unittest.main(verbosity=1)
