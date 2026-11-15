"""Deterministic tests for site-dependent input guidance; no network needed."""
import unittest
from input_guidance_logic import evaluate


class GuidanceTests(unittest.TestCase):
    def test_different_climates_different_flags(self):
        a = evaluate({"humidity_7d_avg_pct": 88, "rainfall_7d_mm": 43,
                      "temperature_max_7d_avg_c": 24, "wind_7d_avg_ms": 2})
        b = evaluate({"humidity_7d_avg_pct": 42, "rainfall_7d_mm": 1,
                      "temperature_max_7d_avg_c": 35, "wind_7d_avg_ms": 9})
        self.assertNotEqual([x.status for x in a], [x.status for x in b])
        self.assertEqual(a[1].status, "Inspect for symptoms")
        self.assertEqual(b[0].status, "Field scouting priority")
        self.assertEqual(a[2].status, "Check field conditions")

    def test_missing_never_becomes_safe(self):
        rows = evaluate({})
        self.assertEqual(rows[0].status, "Data missing")
        self.assertEqual(rows[1].status, "Data missing")
        self.assertEqual(rows[2].status, "Soil test needed")

    def test_no_dose_or_organic_claim(self):
        for climate in ({}, {"humidity_7d_avg_pct": 90,"rainfall_7d_mm": 30,
                           "temperature_max_7d_avg_c": 30,"wind_7d_avg_ms": 8}):
            text = " ".join((row.context + ' ' + row.next_step) for row in evaluate(climate)).lower()
            self.assertNotIn('1.5 ml', text)
            self.assertNotIn('kg/decare', text)
            self.assertNotIn('certified organic', text)


if __name__ == '__main__':
    unittest.main()
