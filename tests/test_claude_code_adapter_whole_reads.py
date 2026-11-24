"""Ticket 092: required files are read whole, and a diff read counts before the load.

A `Read` with `limit` or `offset` does not count for a required design
reference, a registry reference, a spawn template, or `red-flags.md`; the
hold says to read the whole file. For the Review and Security items and the
`pr-review` gate, a change read after the last change counts whether it came
before or after the skill load. Each test drives the hook entry point with a
transcript in Claude Code's recorded shape (see
`claude_code_adapter_support.py`), and each pairs the behavior with a near miss.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from claude_code_adapter_support import (
    REPO_ROOT,
    ROUTER,
    Session,
    decision,
    owed,
    owed_names,
    git_branch_with_change,
    parse,
    reason,
)

DESIGN = "software-design-principles"
REFERENCES = "/opt/goated/skills/software-design-principles/references/"
RED_FLAGS = REFERENCES + "red-flags.md"
# A public top-level definition, which selects these three references.
DEFINITION = "def export(rows):\n" + "\n".join(f"    total_{n} = {n}" for n in range(5))
PLAIN = "\n".join(f"total_{n} = {n}" for n in range(6))
MOCKING = "/opt/goated/skills/tdd/references/mocking-and-seams.md"
# A test edit the registry's mock-or-patch pattern selects `MOCKING` for.
MOCK_EDIT = {"file_path": "tests/test_export.py", "old_string": "pass",
             "new_string": "client = MagicMock()"}
SPEC_TEMPLATE = "/opt/goated/skills/write-a-spec/references/spec-template.md"
# A shell write the registry's spec path selects `SPEC_TEMPLATE` for: a file
# edit lands owing its reads (Ticket 118), and a short shell write still holds.
SPEC_COPY = {"command": "cp a.md docs/specs/export.md"}
DECOUPLING = REFERENCES + "decoupling.md"
# A shell write to a configuration file that shows no text: it selects
# `decoupling.md` and, unable to land, still meets the design-reads hold.
SETTINGS_WRITE = {"command": "generate-settings > config/export.json"}
SPAWN_BRIEF = "D:\\goated\\skills\\handoff\\references\\spawn-brief.md"
IMPLEMENTER = "D:\\goated\\skills\\subagent-driven-development\\references\\implementer-prompt.md"
REVIEWER = "D:\\goated\\skills\\subagent-driven-development\\references\\reviewer-prompt.md"
HANDOFF_BRIEF = (
    "## Goal\n\nAudit the exporter.\n\n## Scope\n\n- Work in: src/export/\n\n"
    "## Done Means\n\n- A list of findings.\n\n## Report Back\n\n- Status: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED\n- Status and findings.\n\n"
    "goated-skills: code-security-review\n"
)
IMPLEMENTER_BRIEF = (
    "## Task\n\nAdd the exporter.\n\n## Ownership\n\n- src/export.py\n\n"
    "## Required Report Format\n\n- Status: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED\n- Status.\n\ngoated-skills: tdd\n"
)
REVIEWER_BRIEF = (
    "## Review Mode\n\nSpec review.\n\n## Review Inputs\n\n- The diff.\n\n"
    "## Required Report Format\n\n- Status: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED\n- Findings.\n\ngoated-skills: standards-and-spec-review\n"
)
REVIEW = "standards-and-spec-review"
SECURITY = "code-security-review"
DOC_SKIP = "goated-skip: doc-sync: internal constant with no documented behavior"
DESIGN_SKIP = "goated-skip: software-design-principles: one mechanical constant change"
OPEN_PR = {"command": "gh pr create --base main --title 'Add export' --body-file body.md"}
WHOLE = "no limit, offset, or pages"


def edit(path: str, new: str, old: str = "pass") -> dict:
    return {"file_path": path, "old_string": old, "new_string": new}


def hold_line(output: dict) -> str:
    return reason(output).split("\n", 1)[0]


def stop(s: Session) -> dict:
    return parse(s.hook("Stop", stop_hook_active=False, last_assistant_message=""))


def items(output: dict, name: str) -> list[str]:
    """The closeout's `name` items in a Stop or PreToolUse hook output."""

    text = output.get("reason") or reason(output)
    return [line for line in text.split("\n") if line.startswith(f"- {name}:")]


class WholeReadTestCase(unittest.TestCase):
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
        s.project.mkdir(parents=True, exist_ok=True)
        s.config.registry_path = REPO_ROOT / "stack" / "goated-stack.yaml"
        s.prompt("Do the task.")
        s.load(ROUTER)
        s.say("goated-route: direct")
        return s

    @staticmethod
    def later_turn(s: Session) -> None:
        stop(s)
        s.prompt("Carry on.")
        s.say("goated-route: continue")


