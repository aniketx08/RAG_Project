from langchain_core.runnables import Runnable
from pymilvus import MilvusClient
from utils import log_message
import asyncio
from memory import get_recent_messages, save_message

class CustomRAGChain(Runnable):
    def __init__(self, embeddings, llm, prompt_template, collection_name="rag_demo_local"):
        self.embeddings = embeddings
        self.llm = llm
        self.prompt_template = prompt_template
        self.collection_name = collection_name
        self.client = None
        self.document_count = 0
        self._initialize_milvus()

    def _initialize_milvus(self):
        log_message("Initializing Milvus client...")
        self.client = MilvusClient(uri="tcp://127.0.0.1:19530")

        if not self.client.has_collection(self.collection_name):
            log_message("Creating new collection...")

            self.client.create_collection(
                collection_name=self.collection_name,
                dimension=self.embeddings.dimension,
                metric_type="IP",
                consistency_level="Bounded",
                auto_id=True,
                enable_dynamic_field=True   # 🔑 THIS enables JSON payload
            )

            log_message(f"Collection '{self.collection_name}' created")



    def get_relevant_documents(self, query, k=3):
        """Generate embedding and search Milvus with detailed logging"""
        try:
            log_message(f"Processing query: '{query[:100]}...'")
            
            # Generate query embedding
            log_message("Generating query embedding...")
            query_vector = self.embeddings.embed_query(query)
            
            # Search Milvus
            log_message(f"Searching Milvus for {k} most relevant documents...")
            results = self.client.search(
                collection_name=self.collection_name,
                data=[query_vector],
                limit=k,
                search_params={"metric_type": "IP", "params": {}},
                output_fields=["payload"]
            )

            
            documents = []
            if results and results[0]:
                log_message(f"Found {len(results[0])} search results")
                for i, result in enumerate(results[0]):
                    distance = result.get("distance", 0)
                    payload = result["entity"]["payload"]
                    text_preview = payload["text"][:100]
                    log_message(f"Result {i+1}: distance={distance:.4f}, text='{text_preview}...'")
                    
                    doc = type('Document', (), {
                        'page_content': payload["text"],
                        'metadata': {
                            'source': payload.get("source", "unknown"),
                            'type': payload.get("type", "general"),
                            'distance': distance,
                            'chunk_length': len(payload["text"])
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
                
                data.append({
                    "vector": vector,
                    "payload": {
                        "text": doc.page_content,
                        "source": doc.metadata.get("source", "unknown"),
                        "type": doc.metadata.get("type", "general")
                    }
                })
       
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

    async def run(self, question: str, user_id: str) -> str:
        """
        Async version - handles each request independently
        Multiple concurrent calls will run in parallel
        """            
        try:
            log_message(f"RAG Chain async run called with question: '{question[:100]}...'")

            messages = get_recent_messages(user_id)
            chat_history = "\n".join(
                [f"{m['role'].capitalize()}: {m['content']}" for m in messages]
            )
            
            # Retrieve relevant documents (synchronous operation)
            docs = await asyncio.to_thread(self.get_relevant_documents, question)
            
            if not docs:
                context = "No relevant information found in the knowledge base."
            else:
                context = "\n\n".join([d.page_content for d in docs])
                log_message(f"Context prepared from {len(docs)} documents")
            
            prompt = self.prompt_template.format(
                chat_history=chat_history,
                context=context,
                question=question
            )
            
            # Call LLM asynchronously - this is where concurrent execution happens
            log_message("Calling LLM asynchronously...")
            answer = await self.llm(prompt)     

            save_message(user_id, "user", question)
            save_message(user_id, "assistant", answer)

            log_message("LLM response received")
            return answer     

        except Exception as e:
            error_msg = f"Error in RAG chain run: {str(e)}"
            log_message(error_msg)
            raise