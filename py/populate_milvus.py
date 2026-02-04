"""
Standalone script to populate Milvus with embeddings
Run this BEFORE starting the chatbot to initialize the vector database
"""

import pickle
import json
import numpy as np
from pathlib import Path
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
import time

def populate_milvus():
    """Populate Milvus with embeddings from pickle file"""
    
    # Configuration
    base_dir = Path(__file__).parent.parent  # Go up to root directory
    embeddings_path = base_dir / "Datasets" / "rag_embeddings.pkl"
    config_path = base_dir / "chatbot_config.json"
    
    # Load config
    with open(config_path) as f:
        config = json.load(f)
    
    milvus_host = config.get("milvus_host", "localhost")
    milvus_port = config.get("milvus_port", "19530")
    milvus_collection = config.get("milvus_collection", "bitext_cases")
    milvus_uri = config.get("milvus_uri", "")
    milvus_token = config.get("milvus_token", "")
    milvus_secure = config.get("milvus_secure", False)
    
    print(f"📋 Milvus Configuration:")
    print(f"   Host: {milvus_host}:{milvus_port}")
    print(f"   Collection: {milvus_collection}")
    
    # Connect to Milvus
    print("\n🔗 Connecting to Milvus...")
    try:
        if milvus_uri:
            connections.connect(
                alias="default",
                uri=milvus_uri,
                token=milvus_token or None,
                secure=milvus_secure
            )
        else:
            connections.connect(alias="default", host=milvus_host, port=int(milvus_port))
        print("✅ Connected to Milvus successfully")
    except Exception as e:
        print(f"❌ Failed to connect to Milvus: {e}")
        print("   Make sure Milvus container is running:")
        print("   docker run -d --name milvus-standalone -p 19530:19530 -p 9091:9091 \\")
        print("     -e ETCD_USE_EMBED=true -e ETCD_DATA_DIR=/var/lib/milvus/etcd \\")
        print("     -e COMMON_STORAGETYPE=local milvusdb/milvus:v2.4.1 milvus run standalone")
        return False
    
    # Load embeddings
    print(f"\n📂 Loading embeddings from {embeddings_path}...")
    try:
        with open(embeddings_path, 'rb') as f:
            df = pickle.load(f)
        print(f"✅ Loaded {len(df)} cases from pickle file")
    except Exception as e:
        print(f"❌ Failed to load embeddings: {e}")
        return False
    
    # Create or get collection
    print(f"\n📦 Checking Milvus collection '{milvus_collection}'...")
    try:
        if utility.has_collection(milvus_collection):
            collection = Collection(name=milvus_collection)
            print(f"   Collection exists with {collection.num_entities} entities")
            if collection.num_entities >= len(df):
                print(f"✅ Collection is already fully populated!")
                return True
            print(f"   Need to add {len(df) - collection.num_entities} more entities")
        else:
            print(f"   Creating new collection...")
            fields = [
                FieldSchema(name="case_id", dtype=DataType.VARCHAR, is_primary=True, auto_id=False, max_length=64),
                FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=256),
                FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=64),
                FieldSchema(name="description", dtype=DataType.VARCHAR, max_length=1024),
                FieldSchema(name="solution", dtype=DataType.VARCHAR, max_length=4096),
                FieldSchema(name="full_text", dtype=DataType.VARCHAR, max_length=4096),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384)
            ]
            schema = CollectionSchema(fields, description="Bitext support cases")
            collection = Collection(name=milvus_collection, schema=schema)
            print(f"✅ Created new collection")
    except Exception as e:
        print(f"❌ Failed to create/access collection: {e}")
        return False
    
    # Upload data in batches
    print(f"\n📤 Uploading {len(df)} embeddings to Milvus...")
    batch_size = 1000
    total_uploaded = 0
    
    try:
        for start_idx in range(0, len(df), batch_size):
            end_idx = min(start_idx + batch_size, len(df))
            batch_items = df[start_idx:end_idx]
            
            case_ids = []
            titles = []
            categories = []
            descriptions = []
            solutions = []
            full_texts = []
            vectors = []
            
            for item in batch_items:
                # New format: list of dicts with id, question, answer, embedding
                item_id = str(item.get('id', ''))[:64]
                question = str(item.get('question', ''))
                answer = str(item.get('answer', ''))
                
                case_ids.append(item_id)
                titles.append(question[:256])
                categories.append('QA')
                descriptions.append(question[:1024])
                solutions.append(answer[:4096])
                full_texts.append(answer[:4096])
                
                emb = item.get('embedding', [])
                if isinstance(emb, list):
                    emb = np.array(emb, dtype=np.float32)
                elif isinstance(emb, np.ndarray):
                    emb = emb.astype(np.float32)
                else:
                    emb = np.array(emb, dtype=np.float32)
                
                # Normalize vector
                norm = np.linalg.norm(emb)
                if norm > 0:
                    emb = emb / norm
                vectors.append(emb.tolist())
            
            collection.insert([
                case_ids,
                titles,
                categories,
                descriptions,
                solutions,
                full_texts,
                vectors
            ])
            total_uploaded += len(batch_items)
            print(f"   ✓ Uploaded batch {start_idx + 1}-{end_idx} ({total_uploaded}/{len(df)})")
        
        collection.flush()
        print(f"\n✅ Successfully uploaded {total_uploaded} cases to Milvus")
        
    except Exception as e:
        print(f"❌ Failed to upload data: {e}")
        return False
    
    # Create index
    print(f"\n🔍 Creating index on embeddings...")
    try:
        # Check if index already exists
        indexes = collection.indexes
        index_exists = any(idx.field_name == "embedding" for idx in indexes)
        
        if not index_exists:
            index_params = {
                "index_type": "IVF_FLAT",
                "metric_type": "COSINE",
                "params": {"nlist": 1024}
            }
            collection.create_index(field_name="embedding", index_params=index_params)
            print("✅ Index created successfully")
        else:
            print("✅ Index already exists")
        
        # Load collection
        collection.load()
        print("✅ Collection loaded into memory")
        
    except Exception as e:
        print(f"⚠️  Warning: Index creation or loading failed: {e}")
        print("   Collection is still usable, but searches may be slower")
    
    print(f"\n🎉 Milvus is ready!")
    print(f"   Collection: {milvus_collection}")
    print(f"   Entities: {collection.num_entities}")
    print(f"   Status: Ready for search\n")
    return True

if __name__ == "__main__":
    success = populate_milvus()
    exit(0 if success else 1)
