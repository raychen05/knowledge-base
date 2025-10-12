## Adaptive RAG (Retrieval-Augmented Generation)


It  is a retrieval-augmented generation method where the retrieval strategy dynamically adapts based on the user’s query, context, task, or even intermediate results in multi-step reasoning.


In contrast to static RAG (e.g., a fixed query to a vector DB), adaptive RAG can:

- Choose different retrievers (vector vs. keyword search)
- Modify the query formulation (e.g., reformulate based on question type)
- Adjust retrieval depth (e.g., how many documents to retrieve)
- Chain multiple retrievals (multi-hop or multi-turn)
- Use retrieved content to refine the next retrieval (feedback loop)

---

### 🔧 Example Use Case: Research Assistant

**Goal**: Answer “What is the current state of research on using AI in medical imaging for cancer diagnosis?”

---

### Step-by-Step Adaptive RAG Flow:

1.	Query Understanding & Classification
  - Detects that the user is asking a literature review type of question.
  - Adapts retrieval to use Web of Science + semantic search + recent filters (e.g., last 3 years).

2.	Query Reformulation
  - Reformulates into: "Recent research on AI methods in medical imaging for cancer detection" for retrieval.

3.	Adaptive Retrieval (Multi-Retriever Strategy)
  - Uses:
    - Vector search over a paper embeddings index.
    - Keyword search over abstracts.
    - Citation-based expansion (find high-impact papers).
  - Retrieves:
    - Top 5 seminal papers
    - Top 5 recent high-cited papers
    - 5 systematic reviews

4.	LLM Synthesizes Results
  - Organizes results into themes: deep learning, multimodal imaging, challenges.

5.	Gaps Noticed ➝ Trigger Secondary Retrieval
  - LLM notices “lack of explanation about regulatory barriers”.
  - Triggers follow-up query to legal literature or policy documents.
	
6.	Final Output
  - Returns: a structured summary with citations, timeline of methods, and knowledge gaps.

---

### 💡 Key Characteristics of Adaptive RAG

| Feature             | Static RAG                       | Adaptive RAG                                         |
|---------------------|----------------------------------|------------------------------------------------------|
| Query               | Fixed by user                    | Reformulated intelligently based on context/task      |
| Retriever           | Single (e.g., vector DB)         | Dynamically selects: vector, keyword, graph-based     |
| Retrieval Depth     | Fixed (e.g., top-5)              | Expands or contracts based on need                    |
| Multi-hop Reasoning | Not supported                    | Supported (chains multiple retrievals)                |
| Feedback Loops      | No                               | Yes (uses intermediate results to refine retrieval)   |
| Domain Awareness    | Generic                          | Task/domain-specific strategies                       |


---

### 🔄 Tools to Build Adaptive RAG

- LangChain / LangGraph: Chain-of-thought + adaptive routing
- LlamaIndex: Hybrid retrievers, query transformers
- RAGAS: Evaluate and improve RAG pipeline adaptively
- FAISS + Elasticsearch hybrid search
- LLM Agent layer: Makes retrieval decisions based on task

Great. Below is a LangGraph-based Adaptive RAG agent that:

- Classifies the query type (e.g., fact lookup vs. literature review vs. analysis)
- Reformulates the query
- Chooses the appropriate retriever (e.g., vector DB vs. keyword search)
- Retrieves adaptively
- Performs multi-hop if needed
- Synthesizes the response with citations

---

### 🧠 Goal: Adaptive RAG for Research Assistant

We’ll use:

- LangGraph for routing and stateful control
- LangChain retrievers (FAISS for semantic, BM25 for keyword)
- OpenAI GPT-4 or similar for planning, generation
- LlamaIndex or Elasticsearch (optional backend)

---

### 🧱 Structure Overview

```text
graph TD
    Start --> ClassifyQuery
    ClassifyQuery -->|fact| SimpleRetrieval
    ClassifyQuery -->|review| Reformulate
    Reformulate --> ChooseRetriever
    ChooseRetriever --> RetrieveDocs
    RetrieveDocs --> AnalyzeNeedMore
    AnalyzeNeedMore -->|yes| FollowupRetrieval
    AnalyzeNeedMore -->|no| GenerateAnswer
    FollowupRetrieval --> GenerateAnswer
```

