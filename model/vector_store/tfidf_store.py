# Purpose: Manages hybrid vector store with dense and sparse retrieval
# Why: Combines benefits of semantic and keyword search for better results

from swarmauri.standard.documents.concrete.Document import Document
import json
import os
import numpy as np
import faiss
import re
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from utils.logger import logger
from swarmauri.standard.vector_stores.base.VectorStoreBase import VectorStoreBase

class VectorStoreManager:
    """Handles hybrid vector store with dense and sparse retrieval."""
    
    def __init__(self, json_path="constitution_chunks.json"):
        """Initializes hybrid vector store."""
        print("Initializing Hybrid Vector Store")
        
        # Create local cache
        cache_dir = os.path.join(os.getcwd(), ".cache", "models")
        os.makedirs(cache_dir, exist_ok=True)
        
        # Use efficient MiniLM model (small download)
        self.model = SentenceTransformer(
            'all-MiniLM-L6-v2',
            cache_folder=cache_dir
        )
        self.dimension = 384
        self.index = faiss.IndexFlatL2(self.dimension)
        
        # Sparse retrieval
        self.bm25 = None
        self.doc_texts = []
        
        self.documents = []
        self.json_path = json_path
        
        if os.path.exists(json_path):
            print(f"Found {json_path}, loading...")
            self.load_and_populate()
        else:
            print(f"Warning: {json_path} not found")
    
    def load_and_populate(self):
        """Populates both dense and sparse indexes."""
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                chunk_data = json.load(f)
            
            print(f"Loading {len(chunk_data)} chunks")
            
            self.documents = []
            embeddings = []
            self.doc_texts = []
            
            for idx, chunk_dict in enumerate(chunk_data):
                content = chunk_dict["content"]
                metadata = chunk_dict["metadata"]
                
                doc = Document(
                    content=content,
                    metadata={
                        "id": "constitution",
                        "chunk_id": idx,
                        "chapter": metadata.get("chapter", "UNKNOWN"),
                        "is_fundamental_rights": metadata.get("is_fundamental_rights", 0)
                    }
                )
                self.documents.append(doc)
                self.doc_texts.append(content)
                
                # Generate embedding
                embedding = self.model.encode(content)
                embeddings.append(embedding)
            
            # Create dense index
            embeddings = np.array(embeddings).astype('float32')
            self.index.add(embeddings)
            
            # Create sparse index
            tokenized_corpus = [doc.split() for doc in self.doc_texts]
            self.bm25 = BM25Okapi(tokenized_corpus)
            
            print(f"Hybrid index created with {len(self.documents)} documents")
            logger.info(f"Vector store populated with {len(self.documents)} documents")
        except Exception as e:
            print(f"Error loading chunks: {str(e)}")
            logger.error(f"Failed to populate vector store: {str(e)}")
    
    def dense_retrieve(self, query, top_k):
        """Retrieves using dense embeddings."""
        query_embedding = self.model.encode([query])[0]
        distances, indices = self.index.search(np.array([query_embedding]).astype('float32'), top_k)
        return [self.documents[i] for i in indices[0]]
    
    def sparse_retrieve(self, query, top_k):
        """Retrieves using BM25."""
        tokenized_query = query.split()
        doc_scores = self.bm25.get_scores(tokenized_query)
        best_indices = np.argsort(doc_scores)[::-1][:top_k]
        return [self.documents[i] for i in best_indices]
    
    def hybrid_retrieve(self, query, top_k=10):
        """Combines dense and sparse retrieval results."""
        # Get both result sets
        dense_results = self.dense_retrieve(query, top_k*2)
        sparse_results = self.sparse_retrieve(query, top_k*2)
        
        # Combine and deduplicate
        combined = {doc.metadata['chunk_id']: doc for doc in dense_results + sparse_results}
        all_results = list(combined.values())
        
        # Rerank by relevance to query
        query_embedding = self.model.encode(query)
        scored_results = []
        for doc in all_results:
            doc_embedding = self.model.encode(doc.content)
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding))
            
            # Adjust score based on query type
            rights_keywords = ["rights", "human rights", "fundamental rights", "freedom", "liberty"]
            if any(keyword in query.lower() for keyword in rights_keywords):
                boost = 0.5 if doc.metadata['is_fundamental_rights'] == 1 else 0
            else:
                boost = -0.5 if doc.metadata['is_fundamental_rights'] == 1 else 0
            score = similarity + boost
            scored_results.append((doc, score))
        
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scored_results[:top_k]]
    
    def retrieve(self, query, top_k=10):
        """Wrapper for hybrid retrieval to match expected interface."""
        return self.hybrid_retrieve(query, top_k=top_k)
    
    def get_vector_store(self):
        """Returns a VectorStoreBase-compatible interface."""
        class HybridVectorStore(VectorStoreBase):
            def __init__(self, manager):
                self._manager = manager  # Store manager as a protected attribute
            
            def retrieve(self, query, top_k=10):
                return self._manager.hybrid_retrieve(query, top_k)
            
            def add_document(self, document):
                raise NotImplementedError("Adding documents is not supported in this wrapper.")
            
            def add_documents(self, documents):
                raise NotImplementedError("Adding multiple documents is not supported in this wrapper.")
            
            def delete_document(self, document_id):
                raise NotImplementedError("Deleting documents is not supported in this wrapper.")
            
            def get_all_documents(self):
                raise NotImplementedError("Getting all documents is not supported in this wrapper.")
            
            def get_document(self, document_id):
                raise NotImplementedError("Getting a specific document is not supported in this wrapper.")
            
            def update_document(self, document):
                raise NotImplementedError("Updating documents is not supported in this wrapper.")
        
        return HybridVectorStore(self)
    
    def test_retrieval(self, query, top_k=10):
        """Tests retrieval with detailed output."""
        print(f"\n{'='*50}")
        print(f"Testing query: '{query}'")
        print(f"{'='*50}")
        
        if not self.documents:
            print("Vector store is empty")
            return []
        
        results = self.hybrid_retrieve(query, top_k)
        
        print(f"Retrieved {len(results)} documents:")
        for i, doc in enumerate(results, 1):
            meta = doc.metadata
            print(f"\nResult {i}: [Chapter: {meta['chapter']}] [Rights: {meta['is_fundamental_rights']}]")
            print(f"Content: {doc.content[:150]}...")
        
        return results

if __name__ == "__main__":
    vsm = VectorStoreManager()
    test_queries = [
        "What are my fundamental human rights?",
        "How is the president elected?",
        "What are the requirements to run for governor?",
        "Explain the judicial appointment process",
        "What is the role of the National Assembly?",
        "Can I own land in Nigeria?"
    ]
    
    for query in test_queries:
        vsm.test_retrieval(query)