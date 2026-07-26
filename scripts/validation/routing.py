"""Validate adaptive-routing fixtures and their registry vocabulary."""

from __future__ import annotations

from pathlib import Path

from .shared import Finding, is_string_list, load_mapping, relative


PROFILE_ENUMS = {
    "task_size": {"tiny", "standard", "large"},
    "intent_maturity": {"fuzzy", "scoped", "implementation-ready"},
    "workflow_intensity": {"lightweight", "standard", "full"},
    "domain": {"software", "research", "documentation", "content", "other"},
    "continuity": {"single-session", "resumable"},
    "execution": {"single-agent", "delegated"},
}
RISK_FLAGS = {
    "architectural",
    "security",
    "privacy",
    "destructive",
    "external-change",
    "persistent-data",
    "dependency",
    "public-facing",
}
SENSITIVITY_VALUES = {"public", "private", "restricted"}
ACTION_REACH_VALUES = {
    "read-only",
    "session-local",
    "project-changing",
    "external-changing",
}
APPROVAL_MODES = {
    "risk-adaptive-default",
    "confirm-each-write",
    "approve-batch",
    "standing-session-consent",
    "draft-without-applying",
}
SHARED_GATES = {
    "proportional-orientation",
    "direct-work",
    "direct-proof",
    "consolidated-closeout",
}
CHECKPOINTS = {
    "after-clarification-or-diagnosis",
    "after-planning",
    "after-implementation",
    "before-final-completion",
}
REQUIRED_IDENTIFIERS = {
    "tiny-task-bypass",
    "standard-work",
    "checkpoint-escalation",
    "restricted-data",
    "external-changing-action",
    "approval-reuse",
    "evidence-invalidation",
    "conflicting-skill-triggers",
    "individual-skill-fallback",
}
REQUIRED_END_TO_END_FIXTURES = {
    "feature-brief-to-verified-change",
    "bug-report-to-root-cause-fix",
    "product-idea-to-vertical-slice",
    "existing-codebase-to-proportional-onboarding",
}


def route_fixture_vocabulary(
    registry: dict[str, object],
) -> tuple[set[str], set[str], list[Finding]]:
    """Derive signal and gate names owned by the integrated registry."""

    label = "stack/goated-stack.yaml"
    signal_entries = registry.get("route_signals", [])
    skill_entries = registry.get("skills", [])
    if not isinstance(signal_entries, list):
        return set(), set(), [Finding(label, "route_signals must be a list")]
    if not isinstance(skill_entries, list):
        return set(), set(), [Finding(label, "skills must be a list")]

    signals = {
        entry["name"]
        for entry in signal_entries
        if isinstance(entry, dict) and isinstance(entry.get("name"), str)
    }
    gates = set(SHARED_GATES)
    for entry in skill_entries:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name")
        aliases = entry.get("aliases", [])
        if isinstance(name, str):
            gates.add(name)
        if isinstance(aliases, list):
            gates.update(alias for alias in aliases if isinstance(alias, str))
    return signals, gates, []