---

### 🧑‍💻 LangGraph Code (Simplified)


```python
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.retrievers import BM25Retriever, VectorStoreRetriever
from langchain.schema.runnable import RunnableLambda
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

# Set up retrievers
vector_retriever = VectorStoreRetriever(vectorstore=FAISS.load_local("faiss_index", OpenAIEmbeddings()))
keyword_retriever = BM25Retriever.from_documents(docs)

# State: user query + intermediate results
class State(dict): pass

# 1. Classify query type
def classify_query(state: State):
    query = state["query"]
    # Use GPT to classify the type
    llm = ChatOpenAI()
    result = llm.invoke(f"What type of query is this? (fact / review / opinion): {query}")
    return {"query_type": result.content.strip().lower()}

# 2. Reformulate if complex
def reformulate_query(state: State):
    llm = ChatOpenAI()
    query = state["query"]
    reformulated = llm.invoke(f"Reformulate this research query for better retrieval: {query}")
    return {"reformulated_query": reformulated.content}

# 3. Choose retriever
def choose_retriever(state: State):
    query_type = state["query_type"]
    retriever = keyword_retriever if query_type == "fact" else vector_retriever
    return {"retriever": retriever}

# 4. Retrieve
def retrieve_documents(state: State):
    retriever = state["retriever"]
    query = state.get("reformulated_query", state["query"])
    docs = retriever.get_relevant_documents(query)
    return {"documents": docs}

# 5. Analyze if need follow-up
def analyze_need_more(state: State):
    llm = ChatOpenAI()
    context = "\n\n".join([d.page_content for d in state["documents"]])
    result = llm.invoke(f"Does this answer the question: '{state['query']}'?\n\nContext:\n{context}\n\nAnswer 'yes' or 'no'")
    return "FollowupRetrieval" if "no" in result.content.lower() else "GenerateAnswer"

# 6. Generate final answer
def generate_answer(state: State):
    llm = ChatOpenAI()
    context = "\n\n".join([d.page_content for d in state["documents"]])
    result = llm.invoke(f"Using the context below, answer the question: '{state['query']}'\n\nContext:\n{context}")
    return {"final_answer": result.content}

# Build the graph
builder = StateGraph(State)
builder.add_node("ClassifyQuery", classify_query)
builder.add_node("Reformulate", reformulate_query)
builder.add_node("ChooseRetriever", choose_retriever)
builder.add_node("RetrieveDocs", retrieve_documents)
builder.add_node("AnalyzeNeedMore", analyze_need_more)
builder.add_node("GenerateAnswer", generate_answer)
builder.add_node("FollowupRetrieval", retrieve_documents)  # Re-use retrieval for follow-up

# Edges
builder.set_entry_point("ClassifyQuery")
builder.add_edge("ClassifyQuery", "Reformulate")
builder.add_edge("Reformulate", "ChooseRetriever")
builder.add_edge("ChooseRetriever", "RetrieveDocs")
builder.add_edge("RetrieveDocs", "AnalyzeNeedMore")
builder.add_conditional_edges("AnalyzeNeedMore", {
    "FollowupRetrieval": "FollowupRetrieval",
    "GenerateAnswer": "GenerateAnswer",
})
builder.add_edge("FollowupRetrieval", "GenerateAnswer")
builder.set_finish_point("GenerateAnswer")

graph = builder.compile()

```

---


### 🧪 Example Call


```python
response = graph.invoke({"query": "What are recent advances in AI for lung cancer detection using CT scans?"})
print(response["final_answer"])
```


✅ Result

A well-structured, citation-backed answer, adaptively retrieved and synthesized.

---

### 🧩 Variations

You can plug in:

- LlamaIndex query transformers to reformulate queries
- HybridRetriever (combine BM25 + FAISS)
- LangGraph memory to store previous retrievals
- InCites, Web of Science, PubMed APIs for real-time retrieval


---

