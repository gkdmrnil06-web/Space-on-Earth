"""Optional, non-operational SoilGrids point lookup for research prototypes.

ISRIC's SoilGrids REST API is currently paused (checked November 2026).
This module fails safely: no soil values are invented or substituted.
SoilGrids estimates must not be treated as field measurements.
"""

from __future__ import annotations

from typing import Any
import requests

SOILGRIDS_URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"
SOURCE_NAME = "ISRIC SoilGrids 2.0 (model estimate, not a field measurement)"
DEPTH = "0-5cm"
PROPERTIES = ("phh2o", "clay", "sand", "soc")


class SoilDataUnavailable(Exception):
    """Soil estimates could not be retrieved or interpreted safely."""


def parse_soilgrids_response(payload: dict[str, Any]) -> dict[str, Any]:
    """Extract selected modelled 0-5 cm mean values from SoilGrids JSON.

    SoilGrids API scale factors: pH / 10; clay, sand and SOC (g/kg) / 10.
    Clay and sand are returned here as mass percentages; SOC as g/kg.
    """
    layers = payload.get("properties", {}).get("layers", [])
    if not isinstance(layers, list):
        raise SoilDataUnavailable("Unexpected SoilGrids response structure.")

    result = {
        "source": SOURCE_NAME,
        "depth_cm": "0-5",
        "soil_ph": None,
        "clay_percent": None,
        "sand_percent": None,
        "organic_carbon_g_kg": None,
        "data_type": "model_estimate",
    }
    mapping = {
        "phh2o": ("soil_ph", 10),
        "clay": ("clay_percent", 10),
        "sand": ("sand_percent", 10),
        "soc": ("organic_carbon_g_kg", 10),
    }
    for layer in layers:
        name = layer.get("name")
        if name not in mapping:
            continue
        depth = next((d for d in layer.get("depths", [])
                      if d.get("label") == DEPTH), None)
        if not depth:
            continue
        value = depth.get("values", {}).get("mean")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            key, scale = mapping[name]
            result[key] = round(value / scale, 2)

    if all(result[k] is None for k, _ in mapping.values()):
        raise SoilDataUnavailable("No valid soil property values were returned.")
    if result["soil_ph"] is not None and not 0 <= result["soil_ph"] <= 14:
        raise SoilDataUnavailable("The estimated pH is outside the valid scale.")
    for field in ("clay_percent", "sand_percent"):
        if result[field] is not None and not 0 <= result[field] <= 100:
            raise SoilDataUnavailable("Invalid soil texture fraction received.")
    return result


def get_soil_data(latitude: float, longitude: float, timeout: int = 12) -> dict[str, Any]:
    """Query the selected coordinate if the experimental API is available.

    Does not infer a soil type from country and does not replace user measurements.
    """
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        raise ValueError("Invalid latitude or longitude.")
    params = [("lat", round(latitude, 5)), ("lon", round(longitude, 5))]
    params += [("property", prop) for prop in PROPERTIES]
    params += [("depth", DEPTH), ("value", "mean")]
    try:
        response = requests.get(SOILGRIDS_URL, params=params, timeout=timeout)
        response.raise_for_status()
        parsed = parse_soilgrids_response(response.json())
    except (requests.RequestException, ValueError, TypeError, KeyError, SoilDataUnavailable) as exc:
        raise SoilDataUnavailable(
            "SoilGrids data is currently unavailable. No soil properties were assumed. "
            "Use a measured soil pH if available."
        ) from exc
    parsed["latitude"] = latitude
    parsed["longitude"] = longitude
    return parsed
