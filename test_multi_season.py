
"""Test multi-season rotation using synthetic or global NASA data."""

import argparse
from pathlib import Path

import pandas as pd

from multi_season_rotation import compare_two_seasons


def sample_daily_data():
    dates = pd.date_range(
        "2021-01-01", "2025-12-31", freq="D"
    )

    temperatures = [
        20.0 if month <= 6 else 27.0
        for month in dates.month
    ]

    rainfall = [
        3.0 if month in (3, 4, 5, 6) else 0.8
        for month in dates.month
    ]

    return pd.DataFrame(
        {
            "Temperature": temperatures,
            "Precipitation": rainfall,
        },
        index=dates
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--nasa", action="store_true")
    parser.add_argument("--lat", type=float)
    parser.add_argument("--lon", type=float)
    parser.add_argument("--month", type=int, default=3)

    args = parser.parse_args()

    if not 1 <= args.month <= 12:
        parser.error("Month must be between 1 and 12.")

    if args.nasa:
        if args.lat is None or args.lon is None:
            parser.error("--nasa requires --lat and --lon.")

        if not -90 <= args.lat <= 90:
            parser.error("Latitude must be between -90 and 90.")

        if not -180 <= args.lon <= 180:
            parser.error("Longitude must be between -180 and 180.")

        from nasa_data import get_historical_data

        print("Connecting to NASA POWER...")
        print(f"Selected location: {args.lat}, {args.lon}")

        daily = get_historical_data(args.lat, args.lon)
        label = "NASA POWER"

    else:
        daily = sample_daily_data()
        label = "SYNTHETIC TEST DATA - NOT NASA"

    results = compare_two_seasons(
        previous_crop="Maize",
        start_month=args.month,
        months_per_season=3,
        daily_data=daily,
        soil_ph=6.5,
        csv_path=Path(__file__).with_name(
            "crop_requirements.csv"
        )
    )

    print("\nSpace on Earth - Multi-Season Analysis")
    print("Data source:", label)

    for i, key in enumerate(
        ("first_season_climate", "second_season_climate"),
        1
    ):
        climate = results[key]

        print(
            f"Season {i}: "
            f"{'-'.join(climate['month_names'])}, "
            f"{climate['temperature_c']:.1f} C, "
            f"{climate['precipitation_mm']:.0f} mm"
        )

    print("\nRanked rotation scenarios:")

    for rank, plan in enumerate(results["plans"], 1):
        print(
            f"{rank}. "
            f"{' -> '.join(plan['sequence'])}: "
            f"{plan['total_score']}/24"
        )

    assert len(results["plans"]) == 3
    print("\nTests passed.")


if __name__ == "__main__":
    main()
