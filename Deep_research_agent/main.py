import os
import asyncio
import re
import json
import requests
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent

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

# Apply nest_asyncio for Jupyter compatibility
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass

# Load environment variables
load_dotenv()

# Validate API keys
openai_api_key = os.getenv("OPENAI_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")
serp_api_key = os.getenv("SERP_API_KEY")

if not openai_api_key or not gemini_api_key:
    raise ValueError("Please set both OPENAI_API_KEY and GEMINI_API_KEY in your .env file")
if not tavily_api_key or not tavily_api_key.startswith("tvly-"):
    raise ValueError("Please set a valid TAVILY_API_KEY in your .env file")
if not serp_api_key:
    raise ValueError("Please set a valid SERP_API_KEY in your .env file")

# Set up tracing and client
set_tracing_export_api_key(openai_api_key)
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
set_default_openai_client(client=external_client, use_for_tracing=False)

# Configure model
model = OpenAIChatCompletionsModel(
    openai_client=external_client,
    model="gemini-2.5-flash"
)

# Custom Tavily Error Handler
def custom_tavily_error(context: RunContextWrapper[Any], error: Exception) -> str:
    print(f"[Tool Error] fetch_web_data failed: {error}")
    return {"error": "Tavily web search unavailable. Falling back to other sources..."}

