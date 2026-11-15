"""Field-input decision-support screening; NO pesticide/fertilizer dosing.

Rules below are transparent PROJECT-DEFINED DEMO FLAGS, not NASA advisories,
pathogen models, official thresholds, eligibility or verified agronomy rules.
"""
from dataclasses import dataclass
import math


def finite(value):
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True)
class GuidanceRow:
    name: str
    context: str
    status: str
    tone: str
    next_step: str


def evaluate(climate):
    """All comparisons use selected-farm NASA data; no missing->zero coercion.

    Inputs are recent NASA daily summaries, never a real-time forecast. Climate
    cues are illustrative priorities to inspect, not evidence of infection.
    """
    c = climate if isinstance(climate, dict) else {}
    rh = finite(c.get("humidity_7d_avg_pct"))
    temp = finite(c.get("temperature_max_7d_avg_c"))
    rain = finite(c.get("rainfall_7d_mm"))
    wind = finite(c.get("wind_7d_avg_ms"))
    if rh is not None and not 0 <= rh <= 100: rh = None
    if temp is not None and not -80 <= temp <= 65: temp = None
    if rain is not None and rain < 0: rain = None
    if wind is not None and wind < 0: wind = None

    # All flag cutoffs are *illustrative*, not validated pest or crop thresholds.
    warm = temp is not None and temp >= 28
    humid = rh is not None and rh >= 80
    wet = rain is not None and rain >= 20
    dry = rain is not None and rain < 5
    windy = wind is not None and wind >= 6

    if temp is None or rain is None:
        insect = GuidanceRow("🐛 Insect pest management", "Recent temperature or rainfall data unavailable.",
                             "Data missing", "neutral", "Scout the crop for actual pests. No insecticide dose can be calculated from climate data.")
    elif warm and dry:
        insect = GuidanceRow("🐛 Insect pest management", f"Warm/dry watch: 7-day mean Tmax {temp:.1f}°C; rain {rain:.1f} mm. These conditions alone do not establish pest pressure.",
                             "Field scouting priority", "yellow", "Inspect leaves/traps, identify the pest and compare field counts with a crop-specific economic action threshold before considering treatment.")
    else:
        insect = GuidanceRow("🐛 Insect pest management", f"No warm/dry demo flag: 7-day mean Tmax {temp:.1f}°C; rain {rain:.1f} mm.",
                             "Monitor in field", "green", "Continue routine field scouting; this result is not evidence that insects or insecticide use are absent.")

    if rh is None or rain is None:
        fungus = GuidanceRow("🍄 Fungal disease monitoring", "Recent humidity or rainfall data unavailable.",
                             "Data missing", "neutral", "Observe disease symptoms and leaf wetness; no fungicide amount can be inferred.")
    elif humid and wet:
        fungus = GuidanceRow("🍄 Fungal disease monitoring", f"Humid/wet screening flag: 7-day mean RH {rh:.0f}%; rain {rain:.1f} mm.",
                             "Inspect for symptoms", "yellow", "Look for crop-specific disease signs and seek local IPM advice; weather alone cannot diagnose fungal infection.")
    else:
        fungus = GuidanceRow("🍄 Fungal disease monitoring", f"No humid/wet combined flag: 7-day mean RH {rh:.0f}%; rain {rain:.1f} mm.",
                             "Routine monitoring", "green", "Continue checking crop health; a low demo flag does not exclude disease.")

    if rain is None:
        fertilizer = GuidanceRow("🌱 Organic nutrient inputs", "7-day precipitation unavailable; nutrient or runoff context cannot be screened.",
                                "Soil test needed", "neutral", "Obtain soil nutrient test, crop requirements and fertilizer nutrient analysis before deciding any amount.")
    elif wet:
        fertilizer = GuidanceRow("🌱 Organic nutrient inputs", f"Wet-week awareness: NASA grid rainfall {rain:.1f} mm / 7 days. Leaching/runoff depends on field conditions.",
                                "Check field conditions", "yellow", "Check drainage and upcoming local forecast before field operations. Use soil test and nutrient budget; application rate cannot be determined from weather alone.")
    else:
        fertilizer = GuidanceRow("🌱 Organic nutrient inputs", f"NASA grid rainfall {rain:.1f} mm / 7 days. No wet-week demo flag.",
                                "Soil test needed", "neutral", "Do not infer soil nitrogen or manure dose from rainfall. Verify approved input, crop nutrient demand and soil test.")

    if windy:
        spray = GuidanceRow("🌬️ Application drift awareness", f"7-day mean wind {wind:.1f} m/s is above illustrative 6 m/s screening flag (not spray-hour wind).",
                           "Check local conditions", "yellow", "Never use a weekly average to decide when to spray. Follow product label and measure wind onsite at application time.")
    elif wind is None:
        spray = GuidanceRow("🌬️ Application drift awareness", "Wind measurements unavailable.",
                           "Data missing", "neutral", "Check local wind and product label before any lawful application.")
    else:
        spray = GuidanceRow("🌬️ Application drift awareness", f"7-day mean wind {wind:.1f} m/s; not the wind at application time.",
                           "On-site check required", "neutral", "Onsite wind and product label still determine whether application is permissible.")

    # IPM and soil tests are never certified by the weather data.
    return [insect, fungus, fertilizer, spray]