## A Full Working Repo  for Adaptive RAG Agent

Great — here’s an outline of the full working repo you’ll get for an Adaptive RAG Agent using LangGraph:


### 🗂️ Repo Structure

```text
adaptive-rag-agent/
│
├── README.md
├── requirements.txt
│
├── data/
│   └── sample_docs.json              # Sample documents to index
│
├── retrievers/
│   ├── build_faiss_index.py          # Build FAISS from documents
│   └── load_bm25_retriever.py        # Load BM25 from docs
│
├── graph/
│   ├── adaptive_rag_graph.py         # LangGraph pipeline
│   ├── nodes.py                      # All nodes (LLM classify, retrieve, generate)
│   └── run_graph.py                  # Simple CLI or script runner
│
├── utils/
│   └── prompts.py                    # Prompt templates
└── config.py                         # Central config (model, paths)
```

---


### ✅ Features

- FAISS-based vector search using OpenAI embeddings
- BM25 keyword search using langchain.retrievers
- LLM query classification (fact vs review vs analysis)
- LLM query reformulation
- Multi-step retrieval (follow-up queries)
- LLM synthesis of final answer with citations
- LangGraph-based control flow

---

### 🧪 Sample Usage

```bash
python run_graph.py \
  --query "What are the latest deep learning techniques for early breast cancer detection using mammography?"
```

It will:

- Classify as a “literature review”
- Reformulate the query
- Choose FAISS for vector semantic search
- Retrieve relevant papers
- Detect if more info is needed
- Retrieve again if needed
- Generate the answer

---

### 🔧 Setup

**requirements.txt**

```text
langchain>=0.1.14
langgraph>=0.0.35
faiss-cpu
tqdm
openai
python-dotenv
```

**Sample Doc Format**

```json
[
  {
    "title": "Deep learning in mammography: A review",
    "abstract": "This paper reviews convolutional neural networks for detecting breast cancer...",
    "content": "Full content here...",
    "source": "PubMed",
    "year": 2023
  },
  ...
]
```



---



## A Full Working Code for the Adaptive RAG Agent



Great — below is the full working code for the Adaptive RAG Agent using LangGraph.

We’ll go step by step by filling each file in the repo you just created.

---

### ✅ 1. retrievers/build_faiss_index.py

Builds a FAISS index from documents.

```python
# retrievers/build_faiss_index.py

import json
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from config import VECTOR_INDEX_PATH, DOCS_PATH

def build_faiss_index():
    with open(DOCS_PATH, "r") as f:
        docs_raw = json.load(f)
    
    documents = [
        Document(
            page_content=doc["abstract"] or doc["content"],
            metadata={"title": doc["title"], "source": doc["source"], "year": doc["year"]}
        )
        for doc in docs_raw
    ]
    
    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(documents, embeddings)
    db.save_local(VECTOR_INDEX_PATH)
    print(f"FAISS index saved to {VECTOR_INDEX_PATH}")

if __name__ == "__main__":
    build_faiss_index()
```

---

### ✅ 2. retrievers/load_bm25_retriever.py

Loads a BM25 retriever from the same documents.

```python
# retrievers/load_bm25_retriever.py

import json
from langchain.retrievers import BM25Retriever
from langchain.schema import Document
from config import DOCS_PATH

def load_bm25_retriever():
    with open(DOCS_PATH, "r") as f:
        docs_raw = json.load(f)

    documents = [
        Document(
            page_content=doc["abstract"] or doc["content"],
            metadata={"title": doc["title"], "source": doc["source"], "year": doc["year"]}
        )
        for doc in docs_raw
    ]
    
    retriever = BM25Retriever.from_documents(documents)
    retriever.k = 5
    return retriever
```

---


### ✅ 3. utils/prompts.py

Prompt templates for query classification and generation

```python
# utils/prompts.py

classify_prompt = """
Classify this query into one of: [fact, review, opinion].

Query: "{query}"
Answer:"""

reformulate_prompt = """
Reformulate this research query to make it more effective for academic search engines:

Original: "{query}"
Rewritten:"""

generate_prompt = """
Use the following documents to answer the research question.

Question: {query}

Documents:
{context}

Answer:"""
```

