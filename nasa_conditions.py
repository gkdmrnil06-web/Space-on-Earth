"""Real NASA POWER daily soil-moisture and fire-weather context.

No simulated values. Fire-weather risk is an UNVALIDATED heuristic,
not an official wildfire warning or fire-danger rating.
"""
from datetime import date, timedelta
import math
import requests
import pandas as pd
import streamlit as st

API = "https://power.larc.nasa.gov/api/temporal/daily/point"


def _valid(value):
    try:
        v = float(value)
        return v if math.isfinite(v) and v > -900 else None
    except (ValueError, TypeError):
        return None


@st.cache_data(ttl=21600, show_spinner=False)
def _daily(lat, lon, community, parameters, lookback_days=30):
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=lookback_days)
    response = requests.get(API, params={
        "latitude": round(float(lat), 3),
        "longitude": round(float(lon), 3),
        "start": start.strftime("%Y%m%d"),
        "end": end.strftime("%Y%m%d"),
        "parameters": ",".join(parameters),
        "community": community,
        "format": "JSON",
        "time-standard": "UTC",
    }, timeout=35)
    response.raise_for_status()
    payload = response.json()
    data = payload.get("properties", {}).get("parameter", {})
    if not isinstance(data, dict) or not data:
        raise ValueError("NASA POWER returned no parameter series")
    return data


def _series(data, name):
    values = data.get(name, {})
    if not isinstance(values, dict):
        return pd.Series(dtype=float)
    result = {}
    for day, value in values.items():
        v = _valid(value)
        if v is not None:
            try:
                result[pd.Timestamp(str(day))] = v
            except (ValueError, TypeError):
                continue
    return pd.Series(result, dtype=float).sort_index()


def _recent(series, max_age_days=10):
    if series.empty:
        return None, None
    day = series.index[-1]
    if (pd.Timestamp(date.today()) - day).days > max_age_days:
        return None, None
    return float(series.iloc[-1]), day


