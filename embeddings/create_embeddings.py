import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import pickle

import os

# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_STORE_DIR = os.path.join(PROJECT_ROOT, 'embeddings', 'vector_store')

# Ensure vector store directory exists
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

# Load sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')


def create_hotel_embeddings():
    """Create embeddings for hotel data"""
    print("Creating hotel embeddings...")
    df = pd.read_csv(os.path.join(PROJECT_ROOT, 'data', 'hotels_data.csv'))
    
    # Combine relevant columns for embedding
    df['combined_text'] = (df['Hotel Name'].fillna('') + ' ' + 
                          df['Location'].fillna('') + ' ' + 
                          df['place'].fillna('') + ' ' +
                          df['Rating Description'].fillna(''))
    
    embeddings = model.encode(df['combined_text'].tolist())
    
    # Create FAISS index
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    
    # Save index and metadata
    faiss.write_index(index, os.path.join(VECTOR_STORE_DIR, 'hotel_index'))
    with open(os.path.join(VECTOR_STORE_DIR, 'hotel_metadata.pkl'), 'wb') as f:
        pickle.dump(df, f)
    
    print(f"Hotel embeddings created: {len(df)} records")


def create_activity_embeddings():
    """Create embeddings for activity data"""
    print("Creating activity embeddings...")
    df = pd.read_csv(os.path.join(PROJECT_ROOT, 'data', 'activities_data.csv'))
    
    # Combine relevant columns for embedding
    df['combined_text'] = (df['Place'].fillna('') + ': ' + 
                          df['Place_desc'].fillna('') + ' ' +
                          df['Category'].fillna('') + ' ' +
                          df['City'].fillna(''))
    
    embeddings = model.encode(df['combined_text'].tolist())
    
    # Create FAISS index
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    
    # Save index and metadata
    faiss.write_index(index, os.path.join(VECTOR_STORE_DIR, 'activity_index'))
    with open(os.path.join(VECTOR_STORE_DIR, 'activity_metadata.pkl'), 'wb') as f:
        pickle.dump(df, f)
    
    print(f"Activity embeddings created: {len(df)} records")


def create_travel_embeddings():
    """Create embeddings for travel data (flights and trains)"""
    print("Creating travel embeddings...")
    
    # Load flight data
    flight_df = pd.read_csv(os.path.join(PROJECT_ROOT, 'data', 'travel_flight_data.csv'))
    flight_df['data_type'] = 'flight'
    flight_df['combined_text'] = (flight_df['airline'].fillna('') + ' ' + 
                                  flight_df['flight'].fillna('') + ' ' +
                                  flight_df['source_city'].fillna('') + ' to ' +
                                  flight_df['destination_city'].fillna('') + ' ' +
                                  flight_df['class'].fillna(''))
    
    # Load train data
    train_df = pd.read_csv(os.path.join(PROJECT_ROOT, 'data', 'travel_data.csv'))
    train_df['data_type'] = 'train'
    train_df['combined_text'] = (train_df['provider'].fillna('') + ' ' + 
                                 train_df['train_name'].fillna('') + ' ' +
                                 train_df['source'].fillna('') + ' to ' +
                                 train_df['destination'].fillna('') + ' ' +
                                 train_df['class'].fillna(''))
    
    # Combine both datasets
    df = pd.concat([flight_df, train_df], ignore_index=True)
    
    embeddings = model.encode(df['combined_text'].tolist())
    
    # Create FAISS index
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    
    # Save index and metadata
    faiss.write_index(index, os.path.join(VECTOR_STORE_DIR, 'travel_index'))
    with open(os.path.join(VECTOR_STORE_DIR, 'travel_metadata.pkl'), 'wb') as f:
        pickle.dump(df, f)
    
    print(f"Travel embeddings created: {len(df)} records ({len(flight_df)} flights, {len(train_df)} trains)")


def build_all_vector_stores():
    """Build vector stores for all data types"""
    create_hotel_embeddings()
    create_activity_embeddings()
    create_travel_embeddings()
    print("\nAll vector stores created successfully!")


if __name__ == "__main__":
    build_all_vector_stores()