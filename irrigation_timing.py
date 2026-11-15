"""Historical monthly rainfall and dry-day context for irrigation planning.

NASA POWER historical gridded data are not a forecast, soil-water balance,
root-zone moisture reading, crop evapotranspiration or irrigation schedule.
"""

from __future__ import annotations

import calendar
import math
import pandas as pd


def monthly_irrigation_context(daily_data, start_month, duration_months, years=range(2021, 2026)):
    """Summarize complete monthly windows across selected historical years.

    Months may wrap around December. Each year/month must have every date and
    nonmissing, nonnegative rainfall and finite temperature to be included.
    The dry-day cutoff (<1 mm/day) is a descriptive prototype threshold.
    """
    start_month = int(start_month)
    duration_months = int(duration_months)
    if not 1 <= start_month <= 12 or not 1 <= duration_months <= 6:
        raise ValueError("The starting month must be 1-12 and duration 1-6.")
    if not {"Temperature", "Precipitation"}.issubset(daily_data.columns):
        raise ValueError("Daily NASA POWER Temperature and Precipitation are required.")

    frame = daily_data[["Temperature", "Precipitation"]].copy()
    frame.index = pd.to_datetime(frame.index)
    frame = frame.sort_index()
    if frame.index.has_duplicates:
        raise ValueError("Duplicate daily dates in NASA data.")
    frame = frame.apply(pd.to_numeric, errors="coerce")
    output = []

    for offset in range(duration_months):
        month = ((start_month - 1 + offset) % 12) + 1
        year_offset = (start_month - 1 + offset) // 12
        records = []
        for season_year in years:
            year = int(season_year) + year_offset
            begin = pd.Timestamp(year, month, 1)
            end = begin + pd.DateOffset(months=1)
            block = frame.loc[(frame.index >= begin) & (frame.index < end)]
            days = (end - begin).days
            if (len(block) != days or block.index.normalize().nunique() != days
                or block.isna().any().any()
                or (block["Precipitation"] < 0).any()
                or not all(math.isfinite(float(t)) for t in block["Temperature"])):
                continue
            dry_share = float((block["Precipitation"] < 1.0).mean())
            records.append({
                "rainfall_mm": float(block["Precipitation"].sum()),
                "temperature_c": float(block["Temperature"].mean()),
                "dry_day_percent": dry_share * 100,
                "days": days,
            })
        if len(records) < 3:
            raise ValueError(f"Insufficient complete historical months for {calendar.month_name[month]} (need 3+ years).")

        rainfall = sum(rec["rainfall_mm"] for rec in records) / len(records)
        temp = sum(rec["temperature_c"] for rec in records) / len(records)
        dry = sum(rec["dry_day_percent"] for rec in records) / len(records)

        # Descriptive monitoring emphasis, NOT crop irrigation demand.
        if dry >= 80:
            attention = "Higher dry-day frequency"
        elif dry >= 60:
            attention = "Moderate dry-day frequency"
        else:
            attention = "Lower dry-day frequency"

        output.append({
            "month": calendar.month_abbr[month],
            "month_full": calendar.month_name[month],
            "month_number": month,
            "rainfall_mm": round(rainfall, 2),
            "temperature_c": round(temp, 2),
            "dry_day_percent": round(dry, 1),
            "attention": attention,
            "valid_years": len(records),
        })
    return output
