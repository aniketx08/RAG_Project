import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.document_loaders import Docx2txtLoader
from utils import log_message

def load_pdf(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name
    
    loader = PyPDFLoader(tmp_file_path)
    docs = loader.load()
    os.unlink(tmp_file_path)
    log_message(f"Loaded {len(docs)} pages from PDF")
    return docs

def load_web(url):
    loader = WebBaseLoader(url)
    docs = loader.load()
    log_message(f"Loaded {len(docs)} documents from web page")
    return docs

def load_word(uploaded_file):
    log_message("[WORD] Using Docx2txtLoader")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    loader = Docx2txtLoader(tmp_path)
    docs = loader.load()

    os.unlink(tmp_path)

    log_message(f"[WORD] Loaded {len(docs)} documents from Word")
    log_message(f"[WORD] Sample text: {docs[0].page_content[:200]}")

    return docs
