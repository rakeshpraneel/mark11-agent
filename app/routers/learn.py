from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from io import BytesIO
import datetime

import app.agent.run_agent as run_agent

router = APIRouter()

@router.post("/get_document",summary ="Learn with Sauluh", 
             description="Sauluh gives you documented response, can be used for learning and ref purposes, " \
             "He is running on free tier so pls be mindfull or else he'll run away 🏃")
async def chat_with_agent(input_msg: str, request: Request):
    try:
        client_host = request.client.host
        try:
            response = await run_agent.process_msg(input_msg, client_host)

            response = str(response)

            buffer = BytesIO()
            buffer.write(response.encode("utf-8"))
            buffer.seek(0)

            # File name with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sauluh_response_{timestamp}.txt"


            return StreamingResponse(
            buffer,
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            },
        )

        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"Issue reading client host::: {str(e)}")
        return HTTPException(status_code=500, detail=str(e))