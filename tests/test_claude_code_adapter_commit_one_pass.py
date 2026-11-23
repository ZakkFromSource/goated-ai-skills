"""Ticket 120: commit-time holds in one pass, and asks that fire where they can find something.

Each test drives the hook entry point with a transcript in Claude Code's
recorded shape (see `claude_code_adapter_support.py`).
"""

from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

from claude_code_adapter_support import (
    ROUTER,
    Session,
    decision,
    git_branch_with_change,
    reason,
)

HOLD_LINE = re.compile(r"^goated-hold: ([a-z-]+) \| ([a-z-]+)$", re.MULTILINE)
COMMIT = {"command": 'git commit -am "Raise the export limit"'}
DIFF = "git diff"
PROOF_SKIP = "goated-skip: verification-before-completion: no test suite covers this file"
DOC_SKIP = "goated-skip: doc-sync: internal constant with no documented behavior"
RED_FLAGS = "/opt/goated/skills/software-design-principles/references/red-flags.md"


def gates_of(output: dict) -> list[str]:
    return [gate for gate, _ in HOLD_LINE.findall(reason(output))]


def edit(path: str, new: str, old: str) -> dict:
    return {"file_path": path, "old_string": old, "new_string": new}


class SessionCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self._count = 0

    def session(self, prompt: str = "Raise the export limit and commit it.") -> Session:
        self._count += 1
        folder = self.root / f"s{self._count}"
        folder.mkdir()
        s = Session(folder, session_id=f"session-{self._count}")
        s.prompt(prompt)
        s.load(ROUTER)
        s.say("goated-route: direct")
        return s

    def code_change(self, s: Session) -> None:
        s.call("Edit", edit("src/export.py", "LIMIT = 20", "LIMIT = 10"))


class OneMessageTests(SessionCase):
    """R4: a held commit names every unmet ask at once."""

    def test_a_commit_missing_its_load_read_and_proof_names_all_three_at_once(self) -> None:
        s = self.session()
        self.code_change(s)

        held = s.call("Bash", COMMIT)
        self.assertEqual(decision(held), "deny")
        self.assertEqual(gates_of(held), ["commit", "closeout"])
        text = reason(held)
        self.assertIn("`commit-message`", text)
        self.assertIn("Read the change", text)
        self.assertIn("- Proof:", text)

    def test_a_bad_message_and_a_missing_load_and_read_come_together(self) -> None:
        s = self.session()
        self.code_change(s)

        long_subject = "Raise the export limit " + "and more " * 10
        text = reason(s.call("Bash", {"command": f'git commit -am "{long_subject}"'}))
        self.assertIn("`commit-message`", text)
        self.assertIn("breaks the commit-message contract", text)
        self.assertIn("Read the change", text)

    def test_meeting_everything_in_one_go_lets_the_retry_pass(self) -> None:
        s = self.session()
        self.code_change(s)
        s.call("Bash", COMMIT)
        s.load("commit-message")
        s.run(DIFF)
        s.say(PROOF_SKIP)
        s.say(DOC_SKIP)
        self.assertEqual(decision(s.call("Bash", COMMIT)), "pass")


class ChangeReadKeptTests(SessionCase):
    """R5: a doc or comment-only change after a change read keeps it."""

    def read_and_met(self) -> Session:
        s = self.session()
        self.code_change(s)
        s.load("commit-message")
        s.say(PROOF_SKIP)
        s.say(DOC_SKIP)
        s.run(DIFF)
        return s

    def test_a_markdown_edit_after_the_read_keeps_it(self) -> None:
        s = self.read_and_met()
        s.call("Edit", edit("NOTES.md", "Limit is 20.", "Limit is 10."))
        self.assertEqual(decision(s.call("Bash", COMMIT)), "pass")

    def test_a_comment_only_edit_after_the_read_keeps_it(self) -> None:
        s = self.read_and_met()
        s.call("Edit", edit("src/export.py", "LIMIT = 20  # rows per page", "LIMIT = 20"))
        self.assertEqual(decision(s.call("Bash", COMMIT)), "pass")

    def test_a_one_line_code_edit_after_the_read_resets_it(self) -> None:
        s = self.read_and_met()
        s.call("Edit", edit("src/export.py", "LIMIT = 30", "LIMIT = 20"))
        held = s.call("Bash", COMMIT)
        self.assertEqual(decision(held), "deny")
        self.assertIn("commit", gates_of(held))

    def test_a_diff_chained_before_the_commit_is_not_the_read(self) -> None:
        s = self.session()
        self.code_change(s)
        s.load("commit-message")
        s.say(PROOF_SKIP)
        s.say(DOC_SKIP)
        held = s.call("Bash", {"command": 'git diff && git commit -am "Raise the export limit"'})
        self.assertEqual(gates_of(held), ["commit"])


