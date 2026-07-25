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
import os
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError


# Public V1 skill folders live under exactly these category names.
PUBLIC_CATEGORIES = {"agent-workflows", "engineering", "productivity"}

# These body sections preserve behavior that used to live in frontmatter.
REQUIRED_SECTIONS = ("## Dependencies", "## Output Contract")

# The normalized required frontmatter shape is:
# name, description, and metadata.goated-category.
REQUIRED_FRONTMATTER_KEYS = {"name", "description", "metadata"}

# Standard Agent Skills fields are allowed, but this repo does not rely on them.
# If they appear, the script asks for human review instead of failing.
OPTIONAL_REVIEW_KEYS = {"license", "compatibility"}
ALLOWED_FRONTMATTER_KEYS = REQUIRED_FRONTMATTER_KEYS | OPTIONAL_REVIEW_KEYS

# These were useful during early GOATED design, but issue 059 moved this
# behavior into Markdown body sections for wider agent compatibility.
BANNED_TOP_LEVEL_KEYS = {
    "category",
    "classification",
    "status",
    "triggers",
    "outputs",
    "depends_on",
    "adapters",
}

# VS Code supports these fields, but GOATED public skills stay framework-neutral.
VSCODE_ONLY_KEYS = {
    "argument-hint",
    "user-invocable",
    "disable-model-invocation",
    "context",
}

# Experimental invocation controls are intentionally out of scope for V1.
EXPERIMENTAL_KEYS = {"allowed-tools"}

# Directory names skipped during broad repo scans. This keeps validation focused
# on public source files and avoids virtualenvs, build output, and private notes.
SKIPPED_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "vendor",
    "build",
    "dist",
    "target",
    ".dart_tool",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".local",
    ".scratch",
    "tmp",
    "temp",
    "__pycache__",
}

# Public text scans are deliberately narrow. They are used for local path leaks
# and docs drift, not for broad secret scanning.
PUBLIC_TEXT_SUFFIXES = {
    ".md",
    ".mdx",
    ".rst",
    ".txt",
    ".py",
    ".toml",
    ".yml",
    ".yaml",
    ".json",
    ".lock",
}
PUBLIC_TEXT_NAMES = {".gitignore"}

# Adaptive-routing fixtures use a deliberately small structural contract. The
# V2 spec reserves formal JSON Schema validation for the registry while fixture
# serialization is still maturing.
ROUTE_FIXTURE_PROFILE_ENUMS = {
    "task_size": {"tiny", "standard", "large"},
    "intent_maturity": {"fuzzy", "scoped", "implementation-ready"},
    "workflow_intensity": {"lightweight", "standard", "full"},
    "domain": {"software", "research", "documentation", "content", "other"},
    "continuity": {"single-session", "resumable"},
    "execution": {"single-agent", "delegated"},
}
ROUTE_FIXTURE_RISK_FLAGS = {
    "architectural",
    "security",
    "privacy",
    "destructive",
    "external-change",
    "persistent-data",
    "dependency",
    "public-facing",
}
ROUTE_FIXTURE_SENSITIVITY_VALUES = {"public", "private", "restricted"}
ROUTE_FIXTURE_ACTION_REACH_VALUES = {
    "read-only",
    "session-local",
    "project-changing",
    "external-changing",
}
ROUTE_FIXTURE_APPROVAL_MODES = {
    "risk-adaptive-default",
    "confirm-each-write",
    "approve-batch",
    "standing-session-consent",
    "draft-without-applying",
}
SHARED_ROUTE_GATES = {
    "proportional-orientation",
    "direct-work",
    "direct-proof",
    "consolidated-closeout",
}
ROUTE_CHECKPOINTS = {
    "after-clarification-or-diagnosis",
    "after-planning",
    "after-implementation",
    "before-final-completion",
}
REQUIRED_ROUTE_FIXTURE_IDENTIFIERS = {
    "tiny-task-bypass",
    "standard-work",
    "checkpoint-escalation",
    "restricted-data",
    "external-changing-action",
    "approval-reuse",
    "evidence-invalidation",
}
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
REQUIRED_PLANNING_FIXTURE_IDENTIFIERS = {
    "compact-spec",
    "full-spec",
    "single-ticket",
    "multi-ticket",
}
REQUIRED_ARCHITECTURE_PLANNING_FIXTURE_IDENTIFIERS = {
    "current-state-map-vs-architecture-design",
    "architecture-review-only",
    "inline-implementation-plan",
    "durable-implementation-plan",
    "compact-plan-promotion",
}
REQUIRED_KNOWLEDGE_RETRIEVAL_FIXTURE_IDENTIFIERS = {
    "authoritative-source",
    "conflicting-note",
    "missing-capability-fallback",
    "no-mutation",
    "ordinary-files-only",
    "stale-note",
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

# Regex helpers for specific mechanical checks. These intentionally favor clear,
# high-confidence matches over clever parsing.
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]+\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
LEGACY_SCHEMA_LINE_RE = re.compile(
    r"^\s{0,4}(category|classification|status|triggers|outputs|depends_on|adapters):\s*",
    re.MULTILINE,
)

# These path-leak regexes catch obvious local user home-directory paths.
# They intentionally allow generic placeholders like C:/Users/.../skills.
WINDOWS_USER_PATH_RE = re.compile(
    r"\b[A-Za-z]:[\\/]+Users[\\/]+(?!\.{2,3}(?:[\\/]|$))"
    r"[A-Za-z0-9._-]+[\\/][^\s)>\"`]*"
)
POSIX_USER_PATH_RE = re.compile(
    r"(?<![\w])/(?:Users|home)/(?!\.{2,3}(?:/|$))[A-Za-z0-9._-]+/[^\s)>\"`]*"
)


