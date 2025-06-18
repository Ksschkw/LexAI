# Purpose: Manages the TF-IDF vector store for document retrieval.
# Why: Explicitly separates vector storage for modularity and scalability.

from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.vector_stores.concrete.TfidfVectorStore import TfidfVectorStore
import json
import os
from utils.logger import logger

class VectorStoreManager:
    """Handles initialization and population of the TF-IDF vector store."""
    
    def __init__(self, json_path="constitution_chunks.json"):
        """Initializes an empty TF-IDF vector store and loads chunks if file exists.
        
        Args:
            json_path (str): Path to the JSON file containing document chunks.
        """
        self.vector_store = TfidfVectorStore()
        self.json_path = json_path
        print("Initializing VectorStoreManager")
        if os.path.exists(json_path):
            print(f"Found {json_path}, loading...")
            self.load_and_populate()
        else:
            logger.warning(f"JSON file not found at {json_path} - vector store remains empty")
            print(f"Warning: {json_path} not found")
    
    def load_and_populate(self):
        """Loads chunks from JSON file and populates the vector store."""
        logger.info(f"Loading chunks from {self.json_path}")
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                chunks = json.load(f)
            print(f"Loading {len(chunks)} chunks from {self.json_path}")
            self.add_documents(chunks)
            logger.info(f"Populated vector store with {len(chunks)} chunks")
            print("Documents added to vector store")
        except Exception as e:
            logger.error(f"Failed to load or populate vector store: {str(e)}")
    
    def add_documents(self, chunks):
        """Adds document chunks to the vector store.
        
        Args:
            chunks (list): List of text chunks from DocumentManager or JSON.
        """
        documents = []
        for i, chunk in enumerate(chunks):
            doc = Document(
                content=chunk,
                metadata={"id": "constitution", "chunk_id": i}
            )
            documents.append(doc)
        self.vector_store.add_documents(documents)
        print(f"Successfully added {len(documents)} documents")
        logger.debug(f"Added {len(documents)} documents to vector store")
    
    def get_store(self):
        """Returns the populated vector store.
        
        Returns:
            TfidfVectorStore: The vector store instance.
        """
        return self.vector_store
    
    def test_retrieval(self, query, top_k=1):
        """Tests retrieval from the vector store.
        
        Args:
            query (str): Query to retrieve documents for.
            top_k (int): Number of top results to return.
        Returns:
            list: Retrieved documents.
        """
        if not self.vector_store.documents:
            logger.warning("Vector store is empty - no retrieval possible")
            return []
        return self.vector_store.retrieve(query, top_k=top_k)

if __name__ == "__main__":
    # Test the vector store
    logger.info("Running vector store test")
    vsm = VectorStoreManager()
    if vsm.vector_store.documents:
        test_query = "What are my rights?"
        results = vsm.test_retrieval(test_query)
        print("Testing retrieval...")
        logger.info(f"Test retrieval for '{test_query}' returned {len(results)} results")
        for i, doc in enumerate(results):
            logger.info(f"Result {i + 1}: {doc.content[:50]}...")
        
    else:
        logger.info("No documents loaded - populate vector store first")