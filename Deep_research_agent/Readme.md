# 🔎 Multi-Agent Hybrid Research System

This project implements a **multi-agent research framework** that plans, searches, and synthesizes information into professional reports. Inspired by human research workflows, the system uses a **plan → search → analyze → report** pipeline instead of simple Q&A.

---

## ✨ Key Features

- **Planning Agent** → Decomposes queries into actionable research steps.  
- **Web Search Agent** → Executes hybrid searches across **Tavily** and **SerpAPI**, deduplicates results, and validates credibility.  
- **Reporting Agent** → Produces concise, well-structured reports in Markdown with findings, analysis, and citations.  
- **Orchestrator Agent** → Coordinates all steps, ensures ordered execution, and provides debug streams (`[Plan Stream]`, `[Search Stream]`, `[Report Stream]`).  
- **Hybrid Search Strategy** → Combines semantic search (Tavily) with broad web coverage (SerpAPI), ensuring resilience and source diversity.  

---

## ⚙️ How It Works

1. **User Query** → Provide a natural-language question (e.g., *“Give me updates in the world of tech?”*).  
2. **Plan Generation** → Planning Agent outputs a structured research plan.  
3. **Hybrid Search** → Tavily and SerpAPI APIs retrieve top results with metadata (title, description, URL, source, icon).  
4. **Report Generation** → Reporting Agent synthesizes findings into a professional, 150–200 word Markdown report.  
5. **Orchestration** → All agents are coordinated in sequence, preventing repetition and ensuring traceability.  

---

## 📊 Example Run

```bash
(Agents) PS C:\Users\PMYLS\Desktop\OpenAI SDK\Agents> uv run research_agent.py
Sample Output (Query: "Give me updates in the world of tech?")
markdown
Copy code
Processing Query: Give me updates in the world of tech?
Planning...
[Plan Stream] Planning...

Research Plan:
1. Search "major tech news 2025," "tech industry trends 2025," and "CES 2025 announcements" using reputable tech news outlets.
2. Identify significant product launches, AI advancements, policy changes, and major company acquisitions or partnerships reported for 2025.
3. Extract specific details such as dates, companies involved, and reported impacts from official company press releases and reputable financial news sources.
4. Validate and broaden context using specialist tech blogs, industry analyst reports, and discussions on professional tech forums or X (Twitter) for 2025 updates.

Searching...
[Tavily Debug] Retrieved 5 results
[SerpAPI Debug] Retrieved 5 results

Sources Retrieved:
1. 25 New Technology Trends for 2025 - Simplilearn  
   https://www.simplilearn.com/top-technology-trends-and-jobs-article
2. Gartner's Top 10 Strategic Technology Trends 2025  
   https://www.gartner.com/en/articles/top-technology-trends-2025
3. Top 10 Technology Trends For 2025 - Forbes  
   https://www.forbes.com/councils/forbestechcouncil/2025/02/03/top-10-technology-trends-for-2025/
4. Top 10 in Tech – May 2025 - Digitopia  
   https://digitopia.co/blog/top-10-in-tech-may-2025/
5. McKinsey Technology Trends Outlook 2025  
   https://www.mckinsey.com/capabilities/mckinsey-digital/our-insights/the-top-trends-in-tech

Reporting...
[Report Stream]

Final Report:
This report synthesizes information regarding technology trends in 2025, providing an overview of market growth and key advancements.

### Key Findings
* **Agentic AI** emerges as a dominant trend, enabling autonomous agents for enterprise tasks.  
* Major AI milestones include universal deepfake detection (98% accuracy) and launch of Malaysia’s AI-powered Ryt Bank.  
* Broader trends include AR, post-quantum cryptography, spatial computing, disinformation security, and polyfunctional robots.  
* Infrastructure advances include Broadcom’s next-gen AI chips and nuclear-powered data centers.  
* Events such as the Qatar Economic Forum 2025 highlighted AI, blockchain, and sustainable technologies.  

### Analysis
The retrieved sources consistently identify **Artificial Intelligence** as the central driver of technological change in 2025. While most findings are well-sourced (e.g., Gartner, Forbes, McKinsey), some aggregated data lacks direct citation, warranting further validation.

### Conclusion
The 2025 tech landscape is marked by pervasive AI adoption, critical infrastructure shifts, and expanding applications of emerging technologies, signaling a year of rapid innovation and integration.

### Citations
1. [Simplilearn – 25 New Technology Trends 2025](https://www.simplilearn.com/top-technology-trends-and-jobs-article)  
2. [Gartner – Top 10 Strategic Technology Trends 2025](https://www.gartner.com/en/articles/top-technology-trends-2025)  
3. [Forbes – Top 10 Technology Trends 2025](https://www.forbes.com/councils/forbestechcouncil/2025/02/03/top-10-technology-trends-for-2025/)  
4. [Digitopia – Top 10 in Tech May 2025](https://digitopia.co/blog/top-10-in-tech-may-2025/)  
5. [McKinsey – Technology Trends Outlook 2025](https://www.mckinsey.com/capabilities/mckinsey-digital/our-insights/the-top-trends-in-tech)
🚀 Why This Matters
Transparency → Every stage (plan, search, report) is visible and debuggable.

Reliability → Reduces hallucinations via source-backed synthesis.

Recency → Prioritizes 2025 results and trusted outlets.

Flexibility → Handles vague or broad queries with fallback strategies.

Professional Output → Markdown reports are concise, citable, and ready for use in briefs or research docs.

🛠️ Setup
Clone this repo

Install dependencies:

bash
Copy code
uv pip install -r requirements.txt
Add your API keys for Tavily and SerpAPI.

Run with:

bash
Copy code
uv run research_agent.py
```
## ✨ Key Features

1. Expand hybrid search with domain-specific APIs (finance, medical, scientific).
2. Improve citation granularity with per-claim source mapping.
3. Add streaming output with live report drafting.
4. Extend agent memory for multi-turn research sessions.
