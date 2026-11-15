"""Mocked NASA response tests: same place vs different place; no external calls."""
import importlib
import sys
import types
import unittest
from datetime import date, timedelta
from unittest.mock import patch

import pandas as pd

# Streamlit not needed for the data integration unit test.
if "streamlit" not in sys.modules:
    st = types.ModuleType('streamlit')
    st.cache_data = lambda **kwargs: lambda func: func
    sys.modules['streamlit'] = st
import nasa_conditions as nc


def payload(lat, lon):
    days = [(date.today() - timedelta(days=i)).strftime('%Y%m%d') for i in range(1, 32)]
    wet = float(lat) < 0
    rain = 8.0 if wet else 0.1
    rh = 90.0 if wet else 40.0
    t = 25.0 if wet else 35.0
    data = {
        'T2M_MAX': {d: t for d in days},
        'RH2M': {d: rh for d in days},
        'WS10M': {d: 2.0 for d in days},
        'PRECTOTCORR': {d: rain for d in days},
    }
    return {'properties': {'parameter': data}}


class DummyResponse:
    def __init__(self, data): self.data = data
    def raise_for_status(self): pass
    def json(self): return self.data


class InputWeatherIntegrationTests(unittest.TestCase):
    def test_selected_coordinates_and_no_new_request(self):
        calls = []
        def request(url, params, timeout):
            calls.append((params['latitude'], params['longitude'], tuple(params['parameters'].split(','))))
            if params['community'] == 'HY':
                return DummyResponse({'properties': {'parameter': {'SFMC': {}}}})
            return DummyResponse(payload(params['latitude'], params['longitude']))
        with patch.object(nc.requests, 'get', request):
            a = nc.get_nasa_conditions(-1.286, 36.817)
            b = nc.get_nasa_conditions(38.466, 27.221)
        self.assertEqual(len(calls), 10)  # Four soil fallbacks plus one weather call per location
        self.assertTrue(all(item[:2] == (-1.286, 36.817) for item in calls[:5]))
        self.assertTrue(all(item[:2] == (38.466, 27.221) for item in calls[5:]))
        self.assertEqual(a['input_weather']['rainfall_7d_mm'], 56.0)
        self.assertAlmostEqual(b['input_weather']['rainfall_7d_mm'], 0.7)
        from input_guidance_logic import evaluate
        self.assertNotEqual([r.status for r in evaluate(a['input_weather'])],
                            [r.status for r in evaluate(b['input_weather'])])

    def test_incomplete_day_cannot_be_treated_as_zero_rain(self):
        data = payload(-1, 36)
        latest = (date.today() - timedelta(days=2)).strftime('%Y%m%d')
        data['properties']['parameter']['PRECTOTCORR'][latest] = -999
        def request(url, params, timeout):
            if params['community'] == 'HY':
                return DummyResponse({'properties': {'parameter': {'SFMC': {}}}})
            return DummyResponse(data)
        with patch.object(nc.requests, 'get', request):
            x = nc.get_nasa_conditions(-1, 36)['input_weather']
        self.assertIsNone(x['rainfall_7d_mm'])
        self.assertEqual(x['humidity_7d_avg_pct'], 90)


if __name__ == '__main__': unittest.main()
