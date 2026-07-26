"""Validate specification, ticket, architecture, and implementation planning."""

from __future__ import annotations

import re
from pathlib import Path

from .shared import (
    Finding,
    is_string_list,
    load_mapping,
    read_text,
    relative,
    validate_fixture_contract_values,
)


REQUIRED_PLANNING_FIXTURE_IDENTIFIERS = {
    "compact-spec",
    "full-spec",
    "single-ticket",
    "multi-ticket",
    "wide-refactor",
}


REQUIRED_ARCHITECTURE_PLANNING_FIXTURE_IDENTIFIERS = {
    "current-state-map-vs-architecture-design",
    "architecture-review-only",
    "inline-implementation-plan",
    "durable-implementation-plan",
    "compact-plan-promotion",
}


COMPACT_SPEC_SECTIONS = {
    "problem",
    "goals",
    "non-goals",
    "requirements",
    "acceptance-criteria",
    "constraints",
    "open-questions",
}


FULL_SPEC_DEPTH_SECTIONS = {
    "stakeholders",
    "architecture",
    "rollout",
    "migration",
    "analytics",
    "risks",
}


FRESH_AGENT_TICKET_FIELDS = {
    "parent-spec",
    "what-to-build",
    "recommended-first-reads",
    "acceptance-criteria",
    "expected-proof",
    "blocked-by",
    "scope-exclusions",
}


FRESH_AGENT_TICKET_HEADINGS = {
    "## Parent Spec",
    "## What To Build",
    "## Recommended First Reads",
    "## Acceptance Criteria",
    "## Expected Proof",
    "## Blocked By",
    "## Scope Exclusions",
}


def validate_planning_spec_expected(
    expected: dict[str, object],
    fixture_label: str,
) -> list[Finding]:
    """Validate the observable contract for one spec fixture."""

    errors: list[Finding] = []
    mode = expected.get("mode")
    sections = expected.get("sections")
    if mode not in {"compact", "full"}:
        errors.append(Finding(fixture_label, "planning spec mode is unsupported"))
    if not is_string_list(sections, allow_empty=False):
        errors.append(
            Finding(
                fixture_label,
                "planning spec sections must be a non-empty string list",
            )
        )
        sections = []

    required_sections = set(COMPACT_SPEC_SECTIONS)
    if mode == "full":
        required_sections.update(FULL_SPEC_DEPTH_SECTIONS)
    for section in sorted(required_sections - set(sections)):
        errors.append(
            Finding(
                fixture_label,
                f"{mode} spec fixture is missing required section: {section}",
            )
        )

    path = expected.get("path")
    if not isinstance(path, str) or not path.startswith("docs/specs/"):
        errors.append(
            Finding(
                fixture_label,
                "planning spec fixture must use the docs/specs/ default path",
            )
        )
    return errors


