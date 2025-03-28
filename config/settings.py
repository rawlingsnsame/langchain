import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

    EMBEDDING_MODEL = "text-embedding-ada-002"
    EMBEDDING_DIMENSION = 1536

    CHAT_MODEL = "gpt-4"

    K_MATCHING_DOCS = 2
    TEMPERATURE = 0.75


settings = Settings()
