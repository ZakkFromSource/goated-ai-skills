"""Characterization tests for the validator's public compatibility surface."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import scripts.validate_skills as validator
from scripts.validation import shared
from scripts.validation.behavior_proof import (
    validate_behavior_proof_fixtures as validate_behavior_proof_concern,
    validate_output_communication_fixtures as validate_output_communication_concern,
    validate_review_verification_fixtures as validate_review_verification_concern,
)
from scripts.validation.onboarding import (
    validate_clarification_fixtures as validate_clarification_fixture_concern,
    validate_onboarding_fixtures as validate_onboarding_fixture_concern,
)
from scripts.validation.planning import (
    validate_architecture_planning_fixtures as validate_architecture_planning_concern,
    validate_planning_fixtures as validate_planning_concern,
)
from scripts.validation.registry import (
    registry_summary as registry_concern_summary,
)
from scripts.validation.registry import (
    validate_registry as validate_registry_concern,
)
from scripts.validation.routing import (
    validate_end_to_end_fixtures as validate_end_to_end_fixture_concern,
    validate_route_fixtures as validate_route_fixture_concern,
)
from scripts.validation.skill_packages import validate_skill_packages


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_SCRIPT = REPO_ROOT / "scripts" / "validate_skills.py"

COMPATIBILITY_EXPORTS = (
    "validate_architecture_planning_fixtures",
    "validate_behavior_proof_fixtures",
    "validate_canonical_architecture_references",
    "validate_clarification_fixtures",
    "validate_end_to_end_fixtures",
    "validate_knowledge_retrieval_fixtures",
    "validate_merge_conflict_fixtures",
    "validate_onboarding_fixtures",
    "validate_output_communication_fixtures",
    "validate_planning_fixtures",
    "validate_registry",
    "validate_review_verification_fixtures",
    "validate_route_fixtures",
    "validate_setup_scribe_fixtures",
    "validate_source_grounded_research_fixtures",
    "validate_wayfinding_fixtures",
)

EXPECTED_SUCCESS_LINES = (
    "GOATED skill validation passed for 37 implemented skills.",
    "Integrated registry validation passed for 37 catalog entries.",
    "Adaptive routing fixture validation passed for 9 scenarios.",
    "End-to-end fixture validation passed for 4 scenarios.",
    "Onboarding fixture validation passed for 4 scenarios.",
    "Clarification fixture validation passed for 6 scenarios.",
    "Planning fixture validation passed for 5 scenarios.",
    (
        "Architecture and implementation-planning fixture validation "
        "passed for 5 scenarios."
    ),
    "Behavior-proof fixture validation passed for 14 scenarios.",
    "Merge-conflict fixture validation passed for 5 scenarios.",
    "Review-and-verification fixture validation passed for 7 scenarios.",
    "Output-and-communication fixture validation passed for 9 scenarios.",
    "Knowledge-retrieval fixture validation passed for 6 scenarios.",
    "Source-grounded-research fixture validation passed for 6 scenarios.",
    "Setup Scribe fixture validation passed for 8 scenarios.",
    "Wayfinding fixture validation passed for 10 scenarios.",
    (
        "Word-budget report: shared policy 1193 words "
        "(within 800-1,200 target)."
    ),
    "Human-review notes: 0",
    "Report-only docs/example schema drift: 3",
)


def run_validator(*arguments: str) -> subprocess.CompletedProcess[str]:
    """Run the public command exactly as repository users and CI invoke it."""

    return subprocess.run(
        [sys.executable, str(VALIDATOR_SCRIPT), *arguments],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


class ValidatorCompatibilityTests(unittest.TestCase):
    """Protect public imports, result grouping, presentation, and exit codes."""

    def test_existing_validation_function_imports_remain_callable(self) -> None:
        for export_name in COMPATIBILITY_EXPORTS:
            with self.subTest(export_name=export_name):
                self.assertTrue(callable(getattr(validator, export_name)))

    def test_finding_format_preserves_optional_line_numbers(self) -> None:
        without_line = validator.Finding("path/to/file.md", "message")
        with_line = validator.Finding("path/to/file.md", "message", line=12)

        self.assertEqual(without_line.format(), "path/to/file.md: message")
        self.assertEqual(with_line.format(), "path/to/file.md:12: message")

    def test_aggregate_results_preserve_baseline_groups(self) -> None:
        errors, review_notes, drift, skill_count = validator.validate_skills(
            REPO_ROOT
        )

        self.assertEqual(errors, [])
        self.assertEqual(review_notes, [])
        self.assertEqual(skill_count, 37)
        self.assertEqual(len(drift), 3)
        self.assertEqual(
            [finding.path for finding in drift],
            [
                "issues/062-add-learning-capture-skill.md",
                "skills/productivity/learning-capture/references/examples.md",
                (
                    "skills/productivity/learning-capture/references/"
                    "lesson-note-template.md"
                ),
            ],
        )

    def test_successful_cli_preserves_output_order_and_zero_exit_status(self) -> None:
        result = run_validator()

        self.assertEqual(result.returncode, 0, result.stderr)
        previous_position = -1
        for expected_line in EXPECTED_SUCCESS_LINES:
            with self.subTest(expected_line=expected_line):
                position = result.stdout.find(expected_line)
                self.assertGreater(position, previous_position, result.stdout)
                previous_position = position

    def test_invalid_repository_returns_nonzero_exit_status(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            result = run_validator("--repo", temporary_directory)

        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("GOATED skill validation failed", result.stdout)
        self.assertIn("Blocking errors", result.stdout)


class SharedValidationPrimitiveTests(unittest.TestCase):
    """Prove shared primitives without importing any concern implementation."""

    def test_public_text_scan_skips_private_and_generated_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = Path(temporary_directory)
            public_file = repo / "docs" / "guide.md"
            private_file = repo / ".local" / "notes.md"
            generated_file = repo / "__pycache__" / "module.py"
            public_file.parent.mkdir()
            private_file.parent.mkdir()
            generated_file.parent.mkdir()
            public_file.write_text("public", encoding="utf-8")
            private_file.write_text("private", encoding="utf-8")
            generated_file.write_text("generated", encoding="utf-8")

            scanned_files = shared.iter_public_text_files(repo)

        self.assertEqual(scanned_files, [public_file])

    def test_mapping_loader_reports_missing_and_non_mapping_documents(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = Path(temporary_directory)
            missing_path = repo / "missing.yaml"
            list_path = repo / "list.yaml"
            list_path.write_text("- one\n- two\n", encoding="utf-8")

            missing_mapping, missing_findings = shared.load_mapping(
                missing_path,
                "missing.yaml",
            )
            list_mapping, list_findings = shared.load_mapping(
                list_path,
                "list.yaml",
            )

        self.assertIsNone(missing_mapping)
        self.assertEqual(
            missing_findings,
            [shared.Finding("missing.yaml", "missing required file")],
        )
        self.assertIsNone(list_mapping)
        self.assertEqual(
            list_findings,
            [shared.Finding("list.yaml", "document must be a mapping")],
        )

    def test_fixture_contract_findings_keep_required_field_order(self) -> None:
        findings = shared.validate_fixture_contract_values(
            {"first": "wrong"},
            {"first": "expected", "second": True},
            "fixture.yaml",
            "shared contract",
        )

        self.assertEqual(
            [finding.message for finding in findings],
            [
                "shared contract requires first='expected'",
                "shared contract requires second=True",
            ],
        )


class SkillPackageValidationTests(unittest.TestCase):
    """Prove skill-package validation through its cohesive module interface."""

    def test_valid_skill_package_returns_no_findings(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = Path(temporary_directory)
            skill_file = (
                repo
                / "skills"
                / "engineering"
                / "example-skill"
                / "SKILL.md"
            )
            skill_file.parent.mkdir(parents=True)
            skill_file.write_text(
                "\n".join(
                    [
                        "---",
                        "name: example-skill",
                        "description: Demonstrate a valid skill package.",
                        "metadata:",
                        "  goated-category: engineering",
                        "---",
                        "",
                        "# Example Skill",
                        "",
                        "## Dependencies",
                        "",
                        "Hard: None.",
                        "",
                        "## Output Contract",
                        "",
                        "Return the example result.",
                    ]
                ),
                encoding="utf-8",
            )

            result = validate_skill_packages(repo)

        self.assertEqual(result.errors, [])
        self.assertEqual(result.review_notes, [])
        self.assertEqual(result.drift, [])
        self.assertEqual(result.skill_files, (skill_file,))


class RegistryConcernValidationTests(unittest.TestCase):
    """Prove registry validation without loading fixture concern modules."""

    def test_current_registry_and_word_budget_summary_are_valid(self) -> None:
        errors = validate_registry_concern(REPO_ROOT)
        catalog_count, policy_words, over_budget_paths = (
            registry_concern_summary(REPO_ROOT)
        )

        self.assertEqual(errors, [])
        self.assertEqual(catalog_count, 37)
        self.assertEqual(policy_words, 1193)
        self.assertIn(
            "skills/engineering/tdd/SKILL.md",
            over_budget_paths,
        )


class RoutingConcernValidationTests(unittest.TestCase):
    """Prove adaptive routing fixtures through the focused concern module."""

    def test_current_adaptive_routing_fixtures_are_valid(self) -> None:
        self.assertEqual(validate_route_fixture_concern(REPO_ROOT), [])

    def test_current_end_to_end_routing_fixtures_are_valid(self) -> None:
        self.assertEqual(validate_end_to_end_fixture_concern(REPO_ROOT), [])


class OnboardingConcernValidationTests(unittest.TestCase):
    """Prove clarification and onboarding through their concern module."""

    def test_current_clarification_fixtures_are_valid(self) -> None:
        self.assertEqual(validate_clarification_fixture_concern(REPO_ROOT), [])

    def test_current_onboarding_fixtures_are_valid(self) -> None:
        self.assertEqual(validate_onboarding_fixture_concern(REPO_ROOT), [])


class PlanningConcernValidationTests(unittest.TestCase):
    """Prove planning fixtures through the focused concern module."""

    def test_current_planning_fixtures_are_valid(self) -> None:
        self.assertEqual(validate_planning_concern(REPO_ROOT), [])

    def test_current_architecture_planning_fixtures_are_valid(self) -> None:
        self.assertEqual(validate_architecture_planning_concern(REPO_ROOT), [])


class BehaviorProofConcernValidationTests(unittest.TestCase):
    """Prove delivery-proof fixtures through their focused concern module."""

    def test_current_behavior_proof_fixtures_are_valid(self) -> None:
        self.assertEqual(validate_behavior_proof_concern(REPO_ROOT), [])

    def test_current_review_verification_fixtures_are_valid(self) -> None:
        self.assertEqual(validate_review_verification_concern(REPO_ROOT), [])

    def test_current_output_communication_fixtures_are_valid(self) -> None:
        self.assertEqual(validate_output_communication_concern(REPO_ROOT), [])


if __name__ == "__main__":
    unittest.main()
