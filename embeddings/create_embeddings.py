import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import pickle

def build_vector_store():
    df = pd.read_csv('../data/raw/activities_data.csv')
    # Combine Place and Description for embedding
    df['combined_text'] = df['Place'] + ": " + df['Place_desc']
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(df['combined_text'].tolist())
    
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    
    # Save files
    faiss.write_index(index, "vector_store/faiss_index")
    with open("vector_store/metadata.pkl", "wb") as f:
        pickle.dump(df, f)

if __name__ == "__main__":
    build_vector_store()