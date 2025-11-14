from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

import app.agent.run_agent as run_agent

router = APIRouter()

@router.post("/send_message",summary="Chat with Sauluh",
             description="Feeling bored or want to know something, chat with sauluh he may help you, "\
             "He is running on free tier so pls be mindfull or else he'll run away 🏃")
async def chat_with_agent(input_msg: str, request: Request):
    try:
        client_host = request.client.host
        try:
            response = await run_agent.process_msg(input_msg, client_host)
            return JSONResponse(status_code=200, content=str(response))
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))