"""Aggregate and render validator results without owning concern execution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from .shared import Finding


FIXTURE_DIRECTORIES = {
    "routing": "routing",
    "end_to_end": "end-to-end",
    "onboarding": "onboarding",
    "clarification": "clarification",
    "planning": "planning",
    "architecture_planning": "architecture-planning",
    "behavior_proof": "behavior-proof",
    "merge_conflicts": "merge-conflicts",
    "review_verification": "review-verification",
    "output_communication": "output-communication",
    "knowledge_retrieval": "knowledge-retrieval",
    "source_grounded_research": "source-grounded-research",
    "setup_scribe": "setup-scribe",
    "wayfinding": "wayfinding",
}

FIXTURE_SUCCESS_LABELS = (
    ("routing", "Adaptive routing"),
    ("end_to_end", "End-to-end"),
    ("onboarding", "Onboarding"),
    ("clarification", "Clarification"),
    ("planning", "Planning"),
    (
        "architecture_planning",
        "Architecture and implementation-planning",
    ),
    ("behavior_proof", "Behavior-proof"),
    ("merge_conflicts", "Merge-conflict"),
    ("review_verification", "Review-and-verification"),
    ("output_communication", "Output-and-communication"),
    ("knowledge_retrieval", "Knowledge-retrieval"),
    ("source_grounded_research", "Source-grounded-research"),
    ("setup_scribe", "Setup Scribe"),
    ("wayfinding", "Wayfinding"),
)


@dataclass(frozen=True)
class ValidationReport:
    """All data needed to render one validator command result."""

    errors: tuple[Finding, ...]
    review_notes: tuple[Finding, ...]
    drift: tuple[Finding, ...]
    skill_count: int
    registry_count: int
    policy_words: int
    skills_over_budget: tuple[str, ...]
    fixture_counts: Mapping[str, int]

    @property
    def exit_code(self) -> int:
        """Return the command exit code; only blocking errors fail."""

        return 1 if self.errors else 0

    @property
    def policy_budget_status(self) -> str:
        """Describe the shared-policy word count against its target."""

        if 800 <= self.policy_words <= 1200:
            return "within 800-1,200 target"
        if self.policy_words < 800:
            return "below 800-1,200 target"
        return "above 800-1,200 target"


def collect_fixture_counts(repo: Path) -> dict[str, int]:
    """Count each fixture family in stable presentation order."""

    fixture_root = repo / "stack" / "fixtures"
    return {
        name: len(list((fixture_root / directory).glob("*.yaml")))
        for name, directory in FIXTURE_DIRECTORIES.items()
    }


def build_validation_report(
    repo: Path,
    *,
    errors: Sequence[Finding],
    review_notes: Sequence[Finding],
    drift: Sequence[Finding],
    skill_count: int,
    registry_summary: tuple[int, int, list[str]],
) -> ValidationReport:
    """Build the immutable report data used by command presentation."""

    registry_count, policy_words, skills_over_budget = registry_summary
    return ValidationReport(
        errors=tuple(errors),
        review_notes=tuple(review_notes),
        drift=tuple(drift),
        skill_count=skill_count,
        registry_count=registry_count,
        policy_words=policy_words,
        skills_over_budget=tuple(skills_over_budget),
        fixture_counts=collect_fixture_counts(repo),
    )


def print_findings(
    title: str,
    findings: Sequence[Finding],
    limit: int = 30,
) -> None:
    """Print a readable finding group with a cap for noisy failures."""

    print(f"\n{title}: {len(findings)}")
    for finding in findings[:limit]:
        print(f"- {finding.format()}")
    remaining = len(findings) - limit
    if remaining > 0:
        print(f"- ... {remaining} more")


def render_validation_report(report: ValidationReport) -> int:
    """Render the established CLI output and return its exit code."""

    if report.errors:
        print(
            "GOATED skill validation failed for "
            f"{report.skill_count} implemented skills."
        )
        print_findings("Blocking errors", report.errors)
        print(
            f"Integrated registry checked with {report.registry_count} "
            f"catalog entries; shared policy is {report.policy_words} words "
            f"({report.policy_budget_status})."
        )
    else:
        print(
            "GOATED skill validation passed for "
            f"{report.skill_count} implemented skills."
        )
        print(
            "Integrated registry validation passed for "
            f"{report.registry_count} catalog entries."
        )
        for fixture_name, label in FIXTURE_SUCCESS_LABELS:
            print(
                f"{label} fixture validation passed for "
                f"{report.fixture_counts[fixture_name]} scenarios."
            )
        print(
            f"Word-budget report: shared policy {report.policy_words} words "
            f"({report.policy_budget_status})."
        )
        if report.skills_over_budget:
            print(
                "Skills above the 1,500-word decomposition threshold: "
                + ", ".join(report.skills_over_budget)
            )
        else:
            print("Skills above the 1,500-word decomposition threshold: 0")
        print(
            "Per-type soft targets remain review-only until registry roles are "
            "assigned budget classes."
        )

    if report.review_notes:
        print_findings("Human-review notes", report.review_notes)
    else:
        print("\nHuman-review notes: 0")

    if report.drift:
        print_findings("Report-only docs/example schema drift", report.drift)
    else:
        print("\nReport-only docs/example schema drift: 0")

    return report.exit_code