def validate_wide_refactor_ticket_expected(
    expected: dict[str, object],
    tickets: list[object],
    fixture_label: str,
) -> list[Finding]:
    """Validate expand, migrate, contract, and integration-branch invariants."""

    errors: list[Finding] = []
    phase_tickets = {
        phase: [
            ticket
            for ticket in tickets
            if isinstance(ticket, dict) and ticket.get("phase") == phase
        ]
        for phase in ("expand", "migrate", "contract")
    }
    expand_tickets = phase_tickets["expand"]
    migrate_tickets = phase_tickets["migrate"]
    contract_tickets = phase_tickets["contract"]

    if len(expand_tickets) != 1:
        errors.append(
            Finding(
                fixture_label,
                "wide-refactor fixture must define exactly one expand ticket",
            )
        )
    if not migrate_tickets:
        errors.append(
            Finding(
                fixture_label,
                "wide-refactor fixture must define at least one migrate ticket",
            )
        )
    if len(contract_tickets) != 1:
        errors.append(
            Finding(
                fixture_label,
                "wide-refactor fixture must define exactly one contract ticket",
            )
        )

    if len(expand_tickets) == 1:
        expand_ticket_id = expand_tickets[0].get("id")
        for migrate_ticket in migrate_tickets:
            migrate_ticket_id = migrate_ticket.get("id")
            if expand_ticket_id not in migrate_ticket.get("blocked_by", []):
                errors.append(
                    Finding(
                        fixture_label,
                        "wide-refactor migrate ticket "
                        f"{migrate_ticket_id} must be blocked by expand "
                        f"ticket {expand_ticket_id}",
                    )
                )
            blast_radius_basis = migrate_ticket.get("blast_radius_basis")
            if (
                not isinstance(blast_radius_basis, str)
                or not blast_radius_basis.strip()
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "wide-refactor migrate ticket "
                        f"{migrate_ticket_id} must name its blast_radius_basis",
                    )
                )

    migrate_ticket_ids = [
        migrate_ticket.get("id") for migrate_ticket in migrate_tickets
    ]
    if len(contract_tickets) == 1:
        contract_ticket = contract_tickets[0]
        if set(contract_ticket.get("blocked_by", [])) != set(migrate_ticket_ids):
            errors.append(
                Finding(
                    fixture_label,
                    "wide-refactor contract ticket "
                    f"{contract_ticket.get('id')} must be blocked by every "
                    "migrate ticket: "
                    f"{', '.join(str(ticket_id) for ticket_id in migrate_ticket_ids)}",
                )
            )
        if contract_ticket.get("proves_no_old_callers") is not True:
            errors.append(
                Finding(
                    fixture_label,
                    "wide-refactor contract ticket must prove no old callers remain",
                )
            )

    integration_branch = expected.get("integration_branch")
    if not isinstance(integration_branch, dict):
        errors.append(
            Finding(
                fixture_label,
                "wide-refactor integration_branch must be a mapping",
            )
        )
    elif integration_branch.get("used") is True:
        integration_reason = integration_branch.get("reason")
        if (
            integration_branch.get("independently_green_batches") is not False
            or not isinstance(integration_reason, str)
            or not integration_reason.strip()
        ):
            errors.append(
                Finding(
                    fixture_label,
                    "wide-refactor integration branch is allowed only when "
                    "migration batches cannot remain green independently "
                    "and the reason is recorded",
                )
            )
    elif integration_branch.get("used") is not False:
        errors.append(
            Finding(
                fixture_label,
                "wide-refactor integration_branch used must be boolean",
            )
        )
    return errors


def validate_ticket_ready_frontier(
    expected: dict[str, object],
    tickets: list[object],
    fixture_label: str,
) -> list[Finding]:
    """Validate that the reported frontier follows current completion state."""

    completed_ticket_ids = expected.get("completed_ticket_ids")
    ready_frontier = expected.get("ready_frontier")
    if completed_ticket_ids is None and ready_frontier is None:
        return []

    errors: list[Finding] = []
    if not is_string_list(completed_ticket_ids):
        errors.append(
            Finding(
                fixture_label,
                "planning ticket completed_ticket_ids must be a string list",
            )
        )
        completed_ticket_ids = []
    if not is_string_list(ready_frontier):
        errors.append(
            Finding(
                fixture_label,
                "planning ticket ready_frontier must be a string list",
            )
        )
        ready_frontier = []

    completed_ticket_id_set = set(completed_ticket_ids)
    calculated_frontier = [
        ticket.get("id")
        for ticket in tickets
        if isinstance(ticket, dict)
        and ticket.get("id") not in completed_ticket_id_set
        and set(ticket.get("blocked_by", [])).issubset(completed_ticket_id_set)
    ]
    if ready_frontier != calculated_frontier:
        errors.append(
            Finding(
                fixture_label,
                "planning ticket ready_frontier must contain exactly the "
                "uncompleted tickets whose blockers are complete: "
                f"{', '.join(str(ticket_id) for ticket_id in calculated_frontier)}",
            )
        )
    return errors


def validate_planning_order_expected(
    expected: dict[str, object],
    tickets: list[object],
    fixture_label: str,
    repo: Path,
) -> list[Finding]:
    """Validate the multi-ticket order path, sample, and reported frontier."""

    if len(tickets) <= 1:
        return []

    errors: list[Finding] = []
    order_file = expected.get("order_file")
    if not isinstance(order_file, str) or not re.fullmatch(
        r"tickets/[^/]+-order\.md", order_file
    ):
        errors.append(
            Finding(
                fixture_label,
                "multi-ticket fixture must define a tickets/<spec-slug>-order.md file",
            )
        )

    order_sample = expected.get("order_sample")
    if not isinstance(order_sample, str):
        errors.append(
            Finding(
                fixture_label,
                "multi-ticket fixture must link an order sample",
            )
        )
        return errors

    order_sample_path = repo / "stack" / "fixtures" / "planning" / order_sample
    if not order_sample_path.is_file():
        errors.append(
            Finding(
                fixture_label,
                f"planning order sample does not exist: {order_sample}",
            )
        )
        return errors

    ready_frontier = expected.get("ready_frontier")
    if not is_string_list(ready_frontier):
        return errors

    order_sample_text = read_text(order_sample_path)
    frontier_section_match = re.search(
        r"^## Ready Frontier\s*$\n(?P<body>.*?)(?=^## |\Z)",
        order_sample_text,
        re.MULTILINE | re.DOTALL,
    )
    if frontier_section_match is None:
        errors.append(
            Finding(
                fixture_label,
                "planning order sample must report a Ready Frontier",
            )
        )
        return errors
    frontier_section = frontier_section_match.group("body")

    ticket_paths_by_id = {
        ticket.get("id"): ticket.get("path")
        for ticket in tickets
        if isinstance(ticket, dict)
    }
    for ready_ticket_id in ready_frontier:
        ready_ticket_path = ticket_paths_by_id.get(ready_ticket_id)
        if (
            isinstance(ready_ticket_path, str)
            and f"`{ready_ticket_path}`" not in frontier_section
        ):
            errors.append(
                Finding(
                    fixture_label,
                    "planning order sample Ready Frontier is missing "
                    f"{ready_ticket_path}",
                )
            )
    return errors


