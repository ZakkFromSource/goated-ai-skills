"""Behavior tests for the closeout's Review and Verification items (Ticket 069).

The Review item weighs the branch's work against its base, so its tests run
against a real scratch git repository in the session's project folder: the
files a turn writes are written to disk as well as recorded as tool calls.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from claude_code_adapter_support import (
    BRIEF,
    REPO_ROOT,
    ROUTER,
    Session,
    decision,
    git_branch_with_change,
    parse,
    reason,
)

CLOSEOUT_HOLD = "goated-hold: closeout | justified-skip"
DESIGN_SKIP = "goated-skip: software-design-principles: one mechanical constant change"
DOC_SKIP = "goated-skip: doc-sync: internal constant with no documented behavior"
PROOF_SKIP = "goated-skip: verification-before-completion: no test suite covers this file"
REVIEW = "standards-and-spec-review"
REVIEW_SKIP = f"goated-skip: {REVIEW}: the added lines are generated fixtures"
VERIFY = "verification-before-completion"
REVIEWER_PROMPT = "D:\\goated\\skills\\subagent-driven-development\\references\\reviewer-prompt.md"
REVIEWER_BRIEF = (
    "## Review Mode\n\nSpec and standards review of the export branch.\n\n"
    "## Review Inputs\n\n- The diff against main.\n\n"
    "## Required Report Format\n\n- Findings with file paths.\n\n"
    "goated-skills: standards-and-spec-review\n"
)
OPEN_PR = {"command": "gh pr create --base main --title 'Add export' --body-file body.md"}


def git(project: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
         "-c", "commit.gpgsign=false", "-c", "core.autocrlf=false", *args],
        cwd=project, check=True, capture_output=True,
    )


def lines(count: int, word: str = "line") -> str:
    return "".join(f"{word} {n}\n" for n in range(count))


def stop(s: Session) -> dict:
    return parse(s.hook("Stop", stop_hook_active=False, last_assistant_message=""))


def commit_call(s: Session) -> dict:
    return s.call("Bash", {"command": 'git commit -m "Add export"'})


class ReviewTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self._sessions = 0

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def session(self, route: str = "goated-route: direct") -> Session:
        self._sessions += 1
        folder = self.root / f"s{self._sessions}"
        folder.mkdir()
        s = Session(folder, session_id=f"session-{self._sessions}")
        self.turn(s, route)
        return s

    @staticmethod
    def turn(s: Session, route: str = "goated-route: direct") -> None:
        s.prompt("Add CSV export.")
        s.load(ROUTER)
        s.say(route)
        if "requires:" in route:
            for skill in route.split("requires:", 1)[1].split(","):
                s.load(skill.strip())

    @staticmethod
    def branch(s: Session, committed: int, *, ignore: str | None = None) -> None:
        """Make the project a checkout on branch `feature`, off `main`, with
        `committed` lines committed on the branch; `ignore`: a .gitignore
        pattern committed on main and merged into the branch."""

        git_branch_with_change(s.project, committed)
        if ignore:
            git(s.project, "checkout", "-q", "main")
            (s.project / ".gitignore").write_text(ignore + "\n", encoding="utf-8")
            git(s.project, "add", ".gitignore")
            git(s.project, "commit", "-q", "-m", "Ignore")
            git(s.project, "checkout", "-q", "feature")
            git(s.project, "merge", "-q", "--no-edit", "main")

    @staticmethod
    def write(s: Session, path: str, count: int, word: str = "line") -> dict:
        """Write a `count`-line file to disk and record the Write call for it."""

        s.say(DESIGN_SKIP)
        target = s.project / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(lines(count, word), encoding="utf-8")
        return s.call("Write", {"file_path": path, "content": lines(count, word)})

    @staticmethod
    def meet_the_rest(s: Session) -> None:
        """Prove the change and pass doc-sync and the commit gate."""

        s.run("pytest -q")
        s.say(DOC_SKIP)
        s.load("commit-message")
        s.run("git diff")


class ReviewItemSizeTests(ReviewTestCase):
    def test_a_large_branch_is_held_at_commit_with_review_and_399_lines_is_not(self) -> None:
        for committed, large in ((380, True), (379, False)):
            with self.subTest(lines=committed + 20):
                s = self.session()
                self.branch(s, committed)
                self.write(s, "src/export.py", 20)
                self.meet_the_rest(s)

                held = commit_call(s)
                if large:
                    self.assertEqual(reason(held).split("\n", 1)[0], CLOSEOUT_HOLD)
                    self.assertIn("- Review:", reason(held))
                    self.assertIn("400 changed lines of non-test code", reason(held))
                    self.assertIn("- Review:", stop(s)["reason"])
                else:
                    self.assertEqual(decision(held), "pass")
                    self.assertEqual(stop(s), {})

    def test_staged_unstaged_and_untracked_changes_count(self) -> None:
        for appended, large in ((5, True), (4, False)):
            with self.subTest(appended=appended):
                s = self.session()
                self.branch(s, 390)
                self.write(s, "src/export.py", 5)
                git(s.project, "add", "src/export.py")  # Staged.
                with (s.project / "src" / "change.py").open("a", encoding="utf-8") as handle:
                    handle.write(lines(appended, "more"))  # Unstaged.
                self.meet_the_rest(s)

                self.assertEqual("- Review:" in reason(commit_call(s)), large)

    def test_an_ignored_file_does_not_count_and_an_untracked_one_does(self) -> None:
        text = lines(50).encode()
        for folder, content, large in (("build", text, False), ("out", text, True),
                                       ("out", text.replace(b"\n", b"\0\n"), False),  # Binary.
                                       # Five lines, the last with no newline: 400 in all.
                                       ("out", lines(5).encode().rstrip(b"\n"), True)):
            with self.subTest(folder=folder, binary=b"\0" in content):
                s = self.session()
                self.branch(s, 390, ignore="build/")
                self.write(s, "src/export.py", 5)
                (s.project / folder).mkdir()
                (s.project / folder / "bundle.js").write_bytes(content)
                self.meet_the_rest(s)

                self.assertEqual("- Review:" in reason(commit_call(s)), large)

    def test_two_300_line_commits_raise_the_item_at_the_second(self) -> None:
        s = self.session()
        self.branch(s, 0)
        self.write(s, "src/first.py", 300)
        self.meet_the_rest(s)
        self.assertEqual(decision(commit_call(s)), "pass")
        git(s.project, "add", "-A")
        git(s.project, "commit", "-q", "-m", "First half")

        self.turn(s)
        self.write(s, "src/second.py", 300)
        self.meet_the_rest(s)
        held = commit_call(s)
        self.assertIn("- Review:", reason(held))
        self.assertIn("600 changed lines of non-test code", reason(held))

    def test_on_the_base_branch_or_unmeasurable_no_review_and_the_rest_unchanged(self) -> None:
        def items(s: Session) -> str:
            self.write(s, "src/export.py", 500)
            s.run("pytest -q")
            return stop(s)["reason"]

        unmeasured = items(self.session())  # No git checkout at all.
        self.assertNotIn("- Review:", unmeasured)

        on_base = self.session()
        git_branch_with_change(on_base.project, 10, stay_on_base=True)
        self.assertEqual(items(on_base), unmeasured)

        no_base = self.session()
        git_branch_with_change(no_base.project, 10, base="trunk")
        self.assertEqual(items(no_base), unmeasured)

        feature = self.session()  # The near miss: the same work on a branch off main.
        git_branch_with_change(feature.project, 10)
        self.assertIn("- Review:", items(feature))

    def test_a_stale_remote_base_measures_from_the_local_base_fork_point(self) -> None:
        # Lead review M1: local main is 500 lines ahead of origin/main, merged locally.
        for ticket_lines, large in ((10, False), (400, True)):
            with self.subTest(ticket_lines=ticket_lines):
                s = self.session()
                git_branch_with_change(s.project, 0, remote_head=True, stay_on_base=True)
                (s.project / "merged.txt").write_text(lines(500), encoding="utf-8")
                git(s.project, "add", "merged.txt")
                git(s.project, "commit", "-q", "-m", "Earlier ticket, merged locally")
                git(s.project, "checkout", "-q", "-b", "ticket")
                self.write(s, "src/export.py", ticket_lines)
                self.meet_the_rest(s)

                self.assertEqual("- Review:" in reason(commit_call(s)), large)

    def test_a_detached_head_is_not_measured(self) -> None:
        for detached in (True, False):
            with self.subTest(detached=detached):
                s = self.session()
                git_branch_with_change(s.project, 450)
                if detached:
                    git(s.project, "checkout", "-q", "--detach")
                self.write(s, "src/export.py", 6)
                s.run("pytest -q")
                self.assertEqual("- Review:" in stop(s)["reason"], not detached)

    def test_an_untracked_symlink_counts_one_line_not_its_target(self) -> None:
        outside = self.root / "outside.txt"
        outside.write_text(lines(500), encoding="utf-8")
        for linked, large in ((True, False), (False, True)):
            with self.subTest(linked=linked):
                s = self.session()
                self.branch(s, 390)
                self.write(s, "src/export.py", 5)
                if linked:
                    try:
                        os.symlink(outside, s.project / "data.py")
                    except (OSError, NotImplementedError):
                        self.skipTest("this system cannot create symbolic links")
                else:
                    (s.project / "data.py").write_text(lines(500), encoding="utf-8")
                self.meet_the_rest(s)
                held = reason(commit_call(s))
                # Python 3.11's rmtree on Windows cannot clear a folder holding a file link.
                (s.project / "data.py").unlink()
                self.assertEqual("- Review:" in held, large)

    def test_the_pr_review_gate_measures_only_committed_work_as_before(self) -> None:
        for committed, held in ((399, False), (400, True)):
            with self.subTest(committed=committed):
                s = self.session()
                git_branch_with_change(s.project, committed)
                (s.project / "scratch.txt").write_text(lines(50), encoding="utf-8")
                s.load("pr-description")
                s.run("git diff main...HEAD")

                output = s.call("Bash", OPEN_PR)
                self.assertEqual(reason(output).startswith("goated-hold: pr-review"), held)


class CodeOnlySizeTests(ReviewTestCase):
    """"Large" counts changed lines in code files outside test paths only (spec R11)."""

    def commit_on_branch(self, s: Session, files: dict[str, int]) -> None:
        """Commit `files` (path: line count) on branch `feature`, off `main`."""

        git_branch_with_change(s.project, 0)
        for path, count in files.items():
            target = s.project / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(lines(count), encoding="utf-8")
        git(s.project, "add", "-A")
        git(s.project, "commit", "-q", "-m", "Work")

    MIXED = {"tests/test_export.py": 200, "src/export_test.go": 100,
             "tests/fixtures/rows.json": 100, "docs/export.md": 100}

    def test_test_fixture_and_doc_lines_do_not_make_a_branch_large(self) -> None:
        for code, large in ((294, False), (394, True)):
            with self.subTest(code=code + 6):
                s = self.session()
                self.commit_on_branch(s, {"src/export.py": code, **self.MIXED})
                self.write(s, "src/more.py", 6)
                s.run("pytest -q")
                s.say(DOC_SKIP)
                held = stop(s).get("reason", "")
                self.assertEqual("- Review:" in held, large)
                self.assertEqual("- Verification:" in held, large)
                if large:
                    self.assertIn("since this branch's work is 400 changed lines of non-test code", held)
                    self.assertIn("claiming it is done, since this branch's work is 400 changed lines of non-test code", held)

    def test_pr_review_counts_only_non_test_code(self) -> None:
        for code, held in ((300, False), (400, True)):
            with self.subTest(code=code):
                s = self.session()
                self.commit_on_branch(s, {"src/export.py": code, **self.MIXED})
                s.load("pr-description")
                s.run("git diff main...HEAD")

                output = s.call("Bash", OPEN_PR)
                self.assertEqual(reason(output).startswith("goated-hold: pr-review"), held)
                if held:
                    self.assertIn("has 400 changed lines of non-test code against its base", reason(output))

    def test_an_untracked_non_code_folder_adds_nothing(self) -> None:
        for name, large in (("notes.md", False), ("gen.py", True)):
            with self.subTest(name=name):
                s = self.session()
                self.commit_on_branch(s, {"src/export.py": 300})
                self.write(s, "src/more.py", 6)
                (s.project / "scratch").mkdir()
                (s.project / "scratch" / name).write_text(lines(200), encoding="utf-8")
                s.run("pytest -q")
                s.say(DOC_SKIP)
                self.assertEqual("- Review:" in stop(s).get("reason", ""), large)


class ReviewItemMetTests(ReviewTestCase):
    def large(self) -> Session:
        """A turn on a 420-line branch with every item but Review met."""

        s = self.session()
        self.branch(s, 400)
        self.write(s, "src/export.py", 20)
        s.load(VERIFY)
        self.meet_the_rest(s)
        return s

    def reviewer(self, s: Session, agent_id: str, brief: str = REVIEWER_BRIEF) -> None:
        agent = s.subagent(agent_id)
        agent.prompt("Review the branch.", hook=False)
        agent.run("git diff main")
        self.assertEqual(decision(s.spawn(agent_id, brief)), "pass")

    def test_a_reviewer_subagent_after_the_last_change_meets_it(self) -> None:
        s = self.large()
        self.assertIn("- Review:", reason(commit_call(s)))
        s.load("subagent-driven-development")
        s.read(REVIEWER_PROMPT)
        self.reviewer(s, "r1")

        self.assertEqual(decision(commit_call(s)), "pass")
        self.assertEqual(stop(s), {})

    def test_a_reviewer_before_a_later_change_does_not(self) -> None:
        s = self.large()
        s.load("subagent-driven-development")
        s.read(REVIEWER_PROMPT)
        self.reviewer(s, "r2")
        s.load("receiving-code-review")  # The review-intake gate holds a fix until it loads.
        self.assertEqual(decision(self.write(s, "src/export.py", 21)), "pass")
        s.run("pytest -q")
        s.run("git diff")

        self.assertIn("- Review:", reason(commit_call(s)))

    def launch_in_background(self, s: Session, agent_id: str) -> str:
        """Start a reviewer in the background: its result says only that it launched."""

        s.load("subagent-driven-development")
        s.read(REVIEWER_PROMPT)
        agent = s.subagent(agent_id)
        agent.prompt("Review the branch.", hook=False)
        tool_use_id, output = s._judge("Agent", {"prompt": REVIEWER_BRIEF, "run_in_background": True})
        self.assertEqual(decision(output), "pass")
        s._tool_result(tool_use_id, "Async agent launched successfully.", extra={
            "toolUseResult": {"isAsync": True, "status": "async_launched", "agentId": agent_id}})
        return tool_use_id

    @staticmethod
    def notification(agent_id: str, tool_use_id: str, status: str = "completed") -> str:
        return (f"<task-notification>\n<task-id>{agent_id}</task-id>\n<tool-use-id>{tool_use_id}"
                f"</tool-use-id>\n<status>{status}</status>\n<summary>Review done.</summary>\n"
                "</task-notification>")

    def test_a_background_reviewer_counts_only_once_its_completion_arrives(self) -> None:
        # Lead review M2: both recorded shapes of the completion, and near misses.
        def as_prompt(s: Session, text: str) -> None:
            s.prompt(text, hook=False, new_prompt_id=False,
                     origin={"kind": "task-notification"}, turnOrigin="task_notification")

        def as_attachment(s: Session, text: str) -> None:
            s._append({"type": "attachment",
                       "attachment": {"type": "queued_command", "prompt": text}})

        for deliver in (as_prompt, as_attachment):
            with self.subTest(deliver=deliver.__name__):
                s = self.large()
                tool_use_id = self.launch_in_background(s, "bg1")
                self.assertIn("- Review:", reason(commit_call(s)))
                deliver(s, self.notification("other9", tool_use_id))
                self.assertIn("- Review:", reason(commit_call(s)))
                deliver(s, self.notification("bg1", tool_use_id, status="failed"))
                self.assertIn("- Review:", reason(commit_call(s)))
                deliver(s, self.notification("bg1", tool_use_id))
                self.assertEqual(decision(commit_call(s)), "pass")

    def test_a_background_reviewers_hand_back_counts_as_its_completion(self) -> None:
        s = self.large()
        self.launch_in_background(s, "bg2")
        s._append({"type": "attachment", "attachment": {
            "type": "queued_command",
            "prompt": '<agent-message from="bg2">\n[Subagent hand-back] The report follows:\n  No findings.'}})
        self.assertEqual(decision(commit_call(s)), "pass")

    def test_a_side_session_started_with_a_reviewer_brief_does_not(self) -> None:
        # Its result arrives at once, but the review has only started (maintainer decision).
        for tool, field in (("mcp__ccd_session__start_session", "prompt"),
                            ("mcp__ccd_session__hand_off_to_session", "remaining_plan")):
            with self.subTest(tool=tool):
                s = self.large()
                s.load("subagent-driven-development")
                s.read(REVIEWER_PROMPT)
                started = s.call(tool, {field: REVIEWER_BRIEF, "title": "Review export"},
                                 result="Session started.")
                self.assertEqual(decision(started), "pass")
                self.assertIn("- Review:", reason(commit_call(s)))

    def test_a_subagent_briefed_from_the_handoff_template_does_not(self) -> None:
        s = self.large()
        s.brief_with_handoff()
        self.reviewer(s, "h1", BRIEF)

        held = commit_call(s)
        self.assertIn("- Review:", reason(held))
        self.assertIn("reviewer-prompt.md", reason(held))

    def test_the_skill_load_and_a_later_change_read_meet_it_and_the_load_alone_does_not(self) -> None:
        # `large` read the diff after the last change and before this load, which counts (Ticket 092).
        s = self.large()
        s.load(REVIEW)
        self.assertEqual(decision(commit_call(s)), "pass")

        # The near miss: the load with no change read after the last change.
        s = self.session()
        self.branch(s, 400)
        self.write(s, "src/export.py", 20)
        s.load(VERIFY)
        s.run("pytest -q")
        s.say(DOC_SKIP)
        s.load(REVIEW)
        held = stop(s)
        self.assertIn("- Review:", held["reason"])
        self.assertIn(f"goated-skip: {REVIEW}: <reason>", held["reason"])
        s.run("git diff main")
        self.assertEqual(stop(s), {})

    def test_a_skip_line_naming_the_review_skill_meets_it(self) -> None:
        s = self.large()
        s.say(REVIEW_SKIP)
        self.assertEqual(decision(commit_call(s)), "pass")


class BriefedSessionReviewTests(ReviewTestCase):
    """A session started from a brief meets no Review item (spec R10): the
    session that started it reviews the work."""

    BRIEF_PROMPT = (
        "<system-reminder>\nLinked sessions now: none.\n</system-reminder>\n"
        "Background (from the session that started this one):\nThe exporter work.\n\n"
        "## Task\n\nAdd CSV export.\n\n{route}\n"
    )

    def briefed(self, route: str = "goated-route: direct") -> Session:
        self._sessions += 1
        folder = self.root / f"s{self._sessions}"
        folder.mkdir()
        s = Session(folder, session_id=f"session-{self._sessions}")
        s.hook("SessionStart", source="startup")
        s.prompt(self.BRIEF_PROMPT.format(route=route), origin=None,
                 turnOrigin="host_synthetic", promptSource="sdk")
        return s

    def large_turn(self, s: Session, path: str = "src/export.py") -> str:
        """Write 600 code lines, meet every item but Review and Verification,
        and return the closeout's items."""

        self.write(s, path, 600)
        s.run("pytest -q")
        s.say(DOC_SKIP)
        held = stop(s)["reason"]
        self.assertIn("done, since this branch's work is", held)  # Measured as large.
        return held

    def test_a_briefed_session_meets_no_review_item_in_any_turn(self) -> None:
        s = self.briefed()
        self.branch(s, 0)
        self.assertNotIn("- Review:", self.large_turn(s))

        self.turn(s)  # A typed prompt ends the brief's route, not the briefing.
        self.assertNotIn("- Review:", self.large_turn(s, "src/second.py"))

        s.compact()
        self.turn(s)
        self.assertNotIn("- Review:", self.large_turn(s, "src/third.py"))

    def test_a_brief_with_no_route_line_still_meets_it(self) -> None:
        # Only a brief the adapter recognizes, by its route line, marks the session.
        s = self.briefed(route="")
        s.load(ROUTER)
        s.say("goated-route: direct")
        self.branch(s, 0)
        self.assertIn("- Review:", self.large_turn(s))

    def test_a_brief_with_a_skills_line_and_no_route_line_meets_none(self) -> None:
        # Round 7, R2: the skills line marks the brief, for the Review item only.
        s = self.briefed(route="goated-skills: tdd")
        held = reason(s.call("Write", {"file_path": "src/early.py", "content": "x = 1\n"}))
        self.assertIn("goated-hold: router-first", held)  # Routed as an unbriefed session is.
        s.load(ROUTER)
        s.say("goated-route: direct")
        self.branch(s, 0)
        self.assertNotIn("- Review:", self.large_turn(s))

    def test_a_typed_first_prompt_with_a_skills_line_is_no_brief(self) -> None:
        s = self.session()
        self.branch(s, 0)
        s.say("goated-skills: tdd")
        self.assertIn("- Review:", self.large_turn(s))

    def test_the_same_branch_in_a_typed_session_meets_it(self) -> None:
        s = self.session()
        self.branch(s, 0)
        self.assertIn("- Review:", self.large_turn(s))

    def test_a_briefed_full_route_still_meets_verification(self) -> None:
        s = self.briefed("goated-route: full | requires: tdd")
        s.load("tdd")
        self.write(s, "src/export.py", 6)
        s.run("pytest -q")
        s.say(DOC_SKIP)
        held = stop(s)["reason"]
        self.assertIn("- Verification:", held)
        self.assertNotIn("- Review:", held)