@dataclass(frozen=True)
class Finding:
    """One validation message tied to a file and optional line number."""

    path: str
    message: str
    line: int | None = None

    def format(self) -> str:
        location = self.path if self.line is None else f"{self.path}:{self.line}"
        return f"{location}: {self.message}"


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


def relative(path: Path, repo: Path) -> str:
    """Return a stable repo-relative path for readable output."""

    return path.relative_to(repo).as_posix()


def read_text(path: Path) -> str:
    """Read text files leniently so one odd byte does not crash validation."""

    return path.read_text(encoding="utf-8", errors="replace")


def iter_files(repo: Path) -> list[Path]:
    """Walk the repo without following symlinks or scanning generated folders."""

    paths: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(repo):
        # Editing dirnames in place tells os.walk which child directories to skip.
        dirnames[:] = sorted(
            dirname
            for dirname in dirnames
            if dirname not in SKIPPED_DIR_NAMES
            and not (Path(dirpath) / dirname).is_symlink()
        )
        current_dir = Path(dirpath)
        for filename in sorted(filenames):
            path = current_dir / filename
            if path.is_symlink():
                continue
            paths.append(path)
    return sorted(paths, key=lambda item: item.relative_to(repo).as_posix().lower())


def iter_public_text_files(repo: Path) -> list[Path]:
    """Return files that are reasonable to scan as public text surfaces."""

    return [
        path
        for path in iter_files(repo)
        if path.suffix.lower() in PUBLIC_TEXT_SUFFIXES or path.name in PUBLIC_TEXT_NAMES
    ]


def find_skill_files(repo: Path) -> tuple[list[Path], list[Finding]]:
    """Find implemented skills and reject malformed SKILL.md locations."""

    skills_root = repo / "skills"
    if not skills_root.exists():
        return [], [Finding("skills", "missing skills directory")]

    skill_files = sorted(skills_root.rglob("SKILL.md"))
    errors: list[Finding] = []
    valid_files: list[Path] = []

    for path in skill_files:
        parts = path.relative_to(repo).parts
        # Implemented public skills are always exactly:
        # skills/<category>/<skill-name>/SKILL.md
        if len(parts) != 4 or parts[0] != "skills" or parts[3] != "SKILL.md":
            errors.append(
                Finding(
                    relative(path, repo),
                    "SKILL.md must live at skills/<category>/<skill-name>/SKILL.md",
                )
            )
            continue
        if parts[1] not in PUBLIC_CATEGORIES:
            errors.append(
                Finding(
                    relative(path, repo),
                    f"unknown public category {parts[1]!r}; expected one of {sorted(PUBLIC_CATEGORIES)}",
                )
            )
            continue
        valid_files.append(path)

    return valid_files, errors


def split_frontmatter(text: str, path_label: str) -> tuple[dict[str, object] | None, str, list[Finding]]:
    """Split a Markdown file into YAML frontmatter and Markdown body text."""

    lines = text.splitlines()
    # Some Windows editors write a UTF-8 BOM. lstrip keeps those files valid.
    if not lines or lines[0].lstrip("\ufeff").strip() != "---":
        return None, text, [Finding(path_label, "missing YAML frontmatter")]

    end_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break

    if end_index is None:
        return None, text, [Finding(path_label, "unterminated YAML frontmatter")]

    yaml_text = "\n".join(lines[1:end_index])
    body = "\n".join(lines[end_index + 1 :])
    try:
        # safe_load parses normal YAML data without constructing Python objects.
        loaded = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        return None, body, [Finding(path_label, f"frontmatter YAML parse error: {exc}")]

    if not isinstance(loaded, dict):
        return None, body, [Finding(path_label, "frontmatter must be a mapping")]

    return loaded, body, []


def validate_frontmatter(
    path: Path, repo: Path, frontmatter: dict[str, object]
) -> tuple[list[Finding], list[Finding]]:
    """Validate the normalized frontmatter contract for one implemented skill."""

    path_label = relative(path, repo)
    category = path.relative_to(repo).parts[1]
    errors: list[Finding] = []
    notes: list[Finding] = []

    keys = set(frontmatter)
    # Specific disallowed fields get specific messages. This helps a maintainer
    # understand whether a field is legacy GOATED, framework-specific, or simply
    # unknown.
    for key in sorted(keys & BANNED_TOP_LEVEL_KEYS):
        errors.append(Finding(path_label, f"banned GOATED legacy frontmatter key: {key}"))
    for key in sorted(keys & VSCODE_ONLY_KEYS):
        errors.append(Finding(path_label, f"VS Code-only frontmatter key is not allowed: {key}"))
    for key in sorted(keys & EXPERIMENTAL_KEYS):
        errors.append(Finding(path_label, f"experimental frontmatter key is not allowed: {key}"))
    special_disallowed_keys = BANNED_TOP_LEVEL_KEYS | VSCODE_ONLY_KEYS | EXPERIMENTAL_KEYS
    for key in sorted(keys - ALLOWED_FRONTMATTER_KEYS - special_disallowed_keys):
        errors.append(Finding(path_label, f"unexpected frontmatter key: {key}"))
    for key in sorted(keys & OPTIONAL_REVIEW_KEYS):
        notes.append(Finding(path_label, f"optional frontmatter key requires human review: {key}"))

    # Required scalar fields must exist and be useful for skill discovery.
    for key in ("name", "description"):
        value = frontmatter.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(Finding(path_label, f"frontmatter {key!r} must be a non-empty string"))

    # metadata is allowed only for public category bookkeeping.
    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        errors.append(Finding(path_label, "frontmatter 'metadata' must be a mapping"))
        return errors, notes

    metadata_keys = set(metadata)
    for key in sorted(metadata_keys - {"goated-category"}):
        errors.append(Finding(path_label, f"metadata contains unexpected key: {key}"))

    # The category in metadata must agree with the folder path so copied skills
    # carry the same category label that the repo uses.
    goated_category = metadata.get("goated-category")
    if not isinstance(goated_category, str) or not goated_category.strip():
        errors.append(Finding(path_label, "metadata.goated-category must be a non-empty string"))
    elif goated_category not in PUBLIC_CATEGORIES:
        errors.append(
            Finding(
                path_label,
                f"metadata.goated-category {goated_category!r} is not one of {sorted(PUBLIC_CATEGORIES)}",
            )
        )
    elif goated_category != category:
        errors.append(
            Finding(
                path_label,
                f"metadata.goated-category {goated_category!r} must match category folder {category!r}",
            )
        )

    return errors, notes


