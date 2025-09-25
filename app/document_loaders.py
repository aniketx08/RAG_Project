import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
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