class DesignReferenceTests(WholeReadTestCase):
    def designing(self) -> Session:
        s = self.routed()
        s.load(DESIGN)
        s.read(REFERENCES + "process.md")
        s.read(REFERENCES + "complexity-and-modules.md")
        return s

    def test_a_read_with_a_limit_leaves_the_reference_owed_and_a_whole_read_clears_it(self) -> None:
        s = self.designing()
        s.read(REFERENCES + "readability.md", limit=20)

        landed = s.call("Edit", edit("src/export.py", DEFINITION))
        self.assertEqual(decision(landed), "pass")
        self.assertEqual(owed_names(landed), {"readability.md"})
        self.assertIn(WHOLE, owed(landed))
        s.read(REFERENCES + "readability.md")
        self.later_turn(s)  # A new turn, where an unread reference would be owed again.
        self.assertEqual(owed(s.call("Edit", edit("src/export.py", DEFINITION))), "")

    def test_a_read_with_a_limit_leaves_the_hold_on_a_write_that_cannot_land(self) -> None:
        s = self.routed()
        s.load(DESIGN)
        s.read(DECOUPLING, limit=20)

        held = s.call("Bash", SETTINGS_WRITE)
        self.assertEqual(hold_line(held), "goated-hold: design-reads | justified-skip")
        self.assertIn("references/decoupling.md", reason(held))
        self.assertIn(WHOLE, reason(held))
        s.read(DECOUPLING)
        self.assertEqual(decision(s.call("Bash", SETTINGS_WRITE)), "pass")

    def test_a_read_with_an_offset_alone_is_partial(self) -> None:
        s = self.designing()
        s.read(REFERENCES + "readability.md", offset=10)

        self.assertEqual(owed_names(s.call("Edit", edit("src/export.py", DEFINITION))),
                         {"readability.md"})

    def test_a_whole_read_in_an_earlier_turn_counts_and_a_partial_one_does_not(self) -> None:
        s = self.designing()
        s.read(REFERENCES + "readability.md")
        self.later_turn(s)
        quiet = s.call("Edit", edit("src/export.py", DEFINITION))
        self.assertEqual((decision(quiet), owed(quiet)), ("pass", ""))

        # The near miss: the partial read of an earlier turn was not recorded as read.
        s = self.designing()
        s.read(REFERENCES + "readability.md", limit=20)
        self.later_turn(s)
        landed = s.call("Edit", edit("src/export.py", DEFINITION))
        self.assertEqual(owed_names(landed), {"readability.md"})


class RegistryReferenceTests(WholeReadTestCase):
    def test_a_read_with_a_limit_or_offset_leaves_the_hold_and_a_whole_read_clears_it(self) -> None:
        s = self.routed()
        s.load("write-a-spec")
        s.read(SPEC_TEMPLATE, limit=20)

        held = s.call("Bash", SPEC_COPY)
        self.assertEqual(hold_line(held), "goated-hold: reference-reads | justified-skip")
        self.assertIn(WHOLE, reason(held))
        s.read(SPEC_TEMPLATE, offset=5)
        self.assertEqual(hold_line(s.call("Bash", SPEC_COPY)),
                         "goated-hold: reference-reads | justified-skip")
        s.read(SPEC_TEMPLATE)
        self.assertEqual(decision(s.call("Bash", SPEC_COPY)), "pass")

    def test_a_file_edit_owes_the_reference_after_a_partial_read(self) -> None:
        s = self.routed()
        s.load("tdd")
        s.read(MOCKING, limit=20)

        landed = s.call("Edit", MOCK_EDIT)
        self.assertEqual(decision(landed), "pass")
        self.assertIn("tdd/references/mocking-and-seams.md", owed(landed))
        self.assertIn(WHOLE, owed(landed))
        s.read(MOCKING)
        self.later_turn(s)  # A new turn, where an unread reference would be owed again.
        self.assertEqual(owed(s.call("Edit", MOCK_EDIT)), "")


class SpawnTemplateTests(WholeReadTestCase):
    def test_each_template_read_with_a_limit_leaves_the_hold_and_a_whole_read_clears_it(self) -> None:
        for skill, template, brief in (("handoff", SPAWN_BRIEF, HANDOFF_BRIEF),
                                       ("subagent-driven-development", IMPLEMENTER, IMPLEMENTER_BRIEF),
                                       ("subagent-driven-development", REVIEWER, REVIEWER_BRIEF)):
            with self.subTest(template=template):
                s = self.routed()
                s.load(skill)
                s.read(template, limit=20)

                held = s.spawn("a1", brief)
                self.assertEqual(hold_line(held), "goated-hold: spawn | strict")
                self.assertIn(WHOLE, reason(held))
                s.read(template)
                self.assertEqual(decision(s.spawn("a2", brief)), "pass")


