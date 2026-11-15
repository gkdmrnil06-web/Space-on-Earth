"""Explainable NASA + FAO ECOCROP crop screening prototype.

Not planting advice. FAO ECOCROP temperature ranges are general species-level
ranges, not validated local/variety-specific yield models. The FAO annual
rainfall thresholds MUST NOT be applied to seasonal rainfall totals.
"""
from pathlib import Path
from functools import lru_cache
import math
import pandas as pd

CSV_PATH = Path(__file__).resolve().parent / "crop_requirements.csv"

# Demo heuristics, separate from FAO-sourced temperature requirements.
CROPS = {
    "Maize": {"family": "cereal", "water": "high", "soils": ["Loamy", "Clay"]},
    "Wheat": {"family": "cereal", "water": "medium", "soils": ["Loamy", "Clay"]},
    "Beans": {"family": "legume", "water": "medium", "soils": ["Loamy", "Sandy"]},
    "Sorghum": {"family": "cereal", "water": "low", "soils": ["Loamy", "Sandy"]},
    "Rice": {"family": "cereal", "water": "high", "soils": ["Clay", "Loamy"]},
    "Potato": {"family": "solanaceae", "water": "medium", "soils": ["Loamy", "Sandy"]},
    "Sunflower": {"family": "oilseed", "water": "medium", "soils": ["Loamy", "Clay"]},
    "Tomato": {"family": "solanaceae", "water": "medium", "soils": ["Loamy", "Sandy"]},
    "Chickpea": {"family": "legume", "water": "low", "soils": ["Loamy", "Sandy"]},
    "Barley": {"family": "cereal", "water": "medium", "soils": ["Loamy", "Clay"]},
    "Soybean": {"family": "legume", "water": "medium", "soils": ["Loamy", "Clay"]},
    "Lentil": {"family": "legume", "water": "low", "soils": ["Loamy", "Sandy"]},
    "Groundnut": {"family": "legume", "water": "medium", "soils": ["Loamy", "Sandy"]},
}


# USDA NRCS mineral-soil texture classes. The original three crop-soil
# compatibility flags are prototype heuristics, not measured soil suitability.
SOIL_TEXTURES = ['Sand', 'Loamy sand', 'Sandy loam', 'Loam', 'Silt loam', 'Silt', 'Sandy clay loam', 'Clay loam', 'Silty clay loam', 'Sandy clay', 'Silty clay', 'Clay']
SOIL_OPTIONS = ["Unknown / Not tested"] + SOIL_TEXTURES
SOIL_ALIASES = {"Loamy": "Loam", "Sandy": "Sand"}

@lru_cache(maxsize=1)
def _load_requirements():
    """Load FAO data from the CSV next to this module."""
    data = pd.read_csv(CSV_PATH).set_index("crop")
    required = (
        "optimal_temp_min_c", "optimal_temp_max_c",
        "absolute_temp_min_c", "absolute_temp_max_c"
    )
    for crop in CROPS:
        if crop not in data.index:
            raise ValueError(f"Missing FAO record for {crop}.")
        if data.loc[crop, list(required)].isna().any():
            raise ValueError(f"Missing temperature requirements for {crop}.")
    return data


def _temperature_score(value, optimal_min, optimal_max, absolute_min, absolute_max):
    """Exploratory 0-4 score: optimal=4, declining toward absolute limits."""
    if value is None or not math.isfinite(float(value)):
        return None
    value = float(value)
    if optimal_min <= value <= optimal_max:
        return 4.0
    if value <= absolute_min or value >= absolute_max:
        return 0.0
    if value < optimal_min:
        return 4 * (value - absolute_min) / (optimal_min - absolute_min)
    return 4 * (absolute_max - value) / (absolute_max - optimal_max)


