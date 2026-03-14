from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from langserve import add_routes
import tempfile
from pydantic import BaseModel
from rag_chain import CustomRAGChain
from prompt_template import PROMPT
from embeddings import NomicEmbeddings
from llm import OllamaLLM
from document_loaders import load_pdf, load_web, load_word
from text_splitter import split_documents
from utils import log_message
from typing import List, Dict, Any
import os
import asyncio
from auth import get_current_user
from memory import chat_memory_collection
from db import conversations_collection
from uuid import uuid4
from datetime import datetime
from fastapi import FastAPI, UploadFile, File
from faster_whisper import WhisperModel
import shutil
import os
from deep_translator import GoogleTranslator
from title_prompt import TITLE_PROMPT

# Setup App
app = FastAPI(title="RAG API", version="1.0")

# model = WhisperModel(
#     "medium",
#     device="cpu"
# )

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
    conversation_id: str

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


async def generate_chat_title(llm, question: str):

    prompt = TITLE_PROMPT.format(question=question)

    response = await llm(prompt)

    title = response.strip()

    return title

async def process_ingestion(
    file_content: bytes = None,
    filename: str = None,
    url: str = None
) -> Dict[str, Any]:

    global rag_chain

    try:
        docs = []
        # 1. Log ingestion request
        log_message(
            f"[INGEST] file={filename}, "
            f"bytes={len(file_content) if file_content else 0}, "
            f"url={url}"
        )

        # ---- FILE UPLOAD HANDLING ----
        if file_content and filename:
            log_message(f"[INGEST] Detected uploaded file: {filename}")
            
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

            # PDF
            if filename.lower().endswith(".pdf"):
                log_message("[INGEST] Routing to PDF loader")
                docs.extend(await run_in_threadpool(load_pdf, file_wrapper))

            elif filename.lower().endswith(".docx"):
                log_message("[INGEST] Routing to WORD loader")
                docs.extend(await run_in_threadpool(load_word, file_wrapper))
            

        # ---- WEB URL ----
        if url:
            docs.extend(await run_in_threadpool(load_web, url))

        if not docs:
            return {"message": "No documents to ingest", "doc_count": 0}

        # ---- SPLIT / CHUNK ----
        docs = await run_in_threadpool(split_documents, docs)

        # ---- ADD TO VECTOR DB ----
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
async def question_answer(req: QARequest, request: Request):
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

            user_id = get_current_user(request)

            # Check existing conversation
            convo = conversations_collection.find_one({"_id": req.conversation_id})

            if convo and convo["title"] == "New Chat":

                title = await generate_chat_title(rag_chain.llm, req.question)

                conversations_collection.update_one(
                    {"_id": req.conversation_id},
                    {"$set": {"title": title}}
                )

            # Call RAG chain's async run method
            answer = await rag_chain.run(
                question=req.question,
                user_id=user_id,
                conversation_id=req.conversation_id
            )
            
            log_message(f"[COMPLETED] QA request: {req.question[:50]}...")
        
        return {"answer": answer}
            
    except HTTPException:
        raise
    except Exception as e:
        log_message(f"Error in QA endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
# @app.post("/transcribe")
# async def transcribe(
#     file: UploadFile = File(...),
#     language: str = Form("auto")
# ):

#     file_path = f"temp_{file.filename}"

#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     try:
#         if language != "auto":
#             segments, info = model.transcribe(
#                 file_path,
#                 language=language
#             )
#         else:
#             segments, info = model.transcribe(file_path)

#         transcript = ""
#         for segment in segments:
#             transcript += segment.text + " "

#         return {"text": transcript.strip()}

#     finally:
#         if os.path.exists(file_path):
#             os.remove(file_path)

class TranslateRequest(BaseModel):
    text: str
    source_lang: str

@app.post("/translate")
async def translate(req: TranslateRequest):
    translated = GoogleTranslator(
        source=req.source_lang.split("-")[0],
        target="en"
    ).translate(req.text)

    return {"translated_text": translated}


from fastapi import Request

@app.get("/chats")
async def get_chats(request: Request):
    user_id = get_current_user(request)

    chats = (
        chat_memory_collection
        .find({"user_id": user_id})
        .sort("created_at", 1)
    )

    return [
        {
            "role": c["role"],
            "content": c["content"]
        }
        for c in chats
    ]

from uuid import uuid4
from db import conversations_collection

@app.post("/conversations")
async def create_conversation(request: Request):

    user_id = get_current_user(request)

    convo_id = str(uuid4())

    conversations_collection.insert_one({
        "_id": convo_id,
        "user_id": user_id,
        "title": "New Chat",
        "created_at": datetime.utcnow()
    })

    return {"conversation_id": convo_id}

@app.get("/conversations")
async def get_conversations(request: Request):

    user_id = get_current_user(request)

    convos = conversations_collection.find({"user_id": user_id})

    return [
        {
            "id": c["_id"],
            "title": c["title"]
        }
        for c in convos
    ]

@app.get("/messages/{conversation_id}")
async def get_messages(conversation_id: str, request: Request):

    user_id = get_current_user(request)

    msgs = chat_memory_collection.find({
        "user_id": user_id,
        "conversation_id": conversation_id
    }).sort("created_at", 1)

    return [
        {
            "role": m["role"],
            "content": m["content"]
        }
        for m in msgs
    ]

# Add LangServe routes
if rag_chain:
    add_routes(app, rag_chain, path="/rag") 

if __name__ == "__main__":
    import uvicorn
    # Single worker for simplicity, but async handles concurrency
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)