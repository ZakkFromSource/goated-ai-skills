"""Ticket 096: a turn learns its closeout items before its report.

After a turn's first finished code change by a file edit tool, the
`PostToolUse` hook adds one note, as context for the agent, naming the
closeout items the turn will meet. The note never holds anything; the
closeout itself still decides. Each test drives the hook entry point with a
transcript in Claude Code's recorded shape (see
`claude_code_adapter_support.py`).
"""

from __future__ import annotations

import re
import tempfile
import time
import unittest
from pathlib import Path

from claude_code_adapter_support import (
    ROUTER,
    Session,
    decision,
    parse,
    reason,
)

CODE = "src/export.py"
AUTH = {"file_path": "src/auth.py", "content": "key = 1\n"}
FULL_ADVICE = "may not be seen"
SKILLS = "/opt/goated/skills"
ITEM_LABEL = re.compile(r"^- ([A-Z][a-z]+):", re.MULTILINE)


def small_edit(path: str = CODE) -> dict:
    return {"file_path": path, "old_string": "rate = 1", "new_string": "rate = 2"}


def large_write(path: str = CODE) -> dict:
    return {"file_path": path, "content": "".join(f"value_{n} = {n}\n" for n in range(30))}


def note(output: dict) -> str:
    """The note a PostToolUse output carries, or ""."""

    specific = output.get("hookSpecificOutput", {})
    if specific.get("hookEventName") != "PostToolUse":
        return ""
    return specific.get("additionalContext", "")


def labels(output: dict) -> list[str]:
    return ITEM_LABEL.findall(note(output))


def stop_reason(s: Session) -> str:
    return parse(s.hook("Stop", stop_hook_active=False, last_assistant_message="")).get("reason", "")


def change(s: Session, tool: str, tool_input: dict, *, recorded: bool = True,
           response: object = None, **fields) -> tuple[dict, dict]:
    """Make one file edit call as Claude Code runs it: PreToolUse; unless that
    holds the call, the tool runs and PostToolUse runs before the call's
    result is recorded. Returns both hooks' outputs ({} for a PostToolUse
    that never ran).

    `recorded=False` keeps even the call's tool_use out of the transcript
    until PostToolUse has returned. `response` replaces the tool's response.
    """

    tool_use_id = s._new_id()
    before = parse(s.hook("PreToolUse", tool_name=tool, tool_input=tool_input,
                          tool_use_id=tool_use_id, **fields))
    if recorded:
        s._tool_uses([(tool_use_id, tool, tool_input)])
    held = reason(before)
    if held:
        if not recorded:
            s._tool_uses([(tool_use_id, tool, tool_input)])
        s._tool_result(tool_use_id, held, is_error=True)
        return before, {}
    after = parse(s.hook(
        "PostToolUse", tool_name=tool, tool_input=tool_input, tool_use_id=tool_use_id,
        tool_response=response if response is not None else {
            "filePath": tool_input.get("file_path"), "success": True},
        **fields,
    ))
    if not recorded:
        s._tool_uses([(tool_use_id, tool, tool_input)])
    s._tool_result(tool_use_id, "The file was updated.")
    return before, after


