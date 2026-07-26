"""Validate behavior proof, review, and output communication fixtures."""

from __future__ import annotations

from pathlib import Path

from .shared import (
    Finding,
    is_string_list,
    load_mapping,
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
