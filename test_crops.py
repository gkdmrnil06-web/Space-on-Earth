
import pandas as pd

# Load the crop requirements database
crops = pd.read_csv("crop_requirements.csv")

print("TerraShift Crop Requirements")
print("----------------------------")

# Show the maize record
maize = crops[crops["crop"] == "Maize"]

print(maize.to_string(index=False))

print("\nTotal crops:", len(crops))
print(
    "Crops with temperature data:",
    crops["optimal_temp_min_c"].notna().sum()
)
