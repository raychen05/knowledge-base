## Starter Template for Building an Agentic AI System


Here's a starter template for building an Agentic AI system that:

- Reads Web of Science papers
- Tracks research trends (by topic, region, funder, institution)
- Writes automated reports with citations

We'll use:

- ✅ LangGraph – for agent state control
- ✅ LangChain – for tools, memory, and LLM interface
- ✅ LlamaIndex – for RAG (retrieval from indexed research documents)
- ✅ OpenAI GPT-4 / Claude 3 – for planning, reasoning, and summarization



📦 Requirements

```bash
pip install langgraph langchain llama-index openai

```


🧱 Folder Structure


```graphsql
research_analyst_agent/
├── wos_docs/                       # Folder with academic text chunks or PDFs
├── agent.py                        # Main logic
├── components/
│   ├── retriever.py                # RAG retrieval from LlamaIndex
│   ├── reporter.py                 # Research trend summarizer
│   └── planner.py                  # Task planner agent
```


📂 components/retriever.py

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

def get_retriever():
    docs = SimpleDirectoryReader("wos_docs").load_data()
    index = VectorStoreIndex.from_documents(docs)
    return index.as_retriever(similarity_top_k=5)

```


📂 components/reporter.py

```python
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(model="gpt-4", temperature=0.3)

def write_summary(context, topic, region):
    prompt = f"""
You are a research analyst. Summarize recent trends in "{topic}" in "{region}" based on the following documents:

{context}

Write 3 paragraphs with citations. Be concise and objective.
"""
    return llm.invoke(prompt)

```


📂 components/planner.py

```python

from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(model="gpt-4")

def plan_research_tasks(query: str):
    prompt = f"""
Given the user query: "{query}", break it down into sub-tasks.

Output format (JSON):
[
  {{ "step": 1, "task": "...", "target": "...", "topic": "...", "region": "..."}},
  ...
]
"""
    return llm.invoke(prompt)
```

🧠 agent.py (LangGraph-powered Agentic Workflow)


```python
from langgraph.graph import StateGraph
from components.retriever import get_retriever
from components.reporter import write_summary
from components.planner import plan_research_tasks

retriever = get_retriever()

def retrieve_and_summarize(state):
    step = state["plan"][state["current_step"]]
    context = retriever.retrieve(f"{step['topic']} in {step['region']}")
    summary = write_summary("\n".join([d.text for d in context]), step['topic'], step['region'])
    return {
        **state,
        "summaries": state["summaries"] + [summary],
        "current_step": state["current_step"] + 1
    }

def check_done(state):
    return state["current_step"] >= len(state["plan"])

def build_agent():
    graph = StateGraph()

    graph.add_node("summarize_step", retrieve_and_summarize)
    graph.set_entry_point("summarize_step")

    graph.add_conditional_edges(
        "summarize_step",
        check_done,
        if_true="end",
        if_false="summarize_step"
    )

    return graph.compile()

def run_agent(user_query):
    plan_json = plan_research_tasks(user_query)
    plan = eval(plan_json.content) if hasattr(plan_json, 'content') else eval(plan_json)
    workflow = build_agent()
    final_state = workflow.invoke({
        "plan": plan,
        "summaries": [],
        "current_step": 0
    })
    return final_state["summaries"]

```


🧪 Usage Example


```python
if __name__ == "__main__":
    user_query = "Write a report on renewable energy research trends in Germany and China over the past 5 years."
    summaries = run_agent(user_query)

    print("\n\n🔍 Final Research Summary Report:\n")
    for i, section in enumerate(summaries):
        print(f"\n### Section {i+1}\n{section}\n")

```


🧠 What This Agent Can Do

- 🧩 Plan: Break down queries into per-topic/region tasks
- 🔍 Retrieve: Search relevant documents from academic corpus
- ✍️ Generate: Write multi-part research report with citations
- 🔁 Loop: Steps through tasks one-by-one, with memory


✅ Extension Ideas


| Feature                          | How to Add                                                           |
|----------------------------------|----------------------------------------------------------------------|
| Export to PDF / DOCX             | Use `python-docx` or `WeasyPrint`                                   |
| Include charts (e.g., funding trend) | Integrate with `matplotlib` + citation count over time             |
| Agent memory of past reports     | Use LangChain `ConversationBufferMemory`                            |
| Multi-agent support              | Add `CrewAI` or `AutoGen` for planner, summarizer, and reviewer roles |
| Web of Science API integration   | Call WOS REST APIs for live metadata                                |