class VerificationItemTests(ReviewTestCase):
    """Outside a git checkout, so the branch's size is unknown: each other trigger alone."""

    def finished(self, s: Session) -> dict:
        s.run("pytest -q")
        s.say(DOC_SKIP)
        return stop(s)

    def assert_only_verification(self, held: dict) -> None:
        self.assertEqual(held.get("reason", "").split("\n", 1)[0], CLOSEOUT_HOLD)
        items = [line for line in held["reason"].splitlines() if line.startswith("- ")]
        self.assertEqual([line.split(":", 1)[0] for line in items], ["- Verification"])
        self.assertIn(f"`{VERIFY}`", items[0])

    def test_a_full_route_raises_it_and_a_standard_one_does_not(self) -> None:
        s = self.session("goated-route: full | requires: tdd")
        self.write(s, "src/export.py", 6)
        self.assert_only_verification(self.finished(s))
        s.load(VERIFY)
        self.assertEqual(stop(s), {})

        plain = self.session("goated-route: standard | requires: tdd")
        self.write(plain, "src/export.py", 6)
        self.assertEqual(self.finished(plain), {})

    def test_a_subagents_code_change_raises_it_and_a_docs_change_does_not(self) -> None:
        for path, raised in (("src/app.py", True), ("docs/guide.md", False)):
            with self.subTest(path=path):
                s = self.session()
                s.brief_with_handoff()
                agent = s.subagent("w1")
                agent.prompt("Implement it.", hook=False)
                agent.say(DESIGN_SKIP)
                agent.call("Edit", {"file_path": path, "old_string": "a", "new_string": "b"},
                           agent_id="w1", agent_type="general-purpose")
                agent.run("pytest -q")
                self.assertEqual(decision(s.spawn("w1", BRIEF)), "pass")
                held = self.finished(s)
                if raised:
                    self.assert_only_verification(held)
                else:
                    self.assertEqual(held, {})

    def test_a_sensitive_file_raises_it_and_a_lookalike_does_not(self) -> None:
        for path, raised in (("src/auth.py", True), ("src/author.py", False)):
            with self.subTest(path=path):
                s = self.session()
                s.say("goated-skip: code-security-review: a renamed constant, no trust boundary")
                self.write(s, path, 6)
                held = self.finished(s)
                if raised:
                    self.assert_only_verification(held)
                else:
                    self.assertEqual(held, {})

    def test_a_large_branch_raises_it(self) -> None:
        s = self.session()
        self.branch(s, 400)
        self.write(s, "src/export.py", 6)
        s.say(REVIEW_SKIP)
        self.assert_only_verification(self.finished(s))

    def test_one_skip_line_clears_both_verification_and_proof(self) -> None:
        s = self.session("goated-route: full | requires: tdd")
        self.write(s, "src/export.py", 6)
        s.say(DOC_SKIP)
        held = stop(s)["reason"]
        self.assertIn("- Proof:", held)
        self.assertIn("- Verification:", held)

        s.say("goated-skip: handoff: nothing is left unfinished here")
        held = stop(s)["reason"]
        self.assertIn("- Proof:", held)
        self.assertIn("- Verification:", held)

        s.say(PROOF_SKIP)
        self.assertEqual(stop(s), {})


