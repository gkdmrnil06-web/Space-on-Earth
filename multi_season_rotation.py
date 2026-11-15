"""TerraShift: exploratory two-season crop-rotation screening.

Uses historical NASA POWER temperature data and FAO ECOCROP reference ranges.
Does not predict future weather, yields, irrigation requirements, or planting success.
"""

from __future__ import annotations

from itertools import permutations
from pathlib import Path
import calendar
import math

import pandas as pd


CROP_DATA = Path(__file__).with_name("crop_requirements.csv")


def load_crop_requirements(csv_path=None):
    """Read the existing FAO ECOCROP CSV; fail clearly if data is incomplete."""
    path = Path(csv_path) if csv_path else CROP_DATA
    crops = pd.read_csv(path).set_index("crop")
    required = (
        "crop_family", "optimal_temp_min_c", "optimal_temp_max_c",
        "absolute_temp_min_c", "absolute_temp_max_c",
        "optimal_ph_min", "optimal_ph_max", "absolute_ph_min", "absolute_ph_max",
    )
    for col in required:
        if col not in crops.columns or crops[col].isna().any():
            raise ValueError(f"Missing FAO crop requirement: {col}")
    return crops


def advance_month(start_month, months):
    """Return the start month of the next consecutive planting window."""
    return ((start_month - 1 + months) % 12) + 1


def _month_window(start_year, start_month, duration_months):
    """Actual date boundaries for a calendar window, including year rollover."""
    start = pd.Timestamp(start_year, start_month, 1)
    year = start_year + (start_month - 1 + duration_months) // 12
    month = ((start_month - 1 + duration_months) % 12) + 1
    end = pd.Timestamp(year, month, 1)
    return start, end


def historical_season_context(daily_data, start_month, duration_months, years=range(2021, 2026)):
    """Average complete historical season windows; never forecast future weather.

    Each year is weighted equally; partial windows and missing NASA days are excluded.
    """
    if start_month not in range(1, 13) or duration_months not in range(1, 13):
        raise ValueError("Season start must be 1-12 and duration must be 1-12 months.")
    if "Temperature" not in daily_data.columns or "Precipitation" not in daily_data.columns:
        raise ValueError("Expected NASA columns: Temperature and Precipitation")

    frame = daily_data.copy()
    frame.index = pd.to_datetime(frame.index)
    frame = frame.sort_index()
    observations = []
    for year in years:
        start, end = _month_window(year, start_month, duration_months)
        block = frame.loc[(frame.index >= start) & (frame.index < end)]
        expected_days = (end - start).days
        # A complete window requires every calendar day and both observed parameters.
        if (
            len(block) != expected_days
            or block.index.normalize().nunique() != expected_days
            or block[["Temperature", "Precipitation"]].isna().any().any()
        ):
            continue
        observations.append({
            "year": year,
            "temperature_c": float(block["Temperature"].mean()),
            "precipitation_mm": float(block["Precipitation"].sum()),
        })
    if len(observations) < 3:
        raise ValueError("Fewer than 3 complete historical season windows available.")
    return {
        "start_month": start_month,
        "duration_months": duration_months,
        "month_names": [calendar.month_abbr[(start_month - 1 + i) % 12 + 1] for i in range(duration_months)],
        "temperature_c": sum(x["temperature_c"] for x in observations) / len(observations),
        "precipitation_mm": sum(x["precipitation_mm"] for x in observations) / len(observations),
        "years_used": [x["year"] for x in observations],
        "years_requested": list(years),
    }


def _reference_match(value, optimal_min, optimal_max, absolute_min, absolute_max, max_points):
    """Illustrative, NOT calibrated, reference-range score."""
    values = [float(v) for v in (optimal_min, optimal_max, absolute_min, absolute_max)]
    o_min, o_max, a_min, a_max = values
    if o_min <= value <= o_max:
        return float(max_points), "within FAO optimal range"
    if a_min <= value <= a_max:
        return max_points / 2.0, "within FAO absolute range; outside optimal range"
    return 0.0, "outside FAO absolute range"


