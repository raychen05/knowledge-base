## Academic Impact Analysis Agent 


Designing an Academic Impact Analysis Agent powered by LLMs involves integrating structured research data (e.g., Web of Science, InCites, Scopus, OpenAlex, etc.) with intelligent reasoning and synthesis capabilities provided by large language models. Below is a comprehensive feature set categorized by use case, powered or enhanced by LLMs:

---

### 🧠 Top Features for Academic Impact Analysis Agent (Powered by LLM)

🔬 1. Research Impact Assessment

- 	Impact Score Explanation: Interpret InCites/JCR/WoS metrics (e.g., CNCI, JIF) in natural language.
- 	Citation Quality Analysis: Distinguish between self-citations, high-impact vs. low-impact citations.
- 	Field-Normalized Comparison: Compare author/paper metrics against field norms using natural language generation.
- 	Temporal Impact Trend: Explain growth, peak, or decline in citations and publication frequency.

---

🏆 2. Author/Institution Ranking & Benchmarking

- 	Strengths & Weaknesses Summary: Summarize an author’s research focus, strengths, and underexplored areas.
- 	Institutional Contribution Mapping: Map top institutions by research output/impact in a domain.
- 	Collaboration Strength Analysis: Analyze the effectiveness and reach of co-authorships or international collaborations.

---

🧾 3. Grant and Funding Impact Analysis

- 	Funding-to-Impact Attribution: Attribute research output/citations to specific grants using metadata linking and synthesis.
- 	ROI Summarization: Generate textual reports summarizing the return on investment (publications, impact) of a funder.
- 	Funder Comparison: Generate comparative summaries (e.g., NIH vs. NSF vs. EU Horizon).

---

🔍 4. Publication Quality & Novelty Assessment

- 	Research Novelty Detection: Compare abstract/content with prior work to assess novelty or originality.
- 	Trend vs. Innovation: Classify papers as trend-following vs. innovative using topic modeling + LLMs.
- 	Journal Fit & Quality Check: Evaluate whether a paper fits the journal’s scope and impact tier.

---

🧑‍🔬 5. Expert & Reviewer Discovery

- 	Expert Justification Summaries: When recommending reviewers, explain their relevance (e.g., “Dr. X has published 12 papers on topic Y in the last 5 years”).
- 	Conflict Detection: Identify conflicts of interest from coauthorship, institutions, or grants.
- 	Reviewer Diversity Analysis: Assess and summarize diversity (gender, geography, topic coverage).

---

🕸️ 6. Citation Network Reasoning

- 	Citation Chain Narration: Trace and explain the influence path across a citation network.
- 	Key Paper Identification: Summarize the most central papers in a citation graph with reasons.
- 	Influence Clusters: Identify and describe influential clusters of research or schools of thought.

---

📚 7. Topic & Research Area Evolution

- 	Emerging Topic Detection: Identify rising topics via trend analysis and describe in plain language.
- 	Topic Drift Summary: Explain how an author or journal’s research focus has changed over time.
- 	Taxonomy Synthesis: Auto-generate a hierarchical topic structure from large corpora.

---

📈 8. Multi-Dimensional Report Generation

- 	Narrative Reports: Auto-generate executive summaries for departments, researchers, institutions.
- 	Comparative Dashboards: Textual comparison of multiple entities across impact metrics and topics.
- 	Custom Impact Storytelling: Generate “impact stories” for use in grant applications, tenure cases, or funding justifications.

---

🛠️ 9. Data Cleaning & Metadata Normalization

- 	Affiliation Normalization: LLM-assisted name disambiguation and canonicalization for institutions and authors.
- 	Missing Metadata Filling: Predict and fill missing grant numbers, author roles, countries using context.
- 	Name Disambiguation: Resolve ambiguous author names using embeddings + LLM reasoning.

---

💬 10. Conversational Analytics Agent

- 	Natural Language Queries: Support questions like:
- 	“What is the most cited paper by Dr. Smith in machine learning?”
- 	“Has the University of Toronto’s AI research impact increased over the past 5 years?”
- 	Interactive Drill-Down: Step-by-step exploration (“Tell me more about their coauthors in China”).
- 	Explanatory Dialogue: Explain complex metrics (“What does CNCI 1.5 mean?”).

