"""Release-level checks for representative V1/V2 instruction comparisons."""

from __future__ import annotations

import unittest

from scripts.compare_v1_v2_context import (
    MATERIAL_REDUCTION_PERCENT,
    compare_routes,
)


class ContextComparisonTests(unittest.TestCase):
    def test_all_required_routes_are_materially_smaller_than_v1(self) -> None:
        comparisons = compare_routes()

        self.assertEqual(4, len(comparisons))
        for comparison in comparisons:
            with self.subTest(comparison.identifier):
                self.assertGreaterEqual(
                    comparison.reduction_percent,
                    MATERIAL_REDUCTION_PERCENT,
                )


if __name__ == "__main__":
    unittest.main()
