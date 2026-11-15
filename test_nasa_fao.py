
import pandas as pd
from nasa_data import get_nasa_data

# Load FAO ECOCROP requirements
crops = pd.read_csv("crop_requirements.csv")

# Example farm location: Nairobi, Kenya
latitude = -1.2864
longitude = 36.8172

# Retrieve NASA climate data
print("Connecting to NASA POWER...")

climate = get_nasa_data(
    latitude,
    longitude,
    "20240101",
    "20241231"
)

# Calculate the annual mean temperature
annual_temperature = climate["Temperature"].mean()

print("\nNASA + FAO Crop Compatibility Test")
print("----------------------------------")
print(f"Location: {latitude}, {longitude}")
print(f"Annual Mean Temperature: {annual_temperature:.2f} C")

# Compare NASA temperature with FAO ranges
for _, crop in crops.iterrows():
    crop_name = crop["crop"]

    minimum = crop["optimal_temp_min_c"]
    maximum = crop["optimal_temp_max_c"]

    if minimum <= annual_temperature <= maximum:
        status = "Within optimal temperature range"
    else:
        status = "Outside optimal temperature range"

    print(f"{crop_name}: {status}")
