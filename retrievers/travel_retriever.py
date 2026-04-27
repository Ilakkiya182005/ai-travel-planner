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


class TravelRetriever:
    def __init__(self):
        index_path = os.path.join(VECTOR_STORE_DIR, 'travel_index')
        metadata_path = os.path.join(VECTOR_STORE_DIR, 'travel_metadata.pkl')

        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            raise FileNotFoundError("Travel vector store not found. Run create_embeddings.py first.")

        self.index = faiss.read_index(index_path)
        with open(metadata_path, 'rb') as f:
            self.df = pickle.load(f)

    def get_best_travel(self, source, dest, max_price, top_k=5):
        """
        Retrieve best travel options (flights + trains)
        """

        # Query for semantic search
        query = f"travel from {source} to {dest}"
        query_embedding = model.encode([query])

        # Search FAISS
        distances, indices = self.index.search(query_embedding, len(self.df))

        filtered_results = []

        for idx, dist in zip(indices[0], distances[0]):
            if idx >= len(self.df):
                continue

            row = self.df.iloc[idx]

            # Identify columns dynamically
            if row.get('data_type') == 'flight':
                source_col = 'source_city'
                dest_col = 'destination_city'
            else:
                source_col = 'source'
                dest_col = 'destination'

            # Match source & destination
            if (str(row[source_col]).lower() == source.lower() and
                str(row[dest_col]).lower() == dest.lower()):

                result = row.to_dict()
                result['distance'] = float(dist)  # FAISS similarity score

                # Mark if within budget
                result['within_budget'] = result.get('price', float('inf')) <= max_price

                filtered_results.append(result)

        # If nothing found → return empty
        if not filtered_results:
            return []

        # Sort priority:
        # 1. within budget
        # 2. price
        # 3. semantic similarity (distance)
        filtered_results.sort(
            key=lambda x: (
                not x['within_budget'],  # False (better) comes first
                x.get('price', float('inf')),
                x['distance']
            )
        )

        return filtered_results[:top_k]
    def __init__(self):
        # Load vector store for travel data (includes both flights and trains)
        index_path = os.path.join(VECTOR_STORE_DIR, 'travel_index')
        metadata_path = os.path.join(VECTOR_STORE_DIR, 'travel_metadata.pkl')
        
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            raise FileNotFoundError("Travel vector store not found. Please run create_embeddings.py first.")
        
        self.index = faiss.read_index(index_path)
        with open(metadata_path, 'rb') as f:
            self.df = pickle.load(f)

    def get_best_flight(self, source, dest, max_price):
        """
        Search for flights/trains using vector search based on source and destination.
        """
        # Create search query
        query = f"flight from {source} to {dest}"
        query_embedding = model.encode([query])
        
        # Search in vector store
        distances, indices = self.index.search(query_embedding, len(self.df))
        
        # Filter results by source, destination and price
        results = []
        for idx in indices[0]:
            if idx < len(self.df):
                row = self.df.iloc[idx]
                
                # Check if it's a flight
                if row.get('data_type') == 'flight':
                    source_col = 'source_city'
                    dest_col = 'destination_city'
                    price_col = 'price'
                else:
                    # It's a train
                    source_col = 'source'
                    dest_col = 'destination'
                    price_col = 'price'
                
                # Filter by source, destination and price
                if (str(row[source_col]).lower() == source.lower() and 
                    str(row[dest_col]).lower() == dest.lower() and 
                    row[price_col] <= max_price):
                    results.append(row.to_dict())
                    if len(results) >= 1:
                        break
        
        # If no results within budget, get the cheapest option
        if not results:
            for idx in indices[0]:
                if idx < len(self.df):
                    row = self.df.iloc[idx]
                    
                    if row.get('data_type') == 'flight':
                        source_col = 'source_city'
                        dest_col = 'destination_city'
                    else:
                        source_col = 'source'
                        dest_col = 'destination'
                    
                    if (str(row[source_col]).lower() == source.lower() and 
                        str(row[dest_col]).lower() == dest.lower()):
                        results.append(row.to_dict())
                        if len(results) >= 1:
                            break
        
        # Sort by price and return the best one
        if results:
            results.sort(key=lambda x: x.get('price', float('inf')))
        
        return results