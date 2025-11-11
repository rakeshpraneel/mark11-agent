from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

import app.agent.run_agent as run_agent

router = APIRouter()

@router.post("/send_message")
async def chat_with_agent(input_msg: str):
    try:
        response = await run_agent.process_msg(input_msg)
        return JSONResponse(status_code=200, content=str(response))
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))