import os

from langchain_ollama import OllamaEmbeddings


class Config:
    QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
    QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "news_articles")

    MODEL_NAME = os.getenv("MODEL_NAME", "qwen3:1.7b")
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
    EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL", "qwen3-embedding:4b")

    if EMBEDDINGS_MODEL:
        EMBEDDINGS = OllamaEmbeddings(model=EMBEDDINGS_MODEL, base_url=OLLAMA_URL)
    else:
        raise ValueError("No EMBEDDINGS_MODEL was set")
