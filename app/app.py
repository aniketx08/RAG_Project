import streamlit as st
import requests
import os
from utils import log_message

# Initialize session state
if 'log_messages' not in st.session_state:
    st.session_state.log_messages = []

st.title("RAG Demo with Nomic Embeddings & llama3.1")

# Backend API URLs
API_URL = "http://127.0.0.1:8000"
INGEST_URL = f"{API_URL}/ingest"
QA_URL = f"{API_URL}/qa"
STATUS_URL = f"{API_URL}/status"



if st.session_state.log_messages:
    with st.expander("View Logs"):
        for msg in st.session_state.log_messages:
            st.text(msg)

# Document ingestion section
st.header("Document Ingestion")
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
web_url = st.text_input("Or enter a webpage URL:")

if st.button("Ingest Documents"):
    if uploaded_file or web_url:
        try:
            files = {}
            data = {}
            
            if uploaded_file:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            
            if web_url:
                data = {"url": web_url}
            
            # Call FastAPI ingest endpoint
            response = requests.post(INGEST_URL, files=files, data=data)
            if response.status_code == 200:
                result = response.json()
                st.success(result.get("message", "Documents ingested successfully!"))
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")
    else:
        st.warning("Please upload a PDF or enter a URL")


# Question answering section
st.header("Question Answering")
question = st.text_input("Ask a question about your documents:")

if st.button("Get Answer") and question:
    try:
        # Call FastAPI QA endpoint
        response = requests.post(QA_URL, json={"question": question})
        if response.status_code == 200:
            result = response.json()
            st.subheader("Answer:")
            st.write(result.get("answer", "No answer returned"))
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Request failed: {e}")