class NoteCase(unittest.TestCase):
    """Sessions in a temporary folder, routed `direct` unless a test says otherwise."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def session(self, name: str = "s", route: str = "goated-route: direct") -> Session:
        folder = self.root / name
        folder.mkdir()
        s = Session(folder)
        s.prompt("Add CSV export.")
        s.load(ROUTER)
        s.say(route)
        return s

    def next_turn(self, s: Session) -> None:
        s.prompt("Next change.")
        s.load(ROUTER)
        s.say("goated-route: direct")


class FirstCodeChangeTests(NoteCase):
    """Ticket 096, AC1 and AC2: the first code change names the items the turn will meet."""

    def test_the_first_code_edit_names_proof_and_docs(self) -> None:
        s = self.session()
        before, after = change(s, "Edit", small_edit())
        self.assertEqual(decision(before), "pass")
        self.assertEqual(labels(after), ["Proof", "Docs"])
        text = note(after)
        self.assertIn("will ask for Proof and Docs. Meet each after your last code change", text)
        self.assertIn("before your final report", text)
        self.assertNotIn("goated-hold:", text)
        self.assertNotIn("permissionDecision", after["hookSpecificOutput"])
        self.assertNotIn("decision", after)

    def test_the_note_names_the_project_context_docs_that_exist(self) -> None:
        # Ticket 119: the adapter reports which exist; the note names only those.
        s = self.session()
        (s.project / "docs" / "agents").mkdir(parents=True)
        (s.project / "CONTEXT.md").write_text("# Context\n", encoding="utf-8")
        (s.project / "docs" / "agents" / "context-matrix.md").write_text("# M\n", encoding="utf-8")
        _, after = change(s, "Edit", small_edit())
        self.assertIn("context documents, for its terms, sources, and standards: "
                      "`CONTEXT.md` and `docs/agents/context-matrix.md`.", note(after))

    def test_the_note_names_no_context_docs_when_none_exists(self) -> None:
        _, after = change(self.session(), "Edit", small_edit())
        self.assertTrue(note(after))
        self.assertNotIn("context documents", note(after))

    def test_a_test_edit_names_proof_alone(self) -> None:
        # Near miss: a test file is code, but changes no behavior docs describe.
        s = self.session()
        _, after = change(s, "Edit", small_edit("tests/test_export.py"))
        self.assertEqual(labels(after), ["Proof"])

    def test_an_item_already_met_is_left_out(self) -> None:
        s = self.session()
        s.say("goated-skip: doc-sync: an internal constant with no documented behavior")
        _, after = change(s, "Edit", small_edit())
        self.assertEqual(labels(after), ["Proof"])

    def test_a_substantial_edit_with_design_loaded_names_the_red_flags(self) -> None:
        s = self.session()
        s.load("software-design-principles")
        for name in ("process", "complexity-and-modules", "readability"):
            s.read(f"{SKILLS}/software-design-principles/references/{name}.md")
        before, after = change(s, "Write", large_write())
        self.assertEqual(decision(before), "pass", reason(before))
        self.assertEqual(labels(after), ["Proof", "Docs", "Design"])
        self.assertIn("red-flags.md", note(after))

    def test_a_small_edit_with_design_loaded_earlier_names_no_design_item(self) -> None:
        # Near miss: the skill counts as loaded, but the edit is small.
        s = self.session()
        s.load("software-design-principles")
        self.next_turn(s)
        _, after = change(s, "Edit", small_edit())
        self.assertEqual(labels(after), ["Proof", "Docs"])

    def test_a_full_route_names_verification(self) -> None:
        s = self.session(route="goated-route: full | requires: tdd")
        s.load("tdd")
        _, after = change(s, "Edit", small_edit("tests/test_export.py"))
        self.assertEqual(labels(after), ["Proof", "Verification"])


class OncePerTurnTests(NoteCase):
    """Ticket 096, AC3: one note per turn."""

    def test_a_second_code_change_brings_none_and_the_next_turn_brings_one(self) -> None:
        s = self.session()
        _, first = change(s, "Edit", small_edit())
        _, second = change(s, "Edit", small_edit("src/other.py"))
        self.assertTrue(note(first))
        self.assertEqual(second, {})
        self.next_turn(s)
        _, next_turn = change(s, "Edit", small_edit())
        self.assertEqual(labels(next_turn), ["Proof", "Docs"])

    def test_the_same_list_is_noted_once_per_task_and_a_changed_list_again(self) -> None:
        # Round 7, R4: a follow-up turn of the same task, with the same list, gets none.
        s = self.session()
        _, first = change(s, "Edit", small_edit())
        self.assertEqual(labels(first), ["Proof", "Docs"])
        s.prompt("Tweak it.")
        _, same = change(s, "Edit", small_edit("src/other.py"))
        self.assertEqual(note(same), "")
        s.prompt("Now the full version.")
        s.load("software-design-principles")
        for name in ("process", "complexity-and-modules", "readability"):
            s.read(f"{SKILLS}/software-design-principles/references/{name}.md")
        _, changed = change(s, "Write", large_write("src/third.py"))
        self.assertEqual(labels(changed), ["Proof", "Docs", "Design"])

    def closeout_held(self, s: Session) -> None:
        """Change code by a shell command, which brings no note, then meet the
        closeout at a commit."""

        s.run("echo 'rate = 2' > src/export.py")
        s.load("commit-message")
        s.run("git diff")
        self.assertIn("goated-hold: closeout", reason(s.run('git commit -am "Change rate"')))

    def test_a_turn_that_already_met_a_closeout_hold_gets_none(self) -> None:
        s = self.session()
        self.closeout_held(s)
        _, after = change(s, "Edit", small_edit())
        self.assertEqual(after, {})

    def test_a_closeout_hold_in_an_earlier_turn_does_not_count(self) -> None:
        # Near miss: the closeout held in the previous turn, not this one.
        s = self.session()
        self.closeout_held(s)
        self.next_turn(s)
        _, after = change(s, "Edit", small_edit())
        self.assertEqual(labels(after), ["Proof", "Docs"])


class NoNoteTests(NoteCase):
    """Ticket 096, AC4 and AC10: what brings no note, each beside a change that brings one."""

    def test_a_docs_edit_brings_none_and_a_later_code_edit_still_brings_one(self) -> None:
        s = self.session()
        _, docs = change(s, "Edit", small_edit("docs/guide.md"))
        self.assertEqual(docs, {})
        _, code = change(s, "Edit", small_edit())
        self.assertEqual(labels(code), ["Proof", "Docs"])

    def test_a_held_edit_brings_none_and_claims_nothing(self) -> None:
        s = self.session()
        held, after = change(s, "Write", AUTH)
        self.assertEqual(decision(held), "deny")
        self.assertEqual(after, {})
        _, code = change(s, "Edit", small_edit())
        self.assertTrue(note(code))

    def test_a_failed_edit_brings_none(self) -> None:
        s = self.session()
        failed = parse(s.hook("PostToolUseFailure", tool_name="Edit", tool_input=small_edit(),
                              tool_use_id="toolu_failed", error="String not found in file."))
        self.assertEqual(failed, {})
        _, errored = change(s, "Edit", small_edit(), response="Error: String not found in file.")
        self.assertEqual(errored, {})
        _, unsuccessful = change(s, "Edit", small_edit(), response={"success": False})
        self.assertEqual(unsuccessful, {})
        _, code = change(s, "Edit", small_edit())
        self.assertTrue(note(code))

    def test_an_edit_outside_the_project_brings_none(self) -> None:
        s = self.session()
        _, outside = change(s, "Edit", small_edit(str(self.root / "scratch" / "probe.py")))
        self.assertEqual(outside, {})
        _, inside = change(s, "Edit", small_edit())
        self.assertTrue(note(inside))

    def test_a_shell_code_change_brings_none(self) -> None:
        s = self.session()
        command = {"command": "echo 'rate = 2' > src/export.py"}
        after = parse(s.hook("PostToolUse", tool_name="Bash", tool_input=command,
                             tool_use_id="toolu_shell", tool_response={"stdout": ""}))
        self.assertEqual(after, {})
        _, code = change(s, "Edit", small_edit())
        self.assertTrue(note(code))

    def test_a_subagents_edit_brings_none(self) -> None:
        s = self.session()
        agent = s.subagent("a1")
        agent.prompt("Change the rate.", hook=False)
        _, after = change(agent, "Edit", small_edit(), agent_id="a1",
                          agent_type="general-purpose")
        self.assertEqual(after, {})
        _, own = change(s, "Edit", small_edit())
        self.assertTrue(note(own))


class PayloadTests(NoteCase):
    """Ticket 096, AC5: the note is judged from the hook's payload."""

    def test_the_note_is_right_before_the_transcript_holds_the_call(self) -> None:
        s = self.session()
        _, after = change(s, "Edit", small_edit(), recorded=False)
        self.assertEqual(labels(after), ["Proof", "Docs"])

    def test_a_check_run_before_the_edit_leaves_proof_due(self) -> None:
        # Near miss: the transcript's last call is a passing check, so only the
        # payload's edit after it makes Proof due.
        s = self.session()
        s.run("pytest -q")
        _, after = change(s, "Edit", small_edit(), recorded=False)
        self.assertEqual(labels(after), ["Proof", "Docs"])