def _midpoint_demo_score(value, optimal_min, optimal_max, absolute_min, absolute_max):
    """Exploratory continuous 0-4 proximity score, NOT a FAO yield model.

    FAO gives broad ranges, not within-range probabilities. The small midpoint
    preference is only a transparent demonstration tie-breaker.
    """
    if value is None or not math.isfinite(float(value)):
        return None
    value = float(value)
    lo, hi = float(optimal_min), float(optimal_max)
    low_abs, high_abs = float(absolute_min), float(absolute_max)
    if lo <= value <= hi:
        midpoint = (lo + hi) / 2
        halfwidth = max((hi - lo) / 2, 1e-6)
        return round(4.0 - abs(value - midpoint) / halfwidth, 2)
    if value < lo:
        return round(3 * max(0.0, min(1.0, (value - low_abs) / max(lo - low_abs, 1e-6))), 2)
    return round(3 * max(0.0, min(1.0, (high_abs - value) / max(high_abs - hi, 1e-6))), 2)


def recent_annual_rainfall(annual):
    """NASA 2021-25 annual rain average, complete years only; None if sparse."""
    if annual is None or 'Precipitation' not in annual.columns:
        return None
    recent = pd.to_numeric(annual.loc[2021:2025, 'Precipitation'], errors='coerce').dropna()
    return float(recent.mean()) if len(recent) >= 4 else None


