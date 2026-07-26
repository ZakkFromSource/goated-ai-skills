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
from pathlib import Path

if __package__:
    from .validation import behavior_proof as behavior_proof_validation
    from .validation import merge_conflicts as merge_conflict_validation
    from .validation import onboarding as onboarding_validation
    from .validation import operations as operations_validation
    from .validation import planning as planning_validation
    from .validation import research as research_validation
    from .validation import reporting as reporting_validation
    from .validation import routing as routing_validation
    from .validation.registry import registry_summary, validate_registry
    from .validation.skill_packages import (
        validate_canonical_architecture_references,
        validate_skill_packages,
    )
    from .validation.shared import Finding
else:
    from validation import behavior_proof as behavior_proof_validation
    from validation import merge_conflicts as merge_conflict_validation
    from validation import onboarding as onboarding_validation
    from validation import operations as operations_validation
    from validation import planning as planning_validation
    from validation import research as research_validation
    from validation import reporting as reporting_validation
    from validation import routing as routing_validation
    from validation.registry import registry_summary, validate_registry
    from validation.skill_packages import (
        validate_canonical_architecture_references,
        validate_skill_packages,
    )
    from validation.shared import Finding


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


def main() -> int:
    """Run validation and delegate presentation to the reporting module."""

    args = parse_args()
    repo = args.repo.expanduser().resolve()
    if not repo.exists() or not repo.is_dir():
        raise SystemExit(f"Repo path does not exist or is not a directory: {repo}")

    errors, review_notes, drift, skill_count = validate_skills(repo)
    report = reporting_validation.build_validation_report(
        repo,
        errors=errors,
        review_notes=review_notes,
        drift=drift,
        skill_count=skill_count,
        registry_summary=registry_summary(repo),
    )
    return reporting_validation.render_validation_report(report)


if __name__ == "__main__":
    raise SystemExit(main())
