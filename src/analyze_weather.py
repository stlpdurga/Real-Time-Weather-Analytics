from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Project paths
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "processed"
CHART_DIR = ROOT / "visualizations"
CHART_DIR.mkdir(parents=True, exist_ok=True)

# Load collected weather datasets
hourly = pd.read_csv(DATA_DIR / "hourly_weather.csv")
daily = pd.read_csv(DATA_DIR / "daily_weather.csv")

# Prepare data types
hourly["time"] = pd.to_datetime(hourly["time"], errors="coerce")
daily["time"] = pd.to_datetime(daily["time"], errors="coerce")

numeric_cols = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation_probability",
    "precipitation",
    "wind_speed_10m"
]

for col in numeric_cols:
    hourly[col] = pd.to_numeric(hourly[col], errors="coerce")

# -----------------------------
# 1. DATA QUALITY CHECKS
# -----------------------------
print("\n--- DATA QUALITY REPORT ---")
print("Hourly rows:", len(hourly))
print("Daily rows:", len(daily))
print("\nMissing values:\n", hourly.isnull().sum())
print("\nDuplicate rows:", hourly.duplicated().sum())
print("Invalid timestamps:", hourly["time"].isna().sum())

# Remove duplicate rows and invalid timestamps
hourly = hourly.drop_duplicates()
hourly = hourly.dropna(subset=["time"])
daily = daily.drop_duplicates()
daily = daily.dropna(subset=["time"])

# Report missing numeric values; don't silently invent measurements
print("\nMissing numeric values after validation:")
print(hourly[numeric_cols].isnull().sum())

# -----------------------------
# 2. DESCRIPTIVE STATISTICS
# -----------------------------
print("\n--- DESCRIPTIVE STATISTICS ---")
print(hourly[numeric_cols].describe().round(2))

print("\n--- DAILY FORECAST ---")
print(daily.to_string(index=False))

print("\n--- KEY FINDINGS ---")
print(
    "Average forecast temperature:",
    round(hourly["temperature_2m"].mean(), 2), "°C"
)
print(
    "Highest forecast temperature:",
    round(hourly["temperature_2m"].max(), 2), "°C"
)
print(
    "Lowest forecast temperature:",
    round(hourly["temperature_2m"].min(), 2), "°C"
)
print(
    "Average relative humidity:",
    round(hourly["relative_humidity_2m"].mean(), 2), "%"
)
print(
    "Maximum hourly rain probability:",
    round(hourly["precipitation_probability"].max(), 2), "%"
)

# -----------------------------
# 3. CORRELATION ANALYSIS
# -----------------------------
print("\n--- CORRELATION MATRIX ---")
print(hourly[numeric_cols].corr().round(2))

# -----------------------------
# 4. VISUALIZATIONS
# -----------------------------
sns.set_theme(style="whitegrid")

def save_chart(filename):
    plt.tight_layout()
    plt.savefig(CHART_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved chart:", filename)

# Chart 1: Hourly temperature trend
plt.figure(figsize=(12, 5))
sns.lineplot(data=hourly, x="time", y="temperature_2m")
plt.title("Hourly Temperature Forecast")
plt.xlabel("Forecast Time")
plt.ylabel("Temperature (°C)")
plt.xticks(rotation=45)
save_chart("01_temperature_trend.png")

# Chart 2: Hourly humidity trend
plt.figure(figsize=(12, 5))
sns.lineplot(data=hourly, x="time", y="relative_humidity_2m")
plt.title("Hourly Relative Humidity Forecast")
plt.xlabel("Forecast Time")
plt.ylabel("Relative Humidity (%)")
plt.xticks(rotation=45)
save_chart("02_humidity_trend.png")

# Chart 3: Rain probability
plt.figure(figsize=(12, 5))
sns.lineplot(
    data=hourly,
    x="time",
    y="precipitation_probability"
)
plt.title("Hourly Probability of Precipitation")
plt.xlabel("Forecast Time")
plt.ylabel("Probability (%)")
plt.xticks(rotation=45)
save_chart("03_rain_probability.png")

# Chart 4: Wind speed
plt.figure(figsize=(12, 5))
sns.lineplot(data=hourly, x="time", y="wind_speed_10m")
plt.title("Hourly Wind Speed Forecast")
plt.xlabel("Forecast Time")
plt.ylabel("Wind Speed (km/h)")
plt.xticks(rotation=45)
save_chart("04_wind_speed.png")

# Chart 5: Daily minimum vs maximum temperature
daily_long = daily.melt(
    id_vars=["time"],
    value_vars=["temperature_2m_min", "temperature_2m_max"],
    var_name="Temperature Type",
    value_name="Temperature (°C)"
)

daily_long["Temperature Type"] = daily_long["Temperature Type"].map({
    "temperature_2m_min": "Minimum",
    "temperature_2m_max": "Maximum"
})

plt.figure(figsize=(10, 5))
sns.barplot(
    data=daily_long,
    x="time",
    y="Temperature (°C)",
    hue="Temperature Type"
)
plt.title("Daily Minimum vs Maximum Temperature")
plt.xlabel("Forecast Date")
plt.ylabel("Temperature (°C)")
plt.xticks(rotation=45)
save_chart("05_daily_temperature_range.png")

# Export validated data for Power BI
hourly.to_csv(DATA_DIR / "hourly_weather_clean.csv", index=False)
daily.to_csv(DATA_DIR / "daily_weather_clean.csv", index=False)

print("\nEDA COMPLETE")
print("Charts saved in:", CHART_DIR)
print("Cleaned datasets saved in:", DATA_DIR)