REFERENCES = "/opt/goated/skills/software-design-principles/references/"
PLAIN = "\n".join(f"total_{n} = {n}" for n in range(6))
CONTEXT = "total_0 = 0\ntotal_1 = 1\ntotal_2 = 2\n"


def stop(s: Session) -> str:
    """The Stop hook's raw output: "" when the turn may end."""

    return s.hook("Stop", stop_hook_active=False, last_assistant_message="")


class DesignFollowUpTests(SessionCase):
    """R6: after a red-flags read, a small follow-up is counted by the lines it adds."""

    def scanned(self) -> Session:
        s = self.session("Add the export totals.")
        s.load("software-design-principles")
        s.read(REFERENCES + "errors.md")
        s.call("Edit", edit("src/export.py", PLAIN, "pass"))
        s.run("pytest -q")
        s.say(DOC_SKIP)
        s.read(RED_FLAGS)
        s.run(DIFF)
        self.assertEqual(stop(s), "")
        return s

    def test_a_two_line_fix_sent_with_three_context_lines_needs_only_a_change_read(self) -> None:
        s = self.scanned()
        s.call("Edit", edit("src/export.py", CONTEXT + "total_3 = 30\ntotal_4 = 40",
                            CONTEXT + "total_3 = 3\ntotal_4 = 4"))
        s.run("pytest -q")
        held = stop(s)
        self.assertIn("- Design: read the change itself after reading the red flags", held)
        self.assertNotIn("red-flags.md", held)
        s.run(DIFF)
        self.assertEqual(stop(s), "")

    def test_a_scanned_edit_is_measured_with_its_context_lines(self) -> None:
        # Probe K10: the change the red flags scanned is counted as before, context
        # included, so a 1-line fix after it needs only a change read.
        s = self.session("Add the export totals.")
        s.load("software-design-principles")
        s.read(REFERENCES + "errors.md")
        context = "\n".join(f"{name} = 0" for name in "abcdef")
        s.call("Edit", edit("src/export.py",
                            context + "\n" + "\n".join(f"t{n} = {n}" for n in range(1, 5)),
                            context))
        s.run("pytest -q")
        s.say(DOC_SKIP)
        s.read(RED_FLAGS)
        s.call("Edit", edit("src/export.py", "t4 = 40", "t4 = 4"))
        s.run("pytest -q")
        s.run(DIFF)
        self.assertEqual(stop(s), "")

    def test_a_five_line_addition_needs_the_red_flags_read_again(self) -> None:
        s = self.scanned()
        s.call("Edit", edit("src/export.py",
                            "total_5 = 5\n" + "\n".join(f"extra_{n} = {n}" for n in range(5)),
                            "total_5 = 5"))
        s.run("pytest -q")
        s.run(DIFF)
        self.assertIn("red-flags.md", stop(s))


class DocsByDocChangeTests(SessionCase):
    """R7: a doc changed after the last code change, then read, meets Docs."""

    def test_code_then_a_doc_then_a_read_meets_docs_with_no_load(self) -> None:
        s = self.session()
        self.code_change(s)
        s.run("pytest -q")
        s.call("Edit", edit("docs/export.md", "The limit is 20.", "The limit is 10."))
        self.assertIn("- Docs:", stop(s))
        s.read("docs/export.md")
        self.assertEqual(stop(s), "")

    def test_a_doc_changed_before_the_code_does_not_meet_docs(self) -> None:
        s = self.session()
        s.call("Edit", edit("docs/export.md", "The limit is 20.", "The limit is 10."))
        self.code_change(s)
        s.run("pytest -q")
        s.run(DIFF)
        self.assertIn("- Docs:", stop(s))


MERGE_FAILED = ("CONFLICT (content): Merge conflict in src/export.py\n"
                "Automatic merge failed; fix conflicts and then commit the result.")
MARKED = "<<<<<<< HEAD\nLIMIT = 10\n=======\nLIMIT = 20\n>>>>>>> feature"
MERGE_COMMIT = {"command": 'git commit -am "Merge the feature branch"'}


