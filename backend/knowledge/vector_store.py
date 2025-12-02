"""
Vector Store Module for One Development Knowledge Base
Provides a unified interface to ChromaDB for storing and retrieving documents.
"""

import chromadb
from chromadb.config import Settings
import os

# Singleton instance
_vector_store = None


class VectorStore:
    """Wrapper around ChromaDB for knowledge base operations"""
    
    def __init__(self):
        # Path to ChromaDB storage
        self.db_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'chroma_db'
        )
        os.makedirs(self.db_path, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=False
            )
        )
        
        # Get or create the collection
        try:
            self.collection = self.client.get_collection("onedevelopment_knowledge")
        except:
            self.collection = self.client.create_collection(
                name="onedevelopment_knowledge",
                metadata={"description": "Knowledge base for One Development"}
            )
        
        print(f"✅ VectorStore initialized with {self.collection.count()} documents")
    
    def add_texts(self, texts: list, metadatas: list = None):
        """Add texts to the vector store"""
        if not texts:
            return
        
        # Generate unique IDs
        import uuid
        ids = [str(uuid.uuid4()) for _ in texts]
        
        # Ensure metadatas is the right length
        if metadatas is None:
            metadatas = [{}] * len(texts)
        
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        return ids
    
    def similarity_search(self, query: str, k: int = 5):
        """Search for similar documents"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k
            )
            
            # Convert to document-like objects
            documents = []
            if results and results.get('documents'):
                for i, doc in enumerate(results['documents'][0]):
                    # Create a simple document object
                    class Document:
                        def __init__(self, content, metadata):
                            self.page_content = content
                            self.metadata = metadata
                    
                    metadata = results['metadatas'][0][i] if results.get('metadatas') else {}
                    documents.append(Document(doc, metadata))
            
            return documents
            
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []
    
    def get_count(self):
        """Get number of documents in the store"""
        return self.collection.count()


def get_vector_store() -> VectorStore:
    """Get or create the singleton VectorStore instance"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store

