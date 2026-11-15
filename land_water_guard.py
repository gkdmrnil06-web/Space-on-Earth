"""Conservative land/water check for farm coordinates.

Natural Earth public-domain 1:110m land boundaries provide an offline
coastline check. Bundled intermediate-resolution GSHHG lake polygons provide
point-in-water detection even where reverse geocoding reports nearby land.
A cached OpenStreetMap Nominatim reverse lookup checks other candidate points.
An unavailable/ambiguous lookup is NOT silently treated as verified farmland.
No geolocation data are uploaded other than the selected coordinate to the
Nominatim public reverse-geocoding service when the check is run.
"""
from functools import lru_cache
from pathlib import Path
import json
import math
from shapely.geometry import Point, shape
from shapely.ops import unary_union
from shapely.strtree import STRtree

MAP_PATH = Path(__file__).parent / 'assets' / 'naturalearth_land_110m.geojson'
LAKES_PATH = Path(__file__).parent / 'assets' / 'gshhg_lakes_intermediate.geojson'
WATER_TYPES = {
    'water', 'lake', 'reservoir', 'river', 'riverbank', 'stream', 'canal',
    'sea', 'ocean', 'bay', 'strait', 'lagoon', 'wetland', 'pond', 'basin',
    'waterway', 'dock', 'harbour', 'fjord',
}

@lru_cache(maxsize=1)
def _land_shape():
    features = json.loads(MAP_PATH.read_text(encoding='utf-8'))['features']
    return unary_union([shape(f['geometry']) for f in features if f.get('geometry')])


@lru_cache(maxsize=1)
def _lake_index():
    """Local inland-water polygons. Never depend on reverse geocoding for lakes."""
    features = json.loads(LAKES_PATH.read_text(encoding='utf-8'))['features']
    geometries = [shape(feature['geometry']) for feature in features if feature.get('geometry')]
    return STRtree(geometries)


def _inside_mapped_lake(point):
    lake_index = _lake_index()
    return any(lake_index.geometries[index].covers(point) for index in lake_index.query(point))


def _near_coast(geometry, point, latitude):
    # Conservative margin: the included 1:110m polygons can miss small
    # islands, river mouths and close-to-shore locations.
    margin_degrees = 0.15 / max(0.35, math.cos(math.radians(latitude)))
    return geometry.boundary.distance(point) <= margin_degrees

@lru_cache(maxsize=2048)
def _reverse_classification(latitude, longitude):
    """Return 'water', 'not_water_detected', or 'unavailable'.

    Nominatim's reverse result is the *nearest mapped OSM object*, not
    exhaustive land-cover evidence. Positive water identification is useful;
    no water tag alone cannot prove dry ground.
    """
    try:
        from geopy.geocoders import Nominatim
        result = Nominatim(user_agent='space-on-earth-land-check/1.0', timeout=5).reverse(
            (latitude, longitude), exactly_one=True, zoom=17, language='en'
        )
        if not result:
            return 'unavailable'
        raw = result.raw or {}
        category = str(raw.get('category', raw.get('class', ''))).lower()
        kind = str(raw.get('type', '')).lower()
        addresstype = str(raw.get('addresstype', '')).lower()
        address = raw.get('address', {}) or {}
        if (category in {'waterway'} or kind in WATER_TYPES or
            addresstype in WATER_TYPES or
            any(k in address for k in ('water', 'lake', 'reservoir', 'bay', 'sea', 'ocean'))):
            return 'water'
        return 'not_water_detected'
    except Exception:
        return 'unavailable'

@lru_cache(maxsize=2048)
def classify_location(latitude, longitude):
    """Return (status, reason), with status land/water/uncertain.

    Land means a coarse land polygon and a successful OSM reverse lookup that
    did not identify a water feature. It is still NOT a verified farm parcel.
    """
    try:
        latitude, longitude = float(latitude), float(longitude)
        if not (math.isfinite(latitude) and math.isfinite(longitude)):
            return 'uncertain', 'invalid_coordinates'
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            return 'uncertain', 'invalid_coordinates'
        point = Point(longitude, latitude)
        # A freshwater lake remains inside the coarse continent polygon.
        # Check its own water-surface polygon before land/OSM address logic.
        if _inside_mapped_lake(point):
            return 'water', 'mapped_water_feature'
        land = _land_shape()
        inside = land.covers(point)
        coast = _near_coast(land, point, latitude)
        # Remote ocean: can reject immediately, even without internet.
        if not inside and not coast:
            return 'water', 'ocean_or_sea'
        reverse = _reverse_classification(round(latitude, 5), round(longitude, 5))
        if reverse == 'water':
            return 'water', 'mapped_water_feature'
        if reverse == 'unavailable':
            return 'uncertain', 'reverse_unavailable'
        if not inside or coast:
            # The coarse coastline isn't accurate enough to decide.
            return 'uncertain', 'coastline_uncertain'
        return 'land', 'land_candidate'
    except (OSError, ValueError, KeyError, TypeError):
        return 'uncertain', 'land_mask_unavailable'