def validate_route_fixture_profile(
    expected: dict[str, object],
    fixture_label: str,
) -> list[Finding]:
    """Validate the work-profile and proof fields for one route fixture."""

    profile = expected.get("profile")
    if not isinstance(profile, dict):
        return [
            Finding(
                fixture_label,
                "routing fixture expected.profile must be a mapping",
            )
        ]

    errors: list[Finding] = []
    for field, allowed_values in PROFILE_ENUMS.items():
        if profile.get(field) not in allowed_values:
            errors.append(
                Finding(
                    fixture_label,
                    f"routing fixture expected.profile.{field} "
                    "has unsupported value",
                )
            )
    risk_flags = profile.get("risk_flags")
    if not is_string_list(risk_flags):
        errors.append(
            Finding(
                fixture_label,
                "routing fixture expected.profile.risk_flags "
                "must be a string list",
            )
        )
    else:
        errors.extend(
            Finding(
                fixture_label,
                f"routing fixture references undefined risk flag: {risk_flag}",
            )
            for risk_flag in risk_flags
            if risk_flag not in RISK_FLAGS
        )
    if expected.get("data_sensitivity") not in SENSITIVITY_VALUES:
        errors.append(
            Finding(
                fixture_label,
                "routing fixture expected.data_sensitivity "
                "has unsupported value",
            )
        )
    if expected.get("action_reach") not in ACTION_REACH_VALUES:
        errors.append(
            Finding(
                fixture_label,
                "routing fixture expected.action_reach has unsupported value",
            )
        )
    proof_strategy = expected.get("proof_strategy")
    if not isinstance(proof_strategy, str) or not proof_strategy:
        errors.append(
            Finding(
                fixture_label,
                "routing fixture expected.proof_strategy "
                "must be a non-empty string",
            )
        )
    return errors


def validate_gate_list(
    values: object,
    field_label: str,
    fixture_label: str,
    registered_gates: set[str],
) -> tuple[list[Finding], list[str]]:
    """Validate one route gate list and return its usable values."""

    if not is_string_list(values):
        return [Finding(fixture_label, f"{field_label} must be a string list")], []
    gates = list(values)
    return (
        [
            Finding(
                fixture_label,
                f"routing fixture references undefined gate: {gate}",
            )
            for gate in gates
            if gate not in registered_gates
        ],
        gates,
    )


def validate_route(
    expected: dict[str, object],
    fixture_label: str,
    registered_gates: set[str],
) -> list[Finding]:
    """Validate initial gate selection and prevent duplicate classification."""

    route = expected.get("route")
    if not isinstance(route, dict):
        return [
            Finding(
                fixture_label,
                "routing fixture expected.route must be a mapping",
            )
        ]

    errors: list[Finding] = []
    selected_gates: set[str] = set()
    for field in ("required_gates", "conditional_gates", "skipped_gates"):
        field_errors, gates = validate_gate_list(
            route.get(field),
            f"routing fixture expected.route.{field}",
            fixture_label,
            registered_gates,
        )
        errors.extend(field_errors)
        for gate in gates:
            if gate in selected_gates:
                errors.append(
                    Finding(
                        fixture_label,
                        f"routing fixture selects gate more than once: {gate}",
                    )
                )
            selected_gates.add(gate)
    return errors


def validate_checkpoints(
    expected: dict[str, object],
    fixture_label: str,
    defined_signals: set[str],
    registered_gates: set[str],
) -> list[Finding]:
    """Validate material-signal route changes at controlled checkpoints."""

    events = expected.get("checkpoint_events")
    if not isinstance(events, list):
        return [
            Finding(
                fixture_label,
                "routing fixture expected.checkpoint_events must be a list",
            )
        ]

    errors: list[Finding] = []
    for event in events:
        if not isinstance(event, dict):
            errors.append(
                Finding(
                    fixture_label,
                    "routing fixture checkpoint event must be a mapping",
                )
            )
            continue
        checkpoint = event.get("checkpoint")
        if checkpoint not in CHECKPOINTS:
            errors.append(
                Finding(
                    fixture_label,
                    "routing fixture checkpoint event uses unsupported "
                    f"checkpoint: {checkpoint}",
                )
            )
        trigger = event.get("trigger")
        if trigger not in defined_signals:
            errors.append(
                Finding(
                    fixture_label,
                    "routing fixture checkpoint event uses undefined "
                    f"signal: {trigger}",
                )
            )
        route_delta = event.get("route_delta")
        if not isinstance(route_delta, dict):
            errors.append(
                Finding(
                    fixture_label,
                    "routing fixture checkpoint event must define route_delta",
                )
            )
            continue
        for field in ("add_required", "add_conditional", "remove"):
            field_errors, _ = validate_gate_list(
                route_delta.get(field),
                f"routing fixture checkpoint route_delta.{field}",
                fixture_label,
                registered_gates,
            )
            errors.extend(field_errors)
    return errors


