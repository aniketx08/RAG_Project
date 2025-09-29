from langchain.embeddings.base import Embeddings
from typing import List
from utils import log_message
import ollama

class NomicEmbeddings(Embeddings):
    def __init__(self, model_name="nomic-embed-text:v1.5"):
        self.model_name = model_name
        self._dimension = None
        log_message(f"Initialized NomicEmbeddings with model: {model_name}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents with detailed logging"""
        if not texts:
            log_message("No texts to embed")
            return []
            
        embeddings_list = []
        log_message(f"Generating embeddings for {len(texts)} document chunks...")
        
        # Log text length statistics
        text_lengths = [len(text) for text in texts]
        avg_length = sum(text_lengths) / len(text_lengths)
        max_length = max(text_lengths)
        min_length = min(text_lengths)
        log_message(f"Text length stats - Avg: {avg_length:.1f}, Min: {min_length}, Max: {max_length}")
        
        for i, text in enumerate(texts):
            if i % 5 == 0:  # More frequent progress updates
                log_message(f"Processing chunk {i+1}/{len(texts)} (length: {len(text)})")
            
            try:
                # Show sample of text being embedded
                if i < 3:
                    log_message(f"Embedding chunk {i+1}: '{text[:100]}...'")
                
                response = ollama.embeddings(prompt=text, model=self.model_name)
                embedding = response['embedding']
                embeddings_list.append(embedding)
                
                # Cache dimension on first call
                if self._dimension is None:
                    self._dimension = len(embedding)
                    log_message(f"Embedding dimension: {self._dimension}")
                    
            except Exception as e:
                log_message(f"Error generating embedding for chunk {i+1}: {str(e)}")
                log_message(f"Failed text (first 200 chars): {text[:200]}")
                raise
        
        log_message(f"Successfully generated {len(embeddings_list)} embeddings")
        return embeddings_list

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query with logging"""
        try:
            log_message(f"Embedding query (length: {len(text)}): '{text[:100]}...'")
            
            response = ollama.embeddings(prompt=text, model=self.model_name)
            embedding = response['embedding']
            
            if self._dimension is None:
                self._dimension = len(embedding)
                log_message(f"Query embedding dimension: {self._dimension}")
                
            log_message(f"Successfully generated query embedding")
            return embedding
            
        except Exception as e:
            log_message(f"Error generating query embedding: {str(e)}")
            log_message(f"Failed query: {text}")
            raise

    @property
    def dimension(self):
        """Get embedding dimension"""
        if self._dimension is None:
            log_message("Getting dimension with sample embedding...")
            sample_embedding = self.embed_query("sample")
            self._dimension = len(sample_embedding)
        return self._dimension