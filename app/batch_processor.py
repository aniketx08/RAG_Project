# batch_processor.py
import asyncio
import time
import uuid
from typing import List, Dict, Any, Tuple
from utils import log_message
from dataclasses import dataclass

@dataclass
class BatchRequestItem:
    request_id: str
    question: str
    future: asyncio.Future
    timestamp: float
    context: str = ""
    prompt: str = ""

class BatchProcessor:
    def __init__(self, rag_chain, batch_size=3, batch_timeout=2.0):
        self.rag_chain = rag_chain
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.batch_queue = asyncio.Queue()
        self.processor_task = None
        self.is_running = False

    async def start(self):
        """Start the batch processor"""
        if not self.is_running:
            self.is_running = True
            self.processor_task = asyncio.create_task(self._batch_processor())
            log_message("Batch processor started")

    async def stop(self):
        """Stop the batch processor"""
        self.is_running = False
        if self.processor_task:
            self.processor_task.cancel()
            try:
                await self.processor_task
            except asyncio.CancelledError:
                pass
            log_message("Batch processor stopped")

    async def add_request(self, question: str, timeout: float = 300.0) -> str:
        """Add a request to the batch queue and wait for response"""
        request_id = str(uuid.uuid4())
        future = asyncio.Future()
        
        batch_item = BatchRequestItem(
            request_id=request_id,
            question=question,
            future=future,
            timestamp=time.time()
        )
        
        await self.batch_queue.put(batch_item)
        log_message(f"Added question to batch queue: {question[:50]}...")
        
        try:
            answer = await asyncio.wait_for(future, timeout=timeout)
            return answer
        except asyncio.TimeoutError:
            raise Exception("Request timeout - batch processing took too long")

    async def _batch_processor(self):
        """Background task that processes batched requests"""
        batch_items = []
        
        while self.is_running:
            try:
                # Wait for requests or timeout
                try:
                    # Get first item or wait for timeout
                    if not batch_items:
                        item = await asyncio.wait_for(
                            self.batch_queue.get(), 
                            timeout=self.batch_timeout
                        )
                        batch_items.append(item)
                    
                    # Collect more items up to batch size or timeout
                    start_time = time.time()
                    while (len(batch_items) < self.batch_size and 
                           (time.time() - start_time) < self.batch_timeout):
                        try:
                            item = await asyncio.wait_for(
                                self.batch_queue.get(), 
                                timeout=max(0.1, self.batch_timeout - (time.time() - start_time))
                            )
                            batch_items.append(item)
                        except asyncio.TimeoutError:
                            break
                    
                    if batch_items:
                        await self._process_batch(batch_items)
                        batch_items = []
                        
                except asyncio.TimeoutError:
                    # No requests came in, continue waiting
                    continue
                    
            except Exception as e:
                log_message(f"Error in batch processor: {e}")
                # Clear any failed batch items
                for item in batch_items:
                    if not item.future.done():
                        item.future.set_exception(e)
                batch_items = []
                await asyncio.sleep(1)  # Brief pause before retrying

    async def _process_batch(self, batch_items: List[BatchRequestItem]):
        """Process a batch of requests together"""
        try:
            log_message(f"Processing batch of {len(batch_items)} requests")
            
            if not self.rag_chain:
                error = Exception("RAG chain not initialized")
                for item in batch_items:
                    if not item.future.done():
                        item.future.set_exception(error)
                return
            
            # Step 1: Retrieve context for all questions in parallel
            retrieval_tasks = []
            for item in batch_items:
                task = asyncio.create_task(self._retrieve_context(item.question))
                retrieval_tasks.append((item, task))
            
            # Wait for all retrievals to complete
            for item, task in retrieval_tasks:
                try:
                    context, has_relevant_content, error_msg = await task
                    
                    if not has_relevant_content:
                        # No relevant documents found - respond appropriately
                        response_msg = (error_msg if error_msg else 
                                      "I don't have information about this topic in my knowledge base. "
                                      "Please ensure you've ingested relevant documents first.")
                        if not item.future.done():
                            item.future.set_result(response_msg)
                        continue
                        
                    item.context = context
                    # Build prompt for this item
                    item.prompt = self.rag_chain.prompt_template.format(
                        context=item.context, 
                        question=item.question
                    )
                    
                except Exception as e:
                    log_message(f"Error retrieving context for question '{item.question}': {e}")
                    if not item.future.done():
                        item.future.set_exception(e)
                    continue
            
            # Step 2: Filter successful items and create batch prompt
            successful_items = [item for item in batch_items 
                              if item.prompt and not item.future.done()]
            
            if not successful_items:
                log_message("No successful items to process in batch")
                return
            
            # Step 3: Create combined batch prompt for LLM
            batch_prompt = self._create_batch_prompt(successful_items)
            
            # Step 4: Send single request to LLM
            log_message(f"Sending batch prompt to LLM for {len(successful_items)} questions")
            try:
                batch_response = await self.rag_chain.llm(batch_prompt)
                
                # Step 5: Parse and distribute responses
                answers = self._parse_batch_response(batch_response, successful_items)
                
                # Step 6: Set results for each future
                for item, answer in zip(successful_items, answers):
                    if not item.future.done():
                        item.future.set_result(answer)
                        
            except Exception as e:
                log_message(f"Error in batch LLM call: {e}")
                for item in successful_items:
                    if not item.future.done():
                        item.future.set_exception(e)
                        
        except Exception as e:
            log_message(f"Error in _process_batch: {e}")
            for item in batch_items:
                if not item.future.done():
                    item.future.set_exception(e)

    async def _retrieve_context(self, question: str) -> Tuple[str, bool, str]:
        """Retrieve context for a single question and return context + relevance info"""
        try:
            # Run the synchronous retrieval in a thread pool
            loop = asyncio.get_event_loop()
            docs = await loop.run_in_executor(
                None, 
                self.rag_chain.retriever.get_relevant_documents, 
                question
            )
            
            if not docs:
                return "", False, "No documents found in the knowledge base."
            
            # Check if documents have meaningful content (not just empty or very short)
            meaningful_docs = [doc for doc in docs if len(doc.page_content.strip()) > 50]
            
            if not meaningful_docs:
                return "", False, "No relevant documents found for this question."
            
            context = "\n".join([d.page_content for d in meaningful_docs])
            
            # Simple relevance check - you can make this more sophisticated
            has_relevant_content = len(context.strip()) > 100
            
            return context, has_relevant_content, ""
            
        except Exception as e:
            log_message(f"Error retrieving context: {e}")
            return "", False, f"Error retrieving documents: {e}"

    def _create_batch_prompt(self, items: List[BatchRequestItem]) -> str:
        """Create a single prompt that asks the LLM to answer multiple questions"""
        batch_prompt = """You are a strict document-based question answering assistant. You must ONLY answer questions based on the provided context documents. 

IMPORTANT RULES:
1. If the context doesn't contain information to answer a question, respond with "I don't have enough information in the provided documents to answer this question."
2. Do not use your general knowledge or training data
3. Only use information explicitly stated in the context provided for each question
4. Be precise and cite specific information from the context

Format your response as follows:
ANSWER_1: [your answer to question 1 based only on context 1]
ANSWER_2: [your answer to question 2 based only on context 2]
...and so on.

Here are the questions and their contexts:

"""
        
        for i, item in enumerate(items, 1):
            batch_prompt += f"""
QUESTION_{i}: {item.question}
CONTEXT_{i}: {item.context}

"""
        
        batch_prompt += f"\nRemember: Answer ONLY based on the provided contexts. If a context doesn't contain the answer, say you don't have enough information. Provide {len(items)} answers in the format specified above."
        return batch_prompt

    def _parse_batch_response(self, response: str, items: List[BatchRequestItem]) -> List[str]:
        """Parse the LLM's batch response and extract individual answers"""
        answers = []
        lines = response.strip().split('\n')
        
        # Look for ANSWER_X: patterns
        current_answer = ""
        answer_index = 0
        
        for line in lines:
            line = line.strip()
            if line.startswith(f"ANSWER_{answer_index + 1}:"):
                if current_answer and answer_index < len(items):
                    answers.append(current_answer.strip())
                current_answer = line[len(f"ANSWER_{answer_index + 1}:"):].strip()
                answer_index += 1
            elif line.startswith("ANSWER_") and ":" in line:
                # Handle any ANSWER_X: format
                if current_answer and len(answers) < len(items):
                    answers.append(current_answer.strip())
                current_answer = line.split(":", 1)[1].strip()
            else:
                if current_answer:
                    current_answer += " " + line
        
        # Add the last answer
        if current_answer and len(answers) < len(items):
            answers.append(current_answer.strip())
        
        # Ensure we have the right number of answers
        while len(answers) < len(items):
            answers.append("I couldn't generate an answer for this question.")
        
        return answers[:len(items)]