def _score_next_crop(crop_name, previous_name, crop_info, previous_info, climate, soil_ph):
    t_score, t_note = _reference_match(
        climate["temperature_c"],
        crop_info["optimal_temp_min_c"], crop_info["optimal_temp_max_c"],
        crop_info["absolute_temp_min_c"], crop_info["absolute_temp_max_c"],
        8.0,
    )
    ph_score = None
    ph_note = "pH not supplied; no pH contribution"
    if soil_ph is not None:
        if not 0 <= soil_ph <= 14:
            raise ValueError("Measured pH must be between 0 and 14")
        ph_score, ph_note = _reference_match(
            float(soil_ph),
            crop_info["optimal_ph_min"], crop_info["optimal_ph_max"],
            crop_info["absolute_ph_min"], crop_info["absolute_ph_max"],
            2.0,
        )
    family_change = str(crop_info["crop_family"]) != str(previous_info["crop_family"])
    rotation_points = 2.0 if family_change else 0.0
    # Also disallow consecutive repetition at the sequence generation stage.
    total = t_score + (ph_score or 0.0) + rotation_points
    return {
        "crop": crop_name,
        "score": round(total, 2),
        "temperature_score": t_score,
        "ph_score": ph_score,
        "rotation_score": rotation_points,
        "notes": [
            f"NASA historical mean for {', '.join(climate['month_names'])}: {climate['temperature_c']:.1f} C; temperature {t_note}",
            f"FAO optimal temperature: {crop_info['optimal_temp_min_c']:g}-{crop_info['optimal_temp_max_c']:g} C",
            f"Measured soil pH: {soil_ph}; {ph_note}" if soil_ph is not None else ph_note,
            f"Crop family change from {previous_name}: {'yes' if family_change else 'no'}",
            f"Historical precipitation: {climate['precipitation_mm']:.0f} mm; NOT compared with annual FAO rainfall ranges",
        ],
    }


def compare_two_seasons(previous_crop, start_month, months_per_season, daily_data,
                        soil_ph=None, csv_path=None, number_of_plans=3):
    """Rank exploratory two-step rotations for consecutive calendar windows.

    This ranks historical climate *screening* scenarios, not future crop predictions.
    Soil texture and real irrigation-water demand are intentionally not scored.
    """
    crops = load_crop_requirements(csv_path)
    if previous_crop not in crops.index:
        raise ValueError(f"Unknown previous crop: {previous_crop}")
    first = historical_season_context(daily_data, start_month, months_per_season)
    second_month = advance_month(start_month, months_per_season)
    second = historical_season_context(daily_data, second_month, months_per_season)
    plans = []
    candidates = [name for name in crops.index if name != previous_crop]
    for crop_1, crop_2 in permutations(candidates, 2):
        detail_1 = _score_next_crop(crop_1, previous_crop, crops.loc[crop_1], crops.loc[previous_crop], first, soil_ph)
        detail_2 = _score_next_crop(crop_2, crop_1, crops.loc[crop_2], crops.loc[crop_1], second, soil_ph)
        plans.append({
            "sequence": [previous_crop, crop_1, crop_2],
            "total_score": round(detail_1["score"] + detail_2["score"], 2),
            "season_1": detail_1,
            "season_2": detail_2,
        })
    plans.sort(key=lambda p: (-p["total_score"], p["sequence"]))
    return {
        "first_season_climate": first,
        "second_season_climate": second,
        "plans": plans[:number_of_plans],
        "limitations": (
            "Historical NASA POWER climate averages, not forecasts. FAO ECOCROP ranges are "
            "general references. Scoring weights are illustrative, not validated. "
            "Annual crop rainfall ranges do not represent irrigation needs or seasonal rainfall targets. "
            "No crop-variety, soil texture, actual planting calendar, pests, disease, nutrient "
            "management, yield or fallow-time evaluation. Not planting advice."
        ),
    }
