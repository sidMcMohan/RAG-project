import pandas as pd
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

# Load CSV
print("Loading CSV...")
df = pd.read_csv('csv/preprocessed_bitext_casesS.csv')
print(f"Loaded {len(df)} cases")
print(f"Columns: {df.columns.tolist()}")
print(f"First row:\n{df.iloc[0]}")

# Generate embeddings from cases
print("\nLoading SentenceTransformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

print(f"Generating embeddings for {len(df)} cases...")
embeddings = model.encode(df['full_text'].tolist(), show_progress_bar=True)
print(f"Generated shape: {embeddings.shape}")

# Create dataframe with embeddings
print("Creating embeddings dataframe...")
embeddings_df = df.copy()
embeddings_df['embedding'] = [emb for emb in embeddings]

# Save as pickle
print("Saving to pickle...")
with open('bitext_cases_with_embeddings.pkl', 'wb') as f:
    pickle.dump(embeddings_df, f)
print("✅ Done!")
