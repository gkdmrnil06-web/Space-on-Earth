"""Offline tests plus optional live SoilGrids WCS lookup."""
import argparse
from unittest.mock import patch
import numpy as np
from pyproj import CRS, Transformer
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
from soil_wcs import lookup_soil_ph


def mock_geotiff(raw_array):
    lon, lat = 36.8172, -1.2864
    x, y = Transformer.from_crs(CRS.from_epsg(4326),
             CRS.from_proj4('+proj=igh +datum=WGS84 +units=m +no_defs'),
             always_xy=True).transform(lon, lat)
    raw_array = np.asarray(raw_array, dtype='int16')
    with MemoryFile() as mem:
        with mem.open(driver='GTiff', height=raw_array.shape[0],
            width=raw_array.shape[1], count=1, dtype='int16',
            transform=from_origin(x-500, y+500, 250, 250),
            nodata=-32768) as dst:
            dst.write(raw_array, 1)
        return mem.read()


class FakeResponse:
    def __init__(self, content):
        self.content = content
    def raise_for_status(self):
        pass


def check(raw, expected_status, expected_ph):
    with patch('soil_wcs.requests.get', return_value=FakeResponse(mock_geotiff(raw))):
        result = lookup_soil_ph(-1.2864, 36.8172)
    assert result['status'] == expected_status, result
    assert result['ph'] == expected_ph, result
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--live', action='store_true')
    p.add_argument('--lat', type=float, default=-1.2864)
    p.add_argument('--lon', type=float, default=36.8172)
    opts = p.parse_args()
    print('Exact-cell test:', check([[65]*4 for _ in range(4)], 'available', 6.5)['status'])
    nearby = check([[0,61,0,0], [0,61,0,0], [0,61,0,0], [0,61,61,0]], 'nearby', 6.1)
    print('Nearby-cell test:', nearby['status'], 'distance (m):', nearby['distance_m'])
    print('All-zero test:', check([[0]*4 for _ in range(4)], 'unavailable', None)['status'])
    print('Far-cell test:', check([[61,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]], 'unavailable', None)['status'])
    print('Offline tests passed. Synthetic inputs are NOT actual soil observations.')
    if opts.live:
        print(f'Checking SoilGrids WCS for {opts.lat}, {opts.lon}...')
        result = lookup_soil_ph(opts.lat, opts.lon)
        print(result)
        print('Model estimates are NOT field soil measurements.')


if __name__ == '__main__':
    main()
