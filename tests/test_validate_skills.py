"""Behavior tests for the repository validation command."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.validate_skills import (
    validate_architecture_planning_fixtures,
    validate_behavior_proof_fixtures,
    validate_canonical_architecture_references,
    validate_clarification_fixtures,
    validate_end_to_end_fixtures,
    validate_knowledge_retrieval_fixtures,
    validate_merge_conflict_fixtures,
    validate_onboarding_fixtures,
    validate_output_communication_fixtures,
    validate_planning_fixtures,
    validate_registry,
    validate_review_verification_fixtures,
    validate_route_fixtures,
    validate_setup_scribe_fixtures,
    validate_source_grounded_research_fixtures,
    validate_wayfinding_fixtures,
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


def copy_end_to_end_fixtures(destination: Path) -> Path:
    """Copy end-to-end fixtures and the registry used to resolve skill names."""

    fixture_destination = destination / "stack" / "fixtures" / "end-to-end"
    fixture_destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        REPO_ROOT / "stack" / "fixtures" / "end-to-end",
        fixture_destination,
    )
    shutil.copy(REPO_ROOT / "stack" / "goated-stack.yaml", destination / "stack")
    return fixture_destination


def copy_planning_fixtures(destination: Path) -> Path:
    """Copy planning fixtures and return their destination directory."""

    fixture_destination = destination / "stack" / "fixtures" / "planning"
    shutil.copytree(
        REPO_ROOT / "stack" / "fixtures" / "planning",
        fixture_destination,
    )
    return fixture_destination


def copy_architecture_planning_fixtures(destination: Path) -> Path:
    """Copy architecture and implementation-planning fixtures."""

    fixture_destination = (
        destination / "stack" / "fixtures" / "architecture-planning"
    )
    shutil.copytree(
        REPO_ROOT / "stack" / "fixtures" / "architecture-planning",
        fixture_destination,
    )
    return fixture_destination


def copy_behavior_proof_fixtures(destination: Path) -> Path:
    """Copy behavior-proof fixtures and return their destination directory."""

    fixture_destination = (
        destination / "stack" / "fixtures" / "behavior-proof"
    )
    shutil.copytree(
        REPO_ROOT / "stack" / "fixtures" / "behavior-proof",
        fixture_destination,
    )
    return fixture_destination


def copy_merge_conflict_fixtures(destination: Path) -> Path:
    """Copy merge-conflict fixtures and return their destination directory."""

    fixture_destination = destination / "stack" / "fixtures" / "merge-conflicts"
    shutil.copytree(
        REPO_ROOT / "stack" / "fixtures" / "merge-conflicts",
        fixture_destination,
    )
    return fixture_destination


def copy_wayfinding_fixtures(destination: Path) -> Path:
    """Copy Wayfinder fixtures and return their destination directory."""

    fixture_destination = destination / "stack" / "fixtures" / "wayfinding"
    shutil.copytree(
        REPO_ROOT / "stack" / "fixtures" / "wayfinding",
        fixture_destination,
    )
    return fixture_destination


def copy_knowledge_retrieval_fixtures(destination: Path) -> Path:
    """Copy knowledge-retrieval fixtures and return their directory."""

    fixture_destination = (
        destination / "stack" / "fixtures" / "knowledge-retrieval"
    )
    shutil.copytree(
        REPO_ROOT / "stack" / "fixtures" / "knowledge-retrieval",
        fixture_destination,
    )
    return fixture_destination


def copy_setup_scribe_fixtures(destination: Path) -> Path:
    """Copy Setup Scribe fixtures and return their destination directory."""

    fixture_destination = destination / "stack" / "fixtures" / "setup-scribe"
    shutil.copytree(
        REPO_ROOT / "stack" / "fixtures" / "setup-scribe",
        fixture_destination,
    )
    return fixture_destination


def copy_source_grounded_research_fixtures(destination: Path) -> Path:
    """Copy source-grounded-research fixtures and return their directory."""

    fixture_destination = (
        destination / "stack" / "fixtures" / "source-grounded-research"
    )
    shutil.copytree(
        REPO_ROOT / "stack" / "fixtures" / "source-grounded-research",
        fixture_destination,
    )
    return fixture_destination


def copy_review_verification_fixtures(destination: Path) -> Path:
    """Copy review and verification fixtures and return their directory."""

    fixture_destination = (
        destination / "stack" / "fixtures" / "review-verification"
    )
    shutil.copytree(
        REPO_ROOT / "stack" / "fixtures" / "review-verification",
        fixture_destination,
    )
    return fixture_destination


def copy_output_communication_fixtures(destination: Path) -> Path:
    """Copy output and communication fixtures and return their directory."""

    fixture_destination = (
        destination / "stack" / "fixtures" / "output-communication"
    )
    shutil.copytree(
        REPO_ROOT / "stack" / "fixtures" / "output-communication",
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

    def test_v1_names_resolve_to_one_v2_canonical_skill_each(self) -> None:
        registry = yaml.safe_load(
            (REPO_ROOT / "stack" / "goated-stack.yaml").read_text(
                encoding="utf-8"
            )
        )
        entries = {entry["name"]: entry for entry in registry["skills"]}

        self.assertEqual(["write-a-prd"], entries["write-a-spec"]["aliases"])
        self.assertEqual(
            ["prd-to-issues"],
            entries["spec-to-tickets"]["aliases"],
        )
        self.assertNotIn("write-a-prd", entries)
        self.assertNotIn("prd-to-issues", entries)
        self.assertEqual(
            ["plan-codebase-architecture"],
            entries["design-codebase-architecture"]["aliases"],
        )
        self.assertEqual(
            ["improve-codebase-architecture"],
            entries["review-codebase-architecture"]["aliases"],
        )
        self.assertNotIn("plan-codebase-architecture", entries)
        self.assertNotIn("improve-codebase-architecture", entries)

    def test_active_surfaces_use_canonical_architecture_names(self) -> None:
        self.assertEqual(
            [],
            validate_canonical_architecture_references(REPO_ROOT),
        )

    def test_deprecated_architecture_name_is_rejected_from_active_docs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            (fixture_root / "README.md").write_text(
                "Use plan-codebase-architecture for design.",
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_canonical_architecture_references(
                    fixture_root
                )
            ]

        self.assertIn(
            "active reference uses deprecated architecture skill name "
            "'plan-codebase-architecture'; use 'design-codebase-architecture'",
            messages,
        )


class PlanningFixtureValidationTests(unittest.TestCase):
    def test_current_planning_fixtures_are_valid(self) -> None:
        self.assertEqual([], validate_planning_fixtures(REPO_ROOT))

    def test_compact_spec_requires_every_compact_contract_section(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_planning_fixtures(fixture_root)
            fixture_path = fixture_directory / "compact-spec.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["sections"].remove("acceptance-criteria")
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_planning_fixtures(fixture_root)
            ]

        self.assertIn(
            "compact spec fixture is missing required section: acceptance-criteria",
            messages,
        )

    def test_multi_ticket_dependencies_must_reference_earlier_tickets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_planning_fixtures(fixture_root)
            fixture_path = fixture_directory / "multi-ticket.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["tickets"][0]["blocked_by"] = ["ticket-002"]
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_planning_fixtures(fixture_root)
            ]

        self.assertIn(
            "ticket ticket-001 depends on ticket-002 before it appears in order",
            messages,
        )

    def test_wide_refactor_migrations_must_be_blocked_by_expand(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_planning_fixtures(fixture_root)
            fixture_path = fixture_directory / "wide-refactor.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["tickets"][1]["blocked_by"] = []
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_planning_fixtures(fixture_root)
            ]

        self.assertIn(
            "wide-refactor migrate ticket ticket-002 must be blocked by "
            "expand ticket ticket-001",
            messages,
        )

    def test_wide_refactor_migrations_require_blast_radius_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_planning_fixtures(fixture_root)
            fixture_path = fixture_directory / "wide-refactor.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["tickets"][1]["blast_radius_basis"] = ""
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_planning_fixtures(fixture_root)
            ]

        self.assertIn(
            "wide-refactor migrate ticket ticket-002 must name its "
            "blast_radius_basis",
            messages,
        )

    def test_wide_refactor_contract_must_wait_for_every_migration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_planning_fixtures(fixture_root)
            fixture_path = fixture_directory / "wide-refactor.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["tickets"][3]["blocked_by"] = ["ticket-002"]
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_planning_fixtures(fixture_root)
            ]

        self.assertIn(
            "wide-refactor contract ticket ticket-004 must be blocked by every "
            "migrate ticket: ticket-002, ticket-003",
            messages,
        )

    def test_integration_branch_exception_requires_a_nonempty_reason(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_planning_fixtures(fixture_root)
            fixture_path = fixture_directory / "wide-refactor.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["integration_branch"] = {
                "used": True,
                "independently_green_batches": False,
                "reason": "",
            }
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_planning_fixtures(fixture_root)
            ]

        self.assertIn(
            "wide-refactor integration branch is allowed only when migration "
            "batches cannot remain green independently and the reason is recorded",
            messages,
        )

    def test_ticket_ready_frontier_must_match_completed_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_planning_fixtures(fixture_root)
            fixture_path = fixture_directory / "wide-refactor.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["ready_frontier"] = ["ticket-002"]
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_planning_fixtures(fixture_root)
            ]

        self.assertIn(
            "planning ticket ready_frontier must contain exactly the uncompleted "
            "tickets whose blockers are complete: ticket-001",
            messages,
        )

    def test_order_sample_must_report_each_ready_ticket_in_frontier_section(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_planning_fixtures(fixture_root)
            sample_path = (
                fixture_directory / "samples" / "wide-refactor-order.md"
            )
            sample = sample_path.read_text(encoding="utf-8").replace(
                "## Ready Frontier\n\n"
                "- `tickets/001-expand-shared-symbol-contract.md`",
                "## Ready Frontier\n\n- None",
            )
            sample_path.write_text(sample, encoding="utf-8")

            messages = [
                finding.message
                for finding in validate_planning_fixtures(fixture_root)
            ]

        self.assertIn(
            "planning order sample Ready Frontier is missing "
            "tickets/001-expand-shared-symbol-contract.md",
            messages,
        )

    def test_approved_ticket_batch_is_reused_when_reach_is_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_planning_fixtures(fixture_root)
            fixture_path = fixture_directory / "multi-ticket.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["approval"]["ask_again"] = True
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_planning_fixtures(fixture_root)
            ]

        self.assertIn(
            "planning fixture must reuse approval while scope and action reach "
            "remain unchanged",
            messages,
        )

    def test_ticket_sample_must_be_fresh_agent_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_planning_fixtures(fixture_root)
            sample_path = fixture_directory / "samples" / "single-ticket.md"
            sample = sample_path.read_text(encoding="utf-8").replace(
                "## Expected Proof",
                "## Evidence",
            )
            sample_path.write_text(sample, encoding="utf-8")

            messages = [
                finding.message
                for finding in validate_planning_fixtures(fixture_root)
            ]

        self.assertIn(
            "ticket ticket-001 sample is missing heading: ## Expected Proof",
            messages,
        )


class ArchitecturePlanningFixtureValidationTests(unittest.TestCase):
    def test_current_architecture_planning_fixtures_are_valid(self) -> None:
        self.assertEqual(
            [],
            validate_architecture_planning_fixtures(REPO_ROOT),
        )

    def test_current_state_mapping_cannot_route_to_prescriptive_design(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_architecture_planning_fixtures(fixture_root)
            fixture_path = (
                fixture_directory
                / "current-state-map-vs-architecture-design.yaml"
            )
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["routes"][0]["skill"] = (
                "design-codebase-architecture"
            )
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_architecture_planning_fixtures(
                    fixture_root
                )
            ]

        self.assertIn(
            "current-state-map must route to architecture-design-map",
            messages,
        )

    def test_architecture_review_cannot_become_a_prescriptive_blueprint(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_architecture_planning_fixtures(fixture_root)
            fixture_path = fixture_directory / "architecture-review-only.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["route"]["prescriptive_blueprint"] = True
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_architecture_planning_fixtures(
                    fixture_root
                )
            ]

        self.assertIn(
            "architecture review route requires prescriptive_blueprint=False",
            messages,
        )

    def test_inline_plan_promotion_reuses_discovery_and_decisions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_architecture_planning_fixtures(fixture_root)
            fixture_path = fixture_directory / "compact-plan-promotion.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["promotion"]["restart_discovery"] = True
            fixture["expected"]["promotion"]["preserves_decisions"] = False
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_architecture_planning_fixtures(
                    fixture_root
                )
            ]

        self.assertIn(
            "plan promotion requires restart_discovery=False",
            messages,
        )
        self.assertIn(
            "plan promotion requires preserves_decisions=True",
            messages,
        )


class BehaviorProofFixtureValidationTests(unittest.TestCase):
    def test_current_behavior_proof_fixtures_are_valid(self) -> None:
        self.assertEqual([], validate_behavior_proof_fixtures(REPO_ROOT))

    def test_broader_proof_surface_is_not_preferred(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_behavior_proof_fixtures(fixture_root)
            fixture_path = fixture_directory / "pure-unit-proof.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["selected_surface"] = "integration"
            fixture["expected"]["broader_surface_preferred"] = True
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_behavior_proof_fixtures(fixture_root)
            ]

        self.assertIn(
            "pure-unit-proof behavior requires selected_surface='unit'",
            messages,
        )
        self.assertIn(
            "pure-unit-proof behavior requires broader_surface_preferred=False",
            messages,
        )

    def test_non_tdd_proof_requires_a_recorded_reason(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_behavior_proof_fixtures(fixture_root)
            fixture_path = fixture_directory / "justified-non-tdd.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["reason_recorded"] = False
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_behavior_proof_fixtures(fixture_root)
            ]

        self.assertIn(
            "justified-non-tdd behavior requires reason_recorded=True",
            messages,
        )

    def test_no_debt_does_not_require_refinement_or_a_skip_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_behavior_proof_fixtures(fixture_root)
            fixture_path = fixture_directory / "no-refinement-debt.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["activate_full_refinement"] = True
            fixture["expected"]["skip_report_required"] = True
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_behavior_proof_fixtures(fixture_root)
            ]

        self.assertIn(
            "no-refinement-debt behavior requires activate_full_refinement=False",
            messages,
        )
        self.assertIn(
            "no-refinement-debt behavior requires skip_report_required=False",
            messages,
        )

    def test_overlapping_delegation_must_remain_sequential(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_behavior_proof_fixtures(fixture_root)
            fixture_path = fixture_directory / "overlapping-delegation.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["parallel_delegation_allowed"] = True
            fixture["expected"]["execution"] = "parallel"
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_behavior_proof_fixtures(fixture_root)
            ]

        self.assertIn(
            "overlapping-delegation behavior requires "
            "parallel_delegation_allowed=False",
            messages,
        )
        self.assertIn(
            "overlapping-delegation behavior requires execution='sequential'",
            messages,
        )


class MergeConflictFixtureValidationTests(unittest.TestCase):
    def test_current_merge_conflict_fixtures_are_valid(self) -> None:
        self.assertEqual([], validate_merge_conflict_fixtures(REPO_ROOT))

    def test_compatible_intents_must_preserve_both_sides(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_merge_conflict_fixtures(fixture_root)
            fixture_path = fixture_directory / "compatible-intent.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["preserves_both_intents"] = False
            fixture["expected"]["invents_unrelated_behavior"] = True
            fixture["expected"]["scoped_checks_run"] = False
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_merge_conflict_fixtures(fixture_root)
            ]

        self.assertIn(
            "compatible-intent behavior requires preserves_both_intents=True",
            messages,
        )
        self.assertIn(
            "compatible-intent behavior requires "
            "invents_unrelated_behavior=False",
            messages,
        )
        self.assertIn(
            "compatible-intent behavior requires scoped_checks_run=True",
            messages,
        )

    def test_incompatible_intent_requires_an_explicit_decision(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_merge_conflict_fixtures(fixture_root)
            fixture_path = fixture_directory / "incompatible-intent.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["semantic_tradeoff_explicit"] = False
            fixture["expected"]["user_decision_required"] = False
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_merge_conflict_fixtures(fixture_root)
            ]

        self.assertIn(
            "incompatible-intent behavior requires "
            "semantic_tradeoff_explicit=True",
            messages,
        )
        self.assertIn(
            "incompatible-intent behavior requires user_decision_required=True",
            messages,
        )

    def test_insufficient_evidence_stops_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_merge_conflict_fixtures(fixture_root)
            fixture_path = fixture_directory / "insufficient-evidence.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["both_intents_established"] = True
            fixture["expected"]["stop_for_evidence"] = False
            fixture["expected"][
                "finish_authorization_substitutes_for_evidence"
            ] = True
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_merge_conflict_fixtures(fixture_root)
            ]

        self.assertIn(
            "insufficient-evidence behavior requires "
            "both_intents_established=False",
            messages,
        )
        self.assertIn(
            "insufficient-evidence behavior requires stop_for_evidence=True",
            messages,
        )
        self.assertIn(
            "insufficient-evidence behavior requires "
            "finish_authorization_substitutes_for_evidence=False",
            messages,
        )

    def test_wrong_operation_allows_safe_abort_without_implied_authority(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_merge_conflict_fixtures(fixture_root)
            fixture_path = fixture_directory / "wrong-operation.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["stopped_before_edit"] = False
            fixture["expected"]["safe_abort_allowed"] = False
            fixture["expected"]["abort_authorized_by_skill"] = True
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_merge_conflict_fixtures(fixture_root)
            ]

        self.assertIn(
            "wrong-operation behavior requires stopped_before_edit=True",
            messages,
        )
        self.assertIn(
            "wrong-operation behavior requires safe_abort_allowed=True",
            messages,
        )
        self.assertIn(
            "wrong-operation behavior requires abort_authorized_by_skill=False",
            messages,
        )

    def test_continuation_requires_fresh_lifecycle_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_merge_conflict_fixtures(fixture_root)
            fixture_path = fixture_directory / "authorized-continuation.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["fresh_authorization_verified"] = False
            fixture["expected"]["continuation_limit"] = 2
            fixture["expected"]["state_reinspected_after_continue"] = False
            fixture["expected"]["stale_evidence_reused"] = True
            fixture["expected"]["next_conflict_authorized"] = True
            fixture["expected"]["push_allowed"] = True
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_merge_conflict_fixtures(fixture_root)
            ]

        self.assertIn(
            "authorized-continuation behavior requires "
            "fresh_authorization_verified=True",
            messages,
        )
        self.assertIn(
            "authorized-continuation behavior requires continuation_limit=1",
            messages,
        )
        self.assertIn(
            "authorized-continuation behavior requires "
            "state_reinspected_after_continue=True",
            messages,
        )
        self.assertIn(
            "authorized-continuation behavior requires stale_evidence_reused=False",
            messages,
        )
        self.assertIn(
            "authorized-continuation behavior requires "
            "next_conflict_authorized=False",
            messages,
        )
        self.assertIn(
            "authorized-continuation behavior requires push_allowed=False",
            messages,
        )


class KnowledgeRetrievalFixtureValidationTests(unittest.TestCase):
    def test_current_knowledge_retrieval_fixtures_are_valid(self) -> None:
        self.assertEqual([], validate_knowledge_retrieval_fixtures(REPO_ROOT))

    def test_current_authoritative_source_must_rank_first(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_knowledge_retrieval_fixtures(fixture_root)
            fixture_path = fixture_directory / "authoritative-source.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["ranked_results"].reverse()
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_knowledge_retrieval_fixtures(
                    fixture_root
                )
            ]

        self.assertIn(
            "knowledge retrieval must rank current authoritative evidence first",
            messages,
        )

    def test_retrieval_must_be_progressive_read_only_and_local(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_knowledge_retrieval_fixtures(fixture_root)
            fixture_path = fixture_directory / "authoritative-source.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["search"]["progressive"] = False
            fixture["expected"]["search"]["read_only"] = False
            fixture["expected"]["search"]["external_web"] = True
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_knowledge_retrieval_fixtures(
                    fixture_root
                )
            ]

        self.assertIn(
            "knowledge retrieval search must be progressive, read-only, and "
            "exclude external web research",
            messages,
        )

    def test_ranking_requires_all_claim_scoped_factors(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_knowledge_retrieval_fixtures(fixture_root)
            fixture_path = fixture_directory / "authoritative-source.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["ranking_factors"]["maturity"] = False
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_knowledge_retrieval_fixtures(
                    fixture_root
                )
            ]

        self.assertIn(
            "knowledge retrieval ranking requires authority, relevance, "
            "confidence, maturity, and freshness",
            messages,
        )

    def test_retrieval_distinguishes_every_knowledge_class(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_knowledge_retrieval_fixtures(fixture_root)
            fixture_path = fixture_directory / "authoritative-source.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["classifications_supported"].remove(
                "brainstorming"
            )
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_knowledge_retrieval_fixtures(
                    fixture_root
                )
            ]

        self.assertIn(
            "knowledge retrieval must distinguish authoritative, history, "
            "observation, inference, brainstorming, and stale material",
            messages,
        )

    def test_conflicts_cannot_be_silently_merged_or_nurtured(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_knowledge_retrieval_fixtures(fixture_root)
            fixture_path = fixture_directory / "conflicting-note.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["conflict"]["silently_merged"] = True
            fixture["expected"]["nurture"]["performed"] = True
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_knowledge_retrieval_fixtures(
                    fixture_root
                )
            ]

        self.assertIn(
            "knowledge retrieval must report conflicts without silently merging",
            messages,
        )
        self.assertIn(
            "knowledge retrieval may recommend learning-capture but cannot "
            "perform nurturing",
            messages,
        )

    def test_resolved_conflict_preserves_both_entries_and_invalidation(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_knowledge_retrieval_fixtures(fixture_root)
            fixture_path = fixture_directory / "conflicting-note.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            observation = fixture["expected"]["evidence_bundle"].pop()
            observation.pop("invalidated_by")
            fixture["expected"]["evidence_bundle"].append(observation)
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_knowledge_retrieval_fixtures(
                    fixture_root
                )
            ]

        self.assertIn(
            "resolved conflicts must preserve both evidence entries and link "
            "the invalidated entry to current authority",
            messages,
        )

    def test_stale_knowledge_must_remain_visible_and_qualified(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_knowledge_retrieval_fixtures(fixture_root)
            fixture_path = fixture_directory / "stale-note.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["report_staleness"] = False
            fixture["expected"]["silently_merge"] = True
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_knowledge_retrieval_fixtures(
                    fixture_root
                )
            ]

        self.assertIn(
            "stale knowledge must be reported without silent merge or discard",
            messages,
        )

    def test_missing_optional_capabilities_require_local_file_fallback(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_knowledge_retrieval_fixtures(fixture_root)
            fixture_path = (
                fixture_directory / "missing-capability-fallback.yaml"
            )
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["fallback"]["ordinary_files"] = False
            fixture["expected"]["external_web"] = True
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_knowledge_retrieval_fixtures(
                    fixture_root
                )
            ]

        self.assertIn(
            "missing capabilities must fall back to ordinary local files",
            messages,
        )
        self.assertIn(
            "knowledge retrieval fixtures must keep external web research out "
            "of scope",
            messages,
        )

    def test_ordinary_files_fixture_requires_a_real_selected_source(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_knowledge_retrieval_fixtures(fixture_root)
            fixture_path = fixture_directory / "ordinary-files-only.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["ordinary_files_sufficient"] = False
            fixture["expected"]["selected_path"] = "samples/missing.md"
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_knowledge_retrieval_fixtures(
                    fixture_root
                )
            ]

        self.assertIn(
            "ordinary-file retrieval requires a real selected_path and "
            "ordinary_files_sufficient=True",
            messages,
        )

    def test_retrieved_evidence_requires_scope_provenance_and_uncertainty(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_knowledge_retrieval_fixtures(fixture_root)
            fixture_path = fixture_directory / "authoritative-source.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            evidence_entry = fixture["expected"]["evidence_bundle"][0]
            evidence_entry.pop("relevance")
            evidence_entry.pop("applicable_scope")
            evidence_entry.pop("finding")
            evidence_entry.pop("provenance")
            evidence_entry.pop("uncertainty")
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_knowledge_retrieval_fixtures(
                    fixture_root
                )
            ]

        self.assertIn(
            "retrieved evidence entries require identifier, relevance, "
            "applicable_scope, finding, provenance, freshness, confidence, "
            "and uncertainty",
            messages,
        )

    def test_shared_evidence_freshness_requires_a_traceable_marker(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_knowledge_retrieval_fixtures(fixture_root)
            fixture_path = fixture_directory / "authoritative-source.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["evidence_bundle"][0]["freshness"] = "current"
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_knowledge_retrieval_fixtures(
                    fixture_root
                )
            ]

        self.assertIn(
            "retrieved evidence freshness requires a commit, date, or "
            "equivalent traceable marker",
            messages,
        )

    def test_fixture_validation_does_not_mutate_ordinary_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_knowledge_retrieval_fixtures(fixture_root)
            before = {
                path.relative_to(fixture_directory): path.read_bytes()
                for path in fixture_directory.rglob("*")
                if path.is_file()
            }

            self.assertEqual(
                [],
                validate_knowledge_retrieval_fixtures(fixture_root),
            )

            after = {
                path.relative_to(fixture_directory): path.read_bytes()
                for path in fixture_directory.rglob("*")
                if path.is_file()
            }

        self.assertEqual(before, after)

    def test_retrieval_contract_forbids_filesystem_and_note_mutation(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_knowledge_retrieval_fixtures(fixture_root)
            fixture_path = fixture_directory / "no-mutation.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["filesystem_mutated"] = True
            fixture["expected"]["note_updated"] = True
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_knowledge_retrieval_fixtures(
                    fixture_root
                )
            ]

        self.assertIn(
            "knowledge retrieval must not mutate files, notes, indexes, or caches",
            messages,
        )


class SourceGroundedResearchFixtureValidationTests(unittest.TestCase):
    """Validate current external-research fixture behavior."""

    def test_current_source_grounded_research_fixtures_are_valid(self) -> None:
        self.assertEqual(
            [],
            validate_source_grounded_research_fixtures(REPO_ROOT),
        )

    def _fixture_messages(
        self,
        fixture_name: str,
        mutate_fixture,
    ) -> list[str]:
        """Return validation messages after one temporary fixture mutation."""

        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_source_grounded_research_fixtures(
                fixture_root
            )
            fixture_path = fixture_directory / fixture_name
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            mutate_fixture(fixture)
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )
            return [
                finding.message
                for finding in validate_source_grounded_research_fixtures(
                    fixture_root
                )
            ]

    def test_research_requires_question_currency_hierarchy_and_safety(
        self,
    ) -> None:
        def remove_shared_contract(fixture) -> None:
            fixture["expected"]["question_framed"] = False
            fixture["expected"]["currency_requirement_framed"] = False
            fixture["expected"]["primary_sources_preferred"] = False
            fixture["expected"]["restricted_sources_respected"] = False

        messages = self._fixture_messages(
            "stale-source.yaml",
            remove_shared_contract,
        )

        self.assertIn(
            "stale-source behavior requires question_framed=True",
            messages,
        )
        self.assertIn(
            "stale-source behavior requires currency_requirement_framed=True",
            messages,
        )
        self.assertIn(
            "stale-source behavior requires primary_sources_preferred=True",
            messages,
        )
        self.assertIn(
            "stale-source behavior requires restricted_sources_respected=True",
            messages,
        )

    def test_evidence_requires_claim_scope_and_traceable_freshness(self) -> None:
        def weaken_evidence(fixture) -> None:
            fixture["expected"]["evidence_delta"][0].pop("applicable_scope")
            fixture["expected"]["evidence_delta"][0]["freshness"] = "current"

        messages = self._fixture_messages(
            "read-only-output.yaml",
            weaken_evidence,
        )

        self.assertIn(
            "research evidence entries require identifier, relevance, "
            "applicable_scope, finding, provenance, freshness, confidence, "
            "and uncertainty",
            messages,
        )
        self.assertIn(
            "research evidence freshness requires a publication, version, "
            "retrieval date, or equivalent traceable marker",
            messages,
        )

    def test_stale_sources_must_remain_visible_and_qualified(self) -> None:
        def hide_staleness(fixture) -> None:
            fixture["expected"]["stale_source_retained"] = False
            fixture["expected"]["current_claim_allowed"] = True

        messages = self._fixture_messages("stale-source.yaml", hide_staleness)

        self.assertIn(
            "stale-source behavior requires stale_source_retained=True",
            messages,
        )
        self.assertIn(
            "stale-source behavior requires current_claim_allowed=False",
            messages,
        )

    def test_conflicting_sources_cannot_be_merged_into_consensus(self) -> None:
        def merge_conflict(fixture) -> None:
            fixture["expected"]["false_consensus_created"] = True
            fixture["expected"]["unresolved_uncertainty_explicit"] = False

        messages = self._fixture_messages(
            "conflicting-sources.yaml",
            merge_conflict,
        )

        self.assertIn(
            "conflicting-sources behavior requires "
            "false_consensus_created=False",
            messages,
        )
        self.assertIn(
            "conflicting-sources behavior requires "
            "unresolved_uncertainty_explicit=True",
            messages,
        )

    def test_missing_primary_source_requires_qualified_fallback(self) -> None:
        def invent_primary_source(fixture) -> None:
            fixture["expected"]["primary_source_available"] = True
            fixture["expected"]["secondary_source_labelled"] = False
            fixture["expected"]["missing_evidence_explicit"] = False

        messages = self._fixture_messages(
            "no-primary-source.yaml",
            invent_primary_source,
        )

        self.assertIn(
            "no-primary-source behavior requires primary_source_available=False",
            messages,
        )
        self.assertIn(
            "no-primary-source behavior requires secondary_source_labelled=True",
            messages,
        )
        self.assertIn(
            "no-primary-source behavior requires missing_evidence_explicit=True",
            messages,
        )

    def test_inline_output_must_not_create_or_mutate_artifacts(self) -> None:
        def mutate_local_knowledge(fixture) -> None:
            fixture["expected"]["durable_artifact_created"] = True
            fixture["expected"]["local_knowledge_mutated"] = True

        messages = self._fixture_messages(
            "read-only-output.yaml",
            mutate_local_knowledge,
        )

        self.assertIn(
            "read-only-output behavior requires durable_artifact_created=False",
            messages,
        )
        self.assertIn(
            "read-only-output behavior requires local_knowledge_mutated=False",
            messages,
        )

    def test_durable_capture_reuses_convention_without_duplicate_truth(
        self,
    ) -> None:
        def duplicate_documentation(fixture) -> None:
            fixture["expected"]["capture_convention"] = "new-research-folder"
            fixture["expected"]["duplicate_truth_created"] = True
            fixture["expected"]["documentation_mirror_created"] = True
            fixture["expected"]["automatic_capture"] = True

        messages = self._fixture_messages(
            "durable-capture.yaml",
            duplicate_documentation,
        )

        self.assertIn(
            "durable-capture behavior requires "
            "capture_convention='project-owned-or-external-docs'",
            messages,
        )
        self.assertIn(
            "durable-capture behavior requires duplicate_truth_created=False",
            messages,
        )
        self.assertIn(
            "durable-capture behavior requires automatic_capture=False",
            messages,
        )

    def test_no_delegation_preserves_the_research_standard(self) -> None:
        def require_background_agents(fixture) -> None:
            fixture["expected"]["background_agents_required"] = True
            fixture["expected"]["single_agent_completed"] = False
            fixture["expected"]["evidence_standard_preserved"] = False

        messages = self._fixture_messages(
            "no-delegation-fallback.yaml",
            require_background_agents,
        )

        self.assertIn(
            "no-delegation-fallback behavior requires "
            "background_agents_required=False",
            messages,
        )
        self.assertIn(
            "no-delegation-fallback behavior requires "
            "single_agent_completed=True",
            messages,
        )
        self.assertIn(
            "no-delegation-fallback behavior requires "
            "evidence_standard_preserved=True",
            messages,
        )

    def test_every_required_research_scenario_must_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_source_grounded_research_fixtures(
                fixture_root
            )
            (fixture_directory / "stale-source.yaml").unlink()
            messages = [
                finding.message
                for finding in validate_source_grounded_research_fixtures(
                    fixture_root
                )
            ]

        self.assertIn(
            "missing required source-grounded-research fixture: stale-source",
            messages,
        )

    def test_fixture_validation_does_not_mutate_research_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_source_grounded_research_fixtures(
                fixture_root
            )
            before = {
                path.relative_to(fixture_directory): path.read_bytes()
                for path in fixture_directory.rglob("*")
                if path.is_file()
            }

            self.assertEqual(
                [],
                validate_source_grounded_research_fixtures(fixture_root),
            )

            after = {
                path.relative_to(fixture_directory): path.read_bytes()
                for path in fixture_directory.rglob("*")
                if path.is_file()
            }

        self.assertEqual(before, after)


class SetupScribeFixtureValidationTests(unittest.TestCase):
    def test_current_setup_scribe_fixtures_are_valid(self) -> None:
        self.assertEqual([], validate_setup_scribe_fixtures(REPO_ROOT))

    def test_backfill_preserves_all_three_evidence_states(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_setup_scribe_fixtures(fixture_root)
            fixture_path = fixture_directory / "mixed-evidence-backfill.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["evidence_states"].remove("unverified")
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_setup_scribe_fixtures(fixture_root)
            ]

        self.assertIn(
            "mixed-evidence-backfill behavior requires "
            "evidence_states=['verified', 'source-backed', 'unverified']",
            messages,
        )

    def test_generated_automation_is_not_executed_or_called_verified(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_setup_scribe_fixtures(fixture_root)
            fixture_path = (
                fixture_directory / "bash-native-helper-automation.yaml"
            )
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["executed"] = True
            fixture["expected"]["verified"] = True
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_setup_scribe_fixtures(fixture_root)
            ]

        self.assertIn(
            "bash-native-helper-automation behavior requires executed=False",
            messages,
        )
        self.assertIn(
            "bash-native-helper-automation behavior requires verified=False",
            messages,
        )

    def test_secret_values_cannot_enter_the_tracked_recipe(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_setup_scribe_fixtures(fixture_root)
            fixture_path = fixture_directory / "secret-rejection.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["secret_value_recorded"] = True
            fixture["expected"]["placeholder_used"] = False
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_setup_scribe_fixtures(fixture_root)
            ]

        self.assertIn(
            "secret-rejection behavior requires secret_value_recorded=False",
            messages,
        )
        self.assertIn(
            "secret-rejection behavior requires placeholder_used=True",
            messages,
        )

    def test_recipe_references_declarative_sources_without_duplication(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_setup_scribe_fixtures(fixture_root)
            fixture_path = fixture_directory / "source-of-truth-reuse.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["manifest_referenced"] = False
            fixture["expected"]["dependency_versions_duplicated"] = True
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_setup_scribe_fixtures(fixture_root)
            ]

        self.assertIn(
            "source-of-truth-reuse behavior requires manifest_referenced=True",
            messages,
        )
        self.assertIn(
            "source-of-truth-reuse behavior requires "
            "dependency_versions_duplicated=False",
            messages,
        )

    def test_project_settings_are_captured_while_personal_settings_are_excluded(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_setup_scribe_fixtures(fixture_root)
            fixture_path = fixture_directory / "personal-setting-exclusion.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["project_setting_captured"] = False
            fixture["expected"]["personal_setting_recorded"] = True
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_setup_scribe_fixtures(fixture_root)
            ]

        self.assertIn(
            "personal-setting-exclusion behavior requires "
            "project_setting_captured=True",
            messages,
        )
        self.assertIn(
            "personal-setting-exclusion behavior requires "
            "personal_setting_recorded=False",
            messages,
        )

    def test_every_required_setup_scribe_scenario_must_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_setup_scribe_fixtures(fixture_root)
            (fixture_directory / "no-reproducibility-impact.yaml").unlink()

            messages = [
                finding.message
                for finding in validate_setup_scribe_fixtures(fixture_root)
            ]

        self.assertIn(
            "missing required setup-scribe fixture: no-reproducibility-impact",
            messages,
        )


class WayfindingFixtureValidationTests(unittest.TestCase):
    def test_current_wayfinding_fixtures_are_valid(self) -> None:
        self.assertEqual([], validate_wayfinding_fixtures(REPO_ROOT))

    def test_chart_creation_requires_all_approved_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_wayfinding_fixtures(fixture_root)
            fixture_path = (
                fixture_directory / "branching-selection-and-approval.yaml"
            )
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["chart_approval"]["visible_frontier"] = False
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_wayfinding_fixtures(fixture_root)
            ]

        self.assertIn(
            "Wayfinder chart approval requires visible_frontier=True",
            messages,
        )

    def test_session_sized_work_cannot_select_wayfinder(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_wayfinding_fixtures(fixture_root)
            fixture_path = fixture_directory / "session-sized-rejection.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["rejection"]["selected"] = True
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_wayfinding_fixtures(fixture_root)
            ]

        self.assertIn(
            "Wayfinder rejection requires selected=False",
            messages,
        )

    def test_rejections_route_to_the_expected_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_wayfinding_fixtures(fixture_root)
            fixture_path = fixture_directory / "session-sized-rejection.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["rejection"]["route_to"] = "wayfinder"
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_wayfinding_fixtures(fixture_root)
            ]

        self.assertIn(
            "Wayfinder rejection requires route_to='grill-me'",
            messages,
        )

    def test_production_execution_cannot_be_enabled_by_pressure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_wayfinding_fixtures(fixture_root)
            fixture_path = fixture_directory / "no-execution-pressure.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["prohibited"]["production_implementation"] = True
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_wayfinding_fixtures(fixture_root)
            ]

        self.assertIn(
            "Wayfinder no-execution boundary requires "
            "production_implementation=False",
            messages,
        )

    def test_completed_state_requires_an_existing_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_wayfinding_fixtures(fixture_root)
            fixture_path = fixture_directory / "lifecycle-transitions.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            completed = next(
                state
                for state in fixture["expected"]["states"]
                if state["state"] == "completed"
            )
            completed["destination_path"] = "samples/destinations/missing.md"
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_wayfinding_fixtures(fixture_root)
            ]

        self.assertIn(
            "completed Wayfinder state requires an existing destination_path",
            messages,
        )

    def test_local_map_must_link_its_frontier_decision(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_wayfinding_fixtures(fixture_root)
            map_path = fixture_directory / "samples" / "map.md"
            map_text = map_path.read_text(encoding="utf-8").replace(
                "[Confirm synchronization guarantees]"
                "(decisions/002-confirm-synchronization-guarantees.md)",
                "Confirm synchronization guarantees",
            )
            map_path.write_text(map_text, encoding="utf-8")

            messages = [
                finding.message
                for finding in validate_wayfinding_fixtures(fixture_root)
            ]

        self.assertIn(
            "Wayfinder map sample must link its frontier decision sample",
            messages,
        )

    def test_local_decision_samples_validate_type_and_delivery_boundary(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_wayfinding_fixtures(fixture_root)
            decision_path = (
                fixture_directory
                / "samples"
                / "decisions"
                / "001-select-storage-strategy.md"
            )
            decision_text = decision_path.read_text(encoding="utf-8").replace(
                "\nresearch\n",
                "\ninvalid-type\n",
            )
            decision_text += "\n## Implementation Plan\n\nDeploy the change.\n"
            decision_path.write_text(decision_text, encoding="utf-8")

            messages = [
                finding.message
                for finding in validate_wayfinding_fixtures(fixture_root)
            ]

        self.assertIn(
            "Wayfinder sample "
            "samples/decisions/001-select-storage-strategy.md "
            "has unsupported decision type",
            messages,
        )
        self.assertIn(
            "Wayfinder decision sample contains delivery heading: "
            "## Implementation Plan",
            messages,
        )

    def test_lifecycle_cases_must_enter_every_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_wayfinding_fixtures(fixture_root)
            fixture_path = fixture_directory / "lifecycle-transitions.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["transitions"] = [
                transition
                for transition in fixture["expected"]["transitions"]
                if transition["to"] != "dropped"
            ]
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_wayfinding_fixtures(fixture_root)
            ]

        self.assertIn(
            "Wayfinder lifecycle transitions must enter every state",
            messages,
        )

    def test_lifecycle_state_snapshots_must_be_unique(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_wayfinding_fixtures(fixture_root)
            fixture_path = fixture_directory / "lifecycle-transitions.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["states"].append(
                {"state": "active", "actionable_frontier": True}
            )
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_wayfinding_fixtures(fixture_root)
            ]

        self.assertIn(
            "Wayfinder lifecycle states must not contain duplicates",
            messages,
        )

    def test_destination_handoff_reuses_discovery_and_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_wayfinding_fixtures(fixture_root)
            fixture_path = fixture_directory / "handoff-to-spec.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["handoff"]["restarts_discovery"] = True
            fixture["expected"]["handoff"]["reuses_evidence_links"] = False
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_wayfinding_fixtures(fixture_root)
            ]

        self.assertIn(
            "Wayfinder destination handoff requires restarts_discovery=False",
            messages,
        )
        self.assertIn(
            "Wayfinder destination handoff requires reuses_evidence_links=True",
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


class ReviewVerificationFixtureValidationTests(unittest.TestCase):
    def test_current_review_verification_fixtures_are_valid(self) -> None:
        self.assertEqual([], validate_review_verification_fixtures(REPO_ROOT))

    def test_fresh_evidence_discipline_cannot_be_weakened(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_review_verification_fixtures(fixture_root)
            fixture_path = fixture_directory / "tiny-diff-verification.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["fresh_evidence_required"] = False
            fixture["expected"]["claim_scope_limited_to_evidence"] = False
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_review_verification_fixtures(fixture_root)
            ]

        self.assertIn(
            "tiny-diff-verification behavior requires "
            "fresh_evidence_required=True",
            messages,
        )
        self.assertIn(
            "tiny-diff-verification behavior requires "
            "claim_scope_limited_to_evidence=True",
            messages,
        )

    def test_security_review_cannot_activate_without_a_sensitive_change(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_review_verification_fixtures(fixture_root)
            fixture_path = fixture_directory / "non-security-change.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["security_review_activated"] = True
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_review_verification_fixtures(fixture_root)
            ]

        self.assertIn(
            "non-security-change behavior requires "
            "security_review_activated=False",
            messages,
        )

    def test_required_review_verification_scenario_cannot_be_removed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_review_verification_fixtures(fixture_root)
            (fixture_directory / "review-feedback-classification.yaml").unlink()

            messages = [
                finding.message
                for finding in validate_review_verification_fixtures(fixture_root)
            ]

        self.assertIn(
            "missing required review-verification fixture: "
            "review-feedback-classification",
            messages,
        )


class OutputCommunicationFixtureValidationTests(unittest.TestCase):
    def test_current_output_communication_fixtures_are_valid(self) -> None:
        self.assertEqual([], validate_output_communication_fixtures(REPO_ROOT))

    def test_message_only_and_prompt_first_defaults_cannot_be_weakened(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_output_communication_fixtures(fixture_root)

            commit_fixture_path = fixture_directory / "message-only-commit.yaml"
            commit_fixture = yaml.safe_load(
                commit_fixture_path.read_text(encoding="utf-8")
            )
            commit_fixture["expected"]["suggests_commands"] = True
            commit_fixture_path.write_text(
                yaml.safe_dump(commit_fixture, sort_keys=False),
                encoding="utf-8",
            )

            prompt_fixture_path = fixture_directory / "prompt-first.yaml"
            prompt_fixture = yaml.safe_load(
                prompt_fixture_path.read_text(encoding="utf-8")
            )
            prompt_fixture["expected"]["first_output"] = "route-metadata"
            prompt_fixture_path.write_text(
                yaml.safe_dump(prompt_fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_output_communication_fixtures(fixture_root)
            ]

        self.assertIn(
            "message-only-commit behavior requires suggests_commands=False",
            messages,
        )
        self.assertIn(
            "prompt-first behavior requires first_output='finished-prompt'",
            messages,
        )

    def test_required_output_scenario_cannot_be_removed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_output_communication_fixtures(fixture_root)
            (
                fixture_directory / "multi-skill-consolidated-closeout.yaml"
            ).unlink()

            messages = [
                finding.message
                for finding in validate_output_communication_fixtures(fixture_root)
            ]

        self.assertIn(
            "missing required output-communication fixture: "
            "multi-skill-consolidated-closeout",
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


class EndToEndFixtureValidationTests(unittest.TestCase):
    def test_current_end_to_end_fixtures_are_valid(self) -> None:
        self.assertEqual([], validate_end_to_end_fixtures(REPO_ROOT))

    def test_diagnosis_minimizes_reproduction_before_ranking_hypotheses(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_end_to_end_fixtures(fixture_root)
            fixture_path = (
                fixture_directory / "bug-report-to-root-cause-fix.yaml"
            )
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            ordered_steps = fixture["expected"]["diagnosis"]["ordered_steps"]
            ordered_steps.remove("rank-falsifiable-hypotheses")
            minimization_index = ordered_steps.index(
                "minimize-confirmed-reproduction"
            )
            ordered_steps.insert(
                minimization_index,
                "rank-falsifiable-hypotheses",
            )
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_end_to_end_fixtures(fixture_root)
            ]

        self.assertIn(
            "diagnosis must minimize a confirmed reducible reproduction "
            "before ranking hypotheses",
            messages,
        )

    def test_required_end_to_end_scenario_cannot_be_removed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_end_to_end_fixtures(fixture_root)
            (fixture_directory / "bug-report-to-root-cause-fix.yaml").unlink()

            messages = [
                finding.message
                for finding in validate_end_to_end_fixtures(fixture_root)
            ]

        self.assertIn(
            "missing required end-to-end fixture: bug-report-to-root-cause-fix",
            messages,
        )

    def test_end_to_end_route_uses_registered_skills_and_one_closeout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            fixture_directory = copy_end_to_end_fixtures(fixture_root)
            fixture_path = fixture_directory / "feature-brief-to-verified-change.yaml"
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["selected_skills"].append("missing-skill")
            fixture["expected"]["closeout"]["single_task_closeout"] = False
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message
                for finding in validate_end_to_end_fixtures(fixture_root)
            ]

        self.assertIn(
            "end-to-end fixture references unregistered skill: missing-skill",
            messages,
        )
        self.assertIn(
            "end-to-end fixture requires one consolidated task closeout",
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