class ConflictCommitTests(SessionCase):
    """R8: with the conflict skill loaded, a conflict's commit asks for the change read and Proof."""

    def resolved(self, loaded: bool, large_full: bool = False) -> Session:
        """A turn that resolved a merge conflict and read the change, the
        conflict skill `loaded` or skipped. `large_full`: on a full route,
        in a checkout whose branch is large, so Review and Verification apply."""

        if large_full:
            self._count += 1
            folder = self.root / f"s{self._count}"
            folder.mkdir()
            s = Session(folder, session_id=f"session-{self._count}")
            git_branch_with_change(s.project, 450)
            s.prompt("Merge the feature branch.")
            s.load(ROUTER)
            s.say("goated-route: full | requires: tdd")
            s.load("tdd")
        else:
            s = self.session("Merge the feature branch.")
        s.call("Bash", {"command": "git merge feature"}, result=MERGE_FAILED, failed=True)
        if loaded:
            s.load("resolving-merge-conflicts")
        else:
            s.say("goated-skip: resolving-merge-conflicts: one constant, the feature side wins")
        s.load("software-design-principles")
        s.call("Edit", edit("src/export.py", "LIMIT = 20", MARKED))
        s.load("commit-message")
        s.run(DIFF)
        return s

    def closeout_items(self, output: dict) -> list[str]:
        text = reason(output).split("goated-hold: closeout", 1)
        return re.findall(r"^- ([A-Za-z]+):", text[1], re.MULTILINE) if len(text) > 1 else []

    def test_with_the_skill_loaded_the_commit_asks_for_proof_alone(self) -> None:
        s = self.resolved(loaded=True)
        held = s.call("Bash", MERGE_COMMIT)
        self.assertEqual(gates_of(held), ["closeout"])
        self.assertEqual(self.closeout_items(held), ["Proof"])
        s.run("pytest -q")
        self.assertEqual(decision(s.call("Bash", MERGE_COMMIT, result="[main 1a2b3c4] Merge")),
                         "pass")
        # The next ordinary commit gets the full closeout again.
        s.call("Edit", edit("src/export.py", "LIMIT = 30", "LIMIT = 20"))
        s.run("pytest -q")
        s.run(DIFF)
        self.assertIn("Docs", self.closeout_items(s.call("Bash", COMMIT)))

    def test_with_the_skill_loaded_review_and_verification_are_not_asked(self) -> None:
        s = self.resolved(loaded=True, large_full=True)
        s.run("pytest -q")
        self.assertEqual(decision(s.call("Bash", MERGE_COMMIT, result="[feature 1a2b3c4] Merge")),
                         "pass")

    def test_without_the_load_a_large_full_route_commit_asks_for_review_and_verification(
            self) -> None:
        s = self.resolved(loaded=False, large_full=True)
        s.run("pytest -q")
        items = self.closeout_items(s.call("Bash", MERGE_COMMIT))
        self.assertIn("Review", items)
        self.assertIn("Verification", items)

    def test_a_doc_showing_marker_lines_is_no_conflict_to_end(self) -> None:
        # Probe K8: markers shown in a doc open no git conflict, so the commit is ordinary.
        s = self.session("Change and commit.")
        s.load("resolving-merge-conflicts")
        s.load("commit-message")
        s.load("software-design-principles")
        s.read("docs/conflicts.md", content="Example:\n" + MARKED + "\n")
        self.code_change(s)
        s.run("pytest -q")
        s.run(DIFF)
        items = self.closeout_items(s.call("Bash", COMMIT))
        self.assertIn("Docs", items)
        self.assertIn("Design", items)

    def test_a_conflict_from_an_earlier_turn_resolved_by_an_edit_now_asks_for_less(self) -> None:
        # Probe K9: the markers the edit removes show the conflict this turn ends.
        s = self.session("Merge the feature branch.")
        s.call("Bash", {"command": "git merge feature"}, result=MERGE_FAILED, failed=True)
        s.prompt("Resolve and commit.")
        s.say("goated-route: continue")
        s.load("resolving-merge-conflicts")
        s.load("commit-message")
        s.load("software-design-principles")
        s.call("Edit", edit("src/export.py", "LIMIT = 20", MARKED))
        s.run("pytest -q")
        s.run(DIFF)
        self.assertEqual(decision(s.call("Bash", MERGE_COMMIT)), "pass")

    def edited_markers(self, path: str, removed: str, added: str, loaded: bool = True) -> list[str]:
        """The closeout items of a commit after an edit of `path` removing
        `removed`, then a code change, a check and a diff; the conflict skill
        `loaded`, or skipped."""

        s = self.session("Tidy and commit.")
        if loaded:
            s.load("resolving-merge-conflicts")
        else:
            s.say("goated-skip: resolving-merge-conflicts: one constant, the feature side wins")
        s.load("commit-message")
        s.load("software-design-principles")
        s.call("Edit", edit(path, added, removed))
        if path != "src/export.py":
            self.code_change(s)
        s.run("pytest -q")
        s.run(DIFF)
        return self.closeout_items(s.call("Bash", COMMIT))

    def test_removing_a_marker_example_from_a_doc_resolves_no_conflict(self) -> None:
        items = self.edited_markers("docs/conflicts.md", "Example:\n" + MARKED + "\n",
                                    "See git's manual.\n")
        self.assertIn("Docs", items)
        self.assertIn("Design", items)

    def test_removing_one_marker_line_from_code_resolves_no_conflict(self) -> None:
        items = self.edited_markers("src/export.py", "<<<<<<< HEAD\nLIMIT = 10", "LIMIT = 10")
        self.assertIn("Docs", items)

    def test_removing_a_full_block_from_code_resolves_a_conflict_with_the_skill(self) -> None:
        self.assertEqual(self.edited_markers("src/export.py", MARKED, "LIMIT = 20"), [])
        # Near miss: the same edit without the skill gets the full closeout.
        self.assertIn("Docs", self.edited_markers("src/export.py", MARKED, "LIMIT = 20",
                                                  loaded=False))

    def test_an_edit_that_keeps_a_marker_resolves_no_conflict(self) -> None:
        items = self.edited_markers("src/export.py", MARKED, "<<<<<<< HEAD\nLIMIT = 20")
        self.assertIn("Docs", items)

    def test_without_the_load_the_commit_gets_the_full_closeout(self) -> None:
        s = self.resolved(loaded=False)
        s.run("pytest -q")
        items = self.closeout_items(s.call("Bash", MERGE_COMMIT))
        self.assertIn("Docs", items)
        self.assertIn("Design", items)


