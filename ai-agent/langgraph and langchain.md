## LangGraph

LangGraph is an advanced extension of LangChain that lets you build multi-step, stateful, branchable agents using a graph-based execution framework. Unlike standard LangChain chains or agents (which are mostly linear or reactive), LangGraph lets you model complex workflows as directed graphs (DAGs or state machines) with memory, control flow, and reasoning.

⸻

### 🧠 What Is LangGraph?

LangGraph = LangChain + State Machine (or DAG) + Memory

-	Nodes = steps (LLMs, tools, functions, etc.)
-	Edges = transitions between steps (can be conditional)
-	Memory = stores intermediate context and agent state
-	Loops/Branches = supported for recursive reasoning, retries, etc.

Think of LangGraph as a declarative agent planner or workflow engine for LLMs.

⸻

### 📦 Core LangGraph Modules

| Module               | Description                                               |
|----------------------|----------------------------------------------------------|
| LangGraph            | Main workflow runner using state machine logic           |
| StateGraph           | Define named nodes (steps) and transitions               |
| Node                 | Each function/tool/agent used as a graph step            |
| Memory               | Shared state passed between steps (dict-like)            |
| Multi-Modal Nodes    | Accepts images, PDFs, structured inputs                  |
| Conditional Branching| Transitions based on state or function output            |
| Loop Control         | Automatically loop until condition met                   |
| EndNode              | Graph exit point                                         |
| Parallel Execution   | Run multiple sub-nodes and merge results                 |
| SubGraphs            | Nest graphs as reusable components                       |


⸻

### 🏗️ Architecture Diagram


```text
User Input
   ↓
+-------------+
| Start Node  |  ←────────────┐
+-------------+               │
   ↓                          │
+-------------+     Loop      │
| Embedding   |──────────┐    │
+-------------+          │    │
   ↓                    ↓     │
+-------------+     +-------------+
| Retrieval   |     | Check Exit? |───→ Yes ──→ Output
+-------------+     +-------------+
                          ↓ No
                    +-------------+
                    | Rephrase    |
                    +-------------+
                          ↓
                   (goes back to Retrieval)

```


⸻

### ⚙️ Workflow Patterns


| Pattern             | Description                                              |
|---------------------|---------------------------------------------------------|
| Linear Chain        | Sequential steps, similar to classic LangChain flows    |
| DAG (Directed Acyclic Graph) | Branching and merging paths for complex logic         |
| Loop with Retry     | Repeat steps until a condition (e.g., confidence) is met|
| State Machine       | Track and transition between decision states             |
| Modular Graphs      | Use subgraphs as reusable workflow components            |
| Multi-agent Graph   | Assign specialized agents to different graph nodes       |



⸻

### 🚀 Application Example: Reviewer Matching Agent (LangGraph Version)

**Use case**: Given a paper abstract, find best reviewers using RAG + clustering + validation.

**Nodes**:

1.	InputParser: Parse paper into title + abstract
2.	EmbedQuery: Generate query embedding
3.	VectorSearch: Search author database using FAISS/Qdrant
4.	MetadataFilter: Filter by institution, domain, ORCID, etc.
5.	RerankWithLLM: Use LLM to rank authors by topic fit
6.	CheckConfidence: If confidence < 0.8 → rephrase query and loop
7.	ReturnTopMatches: Output JSON of top N authors

**Workflow**:

```text
graph TD
  A[Input Parser] --> B[Embed Query]
  B --> C[Vector Search]
  C --> D[Filter by Metadata]
  D --> E[LLM Reranker]
  E --> F{High Confidence?}
  F -->|Yes| G[Return Top Matches]
  F -->|No| H[Rephrase Query]
  H --> C
```

⸻

### 💡 Framework Compatibility

LangGraph integrates with:

-	LangChain modules: LLMs, tools, memory, retrievers, etc.
-	Pydantic or Dict-based state objects
-	FAISS / Qdrant / Pinecone for retrieval
-	Any LLM (OpenAI, Claude, etc.)
-	Memory Stores: ephemeral or persistent (e.g. Redis, SQLite)

⸻

### 🧱 Real-World Examples

| Use Case                | LangGraph Advantage                                         |
|-------------------------|------------------------------------------------------------|
| Research Assistant      | Enables iterative reasoning: search → cluster → summarize  |
| Grant Recommender Agent | Supports eligibility validation and dynamic reranking      |
| Auto Reviewer Picker    | Loops until optimal reviewers are identified               |
| Medical Q&A Agent       | Branches through symptom, condition, treatment, refinement |
| AI Tutor                | Detects knowledge gaps and retries with hints              |
| Paper Quality Evaluator | Combines RAG, metric checks, and explanation with retries  |


