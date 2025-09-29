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
        """Async function to call Ollama LLM"""
        if self.session is None:
            await self._init_session()

        log_message(f"Sending prompt to Ollama (length: {len(prompt)} chars)...")
        
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": 8192,
                "temperature": 0.1,
                "top_p": 0.9,
                "num_predict": -1,
            }
        }

        try:
            response_text = await self._make_request_with_retry(url, payload)
            log_message(f"Received LLM response (length: {len(response_text)} chars)")
            return response_text
                        
        except Exception as e:
            log_message(f"Error calling Ollama: {e}")
            return f"Sorry, an error occurred: {e}"
    
    async def _init_session(self):
        """Initialize the HTTP session with optimized settings"""
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=30,
            keepalive_timeout=300,
            enable_cleanup_closed=True
        )
        timeout = aiohttp.ClientTimeout(total=300)
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
                    wait_time = 2 ** attempt
                    log_message(f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    raise e
    
    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
