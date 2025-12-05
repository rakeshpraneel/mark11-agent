import aiohttp
from typing import List

from app.core.settings import settings

OLLAMA_BASE_URL = f"{settings.SERVER_SIDE_CALL}:11434"  # Default Ollama URL
EMBED_MODEL = "nomic-embed-text"

async def embed_with_ollama(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings using Gemini 2.x embedding model.
    Works for batches (recommended by Google).
    Returns: List of vectors.
    """
    try:
        embeddings = []
    
        async with aiohttp.ClientSession() as session:
            for text in texts:
                async with session.post(
                    f"{OLLAMA_BASE_URL}/api/embeddings",
                    json={
                        "model": EMBED_MODEL,
                        "prompt": text
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        embeddings.append(data["embedding"])
                    else:
                        raise Exception(f"Ollama embedding failed: {response.status}")
        
            return embeddings
            
    except Exception as e:
        print("Gemini embedding error:", e)
        raise e