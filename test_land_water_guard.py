"""Offline verification of geographic guard with simulated reverse responses."""
from unittest.mock import patch
from land_water_guard import classify_location, _reverse_classification


def run():
    samples = [
        ((0, -150), 'water'),    # central Pacific
        ((26, -42), 'water'),   # central Atlantic
        ((38.466, 27.221), 'land'), # Izmir
        ((-1.2864, 36.8172), 'land'), # Nairobi
        ((-1, 33.2), 'water'),  # Lake Victoria, lake polygon
        ((38.56, 43.25), 'water'),  # Lake Van: offline surface polygon
        ((38.55, 43.30), 'water'),  # Lake Van: second interior point
        ((41.1, 29.04), 'uncertain'), # coastal / narrow waterway: fail safely
    ]
    with patch('land_water_guard._reverse_classification', side_effect=lambda lat, lon: 'water' if (lat, lon) == (-1.0, 33.2) else 'not_water_detected'):
        for (lat, lon), expected in samples:
            actual, reason = classify_location(lat, lon)
            assert actual == expected, (lat, lon, actual, expected, reason)
    classify_location.cache_clear()
    with patch('land_water_guard._reverse_classification', return_value='unavailable'):
        assert classify_location(38.466, 27.221)[0] == 'uncertain'
        assert classify_location(0, -150)[0] == 'water'
    print('Land/water tests passed')

if __name__ == '__main__':
    run()
