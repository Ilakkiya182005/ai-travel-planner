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


class ActivityRetriever:
    def __init__(self):
        # Load vector store
        index_path = os.path.join(VECTOR_STORE_DIR, 'activity_index')
        metadata_path = os.path.join(VECTOR_STORE_DIR, 'activity_metadata.pkl')
        
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            raise FileNotFoundError("Activity vector store not found. Please run create_embeddings.py first.")
        
        self.index = faiss.read_index(index_path)
        with open(metadata_path, 'rb') as f:
            self.df = pickle.load(f)

    def search(self, query, city, top_k=5):
        """
        Search for activities using vector search based on query and city.
        """
        # Create search query combining user query and city
        search_query = f"{query} {city}" if query else city
        query_embedding = model.encode([search_query])
        
        # Search in vector store
        distances, indices = self.index.search(query_embedding, len(self.df))
        
        # Filter results by city
        results = []
        for idx in indices[0]:
            if idx < len(self.df):
                row = self.df.iloc[idx]
                if str(row['City']).lower() == city.lower():
                    results.append(row.to_dict())
                    if len(results) >= top_k:
                        break
        
        return results