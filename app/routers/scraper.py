from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
import aiohttp
import datetime
import uuid

import app.agent.run_agent as run_agent
from app.utility.chunker import simple_chunk_text
from app.utility.rag_tool import upsert_documents

router = APIRouter()

@router.post("/scrap",summary="Go Through The Website",
             description="Provide the website url, saul will help u out with queries")
async def scrap_with_agent(url: str):
    # Simple website fetch; for large sites, build async crawler
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=400, detail=f"Failed to fetch {url}")
            html = await resp.text()
    soup = BeautifulSoup(html, "html.parser")
    # Extract visible text from <p> and headers
    paragraphs = []
    for tag in soup.find_all(["p", "h1", "h2", "h3", "li"]):
        text = tag.get_text(strip=True)
        if text:
            paragraphs.append(text)
    text = "\n\n".join(paragraphs)
    chunks = simple_chunk_text(text)
    docs = []
    for i, c in enumerate(chunks):
        docs.append({
        "id": str(uuid.uuid4()),  # Generate a proper UUID
        "content": c,
        "meta": {
            "source_url": url, 
            "chunk_index": i,  # Store the chunk number in metadata instead
            "scraped_at": datetime.datetime.utcnow().isoformat()
        }
    })
    await upsert_documents(docs)
    return {"status": "ok", "uploaded_chunks": len(docs)}