---

### 🏗️ Optional LLM Add-ons:

- 	Semantic Search & Retrieval-Augmented Generation (RAG) for:
- 	Grant abstracts
- 	Research papers
- 	Reviewer databases
- 	LangChain or LangGraph agent to orchestrate multiple tools: e.g., metric fetcher, citation analyzer, impact summarizer, novelty detector.


---

### 🔄 Integration Architecture Overview


```plaintext
         +-----------------------+
         | Web of Science / APIs |
         +----------+------------+
                    |
             +------+------+
             | Preprocessing |
             +------+------+
                    |
        +-----------v------------+
        |  Vector Store (FAISS)  |
        +-----------+------------+
                    |
    +---------------v---------------+
    |    LangGraph or LangChain Agent   |
    +--------+------------+---------+
             |            |
     +-------v--+   +-----v-------+
     |  Metric DB |   |  LLM (OpenAI, etc) |
     +------------+   +-------------------+
```

---


### LLM prompt Templates 


Here is a set of LLM prompt templates for each core feature of an Academic Impact Analysis Agent, designed to be used with GPT-4 or similar foundation models. These prompts assume you have metadata (e.g. publications, citations, metrics) available from sources like Web of Science, Scopus, or your own database.

---

🔬 1. Impact Summary Generation

Prompt:

```yaml
You are an expert research analyst.

Summarize the academic impact of the following researcher based on their publication and citation history:

Researcher: {{name}}
Affiliation: {{affiliation}}
Publications:
{{publications_list}}  # List of papers with year, title, citations
Total Citations: {{total_citations}}
h-index: {{h_index}}

Provide:
1. Summary of impact
2. Key contributions
3. Most influential papers
4. Fields or topics where the researcher has the most influence
5. Trends over time

```


---

📈 2. Citation Trajectory Forecasting

Prompt:
```yaml
You are a bibliometric analyst.

Given the past citation data for a researcher, forecast their future citation trajectory over the next 5 years.

Researcher: {{name}}
Historical citation data (year: citations):
{{citation_data_by_year}}

Provide:
1. A brief trend analysis
2. A 5-year forecast of total citations
3. Any anomalies or noteworthy inflection points
```

---

🧪 3. Top Contributions & Signature Work Identification

Prompt:
```yaml
You are evaluating the most important academic contributions of a researcher.

Researcher: {{name}}
Publications:
{{publications_list}}  # title, venue, year, citation count

Identify:
1. The top 3 most influential papers and why
2. Signature methods, theories, or frameworks introduced
3. How these contributions have influenced the field



---

🔍 4. Research Novelty and Innovation Detection

Prompt:
```yaml
You are an academic reviewer.

Evaluate the novelty and innovation of the following paper in the context of existing literature.

Paper title: {{paper_title}}
Abstract: {{abstract}}
Published in: {{journal}} ({{year}})
Researcher: {{author_name}}

Is this work novel? How does it extend or diverge from past work? What is the innovation?
```



---

🧠 5. Topic Influence Mapping

Prompt:
```yaml

You are a research impact analyst.

Based on the list of papers and topics, analyze the topics where the researcher has the greatest influence.

Researcher: {{name}}
Publications with keywords:
{{papers_with_topics}}  # [title, year, citations, topics/keywords]

Provide:
1. A list of top 3 fields/topics where this researcher is influential
2. How their influence has evolved over time
3. Emerging areas they are contributing to
```

---

🕸 6. Collaboration Impact Evaluation

Prompt:
```yaml
You are analyzing collaborative academic impact.

Researcher: {{name}}
Coauthors: {{coauthor_list}}  # with paper titles and citations

Evaluate:
1. Which coauthors have led to the most impactful collaborations?
2. Are there specific collaborations driving higher citation rates?
3. How has collaboration influenced the researcher’s impact trajectory?
```

---

🏆 7. Benchmarking Against Peers

Prompt:
```yaml
You are a metrics-based reviewer.

Compare the impact of {{name}} with peer researchers working in the same domain.

Target researcher:
- Name: {{name}}
- h-index: {{h_index}}
- Citations: {{citations}}
- Field: {{field}}

Peer group data:
{{peer_stats}}  # List of researchers with similar metrics

