import aiohttp
from utils import log_message
import asyncio

class OllamaLLM:
    def __init__(self, model="llama3.2", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.session = None
        log_message(f"Initialized Ollama LLM with model: {model}")

    async def __call__(self, prompt):
        """Async function to call Ollama LLM"""
        if self.session is None:
            await self._init_session()

        log_message(f"Sending prompt to Ollama: {prompt[:100]}...")
        
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        try:
            response_text = await self._make_request_with_retry(url, payload)
            log_message(f"Received Ollama response: {response_text[:100]}...")
            return response_text
                        
        except Exception as e:
            log_message(f"Error calling Ollama: {e}")
            return f"Sorry, an error occurred: {e}"
    
    async def _init_session(self):
        """Initialize the HTTP session with optimized settings for concurrent requests"""
        connector = aiohttp.TCPConnector(
            limit=100,              # Max total connections
            limit_per_host=30,      # Max connections per host (Ollama)
            keepalive_timeout=300,  # Keep connections alive
            enable_cleanup_closed=True
        )
        timeout = aiohttp.ClientTimeout(total=300)  # 5 min timeout
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
                    log_message(f"All retry attempts failed: {e}")
                    raise e
    
    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
            log_message("Ollama HTTP session closed")