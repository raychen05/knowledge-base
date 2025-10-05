### AI Agent - Find Emerging Topic

To build an AI-powered research assistant agent that automates the discovery of emerging, well-funded, high-impact research topics (as described above), you’ll want a modular, intelligent system that:

-	Connects to Web of Science (WoS) and InCites
-	Extracts and interprets research trends, citation analytics, funding data
-	Uses LLMs to reason, explain, and summarize findings
-	Helps researchers avoid manual search and quickly surface actionable insights

---


### ✅ High-Level Agent Architecture


```plaintext
[User]
   │
   ▼
[Frontend Chat UI or API]
   │
   ▼
[Agent Orchestrator]
   ├──→ [LLM (e.g., GPT-4)] for prompt understanding, summarization
   ├──→ [Search API Wrapper: Web of Science, InCites]
   ├──→ [Trend Analyzer] (publications, citations, funding patterns)
   └──→ [Memory + Cache] for ongoing sessions and topic summaries
```

---

### 🧱 Core Modules & Responsibilities

#### 1. 🧠 LLM Interpreter Layer

-	Interprets user query: “What are the hottest topics in AI funding?”
-	Decides what tool to invoke (search, analyze, summarize)
-	Summarizes results for user

💡 Use:
-	LangChain or custom orchestration
-	GPT-4 or Claude for intelligent reasoning

---

#### 2. 🔍 Search Connector Layer

Interfaces with:
-	Web of Science API (search by topic, keywords, filters)
-	InCites API (if accessible; if not, scrape or mirror with proxy API)

📥 Input:
-	Structured topic query (from user or LLM)

📤 Output:
-	Recent articles, citation data, funders, keywords, etc.

#### 3. 📊 Analytics Engine (Trend Analyzer)

Analyzes search results:
-	Publication trends (by year, field)
-	Citation growth (hotness proxy)
-	Top funders + funding text
-	Keyword co-occurrence
-	Institutional contributors

📈 Use:
-	Python (Pandas, SciPy)
-	VOSviewer for clustering (optional)
-	Plotly for interactive visuals (optional)

---

#### 4. 🧠 LLM Summarization Layer

Turns analytics into a narrative:

“In the last 3 years, the subfield ‘graph neural networks’ has seen a 220% increase in publications. It is heavily funded by NSF and NIH, and dominated by institutions such as MIT and Stanford.”

📌 Use:
-	GPT-4 to summarize JSON results from analytics module
-	Templates for different response formats (bullets, paragraph, charts)

---

#### 5. 🗂 Context & Memory

-	Keeps track of past queries
-	Caches summaries of topics already searched
-	Helps support follow-ups like “Which of these has less competition?”

🧠 Use:
-	Redis or SQLite for small-scale
-	PostgreSQL with JSON fields for structured metadata

---


### 🔧 Example Prompt + Workflow

🗣 User:

“What are the most funded and trending topics in cancer genomics in the last 3 years?”

🧠 Agent Actions:

1.	LLM parses: main topic = “cancer genomics”, timeframe = “last 3 years”
2.	Web of Science API: fetch recent publications
3.	Analyze:
    -	Top keywords
    -	Funding agencies
    -	Citations per year
4.	LLM summarizes results and recommends top 3 emerging subfields

---

### 🛠️ Tools & Technologies


| Component            | Tech Stack                                         |
|----------------------|----------------------------------------------------|
| Agent Core           | LangChain / Custom Python                          |
| LLM                  | OpenAI GPT-4 / Claude                              |
| Search Access        | Web of Science API, InCites API (or scraping)      |
| Trend Analysis       | Python (Pandas, SciPy, matplotlib)                 |
| Memory Store         | Redis / PostgreSQL                                 |
| Frontend             | Streamlit, React, or Flask UI                      |
| Vector Search (opt.) | FAISS or Weaviate (for topic embeddings)           |


✅ Output Example (Agent Response)

Top Emerging Topics in Cancer Genomics (2021–2024):

1.	Single-cell RNA sequencing
    -	📈 Publication Growth: +310%
    -	💰 Top Funders: NIH, CRUK
    -	🧠 Top Institutions: Broad Institute, UCSF

2.	CRISPR-based genome editing
    -	📈 +190%
    -	💰 DARPA, Wellcome Trust

These topics show fast growth and strong funding signals, suggesting good potential for impactful research.

---

### 🧠 Bonus Enhancements

-	Voice input & mobile UI for quick access
-	Email report or PDF export of findings
-	Funding opportunity recommendations via NSF/NIH scraping
-	Collaboration suggestions via co-authorship analysis

---

🚀 Want a Starter Template or GitHub Repo?

I can generate:
-	LangChain agent starter (WoS query → trend analysis → LLM summary)
-	Scripts to simulate WoS/InCites queries (if no API access)
-	Interactive Streamlit UI



