# Tools.py
# Packages
import os
import asyncio
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Any

from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_default_openai_client,
    set_tracing_export_api_key,
    function_tool,
    ModelSettings,
    RunContextWrapper
)

# ----------------------------------------------------------------------
# Load environment variables
# ----------------------------------------------------------------------
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("Please set a valid OPENAI_API_KEY in your .env file")

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("Please set a valid GEMINI_API_KEY in your .env file")

news_api_key = os.getenv("NEWS_API_ORG")
if not news_api_key:
    raise ValueError("Please set a valid NEWS_API_ORG key in your .env file")

# ----------------------------------------------------------------------
# Enable tracing to OpenAI Dashboard
# ----------------------------------------------------------------------
set_tracing_export_api_key(openai_api_key)

# ----------------------------------------------------------------------
# Initialize Provider (Google Gemini via OpenAI-compatible endpoint)
# ----------------------------------------------------------------------
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

set_default_openai_client(client=external_client, use_for_tracing=False)

model = OpenAIChatCompletionsModel(
    openai_client=external_client,
    model="gemini-2.5-flash"
)

# ----------------------------------------------------------------------
# Custom Error Handler for Function Tool
# ----------------------------------------------------------------------
def custom_news_error(context: RunContextWrapper[Any], error: Exception) -> str:
    """Custom error handler for get_tech_updates tool."""
    print(f"[Tool Error] get_tech_updates failed: {error}")
    return {"error": "The news service is temporarily unavailable. Please try again later."}

# ----------------------------------------------------------------------
# Function Tool for Tech Updates
# ----------------------------------------------------------------------
@function_tool(name_override="fetch_updated_news", failure_error_function=custom_news_error)
def get_tech_updates(query: str = "tech news Pakistan"):
    """
    Fetch the latest updates from any topic or company using NewsAPI.
    Returns a list of structured updates (title, description, source, published_at).
    """
    results = []
    keywords = [word for word in query.lower().split() if word not in ["from", "and", "or", "of", "in"]]
    primary_query = " ".join(keywords) if keywords else query.lower()

    if any(intent in query.lower() for intent in ["latest", "today"]):
        today = datetime.now().strftime("%Y-%m-%d")
        date_filter = f"&from={today}&to={today}"
    elif "last" in query.lower():
        last_week = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        date_filter = f"&from={last_week}&to={today}"
    else:
        last_month = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        date_filter = f"&from={last_month}&to={today}"

    all_terms = [primary_query] + keywords
    for term in all_terms:
        news_url = f"https://newsapi.org/v2/everything?q={term}{date_filter}&apiKey={news_api_key}"
        news_response = requests.get(news_url, timeout=5)
        news_data = news_response.json()
        if news_data.get("status") == "ok":
            articles = news_data.get("articles", [])[:5]
            filtered_results = [
                {
                    "title": article.get("title"),
                    "description": article.get("description", "No description"),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "published_at": article.get("publishedAt", "No date")
                }
                for article in articles if article.get("title")
            ]
            results.extend(filtered_results)
            if len(results) >= 5:
                break
        else:
            raise ValueError(f"News API error: {news_data.get('message', 'Unknown error')}")

    if results:
        return results
    else:
        raise ValueError("No updates found. Try a more specific query (e.g., 'Tesla news last week').")

# ----------------------------------------------------------------------
# Main Function
# ----------------------------------------------------------------------
async def main():
    agent = Agent(
        name="Tech Update Agent",
        instructions=(
            "You're an expert personal research agent focused on updates from any topic or company. "
            "Use the get_tech_updates tool to fetch the latest news or updates based on the query. "
            "Structure the response with a summary of the top 3-5 updates, including titles, "
            "brief descriptions, sources, and publish dates (e.g., 'published on YYYY-MM-DD'). "
            "Highlight real-time relevance (e.g., 'published today') if the date matches August 28, 2025. "
            "If no updates are found, suggest rephrasing the query with examples."
        ),
        tools=[get_tech_updates],
        model_settings=ModelSettings(tool_choice="required", max_tokens=500),
        model=model
    )

    queries = ["give me updates of Meta Zuckerberg in AI?"]

    for query in queries:
        try:
            output = await Runner.run(agent, query)
            print(f"\nQuery: {query}")
            print(f"Response: {output.final_output}\n")
        except Exception as e:
            print(f"\nQuery: {query}")
            print(f"Error: {str(e)}\n")

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
