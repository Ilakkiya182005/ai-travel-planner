import pandas as pd

# List all your CSV files
files = [
    "train_data.csv",
    "bus_data.csv",
]

# Read and combine all files
df = pd.concat([pd.read_csv(file) for file in files], ignore_index=True)

# Save as one CSV
df.to_csv("travel_options.csv", index=False)

print("All files merged successfully into travel_options.csv")