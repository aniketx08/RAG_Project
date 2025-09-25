# rag_chain.py
from langchain_core.runnables import Runnable
from utils import log_message
import asyncio

class CustomRAGChain(Runnable):
    def __init__(self, retriever, llm, prompt_template):
        self.retriever = retriever
        self.llm = llm
        self.prompt_template = prompt_template

    def invoke(self, input: dict, config=None) -> dict:
        """LangChain Runnable entrypoint - synchronous version"""
        question = input["question"]

        # Retrieve docs
        docs = self.retriever.get_relevant_documents(question)
        context = "\n".join([d.page_content for d in docs])

        # Build prompt
        prompt = self.prompt_template.format(
            context=context,
            question=question
        )

        # Call LLM - Note: this would need to be made async in a real implementation
        # For now, we'll run the async method in a sync context
        loop = asyncio.get_event_loop()
        answer = loop.run_until_complete(self.llm(prompt))
        return {"output": answer}

    async def run(self, question: str) -> str:
        """Single question processing (for backwards compatibility)"""
        docs = self.retriever.get_relevant_documents(question) 
        context = "\n".join([d.page_content for d in docs])
        prompt = self.prompt_template.format(context=context, question=question)
        
        # Await the LLM's response
        answer = await self.llm(prompt)
        return answer