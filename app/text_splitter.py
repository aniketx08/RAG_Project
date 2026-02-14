from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from utils import log_message

def split_documents(docs):
    if not docs:
        log_message("No documents to split")
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )

    final_docs = []

    for doc in docs:
        text = doc.page_content.strip()
        if not text:
            continue

        chunks = splitter.split_text(text)

        for chunk in chunks:
            final_docs.append(
                Document(
                    page_content=chunk,
                    metadata=doc.metadata
                )
            )

    log_message(f"Final chunks sent to Milvus: {len(final_docs)}")
    return final_docs