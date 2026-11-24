"""The translation layer keeps the adapter's behaviour (Ticket 080).

Ticket 080 put the rules behind the event model with no behaviour change. A
differential run of the adapter before and after the port found the
differences below; each test pins the result the adapter gave before it.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from claude_code_adapter_support import (
    BRIEF,
    ROUTER,
    SPAWN_BRIEF_PATH,
    Session,
    decision,
    owed,
    owed_names,
    parse,
    reason,
)
from goated_adapter import Config, translation
from goated_core import wording
from goated_core.state import StateStore

DESIGN = "software-design-principles"
REVIEWER_TEMPLATE = "/opt/goated/skills/subagent-driven-development/references/reviewer-prompt.md"
REVIEWER_BRIEF = (
    "## Goal\n\nReview the exporter change.\n\n## Scope\n\n- Work in: src/export/\n\n"
    "## Done Means\n\n- Findings.\n\n## Review Mode\n\nspec\n\n"
    "## Review Inputs\n\n- the diff\n\n## Required Report Format\n\n- Status: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED\n- findings\n\n"
    "goated-skills: standards-and-spec-review\n"
)
STANDARD = "goated-route: standard | requires: tdd"


class Case(unittest.TestCase):
    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.sessions = 0

    def session(self) -> Session:
        """A new session in a folder of its own, so subtests never share one."""

        self.sessions += 1
        folder = self.root / f"s{self.sessions}"
        folder.mkdir()
        s = Session(folder)
        s.project.mkdir(parents=True)
        return s

    def routed(self, route: str | None = "goated-route: direct") -> Session:
        s = self.session()
        s.prompt("Fix the exporter.")
        s.load(ROUTER)
        if route is not None:
            s.say(route)
        return s

    def edit(self, s: Session, path: str = "src/export.py", old: str = "a = 1",
             new: str = "a = 2") -> dict:
        return s.call("Edit", {"file_path": str(s.project / path), "old_string": old,
                               "new_string": new})


class RouteLinesCountWhereTheirCallWasMade(Case):
    """A call's route line counts at the call, wherever its result arrives."""

    def test_the_later_call_s_route_wins_whichever_finishes_first(self) -> None:
        for finish in (["toolu_a1", "toolu_a2"], ["toolu_a2", "toolu_a1"]):
            with self.subTest(finish=finish):
                s = self.routed(route=None)
                s._tool_uses([
                    ("toolu_a1", "Bash", {"command": "ls",
                                          "description": "list\ngoated-route: direct"}),
                    ("toolu_a2", "Bash", {"command": "pwd", "description": f"where\n{STANDARD}"}),
                ])
                for tool_id in finish:
                    s._tool_result(tool_id, "ok")
                self.assertIn("goated-hold: pipeline", reason(self.edit(s)))

    def test_a_judged_call_s_own_line_beats_a_sibling_that_finished_first(self) -> None:
        s = self.routed(route=None)
        own = {"command": "echo x > src/a.py", "description": "write\ngoated-route: direct"}
        s._tool_uses([("toolu_b1", "Bash", {"command": "ls", "description": f"list\n{STANDARD}"}),
                      ("toolu_b2", "Bash", own)])
        s._tool_result("toolu_b1", "ok")
        out = parse(s.hook("PreToolUse", tool_name="Bash", tool_input=own, tool_use_id="toolu_b2"))
        self.assertEqual(decision(out), "pass", reason(out))

    def test_a_call_id_recorded_twice_counts_its_first_input_s_lines(self) -> None:
        s = self.routed(route=None)
        s._tool_uses([("toolu_d1", "Bash", {"command": "ls",
                                            "description": "list\ngoated-route: direct"})])
        s._tool_uses([("toolu_d1", "Bash", {"command": "ls", "description": "list"})])
        s._tool_result("toolu_d1", "ok")
        out = self.edit(s, "src/a.py", "a", "b")
        self.assertEqual(decision(out), "pass", reason(out))


class FileWritesCountAsBefore(Case):
    def test_only_an_edit_with_empty_old_text_and_no_edits_list_creates_a_file(self) -> None:
        # A MultiEdit, or an Edit that also carries an `edits` list, is not
        # read as creating the file it names, so it needs no new-file reading.
        for tool, fields in (
            ("MultiEdit", {"edits": [{"old_string": "", "new_string": "x = 1"}]}),
            ("Edit", {"old_string": "", "new_string": "x = 1", "edits": []}),
        ):
            with self.subTest(tool=tool, fields=fields):
                s = self.routed()
                s.load(DESIGN)
                out = s.call(tool, {"file_path": str(s.project / "src" / "new.py"), **fields})
                self.assertEqual((decision(out), owed(out)), ("pass", ""), reason(out))
        # Near miss: a plain Edit with empty old text creates the file, so it
        # lands owing the new-file references (Ticket 118).
        s = self.routed()
        s.load(DESIGN)
        landed = self.edit(s, "src/new.py", "", "x = 1")
        self.assertEqual(decision(landed), "pass")
        self.assertEqual(owed_names(landed),
                         {"process.md", "complexity-and-modules.md", "readability.md"})

    def test_an_empty_edits_list_is_a_small_edit(self) -> None:
        s = self.routed()
        out = s.call("MultiEdit", {"file_path": str(s.project / "src" / "a.py"), "edits": []})
        self.assertEqual(decision(out), "pass", reason(out))


