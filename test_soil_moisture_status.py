"""Offline test of NASA POWER soil moisture availability and status labeling."""
import sys
import types
import unittest
from datetime import date, timedelta
from unittest.mock import patch

# Minimal stub for CI without Streamlit installed.
try:
    import streamlit
except ImportError:
    stub = types.ModuleType("streamlit")
    stub.cache_data = lambda *args, **kwargs: (lambda fn: fn)
    sys.modules["streamlit"] = stub

import requests
import nasa_conditions as nc

class SoilMoistureStatusTests(unittest.TestCase):
    def run_case(self, age, value=0.23, fail=None):
        if fail:
            def mock_daily(*args, **kwargs):
                if args[2] == 'HY':
                    raise fail
                return {}
        else:
            day = date.today() - timedelta(days=age)
            def mock_daily(*args, **kwargs):
                if args[2] == 'HY':
                    self.assertEqual(kwargs['lookback_days'], 180)
                    return {"SFMC": {day.strftime('%Y%m%d'): value}}
                return {}
        with patch.object(nc, '_daily', side_effect=mock_daily):
            return nc.get_nasa_conditions(-17.057, -64.991)

    def test_recent(self):
        r = self.run_case(3)
        self.assertEqual(r['moisture_status'], 'recent')
        self.assertAlmostEqual(r['moisture']['volumetric_pct'], 23)
        self.assertFalse(r['moisture']['is_historical'])

    def test_historical_not_hidden(self):
        r = self.run_case(39)
        self.assertEqual(r['moisture_status'], 'historical')
        self.assertEqual(r['moisture']['age_days'], 39)
        self.assertTrue(r['moisture']['is_historical'])

    def test_missing(self):
        r = self.run_case(4, -999)
        self.assertIsNone(r['moisture'])
        self.assertEqual(r['moisture_status'], 'missing')

    def test_outside_physical_range(self):
        r = self.run_case(4, 1.4)
        self.assertIsNone(r['moisture'])
        self.assertEqual(r['moisture_status'], 'missing')

    def test_network_error(self):
        r = self.run_case(4, fail=requests.ConnectionError('No connection'))
        self.assertEqual(r['moisture_status'], 'network_error')
        self.assertIsNone(r['moisture'])

if __name__ == '__main__':
    unittest.main()
