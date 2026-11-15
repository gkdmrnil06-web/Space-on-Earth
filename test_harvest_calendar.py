"""Regression tests for coordinate-dependent conditional harvest calendar."""
import unittest
from datetime import date, timedelta
import pandas as pd
from farmer_forecast import screening_months, candidate_harvest_window, crop_cycle_window

class HarvestCalendarTests(unittest.TestCase):
    @staticmethod
    def climate(cold_months, warm=24, cool=10):
        dates = pd.date_range('2021-01-01', '2025-12-31', freq='D')
        temps = [cool if d.month in cold_months else warm for d in dates]
        return pd.DataFrame({'Temperature': temps, 'Precipitation': 1.0}, index=dates)

    def test_candidate_drives_interval_and_includes_full_sowing_month(self):
        candidates = screening_months(self.climate({1, 2, 3}), 'Tomato', date(2026, 11, 13))
        win = candidate_harvest_window('Tomato', candidates, from_date=date(2026, 11, 13))
        self.assertEqual(win['sow_first'], date(2026, 11, 13))
        self.assertEqual(win['sow_last'], date(2026, 11, 30))
        self.assertEqual(win['earliest'], date(2026, 11, 13) + timedelta(days=135))
        self.assertEqual(win['latest'], date(2026, 11, 30) + timedelta(days=180))

    def test_distinct_climates_yield_distinct_windows(self):
        # Where November is warm vs cold, first acceptable candidate changes.
        hot_nov = screening_months(self.climate({1, 2, 3}), 'Tomato', date(2026, 11, 13))
        cold_nov = screening_months(self.climate({1, 2, 3, 11, 12}), 'Tomato', date(2026, 11, 13))
        self.assertNotEqual(candidate_harvest_window('Tomato', hot_nov, from_date=date(2026,11,13))['sow_first'],
                            candidate_harvest_window('Tomato', cold_nov, from_date=date(2026,11,13))['sow_first'])

    def test_no_data_yields_no_dates(self):
        self.assertIsNone(candidate_harvest_window('Tomato', []))
        self.assertIsNone(candidate_harvest_window('Unknown', [{'year': 2027, 'month': 3}]))
        self.assertIsNone(candidate_harvest_window('Tomato', [{'year': 2027, 'month': 13}]))

    def test_all_crops_have_valid_cycles(self):
        from farmer_forecast import _crop_cycles
        for crop in _crop_cycles().index:
            win = crop_cycle_window(crop, date(2027, 1, 1))
            self.assertIsNotNone(win, crop)
            self.assertGreaterEqual(win['latest'], win['earliest'])

if __name__ == '__main__':
    unittest.main()