class ReviewPointTests(ReviewTestCase):
    """A review or check met in one turn stays met across later turns while
    the branch has grown by fewer than 50 lines since it (round 7, R1)."""

    def follow_up(self, s: Session, path: str, count: int) -> dict:
        """A person's follow-up turn of the same task, writing `count` code
        lines to `path`, meeting every item but Review and Verification."""

        s.prompt("Tweak the export.")
        self.write(s, path, count)
        s.run("pytest -q")
        s.say(DOC_SKIP)
        return stop(s)

    def reviewed(self, s: Session, how: str = "load") -> None:
        """A turn on a 420-line branch that meets Review and Verification by
        `how`: their loads, with a change read, or their skip lines."""

        self.branch(s, 400)
        self.write(s, "src/export.py", 20)
        if how == "load":
            s.load(VERIFY)
        else:
            s.say(PROOF_SKIP)
        self.meet_the_rest(s)
        if how == "load":
            s.load(REVIEW)
        else:
            s.say(REVIEW_SKIP)
        self.assertEqual(stop(s), {})

    def items(self, held: dict) -> list[str]:
        return [line.split(":", 1)[0][2:] for line in held.get("reason", "").splitlines()
                if line.startswith("- ")]

    def test_a_review_by_load_lasts_under_50_lines_and_is_asked_at_50(self) -> None:
        s = self.session()
        self.reviewed(s)
        self.assertEqual(self.follow_up(s, "src/one.py", 20), {})
        held = self.follow_up(s, "src/two.py", 30)  # 50 lines since the review.
        self.assertEqual(self.items(held), ["Review", "Verification"])

    def test_meeting_it_again_sets_a_new_point(self) -> None:
        s = self.session()
        self.reviewed(s)
        self.follow_up(s, "src/one.py", 60)
        s.load(REVIEW)
        s.run("git diff")
        s.load(VERIFY)
        self.assertEqual(stop(s), {})
        self.assertEqual(self.follow_up(s, "src/two.py", 40), {})

    def test_skip_lines_set_both_points_and_they_survive_a_compaction(self) -> None:
        s = self.session()
        self.reviewed(s, how="skip")
        s.compact()
        self.assertEqual(self.follow_up(s, "src/one.py", 20), {})
        held = self.follow_up(s, "src/two.py", 30)
        self.assertEqual(self.items(held), ["Review", "Verification"])

    def test_a_new_tasks_route_ends_both_points(self) -> None:
        s = self.session()
        self.reviewed(s)
        self.turn(s)  # A new route line starts a new task.
        self.write(s, "src/one.py", 20)
        s.run("pytest -q")
        s.say(DOC_SKIP)
        self.assertEqual(self.items(stop(s)), ["Review", "Verification"])

    def test_the_other_verification_triggers_still_ask_in_each_turn(self) -> None:
        # The compaction drops the load, which otherwise counts until then.
        for trigger in ("full", "sensitive"):
            with self.subTest(trigger=trigger):
                s = self.session("goated-route: full | requires: tdd" if trigger == "full"
                                 else "goated-route: direct")
                self.reviewed(s)
                s.compact()
                s.prompt("Tweak the export.")
                if trigger == "full":
                    s.load("tdd")
                    path = "src/one.py"
                else:
                    s.say("goated-skip: code-security-review: a renamed constant, no boundary")
                    path = "src/auth.py"
                self.write(s, path, 6)
                s.run("pytest -q")
                s.say(DOC_SKIP)
                self.assertEqual(self.items(stop(s)), ["Verification"])

    def test_state_saved_before_review_points_loads_and_asks_as_before(self) -> None:
        s = self.session()
        self.reviewed(s)
        saved = s.config.state_dir / f"{s.session_id}.json"
        state = json.loads(saved.read_text(encoding="utf-8"))
        del state["review_points"]
        saved.write_text(json.dumps(state), encoding="utf-8")
        held = self.follow_up(s, "src/one.py", 20)
        self.assertEqual(self.items(held), ["Review", "Verification"])
        self.assertNotIn("could not", held["reason"])


class PortableStatementTests(unittest.TestCase):
    """The threshold, what is measured, and the triggers are the skills' own text (spec Constraints)."""

    def text(self, skill: str) -> str:
        return " ".join((REPO_ROOT / "skills" / "engineering" / skill / "SKILL.md")
                        .read_text(encoding="utf-8").split())

    def test_the_review_skill_states_the_threshold_and_what_is_measured(self) -> None:
        text = self.text(REVIEW)
        for words in ("400 or more changed lines in code files outside test paths", "untracked",
                      "docs, fixtures, configuration, and tests add nothing", "reviewer prompt"):
            self.assertIn(words, text)

    def test_the_verification_skill_states_its_four_triggers(self) -> None:
        text = self.text(VERIFY)
        for words in ("route is `full`", "a subagent changed code", "security-sensitive file",
                      "400 or more changed lines"):
            self.assertIn(words, text)


if __name__ == "__main__":
    unittest.main()
