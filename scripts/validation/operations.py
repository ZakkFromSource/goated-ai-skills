"""Validate Setup Scribe and Wayfinding operational fixtures."""

from __future__ import annotations

import re
from pathlib import Path

from .shared import (
    Finding,
    HEADING_RE,
    is_string_list,
    load_mapping,
    read_text,
    relative,
    validate_fixture_contract_values,
)


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
