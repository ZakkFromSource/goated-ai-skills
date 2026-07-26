"""Validate clarification and proportional-onboarding fixtures."""

from __future__ import annotations

from pathlib import Path

from .shared import Finding, is_string_list, load_mapping, relative


CLARIFICATION_MODES = {
    "focused",
    "rapid",
    "recommend-and-proceed",
    "deep-dive",
}
CLARIFICATION_WORKFLOW_INTENSITIES = {"lightweight", "standard", "full"}
REQUIRED_CLARIFICATION_FIXTURE_IDENTIFIERS = {
    "lightweight-no-question",
    "rapid-three-question",
    "focused-irreversible-decision",
    "large-architecture-deep-dive",
    "prototype-needed",
    "prototype-not-needed",
}
ONBOARDING_PROFILES = {"lightweight", "standard", "full"}
ONBOARDING_ARTIFACT_ACTIONS = {"create", "refresh", "preserve"}
ONBOARDING_CONTINUITY_STORAGE = {
    "conversation",
    "project-local-ignored",
    "os-temp",
}
REQUIRED_ONBOARDING_FIXTURE_IDENTIFIERS = {
    "lightweight-small-project",
    "standard-incremental-refresh",
    "full-governance-project",
    "resume-from-handoff",
}


def validate_clarification_expected(
    expected: dict[str, object],
    fixture_label: str,
) -> list[Finding]:
    """Validate proportional clarification behavior for one fixture."""

    errors: list[Finding] = []
    mode = expected.get("mode")
    if mode not in CLARIFICATION_MODES:
        errors.append(Finding(fixture_label, "clarification mode is unsupported"))

    if expected.get("workflow_intensity") not in CLARIFICATION_WORKFLOW_INTENSITIES:
        errors.append(
            Finding(fixture_label, "clarification workflow_intensity is unsupported")
        )

    questions = expected.get("questions")
    if not is_string_list(questions):
        errors.append(
            Finding(fixture_label, "clarification questions must be a string list")
        )
        questions = []

    question_budget = expected.get("question_budget")
    if mode == "deep-dive":
        if question_budget is not None:
            errors.append(
                Finding(
                    fixture_label,
                    "deep-dive clarification must not have a preset question budget",
                )
            )
    elif not isinstance(question_budget, int) or question_budget < 0:
        errors.append(
            Finding(
                fixture_label,
                "non-deep-dive clarification requires a non-negative question budget",
            )
        )
    elif len(questions) > question_budget:
        errors.append(
            Finding(fixture_label, "clarification questions exceed the soft budget")
        )

    if mode == "rapid" and len(questions) > 3:
        errors.append(
            Finding(fixture_label, "rapid clarification cannot exceed three questions")
        )
    if mode == "focused" and len(questions) > 1:
        errors.append(
            Finding(
                fixture_label,
                "focused clarification cannot bundle multiple decision questions",
            )
        )

    evidence = expected.get("evidence")
    if not isinstance(evidence, dict):
        errors.append(
            Finding(fixture_label, "clarification evidence must be a mapping")
        )
    else:
        if not is_string_list(evidence.get("reused")):
            errors.append(
                Finding(
                    fixture_label,
                    "clarification evidence.reused must be a string list",
                )
            )
        if evidence.get("discoverable_facts_asked") is not False:
            errors.append(
                Finding(
                    fixture_label,
                    "clarification must not ask for discoverable facts",
                )
            )

    decisions = expected.get("decisions")
    if not isinstance(decisions, dict):
        errors.append(
            Finding(fixture_label, "clarification decisions must be a mapping")
        )
    else:
        for field in ("settled", "provisional", "deferred", "conflicting"):
            if not is_string_list(decisions.get(field)):
                errors.append(
                    Finding(
                        fixture_label,
                        f"clarification decisions.{field} must be a string list",
                    )
                )
        summary_cadence = decisions.get("summary_cadence")
        if mode == "deep-dive" and (
            not isinstance(summary_cadence, str) or not summary_cadence
        ):
            errors.append(
                Finding(
                    fixture_label,
                    "deep-dive clarification requires a decision-summary cadence",
                )
            )

    risk = expected.get("risk")
    if not isinstance(risk, dict):
        errors.append(Finding(fixture_label, "clarification risk must be a mapping"))
    else:
        for field in (
            "irreversible_or_high_risk",
            "explicit_human_decision_required",
            "agent_defaulted",
        ):
            if not isinstance(risk.get(field), bool):
                errors.append(
                    Finding(
                        fixture_label,
                        f"clarification risk.{field} must be boolean",
                    )
                )
        if risk.get("irreversible_or_high_risk") is True and (
            risk.get("explicit_human_decision_required") is not True
            or risk.get("agent_defaulted") is not False
        ):
            errors.append(
                Finding(
                    fixture_label,
                    "irreversible or high-risk decisions require an explicit human "
                    "decision and cannot be agent-defaulted",
                )
            )

    prototype = expected.get("prototype")
    if not isinstance(prototype, dict):
        errors.append(
            Finding(fixture_label, "clarification prototype must be a mapping")
        )
    else:
        if not isinstance(prototype.get("needed"), bool):
            errors.append(
                Finding(
                    fixture_label,
                    "clarification prototype.needed must be boolean",
                )
            )
        if prototype.get("production_work") is not False:
            errors.append(
                Finding(
                    fixture_label,
                    "clarification prototype cannot produce production work",
                )
            )
        if prototype.get("needed") is True:
            for field in ("decision_question", "evidence"):
                if not isinstance(prototype.get(field), str) or not prototype[field]:
                    errors.append(
                        Finding(
                            fixture_label,
                            f"needed prototype requires a non-empty {field}",
                        )
                    )

    envelope_delta = expected.get("envelope_delta")
    if not isinstance(envelope_delta, dict):
        errors.append(
            Finding(fixture_label, "clarification envelope_delta must be a mapping")
        )
    else:
        if envelope_delta.get("updated") is not True:
            errors.append(
                Finding(fixture_label, "clarification must update the shared envelope")
            )
        if envelope_delta.get("duplicate_full_closeout") is not False:
            errors.append(
                Finding(
                    fixture_label,
                    "clarification must not produce a duplicate full closeout",
                )
            )

    return errors


