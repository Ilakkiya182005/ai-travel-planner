import pandas as pd

# Load your CSV file
df = pd.read_csv("hotels_mumbai.csv")   # or your file name

# Add new column
df["place"] = "Mumbai"  # or any value you want to assign

# Save back to CSV
df.to_csv("updated_hotels_mumbai.csv", index=False)

print("Column added successfully!")