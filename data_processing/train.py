import json
import csv

# Load JSON file
with open('train.json', 'r') as file:
    data = json.load(file)

# Get field names (keys)
fields = data[0].keys()

# Write to CSV
with open('train_data.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=fields)
    
    writer.writeheader()  # Write column names
    writer.writerows(data)  # Write data rows

print("✅ JSON converted to CSV successfully!")