def validate_required_sections(path: Path, repo: Path, body: str) -> list[Finding]:
    """Check for required Markdown sections in the skill body."""

    path_label = relative(path, repo)
    headings = {f"## {match.group(1).strip()}" for match in HEADING_RE.finditer(body)}
    return [
        Finding(path_label, f"missing required body section: {section}")
        for section in REQUIRED_SECTIONS
        if section not in headings
    ]


def normalize_markdown_target(raw_target: str) -> str:
    """Extract the path part from a Markdown link target."""

    target = raw_target.strip()
    # Markdown allows links like [x](<path with spaces.md>).
    if target.startswith("<"):
        end = target.find(">")
        if end != -1:
            target = target[1:end]
    else:
        # For ordinary links, anything after whitespace is a title.
        target = target.split()[0] if target.split() else ""
    return unquote(target.strip())


def is_external_or_anchor(target: str) -> bool:
    """Return True for targets this script should not check on disk."""

    if not target or target.startswith("#"):
        return True
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
        return True
    if target.startswith("//"):
        return True
    return False


def validate_markdown_links(path: Path, repo: Path, text: str) -> list[Finding]:
    """Fail on broken relative links from SKILL.md files."""

    errors: list[Finding] = []
    for match in MARKDOWN_LINK_RE.finditer(text):
        target = normalize_markdown_target(match.group(1))
        if is_external_or_anchor(target):
            continue
        target_without_fragment = target.split("#", 1)[0].split("?", 1)[0]
        if not target_without_fragment:
            continue
        if Path(target_without_fragment).is_absolute():
            continue
        resolved = (path.parent / target_without_fragment).resolve()
        if not resolved.exists():
            # Count newlines before the match to produce a 1-based line number.
            line = text.count("\n", 0, match.start()) + 1
            errors.append(
                Finding(
                    relative(path, repo),
                    f"relative Markdown link target does not exist: {target}",
                    line=line,
                )
            )
    return errors


def validate_forbidden_skill_files(skill_file: Path, repo: Path) -> list[Finding]:
    """Reject Codex-specific metadata files inside public skill folders."""

    skill_root = skill_file.parent
    errors: list[Finding] = []
    for path in sorted(skill_root.rglob("openai.yaml")):
        errors.append(Finding(relative(path, repo), "Codex openai.yaml files are not allowed in skill folders"))
    return errors


def scan_public_path_leaks(repo: Path) -> list[Finding]:
    """Find obvious local user paths in public text files."""

    errors: list[Finding] = []
    for path in iter_public_text_files(repo):
        text = read_text(path)
        for regex in (WINDOWS_USER_PATH_RE, POSIX_USER_PATH_RE):
            for match in regex.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                errors.append(
                    Finding(
                        relative(path, repo),
                        f"high-confidence local user path leak: {match.group(0)}",
                        line=line,
                    )
                )
    return errors


def scan_docs_schema_drift(repo: Path, skill_files: set[Path]) -> list[Finding]:
    """Report old schema-looking lines in docs without failing the command."""

    drift: list[Finding] = []
    for path in iter_public_text_files(repo):
        # Skill files are validated strictly elsewhere. This pass is only for
        # prose docs, issue files, examples, and other public text.
        if path in skill_files or path.suffix.lower() not in {".md", ".mdx", ".rst", ".txt"}:
            continue
        text = read_text(path)
        for match in LEGACY_SCHEMA_LINE_RE.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            drift.append(
                Finding(
                    relative(path, repo),
                    f"possible legacy frontmatter example or drift: {match.group(1)}:",
                    line=line,
                )
            )
    return drift


