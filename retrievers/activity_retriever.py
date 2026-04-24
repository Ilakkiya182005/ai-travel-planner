import pandas as pd

class ActivityRetriever:
    def __init__(self):
        self.df = pd.read_csv('data/activities_data.csv')

    def search(self, query, city, top_k=5):
        results = self.df[(self.df['City'].str.lower() == city.lower())]
        return results.head(top_k).to_dict('records')