class TestPathSecurityTests(SessionCase):
    """R9: a test path is not security-sensitive."""

    def test_a_test_file_named_for_login_sessions_meets_no_security_hold(self) -> None:
        s = self.session("Add a session test.")
        held = s.call("Edit", edit("tests/test_login_session.py", "assert ok", "pass"))
        self.assertNotIn("security", gates_of(held))
        self.assertEqual(decision(held), "pass")

    def test_login_session_code_still_meets_the_security_hold(self) -> None:
        s = self.session("Fix the session code.")
        held = s.call("Edit", edit("src/login_session.py", "TTL = 20", "TTL = 10"))
        self.assertEqual(gates_of(held), ["security"])

    def test_test_paths_that_are_not_test_code_or_match_by_kind_still_hold(self) -> None:
        # Only test code is spared, and only from what its name's words select.
        for path in ("tests/.env", "tests/requirements.txt", "requirements_test.txt",
                     ".github/workflows/run_test.yml", "docker-compose.test.yml",
                     "test/fixtures/server.key", "tests/secrets.json",
                     "migrations/0001_test.sql", "src/testing/auth.py", "src/contest/auth.py"):
            with self.subTest(path=path):
                s = self.session("Change the file.")
                self.assertIn("security", gates_of(s.call("Edit", edit(path, "a = 2", "a = 1"))))


class SensitiveChangeResetsReadTests(SessionCase):
    """A sensitive change that is not code, after the read, resets the commit's read."""

    def test_a_ci_workflow_change_after_the_read_needs_another(self) -> None:
        s = self.session()
        s.load("commit-message")
        s.load("code-security-review")
        self.code_change(s)
        s.run(DIFF)
        s.say(PROOF_SKIP)
        s.say(DOC_SKIP)
        s.say("goated-skip: code-security-review: a pinned step in our own workflow only")
        s.call("Edit", edit(".github/workflows/ci.yml", "run: b", "run: a"))
        self.assertIn("commit", gates_of(s.call("Bash", COMMIT)))


class TextDocTests(SessionCase):
    """A `.txt` under a test path or a build file is not a doc for Docs."""

    def test_a_golden_output_or_build_file_does_not_meet_docs(self) -> None:
        for path in ("tests/golden/export.txt", "CMakeLists.txt"):
            with self.subTest(path=path):
                s = self.session()
                self.code_change(s)
                s.run("pytest -q")
                s.call("Edit", edit(path, "limit 20", "limit 10"))
                s.read(path)
                self.assertIn("- Docs:", stop(s))

    def test_a_text_doc_still_meets_docs(self) -> None:
        s = self.session()
        self.code_change(s)
        s.run("pytest -q")
        s.call("Edit", edit("docs/limits.txt", "limit 20", "limit 10"))
        s.read("docs/limits.txt")
        self.assertEqual(stop(s), "")


if __name__ == "__main__":
    unittest.main()
