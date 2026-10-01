from typing import List, Dict, Any, Optional
import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from pypdf import PdfReader
import logging

logger = logging.getLogger(__name__)


class RAGService:
    """RAG service for knowledge retrieval using FAISS"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", index_path: str = "./data/faiss"):
        self.model_name = model_name
        self.index_path = index_path
        self.model: Optional[SentenceTransformer] = None
        self.index: Optional[faiss.Index] = None
        self.documents: List[Dict[str, Any]] = []
    
    def load_model(self):
        """Load the embedding model"""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded")
    
    def load_index(self):
        """Load or create FAISS index"""
        if self.index is None:
            index_file = os.path.join(self.index_path, "index.faiss")
            docs_file = os.path.join(self.index_path, "documents.json")
            
            if os.path.exists(index_file) and os.path.exists(docs_file):
                # Load existing index
                logger.info("Loading existing FAISS index")
                self.index = faiss.read_index(index_file)
                
                import json
                with open(docs_file, 'r') as f:
                    self.documents = json.load(f)
                logger.info(f"Loaded {len(self.documents)} documents")
            else:
                # Create new index
                logger.info("Creating new FAISS index")
                self.index = faiss.IndexFlatL2(384)  # MiniLM dimension
                self.documents = []
    
    def add_document(self, text: str, metadata: Dict[str, Any]):
        """Add a document to the index"""
        if self.model is None:
            self.load_model()
        if self.index is None:
            self.load_index()
        
        # Chunk the document
        chunks = self._chunk_text(text)
        
        for chunk in chunks:
            # Generate embedding
            embedding = self.model.encode([chunk])[0]
            
            # Add to index
            self.index.add(np.array([embedding]).astype('float32'))
            
            # Store document
            self.documents.append({
                "text": chunk,
                "metadata": metadata
            })
        
        logger.info(f"Added {len(chunks)} chunks to index")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        if self.model is None:
            self.load_model()
        if self.index is None:
            self.load_index()
        
        if len(self.documents) == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.model.encode([query])[0]
        
        # Search
        distances, indices = self.index.search(
            np.array([query_embedding]).astype('float32'),
            min(top_k, len(self.documents))
        )
        
        # Return results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                results.append({
                    "text": self.documents[idx]["text"],
                    "metadata": self.documents[idx]["metadata"],
                    "score": float(1 / (1 + dist))  # Convert distance to similarity
                })
        
        return results
    
    def save_index(self):
        """Save index to disk"""
        if self.index is None:
            return
        
        os.makedirs(self.index_path, exist_ok=True)
        
        # Save index
        index_file = os.path.join(self.index_path, "index.faiss")
        faiss.write_index(self.index, index_file)
        
        # Save documents
        import json
        docs_file = os.path.join(self.index_path, "documents.json")
        with open(docs_file, 'w') as f:
            json.dump(self.documents, f)
        
        logger.info("Index saved to disk")
    
    def _chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """Chunk text into smaller pieces"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def process_pdf(self, pdf_path: str, metadata: Dict[str, Any]) -> str:
        """Extract text from PDF"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return ""
