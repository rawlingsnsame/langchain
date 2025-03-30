import logging
import traceback

logger = logging.getLogger(__name__)

ERROR_MESSAGES = {
    "openai.APIConnectionError": "Connection to AI service failed. Please check your network.",
    "openai.RateLimitError": "Rate limit exceeded. Please try again later.",
    "openai.AuthenticationError": "Authentication failed. Check your API key.",
    "ValueError": "Invalid input provided.",
    "pinecone.ServerError": "Pinecone server error. Please try again later.",
    "pinecone.ClientError": "Pinecone client error. Check your API key and index name.",
    "pinecone.IndexError": "Index not found. Check your index name.",
    "pinecone.TimeoutError": "Pinecone request timed out. Please try again later.",
    "pinecone.ConnectionError": "Connection to Pinecone failed. Please check your network.",
}


class CustomApplicationError(Exception):
    """Custom base class for application-specific errors."""

    pass


def get_friendly_error_message(error: Exception) -> str:
    """Convert technical errors to user-friendly messages."""
    error_type = error.__class__.__name__
    qualified_name = f"{error.__class__.__module__}.{error_type}"

    logger.error(f"Error occurred: {error}\n{traceback.format_exc()}")

    for name in [qualified_name, error_type]:
        if name in ERROR_MESSAGES:
            message = ERROR_MESSAGES[name]

            if hasattr(error, "retry_after"):
                message += f" Retry after {error.retry_after} seconds."
            return message

    return "An unexpected error occurred. Please try again later."
