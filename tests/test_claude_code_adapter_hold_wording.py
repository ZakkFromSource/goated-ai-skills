"""Round 7 hold texts in Claude Code's words (R6 and R10).

A script write's holds say that the Edit tool keeps a file's line endings,
so CRLF is no reason to script an edit, and that Git Bash's `sed -i` can
strip CR; the core says nothing of either, since it names no harness. A
commit held for its change read says to make that read in an earlier
message, since one sent in the commit's own message cannot count. Each test
drives the hook entry point (see `claude_code_adapter_support.py`).
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from claude_code_adapter_support import ROUTER, Session, reason
from goated_core import actions, wording

LINE_ENDINGS = ("The Edit tool keeps a file's line endings, so CRLF is no reason to use a "
                "script, and \"sed -i\" in Git Bash can strip CR from a file.")
SCRIPT_WRITE = "python -c \"open('src/app.py', 'w').write('x = 1')\""
SHELL_WRITE = ("cat > src/export.py <<'EOF'\n"
               + "".join(f"total_{n} = {n}\n" for n in range(6)) + "EOF")
EARLIER_MESSAGE = ("Make that read in an earlier message than the commit, since a read sent "
                   "in the commit's own message cannot count for it.")


class HoldWordingTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self._sessions = 0

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def routed(self) -> Session:
        self._sessions += 1
        folder = self.root / f"s{self._sessions}"
        folder.mkdir()
        s = Session(folder, session_id=f"session-{self._sessions}")
        s.prompt("Do the task.")
        s.load(ROUTER)
        s.say("goated-route: direct")
        return s


class LineEndingTests(HoldWordingTestCase):
    def test_the_scripted_edit_hold_says_the_edit_tool_keeps_line_endings(self) -> None:
        held = reason(self.routed().call("Bash", {"command": SCRIPT_WRITE}))
        self.assertIn("goated-hold: scripted-edit", held)
        self.assertIn(LINE_ENDINGS, held)

    def test_a_design_hold_on_a_shell_write_says_it_too(self) -> None:
        held = reason(self.routed().call("Bash", {"command": SHELL_WRITE}))
        self.assertIn("goated-hold: design |", held)
        self.assertIn(LINE_ENDINGS, held)

    def test_a_design_hold_on_an_edit_tool_write_does_not(self) -> None:
        write = {"file_path": "src/export.py",
                 "content": "".join(f"total_{n} = {n}\n" for n in range(30))}
        held = reason(self.routed().call("Write", write))
        self.assertIn("goated-hold: design |", held)
        self.assertNotIn("CRLF", held)

    def test_the_core_s_neutral_words_say_nothing_of_line_endings(self) -> None:
        # The core names no harness (ADR 0004), so its neutral words leave the slot empty.
        text = wording.neutral(f"writes it. {wording.LINE_ENDINGS}A script suits.")
        self.assertEqual(text, "writes it. A script suits.")


class CommitChangeReadTests(HoldWordingTestCase):
    def test_the_commit_hold_asks_for_the_read_in_an_earlier_message(self) -> None:
        s = self.routed()
        s.load("commit-message")
        held = reason(s.call("Bash", {"command": 'git commit -m "Add CSV export"'}))
        self.assertIn("goated-hold: commit | strict", held)
        self.assertIn(EARLIER_MESSAGE, held)

    def test_the_pull_request_hold_keeps_its_wording(self) -> None:
        s = self.routed()
        s.load("pr-description")
        held = reason(s.call("Bash", {"command": 'gh pr create --title "Add export" --body x'}))
        self.assertIn("goated-hold: pull-request | strict", held)
        self.assertNotIn("earlier message", held)
        self.assertIn(actions.UNFINISHED_READ, held)


if __name__ == "__main__":
    unittest.main()