---

### ✅ 4. graph/nodes.py

LangGraph nodes for classification, reformulation, retrieval, generation.

```python
# graph/nodes.py

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.vectorstores import FAISS
from langchain.retrievers import VectorStoreRetriever
from langchain.schema import Document
from config import VECTOR_INDEX_PATH
from retrievers.load_bm25_retriever import load_bm25_retriever
from utils.prompts import classify_prompt, reformulate_prompt, generate_prompt

llm = ChatOpenAI(model="gpt-4", temperature=0)

def classify_query(state):
    prompt = PromptTemplate.from_template(classify_prompt)
    chain = LLMChain(llm=llm, prompt=prompt)
    result = chain.run(query=state["query"]).strip().lower()
    return {"query_type": result}

def reformulate_query(state):
    prompt = PromptTemplate.from_template(reformulate_prompt)
    chain = LLMChain(llm=llm, prompt=prompt)
    rewritten = chain.run(query=state["query"]).strip()
    return {"reformulated_query": rewritten}

def choose_retriever(state):
    if state["query_type"] == "fact":
        retriever = load_bm25_retriever()
    else:
        db = FAISS.load_local(VECTOR_INDEX_PATH, embeddings=llm.embed_query)
        retriever = VectorStoreRetriever(vectorstore=db)
    return {"retriever": retriever}

def retrieve_documents(state):
    retriever = state["retriever"]
    query = state.get("reformulated_query", state["query"])
    docs = retriever.get_relevant_documents(query)
    return {"documents": docs}

def analyze_need_more(state):
    docs = state["documents"]
    if len(docs) < 3:
        return "FollowupRetrieval"
    return "GenerateAnswer"

def generate_answer(state):
    docs = state["documents"]
    context = "\n\n".join([f"{d.metadata['title']}: {d.page_content}" for d in docs])
    prompt = PromptTemplate.from_template(generate_prompt)
    chain = LLMChain(llm=llm, prompt=prompt)
    answer = chain.run(query=state["query"], context=context)
    return {"final_answer": answer.strip()}
```

---

### ✅ 5. graph/adaptive_rag_graph.py

LangGraph flow definition.

```python
# graph/adaptive_rag_graph.py

from langgraph.graph import StateGraph
from graph.nodes import (
    classify_query,
    reformulate_query,
    choose_retriever,
    retrieve_documents,
    analyze_need_more,
    generate_answer,
)

class State(dict): pass

def build_graph():
    builder = StateGraph(State)

    builder.add_node("ClassifyQuery", classify_query)
    builder.add_node("Reformulate", reformulate_query)
    builder.add_node("ChooseRetriever", choose_retriever)
    builder.add_node("RetrieveDocs", retrieve_documents)
    builder.add_node("AnalyzeNeedMore", analyze_need_more)
    builder.add_node("GenerateAnswer", generate_answer)
    builder.add_node("FollowupRetrieval", retrieve_documents)

    builder.set_entry_point("ClassifyQuery")
    builder.add_edge("ClassifyQuery", "Reformulate")
    builder.add_edge("Reformulate", "ChooseRetriever")
    builder.add_edge("ChooseRetriever", "RetrieveDocs")
    builder.add_edge("RetrieveDocs", "AnalyzeNeedMore")
    builder.add_conditional_edges("AnalyzeNeedMore", {
        "FollowupRetrieval": "FollowupRetrieval",
        "GenerateAnswer": "GenerateAnswer",
    })
    builder.add_edge("FollowupRetrieval", "GenerateAnswer")
    builder.set_finish_point("GenerateAnswer")

    return builder.compile()
```

---

### ✅ 6. graph/run_graph.py

CLI entry point.

```python
# graph/run_graph.py

import argparse
from graph.adaptive_rag_graph import build_graph

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, required=True)
    args = parser.parse_args()

    graph = build_graph()
    result = graph.invoke({"query": args.query})
    print("\n🧠 Final Answer:\n", result["final_answer"])

if __name__ == "__main__":
    main()

```