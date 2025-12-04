'''
Module for writing and searching data from vectore database
'''

from typing import List, Dict, Any
from app.services.qdrant_client import get_qdrant_client, ensure_collection, COLLECTION_NAME
from app.utility.embedder import embed_with_ollama
import uuid
import datetime

DIMENSION = 768  # Gemini model text-embedding-004 always returns 768-dim vectors.

# Upsert documents (list of dicts with content + metadata)
async def upsert_documents(docs: List[Dict[str, Any]]):
    client = get_qdrant_client()
    ensure_collection(client, DIMENSION)
    points = []
    for doc in docs:
        text = doc["content"]
        # if using cloud embedding, use async function; here we use sync embed_texts
        vec = (await embed_with_ollama([text]))[0]
        payload = doc.get("meta", {})
        points.append({
            "id": doc.get("id", str(uuid.uuid4())),
            "vector": vec,
            "payload": payload | {"text": text}
        })
    client.upsert(collection_name=COLLECTION_NAME, points=points)

async def search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    client = get_qdrant_client()
    ensure_collection(client, DIMENSION)
    q_vec = (await embed_with_ollama([query]))[0]
    hits = client.query_points(collection_name=COLLECTION_NAME, 
                               query=q_vec, 
                               limit=top_k,
                               with_payload=True,
                            with_vectors=False)
    results = []
    for h in hits.points:
        print(h)
        print("--"*10)
        results.append({
            "id": h.id,
            "score": h.score,
            "payload": h.payload
        })
    print("results")
    print(results)
    return results
