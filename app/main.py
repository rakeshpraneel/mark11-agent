from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn


import app.core.api_setup as api_setup
import app.agent.run_agent as run_agent
import app.routers.chat as chat 

@asynccontextmanager
async def lifespan(_app = FastAPI):
    api_setup.initiate()
    await run_agent.run_agent()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(chat.router, prefix="/sauluhAI/v1")


if __name__ == '__main__':
    config = uvicorn.Config("app.main:app", port=8080, host="0.0.0.0", workers=4)
    server = uvicorn.Server(config)
    server.run()