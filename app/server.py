from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from langserve import add_routes
import tempfile
from pydantic import BaseModel
from rag_chain import CustomRAGChain
from prompt_template import PROMPT
from embeddings import NomicEmbeddings
from llm import OllamaLLM
from document_loaders import load_pdf, load_web
from text_splitter import split_documents
from utils import log_message
from typing import List, Dict, Any
import os
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

# Global variables
rag_chain = None
embeddings = NomicEmbeddings()
llm = OllamaLLM()
qa_lock = asyncio.Lock()  # Lock for sequential QA processing

class QARequest(BaseModel):
    question: str

def initialize_rag_chain():
    """Initialize RAG chain with Milvus integration"""
    global rag_chain
    
    try:
        rag_chain = CustomRAGChain(embeddings, llm, PROMPT)
        log_message("RAG chain initialized successfully")
        return rag_chain
        
    except Exception as e:
        log_message(f"Error initializing RAG chain: {str(e)}")
        raise

# Initialize on startup
initialize_rag_chain()

@app.on_event("startup")
async def startup_event():
    log_message("FastAPI application started")

@app.on_event("shutdown")
async def shutdown_event():
    global llm
    if llm:
        await llm.close()
        log_message("LLM session closed")

async def process_ingestion(file_content: bytes = None, filename: str = None, url: str = None) -> Dict[str, Any]:
    """Process document ingestion"""
    global rag_chain
    
    try:
        docs = []

        # Process PDF
        if file_content and filename and filename.endswith('.pdf'):
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
        
        # Process Web URL
        if url:
            docs.extend(await run_in_threadpool(load_web, url))
        
        if not docs:
            return {"message": "No documents to ingest", "doc_count": 0}

        # Split documents
        docs = await run_in_threadpool(split_documents, docs)

        # Add documents to RAG chain
        result = rag_chain.add_documents(docs)
        
        return result
    
    except Exception as e:
        log_message(f"Error in process_ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def ingest_documents(file: UploadFile = File(None), url: str = Form(None)):
    """Single document ingestion endpoint"""
    try:
        file_content = None
        filename = None
        
        if file:
            file_content = await file.read()
            filename = file.filename
        
        result = await process_ingestion(file_content, filename, url)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/qa")
async def question_answer(req: QARequest):
    """
    QA endpoint - processes ONE request at a time (sequential)
    Other requests will wait in queue until the current one completes
    """
    global qa_lock
    
    try:
        if not rag_chain:
            raise HTTPException(
                status_code=400, 
                detail="RAG chain not initialized. Please ingest documents first."
            )
        
        # Acquire lock - only one request can proceed at a time
        async with qa_lock:
            log_message(f"[PROCESSING] QA request: {req.question[:50]}...")
            
            # Call RAG chain's async run method
            answer = await rag_chain.run(req.question)
            
            log_message(f"[COMPLETED] QA request: {req.question[:50]}...")
        
        return {"answer": answer}
            
    except HTTPException:
        raise
    except Exception as e:
        log_message(f"Error in QA endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Add LangServe routes
if rag_chain:
    add_routes(app, rag_chain, path="/rag")

if __name__ == "__main__":
    import uvicorn
    # Single worker for simplicity, but async handles concurrency
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)