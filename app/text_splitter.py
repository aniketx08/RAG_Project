from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils import log_message

def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(docs)
    log_message(f"Created {len(split_docs)} document chunks.")
    return split_docs