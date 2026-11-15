"""Test SoilGrids data parsing offline; optionally try the live endpoint."""
import argparse
from soil_data import parse_soilgrids_response, get_soil_data, SoilDataUnavailable


def mock_layer(name, value):
    return {"name": name, "depths": [{"label": "0-5cm", "values": {"mean": value}}]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Try the currently paused SoilGrids REST API")
    parser.add_argument("--lat", type=float, default=-1.2864)
    parser.add_argument("--lon", type=float, default=36.8172)
    args = parser.parse_args()

    example = {"properties": {"layers": [
        mock_layer("phh2o", 65),
        mock_layer("clay", 240),
        mock_layer("sand", 490),
        mock_layer("soc", 180),
    ]}}
    soil = parse_soilgrids_response(example)
    assert soil["soil_ph"] == 6.5
    assert soil["clay_percent"] == 24.0
    assert soil["sand_percent"] == 49.0
    assert soil["organic_carbon_g_kg"] == 18.0
    print("Offline parser test passed (synthetic values, not location data).")

    if args.live:
        print(f"Checking optional SoilGrids lookup at {args.lat}, {args.lon}...")
        try:
            observed = get_soil_data(args.lat, args.lon)
        except SoilDataUnavailable as exc:
            print(str(exc))
            print("Safe fallback confirmed: no estimated soil values invented.")
        else:
            print("SoilGrids model estimates (NOT field measurements):")
            for key, value in observed.items():
                print(f"{key}: {value}")


if __name__ == "__main__":
    main()
