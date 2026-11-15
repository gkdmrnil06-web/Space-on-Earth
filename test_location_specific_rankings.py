"""Offline regression tests: run python test_location_specific_rankings.py"""
import pandas as pd
from crop_rotation import compare_strategies, recent_annual_rainfall

def test_distinct_climates():
    annual_a = pd.DataFrame({'Precipitation': [500, 600, 580, 550, 620]}, index=[2021,2022,2023,2024,2025])
    annual_b = pd.DataFrame({'Precipitation': [1300, 1500, 1600, 1450, 1400]}, index=[2021,2022,2023,2024,2025])
    rain_a = recent_annual_rainfall(annual_a)
    rain_b = recent_annual_rainfall(annual_b)
    kwargs = dict(previous_crop='Maize', soil_type='Loam', soil_ph=None)
    a = compare_strategies(**kwargs, seasonal={'recent_temperature': 19.0, 'recent_precipitation': 220}, annual_rainfall_mm=rain_a)
    b = compare_strategies(**kwargs, seasonal={'recent_temperature': 29.0, 'recent_precipitation': 460}, annual_rainfall_mm=rain_b)
    sa = {x['crop']: x['score'] for x in a['Water conservation']}
    sb = {x['crop']: x['score'] for x in b['Water conservation']}
    assert sa != sb, 'Different local climates should not have identical full score sets'
    assert all(x['rain_score'] is not None for x in a['Water conservation'])
    assert a['Water conservation'][0]['local_temperature_c'] == 19.0
    assert b['Water conservation'][0]['local_temperature_c'] == 29.0
    print('PASS: two distinct location climates -> distinct score sets')
    print('Example A:', [(x['crop'], x['score']) for x in a['Water conservation'][:4]])
    print('Example B:', [(x['crop'], x['score']) for x in b['Water conservation'][:4]])

def test_no_rain_data():
    annual = pd.DataFrame({'Precipitation':[None, 500, None, None, 900]}, index=[2021,2022,2023,2024,2025])
    assert recent_annual_rainfall(annual) is None
    a = compare_strategies('Maize', 'Loam', {'recent_temperature':20.0}, annual_rainfall_mm=None)
    assert all(x['rain_score'] is None for x in a['Water conservation'])
    print('PASS: missing annual rainfall stays missing, no invented value')

if __name__ == '__main__':
    test_distinct_climates()
    test_no_rain_data()
