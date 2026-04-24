import pandas as pd
import os

class HotelRetriever:
    def __init__(self, file_path='data/hotels_data.csv'):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Hotel data not found at {file_path}")
        self.df = pd.read_csv(file_path)
        self._preprocess()

    def _preprocess(self):
        # Clean the Price column: remove commas and convert to float
        def clean_price(price):
            if pd.isna(price): return 0.0
            if isinstance(price, (int, float)): return float(price)
            return float(str(price).replace(',', '').replace('₹', '').strip())

        self.df['Price_Clean'] = self.df['Price'].apply(clean_price)
        # Standardize city names to lowercase for easier matching
        self.df['place'] = self.df['place'].str.strip()

    def get_best_hotels(self, city, max_price_per_night, top_k=3):
        """
        Filters hotels by city and budget, then sorts by Rating.
        """
        mask = (self.df['place'].str.lower() == city.lower()) & \
               (self.df['Price_Clean'] <= max_price_per_night)
        
        filtered_hotels = self.df[mask]
        
        # If no hotels found within budget, fallback to the cheapest available in that city
        if filtered_hotels.empty:
            filtered_hotels = self.df[self.df['place'].str.lower() == city.lower()]
            
        return filtered_hotels.sort_values(by='Rating', ascending=False).head(top_k).to_dict('records')