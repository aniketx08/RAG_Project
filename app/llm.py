# llm.py
import aiohttp
from utils import log_message
import asyncio
from typing import List

class OllamaLLM:
    def __init__(self, model="llama3.1", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.session = None

    async def __call__(self, prompt):
        """Async function to call Ollama LLM - optimized for batch requests"""
        if self.session is None:
            await self._init_session()

        log_message(f"Sending prompt to Ollama (length: {len(prompt)} chars)...")
        
        # The URL for the Ollama API generate endpoint
        url = f"{self.base_url}/api/generate"
        
        # The payload for the request - optimized for batch processing
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,  # We want the complete response at once
            "options": {
                "num_ctx": 8192,  # Increase context window for batch processing
                "temperature": 0.1,  # Lower temperature for more consistent batch responses
                "top_p": 0.9,
                "num_predict": -1,  # Let model decide response length
            }
        }

        try:
            # ASYNC HTTP POST request with retry logic for batch processing
            response_text = await self._make_request_with_retry(url, payload)
            log_message(f"Received LLM response (length: {len(response_text)} chars)")
            return response_text
                        
        except Exception as e:
            log_message(f"Error calling Ollama: {e}")
            return f"Sorry, an error occurred: {e}"
    
    async def _init_session(self):
        """Initialize the HTTP session with optimized settings"""
        connector = aiohttp.TCPConnector(
            limit=100,  # Total connection pool size
            limit_per_host=30,  # Connections per host
            keepalive_timeout=300,  # Keep connections alive longer
            enable_cleanup_closed=True
        )
        timeout = aiohttp.ClientTimeout(total=300)  # 5 minute timeout for batch requests
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)

    async def _make_request_with_retry(self, url: str, payload: dict, max_retries: int = 3) -> str:
        """Make HTTP request with exponential backoff retry logic"""
        for attempt in range(max_retries):
            try:
                async with self.session.post(url, json=payload) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return result["response"]
                    
            except aiohttp.ClientError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    log_message(f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    raise e
    
    async def batch_call(self, prompts: List[str]) -> List[str]:
        """
        Process multiple prompts sequentially with better error handling.
        This can be extended for true batch processing if Ollama supports it in the future.
        """
        responses = []
        for i, prompt in enumerate(prompts):
            log_message(f"Processing batch item {i+1}/{len(prompts)}")
            try:
                response = await self.__call__(prompt)
                responses.append(response)
            except Exception as e:
                log_message(f"Error processing batch item {i+1}: {e}")
                responses.append(f"Error processing this request: {e}")
        return responses
    
    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None