def validate_clarification_fixtures(repo: Path) -> list[Finding]:
    """Validate proportional clarification fixtures without freezing a schema."""

    fixture_root = repo / "stack" / "fixtures" / "clarification"
    fixture_paths = sorted(fixture_root.glob("*.yaml"))
    if not fixture_paths:
        return [
            Finding("stack/fixtures/clarification", "no clarification fixtures found")
        ]

    required_fields = {
        "schema_version",
        "identifier",
        "title",
        "request",
        "project_context",
        "expected",
        "prohibited_behaviors",
    }
    errors: list[Finding] = []
    identifiers: set[str] = set()
    for fixture_path in fixture_paths:
        fixture_label = relative(fixture_path, repo)
        fixture, fixture_errors = load_mapping(fixture_path, fixture_label)
        errors.extend(fixture_errors)
        if fixture is None:
            continue

        missing_fields = sorted(required_fields - fixture.keys())
        errors.extend(
            Finding(fixture_label, f"clarification fixture is missing {field}")
            for field in missing_fields
        )
        if missing_fields:
            continue
        if fixture["schema_version"] != "1.0.0":
            errors.append(
                Finding(
                    fixture_label,
                    "unsupported clarification fixture schema_version",
                )
            )

        identifier = fixture["identifier"]
        if not isinstance(identifier, str) or not identifier:
            errors.append(
                Finding(
                    fixture_label,
                    "clarification fixture identifier must be a string",
                )
            )
            continue
        if identifier in identifiers:
            errors.append(
                Finding(
                    fixture_label,
                    f"duplicate clarification fixture identifier: {identifier}",
                )
            )
        identifiers.add(identifier)

        expected = fixture["expected"]
        if not isinstance(expected, dict):
            errors.append(
                Finding(
                    fixture_label,
                    "clarification fixture expected must be a mapping",
                )
            )
            continue
        errors.extend(validate_clarification_expected(expected, fixture_label))
        if not is_string_list(fixture["project_context"]):
            errors.append(
                Finding(
                    fixture_label,
                    "clarification fixture project_context must be a string list",
                )
            )
        if not is_string_list(fixture["prohibited_behaviors"], allow_empty=False):
            errors.append(
                Finding(
                    fixture_label,
                    "clarification fixture prohibited_behaviors must be a non-empty "
                    "string list",
                )
            )

    errors.extend(
        Finding(
            "stack/fixtures/clarification",
            f"missing required clarification fixture: {identifier}",
        )
        for identifier in sorted(
            REQUIRED_CLARIFICATION_FIXTURE_IDENTIFIERS - identifiers
        )
    )
    return errors


