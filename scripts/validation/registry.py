"""Validate the integrated registry and report its catalog word budgets."""

from __future__ import annotations

from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from .shared import Finding, load_mapping, read_text, relative
from .skill_packages import find_skill_files, split_frontmatter


def format_schema_path(path_parts: object) -> str:
    """Format a JSON Schema error path for a human-readable finding."""

    parts = list(path_parts)
    if not parts:
        return "<root>"
    return ".".join(str(part) for part in parts)


def validate_registry(repo: Path) -> list[Finding]:
    """Validate the integrated-stack registry schema and cross-references."""

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
        errors.append(
            Finding(schema_label, f"invalid JSON Schema: {exc.message}")
        )
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
            errors.append(
                Finding(
                    registry_label,
                    f"duplicate route signal: {signal_name}",
                )
            )
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
            errors.append(
                Finding(
                    registry_label,
                    f"duplicate canonical skill name: {name}",
                )
            )
        canonical_names.add(name)

        if path_value in registered_paths:
            errors.append(
                Finding(
                    registry_label,
                    f"duplicate registered skill path: {path_value}",
                )
            )
        registered_paths.add(path_value)

        for alias in aliases:
            assert isinstance(alias, str)
            existing_owner = alias_owners.get(alias)
            if existing_owner is not None:
                errors.append(
                    Finding(
                        registry_label,
                        f"alias {alias!r} resolves to both "
                        f"{existing_owner!r} and {name!r}",
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
            errors.append(
                Finding(
                    registry_label,
                    f"referenced skill does not exist: {path_value}",
                )
            )
            continue

        path_parts = Path(path_value).parts
        path_category = path_parts[1]
        if category != path_category:
            errors.append(
                Finding(
                    registry_label,
                    f"registry category {category!r} does not match "
                    f"skill path category {path_category!r}",
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
                    f"registry name {name!r} does not match skill "
                    f"frontmatter name {frontmatter_name!r}",
                )
            )
        metadata = frontmatter.get("metadata")
        frontmatter_category = (
            metadata.get("goated-category")
            if isinstance(metadata, dict)
            else None
        )
        if frontmatter_category != category:
            errors.append(
                Finding(
                    registry_label,
                    f"registry category {category!r} does not match skill "
                    f"frontmatter category {frontmatter_category!r}",
                )
            )

    for alias, owner in sorted(alias_owners.items()):
        if alias in canonical_names:
            errors.append(
                Finding(
                    registry_label,
                    f"alias {alias!r} for {owner!r} collides with "
                    "a canonical skill name",
                )
            )

    implemented_skills, _ = find_skill_files(repo)
    implemented_paths = {
        relative(path, repo) for path in implemented_skills
    }
    for missing_path in sorted(implemented_paths - registered_paths):
        errors.append(
            Finding(
                registry_label,
                f"implemented skill is missing from registry: {missing_path}",
            )
        )

    return errors


def registry_summary(repo: Path) -> tuple[int, int, list[str]]:
    """Return catalog size, shared-policy words, and over-budget skills."""

    registry, errors = load_mapping(
        repo / "stack" / "goated-stack.yaml",
        "stack/goated-stack.yaml",
    )
    if registry is None or errors:
        return 0, 0, []

    skills = registry.get("skills", [])
    assert isinstance(skills, list)
    policy_path = repo / "stack" / "AGENTS.md"
    policy_words = (
        len(read_text(policy_path).split()) if policy_path.exists() else 0
    )
    over_budget_paths: list[str] = []
    for skill in skills:
        assert isinstance(skill, dict)
        skill_path = repo / str(skill["path"])
        if skill_path.exists() and len(read_text(skill_path).split()) > 1500:
            over_budget_paths.append(str(skill["path"]))
    return len(skills), policy_words, over_budget_paths