Provide:
1. Relative standing of the researcher
2. Strengths or gaps compared to peers
3. Recommendation for improvement or recognition
```

---

🧾 8. Grant Impact Traceback

Prompt:
```yaml
You are an evaluator for research funding ROI.

For each grant listed, trace its academic output and impact.

Researcher: {{name}}
Grants:
{{grants_list}}  # [Grant ID, title, agency, funding amount]

Publications derived from grants:
{{grant_publication_map}}

Analyze:
1. Output (publications) and citation impact for each grant
2. Which grants were most academically fruitful?
3. Which ones underperformed and why?
```

---

📚 9. Knowledge Transfer to Industry (Optional)

Prompt:
```yaml
You are analyzing academic to industry impact.

Researcher: {{name}}
Patents filed: {{patents}}
Industry collaborations: {{industry_collaborators}}
Papers cited in patents: {{cited_in_patents}}

Summarize:
1. Knowledge transferred to industry
2. Any patents/products stemming from their work
3. Evidence of tech transfer or practical deployment
```


---

🧩 Bonus: Multi-modal Integration Prompt (Papers + Graphs + Metrics)

Prompt:

```yaml
You are an AI agent summarizing academic impact using mixed input sources.

Researcher: {{name}}
Papers: {{papers_with_citations_and_topics}}
Coauthor Graph: {{coauthor_graph_summary}}
Institutional metrics: {{institutional_context}}
h-index: {{h_index}}

Generate:
- High-level summary of impact
- Topic areas of influence
- Collaboration strength
- Suggestions for expanding impact
```

---

## ✅ Integration Usage


Each of these prompt templates can be plugged into:

- 	🔁 LangChain (as PromptTemplates)
- 	🧠 LlamaIndex or RAG chains (using metadata context)
- 	🕸 Graph RAG (with embeddings + structured relationships)
- 	🖼 UI tools (e.g., Streamlit or dashboards for analytics)


Here is a concrete LangChain PromptTemplate example for several key academic impact analysis tasks. This uses LangChain’s PromptTemplate class in Python and shows how to define and run LLM-powered academic analysis using researcher metadata.

---

🧠 1. Impact Summary PromptTemplate


```python
from langchain_core.prompts import PromptTemplate

impact_summary_prompt = PromptTemplate.from_template(
    template="""
You are an expert research analyst.

Summarize the academic impact of the following researcher based on their publication and citation history:

Researcher: {name}
Affiliation: {affiliation}
Publications:
{publications}  # Format: title, year, citation count
Total Citations: {total_citations}
h-index: {h_index}

Provide:
1. Summary of impact
2. Key contributions
3. Most influential papers
4. Fields or topics where the researcher has the most influence
5. Trends over time
"""
)
```

Sample usage:

```python
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4", temperature=0.3)

chain = impact_summary_prompt | llm

result = chain.invoke({
    "name": "Dr. Jane Doe",
    "affiliation": "MIT CSAIL",
    "publications": "- 'Learning to Rank', 2018, 510 citations\n- 'Neural IR Models', 2020, 350 citations",
    "total_citations": "1200",
    "h_index": "17"
})

print(result.content)

```

---

📈 2. Citation Forecasting PromptTemplate

```python
citation_forecast_prompt = PromptTemplate.from_template(
    template="""
You are a bibliometric analyst.

Given the past citation data for a researcher, forecast their future citation trajectory over the next 5 years.

Researcher: {name}
Historical citation data (year: citations):
{citation_data}

Provide:
1. A brief trend analysis
2. A 5-year forecast of total citations
3. Any anomalies or noteworthy inflection points
"""
)
```

---

🧪 3. Top Contributions Identification PromptTemplate


```python

