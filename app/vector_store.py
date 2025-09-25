from langchain_community.vectorstores import Milvus
from pymilvus import connections, utility
from utils import log_message
import streamlit as st
import threading

# Thread lock for concurrent ingestion
milvus_lock = threading.Lock()

def init_milvus(docs, embeddings, collection_name="rag_demo_local"):
    try:
        log_message("Connecting to local Milvus on localhost:19530...")

        # Establish connection
        connections.connect(
            alias="default",
            host="127.0.0.1",
            port="19530"
        )

        # Drop existing collection if inconsistent
        if utility.has_collection(collection_name):
            log_message(f"Collection '{collection_name}' already exists. Dropping to ensure schema consistency...")
            utility.drop_collection(collection_name)

        log_message("Creating embeddings and storing in Milvus...")

        # Always acquire lock during ingestion
        with milvus_lock:
            # Normalize docs metadata so schema matches
            for doc in docs:
                if not hasattr(doc, "metadata"):
                    doc.metadata = {}
                # Ensure all docs have same set of keys
                if "source" not in doc.metadata:
                    doc.metadata["source"] = "unknown"
                if "type" not in doc.metadata:
                    doc.metadata["type"] = "general"

            # Insert into Milvus
            vectorstore = Milvus.from_documents(
                docs,
                embeddings,
                connection_args={
                    "host": "127.0.0.1",
                    "port": "19530"
                },
                collection_name=collection_name
            )

        # Store in session
        st.session_state.vectorstore = vectorstore

        log_message("Documents successfully ingested into vector database!")
        st.success("Documents successfully ingested into vector database!")

        return vectorstore

    except Exception as e:
        error_msg = f"Error connecting to Milvus: {str(e)}"
        log_message(error_msg)
        st.error(error_msg)
        st.error("Make sure Milvus is running on localhost:19530 (Docker up!)")
        st.stop()
