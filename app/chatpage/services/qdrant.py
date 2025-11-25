from django.conf import settings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams


def get_qdrant_client():
    client = QdrantClient(settings.QDRANT_HOST)
    vector_size = len(settings.EMBEDDINGS.embed_query("some random text"))

    if not client.collection_exists(settings.QDRANT_COLLECTION):
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

    return client


client = get_qdrant_client()

vector_store = QdrantVectorStore(
    client=client,
    collection_name=settings.QDRANT_COLLECTION,
    embedding=settings.EMBEDDINGS,
)