class MarkerTests(NoteCase):
    """Ticket 096, AC6 and AC7: the note's claim meets no other claim."""

    def test_advice_short_repeat_and_note_share_one_turn(self) -> None:
        s = self.session()
        first_hold, _ = change(s, "Write", AUTH)
        _, first_code = change(s, "Edit", small_edit())
        repeat, _ = change(s, "Write", AUTH)
        _, second_code = change(s, "Edit", small_edit("src/other.py"))
        holds = [reason(first_hold), reason(repeat)]
        self.assertEqual("".join(holds).count(FULL_ADVICE), 1, holds)
        self.assertNotIn("Still unmet", holds[0])
        self.assertIn("Still unmet", holds[1])
        self.assertEqual([bool(note(first_code)), bool(note(second_code))], [True, False])

    def test_the_note_before_any_hold_leaves_the_hold_full(self) -> None:
        # Near miss of the order above: the note's claim comes first.
        s = self.session()
        _, code = change(s, "Edit", small_edit())
        held, _ = change(s, "Write", AUTH)
        self.assertTrue(note(code))
        self.assertIn(FULL_ADVICE, reason(held))
        self.assertNotIn("Still unmet", reason(held))

    def test_an_unwritable_marker_adds_no_note_and_holds_nothing(self) -> None:
        s = self.session()
        # A file where the marker folder belongs: no marker can be made or read.
        (s.config.state_dir / "turn-markers").write_text("", encoding="utf-8")
        before, after = change(s, "Edit", small_edit())
        self.assertEqual(decision(before), "pass")
        self.assertEqual(after, {})


