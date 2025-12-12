from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi import Request
from starlette.responses import FileResponse
from contextlib import asynccontextmanager
import uvicorn


import app.core.api_setup as api_setup
import app.agent.run_agent as run_agent
from app.routers import chat,learn,scraper,query,test 
from app.core.settings import settings

@asynccontextmanager
async def lifespan(_app = FastAPI):
    api_setup.initiate()
    # await run_agent.run_agent()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(chat.router, prefix="/sauluhAI/v1",tags=["Want to bail out ?"])
app.include_router(learn.router, prefix="/sauluhAI/v1",tags=["Want to bail out ?"])
app.include_router(scraper.router, prefix="/sauluhAI/v1",tags=["Want to skim legal codes ?"])
app.include_router(query.router, prefix="/sauluhAI/v1",tags=["Want to know about legal codes ?"])
app.include_router(test.router, prefix="/sauluhAI/v1",tags=["Test model"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

ui = Jinja2Templates(directory="app/templates")

@app.get("/")
async def home_page(request: Request):
    return ui.TemplateResponse(
        name="legal_conversation.html", 
        context={
            "request": request,
            "api_url": f"{settings.CLIENT_SIDE_CALL}/sauluhAI/v1"
        }
    )


if __name__ == '__main__':
    config = uvicorn.Config("app.main:app", port=8080, host="0.0.0.0", workers=4)
    server = uvicorn.Server(config)
    server.run()