class ReviewersAreTheAgentToolsSubagents(Case):
    def edit_after_review(self, tool: str, agent_id: str | None) -> dict:
        s = self.routed()
        s.load("handoff")
        s.read(SPAWN_BRIEF_PATH)
        s.load("subagent-driven-development")
        s.read(REVIEWER_TEMPLATE)
        tool_use_id, out = s._judge(tool, {"prompt": REVIEWER_BRIEF, "description": "review"})
        self.assertEqual(decision(out), "pass", reason(out))
        extra = None if agent_id is None else {
            "toolUseResult": {"status": "completed", "agentId": agent_id}}
        s._tool_result(tool_use_id, "Findings: one bug in rounding.", extra=extra)
        return self.edit(s)

    def test_a_reviewer_subagent_counts_with_or_without_an_agent_id(self) -> None:
        for agent_id in ("abc123def4567890", None):
            with self.subTest(agent_id=agent_id):
                self.assertIn("goated-hold: review-intake",
                              reason(self.edit_after_review("Agent", agent_id)))

    def test_a_side_session_is_no_reviewer_subagent(self) -> None:
        out = self.edit_after_review("mcp__ccd_session__start_session", "abc123def4567890")
        self.assertNotIn("review-intake", reason(out))


class FrictionTellsSpawnToolsApart(Case):
    def test_a_held_agent_spawn_stays_open_when_a_side_session_starts(self) -> None:
        s = self.session()
        for take in range(3):
            s.prompt(f"Hand the audit off, take {take}.")
            s.load(ROUTER)
            s.brief_with_handoff()
            # A line that fails the grammar holds the spawn in every take, since a
            # typed prompt in the task would otherwise continue it (Ticket 119).
            s.say("goated-route: continue please")
            self.assertEqual(decision(s.spawn(f"a{take}aaaaaaaaaaaaaa", BRIEF)), "deny")
            s.call("Bash", {"command": "ls", "description": "list\ngoated-route: direct"})
            s.call("mcp__ccd_session__start_session", {"prompt": BRIEF})
        notice = s.prompt("Hand the audit off, take 3.")
        self.assertEqual(StateStore(s.config.state_dir).load(s.session_id)[0].friction, 3)
        self.assertIn("retrospective", str(notice))


class HoldsQuoteWrittenTextAsWritten(Case):
    """Text a hold quotes is never read as the hold's own wording slots."""

    def test_a_malformed_route_line_is_quoted_as_written(self) -> None:
        for line in ("goated-route: {{read}} with {{skill-tool}} {{no-range}}",
                     "goated-route: {{line-advice|route line|skip routing}}",
                     "goated-route: worse {{carrier}}"):
            with self.subTest(line=line):
                text = reason(self.edit(self.routed(route=line), "src/a.py", "a", "b"))
                self.assertIn(line.split(": ", 1)[1], text)

    def test_a_quoted_advice_slot_is_not_taken_for_the_hold_s_advice(self) -> None:
        s = self.routed(route="goated-route: {{line-advice|route line|skip routing}}")
        text = reason(self.edit(s, "src/a.py", "a", "b"))
        self.assertEqual(text.count("A route line in reply text may not be seen"), 1)


class EverySlotHasClaudeCodeWording(unittest.TestCase):
    SLOTS = {
        "skill-tool": wording.SKILL_TOOL, "read-tool": wording.READ_TOOL, "read": wording.READ,
        "no-range": wording.NO_RANGE, "file-edit-tools": wording.FILE_EDIT_TOOLS,
        "line-endings": wording.LINE_ENDINGS, "carrier": wording.CARRIER,
        "line-advice": wording.unseen_line_advice("route line", "skip routing"),
        "line-advice-short": wording.short_advice("route line", "skip routing"),
        "clearing": wording.clearing_section(["skip line"], ["skip tdd", "skip diagnose"], True),
        "clearing-short": wording.clearing_section(["route line", "skip line"],
                                                   ["skip routing", "skip tdd"], False),
    }

    def test_every_slot_is_filled_for_every_kind_of_held_event(self) -> None:
        self.assertEqual(set(self.SLOTS), wording.NAMES)
        for name, slot in self.SLOTS.items():
            for tool in ("Edit", "Bash", None):
                with self.subTest(slot=name, tool=tool):
                    text = translation.render(f"Before {slot} after\n{slot}", tool, "posix")
                    self.assertNotIn(wording.OPEN, text)
                    self.assertNotIn(wording.CLOSE, text)
                    self.assertNotIn("{{", text)

    def test_a_slot_with_no_wording_fails_loudly(self) -> None:
        with self.assertRaises(ValueError):
            translation.render(f"{wording.OPEN}spelling{wording.CLOSE}")


class ScratchFilesUnderAnOddlyNamedHome(Case):
    # `?` and `*` cannot be in a Windows file name.
    NAMES = ("ho$me", "ho%me", "ho`me") + (() if os.name == "nt" else ("ho*me", "ho?me"))

    def test_a_home_a_shell_would_expand_still_lets_a_scratch_write_through(self) -> None:
        for name in self.NAMES:
            with self.subTest(home=name):
                root = self.root / f"case-{self.NAMES.index(name)}"
                root.mkdir()
                s = Session(root)
                s.config = Config(state_dir=root / "state", home=root / name,
                                  lag_wait_seconds=0.0)
                s.project = s.cwd = root / "work" / "project"
                s.project.mkdir(parents=True)
                (root / "scratch").mkdir()
                s.prompt("Draft notes in a scratch file.")
                out = s.call("Write", {"file_path": str(root / "scratch" / "notes.txt"),
                                       "content": "notes"})
                self.assertEqual(decision(out), "pass", reason(out))


if __name__ == "__main__":
    unittest.main()
