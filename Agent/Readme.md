# 🚀 OpenAI Agents SDK with Multiple LLM Providers  

This repository demonstrates how to use the **OpenAI Agents SDK** with both **OpenAI** and **Non-OpenAI LLMs** (like **Groq, Gemini, Claude, DeepSeek, Moonshot**, etc.).  

The SDK is designed with two principles:  
- **Enough features to be worth using**, but **minimal primitives to learn fast**  
- **Works out of the box**, but highly **customizable for production**  

---

## ✨ Why Use OpenAI Agents SDK?  

- 🔁 **Agent Loop**: Built-in loop to call tools, send results to LLMs, and iterate until completion  
- 🐍 **Python-First**: Orchestrate and chain agents with native Python  
- 🤝 **Handoffs**: Coordinate tasks across multiple agents  
- ✅ **Guardrails**: Validate inputs/outputs with early breaks  
- 💬 **Sessions**: Automatic conversation history management  
- 🛠 **Function Tools**: Any Python function → Agent Tool (with schema validation)  
- 📊 **Tracing**: Debug, monitor, evaluate, and fine-tune workflows  

---

📊 Production Usage

- Use Guardrails to validate inputs/outputs
-Run multiple agents with handoffs for complex workflows
- Use Sessions to persist conversation history
- Enable Tracing for debugging and performance monitoring

## 📦 Installation  

```bash
# Create a project
mkdir my_project && cd my_project

# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows

# Install the SDK
pip install openai-agents

# Install dotenv for environment variables
pip install python-dotenv

🔐 Environment Setup

Create a .env file in the root of your project and add your LLM API keys.
You can use any provider (OpenAI, Groq, Gemini, Claude, DeepSeek, etc.):

OPENAI_API_KEY=your_openai_key_here
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here
CLAUDE_API_KEY=your_claude_key_here

🚦 Quickstart: Build Your First Agent

We’ll build a Personal Research Agent that updates you with trending news in tech, society, and opportunities.

Run the Agent
python personal_agent.py