def validate_canonical_architecture_references(repo: Path) -> list[Finding]:
    """Reject deprecated architecture names from active runtime and user docs."""

    deprecated_names = {
        "plan-codebase-architecture": "design-codebase-architecture",
        "improve-codebase-architecture": "review-codebase-architecture",
    }
    active_paths = [
        repo / "README.md",
        repo / "docs" / "how-to-use.md",
        repo / "docs" / "install.md",
        repo / "stack" / "AGENTS.md",
    ]
    active_paths.extend(sorted((repo / "skills").rglob("*.md")))

    errors: list[Finding] = []
    for path in active_paths:
        if not path.exists():
            continue
        text = read_text(path)
        for deprecated_name, canonical_name in deprecated_names.items():
            for match in re.finditer(re.escape(deprecated_name), text):
                line = text.count("\n", 0, match.start()) + 1
                errors.append(
                    Finding(
                        relative(path, repo),
                        f"active reference uses deprecated architecture skill name "
                        f"{deprecated_name!r}; use {canonical_name!r}",
                        line=line,
                    )
                )
    return errors


def load_mapping(path: Path, label: str) -> tuple[dict[str, object] | None, list[Finding]]:
    """Load a YAML or JSON mapping and return readable parse findings."""

    if not path.exists():
        return None, [Finding(label, "missing required file")]

    try:
        loaded = yaml.safe_load(read_text(path))
    except yaml.YAMLError as exc:
        return None, [Finding(label, f"YAML or JSON parse error: {exc}")]

    if not isinstance(loaded, dict):
        return None, [Finding(label, "document must be a mapping")]
    return loaded, []


def format_schema_path(path_parts: object) -> str:
    """Format a JSON Schema error path for a human-readable finding."""

    parts = list(path_parts)
    if not parts:
        return "<root>"
    return ".".join(str(part) for part in parts)


def validate_registry(repo: Path) -> list[Finding]:
    """Validate the integrated-stack registry schema and source cross-references."""

    registry_path = repo / "stack" / "goated-stack.yaml"
    schema_path = repo / "stack" / "schemas" / "stack-registry.schema.json"
    registry_label = "stack/goated-stack.yaml"
    schema_label = "stack/schemas/stack-registry.schema.json"

    registry, registry_errors = load_mapping(registry_path, registry_label)
    schema, schema_errors = load_mapping(schema_path, schema_label)
    errors = registry_errors + schema_errors
    if registry is None or schema is None:
        return errors

    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        errors.append(Finding(schema_label, f"invalid JSON Schema: {exc.message}"))
        return errors

    validator = Draft202012Validator(schema)
    schema_findings = sorted(
        validator.iter_errors(registry),
        key=lambda finding: [str(part) for part in finding.absolute_path],
    )
    for finding in schema_findings:
        location = format_schema_path(finding.absolute_path)
        errors.append(
            Finding(
                registry_label,
                f"registry schema violation at {location}: {finding.message}",
            )
        )

    # Cross-reference checks need the schema-guaranteed collection shapes.
    # Avoid secondary exceptions and noisy findings when structure is invalid.
    if schema_findings:
        return errors

    signal_entries = registry["route_signals"]
    skill_entries = registry["skills"]
    assert isinstance(signal_entries, list)
    assert isinstance(skill_entries, list)

    defined_signals: set[str] = set()
    for signal in signal_entries:
        assert isinstance(signal, dict)
        signal_name = signal["name"]
        assert isinstance(signal_name, str)
        if signal_name in defined_signals:
            errors.append(Finding(registry_label, f"duplicate route signal: {signal_name}"))
        defined_signals.add(signal_name)

    canonical_names: set[str] = set()
    alias_owners: dict[str, str] = {}
    registered_paths: set[str] = set()
    for skill in skill_entries:
        assert isinstance(skill, dict)
        name = skill["name"]
        path_value = skill["path"]
        category = skill["category"]
        aliases = skill["aliases"]
        accepts_signals = skill["accepts_signals"]
        emits_signals = skill["emits_signals"]
        assert isinstance(name, str)
        assert isinstance(path_value, str)
        assert isinstance(category, str)
        assert isinstance(aliases, list)
        assert isinstance(accepts_signals, list)
        assert isinstance(emits_signals, list)

        if name in canonical_names:
            errors.append(Finding(registry_label, f"duplicate canonical skill name: {name}"))
        canonical_names.add(name)

        if path_value in registered_paths:
            errors.append(Finding(registry_label, f"duplicate registered skill path: {path_value}"))
        registered_paths.add(path_value)

        for alias in aliases:
            assert isinstance(alias, str)
            existing_owner = alias_owners.get(alias)
            if existing_owner is not None:
                errors.append(
                    Finding(
                        registry_label,
                        f"alias {alias!r} resolves to both {existing_owner!r} and {name!r}",
                    )
                )
            alias_owners[alias] = name

        for signal in accepts_signals:
            assert isinstance(signal, str)
            if signal not in defined_signals:
                errors.append(
                    Finding(
                        registry_label,
                        f"skill accepts undefined route signal: {signal}",
                    )
                )
        for signal in emits_signals:
            assert isinstance(signal, str)
            if signal not in defined_signals:
                errors.append(
                    Finding(
                        registry_label,
                        f"skill emits undefined route signal: {signal}",
                    )
                )

        skill_path = repo / Path(path_value)
        if not skill_path.exists():
            errors.append(Finding(registry_label, f"referenced skill does not exist: {path_value}"))
            continue

        path_parts = Path(path_value).parts
        path_category = path_parts[1]
        if category != path_category:
            errors.append(
                Finding(
                    registry_label,
                    f"registry category {category!r} does not match skill path category "
                    f"{path_category!r}",
                )
            )

        frontmatter, _, frontmatter_errors = split_frontmatter(
            read_text(skill_path),
            path_value,
        )
        errors.extend(frontmatter_errors)
        if frontmatter is None:
            continue

        frontmatter_name = frontmatter.get("name")
        if frontmatter_name != name:
            errors.append(
                Finding(
                    registry_label,
                    f"registry name {name!r} does not match skill frontmatter name "
                    f"{frontmatter_name!r}",
                )
            )
        metadata = frontmatter.get("metadata")
        frontmatter_category = (
            metadata.get("goated-category") if isinstance(metadata, dict) else None
        )
        if frontmatter_category != category:
            errors.append(
                Finding(
                    registry_label,
                    f"registry category {category!r} does not match skill frontmatter "
                    f"category {frontmatter_category!r}",
                )
            )

    for alias, owner in sorted(alias_owners.items()):
        if alias in canonical_names:
            errors.append(
                Finding(
                    registry_label,
                    f"alias {alias!r} for {owner!r} collides with a canonical skill name",
                )
            )

    implemented_skills, _ = find_skill_files(repo)
    implemented_paths = {relative(path, repo) for path in implemented_skills}
    for missing_path in sorted(implemented_paths - registered_paths):
        errors.append(
            Finding(
                registry_label,
                f"implemented skill is missing from registry: {missing_path}",
            )
        )

    return errors


