"""Compare representative V1 and V2 route-specific instruction volume.

The V1 baseline is the preserved ``v1-baseline`` Git tag. V2 routes come from
the release-level end-to-end fixtures. The shared integrated policy is reported
separately because it is persistent stack policy, not route-specific specialist
text.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
MATERIAL_REDUCTION_PERCENT = 10.0


@dataclass(frozen=True)
class RouteComparison:
    """Instruction-volume result for one representative workflow."""

    identifier: str
    v1_words: int
    v2_route_words: int
    shared_policy_words: int

    @property
    def reduction_percent(self) -> float:
        return (self.v1_words - self.v2_route_words) / self.v1_words * 100

    @property
    def v2_integrated_words(self) -> int:
        return self.v2_route_words + self.shared_policy_words

    @property
    def materially_smaller(self) -> bool:
        return self.reduction_percent >= MATERIAL_REDUCTION_PERCENT


def word_count(text: str) -> int:
    """Use the validator's whitespace-word convention."""

    return len(text.split())


def git_text(repo: Path, revision: str, path: str) -> str:
    """Read one tracked file at a Git revision without changing the worktree."""

    result = subprocess.run(
        ["git", "show", f"{revision}:{path}"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout


def baseline_skill_paths(repo: Path, revision: str = "v1-baseline") -> dict[str, str]:
    """Map V1 skill folder names to their preserved SKILL.md paths."""

    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", revision],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    paths: dict[str, str] = {}
    for path in result.stdout.splitlines():
        if path.startswith("skills/") and path.endswith("/SKILL.md"):
            paths[Path(path).parent.name] = path
    return paths


def current_skill_paths(repo: Path) -> dict[str, str]:
    """Map canonical V2 registry names to portable skill paths."""

    registry = yaml.safe_load(
        (repo / "stack" / "goated-stack.yaml").read_text(encoding="utf-8")
    )
    return {entry["name"]: entry["path"] for entry in registry["skills"]}


def compare_routes(repo: Path = REPO_ROOT) -> list[RouteComparison]:
    """Calculate all release-level route comparisons."""

    v1_paths = baseline_skill_paths(repo)
    v2_paths = current_skill_paths(repo)
    shared_policy_words = word_count(
        (repo / "stack" / "AGENTS.md").read_text(encoding="utf-8")
    )
    results: list[RouteComparison] = []

    for fixture_path in sorted(
        (repo / "stack" / "fixtures" / "end-to-end").glob("*.yaml")
    ):
        fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
        comparison = fixture["comparison"]
        v1_words = sum(
            word_count(git_text(repo, "v1-baseline", v1_paths[name]))
            for name in comparison["v1_skills"]
        )
        v2_words = sum(
            word_count((repo / v2_paths[name]).read_text(encoding="utf-8"))
            for name in comparison["v2_skills"]
        )
        results.append(
            RouteComparison(
                identifier=fixture["identifier"],
                v1_words=v1_words,
                v2_route_words=v2_words,
                shared_policy_words=shared_policy_words,
            )
        )
    return results


def main() -> int:
    """Print a stable Markdown-compatible report and enforce the soft target."""

    comparisons = compare_routes()
    print(
        "| Scenario | V1 route words | V2 route words | Reduction | "
        "V2 + shared policy |"
    )
    print("| --- | ---: | ---: | ---: | ---: |")
    for result in comparisons:
        print(
            f"| {result.identifier} | {result.v1_words:,} | "
            f"{result.v2_route_words:,} | {result.reduction_percent:.1f}% | "
            f"{result.v2_integrated_words:,} |"
        )

    failures = [
        result.identifier for result in comparisons if not result.materially_smaller
    ]
    print(
        f"\nShared policy: {comparisons[0].shared_policy_words:,} words. "
        "It is shown separately from route-specific skill text."
    )
    if failures:
        print(
            "Routes below the "
            f"{MATERIAL_REDUCTION_PERCENT:.0f}% material-reduction target: "
            + ", ".join(failures)
        )
        return 1
    print(
        "All representative V2 routes meet the "
        f"{MATERIAL_REDUCTION_PERCENT:.0f}% material-reduction target."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
