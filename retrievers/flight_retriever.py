import pandas as pd

class FlightRetriever:
    def __init__(self):
        self.df = pd.read_csv('data/travel_flight_data.csv')

    def get_best_flight(self, source, dest, max_price):
        results = self.df[(self.df['source_city'] == source) & 
                          (self.df['destination_city'] == dest) & 
                          (self.df['price'] <= max_price)]
        return results.sort_values(by='price').head(1).to_dict('records')