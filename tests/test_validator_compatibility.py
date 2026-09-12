"""Characterization tests for the validator's public compatibility surface."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from collections.abc import Callable
from contextlib import ExitStack, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import scripts.validate_skills as validator
from scripts.validation import shared
from scripts.validation.behavior_proof import (
    validate_behavior_proof_fixtures as validate_behavior_proof_concern,
    validate_output_communication_fixtures as validate_output_communication_concern,
    validate_review_verification_fixtures as validate_review_verification_concern,
)
from scripts.validation.merge_conflicts import (
    validate_merge_conflict_fixtures as validate_merge_conflict_concern,
)
from scripts.validation.onboarding import (
    validate_clarification_fixtures as validate_clarification_fixture_concern,
    validate_onboarding_fixtures as validate_onboarding_fixture_concern,
)
from scripts.validation.operations import (
    validate_setup_scribe_fixtures as validate_setup_scribe_concern,
    validate_wayfinding_fixtures as validate_wayfinding_concern,
)
from scripts.validation.planning import (
    validate_architecture_planning_fixtures as validate_architecture_planning_concern,
    validate_planning_fixtures as validate_planning_concern,
)
from scripts.validation.research import (
    validate_knowledge_retrieval_fixtures as validate_knowledge_retrieval_concern,
    validate_source_grounded_research_fixtures as validate_source_research_concern,
)
from scripts.validation.reporting import (
    build_validation_report,
    render_validation_report,
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
from scripts.validation.skill_packages import (
    SkillPackageValidation,
    validate_skill_packages,
)


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

ORCHESTRATED_VALIDATORS = (
    "validate_skill_packages",
    "validate_registry",
    "validate_route_fixtures",
    "validate_end_to_end_fixtures",
    "validate_clarification_fixtures",
    "validate_onboarding_fixtures",
    "validate_planning_fixtures",
    "validate_architecture_planning_fixtures",
    "validate_behavior_proof_fixtures",
    "validate_merge_conflict_fixtures",
    "validate_review_verification_fixtures",
    "validate_output_communication_fixtures",
    "validate_knowledge_retrieval_fixtures",
    "validate_source_grounded_research_fixtures",
    "validate_setup_scribe_fixtures",
    "validate_wayfinding_fixtures",
)

EXPECTED_SUCCESS_OUTPUT = "\n".join(
    (
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
            "Word-budget report: shared policy 1192 words "
            "(within 800-1,200 target)."
        ),
        (
            "Skills above the 1,500-word decomposition threshold: "
            "skills/agent-workflows/project-standards-calibration/SKILL.md, "
            "skills/engineering/architecture-design-map/SKILL.md, "
            "skills/engineering/code-refinement/SKILL.md, "
            "skills/engineering/code-security-review/SKILL.md, "
            "skills/engineering/diagnose/SKILL.md, "
            "skills/engineering/grill-with-docs/SKILL.md, "
            "skills/engineering/review-codebase-architecture/SKILL.md, "
            "skills/engineering/design-codebase-architecture/SKILL.md, "
            "skills/engineering/prototype/SKILL.md, "
            "skills/engineering/receiving-code-review/SKILL.md, "
            "skills/engineering/tdd/SKILL.md, "
            "skills/engineering/verification-before-completion/SKILL.md, "
            "skills/engineering/writing-plans/SKILL.md"
        ),
        (
            "Per-type soft targets remain review-only until registry roles "
            "are assigned budget classes."
        ),
        "",
        "Human-review notes: 0",
        "",
        "Report-only docs/example schema drift: 3",
        (
            "- issues/062-add-learning-capture-skill.md:161: possible legacy "
            "frontmatter example or drift: status:"
        ),
        (
            "- skills/productivity/learning-capture/references/examples.md:89: "
            "possible legacy frontmatter example or drift: status:"
        ),
        (
            "- skills/productivity/learning-capture/references/"
            "lesson-note-template.md:69: possible legacy frontmatter example "
            "or drift: status:"
        ),
        "",
    )
)

EXPECTED_EMPTY_REPOSITORY_OUTPUT = "\n".join(
    (
        "GOATED skill validation failed for 0 implemented skills.",
        "",
        "Blocking errors: 17",
        "- skills: missing skills directory",
        "- stack/goated-stack.yaml: missing required file",
        (
            "- stack/schemas/stack-registry.schema.json: "
            "missing required file"
        ),
        "- stack/goated-stack.yaml: missing required file",
        (
            "- stack/fixtures/end-to-end: "
            "no end-to-end fixtures found"
        ),
        (
            "- stack/fixtures/clarification: "
            "no clarification fixtures found"
        ),
        "- stack/fixtures/onboarding: no onboarding fixtures found",
        "- stack/fixtures/planning: no planning fixtures found",
        (
            "- stack/fixtures/architecture-planning: "
            "no architecture-planning fixtures found"
        ),
        (
            "- stack/fixtures/behavior-proof: "
            "no behavior-proof fixtures found"
        ),
        (
            "- stack/fixtures/merge-conflicts: "
            "no merge-conflict fixtures found"
        ),
        (
            "- stack/fixtures/review-verification: "
            "no review-verification fixtures found"
        ),
        (
            "- stack/fixtures/output-communication: "
            "no output-communication fixtures found"
        ),
        (
            "- stack/fixtures/knowledge-retrieval: "
            "no knowledge-retrieval fixtures found"
        ),
        (
            "- stack/fixtures/source-grounded-research: "
            "no source-grounded-research fixtures found"
        ),
        "- stack/fixtures/setup-scribe: no setup-scribe fixtures found",
        "- stack/fixtures/wayfinding: no wayfinding fixtures found",
        (
            "Integrated registry checked with 0 catalog entries; "
            "shared policy is 0 words (below 800-1,200 target)."
        ),
        "",
        "Human-review notes: 0",
        "",
        "Report-only docs/example schema drift: 0",
        "",
    )
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

    def test_aggregate_runs_each_concern_once_in_baseline_order(self) -> None:
        invocation_log: list[tuple[str, Path]] = []
        package_error = validator.Finding(
            "00-validate_skill_packages",
            "orchestration marker",
        )
        package_review_note = validator.Finding(
            "package-review-note",
            "review marker",
        )
        package_drift = validator.Finding(
            "package-drift",
            "drift marker",
        )
        package_result = SkillPackageValidation(
            errors=[package_error],
            review_notes=[package_review_note],
            drift=[package_drift],
            skill_files=(REPO_ROOT / "skills/example/SKILL.md",),
        )
        expected_errors = [package_error]
        phase_results: dict[
            str,
            SkillPackageValidation | list[validator.Finding],
        ] = {
            "validate_skill_packages": package_result,
        }

        for position, function_name in enumerate(
            ORCHESTRATED_VALIDATORS[1:],
            start=1,
        ):
            marker = validator.Finding(
                f"{position:02d}-{function_name}",
                "orchestration marker",
            )
            expected_errors.append(marker)
            phase_results[function_name] = [marker]

        def record_phase(
            function_name: str,
            result: SkillPackageValidation | list[validator.Finding],
        ) -> Callable[
            [Path],
            SkillPackageValidation | list[validator.Finding],
        ]:
            """Return a phase stand-in that records observable execution."""

            def validation_phase(
                repo: Path,
            ) -> SkillPackageValidation | list[validator.Finding]:
                invocation_log.append((function_name, repo))
                return result

            return validation_phase

        # Phase execution order is an explicit compatibility requirement.
        # Controlled stand-ins isolate orchestration from each concern's own
        # validation rules while marker results prove aggregate result order.
        with ExitStack() as patches:
            for function_name in ORCHESTRATED_VALIDATORS:
                patches.enter_context(
                    patch.object(
                        validator,
                        function_name,
                        side_effect=record_phase(
                            function_name,
                            phase_results[function_name],
                        ),
                    )
                )

            errors, review_notes, drift, skill_count = (
                validator.validate_skills(REPO_ROOT)
            )

        self.assertEqual(
            [function_name for function_name, _ in invocation_log],
            list(ORCHESTRATED_VALIDATORS),
        )
        self.assertTrue(
            all(repo == REPO_ROOT for _, repo in invocation_log),
            invocation_log,
        )
        self.assertEqual(errors, expected_errors)
        self.assertEqual(review_notes, [package_review_note])
        self.assertEqual(drift, [package_drift])
        self.assertEqual(skill_count, 1)

    def test_successful_cli_preserves_exact_output_and_zero_exit_status(self) -> None:
        result = run_validator()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, EXPECTED_SUCCESS_OUTPUT)
        self.assertEqual(result.stderr, "")

    def test_empty_repository_preserves_exact_failure_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            result = run_validator("--repo", temporary_directory)

        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stdout, EXPECTED_EMPTY_REPOSITORY_OUTPUT)
        self.assertEqual(result.stderr, "")


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
        self.assertEqual(policy_words, 1192)
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


class MergeConflictConcernValidationTests(unittest.TestCase):
    """Prove merge-conflict fixtures through their focused concern module."""

    def test_current_merge_conflict_fixtures_are_valid(self) -> None:
        self.assertEqual(validate_merge_conflict_concern(REPO_ROOT), [])


class ResearchConcernValidationTests(unittest.TestCase):
    """Prove retrieval and public research through their concern module."""

    def test_current_knowledge_retrieval_fixtures_are_valid(self) -> None:
        self.assertEqual(validate_knowledge_retrieval_concern(REPO_ROOT), [])

    def test_current_source_grounded_research_fixtures_are_valid(self) -> None:
        self.assertEqual(validate_source_research_concern(REPO_ROOT), [])


class OperationsConcernValidationTests(unittest.TestCase):
    """Prove Setup Scribe and Wayfinding through their concern module."""

    def test_current_setup_scribe_fixtures_are_valid(self) -> None:
        self.assertEqual(validate_setup_scribe_concern(REPO_ROOT), [])

    def test_current_wayfinding_fixtures_are_valid(self) -> None:
        self.assertEqual(validate_wayfinding_concern(REPO_ROOT), [])


class ReportingConcernTests(unittest.TestCase):
    """Prove count aggregation and presentation through the reporting module."""

    def test_success_report_collects_fixture_counts_and_returns_zero(self) -> None:
        report = build_validation_report(
            REPO_ROOT,
            errors=[],
            review_notes=[],
            drift=[],
            skill_count=37,
            registry_summary=(37, 1193, []),
        )
        output = StringIO()

        with redirect_stdout(output):
            exit_code = render_validation_report(report)

        self.assertEqual(exit_code, 0)
        self.assertEqual(report.fixture_counts["routing"], 9)
        self.assertIn(
            "Adaptive routing fixture validation passed for 9 scenarios.",
            output.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()
