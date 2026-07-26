"""Prove each validator concern loads without unrelated concern modules."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

CONCERN_CASES = {
    "skill_packages": ("validate_skill_packages", {"shared"}),
    "registry": ("validate_registry", {"shared", "skill_packages"}),
    "routing": ("validate_route_fixtures", {"shared"}),
    "onboarding": ("validate_onboarding_fixtures", {"shared"}),
    "planning": ("validate_planning_fixtures", {"shared"}),
    "behavior_proof": ("validate_behavior_proof_fixtures", {"shared"}),
    "merge_conflicts": ("validate_merge_conflict_fixtures", {"shared"}),
    "research": ("validate_knowledge_retrieval_fixtures", {"shared"}),
    "operations": ("validate_setup_scribe_fixtures", {"shared"}),
    "reporting": ("collect_fixture_counts", {"shared"}),
}


class ValidatorModuleIsolationTests(unittest.TestCase):
    """Exercise each concern in a fresh interpreter with explicit dependencies."""

    def test_each_concern_loads_without_unrelated_concerns(self) -> None:
        for module_name, (function_name, allowed_dependencies) in CONCERN_CASES.items():
            with self.subTest(module_name=module_name):
                allowed_modules = sorted({module_name, *allowed_dependencies})
                script = "\n".join(
                    [
                        "import importlib",
                        "import sys",
                        "from pathlib import Path",
                        (
                            "module = importlib.import_module("
                            f"'scripts.validation.{module_name}')"
                        ),
                        f"result = module.{function_name}(Path.cwd())",
                        (
                            "loaded = {name.rsplit('.', 1)[-1] "
                            "for name in sys.modules "
                            "if name.startswith('scripts.validation.')}"
                        ),
                        f"allowed = set({allowed_modules!r})",
                        "unexpected = sorted(loaded - allowed)",
                        "assert not unexpected, unexpected",
                    ]
                )

                result = subprocess.run(
                    [sys.executable, "-c", script],
                    cwd=REPO_ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
