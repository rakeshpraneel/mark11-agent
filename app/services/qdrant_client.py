from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
from app.core.settings import settings

# Configure from env or constants
QDRANT_HOST = settings.QDRANT_CLUSTER
QDRANT_API_KEY = settings.QDRANT_API_KEY
COLLECTION_NAME = "rag_documents"

def get_qdrant_client():
    # If using Qdrant Cloud (https), set url and api_key
    if QDRANT_API_KEY:
        return QdrantClient(url=f"https://{QDRANT_HOST}", api_key=QDRANT_API_KEY, )
    else:
        print("Key not found")
        return None

def ensure_collection(client: QdrantClient, dim: int):
    if COLLECTION_NAME not in [c.name for c in client.get_collections().collections]:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
        )