⸻

### 🧪 Example Output Schema

```json
{
  "input_paper": {
    "title": "...",
    "abstract": "..."
  },
  "top_reviewers": [
    {"name": "Dr. Alice Zhang", "score": 0.91, "orcid": "...", "institution": "..."},
    {"name": "Prof. John Doe", "score": 0.88, "orcid": "..."}
  ],
  "iterations": 2,
  "final_confidence": 0.92
}

```

---

## LangChain


LangChain is a powerful framework for building AI agents, chains, and applications that integrate large language models (LLMs) with tools, data, and memory. It provides a modular architecture to compose workflows using LLMs and external systems like vector stores, databases, APIs, and more.


### ✅ Correct Answer

LangChain is the core framework for large language model (LLM) application development, enabling developers to build end-to-end intelligent systems. It provides modular components and standardized interfaces to solve key engineering challenges:

⸻

### 🚀 What LangChain Does


| Category                   | Purpose                                                                                       |
|----------------------------|-----------------------------------------------------------------------------------------------|
| Engineering Development    | Standardizes workflows for data loading, model invocation, memory management, and tool usage  |
| Complex Task Orchestration | Enables multi-step automation using Chains and Agents                                         |
| Production-Grade Deployment| Supports distributed inference, dynamic batching, and vector retrieval for scalable systems   |

⸻


🧩 2. Core Modules (Developer Perspective)


| Module         | Function                                 | Key Classes / Interfaces                |
|----------------|------------------------------------------|-----------------------------------------|
| Model I/O      | Unifies input/output formats across models| `ChatOpenAI`, `HuggingFacePipeline`     |
| Data Connection| Handles data loading and vectorization    | `TextLoader`, `RecursiveTextSplitter`, `FAISS` |
| Chain          | Task orchestration and flow control       | `LLMChain`, `SequentialChain`           |
| Memory         | Manages conversation or workflow state    | `ConversationBufferMemory`, `RedisMemory`|
| Agents         | Dynamic tool invocation                   | `ReActAgent`, `Tool`                    |
| Callbacks      | Monitors training/inference               | `LangSmith`, `WandBIntegration`         |


**Developer Tips**

- **Model I/O** → Understand the effect of parameters like temperature, max_tokens, and top_p on generation quality
- **Data Connection** → Chunking strategy (overlap size, semantic segmentation) directly impacts RAG retrieval accuracy
- **Chain** → Learn LCEL syntax (| pipe operator) to chain multiple components concisely


⸻

### 💡 3. Core Concepts (Code-Level Understanding)


(1) Components and Chains

**Example: LCEL Chained Workflow**

```python
# --- Missing imports ---
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser

# --- LCEL-style chain ---
chain = (
    {"text": RunnablePassthrough()}
    | PromptTemplate.from_template("Summarize the text: {text}")
    | ChatOpenAI(model="gpt-4")
    | StrOutputParser()
)
```

**Key Point**:
All components implement the Runnable interface, allowing for plug-and-play composition of logic blocks.

⸻

(2) Prompt Templates

**Dynamic Prompt Example**

```python
# --- Missing imports ---
from langchain.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert {role}."),
    ("human", "{input}")
])
```

**Debugging Tip**:
Use LangSmith to trace how variables are injected into prompts and to visualize intermediate states.

⸻

(3) Vector Stores

**Building a Vector Database**

```python
# --- Missing imports ---
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

docs = TextLoader("data.txt").load()
splits = RecursiveTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(docs)
vectorstore = Chroma.from_documents(splits, OpenAIEmbeddings())
```

**Performance Tip**:
Use HNSW (Hierarchical Navigable Small World) indexing to accelerate similarity search.

⸻


### 🔗 Summary


| Layer         | Role                   | Example                        |
|---------------|------------------------|-------------------------------|
| Input / Output| Model abstraction      | `ChatOpenAI`, `HuggingFacePipeline` |
| Data          | Load, split, embed     | `TextLoader`, `FAISS`, `Chroma`     |
| Logic         | Flow orchestration     | `LLMChain`, `SequentialChain`, `LCEL` |
| Memory        | Context persistence    | `ConversationBufferMemory`           |
| Tools         | External interaction   | `ReActAgent`, `Tool`                |
| Observability | Debug / tracking       | `LangSmith`, `WandBIntegration`      |


⸻

### 🧱 Core LangChain Modules (v0.1+)

