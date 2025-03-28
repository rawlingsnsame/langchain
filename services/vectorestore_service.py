import pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import Pinecone
from services.embedding_service import EmbeddingService
from config.settings import settings
from utils.error_management import get_friendly_error_message

import logging

class VectorStoreService:
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        self.logger = logging.getLogger(__name__)
        self.vectorstore = self._initilaize_pinecone()

    def _initilaize_pinecone(self):
        try:
            
            pc = pinecone.Pinecone(
                api_key=settings.PINECONE_API_KEY,
                environment="us-east-1-aws"
            )

            index_name = settings.INDEX_NAME

            if index_name not in pc.list_indexes().names():
                pc.create_index(
                    name=index_name,
                    dimension=1536,
                    metric="euclidean",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                )

            return Pinecone.from_existing_index(
                index_name=index_name, embedding=self.embedding_service, text_key="text"
            )
        except Exception as e:
            error_msg = get_friendly_error_message(e)
            self.logger.error(f"Error initializing Pinecone: {e}")
            raise error_msg
    
    def similarity_search(self, query: str, k: int = 3) -> list:
        if self.vectorstore is None:
            return []
        return self.vectorstore.similarity_search(query, k=k)