def validate_planning_ticket_expected(
    expected: dict[str, object],
    fixture_label: str,
    repo: Path,
) -> list[Finding]:
    """Validate ticket portability, ordering, paths, and approval reuse."""

    errors: list[Finding] = []
    slice_strategy = expected.get("slice_strategy", "vertical")
    if slice_strategy not in {"vertical", "wide-refactor"}:
        errors.append(
            Finding(
                fixture_label,
                "planning ticket slice_strategy must be vertical or wide-refactor",
            )
        )

    tickets = expected.get("tickets")
    if not isinstance(tickets, list) or not tickets:
        errors.append(
            Finding(
                fixture_label,
                "planning ticket fixture must define a non-empty ticket list",
            )
        )
        tickets = []

    seen_ticket_ids: set[str] = set()
    for ticket in tickets:
        if not isinstance(ticket, dict):
            errors.append(Finding(fixture_label, "planning ticket must be a mapping"))
            continue
        ticket_id = ticket.get("id")
        if not isinstance(ticket_id, str):
            errors.append(Finding(fixture_label, "planning ticket id must be a string"))
            continue
        path = ticket.get("path")
        if not isinstance(path, str) or not re.fullmatch(
            r"tickets/\d{3}-[^/]+\.md", path
        ):
            errors.append(
                Finding(
                    fixture_label,
                    f"ticket {ticket_id} must use the tickets/NNN-title.md default path",
                )
            )
        blocked_by = ticket.get("blocked_by")
        if not is_string_list(blocked_by):
            errors.append(
                Finding(
                    fixture_label,
                    f"ticket {ticket_id} blocked_by must be a string list",
                )
            )
            blocked_by = []
        for blocker in blocked_by:
            if blocker not in seen_ticket_ids:
                errors.append(
                    Finding(
                        fixture_label,
                        f"ticket {ticket_id} depends on {blocker} before it appears in order",
                    )
                )
        fields = ticket.get("fields")
        if not is_string_list(fields, allow_empty=False):
            fields = []
        for field in sorted(FRESH_AGENT_TICKET_FIELDS - set(fields)):
            errors.append(
                Finding(
                    fixture_label,
                    f"ticket {ticket_id} is missing fresh-agent field: {field}",
                )
            )
        sample = ticket.get("sample")
        if not isinstance(sample, str):
            errors.append(
                Finding(
                    fixture_label,
                    f"ticket {ticket_id} must link a fresh-agent sample",
                )
            )
        else:
            sample_path = repo / "stack" / "fixtures" / "planning" / sample
            if not sample_path.is_file():
                errors.append(
                    Finding(
                        fixture_label,
                        f"ticket {ticket_id} sample does not exist: {sample}",
                    )
                )
            else:
                sample_text = read_text(sample_path)
                for heading in sorted(
                    FRESH_AGENT_TICKET_HEADINGS
                    - set(re.findall(r"^## .+$", sample_text, re.MULTILINE))
                ):
                    errors.append(
                        Finding(
                            fixture_label,
                            f"ticket {ticket_id} sample is missing heading: {heading}",
                        )
                    )
        seen_ticket_ids.add(ticket_id)

    if slice_strategy == "wide-refactor":
        errors.extend(
            validate_wide_refactor_ticket_expected(
                expected,
                tickets,
                fixture_label,
            )
        )
    errors.extend(validate_ticket_ready_frontier(expected, tickets, fixture_label))
    errors.extend(
        validate_planning_order_expected(
            expected,
            tickets,
            fixture_label,
            repo,
        )
    )

    approval = expected.get("approval")
    if not isinstance(approval, dict):
        errors.append(Finding(fixture_label, "planning ticket approval must be a mapping"))
    elif (
        approval.get("existing_batch_approved") is True
        and approval.get("scope_or_reach_changed") is False
        and (
            approval.get("reused") is not True
            or approval.get("ask_again") is not False
        )
    ):
        errors.append(
            Finding(
                fixture_label,
                "planning fixture must reuse approval while scope and action reach remain unchanged",
            )
        )
    return errors