# Raw Function for Tavily Web Search
def raw_fetch_web_data(query: str) -> List[Dict]:
    """
    Performs a deep web search using Tavily API with date filter for recent results.
    """
    url = "https://api.tavily.com/search"
    headers = {
        "Authorization": f"Bearer {tavily_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "query": f"{query} 2025",
        "max_results": 5,
        "search_depth": "advanced",
        "start_date": "2025-01-01"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        if not results:
            print("[Tavily Warning] No results returned for query.")
        return [
            {
                "title": result.get("title", "Untitled"),
                "description": result.get("content", "No description"),
                "url": result.get("url", "No URL"),
                "published_at": result.get("published_date", "No date"),
                "source": "Tavily",
                "icon": "📝"
            }
            for result in results
        ]
    except Exception as e:
        print(f"[Tavily API Error] {e}")
        return []

fetch_web_data = function_tool(raw_fetch_web_data, name_override="fetch_web_data", failure_error_function=custom_tavily_error)

# Raw Function for SerpAPI Web Search
def raw_fetch_web_data_serp(query: str) -> List[Dict]:
    """
    Performs web search using SerpAPI with date filter for recent results.
    """
    url = "https://serpapi.com/search.json"
    params = {
        "q": f"{query} 2025",
        "api_key": serp_api_key,
        "num": 5,
        "tbs": "qdr:m"
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        results = data.get("organic_results", [])
        if not results:
            print("[SerpAPI Warning] No results returned for query.")
        return [
            {
                "title": result.get("title", "Untitled"),
                "description": result.get("snippet", "No description"),
                "url": result.get("link", "No URL"),
                "published_at": result.get("date", "No date"),
                "source": "SerpAPI",
                "icon": "🌐"
            }
            for result in results
        ]
    except Exception as e:
        print(f"[SerpAPI Error] {e}")
        return []

fetch_web_data_serp = function_tool(raw_fetch_web_data_serp)

# Raw Function for Hybrid Search
def raw_fetch_web_data_hybrid(query: str) -> List[Dict]:
    """
    Hybrid search using Tavily and SerpAPI. Returns top 5 results, prioritizing credible sources.
    """
    results = []
    try:
        tavily_results = raw_fetch_web_data(query)
        print(f"[Tavily Debug] Retrieved {len(tavily_results)} results")
        results.extend(tavily_results)
    except Exception as e:
        print(f"[Tavily Error] {e}")
    try:
        serp_results = raw_fetch_web_data_serp(query)
        print(f"[SerpAPI Debug] Retrieved {len(serp_results)} results")
        results.extend(serp_results)
    except Exception as e:
        print(f"[SerpAPI Error] {e}")

    # Deduplicate URLs and prioritize credible, recent results
    seen = set()
    final_results = []
    current_year = str(datetime.now().year)
    for r in results:
        url = r.get("url", "")
        if url and url not in seen and url != "No URL":
            published = r.get("published_at", "No date")
            if current_year in published or published == "No date":
                final_results.append(r)
                seen.add(url)
    final_results = sorted(final_results, key=lambda x: x["published_at"] != "No date", reverse=True)[:5]
    if not final_results:
        print("[Hybrid Search Warning] No valid results from any source.")
    return final_results

fetch_web_data_hybrid = function_tool(raw_fetch_web_data_hybrid)

# PlanningAgent
planning_agent = Agent(
    name="PlanningAgent",
    instructions="""
    You are a planning agent tasked with creating a concise, actionable research plan for any user query.
    - Analyze the query to identify its intent and key topics (e.g., events, updates, definitions).
    - Generate a plan with 4-5 focused, numbered steps (e.g., '1. Search for...', '2. Identify...').
    - Ensure the plan is tailored to the query, uses a numbered list format (e.g., '1. ', '2. '), and guides a web search.
    - Include steps to:
      - Search primary or official sources (e.g., government sites, reputable news for updates).
      - Extract key details (e.g., dates, events, or facts) relevant to the query.
      - Validate with secondary or community sources (e.g., forums, X posts).
      - Prioritize information from 2025 for recency.
    - Return only the plan as plain text, with each step on a new line.
    - Avoid narrative, reports, or extra content.
    """,
    model_settings=ModelSettings(max_tokens=1000),
    model=model
)

# WebSearchAgent
web_search_agent = Agent(
    name="WebSearchAgent",
    instructions="""
    You are a Web Search Expert. Receive a research plan and the original query.
    - Parse the plan into steps (lines starting with '1. ', '2. ', etc.).
    - For each step, use `fetch_web_data_hybrid` with the query and '2025' to fetch relevant, recent results.
    - Return a JSON-serializable list of dictionaries with fields: title, description, url, published_at, source, icon.
    - Ensure results are relevant, have valid URLs, and prioritize 2025 data.
    - If no results, return an empty list.
    - Output only the JSON list (e.g., [{"title": "Example", "description": "Desc", "url": "https://example.com", "published_at": "2025-01-01", "source": "Tavily", "icon": "📝"}]).
    - Do NOT return narratives, reports, or text summaries.
    """,
    tools=[fetch_web_data_hybrid],
    model_settings=ModelSettings(tool_choice="required", max_tokens=1500),
    model=model
)

# ReportingAgent
reporting_agent = Agent(
    name="Reporting_Agent",
    instructions="""
    You are a Reporting Agent specializing in concise, professional reports. Receive search results (list of dictionaries) and the original query.
    - Synthesize results into a markdown report with:
      - **Introduction**: One sentence stating the query and purpose.
      - **Key Findings**: 3-5 bullet points summarizing critical details (e.g., events, updates), prioritizing 2025 data.
      - **Analysis**: Note any inconsistencies, gaps, or source biases in 1-2 sentences.
      - **Conclusion**: One sentence summarizing findings and next steps.
      - **Citations**: List sources (title, source, URL) in a numbered list.
    - Filter out results older than 2025 unless critical to context.
    - If no results, provide a fallback report with a general overview based on the query and a note on data limitations.
    - Keep the report concise (150-200 words), professional, and query-focused.
    Return the report as plain text in markdown format.
    """,
    model_settings=ModelSettings(max_tokens=2000),
    model=model
)

# OrchestratorAgent
orchestrator_agent = Agent(
    name="Orchestrator_Agent",
    instructions="""
    You are an Orchestrator Agent coordinating research for any user query.
    - Execute these steps exactly once, in sequence:
      1. Call `plan_research` to create a research plan. Print "Planning..." and stream with '[Plan Stream]'.
      2. Print the plan under "Research Plan:".
      3. Call `search_web` with the plan and query. Print "Searching..." and stream with '[Search Stream]'.
      4. Print sources (title, source, URL) under "Sources Retrieved:".
      5. Call `generate_report` with results and query. Print "Reporting..." and stream with '[Report Stream]'.
      6. Print the report under "Final Report:".
    - Do NOT repeat steps or tools. Use state tracking to enforce single execution.
    - Log tool calls with '[Tool Call Debug]'.
    - Ensure outputs are relevant to 2025 and query-focused.
    Return the final report as markdown.
    """,
    tools=[
        planning_agent.as_tool(
            tool_name="plan_research",
            tool_description="Generate a concise research plan for a query."
        ),
        web_search_agent.as_tool(
            tool_name="search_web",
            tool_description="Search the web based on a plan and query, returning a JSON list of results."
        ),
        reporting_agent.as_tool(
            tool_name="generate_report",
            tool_description="Synthesize search results into a concise markdown report."
        ),
    ],
    model_settings=ModelSettings(tool_choice="auto", max_tokens=3000),
    model=model
)

# Main function with streaming
async def main():
    queries = ["Give me updates in the world of tech?"]  # User query
    executed_steps = set()
    for query in queries:
        print(f"\nProcessing Query: {query}")
        try:
            # Step 1: Generate research plan
            if "plan" not in executed_steps:
                print("Planning...")
                plan_result = Runner.run_streamed(orchestrator_agent, input=f"Generate a research plan for: {query}")
                plan = ""
                async for event in plan_result.stream_events():
                    if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                        delta = event.data.delta
                        if delta.strip():  # Filter out empty or invalid deltas
                            print(f"[Plan Stream] {delta}", end="", flush=True)
                            plan += delta
                print()
                if not plan or isinstance(plan, dict) and "error" in plan:
                    print("Planning Error: No valid plan generated")
                    plan = (
                        f"1. Search for reputable tech news sources for {query}.\n"
                        "2. Identify key developments in 2025.\n"
                        "3. Validate with secondary sources like X posts.\n"
                        "4. Prioritize information from 2025.\n"
                    )
                # Clean up plan to remove any [Plan Stream] tags
                plan = re.sub(r'\[Plan Stream\]', '', plan).strip()
                print("Research Plan:")
                print(plan)
                executed_steps.add("plan")
                print("[Tool Call Debug] plan_research executed")

            # Step 2: Perform web search
            print("-" * 80)
            if "search" not in executed_steps:
                print("Searching...")
                search_result = Runner.run_streamed(orchestrator_agent, input=f"Search the web based on this plan:\n{plan}\nOriginal query: {query}")
                search_output = []
                search_buffer = ""
                async for event in search_result.stream_events():
                    if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                        delta = event.data.delta
                        if delta.strip():
                            print(f"[Search Stream] {delta}", end="", flush=True)
                            search_buffer += delta
                print()
                print(f"[Debug] Raw search output: {search_buffer}")
                try:
                    if search_buffer.strip().startswith("[") and search_buffer.strip().endswith("]"):
                        search_output = json.loads(search_buffer.strip())
                    else:
                        json_match = re.search(r'\[\s*{.*?}\s*\]', search_buffer, re.DOTALL)
                        if json_match:
                            search_output = json.loads(json_match.group(0))
                        else:
                            # Try single object
                            json_match = re.search(r'\{.*?}\s*$', search_buffer, re.DOTALL)
                            if json_match:
                                search_output = [json.loads(json_match.group(0))]
                            else:
                                print("Search Warning: Unexpected output format")
                                search_output = []
                except Exception as e:
                    print(f"Search Parse Error: {e}")
                    search_output = []
                if not search_output:
                    print("Search Results: No valid data retrieved. Falling back to direct hybrid search.")
                    search_output = raw_fetch_web_data_hybrid(query)
                if not search_output:
                    print("Search Results: No valid data from direct search.")
                    search_output = [
                        {
                            "title": f"Fallback: Overview of {query}",
                            "description": f"General overview of {query}.",
                            "url": "https://example.com/fallback",
                            "published_at": "No date",
                            "source": "Fallback",
                            "icon": "📚"
                        }
                    ]
                print("Sources Retrieved:")
                for i, result in enumerate(search_output, 1):
                    print(f"{i}. {result['title']} ({result['source']})")
                    print(f"   URL: {result.get('url', 'No URL')}")
                executed_steps.add("search")
                print("[Tool Call Debug] search_web executed")

            # Step 3: Generate report
            print("-" * 80)
            if "report" not in executed_steps:
                print("Reporting...")
                report_result = Runner.run_streamed(orchestrator_agent, input=f"Generate a report for query '{query}' using these results:\n{json.dumps(search_output)}")
                report = ""
                async for event in report_result.stream_events():
                    if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                        delta = event.data.delta
                        if delta.strip():
                            print(f"[Report Stream] {delta}", end="", flush=True)
                            report += delta
                print()
                if not report or isinstance(report, dict) and "error" in report:
                    print("Report Error: No valid report generated")
                    report = (
                        f"# Fallback Report on {query}\n\n"
                        "## Introduction\n"
                        f"This report outlines available information on {query}, but no valid search results were found.\n\n"
                        "## Key Findings\n"
                        f"- Limited data available for {query} in 2025.\n"
                        "## Analysis\n"
                        "No credible sources were retrieved, possibly due to API limitations.\n"
                        "## Conclusion\n"
                        f"Further research is needed to provide updates on {query}.\n"
                    )
                print("Final Report:")
                print(report)
                executed_steps.add("report")
                print("[Tool Call Debug] generate_report executed")

            print("-" * 80)

        except Exception as e:
            print(f"Error processing query: {e}")
            print("Fallback: Generating basic plan...")
            plan = (
                f"1. Search for reputable tech news sources for {query}.\n"
                "2. Identify key developments in 2025.\n"
                "3. Validate with secondary sources like X posts.\n"
                "4. Prioritize information from 2025.\n"
            )
            print("Basic Plan:")
            print(plan)
            print("Final Report:")
            print(
                f"# Fallback Report on {query}\n\n"
                "## Introduction\n"
                f"This report outlines available information on {query}, but an error occurred.\n\n"
                "## Key Findings\n"
                f"- No data retrieved for {query} due to processing errors.\n"
                "## Analysis\n"
                "Errors in API or agent execution prevented data collection.\n"
                "## Conclusion\n"
                f"Retry with valid API keys or alternative sources for {query}.\n"
            )

if __name__ == "__main__":
    asyncio.run(main())
