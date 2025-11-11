from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search
from google.adk.runners import InMemoryRunner

import app.config.retry as retry

global runner



async def run_agent():
    global runner
    root_agent = Agent(
    name="helpful_assistant",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry.retry_config
    ),
    description="A simple agent that can answer general questions.",
    instruction="You are a helpful assistant. Use Google Search for current info or if unsure.",
    tools=[google_search],
    )

    print("Root agent defined")

    runner = InMemoryRunner(agent=root_agent)

async def process_msg(input_msg):
    response = await runner.run_debug(input_msg)
    return response