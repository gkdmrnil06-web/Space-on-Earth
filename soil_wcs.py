"""Location-specific SoilGrids pH lookup (informational, not planting advice).

The exact requested pixel is preferred. If it contains an invalid zero / NoData,
we may REPORT a nearby valid grid-cell estimate, explicitly labeled as nearby,
provided that its pixel center is at most 300 m away. Nearby estimates must
never be described as exact-site measurements or fed to crop scoring silently.
"""

import math

import numpy as np
import requests
from pyproj import CRS, Transformer
from rasterio.io import MemoryFile
from rasterio.transform import xy

WCS_URL = "https://maps.isric.org/mapserv"
SOIL_CRS = "http://www.opengis.net/def/crs/EPSG/0/152160"
PROJECTION = "+proj=igh +datum=WGS84 +units=m +no_defs"
COVERAGE = "phh2o_0-5cm_mean"
MAX_NEARBY_DISTANCE_M = 300.0


def extract_ph_from_raster(raster, x, y, max_nearby_distance_m=MAX_NEARBY_DISTANCE_M):
    """Return a labeled exact-cell or nearby-cell estimate, or None.

    SoilGrids pH values use a factor of 10. Zero and declared NoData are
    rejected. Never interpolate across invalid cells or pretend a nearby
    pixel refers to the requested point.
    """
    data = raster.read(1, masked=True)
    raw_values = np.asarray(data.data, dtype=float)
    valid = np.isfinite(raw_values) & (raw_values > 0) & (raw_values <= 140)
    valid &= ~np.ma.getmaskarray(data)
    if raster.nodata is not None and np.isfinite(raster.nodata):
        valid &= raw_values != float(raster.nodata)

    if not (raster.bounds.left <= x < raster.bounds.right and
            raster.bounds.bottom < y <= raster.bounds.top):
        return None

    row, col = raster.index(x, y)
    if not (0 <= row < raster.height and 0 <= col < raster.width):
        return None

    if valid[row, col]:
        return {
            "ph": round(float(raw_values[row, col]) / 10.0, 2),
            "status": "available",
            "estimate_type": "selected_grid_cell",
            "distance_m": None,
        }

    rows, cols = np.where(valid)
    if len(rows) == 0:
        return None
    centers = [xy(raster.transform, int(r), int(c), offset="center")
               for r, c in zip(rows, cols)]
    distances = np.array([math.hypot(cx - x, cy - y) for cx, cy in centers])
    closest = int(np.argmin(distances))
    nearest_distance = float(distances[closest])
    if nearest_distance > max_nearby_distance_m:
        return None

    nearest_row, nearest_col = int(rows[closest]), int(cols[closest])
    return {
        "ph": round(float(raw_values[nearest_row, nearest_col]) / 10.0, 2),
        "status": "nearby",
        "estimate_type": "nearby_grid_cell",
        "distance_m": round(nearest_distance),
    }


def lookup_soil_ph(latitude, longitude, timeout=18):
    """Fetch SoilGrids mean pH (0-5 cm), with provenance and safe fallback."""
    latitude, longitude = float(latitude), float(longitude)
    if not (math.isfinite(latitude) and -90 <= latitude <= 90):
        raise ValueError("Invalid latitude.")
    if not (math.isfinite(longitude) and -180 <= longitude <= 180):
        raise ValueError("Invalid longitude.")

    unavailable = {
        "status": "unavailable", "ph": None,
        "source": "ISRIC SoilGrids WCS", "depth_cm": "0-5",
        "note": "No soil value was assumed.",
        "estimate_type": None, "distance_m": None,
    }
    try:
        transformer = Transformer.from_crs(
            CRS.from_epsg(4326), CRS.from_proj4(PROJECTION), always_xy=True
        )
        x, y = transformer.transform(longitude, latitude)
        if not (math.isfinite(x) and math.isfinite(y)):
            return {**unavailable, "reason": "Coordinate projection failed."}

        params = [
            ("map", "/map/phh2o.map"),
            ("SERVICE", "WCS"), ("VERSION", "2.0.1"),
            ("REQUEST", "GetCoverage"), ("COVERAGEID", COVERAGE),
            ("FORMAT", "GEOTIFF_INT16"),
            ("RESX", "250"), ("RESY", "250"),
            ("SUBSET", f"X({x-500:.1f},{x+500:.1f})"),
            ("SUBSET", f"Y({y-500:.1f},{y+500:.1f})"),
            ("SUBSETTINGCRS", SOIL_CRS), ("OUTPUTCRS", SOIL_CRS),
        ]
        response = requests.get(WCS_URL, params=params, timeout=timeout)
        response.raise_for_status()
        if not response.content.startswith((b"II*\x00", b"MM\x00*")):
            return {**unavailable, "reason": "Service did not return a GeoTIFF."}

        with MemoryFile(response.content) as memory:
            with memory.open() as raster:
                result = extract_ph_from_raster(raster, x, y)

        if result is None:
            return {
                **unavailable,
                "reason": "No valid pH cell at the selected point or within 300 m.",
            }
        if result["status"] == "nearby":
            note = (
                "Nearby SoilGrids grid-cell model estimate, approximately "
                f"{result['distance_m']:.0f} m from the requested point. "
                "NOT the selected field's pH; do not use as a measured value."
            )
        else:
            note = (
                "SoilGrids model estimate for the grid cell containing the "
                "selected point; NOT a laboratory field measurement."
            )
        return {**result, "source": "ISRIC SoilGrids WCS",
                "depth_cm": "0-5", "note": note}
    except (requests.RequestException, OSError, ValueError, RuntimeError) as error:
        return {**unavailable, "reason": f"WCS request failed ({type(error).__name__})."}
