import asyncio
from services.embedding_service import EmbeddingService
from services.vectorestore_service import VectorStoreService
from services.query_service import QueryService

from utils.error_management import get_friendly_error_message, CustomApplicationError


def initialize_vectorstore():
    """Initialize Pinecone vectorstore with dependency injection."""
    try:
        embedding_service = EmbeddingService()
        vector_storeService = VectorStoreService(embedding_service)
        query_service = QueryService(vector_storeService)

        return embedding_service, vector_storeService, query_service
    except Exception as e:
        raise CustomApplicationError("Failed to initialize vectorstore") from e


async def chatbot(prompt):

    try:
        embedding_service, vector_storeService, query_service = initialize_vectorstore()

        if not prompt:
            return "No prompt provided."

        retrieved_docs = query_service.process_query(prompt)
        response = query_service.generate_response(retrieved_docs, prompt)
        await asyncio.sleep(1)
        return {"response": response}

    except Exception as e:
        error_msg = get_friendly_error_message(e)
        return error_msg

