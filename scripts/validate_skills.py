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
    from .validation import behavior_proof as behavior_proof_validation
    from .validation import merge_conflicts as merge_conflict_validation
    from .validation import onboarding as onboarding_validation
    from .validation import operations as operations_validation
    from .validation import planning as planning_validation
    from .validation import research as research_validation
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
    from validation import behavior_proof as behavior_proof_validation
    from validation import merge_conflicts as merge_conflict_validation
    from validation import onboarding as onboarding_validation
    from validation import operations as operations_validation
    from validation import planning as planning_validation
    from validation import research as research_validation
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


# Compatibility re-exports keep existing callers stable while the focused
# module owns specification, ticket, architecture, and implementation planning.
validate_planning_fixtures = planning_validation.validate_planning_fixtures
validate_architecture_planning_fixtures = (
    planning_validation.validate_architecture_planning_fixtures
)


validate_merge_conflict_fixtures = (
    merge_conflict_validation.validate_merge_conflict_fixtures
)


# Compatibility re-exports keep existing callers stable while the focused
# module owns delivery proof, review, verification, and output communication.
validate_behavior_proof_fixtures = (
    behavior_proof_validation.validate_behavior_proof_fixtures
)
validate_review_verification_fixtures = (
    behavior_proof_validation.validate_review_verification_fixtures
)
validate_output_communication_fixtures = (
    behavior_proof_validation.validate_output_communication_fixtures
)


# Compatibility re-exports keep existing callers stable while the focused
# module owns durable retrieval and source-grounded public research.
validate_knowledge_retrieval_fixtures = (
    research_validation.validate_knowledge_retrieval_fixtures
)
validate_source_grounded_research_fixtures = (
    research_validation.validate_source_grounded_research_fixtures
)


# Compatibility re-exports keep existing callers stable while the focused
# module owns Setup Scribe and Wayfinding operational validation.
validate_setup_scribe_fixtures = operations_validation.validate_setup_scribe_fixtures
validate_wayfinding_fixtures = operations_validation.validate_wayfinding_fixtures


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