def validate_planning_fixtures(repo: Path) -> list[Finding]:
    """Validate proportional spec and dependency-aware ticket fixtures."""

    fixture_root = repo / "stack" / "fixtures" / "planning"
    fixture_paths = sorted(fixture_root.glob("*.yaml"))
    if not fixture_paths:
        return [Finding("stack/fixtures/planning", "no planning fixtures found")]

    errors: list[Finding] = []
    identifiers: set[str] = set()
    for fixture_path in fixture_paths:
        fixture_label = relative(fixture_path, repo)
        fixture, fixture_errors = load_mapping(fixture_path, fixture_label)
        errors.extend(fixture_errors)
        if fixture is None:
            continue

        identifier = fixture.get("identifier")
        if not isinstance(identifier, str):
            errors.append(
                Finding(fixture_label, "planning fixture identifier must be a string")
            )
            continue
        if identifier in identifiers:
            errors.append(
                Finding(
                    fixture_label,
                    f"duplicate planning fixture identifier: {identifier}",
                )
            )
        identifiers.add(identifier)

        expected = fixture.get("expected")
        if not isinstance(expected, dict):
            errors.append(
                Finding(fixture_label, "planning fixture expected must be a mapping")
            )
            continue

        artifact_kind = expected.get("artifact_kind")
        if artifact_kind == "spec":
            errors.extend(
                validate_planning_spec_expected(expected, fixture_label)
            )
        elif artifact_kind == "tickets":
            errors.extend(
                validate_planning_ticket_expected(expected, fixture_label, repo)
            )
        else:
            errors.append(
                Finding(fixture_label, "planning fixture artifact_kind is unsupported")
            )

    errors.extend(
        Finding(
            "stack/fixtures/planning",
            f"missing required planning fixture: {identifier}",
        )
        for identifier in sorted(
            REQUIRED_PLANNING_FIXTURE_IDENTIFIERS - identifiers
        )
    )
    return errors