class CloseoutTests(NoteCase):
    """Ticket 096, AC8, AC9 and AC11: the note changes nothing the closeout decides."""

    def test_items_met_before_stop_end_the_turn_with_no_hold(self) -> None:
        s = self.session()
        _, after = change(s, "Edit", small_edit())
        self.assertEqual(labels(after), ["Proof", "Docs"])
        s.run("pytest -q")
        s.load("doc-sync")
        s.run("git diff")
        self.assertEqual(stop_reason(s), "")

    def test_an_unmet_item_still_holds_the_stop(self) -> None:
        # Near miss: the check ran, but the Docs item is left.
        s = self.session()
        change(s, "Edit", small_edit())
        s.run("pytest -q")
        self.assertIn("- Docs:", stop_reason(s))

    def test_a_failure_in_the_new_hook_adds_nothing(self) -> None:
        # The call already ran, so there is no action to explain as let through.
        s = self.session()
        missing = str(self.root / "missing.jsonl")
        unreadable = s.hook("PostToolUse", tool_name="Edit", tool_input=small_edit(),
                            tool_use_id="toolu_x", tool_response={"success": True},
                            transcript_path=missing)
        self.assertEqual(unreadable, "")
        self.assertEqual(s.hook("PostToolUse", tool_name="Edit", tool_input=small_edit(),
                                tool_response={"success": True}, session_id=""), "")
        # Near miss: the PreToolUse of the same failure still warns.
        warned = parse(s.hook("PreToolUse", tool_name="Edit", tool_input=small_edit(),
                              tool_use_id="toolu_x", transcript_path=missing))
        self.assertIn("allowed without checks", warned.get("systemMessage", ""))

    def test_a_lagging_transcript_after_the_note_adds_nothing_and_does_not_wait(self) -> None:
        s = self.session()
        _, first = change(s, "Edit", small_edit())
        self.assertTrue(note(first))
        s.config.lag_wait_seconds = 2.0
        started = time.monotonic()
        later = s.hook("PostToolUse", tool_name="Edit", tool_input=small_edit("src/other.py"),
                       tool_use_id="toolu_9", tool_response={"success": True},
                       prompt_id="prompt-not-yet-recorded")
        self.assertEqual(later, "")
        # The turn's note marker is checked before the transcript is read.
        self.assertLess(time.monotonic() - started, 1.0)

    def test_a_lagging_transcript_before_the_note_waits_then_adds_nothing(self) -> None:
        # Near miss: no note yet, so the hook must read the transcript, and waits for it.
        s = self.session()
        s.config.lag_wait_seconds = 0.3
        started = time.monotonic()
        output = s.hook("PostToolUse", tool_name="Edit", tool_input=small_edit(),
                        tool_use_id="toolu_9", tool_response={"success": True},
                        prompt_id="prompt-not-yet-recorded")
        self.assertEqual(output, "")
        self.assertGreaterEqual(time.monotonic() - started, 0.3)

    def test_without_the_hook_the_closeout_is_as_before(self) -> None:
        with_note, without = self.session("with"), self.session("without")
        change(with_note, "Edit", small_edit())
        without.call("Edit", small_edit())
        held = stop_reason(without)
        self.assertIn("- Proof:", held)
        self.assertEqual(stop_reason(with_note), held)


if __name__ == "__main__":
    unittest.main()
