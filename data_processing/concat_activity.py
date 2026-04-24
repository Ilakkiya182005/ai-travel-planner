import pandas as pd

df1 = pd.read_csv("flights_data.csv")
df2 = pd.read_csv("travel_options.csv")

# Rename columns in df1 to match df2 schema
df1 = df1.rename(columns={
    "provider": "airline",
    "train_name": "flight",
    "train_number": "flight",
    "source": "source_city",
    "destination": "destination_city",
    "departure_time": "departure_time",
    "arrival_time": "arrival_time",
    "duration": "duration",
    "price": "price",
    "available_seats": "Avaiable"
})

# Combine (stack rows)
combined_df = pd.concat([df1, df2], ignore_index=True)

# Save output
combined_df.to_csv("output.csv", index=False)

print("✅ All data combined successfully!")