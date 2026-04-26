import pandas as pd
import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer

# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_STORE_DIR = os.path.join(PROJECT_ROOT, 'embeddings', 'vector_store')

# Load sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')


class HotelRetriever:
    def __init__(self):
        # Load vector store
        index_path = os.path.join(VECTOR_STORE_DIR, 'hotel_index')
        metadata_path = os.path.join(VECTOR_STORE_DIR, 'hotel_metadata.pkl')
        
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            raise FileNotFoundError("Hotel vector store not found. Please run create_embeddings.py first.")
        
        self.index = faiss.read_index(index_path)
        with open(metadata_path, 'rb') as f:
            self.df = pickle.load(f)
    
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
        Filters hotels by city and budget using vector search, then sorts by Rating.
        """
        # Create search query
        query = f"hotels in {city}"
        query_embedding = model.encode([query])
        
        # Search in vector store
        distances, indices = self.index.search(query_embedding, len(self.df))
        
        # Get results and filter by city and price
        results = []
        for idx in indices[0]:
            if idx < len(self.df):
                row = self.df.iloc[idx]
                # Filter by city and price
                if (str(row['place']).lower() == city.lower() and 
                    row.get('Price_Clean', 0) <= max_price_per_night):
                    results.append(row.to_dict())
                    if len(results) >= top_k:
                        break
        
        # If no results within budget, get top rated hotels in city
        if not results:
            for idx in indices[0]:
                if idx < len(self.df):
                    row = self.df.iloc[idx]
                    if str(row['place']).lower() == city.lower():
                        results.append(row.to_dict())
                        if len(results) >= top_k:
                            break
        
        return results