def is_string_list(value: object, *, allow_empty: bool = True) -> bool:
    """Return whether a fixture value is a list containing only strings."""

    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(isinstance(entry, str) for entry in value)
    )


def route_fixture_vocabulary(
    registry: dict[str, object],
) -> tuple[set[str], set[str], list[Finding]]:
    """Derive signal and gate names owned by the integrated registry."""

    registry_label = "stack/goated-stack.yaml"
    signal_entries = registry.get("route_signals", [])
    skill_entries = registry.get("skills", [])
    if not isinstance(signal_entries, list):
        return set(), set(), [Finding(registry_label, "route_signals must be a list")]
    if not isinstance(skill_entries, list):
        return set(), set(), [Finding(registry_label, "skills must be a list")]

    signals = {
        entry["name"]
        for entry in signal_entries
        if isinstance(entry, dict) and isinstance(entry.get("name"), str)
    }
    gates = set(SHARED_ROUTE_GATES)
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

    errors: list[Finding] = []
    profile = expected.get("profile")
    if not isinstance(profile, dict):
        return [
            Finding(fixture_label, "routing fixture expected.profile must be a mapping")
        ]

    for field, allowed_values in ROUTE_FIXTURE_PROFILE_ENUMS.items():
        if profile.get(field) not in allowed_values:
            errors.append(
                Finding(
                    fixture_label,
                    f"routing fixture expected.profile.{field} has unsupported value",
                )
            )
    risk_flags = profile.get("risk_flags")
    if not is_string_list(risk_flags):
        errors.append(
            Finding(
                fixture_label,
                "routing fixture expected.profile.risk_flags must be a string list",
            )
        )
    else:
        errors.extend(
            Finding(
                fixture_label,
                f"routing fixture references undefined risk flag: {risk_flag}",
            )
            for risk_flag in risk_flags
            if risk_flag not in ROUTE_FIXTURE_RISK_FLAGS
        )
    if expected.get("data_sensitivity") not in ROUTE_FIXTURE_SENSITIVITY_VALUES:
        errors.append(
            Finding(
                fixture_label,
                "routing fixture expected.data_sensitivity has unsupported value",
            )
        )
    if expected.get("action_reach") not in ROUTE_FIXTURE_ACTION_REACH_VALUES:
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
                "routing fixture expected.proof_strategy must be a non-empty string",
            )
        )
    return errors


def validate_route_fixture_gate_list(
    values: object,
    field_label: str,
    fixture_label: str,
    registered_gates: set[str],
) -> tuple[list[Finding], list[str]]:
    """Validate one route gate list and return its usable values."""

    if not is_string_list(values):
        return [
            Finding(fixture_label, f"{field_label} must be a string list")
        ], []

    gates = list(values)
    errors = [
        Finding(fixture_label, f"routing fixture references undefined gate: {gate}")
        for gate in gates
        if gate not in registered_gates
    ]
    return errors, gates