def validate_approval(
    expected: dict[str, object],
    fixture_label: str,
) -> list[Finding]:
    """Validate approval mode, reuse, and scope-or-reach invalidation."""

    approval = expected.get("approval")
    if not isinstance(approval, dict):
        return [
            Finding(
                fixture_label,
                "routing fixture expected.approval must be a mapping",
            )
        ]
    if approval.get("mode") not in APPROVAL_MODES:
        return [
            Finding(
                fixture_label,
                "routing fixture expected.approval.mode has unsupported value",
            )
        ]

    errors: list[Finding] = []
    for field in (
        "consent_reused",
        "fresh_approval_required",
        "scope_or_reach_changed",
    ):
        if not isinstance(approval.get(field), bool):
            errors.append(
                Finding(
                    fixture_label,
                    f"routing fixture expected.approval.{field} must be boolean",
                )
            )
    if approval.get("scope_or_reach_changed") is True:
        if approval.get("consent_reused") is True:
            errors.append(
                Finding(
                    fixture_label,
                    "routing fixture cannot reuse approval after scope "
                    "or action reach changes",
                )
            )
        if approval.get("fresh_approval_required") is not True:
            errors.append(
                Finding(
                    fixture_label,
                    "routing fixture must require fresh approval after scope "
                    "or action reach changes",
                )
            )
    return errors


def validate_results(
    fixture: dict[str, object],
    expected: dict[str, object],
    fixture_label: str,
    defined_signals: set[str],
) -> list[Finding]:
    """Validate evidence, signals, closeout ownership, and fixture text."""

    errors: list[Finding] = []
    route_signals = expected.get("route_signals")
    if not is_string_list(route_signals):
        errors.append(
            Finding(
                fixture_label,
                "routing fixture expected.route_signals must be a string list",
            )
        )
    else:
        errors.extend(
            Finding(
                fixture_label,
                f"routing fixture references undefined route signal: {signal}",
            )
            for signal in route_signals
            if signal not in defined_signals
        )

    evidence = expected.get("evidence")
    if not isinstance(evidence, dict):
        errors.append(
            Finding(
                fixture_label,
                "routing fixture expected.evidence must be a mapping",
            )
        )
    else:
        for field in ("reuse", "invalidate"):
            if not is_string_list(evidence.get(field)):
                errors.append(
                    Finding(
                        fixture_label,
                        f"routing fixture expected.evidence.{field} "
                        "must be a string list",
                    )
                )

    closeout = expected.get("closeout")
    if not isinstance(closeout, dict):
        errors.append(
            Finding(
                fixture_label,
                "routing fixture expected.closeout must be a mapping",
            )
        )
    else:
        for field in (
            "skill_reports_internal_deltas",
            "main_agent_consolidates",
        ):
            if not isinstance(closeout.get(field), bool):
                errors.append(
                    Finding(
                        fixture_label,
                        f"routing fixture expected.closeout.{field} "
                        "must be boolean",
                    )
                )

    if not is_string_list(fixture["project_context"]):
        errors.append(
            Finding(
                fixture_label,
                "routing fixture project_context must be a string list",
            )
        )
    if not is_string_list(fixture["prohibited_behaviors"], allow_empty=False):
        errors.append(
            Finding(
                fixture_label,
                "routing fixture prohibited_behaviors "
                "must be a non-empty string list",
            )
        )
    return errors


