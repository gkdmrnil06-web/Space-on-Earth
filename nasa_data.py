"""NASA POWER data access and annual data-quality checks."""
from datetime import datetime
import pandas as pd
import requests

API_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"


def get_nasa_data(latitude, longitude, start_date, end_date):
    """Fetch a NASA POWER daily time series for a global coordinate."""
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        raise ValueError("Invalid geographic coordinates.")
    start = datetime.strptime(start_date, "%Y%m%d")
    end = datetime.strptime(end_date, "%Y%m%d")
    if start > end:
        raise ValueError("Start date must not exceed end date.")
    params = {
        "latitude": round(latitude, 3),
        "longitude": round(longitude, 3),
        "start": start_date,
        "end": end_date,
        "parameters": "T2M,PRECTOTCORR",
        "community": "AG",
        "format": "JSON",
    }
    response = requests.get(API_URL, params=params, timeout=120)
    response.raise_for_status()
    climate = response.json()["properties"]["parameter"]
    df = pd.DataFrame({
        "Temperature": climate["T2M"],
        "Precipitation": climate["PRECTOTCORR"],
    })
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    df = df.apply(pd.to_numeric, errors="coerce")
    df = df.mask(df <= -900)
    df.loc[df["Precipitation"] < 0, "Precipitation"] = float("nan")
    return df.sort_index()


def get_historical_data(latitude, longitude):
    """Keep individual API requests moderate in size."""
    periods = [("20010101", "20121231"), ("20130101", "20251231")]
    pieces = [get_nasa_data(latitude, longitude, start, end) for start, end in periods]
    df = pd.concat(pieces).sort_index()
    return df[~df.index.duplicated(keep="first")]


def annual_statistics(daily):
    """Only use complete precipitation years to avoid biased rain totals."""
    records = []
    for year in range(2001, 2026):
        subset = daily[daily.index.year == year]
        expected = 366 if pd.Timestamp(year, 12, 31).is_leap_year else 365
        valid_temp = subset["Temperature"].count()
        valid_rain = subset["Precipitation"].count()
        records.append({
            "Year": year,
            "Temperature": subset["Temperature"].mean() if valid_temp >= expected * 0.95 else float("nan"),
            "Precipitation": subset["Precipitation"].sum() if valid_rain == expected else float("nan"),
            "Temperature Coverage": valid_temp / expected,
            "Precipitation Coverage": valid_rain / expected,
        })
    return pd.DataFrame(records).set_index("Year")


def climate_comparison(annual):
    """Compare matched historical periods without claiming future prediction."""
    base = annual.loc[2001:2020]
    recent = annual.loc[2021:2025]
    if (base["Temperature"].count() < 15 or recent["Temperature"].count() < 4
            or base["Precipitation"].count() < 15 or recent["Precipitation"].count() < 4):
        raise ValueError("Insufficient complete annual data for a robust comparison.")
    base_temp = base["Temperature"].mean()
    recent_temp = recent["Temperature"].mean()
    base_rain = base["Precipitation"].mean()
    recent_rain = recent["Precipitation"].mean()
    if base_rain <= 0:
        raise ValueError("Reference precipitation must be greater than zero.")
    return {
        "temperature_difference": recent_temp - base_temp,
        "precipitation_difference_pct": 100 * (recent_rain - base_rain) / base_rain,
        "baseline_temperature": base_temp,
        "recent_temperature": recent_temp,
        "baseline_precipitation": base_rain,
        "recent_precipitation": recent_rain,
        "valid_baseline_years": int(base["Precipitation"].count()),
        "valid_recent_years": int(recent["Precipitation"].count()),
    }


def seasonal_comparison(daily, start_month, months=3):
    """Compare matching calendar-month windows in historical and recent years.

    Cross-year windows (e.g. November–January) are grouped by the season's
    start year; only seasons with every requested daily precipitation value
    and >=95% temperature values are admitted.
    """
    if not 1 <= start_month <= 12 or not 1 <= months <= 6:
        raise ValueError("Invalid seasonal window.")
    periods = []
    for year in range(2001, 2026):
        first = pd.Timestamp(year, start_month, 1)
        last = first + pd.DateOffset(months=months)
        if last > pd.Timestamp("2026-01-01"):
            continue
        expected = len(pd.date_range(first, last - pd.Timedelta(days=1), freq="D"))
        frame = daily.loc[(daily.index >= first) & (daily.index < last)]
        if frame["Precipitation"].count() != expected or frame["Temperature"].count() < expected * .95:
            continue
        periods.append({"Year": year, "Temperature": frame["Temperature"].mean(),
                        "Precipitation": frame["Precipitation"].sum()})
    records = pd.DataFrame(periods)
    if records.empty:
        raise ValueError("No complete seasonal records were found.")
    baseline = records.loc[records["Year"].between(2001, 2020)]
    recent = records.loc[records["Year"].between(2021, 2025)]
    if len(baseline) < 15 or len(recent) < 3:
        raise ValueError("Insufficient complete seasonal records. Select another window.")
    return {
        "baseline_temperature": float(baseline["Temperature"].mean()),
        "baseline_precipitation": float(baseline["Precipitation"].mean()),
        "recent_temperature": float(recent["Temperature"].mean()),
        "recent_precipitation": float(recent["Precipitation"].mean()),
        "valid_baseline_seasons": len(baseline),
        "valid_recent_seasons": len(recent),
    }
