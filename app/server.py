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
from batch_processor import BatchProcessor
import threading
from typing import List, Dict, Any
import os



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
batch_processor = None
rag_lock = threading.Lock()

class QARequest(BaseModel):
    question: str

def initialize_rag_chain():
    """Initialize RAG chain with Milvus integration"""
    global rag_chain, batch_processor
    
    try:
        rag_chain = CustomRAGChain(embeddings, llm, PROMPT)
        batch_processor = BatchProcessor(
            rag_chain=rag_chain,
            batch_size=3,
            batch_timeout=2.0
        )
        
        log_message("RAG chain initialized successfully")
        return rag_chain
        
    except Exception as e:
        log_message(f"Error initializing RAG chain: {str(e)}")
        raise

# Initialize on startup
initialize_rag_chain()

@app.on_event("startup")
async def startup_event():
    global batch_processor
    if batch_processor:
        await batch_processor.start()
        log_message("Batch processor started")

@app.on_event("shutdown")
async def shutdown_event():
    global batch_processor, llm
    if batch_processor:
        await batch_processor.stop()
        log_message("Batch processor stopped")
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
        with rag_lock:
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

@app.post("/ingest/batch")
async def batch_ingest_documents(files: List[UploadFile] = File([]), urls: List[str] = Form([])):
    """Batch document ingestion endpoint"""
    try:
        total_docs = 0
        results = []
        
        # Process files
        for file in files:
            if file.filename and file.filename.endswith('.pdf'):
                file_content = await file.read()
                result = await process_ingestion(file_content, file.filename, None)
                total_docs += result.get("doc_count", 0)
                results.append({"filename": file.filename, "result": result})
        
        # Process URLs
        for url in urls:
            result = await process_ingestion(None, None, url)
            total_docs += result.get("doc_count", 0)
            results.append({"url": url, "result": result})
        
        return {
            "total_documents": total_docs,
            "results": results,
            "message": f"Batch ingestion completed with {total_docs} total documents"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/qa")
async def question_answer(req: QARequest):
    """QA endpoint - generates embedding, searches Milvus, sends context to LLM"""
    try:
        if not rag_chain:
            raise HTTPException(
                status_code=400, 
                detail="RAG chain not initialized. Please ingest documents first."
            )
        
        if not batch_processor:
            raise HTTPException(status_code=500, detail="Batch processor not initialized.")
        
        answer = await batch_processor.add_request(req.question, timeout=300.0)
        return {"answer": answer}
            
    except HTTPException:
        raise
    except Exception as e:
        log_message(f"Error in QA endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        from pymilvus import MilvusClient
        client = MilvusClient(uri="http://127.0.0.1:19530")
        milvus_status = "connected"
    except:
        milvus_status = "disconnected"
    
    return {
        "status": "healthy",
        "milvus": milvus_status,
        "rag_chain": "initialized" if rag_chain else "not_initialized",
        "batch_processor": "running" if batch_processor else "not_running"
    }

# Add LangServe routes
if rag_chain:
    add_routes(app, rag_chain, path="/rag")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)