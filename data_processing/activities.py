import pandas as pd
import random

# Load your CSV file
df = pd.read_csv("Tourist.csv")

# List of cities you want
cities = ["Bangalore", "Chennai", "Delhi", "Hyderabad", "Kolkata", "Mumbai", "Munnar"]

# Filter dataset for those cities
df_filtered = df[df["City"].isin(cities)]

# Add new column: entry_fee (random between 100 and 3000)
df_filtered["entry_fee"] = [random.randint(100, 3000) for _ in range(len(df_filtered))]

# Save to new file
df_filtered.to_csv("filtered_tourist_data.csv", index=False)

print("Filtered dataset with entry fees created!")