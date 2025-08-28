# Tools.py

import os
import asyncio
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Any
from agents import (
    Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel,
    set_default_openai_client, set_tracing_export_api_key,
    function_tool, ModelSettings, RunContextWrapper
)

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")
news_api_key   = os.getenv("NEWS_API_ORG")

if not all([openai_api_key, gemini_api_key, news_api_key]):
    raise ValueError("Please set OPENAI_API_KEY, GEMINI_API_KEY, and NEWS_API_ORG in your .env file")

# Enable tracing
set_tracing_export_api_key(openai_api_key)

# Setup Gemini client
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
set_default_openai_client(client=external_client, use_for_tracing=False)

model = OpenAIChatCompletionsModel(openai_client=external_client, model="gemini-2.5-flash")

# Custom error handler
def custom_news_error(context: RunContextWrapper[Any], error: Exception) -> str:
    print(f"[Tool Error] get_tech_updates failed: {error}")
    return {"error": "The news service is temporarily unavailable. Please try again later."}

# Function Tool
@function_tool(name_override="fetch_updated_news", failure_error_function=custom_news_error)
def get_tech_updates(query: str = "tech news Pakistan"):
    """Fetch the latest updates from any topic/company using NewsAPI."""
    # Logic (API request + filtering) ...
    # Returns list of news articles
    ...

# Main agent
async def main():
    agent = Agent(
        name="Tech Update Agent",
        instructions=(
            "You're an expert personal research agent. "
            "Use the get_tech_updates tool to fetch the latest updates."
        ),
        tools=[get_tech_updates],
        model_settings=ModelSettings(tool_choice="required", max_tokens=500),
        model=model
    )
    query = "give me updates of Meta Zuckerberg in AI?"
    output = await Runner.run(agent, query)
    print(f"\nQuery: {query}")
    print(f"Response: {output.final_output}\n")

if __name__ == "__main__":
    asyncio.run(main())

'''
Output:
Query: give me updates of Meta Zuckerberg in AI?

Response: Here are the latest updates on Meta and Mark Zuckerberg's endeavors in AI:

* Meta’s stock price surged after strong earnings, signaling investor confidence despite heavy AI spending.
  Source: The Verge, published on 2025-07-31

* Meta is partnering with Midjourney to integrate its aesthetic technology into Meta’s AI products.
  Source: The Verge, published on 2025-08-22

* Zuckerberg’s “personal superintelligence” plan aims to embed AI more deeply into free time activities.
  Source: The Verge, published on 2025-08-02

* Meta strengthens position in smart glasses with major eyewear partnership.
  Source: Wired, published on 2025-08-02

''''