def validate_route_fixture_route(
    expected: dict[str, object],
    fixture_label: str,
    registered_gates: set[str],
) -> list[Finding]:
    """Validate initial gate selection and prevent duplicate classification."""

    route = expected.get("route")
    if not isinstance(route, dict):
        return [Finding(fixture_label, "routing fixture expected.route must be a mapping")]

    errors: list[Finding] = []
    selected_gates: set[str] = set()
    for field in ("required_gates", "conditional_gates", "skipped_gates"):
        field_errors, gates = validate_route_fixture_gate_list(
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


def validate_route_fixture_checkpoints(
    expected: dict[str, object],
    fixture_label: str,
    defined_signals: set[str],
    registered_gates: set[str],
) -> list[Finding]:
    """Validate material-signal route changes at controlled checkpoints."""

    checkpoint_events = expected.get("checkpoint_events")
    if not isinstance(checkpoint_events, list):
        return [
            Finding(
                fixture_label,
                "routing fixture expected.checkpoint_events must be a list",
            )
        ]

    errors: list[Finding] = []
    for event in checkpoint_events:
        if not isinstance(event, dict):
            errors.append(
                Finding(fixture_label, "routing fixture checkpoint event must be a mapping")
            )
            continue
        checkpoint = event.get("checkpoint")
        if checkpoint not in ROUTE_CHECKPOINTS:
            errors.append(
                Finding(
                    fixture_label,
                    "routing fixture checkpoint event uses unsupported checkpoint: "
                    f"{checkpoint}",
                )
            )
        trigger = event.get("trigger")
        if trigger not in defined_signals:
            errors.append(
                Finding(
                    fixture_label,
                    f"routing fixture checkpoint event uses undefined signal: {trigger}",
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
            field_errors, _ = validate_route_fixture_gate_list(
                route_delta.get(field),
                f"routing fixture checkpoint route_delta.{field}",
                fixture_label,
                registered_gates,
            )
            errors.extend(field_errors)
    return errors


def validate_route_fixture_approval(
    expected: dict[str, object],
    fixture_label: str,
) -> list[Finding]:
    """Validate approval mode, reuse, and scope-or-reach invalidation."""

    approval = expected.get("approval")
    if not isinstance(approval, dict):
        return [
            Finding(fixture_label, "routing fixture expected.approval must be a mapping")
        ]
    if approval.get("mode") not in ROUTE_FIXTURE_APPROVAL_MODES:
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
                    "routing fixture cannot reuse approval after scope or action reach changes",
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


def validate_route_fixture_results(
    fixture: dict[str, object],
    expected: dict[str, object],
    fixture_label: str,
    defined_signals: set[str],
) -> list[Finding]:
    """Validate evidence, signals, closeout ownership, and public fixture text."""

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
            Finding(fixture_label, "routing fixture expected.evidence must be a mapping")
        )
    else:
        for field in ("reuse", "invalidate"):
            if not is_string_list(evidence.get(field)):
                errors.append(
                    Finding(
                        fixture_label,
                        f"routing fixture expected.evidence.{field} must be a string list",
                    )
                )

    closeout = expected.get("closeout")
    if not isinstance(closeout, dict):
        errors.append(
            Finding(fixture_label, "routing fixture expected.closeout must be a mapping")
        )
    else:
        for field in ("skill_reports_internal_deltas", "main_agent_consolidates"):
            if not isinstance(closeout.get(field), bool):
                errors.append(
                    Finding(
                        fixture_label,
                        f"routing fixture expected.closeout.{field} must be boolean",
                    )
                )

    if not is_string_list(fixture["project_context"]):
        errors.append(
            Finding(fixture_label, "routing fixture project_context must be a string list")
        )
    if not is_string_list(fixture["prohibited_behaviors"], allow_empty=False):
        errors.append(
            Finding(
                fixture_label,
                "routing fixture prohibited_behaviors must be a non-empty string list",
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
    defined_signals, registered_gates, vocabulary_errors = route_fixture_vocabulary(
        registry
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
                Finding(fixture_label, "routing fixture identifier must be a string")
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
                Finding(fixture_label, "unsupported routing fixture schema_version")
            )

        expected = fixture["expected"]
        if not isinstance(expected, dict):
            errors.append(
                Finding(fixture_label, "routing fixture expected must be a mapping")
            )
            continue
        errors.extend(validate_route_fixture_profile(expected, fixture_label))
        errors.extend(
            validate_route_fixture_route(expected, fixture_label, registered_gates)
        )
        errors.extend(
            validate_route_fixture_checkpoints(
                expected,
                fixture_label,
                defined_signals,
                registered_gates,
            )
        )
        errors.extend(validate_route_fixture_approval(expected, fixture_label))
        errors.extend(
            validate_route_fixture_results(
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
        for identifier in sorted(REQUIRED_ROUTE_FIXTURE_IDENTIFIERS - identifiers)
    )
    return errors


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
                Finding(fixture_label, "clarification evidence.reused must be a string list")
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
                    Finding(fixture_label, f"clarification risk.{field} must be boolean")
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
                Finding(fixture_label, "clarification prototype.needed must be boolean")
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
                Finding(fixture_label, "unsupported clarification fixture schema_version")
            )

        identifier = fixture["identifier"]
        if not isinstance(identifier, str) or not identifier:
            errors.append(
                Finding(fixture_label, "clarification fixture identifier must be a string")
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
                Finding(fixture_label, "clarification fixture expected must be a mapping")
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
                Finding(fixture_label, "unsupported onboarding fixture schema_version")
            )

        identifier = fixture["identifier"]
        if not isinstance(identifier, str) or not identifier:
            errors.append(
                Finding(fixture_label, "onboarding fixture identifier must be a string")
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
                Finding(fixture_label, "onboarding fixture expected must be a mapping")
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
                    "onboarding fixture prohibited_behaviors must be a non-empty string list",
                )
            )

    errors.extend(
        Finding(
            "stack/fixtures/onboarding",
            f"missing required onboarding fixture: {identifier}",
        )
        for identifier in sorted(
            REQUIRED_ONBOARDING_FIXTURE_IDENTIFIERS - identifiers
        )
    )
    return errors


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


def validate_planning_ticket_expected(
    expected: dict[str, object],
    fixture_label: str,
    repo: Path,
) -> list[Finding]:
    """Validate ticket portability, ordering, paths, and approval reuse."""

    errors: list[Finding] = []
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

    order_file = expected.get("order_file")
    if len(tickets) > 1 and (
        not isinstance(order_file, str)
        or not re.fullmatch(r"tickets/[^/]+-order\.md", order_file)
    ):
        errors.append(
            Finding(
                fixture_label,
                "multi-ticket fixture must define a tickets/<spec-slug>-order.md file",
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


def validate_fixture_contract_values(
    actual: dict[str, object],
    required: dict[str, object],
    fixture_label: str,
    contract_name: str,
) -> list[Finding]:
    """Return readable findings for mismatched fixture contract values."""

    return [
        Finding(
            fixture_label,
            f"{contract_name} requires {field}={required_value!r}",
        )
        for field, required_value in required.items()
        if actual.get(field) != required_value
    ]


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


def validate_knowledge_retrieval_fixtures(repo: Path) -> list[Finding]:
    """Validate the portable knowledge-retrieval behavior fixtures."""

    fixture_root = repo / "stack" / "fixtures" / "knowledge-retrieval"
    fixture_paths = sorted(fixture_root.glob("*.yaml"))
    if not fixture_paths:
        return [
            Finding(
                "stack/fixtures/knowledge-retrieval",
                "no knowledge-retrieval fixtures found",
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
                    "unsupported knowledge-retrieval fixture schema_version",
                )
            )

        identifier = fixture.get("identifier")
        if not isinstance(identifier, str):
            errors.append(
                Finding(
                    fixture_label,
                    "knowledge-retrieval fixture identifier must be a string",
                )
            )
            continue
        if identifier in identifiers:
            errors.append(
                Finding(
                    fixture_label,
                    f"duplicate knowledge-retrieval fixture identifier: {identifier}",
                )
            )
        identifiers.add(identifier)

        if not isinstance(fixture.get("expected"), dict):
            errors.append(
                Finding(
                    fixture_label,
                    "knowledge-retrieval fixture expected must be a mapping",
                )
            )
        if not is_string_list(
            fixture.get("prohibited_behaviors"),
            allow_empty=False,
        ):
            errors.append(
                Finding(
                    fixture_label,
                    "knowledge-retrieval prohibited_behaviors must be "
                    "a non-empty string list",
                )
            )

        expected = fixture.get("expected")
        evidence_bundle = (
            expected.get("evidence_bundle")
            if isinstance(expected, dict)
            else None
        )
        if evidence_bundle is not None:
            required_evidence_fields = {
                "identifier",
                "relevance",
                "applicable_scope",
                "finding",
                "provenance",
                "freshness",
                "confidence",
                "uncertainty",
            }
            if (
                not isinstance(evidence_bundle, list)
                or not evidence_bundle
                or any(
                    not isinstance(entry, dict)
                    or not required_evidence_fields.issubset(entry)
                    for entry in evidence_bundle
                )
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "retrieved evidence entries require identifier, "
                        "relevance, applicable_scope, finding, provenance, "
                        "freshness, confidence, and uncertainty",
                    )
                )
            elif any(
                not isinstance(entry.get("freshness"), str)
                or entry["freshness"].strip().casefold()
                in {"current", "stale", "unknown"}
                for entry in evidence_bundle
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "retrieved evidence freshness requires a commit, "
                        "date, or equivalent traceable marker",
                    )
                )
        if identifier == "authoritative-source" and isinstance(expected, dict):
            search = expected.get("search")
            if (
                not isinstance(search, dict)
                or search.get("progressive") is not True
                or search.get("read_only") is not True
                or search.get("external_web") is not False
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval search must be progressive, "
                        "read-only, and exclude external web research",
                    )
                )
            ranking_factors = expected.get("ranking_factors")
            required_ranking_factors = {
                "authority",
                "relevance",
                "confidence",
                "maturity",
                "freshness",
            }
            if (
                not isinstance(ranking_factors, dict)
                or any(
                    ranking_factors.get(factor) is not True
                    for factor in required_ranking_factors
                )
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval ranking requires authority, "
                        "relevance, confidence, maturity, and freshness",
                    )
                )
            required_classifications = {
                "authoritative",
                "history",
                "observation",
                "inference",
                "brainstorming",
                "stale",
            }
            classifications = expected.get("classifications_supported")
            if (
                not is_string_list(classifications, allow_empty=False)
                or not required_classifications.issubset(classifications)
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval must distinguish authoritative, "
                        "history, observation, inference, brainstorming, and "
                        "stale material",
                    )
                )
            ranked_results = expected.get("ranked_results")
            first_result = (
                ranked_results[0]
                if isinstance(ranked_results, list) and ranked_results
                else None
            )
            if (
                not isinstance(first_result, dict)
                or first_result.get("classification") != "authoritative"
                or first_result.get("freshness") != "current"
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval must rank current authoritative "
                        "evidence first",
                    )
                )
        if identifier == "conflicting-note" and isinstance(expected, dict):
            conflict = expected.get("conflict")
            if (
                not isinstance(conflict, dict)
                or conflict.get("reported") is not True
                or conflict.get("silently_merged") is not False
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval must report conflicts without "
                        "silently merging",
                    )
                )
            conflict_evidence = expected.get("evidence_bundle")
            current_authority = (
                conflict.get("current_authority")
                if isinstance(conflict, dict)
                else None
            )
            current_entries = (
                [
                    entry
                    for entry in conflict_evidence
                    if isinstance(entry, dict)
                    and entry.get("identifier") == current_authority
                    and entry.get("validity") == "current"
                ]
                if isinstance(conflict_evidence, list)
                else []
            )
            invalidated_entries = (
                [
                    entry
                    for entry in conflict_evidence
                    if isinstance(entry, dict)
                    and entry.get("validity") == "invalidated"
                    and entry.get("invalidated_by") == current_authority
                ]
                if isinstance(conflict_evidence, list)
                else []
            )
            if (
                not isinstance(conflict_evidence, list)
                or len(conflict_evidence) != 2
                or len(current_entries) != 1
                or len(invalidated_entries) != 1
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "resolved conflicts must preserve both evidence "
                        "entries and link the invalidated entry to current "
                        "authority",
                    )
                )
            nurture = expected.get("nurture")
            if (
                not isinstance(nurture, dict)
                or nurture.get("route_to") != "learning-capture"
                or nurture.get("performed") is not False
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval may recommend learning-capture "
                        "but cannot perform nurturing",
                    )
                )
        if identifier == "stale-note" and isinstance(expected, dict):
            if (
                expected.get("report_staleness") is not True
                or expected.get("silently_discard") is not False
                or expected.get("silently_merge") is not False
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "stale knowledge must be reported without silent "
                        "merge or discard",
                    )
                )
        if identifier == "ordinary-files-only" and isinstance(expected, dict):
            selected_path = expected.get("selected_path")
            selected_source_exists = (
                isinstance(selected_path, str)
                and (fixture_root / selected_path).is_file()
            )
            if (
                not selected_source_exists
                or expected.get("ordinary_files_sufficient") is not True
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "ordinary-file retrieval requires a real selected_path "
                        "and ordinary_files_sufficient=True",
                    )
                )
        if identifier == "missing-capability-fallback" and isinstance(
            expected,
            dict,
        ):
            fallback = expected.get("fallback")
            if (
                not isinstance(fallback, dict)
                or fallback.get("ordinary_files") is not True
                or expected.get("blocked") is not False
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "missing capabilities must fall back to ordinary "
                        "local files",
                    )
                )
            if expected.get("external_web") is not False:
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval fixtures must keep external web "
                        "research out of scope",
                    )
                )
        if identifier == "no-mutation" and isinstance(expected, dict):
            mutation_fields = {
                "filesystem_mutated",
                "index_created",
                "cache_created",
                "note_updated",
            }
            if any(
                expected.get(field) is not False
                for field in mutation_fields
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval must not mutate files, notes, "
                        "indexes, or caches",
                    )
                )

    errors.extend(
        Finding(
            "stack/fixtures/knowledge-retrieval",
            f"missing required knowledge-retrieval fixture: {identifier}",
        )
        for identifier in sorted(
            REQUIRED_KNOWLEDGE_RETRIEVAL_FIXTURE_IDENTIFIERS - identifiers
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


def registry_summary(repo: Path) -> tuple[int, int, list[str]]:
    """Return catalog size, shared-policy words, and skills over 1,500 words."""

    registry, errors = load_mapping(
        repo / "stack" / "goated-stack.yaml",
        "stack/goated-stack.yaml",
    )
    if registry is None or errors:
        return 0, 0, []

    skills = registry.get("skills", [])
    assert isinstance(skills, list)
    policy_path = repo / "stack" / "AGENTS.md"
    policy_words = len(read_text(policy_path).split()) if policy_path.exists() else 0
    over_budget_paths: list[str] = []
    for skill in skills:
        assert isinstance(skill, dict)
        skill_path = repo / str(skill["path"])
        if skill_path.exists() and len(read_text(skill_path).split()) > 1500:
            over_budget_paths.append(str(skill["path"]))
    return len(skills), policy_words, over_budget_paths


def validate_skills(repo: Path) -> tuple[list[Finding], list[Finding], list[Finding], int]:
    """Run all validation phases and return grouped findings."""

    skill_files, errors = find_skill_files(repo)
    review_notes: list[Finding] = []

    for path in skill_files:
        text = read_text(path)
        path_label = relative(path, repo)

        # A malformed frontmatter block should not stop later body checks. The
        # script returns the body text it can recover, then continues.
        frontmatter, body, frontmatter_errors = split_frontmatter(text, path_label)
        errors.extend(frontmatter_errors)
        if frontmatter is not None:
            frontmatter_errors, frontmatter_notes = validate_frontmatter(path, repo, frontmatter)
            errors.extend(frontmatter_errors)
            review_notes.extend(frontmatter_notes)
        errors.extend(validate_required_sections(path, repo, body))
        errors.extend(validate_markdown_links(path, repo, text))
        errors.extend(validate_forbidden_skill_files(path, repo))

    # Public-boundary checks scan the whole public text surface, not just skills.
    errors.extend(scan_public_path_leaks(repo))
    errors.extend(validate_canonical_architecture_references(repo))

    # The integrated registry is validated without changing the individual-skill
    # checks above, so both V2 installation modes use one command.
    errors.extend(validate_registry(repo))
    errors.extend(validate_route_fixtures(repo))
    errors.extend(validate_clarification_fixtures(repo))
    errors.extend(validate_onboarding_fixtures(repo))
    errors.extend(validate_planning_fixtures(repo))
    errors.extend(validate_architecture_planning_fixtures(repo))
    errors.extend(validate_knowledge_retrieval_fixtures(repo))
    errors.extend(validate_wayfinding_fixtures(repo))

    # Docs drift is informational in issue 060, so it is returned separately.
    drift = scan_docs_schema_drift(repo, set(skill_files))
    return errors, review_notes, drift, len(skill_files)


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
    knowledge_retrieval_fixture_count = len(
        list(
            (repo / "stack" / "fixtures" / "knowledge-retrieval").glob(
                "*.yaml"
            )
        )
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
            "Knowledge-retrieval fixture validation passed for "
            f"{knowledge_retrieval_fixture_count} scenarios."
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
