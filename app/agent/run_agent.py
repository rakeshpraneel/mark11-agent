from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search
from google.adk.runners import InMemoryRunner
from google.adk.agents import Agent, LlmAgent
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.sessions import DatabaseSessionService
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

import app.config.retry as retry
import app.agent.runner_function as runner_function
from app.core.settings import settings

global runner
global session_service


async def run_agent():
    global runner
    global session_service

    system_instruction = """
                You are a structured assistant with smart formatting rules.

RULES:
1. If the response is short (1-2 sentences), return plain text without any JSON, bullets, newlines, or markdown.
2. If the response is detailed, multi-step, or long:
   - Use clean, human-readable bullet points.
   - Keep formatting minimal and compatible with Swagger.
   - Avoid markdown symbols such as **, ##, or backticks.
   - Use simple hyphen '-' bullets OR numbered bullets.
3. NEVER include JSON formatting.
4. NEVER escape characters (no \\n). Use real newlines.
5. Keep all output clean and readable.

Examples:

SHORT ANSWER:
"Yes, you can update a Docker image without restarting the database."

LONG ANSWER:
- Step 1: Build the updated image.
- Step 2: Push it to Docker Hub.
- Step 3: Trigger the Render deployment webhook.
- Step 4: The Render service will pull the new image.

ALWAYS follow this smart-format rule.
"""

    chatbot_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry.retry_config, system_instruction=system_instruction),
    name="text_chat_bot",
    description="A text chatbot with persistent memory",
    tools=[google_search],
)

    # Step 2: Switch to DatabaseSessionService
    # SQLite database will be created automatically
    # db_url = "sqlite:///my_agent_data.db"  # Local SQLite file
    db_url = settings.DB_URL
    session_service = DatabaseSessionService(db_url=db_url)

    # Step 3: Create a new runner with persistent storage
    runner = Runner(agent=chatbot_agent, app_name=settings.APP_NAME, session_service=session_service)

    print("✅ Upgraded to persistent sessions!")
    print(f" {session_service}  - Database: {db_url}")
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