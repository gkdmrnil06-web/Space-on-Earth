"""Short-range weather forecasts and explicitly non-predictive crop-calendar screening."""
from datetime import date, timedelta
from functools import lru_cache
import calendar
import math
from pathlib import Path
import pandas as pd
import requests

FORECAST_API = 'https://api.open-meteo.com/v1/forecast'
CROP_FILE = Path(__file__).with_name('crop_requirements.csv')


def get_16_day_forecast(lat, lon, timeout=15):
    """Free for non-commercial use. Never silently replace forecasts with history."""
    response = requests.get(FORECAST_API, params={
        'latitude': float(lat), 'longitude': float(lon),
        'daily': 'precipitation_sum,precipitation_probability_max,temperature_2m_max,temperature_2m_min,et0_fao_evapotranspiration',
        'timezone': 'auto', 'forecast_days': 16,
    }, timeout=timeout)
    response.raise_for_status()
    data = response.json().get('daily', {})
    mapping = {'time': 'Date', 'precipitation_sum': 'Rain (mm)',
               'precipitation_probability_max': 'Rain chance (%)',
               'temperature_2m_max': 'Max temp (C)',
               'temperature_2m_min': 'Min temp (C)',
               'et0_fao_evapotranspiration': 'Reference ET0 (mm)'}
    if any(k not in data for k in mapping):
        raise ValueError('Forecast response is missing expected daily measurements.')
    frame = pd.DataFrame({new: data[old] for old, new in mapping.items()})
    frame['Date'] = pd.to_datetime(frame['Date'])
    for key in list(mapping.values())[1:]:
        frame[key] = pd.to_numeric(frame[key], errors='coerce')
    return frame


def screening_months(daily, crop, from_date=None):
    """Candidate *months* by historical temperature only, NOT planting recommendations."""
    if daily is None or crop is None:
        return []
    crops = pd.read_csv(CROP_FILE).set_index('crop')
    if crop not in crops.index:
        return []
    row = crops.loc[crop]
    frame = daily.loc[(daily.index.year >= 2021) & (daily.index.year <= 2025)]
    grouped = frame.groupby(frame.index.month)['Temperature'].agg(['mean', 'count'])
    start = from_date or date.today()
    candidates = []
    for i in range(12):
        year = start.year + (start.month - 1 + i) // 12
        month = (start.month - 1 + i) % 12 + 1
        if month not in grouped.index or int(grouped.loc[month, 'count']) < 100:
            continue
        avg = float(grouped.loc[month, 'mean'])
        if math.isfinite(avg) and float(row['optimal_temp_min_c']) <= avg <= float(row['optimal_temp_max_c']):
            candidates.append({'year': year, 'month': month, 'historical_temp_c': round(avg, 1),
                               'label': f'{calendar.month_name[month]} {year}'})
    return candidates


@lru_cache(maxsize=1)
def _crop_cycles():
    return pd.read_csv(CROP_FILE).set_index('crop')


def crop_cycle_window(crop, sowing_date):
    """FAO ECOCROP broad species ranges, not exact harvest dates."""
    if not crop or not sowing_date:
        return None
    crops = _crop_cycles()
    if crop not in crops.index:
        return None
    row = crops.loc[crop]
    minimum = pd.to_numeric(row['crop_cycle_min_days'], errors='coerce')
    maximum = pd.to_numeric(row['crop_cycle_max_days'], errors='coerce')
    if not (pd.notna(minimum) and pd.notna(maximum) and 0 < minimum <= maximum):
        return None
    return {'earliest': sowing_date + timedelta(days=int(minimum)),
            'latest': sowing_date + timedelta(days=int(maximum))}


def forecast_monitoring_table(forecast):
    """Informational monitoring labels. Not irrigation volume/timing decisions."""
    output = forecast.copy()
    def label(row):
        rain = row['Rain (mm)']
        prob = row['Rain chance (%)']
        if pd.isna(rain) or pd.isna(prob):
            return 'Check local conditions'
        if rain >= 5 or prob >= 65:
            return 'Rain possible — check forecast before watering'
        return 'Check soil moisture before deciding to irrigate'
    output['Field check'] = output.apply(label, axis=1)
    return output


def candidate_harvest_window(crop, candidate_months, from_date=None):
    """Conditional date range: first historically temperature-screened sowing month.

    Start of candidate month + crop minimum growing days, through end of
    candidate month + crop maximum growing days. No future NASA weather data
    or variety/soil/management effects are assumed. Returns None if unknown.
    """
    if not candidate_months:
        return None
    first = candidate_months[0]
    try:
        year, month = int(first['year']), int(first['month'])
        if not 1 <= month <= 12:
            return None
        sow_first = max(date(year, month, 1), from_date or date.today())
        sow_last = date(year, month, calendar.monthrange(year, month)[1])
        if sow_first > sow_last:
            return None
    except (ValueError, KeyError, TypeError, OverflowError):
        return None
    lower = crop_cycle_window(crop, sow_first)
    upper = crop_cycle_window(crop, sow_last)
    if lower is None or upper is None:
        return None
    return {'sow_first': sow_first, 'sow_last': sow_last,
            'earliest': lower['earliest'], 'latest': upper['latest'],
            'mean_sowing_temp_c': first.get('historical_temp_c'),
            'basis': 'NASA historical sowing-month temperature (2021–2025) + FAO ECOCROP crop-cycle range'}
