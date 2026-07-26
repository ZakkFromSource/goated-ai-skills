"""Read-only validator for GOATED AI Skills source-repo skill files.

This script is intentionally plain Python. It is meant to be easy for a future
maintainer to inspect and change without learning a test framework, linter, or
custom validation library first.

The validator has three result types:

- blocking errors: fail the command and should be fixed before committing;
- human-review notes: do not fail, but ask a reviewer to look at a standard
  optional field such as `compatibility`;
- report-only drift: do not fail, but point to docs/examples that may still
  mention old schema fields.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

if __package__:
    from .validation import onboarding as onboarding_validation
    from .validation import planning as planning_validation
    from .validation import routing as routing_validation
    from .validation.registry import registry_summary, validate_registry
    from .validation.skill_packages import (
        validate_canonical_architecture_references,
        validate_skill_packages,
    )
    from .validation.shared import (
        Finding,
        HEADING_RE,
        is_string_list,
        load_mapping,
        read_text,
        relative,
        validate_fixture_contract_values,
    )
else:
    from validation import onboarding as onboarding_validation
    from validation import planning as planning_validation
    from validation import routing as routing_validation
    from validation.registry import registry_summary, validate_registry
    from validation.skill_packages import (
        validate_canonical_architecture_references,
        validate_skill_packages,
    )
    from validation.shared import (
        Finding,
        HEADING_RE,
        is_string_list,
        load_mapping,
        read_text,
        relative,
        validate_fixture_contract_values,
    )


REQUIRED_BEHAVIOR_PROOF_FIXTURE_CONTRACTS = {
    "root-cause-bug-fix": {
        "continues_to": "tdd",
        "diagnosis_evidence_reused": True,
        "fresh_authorization_required": False,
        "regression_proof_required": True,
    },
    "pure-unit-proof": {
        "selected_surface": "unit",
        "stable_observable_boundary": "pure-function",
        "broader_surface_preferred": False,
    },
    "property-proof": {
        "selected_surface": "property",
        "stable_observable_boundary": "invariant",
        "broader_surface_preferred": False,
    },
    "component-proof": {
        "selected_surface": "component",
        "stable_observable_boundary": "rendered-component",
        "broader_surface_preferred": False,
    },
    "contract-proof": {
        "selected_surface": "contract",
        "stable_observable_boundary": "provider-consumer-contract",
        "broader_surface_preferred": False,
    },
    "integration-proof": {
        "selected_surface": "integration",
        "stable_observable_boundary": "owned-subsystem-interaction",
        "broader_surface_preferred": False,
    },
    "end-to-end-proof": {
        "selected_surface": "end-to-end",
        "stable_observable_boundary": "user-workflow",
        "broader_surface_preferred": False,
    },
    "justified-non-tdd": {
        "tdd_suitable": False,
        "equivalent_proof_allowed": True,
        "reason_recorded": True,
    },
    "refactor-after-green": {
        "inside_tdd_cycle": True,
        "full_refinement_activated": False,
    },
    "refinement-debt": {
        "concrete_debt_observed": True,
        "activate_full_refinement": True,
    },
    "no-refinement-debt": {
        "explicit_request": False,
        "concrete_debt_observed": False,
        "activate_full_refinement": False,
        "skip_report_required": False,
    },
    "generated-code-cleanup": {
        "substantially_generated": True,
        "cleanup_debt_observed": True,
        "activate_full_refinement": True,
    },
    "independent-delegation": {
        "concrete_task_board": True,
        "non_overlapping_write_scopes": True,
        "shared_interfaces_settled": True,
        "parallel_delegation_allowed": True,
    },
    "overlapping-delegation": {
        "concrete_task_board": True,
        "non_overlapping_write_scopes": False,
        "parallel_delegation_allowed": False,
        "execution": "sequential",
    },
}
MERGE_CONFLICT_SHARED_CONTRACT = {
    "active_operation_detected": True,
    "exact_conflict_scope_identified": True,
    "skill_grants_lifecycle_authority": False,
    "protected_branch_mutation_allowed": False,
    "standalone_behavior_supported": True,
    "integrated_behavior_supported": True,
}
REQUIRED_MERGE_CONFLICT_FIXTURE_CONTRACTS = {
    "compatible-intent": {
        **MERGE_CONFLICT_SHARED_CONTRACT,
        "intent_tracing_attempted": True,
        "both_intents_established": True,
        "current_authoritative_evidence_required": True,
        "resolution_allowed": True,
        "preserves_both_intents": True,
        "invents_unrelated_behavior": False,
        "scoped_checks_discovered": True,
        "scoped_checks_run": True,
        "scoped_checks_passed": True,
    },
    "incompatible-intent": {
        **MERGE_CONFLICT_SHARED_CONTRACT,
        "intent_tracing_attempted": True,
        "both_intents_established": True,
        "current_authoritative_evidence_required": True,
        "resolution_allowed": False,
        "semantic_tradeoff_explicit": True,
        "user_decision_required": True,
    },
    "insufficient-evidence": {
        **MERGE_CONFLICT_SHARED_CONTRACT,
        "intent_tracing_attempted": True,
        "both_intents_established": False,
        "evidence_gap_reported": True,
        "resolution_allowed": False,
        "stop_for_evidence": True,
        "safe_abort_allowed": True,
        "finish_authorization_substitutes_for_evidence": False,
        "resolution_checks_required": False,
    },
    "wrong-operation": {
        **MERGE_CONFLICT_SHARED_CONTRACT,
        "described_operation": "merge",
        "actual_operation": "rebase",
        "operation_matches_request": False,
        "protected_branch_detected": True,
        "unexpected_source_commit_detected": True,
        "unrelated_staged_changes_reported": True,
        "stopped_before_edit": True,
        "intent_tracing_required_before_stop": False,
        "scoped_checks_required_before_stop": False,
        "resolution_allowed": False,
        "safe_abort_allowed": True,
        "abort_authorized_by_skill": False,
    },
    "authorized-continuation": {
        **MERGE_CONFLICT_SHARED_CONTRACT,
        "intent_tracing_attempted": True,
        "both_intents_established": True,
        "current_authoritative_evidence_required": True,
        "resolution_allowed": True,
        "fresh_authorization_verified": True,
        "authorized_actions": ["stage", "continue"],
        "authorized_paths": ["src/request_handler.py"],
        "continuation_limit": 1,
        "scoped_checks_discovered": True,
        "scoped_checks_run": True,
        "scoped_checks_passed": True,
        "checks_before_lifecycle_actions": True,
        "state_reinspected_after_continue": True,
        "new_conflict_detected": True,
        "stale_evidence_reused": False,
        "next_conflict_authorized": False,
        "commit_allowed": False,
        "push_allowed": False,
    },
}
REVIEW_VERIFICATION_SHARED_CONTRACT = {
    "fresh_evidence_required": True,
    "claim_scope_limited_to_evidence": True,
    "reuse_envelope_evidence": True,
    "duplicate_full_closeout": False,
    "specialist_output": "findings-or-route-delta",
}
REQUIRED_REVIEW_VERIFICATION_FIXTURE_CONTRACTS = {
    "tiny-diff-verification": {
        **REVIEW_VERIFICATION_SHARED_CONTRACT,
        "verification_route": "direct-proof",
        "full_verification_activated": False,
    },
    "spec-sensitive-review": {
        **REVIEW_VERIFICATION_SHARED_CONTRACT,
        "standards_spec_review_activated": True,
        "review_axis": "spec",
        "activation_reason": "acceptance-ambiguity",
    },
    "standards-sensitive-review": {
        **REVIEW_VERIFICATION_SHARED_CONTRACT,
        "standards_spec_review_activated": True,
        "review_axis": "standards",
        "activation_reason": "convention-uncertainty",
    },
    "trust-boundary-security-review": {
        **REVIEW_VERIFICATION_SHARED_CONTRACT,
        "security_review_activated": True,
        "trust_boundary_changed": True,
        "sensitive_surface": "authorization",
    },
    "non-security-change": {
        **REVIEW_VERIFICATION_SHARED_CONTRACT,
        "security_review_activated": False,
        "trust_boundary_changed": False,
        "security_skip_report_required": False,
    },
    "delegated-combined-change-verification": {
        **REVIEW_VERIFICATION_SHARED_CONTRACT,
        "full_verification_activated": True,
        "activation_reasons": ["delegated", "multi-surface"],
        "main_agent_sanity_check_required": True,
    },
    "review-feedback-classification": {
        **REVIEW_VERIFICATION_SHARED_CONTRACT,
        "classifications": [
            "accepted",
            "rejected-with-technical-rationale",
            "unclear",
            "user-decision",
        ],
        "repetitive_response_template_required": False,
    },
}
REQUIRED_OUTPUT_COMMUNICATION_FIXTURE_CONTRACTS = {
    "no-doc-impact": {
        "documentation_impact": "none",
        "durable_doc_updates": [],
        "specialist_output": "compact-delta",
        "explicit_no_update_result": True,
        "duplicate_task_closeout": False,
        "empty_fields_omitted": True,
    },
    "docs-required": {
        "documentation_impact": "required",
        "sync_owns_targeted_drift": True,
        "documentation_writer_loaded": False,
        "documentation_cleanup_loaded": False,
        "artifact_specific_detail_preserved": True,
        "duplicate_task_closeout": False,
    },
    "message-only-commit": {
        "first_output": "commit-message-text",
        "message_text_only_by_default": True,
        "stages_files": False,
        "creates_commit": False,
        "pushes": False,
        "suggests_commands": False,
        "optional_context_only_when_material": True,
    },
    "prompt-first": {
        "first_output": "finished-prompt",
        "explanation_default": "omitted",
        "explanation_available_on_request": True,
        "empty_assumptions_omitted": True,
        "route_metadata_before_prompt": False,
    },
    "caveman-safety": {
        "verbosity": "compact",
        "safety_warning_preserved": True,
        "approval_requirement_preserved": True,
        "uncertainty_preserved": True,
        "skipped_checks_preserved": True,
        "implementation_depth_reduced": False,
    },
    "caveman-structured-artifact": {
        "verbosity": "compact",
        "required_artifact_schema_preserved": True,
        "artifact_detail_reduced": False,
        "code_and_exact_text_preserved": True,
        "optional_explanation_compressed": True,
    },
    "learning-confirm-each": {
        "approval_mode": "confirm-each-write",
        "candidate_review_required": True,
        "approval_requested_for_each_write": True,
        "writes_before_approval": False,
        "scope_or_reach_changed": False,
        "sensitive_content_excluded": True,
    },
    "learning-standing-consent": {
        "approval_mode": "standing-session-consent",
        "candidate_review_required": True,
        "existing_consent_covers_writes": True,
        "approval_requested_again": False,
        "scope_or_reach_changed": False,
        "writes_within_destination_scope": True,
        "sensitive_content_excluded": True,
    },
    "multi-skill-consolidated-closeout": {
        "specialist_outputs": "internal-deltas",
        "final_closeout_owner": "main-agent",
        "task_closeout_count": 1,
        "outcome_first": True,
        "important_changes_included": True,
        "fresh_proof_included": True,
        "material_risk_included": True,
        "empty_fields_omitted": True,
        "repeated_paths_or_checks_omitted": True,
    },
}
REQUIRED_KNOWLEDGE_RETRIEVAL_FIXTURE_IDENTIFIERS = {
    "authoritative-source",
    "conflicting-note",
    "missing-capability-fallback",
    "no-mutation",
    "ordinary-files-only",
    "stale-note",
}
SOURCE_GROUNDED_RESEARCH_SHARED_CONTRACT = {
    "question_framed": True,
    "decision_use_framed": True,
    "currency_requirement_framed": True,
    "question_specific_source_hierarchy": True,
    "primary_sources_preferred": True,
    "claim_scoped_evidence": True,
    "findings_separate_from_inference": True,
    "read_only_research": True,
    "copyright_boundary_preserved": True,
    "private_data_excluded": True,
    "credentials_excluded": True,
    "restricted_sources_respected": True,
    "standalone_supported": True,
}
REQUIRED_SOURCE_GROUNDED_RESEARCH_FIXTURE_CONTRACTS = {
    "stale-source": {
        **SOURCE_GROUNDED_RESEARCH_SHARED_CONTRACT,
        "stale_source_retained": True,
        "stale_source_qualified": True,
        "current_claim_allowed": False,
    },
    "conflicting-sources": {
        **SOURCE_GROUNDED_RESEARCH_SHARED_CONTRACT,
        "both_sources_retained": True,
        "disagreement_explicit": True,
        "false_consensus_created": False,
        "unresolved_uncertainty_explicit": True,
    },
    "no-primary-source": {
        **SOURCE_GROUNDED_RESEARCH_SHARED_CONTRACT,
        "primary_source_available": False,
        "bounded_primary_search_attempted": True,
        "secondary_source_labelled": True,
        "confidence_reduced": True,
        "missing_evidence_explicit": True,
    },
    "read-only-output": {
        **SOURCE_GROUNDED_RESEARCH_SHARED_CONTRACT,
        "output_mode": "inline",
        "durable_artifact_created": False,
        "local_knowledge_mutated": False,
        "evidence_delta_returned": True,
    },
    "durable-capture": {
        **SOURCE_GROUNDED_RESEARCH_SHARED_CONTRACT,
        "durable_capture_requested": True,
        "durable_capture_authorized": True,
        "capture_convention": "project-owned-or-external-docs",
        "concise_attributed_summary": True,
        "duplicate_truth_created": False,
        "documentation_mirror_created": False,
        "automatic_capture": False,
    },
    "no-delegation-fallback": {
        **SOURCE_GROUNDED_RESEARCH_SHARED_CONTRACT,
        "delegation_available": False,
        "background_agents_required": False,
        "single_agent_completed": True,
        "evidence_standard_preserved": True,
    },
}
REQUIRED_SETUP_SCRIBE_FIXTURE_CONTRACTS = {
    "live-capture": {
        "mode": "capture",
        "gate_selected": True,
        "reproducibility_impact": True,
        "observation_collection": "quiet",
        "recipe_action": "update",
        "evidence_states": ["verified", "source-backed"],
        "closeout": "compact",
    },
    "mixed-evidence-backfill": {
        "mode": "backfill",
        "exact_history_claimed": False,
        "evidence_states": ["verified", "source-backed", "unverified"],
        "recipe_path": "docs/setup/project-setup.md",
        "chronological_history": False,
    },
    "drift-audit": {
        "mode": "audit",
        "fresh_project_evidence": True,
        "finding_states": [
            "current",
            "stale",
            "missing",
            "moved",
            "unverifiable",
            "obsolete",
        ],
        "recipe_action": "repair",
    },
    "bash-native-helper-automation": {
        "mode": "automate",
        "preferred_automation": "bash",
        "windows_bash_prerequisite": "git-bash",
        "native_helper": "powershell",
        "native_helper_scope": "registry",
        "generated": True,
        "executed": False,
        "verified": False,
        "separate_execution_approval": True,
    },
    "secret-rejection": {
        "mode": "capture",
        "secret_value_recorded": False,
        "placeholder_used": True,
        "security_impact": True,
        "tracked_recipe_safe": True,
    },
    "source-of-truth-reuse": {
        "manifest_referenced": True,
        "dependency_versions_duplicated": False,
        "recipe_owns": [
            "prerequisites",
            "ordering",
            "manual-actions",
            "verification",
            "gaps",
        ],
    },
    "personal-setting-exclusion": {
        "scope": "project-first",
        "project_setting_required": True,
        "project_setting_captured": True,
        "personal_setting_project_dependency": False,
        "personal_setting_recorded": False,
    },
    "no-reproducibility-impact": {
        "gate_selected": False,
        "reproducibility_impact": False,
        "recipe_action": "none",
        "closeout": "compact",
        "skip_report_required": False,
    },
}
REQUIRED_WAYFINDING_FIXTURE_IDENTIFIERS = {
    "branching-selection-and-approval",
    "decision-mode-classification",
    "fog-frontier-blocker-update",
    "handoff-to-architecture",
    "handoff-to-spec",
    "lifecycle-transitions",
    "local-markdown-fallback",
    "no-execution-pressure",
    "session-sized-rejection",
    "settled-implementation-rejection",
}
WAYFINDER_STATES = {
    "active",
    "blocked",
    "on-hold",
    "destination-ready",
    "completed",
    "dropped",
}
WAYFINDER_DECISION_TYPES = {
    "grilling",
    "research",
    "prototype",
    "prerequisite",
}
WAYFINDER_DECISION_MODES = {"AFK", "HITL"}
WAYFINDER_DECISION_STATUSES = {"open", "blocked", "resolved", "dropped"}
WAYFINDER_DELIVERY_HEADINGS = {
    "## Acceptance Criteria",
    "## Expected Proof",
    "## Implementation Plan",
    "## Steps",
    "## What To Build",
}

def parse_args() -> argparse.Namespace:
    """Parse the repo path so the same script can validate temp fixtures."""

    parser = argparse.ArgumentParser(
        description="Validate GOATED AI Skills schema and source-repo guardrails."
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root to validate. Defaults to this script's repo.",
    )
    return parser.parse_args()


validate_route_fixtures = routing_validation.validate_route_fixtures
validate_end_to_end_fixtures = routing_validation.validate_end_to_end_fixtures
validate_diagnosis_minimization_fixture = (
    routing_validation.validate_diagnosis_minimization_fixture
)


# Compatibility re-exports keep existing callers stable while the focused
# module owns clarification and onboarding behavior.
validate_clarification_fixtures = (
    onboarding_validation.validate_clarification_fixtures
)
validate_onboarding_fixtures = onboarding_validation.validate_onboarding_fixtures


def markdown_section_first_line(text: str, heading: str) -> str | None:
    """Return the first non-empty line beneath one level-two heading."""

    match = re.search(
        rf"^{re.escape(heading)}\s*$\s*(.+?)\s*(?=^##\s|\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        return None
    return next(
        (line.strip() for line in match.group(1).splitlines() if line.strip()),
        None,
    )


# Compatibility re-exports keep existing callers stable while the focused
# module owns specification, ticket, architecture, and implementation planning.
validate_planning_fixtures = planning_validation.validate_planning_fixtures
validate_architecture_planning_fixtures = (
    planning_validation.validate_architecture_planning_fixtures
)


def validate_behavior_proof_fixtures(repo: Path) -> list[Finding]:
    """Validate diagnosis, proof, refinement, and delegation behavior."""

    fixture_root = repo / "stack" / "fixtures" / "behavior-proof"
    fixture_paths = sorted(fixture_root.glob("*.yaml"))
    if not fixture_paths:
        return [
            Finding(
                "stack/fixtures/behavior-proof",
                "no behavior-proof fixtures found",
            )
        ]

    errors: list[Finding] = []
    identifiers: set[str] = set()
    for fixture_path in fixture_paths:
        fixture_label = relative(fixture_path, repo)
        fixture, fixture_errors = load_mapping(fixture_path, fixture_label)
        errors.extend(fixture_errors)
        if fixture is None:
            continue

        if fixture.get("schema_version") != "1.0.0":
            errors.append(
                Finding(
                    fixture_label,
                    "unsupported behavior-proof fixture schema_version",
                )
            )

        identifier = fixture.get("identifier")
        if not isinstance(identifier, str):
            errors.append(
                Finding(
                    fixture_label,
                    "behavior-proof fixture identifier must be a string",
                )
            )
            continue
        if identifier in identifiers:
            errors.append(
                Finding(
                    fixture_label,
                    f"duplicate behavior-proof fixture identifier: {identifier}",
                )
            )
        identifiers.add(identifier)

        expected = fixture.get("expected")
        if not isinstance(expected, dict):
            errors.append(
                Finding(
                    fixture_label,
                    "behavior-proof fixture expected must be a mapping",
                )
            )
            continue
        if not is_string_list(fixture.get("prohibited_behaviors"), allow_empty=False):
            errors.append(
                Finding(
                    fixture_label,
                    "behavior-proof prohibited_behaviors must be a non-empty string list",
                )
            )

        contract = REQUIRED_BEHAVIOR_PROOF_FIXTURE_CONTRACTS.get(identifier)
        if contract is None:
            errors.append(
                Finding(
                    fixture_label,
                    f"unsupported behavior-proof fixture: {identifier}",
                )
            )
            continue
        errors.extend(
            validate_fixture_contract_values(
                expected,
                contract,
                fixture_label,
                f"{identifier} behavior",
            )
        )

    errors.extend(
        Finding(
            "stack/fixtures/behavior-proof",
            f"missing required behavior-proof fixture: {identifier}",
        )
        for identifier in sorted(
            set(REQUIRED_BEHAVIOR_PROOF_FIXTURE_CONTRACTS) - identifiers
        )
    )
    return errors


def validate_merge_conflict_fixtures(repo: Path) -> list[Finding]:
    """Validate intent preservation and Git lifecycle authorization behavior."""

    fixture_root = repo / "stack" / "fixtures" / "merge-conflicts"
    fixture_paths = sorted(fixture_root.glob("*.yaml"))
    if not fixture_paths:
        return [
            Finding(
                "stack/fixtures/merge-conflicts",
                "no merge-conflict fixtures found",
            )
        ]

    errors: list[Finding] = []
    identifiers: set[str] = set()
    for fixture_path in fixture_paths:
        fixture_label = relative(fixture_path, repo)
        fixture, fixture_errors = load_mapping(fixture_path, fixture_label)
        errors.extend(fixture_errors)
        if fixture is None:
            continue

        if fixture.get("schema_version") != "1.0.0":
            errors.append(
                Finding(
                    fixture_label,
                    "unsupported merge-conflict fixture schema_version",
                )
            )

        identifier = fixture.get("identifier")
        if not isinstance(identifier, str):
            errors.append(
                Finding(
                    fixture_label,
                    "merge-conflict fixture identifier must be a string",
                )
            )
            continue
        if identifier in identifiers:
            errors.append(
                Finding(
                    fixture_label,
                    f"duplicate merge-conflict fixture identifier: {identifier}",
                )
            )
        identifiers.add(identifier)

        expected = fixture.get("expected")
        if not isinstance(expected, dict):
            errors.append(
                Finding(
                    fixture_label,
                    "merge-conflict fixture expected must be a mapping",
                )
            )
            continue
        if not is_string_list(fixture.get("prohibited_behaviors"), allow_empty=False):
            errors.append(
                Finding(
                    fixture_label,
                    "merge-conflict prohibited_behaviors must be a "
                    "non-empty string list",
                )
            )

        contract = REQUIRED_MERGE_CONFLICT_FIXTURE_CONTRACTS.get(identifier)
        if contract is None:
            errors.append(
                Finding(
                    fixture_label,
                    f"unsupported merge-conflict fixture: {identifier}",
                )
            )
            continue
        errors.extend(
            validate_fixture_contract_values(
                expected,
                contract,
                fixture_label,
                f"{identifier} behavior",
            )
        )

    errors.extend(
        Finding(
            "stack/fixtures/merge-conflicts",
            f"missing required merge-conflict fixture: {identifier}",
        )
        for identifier in sorted(
            set(REQUIRED_MERGE_CONFLICT_FIXTURE_CONTRACTS) - identifiers
        )
    )
    return errors


def validate_review_verification_fixtures(repo: Path) -> list[Finding]:
    """Validate conditional review and evidence-backed closeout behavior."""

    fixture_root = repo / "stack" / "fixtures" / "review-verification"
    fixture_paths = sorted(fixture_root.glob("*.yaml"))
    if not fixture_paths:
        return [
            Finding(
                "stack/fixtures/review-verification",
                "no review-verification fixtures found",
            )
        ]

    errors: list[Finding] = []
    identifiers: set[str] = set()
    for fixture_path in fixture_paths:
        fixture_label = relative(fixture_path, repo)
        fixture, fixture_errors = load_mapping(fixture_path, fixture_label)
        errors.extend(fixture_errors)
        if fixture is None:
            continue

        if fixture.get("schema_version") != "1.0.0":
            errors.append(
                Finding(
                    fixture_label,
                    "unsupported review-verification fixture schema_version",
                )
            )

        identifier = fixture.get("identifier")
        if not isinstance(identifier, str):
            errors.append(
                Finding(
                    fixture_label,
                    "review-verification fixture identifier must be a string",
                )
            )
            continue
        if identifier in identifiers:
            errors.append(
                Finding(
                    fixture_label,
                    f"duplicate review-verification fixture identifier: {identifier}",
                )
            )
        identifiers.add(identifier)

        expected = fixture.get("expected")
        if not isinstance(expected, dict):
            errors.append(
                Finding(
                    fixture_label,
                    "review-verification fixture expected must be a mapping",
                )
            )
            continue
        if not is_string_list(fixture.get("prohibited_behaviors"), allow_empty=False):
            errors.append(
                Finding(
                    fixture_label,
                    "review-verification prohibited_behaviors must be a "
                    "non-empty string list",
                )
            )

        contract = REQUIRED_REVIEW_VERIFICATION_FIXTURE_CONTRACTS.get(identifier)
        if contract is None:
            errors.append(
                Finding(
                    fixture_label,
                    f"unsupported review-verification fixture: {identifier}",
                )
            )
            continue
        errors.extend(
            validate_fixture_contract_values(
                expected,
                contract,
                fixture_label,
                f"{identifier} behavior",
            )
        )

    errors.extend(
        Finding(
            "stack/fixtures/review-verification",
            f"missing required review-verification fixture: {identifier}",
        )
        for identifier in sorted(
            set(REQUIRED_REVIEW_VERIFICATION_FIXTURE_CONTRACTS) - identifiers
        )
    )
    return errors


def validate_output_communication_fixtures(repo: Path) -> list[Finding]:
    """Validate concise artifact output and consolidated closeout behavior."""

    fixture_root = repo / "stack" / "fixtures" / "output-communication"
    fixture_paths = sorted(fixture_root.glob("*.yaml"))
    if not fixture_paths:
        return [
            Finding(
                "stack/fixtures/output-communication",
                "no output-communication fixtures found",
            )
        ]

    errors: list[Finding] = []
    identifiers: set[str] = set()
    for fixture_path in fixture_paths:
        fixture_label = relative(fixture_path, repo)
        fixture, fixture_errors = load_mapping(fixture_path, fixture_label)
        errors.extend(fixture_errors)
        if fixture is None:
            continue

        if fixture.get("schema_version") != "1.0.0":
            errors.append(
                Finding(
                    fixture_label,
                    "unsupported output-communication fixture schema_version",
                )
            )

        identifier = fixture.get("identifier")
        if not isinstance(identifier, str):
            errors.append(
                Finding(
                    fixture_label,
                    "output-communication fixture identifier must be a string",
                )
            )
            continue
        if identifier in identifiers:
            errors.append(
                Finding(
                    fixture_label,
                    f"duplicate output-communication fixture identifier: {identifier}",
                )
            )
        identifiers.add(identifier)

        expected = fixture.get("expected")
        if not isinstance(expected, dict):
            errors.append(
                Finding(
                    fixture_label,
                    "output-communication fixture expected must be a mapping",
                )
            )
            continue
        if not is_string_list(fixture.get("prohibited_behaviors"), allow_empty=False):
            errors.append(
                Finding(
                    fixture_label,
                    "output-communication prohibited_behaviors must be a "
                    "non-empty string list",
                )
            )

        contract = REQUIRED_OUTPUT_COMMUNICATION_FIXTURE_CONTRACTS.get(identifier)
        if contract is None:
            errors.append(
                Finding(
                    fixture_label,
                    f"unsupported output-communication fixture: {identifier}",
                )
            )
            continue
        errors.extend(
            validate_fixture_contract_values(
                expected,
                contract,
                fixture_label,
                f"{identifier} behavior",
            )
        )

    errors.extend(
        Finding(
            "stack/fixtures/output-communication",
            f"missing required output-communication fixture: {identifier}",
        )
        for identifier in sorted(
            set(REQUIRED_OUTPUT_COMMUNICATION_FIXTURE_CONTRACTS) - identifiers
        )
    )
    return errors


def validate_knowledge_retrieval_fixtures(repo: Path) -> list[Finding]:
    """Validate the portable knowledge-retrieval behavior fixtures."""

    fixture_root = repo / "stack" / "fixtures" / "knowledge-retrieval"
    fixture_paths = sorted(fixture_root.glob("*.yaml"))
    if not fixture_paths:
        return [
            Finding(
                "stack/fixtures/knowledge-retrieval",
                "no knowledge-retrieval fixtures found",
            )
        ]

    errors: list[Finding] = []
    identifiers: set[str] = set()
    for fixture_path in fixture_paths:
        fixture_label = relative(fixture_path, repo)
        fixture, fixture_errors = load_mapping(fixture_path, fixture_label)
        errors.extend(fixture_errors)
        if fixture is None:
            continue

        if fixture.get("schema_version") != "1.0.0":
            errors.append(
                Finding(
                    fixture_label,
                    "unsupported knowledge-retrieval fixture schema_version",
                )
            )

        identifier = fixture.get("identifier")
        if not isinstance(identifier, str):
            errors.append(
                Finding(
                    fixture_label,
                    "knowledge-retrieval fixture identifier must be a string",
                )
            )
            continue
        if identifier in identifiers:
            errors.append(
                Finding(
                    fixture_label,
                    f"duplicate knowledge-retrieval fixture identifier: {identifier}",
                )
            )
        identifiers.add(identifier)

        if not isinstance(fixture.get("expected"), dict):
            errors.append(
                Finding(
                    fixture_label,
                    "knowledge-retrieval fixture expected must be a mapping",
                )
            )
        if not is_string_list(
            fixture.get("prohibited_behaviors"),
            allow_empty=False,
        ):
            errors.append(
                Finding(
                    fixture_label,
                    "knowledge-retrieval prohibited_behaviors must be "
                    "a non-empty string list",
                )
            )

        expected = fixture.get("expected")
        evidence_bundle = (
            expected.get("evidence_bundle")
            if isinstance(expected, dict)
            else None
        )
        if evidence_bundle is not None:
            required_evidence_fields = {
                "identifier",
                "relevance",
                "applicable_scope",
                "finding",
                "provenance",
                "freshness",
                "confidence",
                "uncertainty",
            }
            if (
                not isinstance(evidence_bundle, list)
                or not evidence_bundle
                or any(
                    not isinstance(entry, dict)
                    or not required_evidence_fields.issubset(entry)
                    for entry in evidence_bundle
                )
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "retrieved evidence entries require identifier, "
                        "relevance, applicable_scope, finding, provenance, "
                        "freshness, confidence, and uncertainty",
                    )
                )
            elif any(
                not isinstance(entry.get("freshness"), str)
                or entry["freshness"].strip().casefold()
                in {"current", "stale", "unknown"}
                for entry in evidence_bundle
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "retrieved evidence freshness requires a commit, "
                        "date, or equivalent traceable marker",
                    )
                )
        if identifier == "authoritative-source" and isinstance(expected, dict):
            search = expected.get("search")
            if (
                not isinstance(search, dict)
                or search.get("progressive") is not True
                or search.get("read_only") is not True
                or search.get("external_web") is not False
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval search must be progressive, "
                        "read-only, and exclude external web research",
                    )
                )
            ranking_factors = expected.get("ranking_factors")
            required_ranking_factors = {
                "authority",
                "relevance",
                "confidence",
                "maturity",
                "freshness",
            }
            if (
                not isinstance(ranking_factors, dict)
                or any(
                    ranking_factors.get(factor) is not True
                    for factor in required_ranking_factors
                )
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval ranking requires authority, "
                        "relevance, confidence, maturity, and freshness",
                    )
                )
            required_classifications = {
                "authoritative",
                "history",
                "observation",
                "inference",
                "brainstorming",
                "stale",
            }
            classifications = expected.get("classifications_supported")
            if (
                not is_string_list(classifications, allow_empty=False)
                or not required_classifications.issubset(classifications)
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval must distinguish authoritative, "
                        "history, observation, inference, brainstorming, and "
                        "stale material",
                    )
                )
            ranked_results = expected.get("ranked_results")
            first_result = (
                ranked_results[0]
                if isinstance(ranked_results, list) and ranked_results
                else None
            )
            if (
                not isinstance(first_result, dict)
                or first_result.get("classification") != "authoritative"
                or first_result.get("freshness") != "current"
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval must rank current authoritative "
                        "evidence first",
                    )
                )
        if identifier == "conflicting-note" and isinstance(expected, dict):
            conflict = expected.get("conflict")
            if (
                not isinstance(conflict, dict)
                or conflict.get("reported") is not True
                or conflict.get("silently_merged") is not False
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval must report conflicts without "
                        "silently merging",
                    )
                )
            conflict_evidence = expected.get("evidence_bundle")
            current_authority = (
                conflict.get("current_authority")
                if isinstance(conflict, dict)
                else None
            )
            current_entries = (
                [
                    entry
                    for entry in conflict_evidence
                    if isinstance(entry, dict)
                    and entry.get("identifier") == current_authority
                    and entry.get("validity") == "current"
                ]
                if isinstance(conflict_evidence, list)
                else []
            )
            invalidated_entries = (
                [
                    entry
                    for entry in conflict_evidence
                    if isinstance(entry, dict)
                    and entry.get("validity") == "invalidated"
                    and entry.get("invalidated_by") == current_authority
                ]
                if isinstance(conflict_evidence, list)
                else []
            )
            if (
                not isinstance(conflict_evidence, list)
                or len(conflict_evidence) != 2
                or len(current_entries) != 1
                or len(invalidated_entries) != 1
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "resolved conflicts must preserve both evidence "
                        "entries and link the invalidated entry to current "
                        "authority",
                    )
                )
            nurture = expected.get("nurture")
            if (
                not isinstance(nurture, dict)
                or nurture.get("route_to") != "learning-capture"
                or nurture.get("performed") is not False
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval may recommend learning-capture "
                        "but cannot perform nurturing",
                    )
                )
        if identifier == "stale-note" and isinstance(expected, dict):
            if (
                expected.get("report_staleness") is not True
                or expected.get("silently_discard") is not False
                or expected.get("silently_merge") is not False
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "stale knowledge must be reported without silent "
                        "merge or discard",
                    )
                )
        if identifier == "ordinary-files-only" and isinstance(expected, dict):
            selected_path = expected.get("selected_path")
            selected_source_exists = (
                isinstance(selected_path, str)
                and (fixture_root / selected_path).is_file()
            )
            if (
                not selected_source_exists
                or expected.get("ordinary_files_sufficient") is not True
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "ordinary-file retrieval requires a real selected_path "
                        "and ordinary_files_sufficient=True",
                    )
                )
        if identifier == "missing-capability-fallback" and isinstance(
            expected,
            dict,
        ):
            fallback = expected.get("fallback")
            if (
                not isinstance(fallback, dict)
                or fallback.get("ordinary_files") is not True
                or expected.get("blocked") is not False
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "missing capabilities must fall back to ordinary "
                        "local files",
                    )
                )
            if expected.get("external_web") is not False:
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval fixtures must keep external web "
                        "research out of scope",
                    )
                )
        if identifier == "no-mutation" and isinstance(expected, dict):
            mutation_fields = {
                "filesystem_mutated",
                "index_created",
                "cache_created",
                "note_updated",
            }
            if any(
                expected.get(field) is not False
                for field in mutation_fields
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval must not mutate files, notes, "
                        "indexes, or caches",
                    )
                )

    errors.extend(
        Finding(
            "stack/fixtures/knowledge-retrieval",
            f"missing required knowledge-retrieval fixture: {identifier}",
        )
        for identifier in sorted(
            REQUIRED_KNOWLEDGE_RETRIEVAL_FIXTURE_IDENTIFIERS - identifiers
        )
    )
    return errors


def validate_source_grounded_research_fixtures(repo: Path) -> list[Finding]:
    """Validate the portable external-research behavior fixtures."""

    fixture_root = repo / "stack" / "fixtures" / "source-grounded-research"
    fixture_paths = sorted(fixture_root.glob("*.yaml"))
    if not fixture_paths:
        return [
            Finding(
                "stack/fixtures/source-grounded-research",
                "no source-grounded-research fixtures found",
            )
        ]

    errors: list[Finding] = []
    identifiers: set[str] = set()
    required_evidence_fields = {
        "identifier",
        "relevance",
        "applicable_scope",
        "finding",
        "provenance",
        "freshness",
        "confidence",
        "uncertainty",
    }

    for fixture_path in fixture_paths:
        fixture_label = relative(fixture_path, repo)
        fixture, fixture_errors = load_mapping(fixture_path, fixture_label)
        errors.extend(fixture_errors)
        if fixture is None:
            continue

        if fixture.get("schema_version") != "1.0.0":
            errors.append(
                Finding(
                    fixture_label,
                    "unsupported source-grounded-research fixture schema_version",
                )
            )

        identifier = fixture.get("identifier")
        if not isinstance(identifier, str):
            errors.append(
                Finding(
                    fixture_label,
                    "source-grounded-research fixture identifier must be a string",
                )
            )
            continue
        if identifier in identifiers:
            errors.append(
                Finding(
                    fixture_label,
                    f"duplicate source-grounded-research fixture identifier: "
                    f"{identifier}",
                )
            )
        identifiers.add(identifier)

        expected = fixture.get("expected")
        if not isinstance(expected, dict):
            errors.append(
                Finding(
                    fixture_label,
                    "source-grounded-research fixture expected must be a mapping",
                )
            )
            continue
        if not is_string_list(fixture.get("prohibited_behaviors"), allow_empty=False):
            errors.append(
                Finding(
                    fixture_label,
                    "source-grounded-research prohibited_behaviors must be a "
                    "non-empty string list",
                )
            )

        contract = REQUIRED_SOURCE_GROUNDED_RESEARCH_FIXTURE_CONTRACTS.get(
            identifier
        )
        if contract is None:
            errors.append(
                Finding(
                    fixture_label,
                    f"unsupported source-grounded-research fixture: {identifier}",
                )
            )
            continue
        errors.extend(
            validate_fixture_contract_values(
                expected,
                contract,
                fixture_label,
                f"{identifier} behavior",
            )
        )

        evidence_delta = expected.get("evidence_delta")
        if (
            not isinstance(evidence_delta, list)
            or not evidence_delta
            or any(
                not isinstance(entry, dict)
                or not required_evidence_fields.issubset(entry)
                for entry in evidence_delta
            )
        ):
            errors.append(
                Finding(
                    fixture_label,
                    "research evidence entries require identifier, relevance, "
                    "applicable_scope, finding, provenance, freshness, "
                    "confidence, and uncertainty",
                )
            )
        if isinstance(evidence_delta, list) and any(
            isinstance(entry, dict)
            and (
                not isinstance(entry.get("freshness"), str)
                or entry["freshness"].strip().casefold()
                in {"current", "stale", "unknown"}
            )
            for entry in evidence_delta
        ):
            errors.append(
                Finding(
                    fixture_label,
                    "research evidence freshness requires a publication, "
                    "version, retrieval date, or equivalent traceable marker",
                )
            )

    errors.extend(
        Finding(
            "stack/fixtures/source-grounded-research",
            f"missing required source-grounded-research fixture: {identifier}",
        )
        for identifier in sorted(
            set(REQUIRED_SOURCE_GROUNDED_RESEARCH_FIXTURE_CONTRACTS)
            - identifiers
        )
    )
    return errors


def validate_setup_scribe_fixtures(repo: Path) -> list[Finding]:
    """Validate project-first setup reproducibility behavior."""

    fixture_root = repo / "stack" / "fixtures" / "setup-scribe"
    fixture_paths = sorted(fixture_root.glob("*.yaml"))
    if not fixture_paths:
        return [
            Finding(
                "stack/fixtures/setup-scribe",
                "no setup-scribe fixtures found",
            )
        ]

    errors: list[Finding] = []
    identifiers: set[str] = set()
    for fixture_path in fixture_paths:
        fixture_label = relative(fixture_path, repo)
        fixture, fixture_errors = load_mapping(fixture_path, fixture_label)
        errors.extend(fixture_errors)
        if fixture is None:
            continue

        if fixture.get("schema_version") != "1.0.0":
            errors.append(
                Finding(
                    fixture_label,
                    "unsupported setup-scribe fixture schema_version",
                )
            )

        identifier = fixture.get("identifier")
        if not isinstance(identifier, str):
            errors.append(
                Finding(
                    fixture_label,
                    "setup-scribe fixture identifier must be a string",
                )
            )
            continue
        if identifier in identifiers:
            errors.append(
                Finding(
                    fixture_label,
                    f"duplicate setup-scribe fixture identifier: {identifier}",
                )
            )
        identifiers.add(identifier)

        expected = fixture.get("expected")
        if not isinstance(expected, dict):
            errors.append(
                Finding(
                    fixture_label,
                    "setup-scribe fixture expected must be a mapping",
                )
            )
            continue
        if not is_string_list(
            fixture.get("prohibited_behaviors"),
            allow_empty=False,
        ):
            errors.append(
                Finding(
                    fixture_label,
                    "setup-scribe prohibited_behaviors must be a "
                    "non-empty string list",
                )
            )

        contract = REQUIRED_SETUP_SCRIBE_FIXTURE_CONTRACTS.get(identifier)
        if contract is None:
            errors.append(
                Finding(
                    fixture_label,
                    f"unsupported setup-scribe fixture: {identifier}",
                )
            )
            continue
        errors.extend(
            validate_fixture_contract_values(
                expected,
                contract,
                fixture_label,
                f"{identifier} behavior",
            )
        )

    errors.extend(
        Finding(
            "stack/fixtures/setup-scribe",
            f"missing required setup-scribe fixture: {identifier}",
        )
        for identifier in sorted(
            set(REQUIRED_SETUP_SCRIBE_FIXTURE_CONTRACTS) - identifiers
        )
    )
    return errors


def validate_wayfinding_fixtures(repo: Path) -> list[Finding]:
    """Validate Wayfinder selection and chart-approval behavior."""

    fixture_root = repo / "stack" / "fixtures" / "wayfinding"
    fixture_paths = sorted(fixture_root.glob("*.yaml"))
    if not fixture_paths:
        return [Finding("stack/fixtures/wayfinding", "no wayfinding fixtures found")]

    errors: list[Finding] = []
    identifiers: set[str] = set()
    for fixture_path in fixture_paths:
        fixture_label = relative(fixture_path, repo)
        fixture, fixture_errors = load_mapping(fixture_path, fixture_label)
        errors.extend(fixture_errors)
        if fixture is None:
            continue

        if fixture.get("schema_version") != "1.0.0":
            errors.append(
                Finding(
                    fixture_label,
                    "unsupported wayfinding fixture schema_version",
                )
            )

        identifier = fixture.get("identifier")
        if not isinstance(identifier, str):
            errors.append(
                Finding(fixture_label, "wayfinding fixture identifier must be a string")
            )
            continue
        if identifier in identifiers:
            errors.append(
                Finding(
                    fixture_label,
                    f"duplicate wayfinding fixture identifier: {identifier}",
                )
            )
        identifiers.add(identifier)

        expected = fixture.get("expected")
        if not isinstance(expected, dict):
            errors.append(
                Finding(fixture_label, "wayfinding fixture expected must be a mapping")
            )
            continue
        if not is_string_list(
            fixture.get("prohibited_behaviors"),
            allow_empty=False,
        ):
            errors.append(
                Finding(
                    fixture_label,
                    "wayfinding prohibited_behaviors must be a non-empty string list",
                )
            )

        if identifier == "branching-selection-and-approval":
            selection_contract = {
                "selected": True,
                "branching_uncertainty": True,
                "exceeds_one_focused_session": True,
                "already_specified_implementation": False,
            }
            selection = expected.get("selection")
            if not isinstance(selection, dict):
                errors.append(
                    Finding(
                        fixture_label,
                        "Wayfinder selection must be a mapping",
                    )
                )
            else:
                errors.extend(
                    validate_fixture_contract_values(
                        selection,
                        selection_contract,
                        fixture_label,
                        "Wayfinder selection",
                    )
                )

            approval = expected.get("chart_approval")
            if not isinstance(approval, dict):
                errors.append(
                    Finding(
                        fixture_label,
                        "Wayfinder chart_approval must be a mapping",
                    )
                )
            else:
                approval_contract = {
                    "destination": True,
                    "location": True,
                    "visible_frontier": True,
                    "action_reach": True,
                    "initial_write_scope": True,
                    "approved_before_write": True,
                }
                errors.extend(
                    validate_fixture_contract_values(
                        approval,
                        approval_contract,
                        fixture_label,
                        "Wayfinder chart approval",
                    )
                )
        elif identifier in {
            "session-sized-rejection",
            "settled-implementation-rejection",
        }:
            rejection = expected.get("rejection")
            if not isinstance(rejection, dict):
                errors.append(
                    Finding(fixture_label, "Wayfinder rejection must be a mapping")
                )
            else:
                expected_reason = (
                    "session-sized"
                    if identifier == "session-sized-rejection"
                    else "already-specified-implementation"
                )
                expected_route = (
                    "grill-me"
                    if identifier == "session-sized-rejection"
                    else "writing-plans"
                )
                rejection_contract = {
                    "selected": False,
                    "reason": expected_reason,
                    "route_to": expected_route,
                    "map_created": False,
                    "restarts_discovery": False,
                }
                errors.extend(
                    validate_fixture_contract_values(
                        rejection,
                        rejection_contract,
                        fixture_label,
                        "Wayfinder rejection",
                    )
                )
        elif identifier == "local-markdown-fallback":
            artifact_contract = {
                "location": "docs/wayfinding/storage-strategy/map.md",
                "decision_pattern": (
                    "docs/wayfinding/storage-strategy/decisions/"
                    "NNN-<decision-title>.md"
                ),
                "decision_ticket_is_delivery_ticket": False,
            }
            errors.extend(
                validate_fixture_contract_values(
                    expected,
                    artifact_contract,
                    fixture_label,
                    "Wayfinder local artifact",
                )
            )
            for sample_field, headings_field in (
                ("map_sample", "map_headings"),
                ("decision_sample", "decision_headings"),
                ("frontier_decision_sample", "decision_headings"),
            ):
                sample_value = expected.get(sample_field)
                headings = expected.get(headings_field)
                if not isinstance(sample_value, str):
                    errors.append(
                        Finding(
                            fixture_label,
                            f"Wayfinder local artifact requires {sample_field}",
                        )
                    )
                    continue
                if not is_string_list(headings, allow_empty=False):
                    errors.append(
                        Finding(
                            fixture_label,
                            f"Wayfinder local artifact requires {headings_field}",
                        )
                    )
                    continue
                sample_path = fixture_root / sample_value
                if not sample_path.exists():
                    errors.append(
                        Finding(
                            fixture_label,
                            f"Wayfinder sample does not exist: {sample_value}",
                        )
                    )
                    continue
                sample_text = read_text(sample_path)
                for heading in headings:
                    if heading not in sample_text:
                        errors.append(
                            Finding(
                                fixture_label,
                                f"Wayfinder sample {sample_value} is missing "
                                f"heading: {heading}",
                            )
                        )
                if headings_field == "decision_headings":
                    section_values = {
                        heading: markdown_section_first_line(sample_text, heading)
                        for heading in headings
                    }
                    if section_values["## Type"] not in WAYFINDER_DECISION_TYPES:
                        errors.append(
                            Finding(
                                fixture_label,
                                f"Wayfinder sample {sample_value} has unsupported "
                                "decision type",
                            )
                        )
                    if section_values["## Mode"] not in WAYFINDER_DECISION_MODES:
                        errors.append(
                            Finding(
                                fixture_label,
                                f"Wayfinder sample {sample_value} has unsupported "
                                "decision mode",
                            )
                        )
                    if (
                        section_values["## Status"]
                        not in WAYFINDER_DECISION_STATUSES
                    ):
                        errors.append(
                            Finding(
                                fixture_label,
                                f"Wayfinder sample {sample_value} has unsupported "
                                "decision status",
                            )
                        )
                    for required_heading in (
                        "## Blockers",
                        "## Question",
                        "## Evidence Or Asset Links",
                        "## Resolution",
                    ):
                        if not section_values[required_heading]:
                            errors.append(
                                Finding(
                                    fixture_label,
                                    f"Wayfinder sample {sample_value} requires "
                                    f"content under {required_heading}",
                                )
                            )
                    delivery_headings = sorted(
                        WAYFINDER_DELIVERY_HEADINGS.intersection(
                            {
                                f"## {heading}"
                                for heading in HEADING_RE.findall(sample_text)
                            }
                        )
                    )
                    if delivery_headings:
                        errors.append(
                            Finding(
                                fixture_label,
                                f"Wayfinder decision sample contains delivery "
                                f"heading: {delivery_headings[0]}",
                            )
                        )
            map_sample = expected.get("map_sample")
            frontier_sample = expected.get("frontier_decision_sample")
            if isinstance(map_sample, str) and isinstance(frontier_sample, str):
                map_path = Path(map_sample)
                frontier_path = Path(frontier_sample)
                try:
                    frontier_link = frontier_path.relative_to(
                        map_path.parent
                    ).as_posix()
                except ValueError:
                    errors.append(
                        Finding(
                            fixture_label,
                            "Wayfinder frontier decision sample must be local "
                            "to the map sample",
                        )
                    )
                else:
                    map_text = read_text(fixture_root / map_path)
                    if f"]({frontier_link})" not in map_text:
                        errors.append(
                            Finding(
                                fixture_label,
                                "Wayfinder map sample must link its frontier "
                                "decision sample",
                            )
                        )
        elif identifier == "fog-frontier-blocker-update":
            update = expected.get("update")
            if not isinstance(update, dict):
                errors.append(
                    Finding(fixture_label, "Wayfinder update must be a mapping")
                )
            else:
                update_contract = {
                    "primary_decision_focus_count": 1,
                    "frontier_contains_only_precise_questions": True,
                    "clarified_fog_graduates": True,
                    "graduated_fog_removed": True,
                    "blocker_links_updated": True,
                    "authoritative_detail_duplicated": False,
                    "evidence_links_reused": True,
                    "out_of_scope_unchanged": True,
                }
                errors.extend(
                    validate_fixture_contract_values(
                        update,
                        update_contract,
                        fixture_label,
                        "Wayfinder frontier update",
                    )
                )
        elif identifier == "decision-mode-classification":
            if expected.get("classification_independent") is not True:
                errors.append(
                    Finding(
                        fixture_label,
                        "Wayfinder type and mode classification must be independent",
                    )
                )
            decisions = expected.get("decisions")
            if not isinstance(decisions, list) or not decisions:
                errors.append(
                    Finding(
                        fixture_label,
                        "Wayfinder classification requires decision examples",
                    )
                )
            else:
                observed_types: set[str] = set()
                observed_modes: set[str] = set()
                for decision in decisions:
                    if not isinstance(decision, dict):
                        errors.append(
                            Finding(
                                fixture_label,
                                "Wayfinder decision example must be a mapping",
                            )
                        )
                        continue
                    decision_type = decision.get("type")
                    mode = decision.get("mode")
                    if decision_type not in WAYFINDER_DECISION_TYPES:
                        errors.append(
                            Finding(
                                fixture_label,
                                f"unsupported Wayfinder decision type: {decision_type}",
                            )
                        )
                    else:
                        observed_types.add(decision_type)
                    if mode not in WAYFINDER_DECISION_MODES:
                        errors.append(
                            Finding(
                                fixture_label,
                                f"unsupported Wayfinder decision mode: {mode}",
                            )
                        )
                    else:
                        observed_modes.add(mode)
                    if not isinstance(decision.get("reason"), str):
                        errors.append(
                            Finding(
                                fixture_label,
                                "Wayfinder decision classification requires a reason",
                            )
                        )
                    if decision_type == "prerequisite":
                        prerequisite_contract = {
                            "necessary_for_decision": True,
                            "approval_covers_reach": True,
                        }
                        errors.extend(
                            validate_fixture_contract_values(
                                decision,
                                prerequisite_contract,
                                fixture_label,
                                "Wayfinder prerequisite",
                            )
                        )
                if observed_types != WAYFINDER_DECISION_TYPES:
                    errors.append(
                        Finding(
                            fixture_label,
                            "Wayfinder classification must cover every decision type",
                        )
                    )
                if observed_modes != WAYFINDER_DECISION_MODES:
                    errors.append(
                        Finding(
                            fixture_label,
                            "Wayfinder classification must cover AFK and HITL",
                        )
                    )
        elif identifier == "lifecycle-transitions":
            states = expected.get("states")
            if not isinstance(states, list) or not states:
                errors.append(
                    Finding(fixture_label, "Wayfinder lifecycle states must be a list")
                )
            else:
                states_by_name = {
                    state.get("state"): state
                    for state in states
                    if isinstance(state, dict)
                }
                state_names = [
                    state.get("state")
                    for state in states
                    if isinstance(state, dict)
                ]
                if len(state_names) != len(set(state_names)):
                    errors.append(
                        Finding(
                            fixture_label,
                            "Wayfinder lifecycle states must not contain duplicates",
                        )
                    )
                if set(states_by_name) != WAYFINDER_STATES:
                    errors.append(
                        Finding(
                            fixture_label,
                            "Wayfinder lifecycle fixture must cover every state",
                        )
                    )
                active = states_by_name.get("active", {})
                if active.get("actionable_frontier") is not True:
                    errors.append(
                        Finding(
                            fixture_label,
                            "active Wayfinder state requires an actionable frontier",
                        )
                    )
                state_requirements = {
                    "blocked": ("reason", "resume_condition"),
                    "on-hold": ("reason", "review_condition"),
                    "dropped": ("reason",),
                }
                for state_name, required_fields in state_requirements.items():
                    state = states_by_name.get(state_name, {})
                    for field in required_fields:
                        if not isinstance(state.get(field), str):
                            errors.append(
                                Finding(
                                    fixture_label,
                                    f"{state_name} Wayfinder state requires {field}",
                                )
                            )
                destination_ready = states_by_name.get("destination-ready", {})
                if (
                    destination_ready.get("destination_exists") is not False
                    or destination_ready.get("destination_linked") is not False
                ):
                    errors.append(
                        Finding(
                            fixture_label,
                            "destination-ready must precede destination creation",
                        )
                    )
                completed = states_by_name.get("completed", {})
                completed_contract = {
                    "destination_exists": True,
                    "destination_linked": True,
                }
                errors.extend(
                    validate_fixture_contract_values(
                        completed,
                        completed_contract,
                        fixture_label,
                        "completed Wayfinder state",
                    )
                )
                destination_path = completed.get("destination_path")
                if (
                    not isinstance(destination_path, str)
                    or not (fixture_root / destination_path).exists()
                ):
                    errors.append(
                        Finding(
                            fixture_label,
                            "completed Wayfinder state requires an existing "
                            "destination_path",
                        )
                    )
            transitions = expected.get("transitions")
            if not isinstance(transitions, list) or not transitions:
                errors.append(
                    Finding(
                        fixture_label,
                        "Wayfinder lifecycle transitions must be a non-empty list",
                    )
                )
            else:
                transition_targets: set[str] = set()
                transition_pairs: set[tuple[str, str]] = set()
                for transition in transitions:
                    if not isinstance(transition, dict):
                        errors.append(
                            Finding(
                                fixture_label,
                                "Wayfinder lifecycle transition must be a mapping",
                            )
                        )
                        continue
                    from_state = transition.get("from")
                    to_state = transition.get("to")
                    if not isinstance(from_state, str) or not isinstance(
                        to_state,
                        str,
                    ):
                        errors.append(
                            Finding(
                                fixture_label,
                                "Wayfinder lifecycle transition requires from and to",
                            )
                        )
                        continue
                    transition_targets.add(to_state)
                    transition_pairs.add((from_state, to_state))
                    if not isinstance(transition.get("trigger"), str):
                        errors.append(
                            Finding(
                                fixture_label,
                                "Wayfinder lifecycle transition requires a trigger",
                            )
                        )
                    if not is_string_list(
                        transition.get("preserves"),
                        allow_empty=False,
                    ):
                        errors.append(
                            Finding(
                                fixture_label,
                                "Wayfinder lifecycle transition requires preserved "
                                "context",
                            )
                        )
                if transition_targets != WAYFINDER_STATES:
                    errors.append(
                        Finding(
                            fixture_label,
                            "Wayfinder lifecycle transitions must enter every state",
                        )
                    )
                required_pairs = {
                    ("blocked", "active"),
                    ("on-hold", "active"),
                    ("destination-ready", "completed"),
                }
                if not required_pairs.issubset(transition_pairs):
                    errors.append(
                        Finding(
                            fixture_label,
                            "Wayfinder lifecycle transitions must cover resume, "
                            "review, and destination completion",
                        )
                    )
            if expected.get("universal_transition_graph_defined") is not False:
                errors.append(
                    Finding(
                        fixture_label,
                        "Wayfinder fixtures must not invent a universal transition graph",
                    )
                )
        elif identifier == "no-execution-pressure":
            allowed = expected.get("allowed")
            prerequisite = expected.get("prerequisite")
            prohibited = expected.get("prohibited")
            if not isinstance(allowed, dict):
                errors.append(
                    Finding(fixture_label, "Wayfinder allowed evidence must be a mapping")
                )
            else:
                errors.extend(
                    validate_fixture_contract_values(
                        allowed,
                        {
                            "research": True,
                            "disposable_decision_prototype": True,
                            "bounded_prerequisite": True,
                        },
                        fixture_label,
                        "Wayfinder allowed evidence",
                    )
                )
            if not isinstance(prerequisite, dict):
                errors.append(
                    Finding(fixture_label, "Wayfinder prerequisite must be a mapping")
                )
            else:
                errors.extend(
                    validate_fixture_contract_values(
                        prerequisite,
                        {
                            "necessary_for_decision": True,
                            "bounded_to_decision": True,
                            "approval_covers_reach": True,
                        },
                        fixture_label,
                        "Wayfinder prerequisite",
                    )
                )
            if not isinstance(prohibited, dict):
                errors.append(
                    Finding(
                        fixture_label,
                        "Wayfinder prohibited execution must be a mapping",
                    )
                )
            else:
                errors.extend(
                    validate_fixture_contract_values(
                        prohibited,
                        {
                            "production_implementation": False,
                            "migration_execution": False,
                            "publishing": False,
                            "deployment": False,
                        },
                        fixture_label,
                        "Wayfinder no-execution boundary",
                    )
                )
            errors.extend(
                validate_fixture_contract_values(
                    expected,
                    {
                        "notes_override_boundary": False,
                        "route_to_destination_workflow": True,
                    },
                    fixture_label,
                    "Wayfinder pressure response",
                )
            )
        elif identifier in {"handoff-to-spec", "handoff-to-architecture"}:
            handoff = expected.get("handoff")
            if not isinstance(handoff, dict):
                errors.append(
                    Finding(fixture_label, "Wayfinder handoff must be a mapping")
                )
            else:
                expected_skill = (
                    "write-a-spec"
                    if identifier == "handoff-to-spec"
                    else "design-codebase-architecture"
                )
                handoff_contract = {
                    "destination_skill": expected_skill,
                    "reuses_settled_decisions": True,
                    "reuses_evidence_links": True,
                    "restarts_discovery": False,
                    "state_before_destination_exists": "destination-ready",
                    "state_after_destination_linked": "completed",
                    "executes_production_work": False,
                }
                errors.extend(
                    validate_fixture_contract_values(
                        handoff,
                        handoff_contract,
                        fixture_label,
                        "Wayfinder destination handoff",
                    )
                )
                destination_path = handoff.get("destination_path")
                if (
                    not isinstance(destination_path, str)
                    or not (fixture_root / destination_path).exists()
                ):
                    errors.append(
                        Finding(
                            fixture_label,
                            "Wayfinder handoff requires an existing destination_path",
                        )
                    )
        else:
            errors.append(
                Finding(
                    fixture_label,
                    f"unsupported wayfinding fixture: {identifier}",
                )
            )

    errors.extend(
        Finding(
            "stack/fixtures/wayfinding",
            f"missing required wayfinding fixture: {identifier}",
        )
        for identifier in sorted(
            REQUIRED_WAYFINDING_FIXTURE_IDENTIFIERS - identifiers
        )
    )
    return errors


def validate_skills(repo: Path) -> tuple[list[Finding], list[Finding], list[Finding], int]:
    """Run all validation phases and return grouped findings."""

    package_result = validate_skill_packages(repo)
    errors = list(package_result.errors)
    review_notes = list(package_result.review_notes)

    # The integrated registry is validated without changing the individual-skill
    # checks above, so both V2 installation modes use one command.
    errors.extend(validate_registry(repo))
    errors.extend(validate_route_fixtures(repo))
    errors.extend(validate_end_to_end_fixtures(repo))
    errors.extend(validate_clarification_fixtures(repo))
    errors.extend(validate_onboarding_fixtures(repo))
    errors.extend(validate_planning_fixtures(repo))
    errors.extend(validate_architecture_planning_fixtures(repo))
    errors.extend(validate_behavior_proof_fixtures(repo))
    errors.extend(validate_merge_conflict_fixtures(repo))
    errors.extend(validate_review_verification_fixtures(repo))
    errors.extend(validate_output_communication_fixtures(repo))
    errors.extend(validate_knowledge_retrieval_fixtures(repo))
    errors.extend(validate_source_grounded_research_fixtures(repo))
    errors.extend(validate_setup_scribe_fixtures(repo))
    errors.extend(validate_wayfinding_fixtures(repo))

    return (
        errors,
        review_notes,
        list(package_result.drift),
        len(package_result.skill_files),
    )


def print_findings(title: str, findings: list[Finding], limit: int = 30) -> None:
    """Print a readable finding group with a cap for noisy failures."""

    print(f"\n{title}: {len(findings)}")
    for finding in findings[:limit]:
        print(f"- {finding.format()}")
    remaining = len(findings) - limit
    if remaining > 0:
        print(f"- ... {remaining} more")


def main() -> int:
    """Program entrypoint used by `uv run python scripts/validate_skills.py`."""

    args = parse_args()
    repo = args.repo.expanduser().resolve()
    if not repo.exists() or not repo.is_dir():
        raise SystemExit(f"Repo path does not exist or is not a directory: {repo}")

    errors, review_notes, drift, skill_count = validate_skills(repo)
    registry_count, policy_words, skills_over_budget = registry_summary(repo)
    route_fixture_count = len(
        list((repo / "stack" / "fixtures" / "routing").glob("*.yaml"))
    )
    end_to_end_fixture_count = len(
        list((repo / "stack" / "fixtures" / "end-to-end").glob("*.yaml"))
    )
    onboarding_fixture_count = len(
        list((repo / "stack" / "fixtures" / "onboarding").glob("*.yaml"))
    )
    clarification_fixture_count = len(
        list((repo / "stack" / "fixtures" / "clarification").glob("*.yaml"))
    )
    planning_fixture_count = len(
        list((repo / "stack" / "fixtures" / "planning").glob("*.yaml"))
    )
    architecture_planning_fixture_count = len(
        list(
            (repo / "stack" / "fixtures" / "architecture-planning").glob(
                "*.yaml"
            )
        )
    )
    behavior_proof_fixture_count = len(
        list((repo / "stack" / "fixtures" / "behavior-proof").glob("*.yaml"))
    )
    merge_conflict_fixture_count = len(
        list((repo / "stack" / "fixtures" / "merge-conflicts").glob("*.yaml"))
    )
    review_verification_fixture_count = len(
        list(
            (repo / "stack" / "fixtures" / "review-verification").glob(
                "*.yaml"
            )
        )
    )
    output_communication_fixture_count = len(
        list(
            (repo / "stack" / "fixtures" / "output-communication").glob(
                "*.yaml"
            )
        )
    )
    knowledge_retrieval_fixture_count = len(
        list(
            (repo / "stack" / "fixtures" / "knowledge-retrieval").glob(
                "*.yaml"
            )
        )
    )
    source_grounded_research_fixture_count = len(
        list(
            (repo / "stack" / "fixtures" / "source-grounded-research").glob(
                "*.yaml"
            )
        )
    )
    setup_scribe_fixture_count = len(
        list((repo / "stack" / "fixtures" / "setup-scribe").glob("*.yaml"))
    )
    wayfinding_fixture_count = len(
        list((repo / "stack" / "fixtures" / "wayfinding").glob("*.yaml"))
    )
    if 800 <= policy_words <= 1200:
        policy_budget_status = "within 800-1,200 target"
    elif policy_words < 800:
        policy_budget_status = "below 800-1,200 target"
    else:
        policy_budget_status = "above 800-1,200 target"

    # Only blocking errors affect the exit code. Human-review notes and docs
    # drift are visible, but they do not fail the command by design.
    if errors:
        print(f"GOATED skill validation failed for {skill_count} implemented skills.")
        print_findings("Blocking errors", errors)
    else:
        print(f"GOATED skill validation passed for {skill_count} implemented skills.")

    if errors:
        print(
            f"Integrated registry checked with {registry_count} catalog entries; "
            f"shared policy is {policy_words} words ({policy_budget_status})."
        )
    else:
        print(
            f"Integrated registry validation passed for {registry_count} catalog entries."
        )
        print(
            "Adaptive routing fixture validation passed for "
            f"{route_fixture_count} scenarios."
        )
        print(
            "End-to-end fixture validation passed for "
            f"{end_to_end_fixture_count} scenarios."
        )
        print(
            "Onboarding fixture validation passed for "
            f"{onboarding_fixture_count} scenarios."
        )
        print(
            "Clarification fixture validation passed for "
            f"{clarification_fixture_count} scenarios."
        )
        print(
            "Planning fixture validation passed for "
            f"{planning_fixture_count} scenarios."
        )
        print(
            "Architecture and implementation-planning fixture validation passed for "
            f"{architecture_planning_fixture_count} scenarios."
        )
        print(
            "Behavior-proof fixture validation passed for "
            f"{behavior_proof_fixture_count} scenarios."
        )
        print(
            "Merge-conflict fixture validation passed for "
            f"{merge_conflict_fixture_count} scenarios."
        )
        print(
            "Review-and-verification fixture validation passed for "
            f"{review_verification_fixture_count} scenarios."
        )
        print(
            "Output-and-communication fixture validation passed for "
            f"{output_communication_fixture_count} scenarios."
        )
        print(
            "Knowledge-retrieval fixture validation passed for "
            f"{knowledge_retrieval_fixture_count} scenarios."
        )
        print(
            "Source-grounded-research fixture validation passed for "
            f"{source_grounded_research_fixture_count} scenarios."
        )
        print(
            "Setup Scribe fixture validation passed for "
            f"{setup_scribe_fixture_count} scenarios."
        )
        print(
            "Wayfinding fixture validation passed for "
            f"{wayfinding_fixture_count} scenarios."
        )
        print(
            f"Word-budget report: shared policy {policy_words} words "
            f"({policy_budget_status})."
        )
        if skills_over_budget:
            print(
                "Skills above the 1,500-word decomposition threshold: "
                + ", ".join(skills_over_budget)
            )
        else:
            print("Skills above the 1,500-word decomposition threshold: 0")
        print(
            "Per-type soft targets remain review-only until registry roles are "
            "assigned budget classes."
        )

    if review_notes:
        print_findings("Human-review notes", review_notes)
    else:
        print("\nHuman-review notes: 0")

    if drift:
        print_findings("Report-only docs/example schema drift", drift)
    else:
        print("\nReport-only docs/example schema drift: 0")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