def validate_route_fixtures(repo: Path) -> list[Finding]:
    """Validate portable adaptive-routing fixtures without freezing a schema."""

    registry, registry_errors = load_mapping(
        repo / "stack" / "goated-stack.yaml",
        "stack/goated-stack.yaml",
    )
    if registry is None:
        return registry_errors
    defined_signals, registered_gates, vocabulary_errors = (
        route_fixture_vocabulary(registry)
    )
    if vocabulary_errors:
        return vocabulary_errors

    fixture_root = repo / "stack" / "fixtures" / "routing"
    fixture_paths = sorted(fixture_root.glob("*.yaml"))
    if not fixture_paths:
        return [Finding("stack/fixtures/routing", "no routing fixtures found")]

    errors: list[Finding] = []
    identifiers: set[str] = set()
    required_fields = {
        "schema_version",
        "identifier",
        "title",
        "request",
        "project_context",
        "expected",
        "prohibited_behaviors",
    }
    for fixture_path in fixture_paths:
        fixture_label = relative(fixture_path, repo)
        fixture, fixture_errors = load_mapping(fixture_path, fixture_label)
        errors.extend(fixture_errors)
        if fixture is None:
            continue

        missing_fields = sorted(required_fields - fixture.keys())
        errors.extend(
            Finding(fixture_label, f"routing fixture is missing {field}")
            for field in missing_fields
        )
        if missing_fields:
            continue

        identifier = fixture["identifier"]
        if not isinstance(identifier, str) or not identifier:
            errors.append(
                Finding(
                    fixture_label,
                    "routing fixture identifier must be a string",
                )
            )
            continue
        if identifier in identifiers:
            errors.append(
                Finding(
                    fixture_label,
                    f"duplicate routing fixture identifier: {identifier}",
                )
            )
        identifiers.add(identifier)
        if fixture["schema_version"] != "1.0.0":
            errors.append(
                Finding(
                    fixture_label,
                    "unsupported routing fixture schema_version",
                )
            )

        expected = fixture["expected"]
        if not isinstance(expected, dict):
            errors.append(
                Finding(
                    fixture_label,
                    "routing fixture expected must be a mapping",
                )
            )
            continue
        errors.extend(validate_route_fixture_profile(expected, fixture_label))
        errors.extend(validate_route(expected, fixture_label, registered_gates))
        errors.extend(
            validate_checkpoints(
                expected,
                fixture_label,
                defined_signals,
                registered_gates,
            )
        )
        errors.extend(validate_approval(expected, fixture_label))
        errors.extend(
            validate_results(
                fixture,
                expected,
                fixture_label,
                defined_signals,
            )
        )

    errors.extend(
        Finding(
            "stack/fixtures/routing",
            f"missing required routing fixture: {identifier}",
        )
        for identifier in sorted(REQUIRED_IDENTIFIERS - identifiers)
    )
    return errors