def validate_onboarding_evidence(
    expected: dict[str, object],
    fixture_label: str,
    artifact_budget: list[str],
) -> list[Finding]:
    """Validate one shared, reusable onboarding evidence bundle."""

    evidence_bundle = expected.get("evidence_bundle")
    if not isinstance(evidence_bundle, dict):
        return [
            Finding(
                fixture_label,
                "onboarding fixture expected.evidence_bundle must be a mapping",
            )
        ]

    errors: list[Finding] = []
    if not isinstance(evidence_bundle.get("identifier"), str):
        errors.append(
            Finding(
                fixture_label,
                "onboarding evidence bundle identifier must be a string",
            )
        )

    reuse_by = evidence_bundle.get("reuse_by")
    if not is_string_list(reuse_by, allow_empty=False):
        errors.append(
            Finding(
                fixture_label,
                "onboarding evidence bundle reuse_by must be a non-empty string list",
            )
        )
    elif not set(artifact_budget).issubset(reuse_by):
        errors.append(
            Finding(
                fixture_label,
                "onboarding evidence bundle must feed every budgeted artifact",
            )
        )

    entries = evidence_bundle.get("entries")
    if not isinstance(entries, list) or not entries:
        errors.append(
            Finding(
                fixture_label,
                "onboarding evidence bundle entries must be a non-empty list",
            )
        )
    else:
        for entry in entries:
            if not isinstance(entry, dict) or any(
                not isinstance(entry.get(field), str) or not entry[field]
                for field in ("locator", "provenance", "freshness", "key_finding")
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "onboarding evidence entries require locator, provenance, "
                        "freshness, and key_finding strings",
                    )
                )
                break

    inferred_standards = expected.get("inferred_standards", [])
    if not isinstance(inferred_standards, list):
        errors.append(
            Finding(
                fixture_label,
                "onboarding fixture expected.inferred_standards must be a list",
            )
        )
    else:
        for standard in inferred_standards:
            if not isinstance(standard, dict) or any(
                not isinstance(standard.get(field), str) or not standard[field]
                for field in ("statement", "provenance", "freshness", "confidence")
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "inferred standards require statement, provenance, freshness, "
                        "and confidence strings",
                    )
                )
                break
    return errors


def validate_onboarding_continuity(
    expected: dict[str, object],
    fixture_label: str,
) -> list[Finding]:
    """Validate silent orientation and safe resumable-state expectations."""

    errors: list[Finding] = []
    orientation = expected.get("orientation")
    if not isinstance(orientation, dict):
        errors.append(
            Finding(
                fixture_label,
                "onboarding fixture expected.orientation must be a mapping",
            )
        )
    else:
        for field in ("visible_report", "reuse_fresh_state"):
            if not isinstance(orientation.get(field), bool):
                errors.append(
                    Finding(
                        fixture_label,
                        f"onboarding fixture expected.orientation.{field} must be boolean",
                    )
                )
        if orientation.get("visible_report") is True:
            errors.append(
                Finding(
                    fixture_label,
                    "routine onboarding orientation must stay silent",
                )
            )
        if orientation.get("reuse_fresh_state") is False:
            errors.append(
                Finding(
                    fixture_label,
                    "onboarding orientation must reuse fresh state",
                )
            )

    continuity = expected.get("continuity")
    if not isinstance(continuity, dict):
        return errors + [
            Finding(
                fixture_label,
                "onboarding fixture expected.continuity must be a mapping",
            )
        ]

    for field in (
        "resumable",
        "verify_ignore_before_write",
        "os_temp_fallback",
        "links_durable_artifacts",
    ):
        if not isinstance(continuity.get(field), bool):
            errors.append(
                Finding(
                    fixture_label,
                    f"onboarding fixture expected.continuity.{field} must be boolean",
                )
            )
    storage_preference = continuity.get("storage_preference")
    if storage_preference not in ONBOARDING_CONTINUITY_STORAGE:
        errors.append(
            Finding(
                fixture_label,
                "onboarding fixture continuity storage_preference is unsupported",
            )
        )
    if continuity.get("resumable") is True:
        if storage_preference != "project-local-ignored":
            errors.append(
                Finding(
                    fixture_label,
                    "resumable onboarding must prefer ignored project-local state",
                )
            )
        for required_field in (
            "verify_ignore_before_write",
            "os_temp_fallback",
            "links_durable_artifacts",
        ):
            if continuity.get(required_field) is not True:
                errors.append(
                    Finding(
                        fixture_label,
                        f"resumable onboarding requires {required_field}",
                    )
                )
    return errors


