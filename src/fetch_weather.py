import requests
import pandas as pd
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Example city: Hyderabad
latitude = 17.3850
longitude = 78.4867

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": latitude,
    "longitude": longitude,
    "current": [
        "temperature_2m",
        "relative_humidity_2m",
        "apparent_temperature",
        "precipitation",
        "weather_code",
        "wind_speed_10m"
    ],
    "hourly": [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation_probability",
        "precipitation",
        "wind_speed_10m"
    ],
    "daily": [
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_probability_max"
    ],
    "timezone": "Asia/Kolkata",
    "forecast_days": 7
}

try:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    weather = response.json()

    # Current conditions
    current_df = pd.DataFrame([{
        "city": "Hyderabad",
        "timestamp": weather["current"]["time"],
        "temperature_c": weather["current"]["temperature_2m"],
        "humidity_percent": weather["current"]["relative_humidity_2m"],
        "feels_like_c": weather["current"]["apparent_temperature"],
        "precipitation_mm": weather["current"]["precipitation"],
        "weather_code": weather["current"]["weather_code"],
        "wind_speed_kmh": weather["current"]["wind_speed_10m"]
    }])

    # Hourly forecast
    hourly_df = pd.DataFrame(weather["hourly"])
    hourly_df.insert(0, "city", "Hyderabad")
    hourly_df["time"] = pd.to_datetime(hourly_df["time"])

    # Daily forecast
    daily_df = pd.DataFrame(weather["daily"])
    daily_df.insert(0, "city", "Hyderabad")
    daily_df["time"] = pd.to_datetime(daily_df["time"])

    # Basic data-quality checks
    print("\nCURRENT WEATHER")
    print(current_df.to_string(index=False))

    print("\nHOURLY DATA PREVIEW")
    print(hourly_df.head().to_string(index=False))

    print("\nDAILY DATA PREVIEW")
    print(daily_df.head().to_string(index=False))

    print("\nMissing values in hourly data:")
    print(hourly_df.isnull().sum())

    print("\nDuplicate hourly rows:", hourly_df.duplicated().sum())

    # Export CSV files for Power BI
    current_df.to_csv(
        PROCESSED_DIR / "current_weather.csv", index=False
    )
    hourly_df.to_csv(
        PROCESSED_DIR / "hourly_weather.csv", index=False
    )
    daily_df.to_csv(
        PROCESSED_DIR / "daily_weather.csv", index=False
    )

    print("\nSUCCESS: Weather data collected and exported.")
    print(f"Files saved in: {PROCESSED_DIR}")

except requests.RequestException as error:
    print("API request failed:", error)
except (KeyError, ValueError) as error:
    print("Unexpected API response:", error)