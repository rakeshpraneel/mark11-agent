from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
import requests

import app.agent.run_agent as run_agent

router = APIRouter()

@router.get("/test",summary="test local models")
async def test_ollama():
    try:
        response = requests.get("http://localhost:11434/api/tags")
        return JSONResponse(status_code=200, content=str(response.json()))
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))