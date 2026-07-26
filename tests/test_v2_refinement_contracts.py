"""Regression tests for the post-evaluation V2 consistency pass."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def read_repo_text(relative_path: str) -> str:
    """Read one tracked source file using UTF-8."""

    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


class SemanticConsistencyTests(unittest.TestCase):
    def test_grill_with_docs_activation_is_need_based(self) -> None:
        skill = read_repo_text("skills/engineering/grill-with-docs/SKILL.md")

        self.assertNotIn("Gated mandatory", skill)
        self.assertIn(
            "Do not activate it solely because work is cross-file",
            skill,
        )

    def test_grill_me_purpose_supports_proportionate_modes(self) -> None:
        skill = read_repo_text("skills/productivity/grill-me/SKILL.md")
        purpose = skill.split("## Inputs", maxsplit=1)[0]

        self.assertNotIn("one question at a time", purpose)
        self.assertNotIn("relentlessly", purpose)
        self.assertIn("proportionate", purpose)

    def test_router_uses_a_lazy_work_envelope(self) -> None:
        router = read_repo_text(
            "skills/agent-workflows/using-goated-ai-skills/SKILL.md"
        )

        self.assertNotIn("Record every profile dimension", router)
        self.assertIn("Always record goal, scope, action reach, and next action", router)
        self.assertIn(
            "Populate a profile dimension only when it changes routing",
            router,
        )

    def test_integrated_specialists_return_deltas_not_closeouts(self) -> None:
        expected = re.compile(
            r"In integrated use, return only material evidence, change, risk, "
            r"and route\s+deltas\."
        )
        for relative_path in (
            "skills/engineering/tdd/SKILL.md",
            "skills/engineering/subagent-driven-development/SKILL.md",
        ):
            with self.subTest(relative_path=relative_path):
                self.assertRegex(read_repo_text(relative_path), expected)

    def test_wayfinder_can_reuse_covering_envelope_consent(self) -> None:
        wayfinder = read_repo_text(
            "skills/agent-workflows/wayfinder/SKILL.md"
        )

        self.assertRegex(wayfinder, r"Existing envelope consent satisfies")
        self.assertRegex(wayfinder, r"all five chart\s+dimensions")

    def test_active_overview_uses_canonical_v2_delivery_terms(self) -> None:
        readme = read_repo_text("README.md")

        self.assertNotIn("draft PRDs", readme)
        self.assertNotIn("break work into issues", readme)
        self.assertNotIn("when gated mandatory", readme)


class SkillAuthoringDisciplineTests(unittest.TestCase):
    def test_creator_prices_independent_invocation_and_phase_completion(self) -> None:
        skill = read_repo_text(
            "skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md"
        )

        self.assertIn("independent invocation", skill)
        self.assertIn("context cost", skill)
        self.assertIn("observable completion condition", skill)

    def test_evaluation_removes_a_concrete_no_op_instruction(self) -> None:
        evaluation = read_repo_text(
            "skills/agent-workflows/framework-agnostic-skill-creator/"
            "references/skill-evaluation.md"
        )

        self.assertIn('"Be clear and thorough."', evaluation)
        self.assertIn("Remove it as a no-op", evaluation)

    def test_evaluation_progressively_discloses_branch_only_work(self) -> None:
        evaluation = read_repo_text(
            "skills/agent-workflows/framework-agnostic-skill-creator/"
            "references/skill-evaluation.md"
        )

        self.assertIn(
            "Only the port branch needs a compatibility matrix",
            evaluation,
        )
        self.assertIn("branch-specific pointer", evaluation)
        self.assertIn("positive target behavior", evaluation)


class ReferenceNavigationTests(unittest.TestCase):
    def test_long_skill_references_have_contents_navigation(self) -> None:
        missing_contents: list[str] = []
        broken_targets: list[str] = []
        for reference in sorted(REPO_ROOT.glob("skills/**/references/*.md")):
            text = reference.read_text(encoding="utf-8")
            if len(text.splitlines()) <= 100:
                continue

            relative_path = reference.relative_to(REPO_ROOT).as_posix()
            if "\n## Contents\n" not in text:
                missing_contents.append(relative_path)
                continue

            rendered_heading_slugs: set[str] = set()
            in_fence = False
            for line in text.splitlines():
                if line.startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence or not line.startswith("## "):
                    continue

                heading = line.removeprefix("## ").strip().lower()
                slug = re.sub(r"[^\w -]", "", heading)
                rendered_heading_slugs.add(slug.replace(" ", "-"))

            contents = text.split("\n## Contents\n", maxsplit=1)[1]
            contents = contents.split("\n## ", maxsplit=1)[0]
            for target in re.findall(r"\]\(#([^)]+)\)", contents):
                if target not in rendered_heading_slugs:
                    broken_targets.append(f"{relative_path}#{target}")

        self.assertEqual([], missing_contents)
        self.assertEqual([], broken_targets)


class ContinuousIntegrationTests(unittest.TestCase):
    def test_ci_runs_the_repository_acceptance_commands(self) -> None:
        workflow = read_repo_text(".github/workflows/validate.yml")

        self.assertIn('python-version: ["3.11", "3.14"]', workflow)
        self.assertIn('python-version: ${{ matrix.python-version }}', workflow)

        for command in (
            "uv run python scripts/validate_skills.py",
            "uv run python -m unittest discover -s tests -v",
            "uv run python scripts/compare_v1_v2_context.py",
        ):
            with self.subTest(command=command):
                self.assertIn(command, workflow)

        action_references = re.findall(r"uses:\s+[^@\s]+@([^\s]+)", workflow)
        self.assertTrue(action_references)
        for action_reference in action_references:
            with self.subTest(action_reference=action_reference):
                self.assertRegex(action_reference, r"^[0-9a-f]{40}$")


if __name__ == "__main__":
    unittest.main()
