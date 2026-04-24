import serpapi
import pandas as pd

client = serpapi.Client(api_key="d244e57aad37ec5135fca7f09a3f088d724c666095bcebf94d611dc5e0fc4774")

results = client.search({
    "engine": "google_flights_autocomplete",
    "q": "New"
})

suggestions = results["suggestions"]
df = pd.DataFrame(suggestions)
df.to_csv("flight_suggestions.csv", index=False)
print("Saved to flight_suggestions.csv")