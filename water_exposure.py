"""Historical seasonal precipitation exposure from NASA POWER daily records.

Not a water-balance model: no evapotranspiration, soil moisture, irrigation,
crop-specific water requirement, drought diagnosis, or future forecast.
"""

from __future__ import annotations

import calendar
import math

import pandas as pd


def season_rainfall_series(daily_data, start_month, duration_months, years=range(2001, 2026)):
    """Return annual totals for complete, non-overlapping historical month windows.

    A season starting in December can end the following year; incomplete windows
    are skipped. No partial annual precipitation sums are silently admitted.
    """
    if not 1 <= int(start_month) <= 12 or not 1 <= int(duration_months) <= 12:
        raise ValueError("Season month and duration must be between 1 and 12.")
    if "Precipitation" not in daily_data.columns:
        raise ValueError("NASA daily data must include a Precipitation column.")

    frame = daily_data.copy()
    frame.index = pd.to_datetime(frame.index)
    frame = frame.sort_index()
    if frame.index.has_duplicates:
        raise ValueError("NASA daily climate data contains duplicate dates.")
    frame["Precipitation"] = pd.to_numeric(frame["Precipitation"], errors="coerce")

    rows = []
    for year in years:
        first = pd.Timestamp(year=int(year), month=int(start_month), day=1)
        last = first + pd.DateOffset(months=int(duration_months))
        window = frame.loc[(frame.index >= first) & (frame.index < last), "Precipitation"]
        expected_days = (last - first).days
        if (
            len(window) != expected_days
            or window.isna().any()
            or (window < 0).any()
            or window.index.normalize().nunique() != expected_days
        ):
            continue
        rows.append({"Year": int(year), "Precipitation": float(window.sum())})
    return pd.DataFrame(rows, columns=["Year", "Precipitation"])


def calculate_water_exposure(daily_data, start_month, duration_months):
    """Compare recent (2021-25) rainfall with same-calendar 2001-20 baseline.

    Labels describe *relative rainfall only*, not crop water supply sufficiency.
    """
    windows = []
    for index in range(2):
        month = ((int(start_month) - 1 + index * int(duration_months)) % 12) + 1
        series = season_rainfall_series(daily_data, month, duration_months)
        base = series.loc[series["Year"].between(2001, 2020), "Precipitation"]
        recent = series.loc[series["Year"].between(2021, 2025), "Precipitation"]
        if len(base) < 15 or len(recent) < 3:
            raise ValueError(
                f"Insufficient complete precipitation windows for Season {index + 1} "
                "(requires at least 15 reference and 3 recent years)."
            )
        baseline_mean = float(base.mean())
        recent_mean = float(recent.mean())
        if not (math.isfinite(baseline_mean) and baseline_mean > 0 and math.isfinite(recent_mean)):
            raise ValueError("Historical precipitation reference is missing or zero.")
        ratio = recent_mean / baseline_mean
        if ratio < 0.8:
            label = "Lower than historical reference"
        elif ratio > 1.2:
            label = "Higher than historical reference"
        else:
            label = "Near historical reference"
        windows.append({
            "season_number": index + 1,
            "start_month": month,
            "month_names": [calendar.month_abbr[(month - 1 + k) % 12 + 1] for k in range(duration_months)],
            "baseline_mean_mm": baseline_mean,
            "recent_mean_mm": recent_mean,
            "difference_mm": recent_mean - baseline_mean,
            "difference_pct": (ratio - 1) * 100,
            "relative_index": ratio,
            "label": label,
            "baseline_years": base.index.size,
            "recent_years": recent.index.size,
            "series": series,
        })
    return windows