def validate_onboarding_fixtures(repo: Path) -> list[Finding]:
    """Validate portable onboarding profiles and continuity expectations."""

    fixture_root = repo / "stack" / "fixtures" / "onboarding"
    fixture_paths = sorted(fixture_root.glob("*.yaml"))
    if not fixture_paths:
        return [Finding("stack/fixtures/onboarding", "no onboarding fixtures found")]

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
            Finding(fixture_label, f"onboarding fixture is missing {field}")
            for field in missing_fields
        )
        if missing_fields:
            continue
        if fixture["schema_version"] != "1.0.0":
            errors.append(
                Finding(
                    fixture_label,
                    "unsupported onboarding fixture schema_version",
                )
            )

        identifier = fixture["identifier"]
        if not isinstance(identifier, str) or not identifier:
            errors.append(
                Finding(
                    fixture_label,
                    "onboarding fixture identifier must be a string",
                )
            )
            continue
        if identifier in identifiers:
            errors.append(
                Finding(
                    fixture_label,
                    f"duplicate onboarding fixture identifier: {identifier}",
                )
            )
        identifiers.add(identifier)

        expected = fixture["expected"]
        if not isinstance(expected, dict):
            errors.append(
                Finding(
                    fixture_label,
                    "onboarding fixture expected must be a mapping",
                )
            )
            continue
        profile = expected.get("profile")
        if profile not in ONBOARDING_PROFILES:
            errors.append(
                Finding(fixture_label, "onboarding fixture profile is unsupported")
            )
        artifact_budget = expected.get("artifact_budget")
        if not is_string_list(artifact_budget, allow_empty=False):
            errors.append(
                Finding(
                    fixture_label,
                    "onboarding fixture artifact_budget must be a non-empty string list",
                )
            )
            artifact_budget = []
        elif profile == "lightweight" and artifact_budget != ["thin-policy-routing"]:
            errors.append(
                Finding(
                    fixture_label,
                    "lightweight onboarding budget must contain only thin-policy-routing",
                )
            )

        artifact_actions = expected.get("artifact_actions")
        if not isinstance(artifact_actions, dict):
            errors.append(
                Finding(
                    fixture_label,
                    "onboarding fixture artifact_actions must be a mapping",
                )
            )
        else:
            if set(artifact_actions) != set(artifact_budget):
                errors.append(
                    Finding(
                        fixture_label,
                        "onboarding artifact actions must match the artifact budget",
                    )
                )
            for action in artifact_actions.values():
                if action not in ONBOARDING_ARTIFACT_ACTIONS:
                    errors.append(
                        Finding(
                            fixture_label,
                            "onboarding artifact action is unsupported",
                        )
                    )

        errors.extend(
            validate_onboarding_evidence(expected, fixture_label, artifact_budget)
        )
        errors.extend(validate_onboarding_continuity(expected, fixture_label))
        if not is_string_list(fixture["project_context"]):
            errors.append(
                Finding(
                    fixture_label,
                    "onboarding fixture project_context must be a string list",
                )
            )
        if not is_string_list(fixture["prohibited_behaviors"], allow_empty=False):
            errors.append(
                Finding(
                    fixture_label,
                    "onboarding fixture prohibited_behaviors must be a non-empty "
                    "string list",
                )
            )

    errors.extend(
        Finding(
            "stack/fixtures/onboarding",
            f"missing required onboarding fixture: {identifier}",
        )
        for identifier in sorted(REQUIRED_ONBOARDING_FIXTURE_IDENTIFIERS - identifiers)
    )
    return errors