def get_nasa_conditions(lat, lon):
    """Return separate availability for moisture and meteorological risk."""
    answer = {"moisture": None, "fire": None, "input_weather": None, "errors": []}
    if not (-90 <= float(lat) <= 90 and -180 <= float(lon) <= 180):
        answer["errors"].append("Invalid coordinates")
        return answer

    # Some NASA POWER deployments return HTTP 422 for a parameter/community
    # combination. Try the same parameter in another supported community.
    # GWETTOP is a DIFFERENT quantity (dimensionless soil wetness), never
    # label it SFMC or compare it numerically to volumetric moisture.
    # For network failures do not silently substitute a made-up estimate.
    answer["moisture_status"] = "missing"
    answer["soil_wetness"] = None
    answer["moisture_detail"] = ""
    attempts = []
    network_errors = []
    for community, parameter, days in (
        ("HY", "SFMC", 180),
        ("AG", "SFMC", 180),
        ("HY", "GWETTOP", 180),
        ("AG", "GWETTOP", 180),
    ):
        try:
            data = _daily(lat, lon, community, (parameter,), lookback_days=days)
            series = _series(data, parameter)
            series = series[(series >= 0) & (series <= 1)]
            if series.empty:
                attempts.append(f"{community}/{parameter}: no valid values")
                continue
            value = float(series.iloc[-1])
            day = series.index[-1]
            age = (pd.Timestamp(date.today()) - day).days
            if parameter == "SFMC":
                answer["moisture"] = {
                    "volumetric_pct": value * 100,
                    "date": day.strftime("%Y-%m-%d"),
                    "age_days": age,
                    "is_historical": age > 14,
                    "community": community,
                    "source": "NASA POWER SFMC (0-5 cm)",
                }
            else:
                answer["soil_wetness"] = {
                    "fraction": value,
                    "date": day.strftime("%Y-%m-%d"),
                    "age_days": age,
                    "is_historical": age > 14,
                    "community": community,
                    "source": "NASA POWER GWETTOP (surface wetness fraction)",
                }
            answer["moisture_status"] = ("historical" if age > 14 else "recent") if parameter == "SFMC" else "wetness_fallback"
            answer["moisture_detail"] = f"NASA POWER {community}/{parameter}; observation {day:%Y-%m-%d}; age {age} days."
            if age > 14:
                answer["errors"].append("Soil observation is historical, not a live sensor measurement.")
            break
        except requests.HTTPError as exc:
            response = getattr(exc, "response", None)
            status = getattr(response, "status_code", None)
            body = (getattr(response, "text", "") or "").replace("\n", " ")[:160]
            attempts.append(f"{community}/{parameter}: HTTP {status or 'error'} {body}")
            # Bad parameter selection, try supported alternatives.
            if status in (400, 404, 422):
                continue
            if status in (401, 403, 429, 500, 502, 503, 504):
                network_errors.append(f"NASA returned HTTP {status}")
                break
            continue
        except (requests.ConnectionError, requests.Timeout) as exc:
            network_errors.append(f"{type(exc).__name__}: {str(exc)[:140]}")
            break  # endpoint unreachable; different parameter won't fix DNS
        except requests.RequestException as exc:
            network_errors.append(f"{type(exc).__name__}: {str(exc)[:140]}")
            break
        except (ValueError, KeyError, TypeError) as exc:
            attempts.append(f"{community}/{parameter}: invalid response ({type(exc).__name__})")
    if not answer["moisture"] and not answer["soil_wetness"]:
        if network_errors:
            answer["moisture_status"] = "network_error"
            answer["moisture_detail"] = "NASA soil endpoint unreachable or rejected request: " + "; ".join(network_errors)
        else:
            answer["moisture_status"] = "missing"
            answer["moisture_detail"] = "NASA returned no usable soil reading: " + "; ".join(attempts)
        answer["errors"].append(answer["moisture_detail"])

    try:
        weather = _daily(lat, lon, "AG", ("T2M_MAX", "RH2M", "WS10M", "PRECTOTCORR"))
        temp_s = _series(weather, "T2M_MAX")
        rh_s = _series(weather, "RH2M")
        wind_s = _series(weather, "WS10M")
        rain_s = _series(weather, "PRECTOTCORR")
        # Independent field-input climate context, drawn from the SAME NASA
        # weather request as the fire screen. Do not require a fire score for it.
        # Missing data must not be substituted by 0 or a different location.
        weather_joined = pd.concat([temp_s.rename("tmax"), rh_s.rename("rh"),
                                    rain_s.rename("rain"), wind_s.rename("wind")], axis=1).sort_index()
        if not weather_joined.empty:
            latest_day = weather_joined.index[-1]
            if (pd.Timestamp(date.today()) - latest_day).days <= 10:
                seven_days = pd.date_range(latest_day - pd.Timedelta(days=6), latest_day)
                week = weather_joined.reindex(seven_days)
                latest = weather_joined.loc[latest_day]
                def valid_range(value, low, high):
                    return float(value) if pd.notna(value) and low <= float(value) <= high else None
                def complete_mean(column, low, high):
                    values = [valid_range(v, low, high) for v in week[column]]
                    return float(sum(values) / 7) if all(v is not None for v in values) else None
                rain_values = [valid_range(v, 0, 1000) for v in week["rain"]]
                rain_total = float(sum(rain_values)) if all(v is not None for v in rain_values) else None
                answer["input_weather"] = {
                    "date": latest_day.strftime("%Y-%m-%d"),
                    "temperature_max_c": valid_range(latest["tmax"], -80, 65),
                    "humidity_pct": valid_range(latest["rh"], 0, 100),
                    "wind_ms": valid_range(latest["wind"], 0, 100),
                    "humidity_7d_avg_pct": complete_mean("rh", 0, 100),
                    "temperature_max_7d_avg_c": complete_mean("tmax", -80, 65),
                    "wind_7d_avg_ms": complete_mean("wind", 0, 100),
                    "rainfall_7d_mm": rain_total,
                    "complete_days": int(week[["rh", "rain", "tmax"]].notna().all(axis=1).sum()),
                    "source": "NASA POWER daily gridded meteorology (AG)",
                }
            else:
                answer["errors"].append("Input climate context: NASA daily observations are stale")
        # Match same daily UTC date, not unrelated latest observations.
        joined = pd.concat([temp_s.rename("t"), rh_s.rename("rh"),
                            wind_s.rename("wind")], axis=1).dropna()
        if joined.empty:
            raise ValueError("No matching daily weather observations")
        day = joined.index[-1]
        if (pd.Timestamp(date.today()) - day).days > 10:
            raise ValueError("NASA meteorology data is older than 10 days")
        t, rh, wind = [float(joined.iloc[-1][c]) for c in ("t", "rh", "wind")]
        if not (-80 <= t <= 65 and 0 <= rh <= 100 and 0 <= wind <= 100):
            raise ValueError("Meteorological value outside plausible range")
        rain7 = rain_s.loc[(rain_s.index >= day - pd.Timedelta(days=6)) & (rain_s.index <= day)]
        # A complete seven-day precipitation record is required for this heuristic.
        if len(rain7) != 7 or (rain7 < 0).any():
            raise ValueError("Incomplete 7-day NASA rainfall data")
        rainfall = float(rain7.sum())
        # Simple transparent screening heuristic, NOT a validated fire index.
        flags = {
            "hot": t >= 30,
            "dry_air": rh <= 30,
            "windy": wind >= 8,
            "dry_week": rainfall < 5,
        }
        score = sum(flags.values())
        level = ("Low", "Moderate", "Elevated", "High", "Very high")[score]
        answer["fire"] = {
            "level": level, "score": score, "date": day.strftime("%Y-%m-%d"),
            "temperature_max_c": t, "relative_humidity_pct": rh,
            "wind_speed_ms": wind, "rainfall_7d_mm": rainfall,
            "flags": flags,
        }
    except (requests.RequestException, ValueError, KeyError) as exc:
        answer["errors"].append("Fire-weather screening: " + str(exc)[:140])
    return answer