def score_crop(name, previous, soil, priority, seasonal, soil_ph=None, annual_rainfall_mm=None):
    """Rank a crop using FAO temperature limits plus labeled demo heuristics."""
    if name not in CROPS or previous not in CROPS:
        raise ValueError("Unsupported crop.")
    soil = SOIL_ALIASES.get(soil, soil)
    if soil not in SOIL_OPTIONS:
        raise ValueError("Unsupported soil type.")
    if priority not in ("Water conservation", "Soil health"):
        raise ValueError("Unsupported priority.")

    crop = CROPS[name]
    previous_family = CROPS[previous]["family"]
    temperature = seasonal.get("recent_temperature")
    rainfall = seasonal.get("recent_precipitation")
    if temperature is None or not math.isfinite(float(temperature)):
        raise ValueError("NASA seasonal temperature is missing or invalid.")

    requirements = _load_requirements().loc[name]
    climate_score = _midpoint_demo_score(
        temperature,
        requirements["optimal_temp_min_c"], requirements["optimal_temp_max_c"],
        requirements["absolute_temp_min_c"], requirements["absolute_temp_max_c"]
    )
    # ECOCROP rainfall limits are ANNUAL; compare only to complete NASA
    # ANNUAL rainfall totals, never to seasonal precipitation.
    rain_score = _midpoint_demo_score(
        annual_rainfall_mm,
        requirements['optimal_annual_rain_min_mm'], requirements['optimal_annual_rain_max_mm'],
        requirements['absolute_annual_rain_min_mm'], requirements['absolute_annual_rain_max_mm'],
    )
    # Existing coarse crop-soil preferences are demo heuristics only.
    # Do not invent compatibility for the nine new texture classes.
    # Unknown/new textures receive a neutral contribution, not a penalty.
    original_soil = {"Loam": "Loamy", "Sand": "Sandy", "Clay": "Clay"}.get(soil)
    soil_score = (2 if original_soil in crop["soils"] else 0) if original_soil else 1

    # Optional measured soil pH: FAO range, demonstration scoring function.
    ph_score = None
    if soil_ph is not None:
        if not 0 <= float(soil_ph) <= 14 or not math.isfinite(float(soil_ph)):
            raise ValueError("Soil pH must be a finite value between 0 and 14.")
        ph_score = round(_temperature_score(
            float(soil_ph),
            requirements["optimal_ph_min"], requirements["optimal_ph_max"],
            requirements["absolute_ph_min"], requirements["absolute_ph_max"]
        ) / 2, 2)
    rotation_score = 0 if crop["family"] == "perennial" else (0 if name == previous else (3 if crop["family"] != previous_family else 1))
    if crop["family"] == "perennial":
        preference_score = 0  # Orchard crops are not annual rotation recommendations.
    elif priority == "Water conservation":
        preference_score = {"low": 3, "medium": 1.5, "high": 0}[crop["water"]]
    else:
        preference_score = 3 if crop["family"] == "legume" and previous_family != "legume" else 0.5

    total = round(2 * climate_score + (1.5 * rain_score if rain_score is not None else 0)
                  + soil_score + rotation_score + preference_score + (ph_score or 0), 2)
    rainfall_text = f"{float(rainfall):.0f} mm" if rainfall is not None and math.isfinite(float(rainfall)) else "unavailable"
    reasons = [
        f"NASA selected-season temperature: {float(temperature):.1f} C; FAO ECOCROP optimal range {requirements['optimal_temp_min_c']:g}-{requirements['optimal_temp_max_c']:g} C. Demo midpoint proximity {climate_score:.2f}/4; not a planting probability.",
        (f"NASA 2021-2025 complete-year mean annual rainfall: {annual_rainfall_mm:.0f} mm; FAO ECOCROP optimal ANNUAL range {requirements['optimal_annual_rain_min_mm']:g}-{requirements['optimal_annual_rain_max_mm']:g} mm; demo rainfall proximity {rain_score:.2f}/4. This does NOT estimate crop water need or irrigation." if rain_score is not None else "Annual rainfall score unavailable: not enough complete NASA annual data."),
        f"NASA selected-season precipitation: {rainfall_text}; not compared with FAO annual rainfall requirements (different time scales).",
        f"Farmer-reported soil texture: {soil}. Demonstration-only soil contribution {soil_score}/2; neutral for unvalidated texture classes (not a soil test or FAO crop-soil suitability).",
        f"Crop family rotation heuristic: {rotation_score}/3; actual disease and nutrient effects require local agronomic assessment.",
        f"{priority} preference: demonstration-only contribution {preference_score:.1f} points.",
    ]
    if crop["family"] == "perennial":
        reasons.append("Perennial orchard screening only: annual crop rotation and seasonal sowing/harvest logic do not apply. Winter chill, frost, drainage and orchard establishment are not evaluated.")
    if soil_ph is None:
        reasons.append("Measured soil pH was not provided; pH is excluded from scoring.")
    else:
        reasons.append(
            f"Farmer-provided soil pH: {float(soil_ph):.1f}; FAO ECOCROP optimal pH "
            f"{requirements['optimal_ph_min']:g}-{requirements['optimal_ph_max']:g}, "
            f"absolute pH {requirements['absolute_ph_min']:g}-{requirements['absolute_ph_max']:g}. "
            f"Exploratory pH match: {ph_score:.1f}/2 (not a soil laboratory assessment)."
        )
    if str(requirements["source"]) != "FAO ECOCROP":
        reasons.append("Crop thresholds are provisional prototype assumptions, NOT verified FAO ECOCROP values.")
    return {
        "perennial": crop["family"] == "perennial",
        "ph_score": ph_score, "rain_score": rain_score, "annual_rainfall_mm": annual_rainfall_mm,
        "crop": name, "score": total, "climate_score": climate_score, "local_temperature_c": float(temperature),
        "soil_score": soil_score, "rotation_score": rotation_score,
        "preference_score": preference_score, "reasons": reasons,
    }


def compare_strategies(previous_crop, soil_type, seasonal, soil_ph=None, annual_rainfall_mm=None):
    """Preserve the app.py interface and both strategy names."""
    if previous_crop not in CROPS or SOIL_ALIASES.get(soil_type, soil_type) not in SOIL_OPTIONS:
        raise ValueError("Unsupported crop or soil type.")
    results = {}
    for priority in ("Water conservation", "Soil health"):
        results[priority] = sorted(
            [score_crop(name, previous_crop, soil_type, priority, seasonal, soil_ph=soil_ph,
                        annual_rainfall_mm=annual_rainfall_mm)
             for name in CROPS if name != previous_crop],
            key=lambda row: (-row["score"], row["crop"]),
        )
    return results
