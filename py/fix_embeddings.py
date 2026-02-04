"""
Fix RAG by generating embeddings for the FULL Bitext dataset
Current issue: Only 1000 ORDER cases, need all 27K+ cases across all categories
"""

print("="*70)
print("FIXING RAG PIPELINE - LOADING FULL DATASET")
print("="*70)

# Step 1: Try to load the full dataset
try:
    from datasets import load_dataset
    import pandas as pd
    from sentence_transformers import SentenceTransformer
    import pickle
    from tqdm import tqdm
    
    print("\n1. Loading full Bitext dataset from HuggingFace...")
    ds = load_dataset("bitext/Bitext-customer-support-llm-chatbot-training-dataset")
    dataset = ds['train']
    print(f"   ✅ Loaded {len(dataset)} cases")
    
    # Convert to DataFrame
    df = pd.DataFrame(dataset)
    
    # Clean data
    df = df.dropna(subset=['instruction', 'response'])
    df['instruction'] = df['instruction'].astype(str).str.strip()
    df['response'] = df['response'].astype(str).str.strip()
    
    # Create structured format
    df['case_number'] = range(1, len(df) + 1)
    df['product_name'] = df['category']
    df['description'] = df['instruction']
    df['technical_resolution'] = df['response']
    df['full_text'] = "Problem: " + df['description'] + " Resolution: " + df['technical_resolution']
    df['suggested_resolution'] = ""
    df['resolution_execution_log'] = ""
    df['feedback_score'] = None
    
    print("\n2. Category distribution:")
    print(df['category'].value_counts())
    print(f"\nTotal categories: {df['category'].nunique()}")
    print(f"Total cases: {len(df)}")
    
    # Generate embeddings
    print("\n3. Loading embedding model...")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    print("\n4. Generating embeddings (this will take a few minutes)...")
    texts = df['full_text'].tolist()
    
    embeddings_list = []
    batch_size = 32
    for i in tqdm(range(0, len(texts), batch_size), desc="Progress"):
        batch = texts[i:i+batch_size]
        emb = model.encode(batch, convert_to_numpy=True, show_progress_bar=False)
        embeddings_list.extend(emb.tolist())
    
    df['embedding'] = embeddings_list
    
    # Save outputs
    output_cols = [
        "case_number", "product_name", "description", "technical_resolution",
        "suggested_resolution", "resolution_execution_log", "feedback_score",
        "full_text", "embedding"
    ]
    df_out = df[output_cols]
    
    print("\n5. Saving to pickle...")
    df_out.to_pickle("bitext_cases_with_embeddings.pkl")
    
    print("\n6. Saving CSV (without embeddings)...")
    df_out.drop(columns=['embedding']).to_csv("csv/preprocessed_bitext_casesS.csv", index=False)
    
    print("\n" + "="*70)
    print("✅ SUCCESS!")
    print("="*70)
    print(f"Total cases: {len(df_out)}")
    print(f"Categories: {df_out['product_name'].nunique()}")
    print("\nYour RAG now has access to ALL cases across ALL categories!")
    print("Restart Streamlit to use the new dataset.")
    
except ImportError:
    print("\n❌ Missing required package: 'datasets'")
    print("Installing required packages...")
    import subprocess
    import sys
    
    subprocess.check_call([sys.executable, "-m", "pip", "install", "datasets", "tqdm"])
    print("\n✅ Packages installed! Please run this script again.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
