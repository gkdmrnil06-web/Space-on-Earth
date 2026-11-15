
import pandas as pd

# Load FAO ECOCROP requirements
crops = pd.read_csv("crop_requirements.csv")

# Example NASA temperature measurement
nasa_temperature = 20.0

print("TerraShift - FAO Climate Compatibility Test")
print("------------------------------------------")

for _, crop in crops.iterrows():

    crop_name = crop["crop"]

    min_temp = crop["optimal_temp_min_c"]
    max_temp = crop["optimal_temp_max_c"]

    if min_temp <= nasa_temperature <= max_temp:
        status = "Within optimal range"
    else:
        status = "Outside optimal range"

    print(f"{crop_name}: {status}")
