from langchain.embeddings.base import Embeddings
from tqdm import tqdm
import sys
from utils import log_message

class NomicEmbeddings(Embeddings):
    def embed_documents(self, texts):
        from ollama import embeddings as ollama_emb
        embeddings_list = []
        log_message(f"Generating embeddings for {len(texts)} documents...")
        
        for i, t in enumerate(tqdm(texts, desc="Generating embeddings", file=sys.stdout)):
            log_message(f"Embedding document {i+1}/{len(texts)}: {t[:50]}...", streamlit_output=False)
            embedding = ollama_emb(prompt=t, model="nomic-embed-text:v1.5")['embedding']
            log_message(f"Generated embedding with {len(embedding)} dimensions", streamlit_output=False)
            embeddings_list.append(embedding)
        
        return embeddings_list

    def embed_query(self, text):
        from ollama import embeddings as ollama_emb
        log_message(f"Generating query embedding for: {text[:50]}...")
        embedding = ollama_emb(prompt=text, model="nomic-embed-text:v1.5")['embedding']
        log_message(f"Query embedding dimensions: {len(embedding)}")
        return embedding