def validate_end_to_end_fixtures(repo: Path) -> list[Finding]:
    """Validate the four release-level workflow scenarios from the V2 spec."""

    fixture_root = repo / "stack" / "fixtures" / "end-to-end"
    fixture_paths = sorted(fixture_root.glob("*.yaml"))
    if not fixture_paths:
        return [
            Finding(
                "stack/fixtures/end-to-end",
                "no end-to-end fixtures found",
            )
        ]

    registry, registry_errors = load_mapping(
        repo / "stack" / "goated-stack.yaml",
        "stack/goated-stack.yaml",
    )
    errors = list(registry_errors)
    if registry is None:
        return errors

    skill_entries = registry.get("skills")
    signal_entries = registry.get("route_signals")
    if not isinstance(skill_entries, list) or not isinstance(
        signal_entries,
        list,
    ):
        return errors + [
            Finding(
                "stack/goated-stack.yaml",
                "registry skills and route_signals must be lists",
            )
        ]

    registered_skills = {
        entry["name"]
        for entry in skill_entries
        if isinstance(entry, dict) and isinstance(entry.get("name"), str)
    }
    registered_signals = {
        entry["name"]
        for entry in signal_entries
        if isinstance(entry, dict) and isinstance(entry.get("name"), str)
    }
    identifiers: set[str] = set()
    required_fields = {
        "schema_version",
        "identifier",
        "user_request",
        "project_context",
        "expected",
        "prohibited_behaviors",
        "comparison",
    }
    expected_fields = {
        "profile",
        "selected_skills",
        "conditional_skills",
        "skipped_skills",
        "route_signals",
        "evidence",
        "closeout",
    }

    for fixture_path in fixture_paths:
        fixture_label = relative(fixture_path, repo)
        fixture, fixture_errors = load_mapping(fixture_path, fixture_label)
        errors.extend(fixture_errors)
        if fixture is None:
            continue

        for field in sorted(required_fields - fixture.keys()):
            errors.append(
                Finding(
                    fixture_label,
                    f"end-to-end fixture is missing {field}",
                )
            )
        if required_fields - fixture.keys():
            continue
        if fixture["schema_version"] != "1.0.0":
            errors.append(
                Finding(
                    fixture_label,
                    "unsupported end-to-end fixture schema_version",
                )
            )

        identifier = fixture["identifier"]
        if not isinstance(identifier, str) or not identifier:
            errors.append(
                Finding(
                    fixture_label,
                    "end-to-end identifier must be a string",
                )
            )
        elif identifier in identifiers:
            errors.append(
                Finding(
                    fixture_label,
                    f"duplicate end-to-end fixture identifier: {identifier}",
                )
            )
        else:
            identifiers.add(identifier)

        if not isinstance(fixture["user_request"], str) or not fixture[
            "user_request"
        ]:
            errors.append(
                Finding(
                    fixture_label,
                    "end-to-end user_request must be a string",
                )
            )
        if not is_string_list(fixture["project_context"]):
            errors.append(
                Finding(
                    fixture_label,
                    "end-to-end project_context must be a string list",
                )
            )
        if not is_string_list(
            fixture["prohibited_behaviors"],
            allow_empty=False,
        ):
            errors.append(
                Finding(
                    fixture_label,
                    "end-to-end prohibited_behaviors "
                    "must be a non-empty string list",
                )
            )

        expected = fixture["expected"]
        if not isinstance(expected, dict):
            errors.append(
                Finding(
                    fixture_label,
                    "end-to-end expected must be a mapping",
                )
            )
            continue
        for field in sorted(expected_fields - expected.keys()):
            errors.append(
                Finding(
                    fixture_label,
                    f"end-to-end expected is missing {field}",
                )
            )
        if expected_fields - expected.keys():
            continue

        errors.extend(validate_route_fixture_profile(expected, fixture_label))
        if identifier == "bug-report-to-root-cause-fix":
            errors.extend(
                validate_diagnosis_minimization_fixture(
                    expected,
                    fixture_label,
                )
            )
        for field in (
            "selected_skills",
            "conditional_skills",
            "skipped_skills",
        ):
            skills = expected[field]
            if not is_string_list(skills):
                errors.append(
                    Finding(
                        fixture_label,
                        f"end-to-end expected.{field} must be a string list",
                    )
                )
                continue
            for skill in skills:
                if skill not in registered_skills:
                    errors.append(
                        Finding(
                            fixture_label,
                            "end-to-end fixture references unregistered "
                            f"skill: {skill}",
                        )
                    )

        route_signals = expected["route_signals"]
        if not is_string_list(route_signals):
            errors.append(
                Finding(
                    fixture_label,
                    "end-to-end expected.route_signals must be a string list",
                )
            )
        else:
            for signal in route_signals:
                if signal not in registered_signals:
                    errors.append(
                        Finding(
                            fixture_label,
                            "end-to-end fixture references undefined route "
                            f"signal: {signal}",
                        )
                    )

        evidence = expected["evidence"]
        if not isinstance(evidence, dict):
            errors.append(
                Finding(
                    fixture_label,
                    "end-to-end evidence must be a mapping",
                )
            )
        else:
            for field in ("reuse", "refresh_after"):
                if not is_string_list(evidence.get(field)):
                    errors.append(
                        Finding(
                            fixture_label,
                            f"end-to-end evidence.{field} "
                            "must be a string list",
                        )
                    )

        closeout = expected["closeout"]
        if not isinstance(closeout, dict):
            errors.append(
                Finding(
                    fixture_label,
                    "end-to-end closeout must be a mapping",
                )
            )
        else:
            if closeout.get("single_task_closeout") is not True:
                errors.append(
                    Finding(
                        fixture_label,
                        "end-to-end fixture requires one consolidated "
                        "task closeout",
                    )
                )
            if closeout.get("specialists_return_deltas") is not True:
                errors.append(
                    Finding(
                        fixture_label,
                        "end-to-end specialists must return deltas "
                        "instead of closeouts",
                    )
                )

        comparison = fixture["comparison"]
        if not isinstance(comparison, dict):
            errors.append(
                Finding(
                    fixture_label,
                    "end-to-end comparison must be a mapping",
                )
            )
        else:
            for field in ("v1_skills", "v2_skills"):
                if not is_string_list(
                    comparison.get(field),
                    allow_empty=False,
                ):
                    errors.append(
                        Finding(
                            fixture_label,
                            f"end-to-end comparison.{field} "
                            "must be a non-empty string list",
                        )
                    )

    for identifier in sorted(REQUIRED_END_TO_END_FIXTURES - identifiers):
        errors.append(
            Finding(
                "stack/fixtures/end-to-end",
                f"missing required end-to-end fixture: {identifier}",
            )
        )
    return errors


