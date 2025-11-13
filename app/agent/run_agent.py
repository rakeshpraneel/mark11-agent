from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search
from google.adk.runners import InMemoryRunner
from google.adk.agents import Agent, LlmAgent
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.sessions import DatabaseSessionService
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

import app.config.retry as retry
import app.agent.runner_function as runner_function
from app.core.settings import settings

global runner
global session_service


async def run_agent():
    global runner
    global session_service

    chatbot_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry.retry_config),
    name="text_chat_bot",
    description="A text chatbot with persistent memory",
    tools=[google_search]
)

    # Step 2: Switch to DatabaseSessionService
    # SQLite database will be created automatically
    # db_url = "sqlite:///my_agent_data.db"  # Local SQLite file
    db_url = settings.DB_URL
    session_service = DatabaseSessionService(db_url=db_url)

    # Step 3: Create a new runner with persistent storage
    runner = Runner(agent=chatbot_agent, app_name=settings.APP_NAME, session_service=session_service)

    print("✅ Upgraded to persistent sessions!")
    print(f"   - Database: my_agent_data.db")
    print(f"   - Sessions will survive restarts!")


async def process_msg(input_msg, user_id):
    global session_service
    print("Inside process message")
    print(type(session_service))
    response = await runner_function.run_session(
    runner,
    input_msg,
    session_name="default",
    session_service=session_service,
    user_id=user_id
    )

    return response 

# async def run_agent():
#     global runner
#     root_agent = Agent(
#     name="helpful_assistant",
#     model=Gemini(
#         model="gemini-2.5-flash-lite",
#         retry_options=retry.retry_config
#     ),
#     description="A simple agent that can answer general questions.",
#     instruction="You are a helpful assistant. Use Google Search for current info or if unsure.",
#     tools=[google_search],
#     )

#     print("Root agent defined")

#     runner = InMemoryRunner(agent=root_agent)

# async def process_msg(input_msg):
#     response = await runner.run_debug(input_msg)
#     return response