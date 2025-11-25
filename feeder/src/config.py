import os

from langchain_ollama import OllamaEmbeddings


class Config:
    QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
    QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "news_articles")

    MODEL_NAME = os.getenv("MODEL_NAME")
    OLLAMA_URL = os.getenv("OLLAMA_URL")
    EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL")

    EMBEDDINGS = OllamaEmbeddings(model=EMBEDDINGS_MODEL, base_url=OLLAMA_URL)
