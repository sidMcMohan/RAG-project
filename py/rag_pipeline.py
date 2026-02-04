"""
RAG (Retrieval-Augmented Generation) Pipeline
Handles semantic search and response generation for the chatbot
"""

import os
import pickle
import json
import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility


class RAGPipeline:
    """
    RAG Pipeline for semantic search and response generation
    Uses pre-computed embeddings and sentence transformers for similarity matching
    """
    
    def __init__(
        self,
        embeddings_path: str = "Datasets/rag_embeddings.pkl",
        config_path: str = "chatbot_config.json",
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """
        Initialize RAG Pipeline
        
        Args:
            embeddings_path: Path to pickle file with pre-computed embeddings
            config_path: Path to configuration JSON
            model_name: Sentence transformer model name
        """
        # Resolve paths relative to parent directory (project root)
        base_dir = Path(__file__).parent.parent
        
        # Handle both absolute and relative paths
        embeddings_file = Path(embeddings_path)
        config_file = Path(config_path)
        
        if not embeddings_file.is_absolute():
            embeddings_path = str(base_dir / embeddings_path)
        if not config_file.is_absolute():
            config_path = str(base_dir / config_path)
        
        self.embeddings_path = embeddings_path
        self.config_path = config_path
        self.model_name = model_name
        self.model = None
        
        # Load configuration
        self.config = self._load_config()
        self.top_k = max(self.config.get("top_k", 7), 4)
        self.similarity_threshold = self.config.get("similarity_threshold", 0.5)
        self.use_milvus = self.config.get("use_milvus", True)
        self.milvus_collection = self.config.get("milvus_collection", "bitext_cases")
        
        # Load embeddings and case data
        self.cases_data = None
        self.embeddings = None
        self.collection = None
        self._milvus_initialized = False  # Track if Milvus was successfully initialized
        if not self.use_milvus:
            self._load_embeddings()
    
    def _load_config(self) -> Dict:
        """Load configuration from JSON file"""
        config_file = Path(self.config_path)
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self._get_default_config()
        else:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return default configuration"""
        return {
            "top_k": 7,
            "similarity_threshold": 0.5,
            "db_path": "chatbot_logs.db",
            "use_milvus": True,
            "milvus_collection": "bitext_cases",
            "milvus_uri": "",
            "milvus_token": "",
            "milvus_host": "localhost",
            "milvus_port": "19530",
            "milvus_secure": False
        }
    
    def _load_embeddings(self):
        """Load pre-computed embeddings from pickle file"""
        try:
            embeddings_file = Path(self.embeddings_path)
            print(f"📂 Attempting to load embeddings from: {embeddings_file.absolute()}")
            
            if embeddings_file.exists():
                with open(embeddings_file, 'rb') as f:
                    data = pickle.load(f)
                
                # Handle list of dicts format (new dataset)
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                    embeddings_list = []
                    self.cases_data = []
                    
                    for idx, item in enumerate(data):
                        question = str(item.get('question', ''))
                        answer = str(item.get('answer', ''))
                        item_id = str(item.get('id', idx))
                        
                        emb = item.get('embedding', [])
                        if isinstance(emb, list):
                            embeddings_list.append(np.array(emb, dtype=np.float32))
                        else:
                            embeddings_list.append(np.array(emb, dtype=np.float32))
                        
                        case = {
                            'id': item_id,
                            'title': question[:256],
                            'category': 'QA',
                            'description': question,
                            'solution': answer,
                            'full_text': answer,
                            'feedback_score': 0.0
                        }
                        self.cases_data.append(case)
                    
                    self.embeddings = np.array(embeddings_list)
                    print(f"✅ Loaded {len(self.embeddings)} embeddings from list of dicts with {len(self.cases_data)} cases")
                    if self.embeddings.size > 0:
                        print(f"   Embedding shape: {self.embeddings.shape}, Data samples: {len(self.cases_data)}")
                
                # Handle pandas DataFrame format
                elif isinstance(data, pd.DataFrame):
                    # Extract embeddings and case data
                    embeddings_list = data['embedding'].tolist()
                    self.embeddings = np.array([np.array(emb) if isinstance(emb, list) else emb for emb in embeddings_list])
                    
                    # Convert DataFrame rows to dictionaries for case data
                    self.cases_data = []
                    for idx, row in data.iterrows():
                        # Use description as title for better clarity
                        desc = str(row.get('description', ''))
                        # Truncate long descriptions for title
                        title = desc[:100] + '...' if len(desc) > 100 else desc
                        
                        case = {
                            'id': str(row.get('case_number', idx)),
                            'title': title,
                            'category': str(row.get('product_name', 'General')),
                            'description': desc,
                            'solution': str(row.get('technical_resolution', '')),
                            'full_text': str(row.get('full_text', '')),
                            'feedback_score': float(row.get('feedback_score', 0)) if pd.notna(row.get('feedback_score')) else 0
                        }
                        self.cases_data.append(case)
                    
                    print(f"✅ Loaded {len(self.embeddings)} embeddings from DataFrame with {len(self.cases_data)} cases")
                    if self.embeddings.size > 0:
                        print(f"   Embedding shape: {self.embeddings.shape}, Data samples: {len(self.cases_data)}")
                # Handle dict format
                elif isinstance(data, dict):
                    self.embeddings = np.array(data.get('embeddings', []))
                    self.cases_data = data.get('cases', [])
                    print(f"✅ Loaded {len(self.embeddings)} embeddings from dict")
                # Handle tuple format
                elif isinstance(data, tuple) and len(data) == 2:
                    self.embeddings, self.cases_data = data
                    self.embeddings = np.array(self.embeddings)
                    print(f"✅ Loaded {len(self.embeddings)} embeddings from tuple")
                else:
                    self.embeddings = np.array(data)
                    self.cases_data = []
                    print(f"✅ Loaded {len(self.embeddings)} embeddings (format: {type(data)})")
            else:
                print(f"⚠️  Embeddings file not found: {embeddings_file}")
                self.embeddings = np.array([])
                self.cases_data = []
                
        except Exception as e:
            print(f"❌ Error loading embeddings: {e}")
            import traceback
            traceback.print_exc()
            self.embeddings = np.array([])
            self.cases_data = []

    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """Normalize a vector to unit length for cosine similarity"""
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to Milvus VARCHAR max length"""
        if text is None:
            return ""
        if len(text) <= max_length:
            return text
        return text[:max_length]

    def _ensure_milvus_ready(self):
        """Lazy initialization: check and connect to Milvus if needed"""
        if not self.use_milvus or self._milvus_initialized:
            return self._milvus_initialized
        
        try:
            self._init_milvus()
            if not utility.has_collection(self.milvus_collection):
                print(f"❌ Milvus collection '{self.milvus_collection}' not found.")
                print("   Run: python populate_milvus.py to initialize Milvus")
                self._milvus_initialized = False
                return False
            
            self.collection = Collection(name=self.milvus_collection)
            # Check if collection has data
            num_entities = self.collection.num_entities
            if num_entities == 0:
                print(f"❌ Milvus collection is empty. Run: python populate_milvus.py")
                self._milvus_initialized = False
                return False
            
            # Load collection if not already loaded
            try:
                self.collection.load()
            except:
                pass  # Collection might already be loaded
            
            print(f"✅ Milvus ready: {num_entities} entities in collection")
            self._milvus_initialized = True
            return True
            
        except Exception as e:
            print(f"❌ Milvus connection failed: {e}")
            self._milvus_initialized = False
            return False

    def _init_milvus(self):
        """Initialize Milvus connection and collection"""
        milvus_uri = os.getenv("MILVUS_URI", self.config.get("milvus_uri", ""))
        milvus_token = os.getenv("MILVUS_TOKEN", self.config.get("milvus_token", ""))
        milvus_host = os.getenv("MILVUS_HOST", self.config.get("milvus_host", "localhost"))
        milvus_port = os.getenv("MILVUS_PORT", self.config.get("milvus_port", "19530"))
        milvus_secure = os.getenv("MILVUS_SECURE", str(self.config.get("milvus_secure", False))).lower() == "true"

        try:
            if milvus_uri:
                connections.connect(
                    alias="default",
                    uri=milvus_uri,
                    token=milvus_token or None,
                    secure=milvus_secure
                )
            else:
                connections.connect(alias="default", host=milvus_host, port=milvus_port)
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Milvus: {e}")

        try:
            collection_exists = utility.has_collection(self.milvus_collection)
            
            if not collection_exists:
                print(f"Creating new Milvus collection: {self.milvus_collection}")
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
                self.collection = Collection(name=self.milvus_collection, schema=schema)
                print("✅ Collection created successfully")
            else:
                print(f"Using existing Milvus collection: {self.milvus_collection}")
                self.collection = Collection(name=self.milvus_collection)
                # Only load if collection has data and index
                if self.collection.num_entities > 0:
                    self.collection.load()
                    print(f"✅ Loaded collection with {self.collection.num_entities} entities")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Milvus collection: {e}")

    def _ensure_milvus_index(self):
        """Create Milvus index if missing"""
        if not self.collection or self.collection.num_entities == 0:
            return  # Skip indexing for empty collection
        
        index_exists = any(idx.field_name == "embedding" for idx in self.collection.indexes)
        if not index_exists:
            print("Creating vector index...")
            index_params = {
                "index_type": "IVF_FLAT",
                "metric_type": "COSINE",
                "params": {"nlist": 1024}
            }
            self.collection.create_index(field_name="embedding", index_params=index_params)
            print("✅ Index created successfully")
            self.collection.load()
            print("✅ Collection loaded")

    def _ensure_milvus_data(self):
        """Insert data into Milvus if collection is empty"""
        if not self.collection:
            return
        if self.collection.num_entities > 0:
            print(f"✅ Milvus already has {self.collection.num_entities} entities")
            return
        if self.embeddings is None or self.cases_data is None or len(self.embeddings) == 0:
            raise RuntimeError("Embeddings data is empty; cannot populate Milvus.")

        print(f"📤 Uploading {len(self.embeddings)} embeddings to Milvus in batches...")
        batch_size = 1000  # Upload in smaller batches to avoid message size limit
        total_cases = len(self.embeddings)
        
        for start_idx in range(0, total_cases, batch_size):
            end_idx = min(start_idx + batch_size, total_cases)
            batch_cases = self.cases_data[start_idx:end_idx]
            batch_embs = self.embeddings[start_idx:end_idx]
            
            case_ids = []
            titles = []
            categories = []
            descriptions = []
            solutions = []
            full_texts = []
            vectors = []

            for case, emb in zip(batch_cases, batch_embs):
                case_ids.append(self._truncate_text(case.get("id", ""), 64))
                titles.append(self._truncate_text(case.get("title", ""), 256))
                categories.append(self._truncate_text(case.get("category", ""), 64))
                descriptions.append(self._truncate_text(case.get("description", ""), 1024))
                solutions.append(self._truncate_text(case.get("solution", ""), 4096))
                full_texts.append(self._truncate_text(case.get("full_text", ""), 4096))
                vec = np.array(emb, dtype=np.float32)
                vec = self._normalize_vector(vec)
                vectors.append(vec.tolist())

            self.collection.insert([
                case_ids,
                titles,
                categories,
                descriptions,
                solutions,
                full_texts,
                vectors
            ])
            print(f"  Uploaded batch {start_idx + 1}-{end_idx} ({end_idx}/{total_cases})")
        
        self.collection.flush()
        print(f"✅ Successfully uploaded {total_cases} cases to Milvus")

    def _search_milvus(self, query_embedding: np.ndarray, top_k: Optional[int] = None) -> Tuple[List[Dict], List[float]]:
        """Search Milvus for similar cases"""
        if top_k is None:
            top_k = self.top_k
        if not self.collection:
            return [], []

        query_vec = self._normalize_vector(query_embedding).astype(np.float32).tolist()
        search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
        results = self.collection.search(
            data=[query_vec],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["case_id", "title", "category", "description", "solution", "full_text"]
        )

        similar_cases = []
        similarity_scores = []
        for hit in results[0]:
            score = float(hit.score)
            entity = hit.entity
            similar_cases.append({
                "id": entity.get("case_id"),  # Milvus stores as case_id
                "title": entity.get("title"),
                "category": entity.get("category"),
                "description": entity.get("description"),
                "solution": entity.get("solution"),
                "full_text": entity.get("full_text")
            })
            similarity_scores.append(score)

        return similar_cases, similarity_scores
    
    def _get_model(self) -> SentenceTransformer:
        """Lazy load the sentence transformer model."""
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)
        return self.model

    def _get_query_embedding(self, query: str) -> np.ndarray:
        """
        Generate embedding for a query
        
        Args:
            query: User query text
            
        Returns:
            Embedding vector
        """
        embedding = self._get_model().encode(query, convert_to_numpy=True)
        return embedding
    
    def _search_similar_cases(
        self,
        query_embedding: np.ndarray,
        top_k: Optional[int] = None
    ) -> Tuple[List[int], List[float]]:
        """
        Find similar cases using cosine similarity
        
        Args:
            query_embedding: Embedding of the query
            top_k: Number of top results to return
            
        Returns:
            Tuple of (indices, similarity_scores)
        """
        if top_k is None:
            top_k = self.top_k
        
        if len(self.embeddings) == 0:
            return [], []
        
        # Ensure embeddings is 2D
        if len(self.embeddings.shape) == 1:
            embeddings_2d = self.embeddings.reshape(1, -1)
        else:
            embeddings_2d = self.embeddings
        
        # Ensure query embedding is 2D
        query_2d = query_embedding.reshape(1, -1) if len(query_embedding.shape) == 1 else query_embedding
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_2d, embeddings_2d)[0]
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        top_scores = similarities[top_indices]
        
        # Filter by threshold
        valid_indices = []
        valid_scores = []
        for idx, score in zip(top_indices, top_scores):
            if score >= self.similarity_threshold:
                valid_indices.append(idx)
                valid_scores.append(float(score))
        
        return valid_indices, valid_scores
    
    def _format_response(
        self,
        similar_cases: List[Dict],
        similarity_scores: List[float],
        query: str
    ) -> Tuple[str, Dict]:
        """
        Format response using similar cases
        
        Args:
            similar_cases: List of similar case dictionaries
            similarity_scores: List of similarity scores
            query: Original query
            
        Returns:
            Tuple of (response_text, metadata)
        """
        if not similar_cases:
            response = (
                "I couldn't find a direct match for your query in our knowledge base. "
                "Please provide more details, or contact our support team for assistance."
            )
            metadata = {
                "matches_found": 0,
                "confidence": 0.0,
                "message": "No similar cases found"
            }
            return response, metadata
        
        # Build response from best match
        best_case = similar_cases[0]
        best_score = similarity_scores[0]

        if best_score < self.similarity_threshold:
            response = (
                "I couldn't find a direct match for your query in our knowledge base. "
                "Please provide more details, or contact our support team for assistance."
            )
            metadata = {
                "matches_found": 0,
                "confidence": float(best_score),
                "message": "No similar cases found"
            }
            return response, metadata
        
        # Prepare response text
        case_id = best_case.get('id', 'Unknown')
        case_title = best_case.get('title', 'Support Case')
        case_category = best_case.get('category', 'General')
        case_solution = best_case.get('solution', best_case.get('content', 'No solution available'))
        
        # Build confidence message
        confidence_msg = ""
        if best_score >= 0.85:
            confidence_msg = "I found a highly relevant match"
        elif best_score >= 0.70:
            confidence_msg = "I found a relevant match"
        elif best_score >= 0.55:
            confidence_msg = "I found a potentially relevant match"
        else:
            confidence_msg = "I found a somewhat related case"
        
        response = (
            f"{confidence_msg} for your query (confidence: {best_score:.1%}):\n\n"
            f"**Case ID:** {case_id}\n\n"
            f"**Issue:** {case_title}\n\n"
            f"**Resolution:**\n"
            f"{case_solution}"
        )
        
        # Add references to other similar cases if available
        if len(similar_cases) > 1:
            response += f"\n\n---\n**Other related cases you might find helpful:**\n"
            for i, (case, score) in enumerate(zip(similar_cases[1:4], similarity_scores[1:4]), 1):
                ref_id = case.get('id', f'case-{i}')
                ref_description = case.get('description', case.get('title', 'No description available'))
                
                response += (
                    f"\n{i}. **Case ID:** {ref_id} (similarity: {score:.1%})"
                    f"\n**Issue:**\n{ref_description}"
                )
        
        # Prepare metadata
        metadata = {
            "matches_found": len(similar_cases),
            "confidence": float(best_score),
            "top_case": {
                "id": case_id,
                "title": case_title,
                "similarity_score": float(best_score)
            },
            "related_cases": [
                {
                    "id": case.get('id', f'case_{j}'),
                    "title": case.get('title', 'Untitled'),
                    "similarity_score": float(similarity_scores[j])
                }
                for j, case in enumerate(similar_cases[:5])
            ]
        }
        
        return response, metadata
    
    def generate_response(self, query: str) -> Tuple[str, Dict]:
        """
        Generate response for a user query
        
        Args:
            query: User query text
            
        Returns:
            Tuple of (response_text, metadata_dict)
        """
        try:
            # If Milvus is required, check it's available
            if self.use_milvus:
                if not self._ensure_milvus_ready():
                    return (
                        "❌ Milvus database is not available. Please ensure Milvus is running and properly populated.\n"
                        "Run: python populate_milvus.py",
                        {"error": "Milvus not available", "confidence": 0.0, "uses_milvus": False}
                    )
                print(f"🔍 Searching Milvus with query: {query[:50]}...")
                query_embedding = self._get_query_embedding(query)
                similar_cases, similarity_scores = self._search_milvus(query_embedding)
            else:
                # This should not happen if use_milvus is enforced
                return (
                    "❌ Milvus is disabled in configuration. Please enable it.",
                    {"error": "Milvus disabled", "confidence": 0.0}
                )
            
            # Format response
            response, metadata = self._format_response(similar_cases, similarity_scores, query)
            metadata["uses_milvus"] = True
            
            return response, metadata
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return (
                f"❌ Error: {str(e)}",
                {"error": str(e), "confidence": 0.0, "uses_milvus": False}
            )
