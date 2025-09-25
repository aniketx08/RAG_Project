from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from langserve import add_routes
import tempfile
import os
from pydantic import BaseModel
from rag_chain import CustomRAGChain
from prompt_template import PROMPT
from embeddings import NomicEmbeddings
from vector_store import init_milvus
from llm import OllamaLLM
from document_loaders import load_pdf, load_web
from text_splitter import split_documents
from utils import log_message
from batch_processor import BatchProcessor
import threading
from typing import List, Dict, Any
import asyncio

# Setup App
app = FastAPI(title="RAG API", version="1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables with thread safety
rag_chain = None
vectorstore = None
embeddings = NomicEmbeddings()
llm = OllamaLLM()
vectorstore_lock = threading.Lock()
batch_processor = None

# Request tracking
class QARequest(BaseModel):
    question: str

# Initialize RAG chain
def initialize_rag_chain():
    global rag_chain, vectorstore, batch_processor
    
    # Create empty vector store first
    vectorstore = init_milvus([], embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    rag_chain = CustomRAGChain(retriever, llm, PROMPT)
    
    # Initialize batch processor
    batch_processor = BatchProcessor(
        rag_chain=rag_chain,
        batch_size=3,  # Maximum requests to batch together
        batch_timeout=2.0  # Maximum wait time in seconds
    )
    
    return rag_chain

# Initialize on startup
initialize_rag_chain()

# Start batch processor on startup
@app.on_event("startup")
async def startup_event():
    global batch_processor
    if batch_processor:
        await batch_processor.start()

@app.on_event("shutdown")
async def shutdown_event():
    global batch_processor
    if batch_processor:
        await batch_processor.stop()

# Helper function for ingestion processing
async def process_ingestion(file_content: bytes = None, filename: str = None, url: str = None) -> List[Any]:
    """Process ingestion in a thread-safe manner"""
    global vectorstore, rag_chain, embeddings, batch_processor
    
    try:
        docs = []

        # ---------- Process PDF ----------
        if file_content and filename and filename.endswith('.pdf'):
            # Create a temporary file for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(file_content)
                tmp_file_path = tmp_file.name
            
            class FileWrapper:
                def __init__(self, content, filename):
                    self.content = content
                    self.filename = filename
                def getvalue(self):
                    return self.content
                @property
                def name(self):
                    return self.filename
            
            file_wrapper = FileWrapper(file_content, filename)
            docs.extend(await run_in_threadpool(load_pdf, file_wrapper))
            os.unlink(tmp_file_path)
        
        # ---------- Process Web ----------
        if url:
            docs.extend(await run_in_threadpool(load_web, url))
        
        if not docs:
            return {"message": "No documents to ingest"}

        # ---------- Split ----------
        docs = await run_in_threadpool(split_documents, docs)

        REQUIRED_METADATA_KEYS = {
            "source": "unknown",
            "type": "general"
        }
        for doc in docs:
            if not hasattr(doc, "metadata"):
                doc.metadata = {}
            for key, default_value in REQUIRED_METADATA_KEYS.items():
                if key not in doc.metadata:
                    doc.metadata[key] = default_value

        # ---------- Thread-safe vector store update ----------
        with vectorstore_lock:
            # Create new embeddings instance for this request
            request_embeddings = NomicEmbeddings()
            
            # Update vector store with new documents
            if vectorstore:
                # Add documents to existing collection
                vectorstore.add_documents(documents=docs, embedding=request_embeddings)
            else:
                # Initialize new vector store
                vectorstore = init_milvus(docs, request_embeddings)
            
            # Update RAG Chain
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
            rag_chain = CustomRAGChain(retriever, llm, PROMPT)
            
            # Update batch processor with new RAG chain
            if batch_processor:
                batch_processor.rag_chain = rag_chain
        
        return {"doc_count": len(docs), "message": f"Successfully ingested {len(docs)} documents"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Ingestion endpoint with concurrent support
@app.post("/ingest")
async def ingest_documents(
    file: UploadFile = File(None), 
    url: str = Form(None),
):
    try:
        file_content = None
        filename = None
        
        if file:
            file_content = await file.read()
            filename = file.filename
        
        # Process ingestion (handles concurrency internally)
        result = await process_ingestion(file_content, filename, url)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# Batch ingestion endpoint for multiple files/URLs
@app.post("/ingest/batch")
async def batch_ingest_documents(
    files: List[UploadFile] = File([]),
    urls: List[str] = Form([])
):
    try:
        total_docs = 0
        results = []
        
        # Process files
        for file in files:
            if file.filename.endswith('.pdf'):
                file_content = await file.read()
                result = await process_ingestion(file_content, file.filename, None)
                total_docs += result.get("doc_count", 0)
                results.append({
                    "filename": file.filename,
                    "result": result
                })
        
        # Process URLs
        for url in urls:
            result = await process_ingestion(None, None, url)
            total_docs += result.get("doc_count", 0)
            results.append({
                "url": url,
                "result": result
            })
        
        return {
            "total_documents": total_docs,
            "results": results,
            "message": f"Batch ingestion completed with {total_docs} total documents"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Batch-enabled QA endpoint
@app.post("/qa")
async def question_answer(req: QARequest):
    """QA endpoint that batches requests for efficient processing"""
    try:
        if not rag_chain:
            raise HTTPException(status_code=400, detail="RAG chain not initialized. Please ingest documents first.")
        
        if not batch_processor:
            raise HTTPException(status_code=500, detail="Batch processor not initialized.")
        
        # Use the centralized batch processor
        answer = await batch_processor.add_request(req.question, timeout=300.0)
        return {"answer": answer}
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add LangServe route
add_routes(app, rag_chain, path="/rag")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)  # Keep single worker for shared state