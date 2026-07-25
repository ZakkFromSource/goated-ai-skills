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
    validate_knowledge_retrieval_fixtures,
    validate_onboarding_fixtures,
    validate_planning_fixtures,
    validate_registry,
    validate_route_fixtures,
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
