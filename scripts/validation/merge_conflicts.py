"""Validate merge-conflict resolution fixtures."""

from __future__ import annotations

from pathlib import Path

from .shared import (
    Finding,
    is_string_list,
    load_mapping,
    relative,
    validate_fixture_contract_values,
)


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
