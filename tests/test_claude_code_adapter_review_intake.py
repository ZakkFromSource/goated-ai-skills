"""Behavior tests for the `review-intake` gate (Ticket 070).

After a reviewer subagent's result arrives in a turn, the first write to a
code file in the project is held until `receiving-code-review` counts as
loaded, or a skip line naming it is written.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from claude_code_adapter_support import (
    BRIEF,
    REPO_ROOT,
    ROUTER,
    Session,
    decision,
    reason,
)

HOLD = "goated-hold: review-intake | justified-skip"
SKILL = "receiving-code-review"
SKIP = f"goated-skip: {SKILL}: the reviewer reported no findings at all"
SDD = "subagent-driven-development"
REVIEWER_PROMPT = "D:\\goated\\skills\\subagent-driven-development\\references\\reviewer-prompt.md"
IMPLEMENTER_PROMPT = (
    "D:\\goated\\skills\\subagent-driven-development\\references\\implementer-prompt.md")
REVIEWER_BRIEF = (
    "## Review Mode\n\nSpec and standards review of the export change.\n\n"
    "## Review Inputs\n\n- The diff against main.\n\n"
    "## Required Report Format\n\n- Status: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED\n- Findings with file paths.\n\n"
    "goated-skills: standards-and-spec-review\n"
)
IMPLEMENTER_BRIEF = (
    "## Task\n\nAdd the CSV exporter.\n\n## Ownership\n\n- src/export.py\n\n"
    "## Required Report Format\n\n- Status: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED\n- Changed paths and checks run.\n\n"
    "goated-skills: tdd\n"
)
CODE_EDIT = {"file_path": "src/export.py", "old_string": "a = 1", "new_string": "a = 2"}
DOCS_EDIT = {"file_path": "docs/export.md", "old_string": "old", "new_string": "new"}


def gate_line(output: dict) -> str:
    return reason(output).split("\n", 1)[0]


class ReviewIntakeTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self._sessions = 0

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def session(self) -> Session:
        self._sessions += 1
        folder = self.root / f"s{self._sessions}"
        folder.mkdir()
        s = Session(folder, session_id=f"session-{self._sessions}")
        self.turn(s)
        return s

    @staticmethod
    def turn(s: Session) -> None:
        s.prompt("Fix the CSV exporter.")
        s.load(ROUTER)
        s.say("goated-route: direct")

    def reviewer(self, s: Session, agent_id: str = "r1") -> None:
        s.load(SDD)
        s.read(REVIEWER_PROMPT)
        agent = s.subagent(agent_id)
        agent.prompt("Review the change.", hook=False)
        self.assertEqual(decision(s.spawn(agent_id, REVIEWER_BRIEF)), "pass")

    def edit(self, s: Session, tool_input: dict = CODE_EDIT) -> dict:
        return s.call("Edit", dict(tool_input))


class HoldTests(ReviewIntakeTestCase):
    def test_after_a_reviewer_returns_a_code_edit_is_held_until_the_skill_loads(self) -> None:
        s = self.session()
        self.reviewer(s)

        held = self.edit(s)
        self.assertEqual(gate_line(held), HOLD)
        self.assertIn(f"`{SKILL}`", reason(held))
        self.assertIn(f"goated-skip: {SKILL}: <reason>", reason(held))
        s.load(SKILL)
        self.assertEqual(decision(self.edit(s)), "pass")

    def test_near_miss_without_a_reviewer_the_edit_is_not_held(self) -> None:
        s = self.session()
        self.assertEqual(decision(self.edit(s)), "pass")

    def test_a_shell_write_to_a_code_file_is_held_too(self) -> None:
        s = self.session()
        self.reviewer(s)
        self.assertEqual(gate_line(s.run("echo 'a = 2' > src/export.py")), HOLD)
        self.assertEqual(decision(s.run("echo 'notes' > docs/notes.md")), "pass")

    def test_a_skip_line_naming_the_skill_clears_it_for_the_turn(self) -> None:
        s = self.session()
        self.reviewer(s)
        s.say(SKIP)
        self.assertEqual(decision(self.edit(s)), "pass")

    def test_near_miss_a_skip_line_naming_another_skill_does_not(self) -> None:
        s = self.session()
        self.reviewer(s)
        s.say("goated-skip: standards-and-spec-review: the reviewer reported no findings")
        self.assertEqual(gate_line(self.edit(s)), HOLD)

    def test_a_skip_line_lasts_only_for_its_turn(self) -> None:
        s = self.session()
        self.reviewer(s)
        s.say(SKIP)
        self.assertEqual(decision(self.edit(s)), "pass")
        self.turn(s)
        self.reviewer(s, "r2")
        self.assertEqual(gate_line(self.edit(s)), HOLD)

    def test_a_docs_edit_after_the_review_is_not_held_and_a_code_edit_is(self) -> None:
        s = self.session()
        self.reviewer(s)
        self.assertEqual(decision(self.edit(s, DOCS_EDIT)), "pass")
        self.assertEqual(gate_line(self.edit(s)), HOLD)

    def test_a_code_file_outside_the_project_is_not_held(self) -> None:
        s = self.session()
        self.reviewer(s)
        outside = str(s.root / "scratch" / "probe.py")
        self.assertEqual(decision(self.edit(s, dict(CODE_EDIT, file_path=outside))), "pass")


class ScopeTests(ReviewIntakeTestCase):
    def test_near_miss_a_reviewer_from_an_earlier_turn_holds_nothing_in_the_next(self) -> None:
        # Known limit: the review reports, the turn ends to ask the user, and the fixes
        # come in the next turn, which the gate does not see.
        s = self.session()
        self.reviewer(s)
        self.turn(s)
        self.assertEqual(decision(self.edit(s)), "pass")

    def test_near_miss_a_subagents_own_edit_after_the_parents_review_is_not_held(self) -> None:
        s = self.session()
        self.reviewer(s)
        agent = s.subagent("i2")
        agent.prompt("Apply the accepted findings.", hook=False)
        edit = agent.call("Edit", dict(CODE_EDIT), agent_id="i2", agent_type="general-purpose")
        self.assertEqual(decision(edit), "pass")
        self.assertEqual(gate_line(self.edit(s)), HOLD)


class TriggerTests(ReviewIntakeTestCase):
    def test_an_implementer_subagents_return_holds_nothing(self) -> None:
        s = self.session()
        s.load(SDD)
        s.read(IMPLEMENTER_PROMPT)
        s.subagent("i1").prompt("Implement.", hook=False)
        self.assertEqual(decision(s.spawn("i1", IMPLEMENTER_BRIEF)), "pass")
        self.assertEqual(decision(self.edit(s)), "pass")

    def test_a_handoff_briefed_subagents_return_holds_nothing(self) -> None:
        s = self.session()
        s.brief_with_handoff()
        s.subagent("h1").prompt("Audit.", hook=False)
        self.assertEqual(decision(s.spawn("h1", BRIEF)), "pass")
        self.assertEqual(decision(self.edit(s)), "pass")

    def test_a_held_reviewer_spawn_holds_nothing(self) -> None:
        s = self.session()
        s.load(SDD)
        s.read(REVIEWER_PROMPT)
        # No skills line, so the spawn gate holds it.
        brief = REVIEWER_BRIEF.replace("goated-skills: standards-and-spec-review\n", "")
        self.assertNotEqual(decision(s.spawn("r9", brief)), "pass")
        self.assertEqual(decision(self.edit(s)), "pass")

    def test_a_failed_reviewer_spawn_holds_nothing(self) -> None:
        s = self.session()
        s.load(SDD)
        s.read(REVIEWER_PROMPT)
        tool_use_id, output = s._judge("Agent", {"prompt": REVIEWER_BRIEF})
        self.assertEqual(decision(output), "pass")
        s._tool_result(tool_use_id, "Agent failed: API error.", is_error=True)
        self.assertEqual(decision(self.edit(s)), "pass")

    def test_a_background_reviewer_holds_only_once_its_completion_arrives(self) -> None:
        s = self.session()
        s.load(SDD)
        s.read(REVIEWER_PROMPT)
        s.subagent("bg1").prompt("Review.", hook=False)
        tool_use_id, output = s._judge("Agent", {"prompt": REVIEWER_BRIEF,
                                                 "run_in_background": True})
        self.assertEqual(decision(output), "pass")
        s._tool_result(tool_use_id, "Async agent launched successfully.", extra={
            "toolUseResult": {"isAsync": True, "status": "async_launched", "agentId": "bg1"}})
        self.assertEqual(decision(self.edit(s)), "pass")
        s._append({"type": "attachment", "attachment": {
            "type": "queued_command",
            "prompt": '<agent-message from="bg1">\n[Subagent hand-back] Two findings.'}})
        self.assertEqual(gate_line(self.edit(s)), HOLD)

    def test_a_reviewer_brief_sent_to_a_side_session_holds_nothing(self) -> None:
        s = self.session()
        s.load(SDD)
        s.read(REVIEWER_PROMPT)
        output = s.call("mcp__ccd_session__start_session",
                        {"prompt": REVIEWER_BRIEF, "title": "Review export"},
                        result="Session started.")
        self.assertEqual(decision(output), "pass")
        self.assertEqual(decision(self.edit(s)), "pass")


class EarlierLoadTests(ReviewIntakeTestCase):
    def test_a_load_from_an_earlier_turn_still_counted_meets_it(self) -> None:
        s = self.session()
        s.load(SKILL)
        # A hook after the load records it in the session's state, as any later call would.
        self.assertEqual(decision(self.edit(s, DOCS_EDIT)), "pass")
        self.turn(s)
        self.reviewer(s)
        self.assertEqual(decision(self.edit(s)), "pass")

    def test_near_miss_a_load_before_a_compaction_does_not(self) -> None:
        s = self.session()
        s.load(SKILL)
        self.assertEqual(decision(self.edit(s, DOCS_EDIT)), "pass")
        s.compact()
        self.turn(s)
        self.reviewer(s)
        self.assertEqual(gate_line(self.edit(s)), HOLD)


class SkillTextTests(unittest.TestCase):
    def test_the_skill_states_the_trigger_after_a_reviewer_subagent_returns(self) -> None:
        text = (REPO_ROOT / "skills" / "engineering" / SKILL / "SKILL.md").read_text(encoding="utf-8")
        activation = text.split("## Activation", 1)[1].split("\n## ", 1)[0]
        self.assertIn("reviewer subagent", activation)
        self.assertIn("before the first code edit", activation)


if __name__ == "__main__":
    unittest.main()
