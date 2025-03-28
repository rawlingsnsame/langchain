from langchain_openai import OpenAIEmbeddings
from typing import List
from config.settings import settings

from tenacity import retry, stop_after_attempt, wait_exponential

import time
import openai
import logging

logger = logging.getLevelName(__name__)
class EmbeddingService:
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL):
        self.api_key = settings.OPENAI_API_KEY
        self.model_name = model_name
        if not self.api_key:
            raise ValueError("OpenAI API key not set")
        self.model = self._initialize_embeddings(model_name)

    def _initialize_embeddings(self, model_name: str) -> OpenAIEmbeddings:
        try:
            return OpenAIEmbeddings(
                model=model_name,
                openai_api_key=self.api_key,
                max_retries=3,
                request_timeout=60.0
            )
        except Exception as e:
            logger.error(f"Error in _initialize_embeddings: {e}")
            raise
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )

    def embed_query(self, text: str) -> List[float]:
        try:
            text = text.replace("\n", " ")
            return self.model.embed_query(text)
        except openai.APIConnectionError as e:
            logger.error(f"API Connection Error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in embed_query: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            texts = [text.replace("\n", " ") for text in texts]
            return self.model.embed_documents(texts)
        except openai.APIConnectionError as e:
            logger.error(f"API Connection Error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in embed_documents: {e}")
            raise

    def _call_openai_api(self, texts: List[str]) -> List[List[float]]:
        retries = 3
        delay = 2

        for attempt in range(retries):
            try:
                response = openai.embeddings.create(
                    input = texts,
                    model = self.model_name,
                    api_key = self.api_key
                )
                return [item["embedding"] for item in response["data"]]
            except openai.RateLimitError:
                if attempt < retries - 1:
                    time.sleep(delay)
                    delay *= 2
                else:
                    raise RuntimeError("Rate limit exceeded. Try again later.")
            except Exception as e:
                raise RuntimeError(f"Error calling OpenAI API: {e}")

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self._call_openai_api(texts)
