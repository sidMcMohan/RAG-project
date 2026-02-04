import pandas as pd
import pickle
from sentence_transformers import SentenceTransformer
from pathlib import Path

def generate_embeddings():
    # File paths
    base_dir = Path(__file__).parent
    input_csv = base_dir / "rag_mini_bioasq_test.csv"
    output_pkl = base_dir / "rag_embeddings.pkl"
    
    print(f"Loading data from {input_csv}...")
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"Error: File {input_csv} not found.")
        return

    print("Data loaded successfully.")
    print(df.head())
    
    # Initialize model
    model_name = "all-MiniLM-L6-v2"
    print(f"Loading model: {model_name}...")
    model = SentenceTransformer(model_name)
    
    # Generate embeddings
    # We are embedding the 'question' column for better question matching
    print("Generating embeddings for 'question' column...")
    
    # Ensure there are no NaN values in the target column
    df['question'] = df['question'].fillna("")
    
    embeddings = model.encode(df['question'].tolist(), show_progress_bar=True)
    
    # Create a list of dictionaries to store the data
    # This format is flexible for Milvus insertion later
    data_to_save = []
    
    for idx, row in df.iterrows():
        item = {
            'id': row['id'], 
            'question': row['question'],
            'answer': row['answer'],
            'relevant_passage_ids': row['relevant_passage_ids'],
            'embedding': embeddings[idx]
        }
        data_to_save.append(item)
        
    print(f"Embeddings generated. Dimensions: {len(embeddings[0])}")
    
    # Save to pickle
    print(f"Saving to {output_pkl}...")
    with open(output_pkl, 'wb') as f:
        pickle.dump(data_to_save, f)
        
    print("Process complete.")

if __name__ == "__main__":
    generate_embeddings()