top_contributions_prompt = PromptTemplate.from_template(
    template="""
You are evaluating the most important academic contributions of a researcher.

Researcher: {name}
Publications:
{publications}  # title, venue, year, citation count

Identify:
1. The top 3 most influential papers and why
2. Signature methods, theories, or frameworks introduced
3. How these contributions have influenced the field
"""

```


---

### 🧠 Full Example: LangChain RunnableChain

You can define a chain for any feature like this:

```python
from langchain.chains import LLMChain

impact_summary_chain = LLMChain(
    llm=llm,
    prompt=impact_summary_prompt,
    verbose=True,
)
```

To run:

```python
response = impact_summary_chain.invoke({
    "name": "Dr. Alice Smith",
    "affiliation": "Stanford University",
    "publications": "- 'Graph Embeddings', 2019, 1000 citations\n- 'AI for Drug Discovery', 2021, 700 citations",
    "total_citations": "3500",
    "h_index": "22"
})
print(response["text"])
```            

---

### ✅ You can repeat this pattern for all 8–10 academic impact functions:

Each one becomes:

```python
your_feature_chain = LLMChain(llm=llm, prompt=your_feature_prompt)
```   

---

##  A Working Prototype Design of a LangChain Agent


 Great! Here’s a working prototype design of a LangChain Agent for Academic Impact Analysis that routes tasks like impact summary, citation forecast, benchmark, etc., using prompt templates, tools, and agent routing.


---

### 🧠 Agent Design Overview

🔧 Tools / Chains:

Each task is encapsulated as a separate LLMChain or Tool:
- 	impact_summary_chain
- 	citation_forecast_chain
- 	top_contributions_chain
- 	benchmark_against_peers_chain
- 	research_trends_chain

🧩 Routing Strategy:

Use either:
- 	MultiPromptRouter (simple prompt-based)
- 	or a LangGraph agent (recommended for stateful and extensible routing)

---

### 🧰 Step-by-Step Implementation (LangChain LLMRouter Agent)

1. Prompt Templates

Already defined in previous response for:
- 	Impact Summary
- 	Citation Forecast
- 	Top Contributions

You can define more similarly.

---

2. Chains for Each Task

```python
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4", temperature=0.3)

impact_summary_chain = LLMChain(llm=llm, prompt=impact_summary_prompt)
citation_forecast_chain = LLMChain(llm=llm, prompt=citation_forecast_prompt)
top_contributions_chain = LLMChain(llm=llm, prompt=top_contributions_prompt)
```


---

3. Tool Wrappers for Each Chain

```python
from langchain.tools import Tool

tools = [
    Tool(
        name="ImpactSummary",
        func=impact_summary_chain.run,
        description="Summarize the research impact of a scholar using their publications and citations."
    ),
    Tool(
        name="CitationForecast",
        func=citation_forecast_chain.run,
        description="Forecast future citation growth based on historical data."
    ),
    Tool(
        name="TopContributions",
        func=top_contributions_chain.run,
        description="Identify key academic contributions and high-impact papers."
    ),
    # Add more tools here
]
```

---

4. Routing Agent Setup (MultiPromptRouterAgent)

```python
from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
```

---

5. Running the Agent

```python
agent.run("Give me an impact summary of Dr. Jane Doe based on her citation history and top papers.")
```

---

### ✅ Example Input Types

You can build a UI or function that gathers input like:

```json
{
  "name": "Dr. John Smith",
  "affiliation": "University of Toronto",
  "publications": "- 'Deep Transfer Learning', 2016, 850 citations\n- 'Zero-shot NLP', 2020, 500 citations",
  "total_citations": "2000",
  "h_index": "20",
  "citation_data": "2017: 100\n2018: 200\n2019: 300\n2020: 500\n2021: 700"
}
```

Then pass this into the appropriate chain.


---

### 🧠 Optional LangGraph Agent


If you want memory, conversation state, and dynamic workflows (e.g. invoke one chain then reroute based on output), I can convert this into a LangGraph setup.


Here’s a full working example for building RAG chains using LlamaIndex, focused on academic impact analysis using metadata context (like researcher profiles, papers, metrics). This can be used in your Academic Impact Agent or extended for Reviewer Recommender, Grant Matching, etc.

---


## 🧠 Use Case: Academic Impact RAG (Researcher-Level)

We’ll build a RAG pipeline using:

| Layer         | Component                                                      |
|---------------|---------------------------------------------------------------|
| Data Source   | JSON, CSV, SQL, or API of researcher/paper metadata           |
| Index         | VectorStoreIndex or ComposableGraph                           |
| Metadata      | Author name, h-index, topics, affiliations                    |
| Retriever     | Metadata-filtered retriever (`metadata_filters`)               |
| Synthesizer   | LLM with PromptTemplate                                       |
| Output        | Impact summary, top contributions, citation trends            |



---

### 🧰 1. Sample Researcher Metadata (JSON format)

```json
{
  "id": "john_smith",
  "name": "Dr. John Smith",
  "affiliation": "University of Toronto",
  "h_index": 28,
  "total_citations": 4200,
  "papers": [
    {
      "title": "Deep Transfer Learning",
      "year": 2016,
      "citations": 850,
      "topics": ["Transfer Learning", "Representation Learning"]
    },
    {
      "title": "Zero-shot NLP",
      "year": 2020,
      "citations": 600,
      "topics": ["NLP", "Zero-shot Learning"]
    }
  ]
}
```

---

### ⚙️ 2. Build Vector Index with Metadata (LlamaIndex)

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.schema import Document
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms import OpenAI

documents = [
    Document(
        text="Dr. John Smith has published papers in transfer learning and zero-shot NLP...",
        metadata={
            "name": "John Smith",
            "affiliation": "University of Toronto",
            "h_index": 28,
            "topics": ["Transfer Learning", "NLP"]
        }
    ),
    # add more documents per researcher
]

service_context = ServiceContext.from_defaults(
    llm=OpenAI(model="gpt-4"),
    embed_model=OpenAIEmbedding(model="text-embedding-3-small")
)

index = VectorStoreIndex.from_documents(documents, service_context=service_context)
```

---

🔍 3. Metadata-Aware Querying (RAG)

```python
query_engine = index.as_query_engine(
    similarity_top_k=3,
    filters={"topics": "NLP"}
)

response = query_engine.query("Summarize Dr. John Smith's academic impact and top contributions.")
print(response)

query_engine = index.as_query_engine(
    similarity_top_k=3,
    filters={"topics": "NLP"}
)

response = query_engine.query("Summarize Dr. John Smith's academic impact and top contributions.")
print(response)
```


🧠 You can pass user prompts like "What is the citation trend of Dr. John Smith?" and the system will respond using both vector similarity and the metadata.

---

### 🧱 4. Build a RAG Chain with LangChain + LlamaInde


```python
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from llama_index.core.retrievers import VectorIndexRetriever

retriever = index.as_retriever(similarity_top_k=3)
llm = OpenAI(model_name="gpt-4")

rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

result = rag_chain.run("Benchmark Dr. Smith’s citation impact over time and list their most influential work.")
print(result)

```

---

### 🎯 5. Advanced: ComposableGraph Index (Multi-Field Retrieval)

If you want to index researchers by:
- 	name
- 	affiliation
- 	topic cluster
- 	h-index bin

Use ComposableGraph index with keyword + vector retrievers to combine filters and semantic retrieval.

---

### ✅ Summary of Capabilities Powered by RAG


| Task                      | Powered by RAG?      | Metadata Filtering                |
|---------------------------|----------------------|-----------------------------------|
| Impact Summary            | ✅ Yes               | By name, h-index                  |
| Top Contributions         | ✅ Yes               | By topic, citation                |
| Peer Benchmarking         | ✅ Yes               | By affiliation, field             |
| Citation Forecasting      | ➖ (LLM modeled)     | ❌                                |
| Cross-field Topic Impact  | ✅ Yes               | By topic embedding                |
| Reviewer/Co-PI Matching   | ✅ Yes               | By co-authors, ORCID, institution |


Great choice. Hybrid RAG with Elasticsearch + LLMs (e.g., OpenAI, Claude, LLaMA) allows:

- 	🔍 Lexical search (BM25) for exact matches, filters, and metadata-based retrieval
- 	🧠 Semantic reranking or augmentation using vector similarity and LLM synthesis
- 	⚖️ Hybrid ranking: combine BM25 + dense vector + metadata filtering
- 	🎯 RAG pipeline: Retrieve top-k documents from ES, rerank or summarize via LLM

---

### ✅ Goal: Hybrid RAG for Academic Impact Analysis

We’ll build a pipeline that:
	1.	Indexes researcher/paper metadata in Elasticsearch with dense vectors
	2.	Performs hybrid retrieval (BM25 + vector + filters like topics, h-index)
	3.	Ranks results and generates an LLM-based impact summary or benchmark

---

#### ⚙️ 1. Elasticsearch Hybrid RAG Setup

🧱 Sample Document Structure for Indexing

```json
{
  "id": "smith_2020",
  "title": "Zero-shot NLP",
  "abstract": "This paper explores...",
  "year": 2020,
  "authors": ["John Smith", "Anna Lee"],
  "institution": "University of Toronto",
  "topics": ["NLP", "Zero-shot Learning"],
  "h_index": 28,
  "total_citations": 600,
  "vector": [0.001, 0.123, ..., 0.089]  // Dense embedding
}
```

---

#### 🛠 2. Indexing Data

Use Elasticsearch with dense_vector and metadata fields.

```python
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

es = Elasticsearch("http://localhost:9200")
model = SentenceTransformer("all-MiniLM-L6-v2")

text = "Zero-shot NLP..."
embedding = model.encode(text)

doc = {
    "title": "Zero-shot NLP",
    "abstract": text,
    "year": 2020,
    "authors": ["John Smith"],
    "institution": "University of Toronto",
    "topics": ["NLP"],
    "total_citations": 600,
    "vector": embedding.tolist()
}

es.index(index="academic_papers", id="smith_2020", document=doc)
```

---

#### 🔍 3. Hybrid Retrieval Query

```python
query_text = "Dr. John Smith's most influential work on zero-shot learning"
query_vector = model.encode(query_text)

search_query = {
  "size": 5,
  "query": {
    "script_score": {
      "query": {
        "bool": {
          "must": [
            {"match": {"abstract": "zero-shot learning"}},
            {"term": {"authors": "John Smith"}}
          ]
        }
      },
      "script": {
        "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
        "params": {"query_vector": query_vector.tolist()}
      }
    }
  }
}
results = es.search(index="academic_papers", body=search_query)
```


---

### 🤖 4. LLM RAG: Summarize Retrieved Results

Use LangChain or plain OpenAI API:

```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

llm = ChatOpenAI(model="gpt-4")
template = PromptTemplate(
    input_variables=["docs"],
    template="""
You are an academic analyst. Given the following documents, summarize the research impact of the author:
{docs}
Return a structured summary with:
- Research Focus
- Most Cited Work
- Citation Trends
- Collaborators
"""
)

chain = LLMChain(prompt=template, llm=llm)

retrieved_docs = "\n\n".join([hit["_source"]["abstract"] for hit in results["hits"]["hits"]])
summary = chain.run({"docs": retrieved_docs})
print(summary)
```


---

### 🧱 Optional: Hybrid Ranking + FAISS Reranking

You can also combine Elasticsearch + FAISS:
	1.	Use ES to retrieve 100 candidates
	2.	Embed with SentenceTransformer
	3.	Use FAISS to rerank top 10
	4.	Feed to LLM

---


### 🧠 Sample Use Cases Powered by Hybrid RAG


| Task                                 | ES Filter | Dense Vector | LLM |
|-------------------------------------- |:---------:|:------------:|:---:|
| Top-contributing papers               |     ✅     |      ✅       | ✅  |
| Field-specific benchmark (e.g., AI)   |     ✅     |      ✅       | ✅  |
| Forecast citation growth (similar papers) |  ✅     |      ✅       | ✅  |
| Co-PI network exploration             |     ✅     |      ❌*      | ✅  |
| Cross-institution impact comparison   |     ✅     |      ✅       | ✅  |

\* For Co-PI network exploration, consider using a graph database or graph-based retrieval in addition to ES filters.


---


### ✅ Summary: Full Hybrid RAG Stack

```plaintext
          ┌──────────────┐
          │   User Query │
          └─────┬────────┘
                ▼
        ┌───────────────┐
        │ Query Embedding│ ◄─ SentenceTransformer
        └────┬──────────┘
             ▼
   ┌──────────────────────┐
   │ Elasticsearch Hybrid │ ◄─ BM25 + vector + filters
   └────┬─────────────────┘
        ▼
   ┌────────────────────┐
   │ Top-k Document Set │
   └────┬───────────────┘
        ▼
     ┌───────────────┐
     │  LLM Synthesizer│ ◄─ GPT-4 / Claude / Mistral
     └────┬────────────┘
          ▼
    Impact Summary Output

```