import pandas as pd

# List all your CSV files
files = [
    "updated_hotels_delhi.csv",
    "updated_hotels_bangalore.csv",
    "updated_hotels_hyderabad.csv",
    "updated_hotels_kolkata.csv",
    "updated_hotels_mumbai.csv",
    "updated_hotels_munnar.csv",
    "updated_hotels_chennai.csv"
]

# Read and combine all files
df = pd.concat([pd.read_csv(file) for file in files], ignore_index=True)

# Save as one CSV
df.to_csv("hotels_data.csv", index=False)

print("All files merged successfully into hotels.csv")