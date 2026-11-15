"""Offline tests for historical precipitation exposure; no NASA API call."""

import pandas as pd

from water_exposure import calculate_water_exposure, season_rainfall_series


def test_equal_seasons():
    dates = pd.date_range("2001-01-01", "2025-12-31", freq="D")
    data = pd.DataFrame({"Precipitation": 2.0}, index=dates)
    output = calculate_water_exposure(data, 3, 3)
    assert len(output) == 2
    assert all(abs(s["relative_index"] - 1.0) < 1e-9 for s in output)
    assert all(s["label"] == "Near historical reference" for s in output)
    assert all(s["baseline_years"] == 20 and s["recent_years"] == 5 for s in output)


def test_lower_second_season():
    dates = pd.date_range("2001-01-01", "2025-12-31", freq="D")
    values = [0.4 if (d.year >= 2021 and d.month in (6, 7, 8)) else 2.0 for d in dates]
    data = pd.DataFrame({"Precipitation": values}, index=dates)
    output = calculate_water_exposure(data, 3, 3)
    assert output[0]["label"] == "Near historical reference"
    assert output[1]["label"] == "Lower than historical reference"
    assert abs(output[1]["relative_index"] - .2) < 1e-9


def test_missing_days_not_used():
    dates = pd.date_range("2001-01-01", "2025-12-31", freq="D")
    data = pd.DataFrame({"Precipitation": 1.0}, index=dates)
    data.loc[pd.Timestamp("2024-06-19"), "Precipitation"] = float("nan")
    series = season_rainfall_series(data, 6, 3)
    assert 2024 not in series["Year"].tolist()
    assert 2023 in series["Year"].tolist()


def test_cross_year_excludes_incomplete_2025():
    dates = pd.date_range("2001-01-01", "2025-12-31", freq="D")
    data = pd.DataFrame({"Precipitation": 1.0}, index=dates)
    series = season_rainfall_series(data, 11, 3)
    assert 2025 not in series["Year"].tolist()
    assert 2024 in series["Year"].tolist()


if __name__ == "__main__":
    test_equal_seasons()
    test_lower_second_season()
    test_missing_days_not_used()
    test_cross_year_excludes_incomplete_2025()
    print("4/4 water exposure offline tests passed.")
