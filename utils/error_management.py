import openai
import pinecone

def get_friendly_error_message(error: Exception) -> str:
    """Convert technical errors to user-friendly messages."""
    if isinstance(error, openai.APIConnectionError):
        return "Unable to connect to the service. Please check your internet connection and try again."
    elif isinstance(error, openai.RateLimitError):
        return "The service is currently busy. Please try again in a few moments."
    elif isinstance(error, openai.APIError):
        return "The service is temporarily unavailable. Please try again later."
    elif isinstance(error, pinecone.PineconeException):
        return "Unable to access the knowledge base. Please try again later."
    else:
        return "Something went wrong. see logs."
