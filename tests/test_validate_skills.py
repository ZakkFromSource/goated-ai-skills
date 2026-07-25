"""Behavior tests for the repository validation command."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.validate_skills import validate_registry, validate_route_fixtures


REPO_ROOT = Path(__file__).resolve().parents[1]


def copy_registry_fixture(destination: Path) -> Path:
    """Copy only the integrated stack and referenced skill catalog."""

    shutil.copytree(REPO_ROOT / "stack", destination / "stack")
    shutil.copytree(REPO_ROOT / "skills", destination / "skills")
    return destination / "stack" / "goated-stack.yaml"


class RegistryValidationTests(unittest.TestCase):
    def test_current_integrated_stack_registry_is_valid(self) -> None:
        self.assertEqual([], validate_registry(REPO_ROOT))

    def test_unknown_emitted_signal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            registry_path = copy_registry_fixture(fixture_root)
            registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
            registry["skills"][0]["emits_signals"].append("not-defined")
            registry_path.write_text(
                yaml.safe_dump(registry, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message for finding in validate_registry(fixture_root)
            ]

        self.assertIn(
            "skill emits undefined route signal: not-defined",
            messages,
        )

    def test_registry_structure_is_checked_against_json_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            registry_path = copy_registry_fixture(fixture_root)
            registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
            del registry["contracts"]
            registry_path.write_text(
                yaml.safe_dump(registry, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message for finding in validate_registry(fixture_root)
            ]

        self.assertTrue(
            any(
                message.startswith("registry schema violation")
                and "'contracts' is a required property" in message
                for message in messages
            )
        )

    def test_registry_category_must_match_skill_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            registry_path = copy_registry_fixture(fixture_root)
            registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
            registry["skills"][0]["category"] = "engineering"
            registry_path.write_text(
                yaml.safe_dump(registry, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message for finding in validate_registry(fixture_root)
            ]

        self.assertIn(
            "registry category 'engineering' does not match skill path category "
            "'agent-workflows'",
            messages,
        )

    def test_every_implemented_skill_must_be_registered(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            registry_path = copy_registry_fixture(fixture_root)
            registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
            removed_path = registry["skills"].pop(0)["path"]
            registry_path.write_text(
                yaml.safe_dump(registry, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message for finding in validate_registry(fixture_root)
            ]

        self.assertIn(
            f"implemented skill is missing from registry: {removed_path}",
            messages,
        )

    def test_alias_cannot_collide_with_a_canonical_skill_name(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            registry_path = copy_registry_fixture(fixture_root)
            registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
            alias_owner = registry["skills"][0]
            canonical_name = registry["skills"][1]["name"]
            alias_owner["aliases"].append(canonical_name)
            registry_path.write_text(
                yaml.safe_dump(registry, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message for finding in validate_registry(fixture_root)
            ]

        self.assertIn(
            f"alias {canonical_name!r} for {alias_owner['name']!r} collides "
            "with a canonical skill name",
            messages,
        )


class RouteFixtureValidationTests(unittest.TestCase):
    def test_current_route_fixtures_are_valid(self) -> None:
        self.assertEqual([], validate_route_fixtures(REPO_ROOT))

    def test_route_fixture_signal_must_be_defined_by_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            copy_registry_fixture(fixture_root)
            fixture_path = (
                fixture_root
                / "stack"
                / "fixtures"
                / "routing"
                / "tiny-task-bypass.yaml"
            )
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["route_signals"] = ["not-defined"]
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message for finding in validate_route_fixtures(fixture_root)
            ]

        self.assertIn(
            "routing fixture references undefined route signal: not-defined",
            messages,
        )

    def test_route_fixture_gate_must_resolve_to_shared_or_registered_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            copy_registry_fixture(fixture_root)
            fixture_path = (
                fixture_root
                / "stack"
                / "fixtures"
                / "routing"
                / "tiny-task-bypass.yaml"
            )
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["route"]["required_gates"].append("not-defined")
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message for finding in validate_route_fixtures(fixture_root)
            ]

        self.assertIn(
            "routing fixture references undefined gate: not-defined",
            messages,
        )

    def test_checkpoint_event_requires_material_signal_and_route_delta(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            copy_registry_fixture(fixture_root)
            fixture_path = (
                fixture_root
                / "stack"
                / "fixtures"
                / "routing"
                / "tiny-task-bypass.yaml"
            )
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["checkpoint_events"] = [
                {
                    "checkpoint": "during-arbitrary-work",
                    "trigger": "security-impact",
                }
            ]
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message for finding in validate_route_fixtures(fixture_root)
            ]

        self.assertIn(
            "routing fixture checkpoint event uses unsupported checkpoint: "
            "during-arbitrary-work",
            messages,
        )
        self.assertIn(
            "routing fixture checkpoint event must define route_delta",
            messages,
        )

    def test_approval_reuse_is_rejected_after_scope_or_reach_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            copy_registry_fixture(fixture_root)
            fixture_path = (
                fixture_root
                / "stack"
                / "fixtures"
                / "routing"
                / "tiny-task-bypass.yaml"
            )
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["approval"]["scope_or_reach_changed"] = True
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message for finding in validate_route_fixtures(fixture_root)
            ]

        self.assertIn(
            "routing fixture cannot reuse approval after scope or action reach changes",
            messages,
        )

    def test_evidence_expectations_must_name_reuse_and_invalidation_sets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            copy_registry_fixture(fixture_root)
            fixture_path = (
                fixture_root
                / "stack"
                / "fixtures"
                / "routing"
                / "tiny-task-bypass.yaml"
            )
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            del fixture["expected"]["evidence"]["invalidate"]
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message for finding in validate_route_fixtures(fixture_root)
            ]

        self.assertIn(
            "routing fixture expected.evidence.invalidate must be a string list",
            messages,
        )

    def test_required_route_fixture_scenario_cannot_be_removed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            copy_registry_fixture(fixture_root)
            (
                fixture_root
                / "stack"
                / "fixtures"
                / "routing"
                / "standard-work.yaml"
            ).unlink()

            messages = [
                finding.message for finding in validate_route_fixtures(fixture_root)
            ]

        self.assertIn(
            "missing required routing fixture: standard-work",
            messages,
        )

    def test_route_fixture_risk_flag_must_use_shared_vocabulary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            copy_registry_fixture(fixture_root)
            fixture_path = (
                fixture_root
                / "stack"
                / "fixtures"
                / "routing"
                / "tiny-task-bypass.yaml"
            )
            fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
            fixture["expected"]["profile"]["risk_flags"] = ["not-defined"]
            fixture_path.write_text(
                yaml.safe_dump(fixture, sort_keys=False),
                encoding="utf-8",
            )

            messages = [
                finding.message for finding in validate_route_fixtures(fixture_root)
            ]

        self.assertIn(
            "routing fixture references undefined risk flag: not-defined",
            messages,
        )


if __name__ == "__main__":
    unittest.main()