| Module            | Description                                                                                  |
|-------------------|----------------------------------------------------------------------------------------------|
| llms              | Interfaces to LLM providers (OpenAI, Anthropic, Cohere, etc.)                                |
| prompts           | Prompt templates for chat, messages, and structured inputs                                   |
| output_parsers    | Convert LLM outputs to structured formats (JSON, Pydantic, custom types)                     |
| chains            | Logic pipelines connecting LLMs, tools, and inputs/outputs                                   |
| agents            | Intelligent systems that plan and execute tool calls                                         |
| tools             | External tools usable by agents (APIs, code execution, databases)                            |
| retrievers        | Document retrievers (FAISS, Qdrant, BM25, etc.)                                              |
| memory            | Store intermediate conversation or task state (buffer, summary, vector memory)               |
| vectorstores      | Interfaces to vector databases (Pinecone, FAISS, Qdrant, Weaviate, etc.)                     |
| document_loaders  | Load documents from PDFs, URLs, Notion, databases, etc.                                      |
| text_splitters    | Break documents into chunks with overlap                                                     |
| embeddings        | Generate text embeddings via OpenAI, HuggingFace, etc.                                       |
| evaluation        | Tools to evaluate LLM outputs (criteria-based, GPT-assisted, etc.)                           |
| schema            | Core interface definitions (messages, tool calls, document objects)                          |
| experimental      | Cutting-edge modules (LangGraph, MultiModal, Function Agents, etc.)                          |


⸻

### 🏗️ Architecture Diagram

```text
+------------------+
|   User Query     |
+--------+---------+
         ↓
+--------v---------+          +---------------------+
|   PromptTemplate +--------->     LanguageModel    |
+--------+---------+          +---------------------+
         ↓                             ↓
+--------v---------+        +----------v-----------+
|     Chain / Agent +----->|   Tool / Retriever    |
+--------+---------+        +----------+-----------+
         ↓                             ↓
+--------v---------+        +----------v-----------+
|    OutputParser  +<------| Memory / VectorStore  |
+------------------+        +----------------------+

```

⸻

### ⚙️ Workflow Types

| Workflow Type         | Description / Use Case                                              |
|-----------------------|---------------------------------------------------------------------|
| Chain                 | Linear or branched steps (e.g., summarize → extract → respond)      |
| Agent                 | Dynamic planning; agent decides which tools to call at each step    |
| RAG                   | Retrieval-Augmented Generation; search docs/DBs to provide context  |
| Tool-Calling LLM      | LLM auto-selects and invokes tools (e.g., OpenAI function calling)  |
| LangGraph             | Stateful, graph-based flows (DAG/state machine; supports loops, memory, branching) |


⸻

### 📦 Example Applications

| Use Case              | Description                                                      |
|-----------------------|------------------------------------------------------------------|
| AI Research Assistant | Retrieve papers, summarize content, and build citation graphs    |
| Customer Support Bot  | Chatbot with RAG from documentation and integrated billing tools |
| Data QA Tool          | Query and validate data from SQL, CSV, or Excel sources          |
| Grant Recommender     | Match user profiles to relevant grants using vector search       |
| Codebase Q&A          | Load GitHub repositories, split and embed code, enable RAG       |
| Reviewer Matcher      | Embed papers, retrieve authors from FAISS/Qdrant, rank with LLM  |


⸻

### 🧩 Application: Reviewer Matcher Agent

LangChain Modules:

-	document_loaders: Load input paper (title + abstract)
-	embeddings: Encode paper
-	retrievers: Retrieve similar authors from FAISS
-	tools: Custom tool for filtering by ORCID, affiliation, topic
-	agents: LLM agent to select retrieval + reranking
-	memory: Store matching history per session
-	output_parsers: Return list of top N authors (JSON schema)

**Optional**:
-	LangGraph: Model multi-step review logic (filter → retrieve → rerank → explain)

⸻

### 🧠 Advanced Use: LangGraph for Agent Planning

LangGraph allows multi-step, loopable, dynamic agent workflows like:

```text
graph TD
  Start --> Normalize
  Normalize --> Retrieve
  Retrieve --> Rerank
  Rerank --> Decision{High confidence?}
  Decision -->|Yes| Finalize
  Decision -->|No| LLM_Resolve
  LLM_Resolve --> Finalize
```

⸻

### 🛠️ Framework Options

LangChain works with:

-	LLMs: OpenAI, Anthropic, Mistral, LLaMA2, etc.
-	Vector DBs: FAISS, Qdrant, Weaviate, Pinecone, etc.
-	Storage: SQLite, Redis, MongoDB
-	APIs: Wolfram, SERP, Web search, SQL, custom APIs