def validate_architecture_planning_fixtures(repo: Path) -> list[Finding]:
    """Validate proportional architecture and implementation-plan routing."""

    fixture_root = repo / "stack" / "fixtures" / "architecture-planning"
    fixture_paths = sorted(fixture_root.glob("*.yaml"))
    if not fixture_paths:
        return [
            Finding(
                "stack/fixtures/architecture-planning",
                "no architecture-planning fixtures found",
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
                    "unsupported architecture-planning fixture schema_version",
                )
            )

        identifier = fixture.get("identifier")
        if not isinstance(identifier, str):
            errors.append(
                Finding(
                    fixture_label,
                    "architecture-planning fixture identifier must be a string",
                )
            )
            continue
        if identifier in identifiers:
            errors.append(
                Finding(
                    fixture_label,
                    f"duplicate architecture-planning fixture identifier: {identifier}",
                )
            )
        identifiers.add(identifier)

        expected = fixture.get("expected")
        if not isinstance(expected, dict):
            errors.append(
                Finding(
                    fixture_label,
                    "architecture-planning fixture expected must be a mapping",
                )
            )
            continue

        if expected.get("rebuilds_delivery_pipeline") is not False:
            errors.append(
                Finding(
                    fixture_label,
                    "architecture and planning routes must not rebuild the delivery pipeline",
                )
            )
        if not is_string_list(fixture.get("prohibited_behaviors"), allow_empty=False):
            errors.append(
                Finding(
                    fixture_label,
                    "architecture-planning prohibited_behaviors must be a non-empty string list",
                )
            )

        if identifier == "current-state-map-vs-architecture-design":
            routes = expected.get("routes")
            if not isinstance(routes, list) or len(routes) != 2:
                errors.append(
                    Finding(
                        fixture_label,
                        "mapping-versus-design fixture must define exactly two routes",
                    )
                )
                continue
            route_by_kind = {
                route.get("request_kind"): route
                for route in routes
                if isinstance(route, dict)
            }
            required_routes = {
                "current-state-map": (
                    "architecture-design-map",
                    "descriptive",
                ),
                "architecture-design": (
                    "design-codebase-architecture",
                    "prescriptive",
                ),
            }
            for request_kind, (skill_name, intent) in required_routes.items():
                route = route_by_kind.get(request_kind)
                if not isinstance(route, dict) or route.get("skill") != skill_name:
                    errors.append(
                        Finding(
                            fixture_label,
                            f"{request_kind} must route to {skill_name}",
                        )
                    )
                    continue
                if route.get("intent") != intent:
                    errors.append(
                        Finding(
                            fixture_label,
                            f"{request_kind} requires intent={intent!r}",
                        )
                    )
                if route.get("smallest_useful_visualization") is not True:
                    errors.append(
                        Finding(
                            fixture_label,
                            f"{request_kind} must use the smallest useful visualization",
                        )
                    )
                if route.get("mermaid_required") is not False:
                    errors.append(
                        Finding(
                            fixture_label,
                            f"{request_kind} must not require Mermaid",
                        )
                    )
                if not isinstance(route.get("next_signal"), str):
                    errors.append(
                        Finding(
                            fixture_label,
                            f"{request_kind} requires one next_signal",
                        )
                    )
            if expected.get("shared_discovery_reused") is not True:
                errors.append(
                    Finding(
                        fixture_label,
                        "mapping and design routes must be able to reuse shared discovery",
                    )
                )

        elif identifier == "architecture-review-only":
            route = expected.get("route")
            if not isinstance(route, dict):
                errors.append(
                    Finding(fixture_label, "review-only fixture route must be a mapping")
                )
                continue
            review_contract = {
                "skill": "review-codebase-architecture",
                "intent": "review-only",
                "prescriptive_blueprint": False,
                "mutates_target_architecture": False,
            }
            errors.extend(
                validate_fixture_contract_values(
                    route,
                    review_contract,
                    fixture_label,
                    "architecture review route",
                )
            )
            if not isinstance(route.get("next_signal"), str):
                errors.append(
                    Finding(
                        fixture_label,
                        "architecture review route requires one next_signal",
                    )
                )

        elif identifier in {
            "inline-implementation-plan",
            "durable-implementation-plan",
        }:
            plan = expected.get("plan")
            if not isinstance(plan, dict):
                errors.append(
                    Finding(
                        fixture_label,
                        "implementation-plan fixture plan must be a mapping",
                    )
                )
                continue
            expected_mode = (
                "inline"
                if identifier == "inline-implementation-plan"
                else "durable"
            )
            expected_tracked = expected_mode == "durable"
            if plan.get("skill") != "writing-plans":
                errors.append(
                    Finding(fixture_label, "implementation plans must use writing-plans")
                )
            if plan.get("mode") != expected_mode:
                errors.append(
                    Finding(
                        fixture_label,
                        f"{identifier} requires mode={expected_mode!r}",
                    )
                )
            if plan.get("tracked") is not expected_tracked:
                errors.append(
                    Finding(
                        fixture_label,
                        f"{expected_mode} plan tracked state is incorrect",
                    )
                )
            mode_contract = (
                {
                    "held_in_envelope": True,
                    "promotion_supported": True,
                }
                if expected_mode == "inline"
                else {"respects_project_convention": True}
            )
            errors.extend(
                validate_fixture_contract_values(
                    plan,
                    mode_contract,
                    fixture_label,
                    f"{expected_mode} plan",
                )
            )
            if not isinstance(plan.get("next_signal"), str):
                errors.append(
                    Finding(
                        fixture_label,
                        "implementation plan requires one next_signal",
                    )
                )

        elif identifier == "compact-plan-promotion":
            promotion = expected.get("promotion")
            if not isinstance(promotion, dict):
                errors.append(
                    Finding(fixture_label, "plan promotion must be a mapping")
                )
                continue
            promotion_contract = {
                "from": "inline",
                "to": "durable",
                "restart_discovery": False,
                "reuses_evidence": True,
                "preserves_decisions": True,
            }
            errors.extend(
                validate_fixture_contract_values(
                    promotion,
                    promotion_contract,
                    fixture_label,
                    "plan promotion",
                )
            )
        else:
            errors.append(
                Finding(
                    fixture_label,
                    f"unsupported architecture-planning fixture: {identifier}",
                )
            )

    errors.extend(
        Finding(
            "stack/fixtures/architecture-planning",
            f"missing required architecture-planning fixture: {identifier}",
        )
        for identifier in sorted(
            REQUIRED_ARCHITECTURE_PLANNING_FIXTURE_IDENTIFIERS - identifiers
        )
    )
    return errors
