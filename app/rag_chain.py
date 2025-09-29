from langchain_core.runnables import Runnable
from pymilvus import MilvusClient
from utils import log_message
import asyncio
import threading

# Thread lock for concurrent operations
milvus_lock = threading.Lock()

class CustomRAGChain(Runnable):
    def __init__(self, embeddings, llm, prompt_template, collection_name="rag_demo_local"):
        self.embeddings = embeddings
        self.llm = llm
        self.prompt_template = prompt_template
        self.collection_name = collection_name
        self.client = None
        self.document_count = 0  # Track number of documents
        self._initialize_milvus()

    def _initialize_milvus(self):
        """Initialize Milvus client with proper schema"""
        try:
            log_message("Initializing Milvus client...")
            
            self.client = MilvusClient(uri="http://127.0.0.1:19530")
            
            with milvus_lock:
                log_message(f"Setting up collection '{self.collection_name}'...")
                
                # Get dimension from embeddings
                log_message("Getting embedding dimension...")
                sample_vector = self.embeddings.embed_query("sample text for dimension")
                dimension = len(sample_vector)
                log_message(f"Embedding dimension: {dimension}")
                
                # Create collection if it doesn't exist
                if not self.client.has_collection(collection_name=self.collection_name):
                    log_message("Creating new collection...")
                    self.client.create_collection(
                        collection_name=self.collection_name,
                        dimension=dimension,
                        metric_type="IP",
                        consistency_level="Bounded",
                        auto_id=True
                    )
                    log_message(f"Collection '{self.collection_name}' created with dimension {dimension}")
                else:
                    log_message(f"Collection '{self.collection_name}' already exists")
                    # Get current document count
                    try:
                        stats = self.client.get_collection_stats(collection_name=self.collection_name)
                        self.document_count = stats.get('row_count', 0)
                        log_message(f"Found {self.document_count} existing documents in collection")
                    except:
                        log_message("Could not get collection stats")
            
            log_message("Milvus RAG chain initialized successfully!")
            
        except Exception as e:
            error_msg = f"Error initializing Milvus: {str(e)}"
            log_message(error_msg)
            raise Exception(error_msg)

    def get_relevant_documents(self, query, k=3):
        """Generate embedding and search Milvus with detailed logging"""
        try:
            log_message(f"Processing query: '{query[:100]}...'")
            
            # Generate query embedding
            log_message("Generating query embedding...")
            query_vector = self.embeddings.embed_query(query)
            log_message(f"Query embedding generated (dimension: {len(query_vector)})")
            
            # Search Milvus
            log_message(f"Searching Milvus for {k} most relevant documents...")
            results = self.client.search(
                collection_name=self.collection_name,
                data=[query_vector],
                limit=k,
                search_params={"metric_type":"IP","params":{}},
                output_fields=["text", "source", "type"]
            )
            
            documents = []
            if results and results[0]:
                log_message(f"Found {len(results[0])} search results")
                for i, result in enumerate(results[0]):
                    distance = result.get("distance", 0)
                    text_preview = result["entity"]["text"][:100]
                    log_message(f"Result {i+1}: distance={distance:.4f}, text='{text_preview}...'")
                    
                    doc = type('Document', (), {
                        'page_content': result["entity"]["text"],
                        'metadata': {
                            'source': result["entity"].get("source", "unknown"),
                            'type': result["entity"].get("type", "general"),
                            'distance': distance,
                            'chunk_length': len(result["entity"]["text"])
                        }
                    })()
                    documents.append(doc)
            else:
                log_message("No search results found")
            
            log_message(f"Retrieved {len(documents)} relevant documents")
            return documents
            
        except Exception as e:
            log_message(f"Error searching Milvus: {str(e)}")
            return []

    def add_documents(self, docs):
        """Add documents to Milvus collection with detailed processing info"""
        if not docs:
            log_message("No documents to add")
            return {"message": "No documents to add", "doc_count": 0}
        
        try:
            with milvus_lock:
                log_message(f"Adding {len(docs)} document chunks to Milvus...")
                                
                # Show sample chunks
                for i, doc in enumerate(docs[:3]):
                    log_message(f"Sample chunk {i+1} (length {len(doc.page_content)}): '{doc.page_content[:100]}...'")
                
                # Generate embeddings for all documents
                log_message("Generating embeddings for document chunks...")
                text_contents = [doc.page_content for doc in docs]
                vectors = self.embeddings.embed_documents(text_contents)
                log_message(f"Generated {len(vectors)} embeddings")
                
                # Prepare data for insertion
                data = []
                for i, (doc, vector) in enumerate(zip(docs, vectors)):
                    if not hasattr(doc, "metadata") or doc.metadata is None:
                        doc.metadata = {}
                    
                    doc_data = {
                        "vector": vector,
                        "text": doc.page_content,
                        "source": str(doc.metadata.get("source", "unknown")),
                        "type": str(doc.metadata.get("type", "general"))
                    }
                    data.append(doc_data)
                    
                    if i < 3:  # Log first few entries
                        log_message(f"Prepared data entry {i+1}: source='{doc_data['source']}', text_length={len(doc_data['text'])}")
                
                # Insert into Milvus
                log_message("Inserting data into Milvus...")
                result = self.client.insert(collection_name=self.collection_name, data=data)
                
                inserted_count = result.get('insert_count', 0)
                self.document_count += inserted_count
                
                log_message(f"Successfully inserted {inserted_count} document chunks")
                log_message(f"Total documents in collection: {self.document_count}")
                
                return {
                    "doc_count": inserted_count,
                    "total_docs": self.document_count,
                    "message": f"Successfully added {inserted_count} document chunks (total: {self.document_count})"
                }
                
        except Exception as e:
            error_msg = f"Error adding documents: {str(e)}"
            log_message(error_msg)
            raise Exception(error_msg)

    def invoke(self, input: dict, config=None) -> dict:
        """LangChain Runnable entrypoint with enhanced logging"""
        question = input["question"]
        log_message(f"RAG Chain invoke called with question: '{question[:100]}...'")
        
        # Get relevant documents
        docs = self.get_relevant_documents(question)
        
        if not docs:
            log_message("No relevant documents found for context")
            context = "No relevant information found in the knowledge base."
        else:
            context = "\n\n".join([d.page_content for d in docs])
            log_message(f"Context prepared from {len(docs)} documents (total length: {len(context)})")
        
        # Format prompt
        prompt = self.prompt_template.format(context=context, question=question)
        log_message(f"Prompt prepared (length: {len(prompt)})")

        try:
            log_message("Calling LLM...")
            if asyncio.iscoroutinefunction(self.llm):
                answer = asyncio.run(self.llm(prompt))
            else:
                answer = self.llm(prompt)
            
            log_message(f"LLM response received (length: {len(answer)})")
            return {"output": answer, "source_documents": docs}
            
        except Exception as e:
            error_msg = f"Error in RAG chain invoke: {str(e)}"
            log_message(error_msg)
            raise

    async def run(self, question: str) -> str:
        """Async version with enhanced logging"""            
        try:
            log_message(f"RAG Chain async run called with question: '{question[:100]}...'")
            
            docs = self.get_relevant_documents(question)
            
            if not docs:
                context = "No relevant information found in the knowledge base."
            else:
                context = "\n\n".join([d.page_content for d in docs])
                log_message(f"Context prepared from {len(docs)} documents")
            
            prompt = self.prompt_template.format(context=context, question=question)
            
            log_message("Calling LLM asynchronously...")
            if asyncio.iscoroutinefunction(self.llm):
                answer = await self.llm(prompt)
            else:
                answer = self.llm(prompt)
            
            log_message("LLM response received")
            return answer
            
        except Exception as e:
            error_msg = f"Error in RAG chain run: {str(e)}"
            log_message(error_msg)
            raise