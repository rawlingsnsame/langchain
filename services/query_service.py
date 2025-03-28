from typing import List
from utils.preprocessing import preprocess_query
from services.vectorestore_service import VectorStoreService
from config.settings import settings

from tenacity import retry, stop_after_attempt, wait_exponential

from openai import OpenAI

import logging

logger = logging.getLogger(__name__)

class QueryService:
    def __init__(self, vectorstore_service: VectorStoreService):
        self.vectorstore_service = vectorstore_service
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=60.0,
            max_retries=3
            )
        self.chat_model = settings.CHAT_MODEL
        self.temperature = settings.TEMPERATURE
        self.k_matching_docs = settings.K_MATCHING_DOCS

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )

    def process_query(self, query: str) -> List[str]:
        try:
            processed_query = preprocess_query(query)

            return self.vectorstore_service.similarity_search(
                processed_query, 
                k=self.k_matching_docs
            )
        except Exception as e:
            logger.error(f"Error in process_query: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )

    def generate_response(self, context: List[str], query: str) -> str:
        try:
            context_str = "\n\n".join([doc.page_content for doc in context])

            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a tax assistant with name taxbotspecializing in Cameroon tax regulations. " + \
                        "Provide clear, precise answers based on the given context."
                        "If the question is not related to tax in any way, tell the user nicely that you are not able to answer it."
                        "But your happy to help with any tax related questions." 
                        "How ever, if they are greetings, respond with a friendly greeting."
                    },
                    {
                        "role": "user",
                        "content": f"Context:\n{context_str}\n\nQuery: {query}",
                    },
                ],
                temperature=self.temperature,
            )
            response_content = response.choices[0].message.content
            return response_content
        except Exception:
            raise