class RedFlagsTests(WholeReadTestCase):
    def designed(self) -> Session:
        s = self.routed()
        s.load(DESIGN)
        self.assertEqual(decision(s.call("Edit", edit("src/export.py", PLAIN))), "pass")
        s.run("pytest -q")
        s.say(DOC_SKIP)
        return s

    def test_a_partial_red_flags_read_leaves_the_design_item_at_stop_and_commit(self) -> None:
        s = self.designed()
        s.read(RED_FLAGS, limit=20)
        s.run("git diff")

        design = items(stop(s), "Design")
        self.assertEqual(len(design), 1, design)
        self.assertIn("red-flags.md", design[0])
        self.assertIn(WHOLE, design[0])
        s.load("commit-message")
        s.run("git diff")
        committed = s.call("Bash", {"command": 'git commit -m "Add export"'})
        self.assertIn("red-flags.md", "\n".join(items(committed, "Design")))

        s.read(RED_FLAGS)
        s.run("git diff")
        self.assertEqual(stop(s), {})

    def test_a_partial_read_before_a_small_fix_does_not_cover_it(self) -> None:
        # A small fix after a red-flags read needs only a change read (Ticket 089),
        # but only when that earlier read was whole.
        s = self.designed()
        s.read(RED_FLAGS, offset=1)
        s.run("git diff")
        self.assertEqual(decision(s.call("Edit", edit("src/export.py", "fix_0 = 0"))), "pass")
        s.run("pytest -q")
        s.run("git diff")
        self.assertIn("red-flags.md", "\n".join(items(stop(s), "Design")))

        s = self.designed()
        s.read(RED_FLAGS)
        s.run("git diff")
        self.assertEqual(decision(s.call("Edit", edit("src/export.py", "fix_0 = 0"))), "pass")
        s.run("pytest -q")
        s.run("git diff")
        self.assertEqual(stop(s), {})


class ReviewOrderTests(WholeReadTestCase):
    def large(self) -> Session:
        """A turn on a 420-line branch with every closeout item but Review met."""

        s = self.routed()
        git_branch_with_change(s.project, 400)
        s.say(DESIGN_SKIP)
        target = s.project / "src" / "export.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        content = "".join(f"line {n}\n" for n in range(20))
        target.write_text(content, encoding="utf-8")
        s.call("Write", {"file_path": "src/export.py", "content": content})
        s.load("verification-before-completion")
        s.run("pytest -q")
        s.say(DOC_SKIP)
        return s

    def test_a_diff_read_before_the_review_load_meets_the_review_item(self) -> None:
        s = self.large()
        s.run("git diff main")
        s.load(REVIEW)

        self.assertEqual(stop(s), {})

    def test_a_diff_read_before_the_last_change_does_not(self) -> None:
        s = self.large()
        s.run("git diff main")
        s.load(REVIEW)
        s.call("Edit", edit("src/export.py", "line 0", old="line 1"))
        s.run("pytest -q")

        review = items(stop(s), "Review")
        self.assertEqual(len(review), 1, review)
        self.assertNotIn("After loading", review[0])


class SecurityOrderTests(WholeReadTestCase):
    def changed_by_subagent(self) -> Session:
        """A turn in which a subagent changed `src/auth.py`; Security is the item left."""

        s = self.routed()
        s.load("verification-before-completion")
        s.say(DESIGN_SKIP)
        s.say(DOC_SKIP)
        s.brief_with_handoff()
        agent = s.subagent("b1")
        agent.prompt("Implement it.", hook=False)
        agent.say("goated-skip: code-security-review: the parent reviews the change")
        agent.call("Edit", edit("src/auth.py", "b", old="a"), agent_id="b1", agent_type="general-purpose")
        self.assertEqual(decision(s.spawn("b1", HANDOFF_BRIEF)), "pass")
        s.run("pytest -q")
        return s

    def test_a_diff_read_before_the_security_load_meets_the_security_item(self) -> None:
        s = self.changed_by_subagent()
        s.run("git diff")
        s.load(SECURITY)

        self.assertEqual(stop(s), {})

    def test_a_diff_read_before_the_last_sensitive_change_does_not(self) -> None:
        s = self.changed_by_subagent()
        s.run("git diff")
        s.load(SECURITY)
        s.call("Edit", edit("src/auth.py", "c", old="b"))
        s.run("pytest -q")

        security = items(stop(s), "Security")
        self.assertEqual(len(security), 1, security)
        self.assertNotIn("After loading", security[0])


class PullRequestReviewOrderTests(WholeReadTestCase):
    def described(self) -> Session:
        s = self.routed()
        git_branch_with_change(s.project, 450)
        s.load("pr-description")
        return s

    def test_a_diff_read_before_the_review_load_meets_pr_review(self) -> None:
        s = self.described()
        s.run("git diff main...HEAD")
        s.load(REVIEW)

        self.assertEqual(decision(s.call("Bash", OPEN_PR)), "pass")

    def test_a_diff_read_before_the_last_change_does_not(self) -> None:
        s = self.described()
        s.run("git diff main...HEAD")
        s.load(REVIEW)
        s.call("Edit", edit("README.md", "b", old="a"))

        held = s.call("Bash", OPEN_PR)
        self.assertEqual(decision(held), "deny")
        self.assertNotIn("after loading", reason(held))


if __name__ == "__main__":
    unittest.main()
