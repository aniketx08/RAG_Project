from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils import log_message

def split_documents(docs):
    """Split documents into chunks suitable for embedding"""
    if not docs:
        log_message("No documents to split")
        return []
    
    # Configure splitter - 500 chars is quite small, consider increasing
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # You might want to increase this to 1000-1500
        chunk_overlap=50,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    log_message(f"Splitting {len(docs)} documents into chunks...")
    
    # Log original document info
    total_chars = sum(len(doc.page_content) for doc in docs)
    log_message(f"Total characters in original documents: {total_chars}")
    
    # Split documents
    split_docs = splitter.split_documents(docs)
    
    # Log chunk statistics
    chunk_sizes = [len(chunk.page_content) for chunk in split_docs]
    
    log_message(f"Created {len(split_docs)} document chunks")
    
    # Log first few chunks for verification
    for i, chunk in enumerate(split_docs[:3]):
        log_message(f"Sample chunk {i+1} (length {len(chunk.page_content)}): {chunk.page_content[:100]}...")
    
    return split_docs