def validate_diagnosis_minimization_fixture(
    expected: dict[str, object],
    fixture_label: str,
) -> list[Finding]:
    """Validate reproduction minimization before broad diagnostic theories."""

    diagnosis = expected.get("diagnosis")
    if not isinstance(diagnosis, dict):
        return [
            Finding(
                fixture_label,
                "bug diagnosis requires a reproduction-minimization contract",
            )
        ]

    errors: list[Finding] = []
    if diagnosis.get("reproduction_scale") != "large-reducible":
        errors.append(
            Finding(
                fixture_label,
                "diagnosis minimization fixture must use a large "
                "reducible reproduction",
            )
        )

    ordered_steps = diagnosis.get("ordered_steps")
    required_steps = (
        "establish-fast-feedback-loop",
        "confirm-exact-symptom",
        "minimize-confirmed-reproduction",
        "rank-falsifiable-hypotheses",
    )
    has_required_order = (
        is_string_list(ordered_steps, allow_empty=False)
        and all(step in ordered_steps for step in required_steps)
        and all(
            ordered_steps.index(earlier) < ordered_steps.index(later)
            for earlier, later in zip(required_steps, required_steps[1:])
        )
    )
    if not has_required_order:
        errors.append(
            Finding(
                fixture_label,
                "diagnosis must minimize a confirmed reducible reproduction "
                "before ranking hypotheses",
            )
        )

    if diagnosis.get("retained_elements_accounted_for") is not True:
        errors.append(
            Finding(
                fixture_label,
                "diagnosis minimization must account for every "
                "retained element",
            )
        )
    if diagnosis.get("symptom_fidelity_preserved") is not True:
        errors.append(
            Finding(
                fixture_label,
                "diagnosis minimization must preserve symptom fidelity",
            )
        )

    safe_fallbacks = diagnosis.get("safe_lower_confidence_fallbacks")
    required_fallbacks = {
        "intermittent",
        "production-only",
        "destructive",
        "human-in-the-loop",
    }
    if not is_string_list(safe_fallbacks) or not required_fallbacks.issubset(
        safe_fallbacks
    ):
        errors.append(
            Finding(
                fixture_label,
                "diagnosis minimization must retain safe lower-confidence "
                "fallbacks for intermittent, production-only, destructive, "
                "and human-in-the-loop cases",
            )
        )

    return errors
