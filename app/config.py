import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MILVUS_URI = os.getenv("MILVUS_URI")
ZILLIZ_API_KEY = os.getenv("ZILLIZ_API_KEY")

# LangChain
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")