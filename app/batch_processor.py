import asyncio
import time
import uuid
from typing import List, Tuple
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
                    continue
                    
            except Exception as e:
                log_message(f"Error in batch processor: {e}")
                for item in batch_items:
                    if not item.future.done():
                        item.future.set_exception(e)
                batch_items = []
                await asyncio.sleep(1)

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
                        response_msg = (error_msg if error_msg else 
                                      "I don't have information about this topic in my knowledge base. "
                                      "Please ensure you've ingested relevant documents first.")
                        if not item.future.done():
                            item.future.set_result(response_msg)
                        continue
                        
                    item.context = context
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
            
            # Step 3: Send to LLM (batch or individual)
            if len(successful_items) == 1:
                # Single request - use individual processing
                item = successful_items[0]
                try:
                    answer = await self.rag_chain.llm(item.prompt)
                    if not item.future.done():
                        item.future.set_result(answer)
                except Exception as e:
                    if not item.future.done():
                        item.future.set_exception(e)
            else:
                # Multiple requests - use batch processing
                await self._process_batch_llm(successful_items)
                        
        except Exception as e:
            log_message(f"Error in _process_batch: {e}")
            for item in batch_items:
                if not item.future.done():
                    item.future.set_exception(e)

    async def _process_batch_llm(self, successful_items: List[BatchRequestItem]):
        """Process multiple items with batch LLM call"""
        try:
            batch_prompt = self._create_batch_prompt(successful_items)
            
            log_message(f"Sending batch prompt to LLM for {len(successful_items)} questions")
            log_message(f"Batch prompt preview: {batch_prompt[:500]}...")
            
            batch_response = await self.rag_chain.llm(batch_prompt)
            log_message(f"Batch response preview: {batch_response[:500]}...")
            
            answers = self._parse_batch_response(batch_response, successful_items)
            
            for i, (item, answer) in enumerate(zip(successful_items, answers)):
                log_message(f"Answer {i+1}: {answer[:100]}...")
                if not item.future.done():
                    item.future.set_result(answer)
                    
        except Exception as e:
            log_message(f"Error in batch LLM call: {e}")
            for item in successful_items:
                if not item.future.done():
                    item.future.set_exception(e)

    async def _retrieve_context(self, question: str) -> Tuple[str, bool, str]:
        """Retrieve context for a single question using the RAG chain directly"""
        try:
            loop = asyncio.get_event_loop()
            docs = await loop.run_in_executor(
                None, 
                self.rag_chain.get_relevant_documents,
                question
            )
            
            if not docs:
                return "", False, "No documents found in the knowledge base."
            
            meaningful_docs = [doc for doc in docs if len(doc.page_content.strip()) > 50]
            
            if not meaningful_docs:
                return "", False, "No relevant documents found for this question."
            
            context = "\n\n".join([d.page_content for d in meaningful_docs])
            has_relevant_content = len(context.strip()) > 100
            
            return context, has_relevant_content, ""
            
        except Exception as e:
            log_message(f"Error retrieving context: {e}")
            return "", False, f"Error retrieving documents: {e}"

    def _create_batch_prompt(self, items: List[BatchRequestItem]) -> str:
        """Create a single prompt that asks the LLM to answer multiple questions with clearly marked responses"""
        
        batch_prompt = """You are a helpful AI assistant. I will provide you with multiple questions and their contexts. Please answer each question thoroughly based on the provided context.

IMPORTANT: Start each answer with exactly "ANSWER_X:" where X is the question number (1, 2, 3, etc.).

"""
        
        for i, item in enumerate(items, 1):
            batch_prompt += f"""QUESTION {i}: {item.question}

CONTEXT {i}: {item.context}

ANSWER_{i}: """
            
            if i < len(items):
                batch_prompt += "\n\n" + "="*50 + "\n\n"
        
        return batch_prompt

    def _parse_batch_response(self, response: str, items: List[BatchRequestItem]) -> List[str]:
        """Parse the LLM's batch response and extract individual answers"""
        log_message(f"Parsing response for {len(items)} questions")
        
        answers = []
        
        # Split by ANSWER_X: markers
        import re
        
        # Find all ANSWER_X: patterns and their positions
        answer_pattern = r'ANSWER_(\d+):\s*'
        matches = list(re.finditer(answer_pattern, response))
        
        if not matches:
            log_message("No ANSWER_X: markers found, trying fallback parsing")
            # Fallback: try to split by common separators
            parts = re.split(r'\n\s*={10,}\s*\n|\n\s*-{10,}\s*\n|\n\n\n+', response)
            for i, part in enumerate(parts):
                if i < len(items):
                    clean_answer = part.strip()
                    if clean_answer:
                        answers.append(clean_answer)
        else:
            log_message(f"Found {len(matches)} ANSWER markers")
            
            for i in range(len(matches)):
                answer_num = int(matches[i].group(1))
                start_pos = matches[i].end()
                
                # Find end position (start of next answer or end of string)
                if i + 1 < len(matches):
                    end_pos = matches[i + 1].start()
                else:
                    end_pos = len(response)
                
                answer_text = response[start_pos:end_pos].strip()
                
                # Remove any trailing separators
                answer_text = re.sub(r'\s*={10,}\s*$', '', answer_text)
                answer_text = re.sub(r'\s*-{10,}\s*$', '', answer_text)
                
                # Ensure we have the answer in the right order
                while len(answers) < answer_num:
                    answers.append("I couldn't generate an answer for this question.")
                
                if answer_num <= len(answers):
                    answers[answer_num - 1] = answer_text
                else:
                    answers.append(answer_text)
                
                log_message(f"Parsed answer {answer_num}: {answer_text[:100]}...")
        
        # Ensure we have exactly the right number of answers
        while len(answers) < len(items):
            answers.append("I couldn't generate an answer for this question.")
        
        return answers[:len(items)]