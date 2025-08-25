import os 
import asyncio

from agents import (
    Agent, Runner, AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_default_openai_client, set_tracing_disabled
)
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Disable tracing (optional)
set_tracing_disabled(disabled=True)

# Retrieve API Key
groq_api_key   = os.getenv("GROQ_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
if not groq_api_key:
    raise ValueError("Please enter API Key of LLM in .env")

# Initialize Provider (Groq as example)
external_client = AsyncOpenAI(
    api_key= groq_api_key,
    base_url= "https://api.groq.com/openai/v1"
)

# Set default OpenAI Client
set_default_openai_client(client=external_client, use_for_tracing=False)

# Configure Model
model = OpenAIChatCompletionsModel(
    openai_client= external_client,
    model= "moonshotai/kimi-k2-instruct"  # Replace with your LLM model
)

# Main Function
async def main():
    agent = Agent(
        name="Personal Agent",
        instructions="You are an expert research assistant. Update me about trending tech, social, and opportunity-related news.",
        model=model
    )

    result = await Runner.run(agent, "Tell me about the latest AI trends.")
    print("\nCALLING AGENT...\n")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
