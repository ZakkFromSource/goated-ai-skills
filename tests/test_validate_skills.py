"""Behavior tests for the repository validation command."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.validate_skills import (
    validate_clarification_fixtures,
    validate_onboarding_fixtures,
    validate_registry,
    validate_route_fixtures,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def copy_registry_fixture(destination: Path) -> Path:
    """Copy only the integrated stack and referenced skill catalog."""

    shutil.copytree(REPO_ROOT / "stack", destination / "stack")
    shutil.copytree(REPO_ROOT / "skills", destination / "skills")
    return destination / "stack" / "goated-stack.yaml"


def copy_onboarding_fixtures(destination: Path) -> Path:
    """Copy onboarding fixtures and return their destination directory."""

    fixture_destination = destination / "stack" / "fixtures" / "onboarding"
    shutil.copytree(
        REPO_ROOT / "stack" / "fixtures" / "onboarding",
        fixture_destination,
    )
    return fixture_destination


def copy_clarification_fixtures(destination: Path) -> Path:
    """Copy clarification fixtures and return their destination directory."""

    fixture_destination = destination / "stack" / "fixtures" / "clarification"
    shutil.copytree(
        REPO_ROOT / "stack" / "fixtures" / "clarification",
        fixture_destination,
    )
    return fixture_destination


class RegistryValidationTests(unittest.TestCase):
    def test_current_integrated_stack_registry_is_valid(self) -> None:
        self.assertEqual([], validate_registry(REPO_ROOT))

    def test_unknown_emitted_signal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            registry_path = copy_registry_fixture(fixture_root)
            registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
            registry["skills"][0]["emits_signals"].append("not-defined")
            registry_path.write_text(
                yaml.safe_dump(registry, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message for finding in validate_registry(fixture_root)
            ]

        self.assertIn(
            "skill emits undefined route signal: not-defined",
            messages,
        )

    def test_registry_structure_is_checked_against_json_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            registry_path = copy_registry_fixture(fixture_root)
            registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
            del registry["contracts"]
            registry_path.write_text(
                yaml.safe_dump(registry, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message for finding in validate_registry(fixture_root)
            ]

        self.assertTrue(
            any(
                message.startswith("registry schema violation")
                and "'contracts' is a required property" in message
                for message in messages
            )
        )

    def test_registry_category_must_match_skill_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            registry_path = copy_registry_fixture(fixture_root)
            registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
            registry["skills"][0]["category"] = "engineering"
            registry_path.write_text(
                yaml.safe_dump(registry, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message for finding in validate_registry(fixture_root)
            ]

        self.assertIn(
            "registry category 'engineering' does not match skill path category "
            "'agent-workflows'",
            messages,
        )

    def test_every_implemented_skill_must_be_registered(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            registry_path = copy_registry_fixture(fixture_root)
            registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
            removed_path = registry["skills"].pop(0)["path"]
            registry_path.write_text(
                yaml.safe_dump(registry, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message for finding in validate_registry(fixture_root)
            ]

        self.assertIn(
            f"implemented skill is missing from registry: {removed_path}",
            messages,
        )

    def test_alias_cannot_collide_with_a_canonical_skill_name(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            registry_path = copy_registry_fixture(fixture_root)
            registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
            alias_owner = registry["skills"][0]
            canonical_name = registry["skills"][1]["name"]
            alias_owner["aliases"].append(canonical_name)
            registry_path.write_text(
                yaml.safe_dump(registry, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message for finding in validate_registry(fixture_root)
            ]

        self.assertIn(
            f"alias {canonical_name!r} for {alias_owner['name']!r} collides "
            "with a canonical skill name",
            messages,
        )


class RouteFixtureValidationTests(unittest.TestCase):
    def test_current_route_fixtures_are_valid(self) -> None:
        self.assertEqual([], validate_route_fixtures(REPO_ROOT))

    def test_route_fixture_signal_must_be_defined_by_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            copy_registry_fixture(fixture_root)
            fixture_path = (
                fixture_root
                / "stack"
                / "fixtures"
                / "routing"
                / "tiny-task-bypass.yaml"
            )
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["route_signals"] = ["not-defined"]
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message for finding in validate_route_fixtures(fixture_root)
            ]

        self.assertIn(
            "routing fixture references undefined route signal: not-defined",
            messages,
        )

    def test_route_fixture_gate_must_resolve_to_shared_or_registered_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            copy_registry_fixture(fixture_root)
            fixture_path = (
                fixture_root
                / "stack"
                / "fixtures"
                / "routing"
                / "tiny-task-bypass.yaml"
            )
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["route"]["required_gates"].append("not-defined")
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message for finding in validate_route_fixtures(fixture_root)
            ]

        self.assertIn(
            "routing fixture references undefined gate: not-defined",
            messages,
        )

    def test_checkpoint_event_requires_material_signal_and_route_delta(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            copy_registry_fixture(fixture_root)
            fixture_path = (
                fixture_root
                / "stack"
                / "fixtures"
                / "routing"
                / "tiny-task-bypass.yaml"
            )
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["checkpoint_events"] = [
                {
                    "checkpoint": "during-arbitrary-work",
                    "trigger": "security-impact",
                }
            ]
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message for finding in validate_route_fixtures(fixture_root)
            ]

        self.assertIn(
            "routing fixture checkpoint event uses unsupported checkpoint: "
            "during-arbitrary-work",
            messages,
        )
        self.assertIn(
            "routing fixture checkpoint event must define route_delta",
            messages,
        )

    def test_approval_reuse_is_rejected_after_scope_or_reach_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            copy_registry_fixture(fixture_root)
            fixture_path = (
                fixture_root
                / "stack"
                / "fixtures"
                / "routing"
                / "tiny-task-bypass.yaml"
            )
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["approval"]["scope_or_reach_changed"] = True
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message for finding in validate_route_fixtures(fixture_root)
            ]

        self.assertIn(
            "routing fixture cannot reuse approval after scope or action reach changes",
            messages,
        )

    def test_evidence_expectations_must_name_reuse_and_invalidation_sets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            copy_registry_fixture(fixture_root)
            fixture_path = (
                fixture_root
                / "stack"
                / "fixtures"
                / "routing"
                / "tiny-task-bypass.yaml"
            )
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            del fixture["expected"]["evidence"]["invalidate"]
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message for finding in validate_route_fixtures(fixture_root)
            ]

        self.assertIn(
            "routing fixture expected.evidence.invalidate must be a string list",
            messages,
        )

    def test_required_route_fixture_scenario_cannot_be_removed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            copy_registry_fixture(fixture_root)
            (
                fixture_root
                / "stack"
                / "fixtures"
                / "routing"
                / "standard-work.yaml"
            ).unlink()

            messages = [
                finding.message for finding in validate_route_fixtures(fixture_root)
            ]

        self.assertIn(
            "missing required routing fixture: standard-work",
            messages,
        )

    def test_route_fixture_risk_flag_must_use_shared_vocabulary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            copy_registry_fixture(fixture_root)
            fixture_path = (
                fixture_root
                / "stack"
                / "fixtures"
                / "routing"
                / "tiny-task-bypass.yaml"
            )
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["profile"]["risk_flags"] = ["not-defined"]
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message for finding in validate_route_fixtures(fixture_root)
            ]

        self.assertIn(
            "routing fixture references undefined risk flag: not-defined",
            messages,
        )


class ClarificationFixtureValidationTests(unittest.TestCase):
    def test_current_clarification_fixtures_are_valid(self) -> None:
        self.assertEqual([], validate_clarification_fixtures(REPO_ROOT))

    def test_focused_mode_cannot_bundle_multiple_decision_questions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_clarification_fixtures(fixture_root)
            fixture_path = fixture_directory / "lightweight-no-question.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["question_budget"] = 2
            fixture["expected"]["questions"] = [
                "Which name should be used?",
                "Which release should include it?",
            ]
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_clarification_fixtures(fixture_root)
            ]

        self.assertIn(
            "focused clarification cannot bundle multiple decision questions",
            messages,
        )

    def test_rapid_mode_cannot_exceed_three_questions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_clarification_fixtures(fixture_root)
            fixture_path = fixture_directory / "rapid-three-question.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["question_budget"] = 4
            fixture["expected"]["questions"].append("Should there be a fallback?")
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_clarification_fixtures(fixture_root)
            ]

        self.assertIn(
            "rapid clarification cannot exceed three questions",
            messages,
        )

    def test_deep_dive_requires_unlimited_budget_and_summary_cadence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_clarification_fixtures(fixture_root)
            fixture_path = fixture_directory / "large-architecture-deep-dive.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["question_budget"] = 10
            fixture["expected"]["decisions"]["summary_cadence"] = ""
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_clarification_fixtures(fixture_root)
            ]

        self.assertIn(
            "deep-dive clarification must not have a preset question budget",
            messages,
        )
        self.assertIn(
            "deep-dive clarification requires a decision-summary cadence",
            messages,
        )

    def test_high_risk_decision_cannot_be_agent_defaulted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_clarification_fixtures(fixture_root)
            fixture_path = fixture_directory / "focused-irreversible-decision.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["risk"]["explicit_human_decision_required"] = False
            fixture["expected"]["risk"]["agent_defaulted"] = True
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_clarification_fixtures(fixture_root)
            ]

        self.assertIn(
            "irreversible or high-risk decisions require an explicit human "
            "decision and cannot be agent-defaulted",
            messages,
        )

    def test_prototype_must_remain_decision_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_clarification_fixtures(fixture_root)
            fixture_path = fixture_directory / "prototype-needed.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["prototype"]["production_work"] = True
            fixture["expected"]["envelope_delta"]["duplicate_full_closeout"] = True
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_clarification_fixtures(fixture_root)
            ]

        self.assertIn(
            "clarification prototype cannot produce production work",
            messages,
        )
        self.assertIn(
            "clarification must not produce a duplicate full closeout",
            messages,
        )


class OnboardingFixtureValidationTests(unittest.TestCase):
    def test_current_onboarding_fixtures_are_valid(self) -> None:
        self.assertEqual([], validate_onboarding_fixtures(REPO_ROOT))

    def test_routine_orientation_must_stay_silent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            copy_onboarding_fixtures(fixture_root)
            fixture_path = (
                fixture_root
                / "stack"
                / "fixtures"
                / "onboarding"
                / "lightweight-small-project.yaml"
            )
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["orientation"]["visible_report"] = True
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_onboarding_fixtures(fixture_root)
            ]

        self.assertIn(
            "routine onboarding orientation must stay silent",
            messages,
        )

    def test_lightweight_budget_cannot_require_governance_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_onboarding_fixtures(fixture_root)
            fixture_path = fixture_directory / "lightweight-small-project.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["artifact_budget"].append("project-standards")
            fixture["expected"]["artifact_actions"]["project-standards"] = "create"
            fixture["expected"]["evidence_bundle"]["reuse_by"].append(
                "project-standards"
            )
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_onboarding_fixtures(fixture_root)
            ]

        self.assertIn(
            "lightweight onboarding budget must contain only thin-policy-routing",
            messages,
        )

    def test_one_evidence_bundle_must_feed_every_budgeted_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_onboarding_fixtures(fixture_root)
            fixture_path = fixture_directory / "standard-incremental-refresh.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["evidence_bundle"]["reuse_by"].remove(
                "project-standards"
            )
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_onboarding_fixtures(fixture_root)
            ]

        self.assertIn(
            "onboarding evidence bundle must feed every budgeted artifact",
            messages,
        )

    def test_inferred_standards_require_provenance_and_freshness(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_onboarding_fixtures(fixture_root)
            fixture_path = fixture_directory / "standard-incremental-refresh.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            del fixture["expected"]["inferred_standards"][0]["freshness"]
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_onboarding_fixtures(fixture_root)
            ]

        self.assertIn(
            "inferred standards require statement, provenance, freshness, "
            "and confidence strings",
            messages,
        )

    def test_resumable_work_requires_ignore_check_and_temp_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_onboarding_fixtures(fixture_root)
            fixture_path = fixture_directory / "resume-from-handoff.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["continuity"]["verify_ignore_before_write"] = False
            fixture["expected"]["continuity"]["os_temp_fallback"] = False
            fixture["expected"]["continuity"]["links_durable_artifacts"] = False
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_onboarding_fixtures(fixture_root)
            ]

        self.assertIn(
            "resumable onboarding requires verify_ignore_before_write",
            messages,
        )
        self.assertIn(
            "resumable onboarding requires os_temp_fallback",
            messages,
        )
        self.assertIn(
            "resumable onboarding requires links_durable_artifacts",
            messages,
        )


if __name__ == "__main__":
    unittest.main()
