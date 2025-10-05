## Emerging Topic Finder AI Agent

Here’s a complete design for an Academic Emerging Topic Finder AI Agent, including a top feature list powered by LLMs, architecture principles, and task workflows.

---

### 🎯 Objective

Help researchers, funders, institutions, and publishers identify emerging topics, research frontiers, disruptive trends, and growing scientific communities using literature, citations, grants, patents, preprints, and conferences.

---

### 🧠 Top LLM-Powered Features for Emerging Topic Finder


1. Trend Detection & Topic Evolution

- 	Analyze multi-year publications to detect emerging, growing, peaking, or declining topics.
- 	LLM-powered summarization of topic trajectory and subfield splits/merges.
- 	Prompt: “Summarize the evolution of AI in drug discovery from 2015–2025 and identify emerging subtopics.”

2. Hot Paper & Preprint Detection

- 	Surface rapidly cited or widely discussed papers/preprints.
- 	LLM assesses novelty and interdisciplinary impact based on abstract/full text.
- 	Prompt: “Evaluate if this paper introduces a novel research direction in cancer immunotherapy.”

3. Topic Novelty & Disruption Scoring

- 	Assess novelty of a topic based on:
- 	Concept uniqueness (vs prior work).
- 	Interdisciplinary fusion.
- 	Low overlap with previous clusters (using embeddings + LLM).
- 	Prompt: “Does this topic on quantum ML for protein folding combine previously unlinked disciplines?”

4. Emerging Topic Clustering & Labeling

- 	Group papers with embeddings (e.g. SPECTER, SciBERT) → cluster → LLM generates concise topic labels & summaries.
- 	Prompt: “Label and summarize this cluster of 20 abstracts in 2 sentences.”

5. Cross-Domain Trend Discovery

- 	LLM discovers topics emerging simultaneously across fields (e.g., LLMs in bioinformatics + education).
- 	Prompt: “Which domains have started applying transformers since 2021 and what are the key breakthroughs?”

6. Citation Network Frontier Detection

- 	Combine citation network analysis with LLM summary of low-density/high-growth clusters.
- 	Prompt: “Identify research areas that form new citation frontiers since 2023.”

7. Early-Stage Researcher Activity Detection

- 	LLM highlights fresh topics pursued by early-career researchers or new labs (signals innovation).
- 	Prompt: “List new labs publishing in microfluidic organoid research since 2022 and their focus.”

8. Funding-to-Publication Pipeline Analysis

- 	Detect emerging topics with strong funding signals but limited publications → early indicator.
- 	Prompt: “Which grant-funded topics have yet to be widely published?”

9. Geographic & Institutional Emergence

- 	LLM analyzes metadata to surface which countries, institutions, or labs are pioneering a topic.
- 	Prompt: “Which Asian institutions are leading in green hydrogen photochemistry research?”

10. Emergence Alert Feed / Topic Radar

- 	Auto-curated, LLM-summarized daily/weekly report of emerging topics with:
- 	Trend score
- 	Top papers
- 	Novelty summary
- 	Growth rate
- 	Prompt: “Generate a weekly alert of emerging topics in synthetic biology.”

---

### 🏗️ System Architecture

🔹 Data Sources

- 	Web of Science, Dimensions, arXiv, bioRxiv, PubMed, CrossRef
- 	Patents (USPTO, EPO), Grants (NIH, NSF, Horizon)
- 	Citation Graphs, Conference CFPs

🔹 Pipeline

	1.	Ingest & Normalize: Metadata, full text, citations
	2.	Embed: SPECTER/SciBERT/Instructor embeddings
	3.	Cluster: HDBSCAN / Louvain clustering on embedding + temporal data
	4.	Analyze: Trend, novelty, growth, interdisciplinarity
	5.	LLM Synthesis: Topic labeling, summary, reasoning
	6.	UI/API: Query interface, alert dashboard, topic graph

🔹 Tools

- 	LLMs: GPT-4o, Claude, or open-source (Mixtral, LLaMA)
- 	Vector DB: FAISS / Weaviate / Elasticsearch
- 	Graph DB: Neo4j (for co-authorship, citation, institution networks)
- 	Scheduler: Airflow / Prefect for weekly updates


---

### 💡 LLM Prompt Engineering Examples

📌 Topic Labeling

Given these 10 abstracts, what is the best 3-word name for this emerging research area?

📌 Novelty Assessment

Does this abstract describe a novel combination of research fields or a significant advancement?

📌 Interdisciplinary Detection

Identify all domain terms in this abstract and map which scientific fields they belong to.

📌 Cross-topic Merging

Which two topics among this list show signs of converging based on shared papers or citations?

---

### ✅ Applications

- 	Researchers: Identify new directions to explore
- 	Funders: Spot trends early for strategic investment
- 	Publishers: Curate hot-topic special issues
- 	Institutions: Benchmark research emergence and lead


---

Here is a curated list of actual LLM prompts—tailored for each feature—designed for your Academic Emerging Topic Finder AI Agent. These are production-ready templates that can be used in LangChain, LlamaIndex, or custom pipelines.

---

### 🎯 LLM Prompt Templates by Feature

---

1. Trend Detection & Topic Evolution

Prompt:
```plaintext
You are an expert science analyst. Given the following list of paper titles and abstracts published between 2015 and 2025, analyze the evolution of the research topic. Identify key shifts in focus, terminology, or methodology, and summarize the trajectory in bullet points.

Papers:
{{documents}}

Output:
- Time period trends (e.g., 2015–2018: ..., 2019–2022: ...)
- Emerging subtopics or offshoots
- Declining trends (if any)
```



---

2. Hot Paper & Preprint Detection

Prompt:
```plaintext
A new preprint has received a high number of downloads and mentions. Based on the title and abstract, evaluate if the paper likely represents a novel or impactful contribution.

Title: {{title}}
Abstract: {{abstract}}

Assess:
1. Novelty of idea or approach
2. Potential cross-domain relevance
3. Impact compared to prior works
4. Likelihood it will drive a new research trend

Respond with bullet-point assessment.
```



---

3. Topic Novelty & Disruption Scoring

Prompt:
```plaintext
You're analyzing the originality of a research topic cluster. Read the following paper abstracts and rate the novelty of the topic based on:
- Conceptual originality
- Interdisciplinary connections
- Departure from established literature

Abstracts:
{{documents}}

Respond with:
- Overall novelty score: (High / Medium / Low)
- Key reasons
- Prior fields or paradigms it breaks from
```


---

4. Emerging Topic Clustering & Labeling

Prompt:
```plaintext
You're given a set of paper abstracts that belong to the same topic cluster. Your task is to:
1. Assign a short and descriptive topic label (3–6 words)
2. Write a 2-sentence summary of the cluster
3. List 3 key themes or keywords from the papers

Cluster Abstracts:
{{documents}}
```


---

5. Cross-Domain Trend Discovery

Prompt:
```plaintext
You are a research trend analyst. Given a set of abstracts from different disciplines, identify whether any emerging technique or topic is being adopted across multiple fields.

Abstracts:
{{documents}}

Output:
- Shared technique or topic
- Fields applying it
- Timeline of spread
```


---

6. Citation Network Frontier Detection

Prompt:
```plaintext
The following group of papers has formed a loosely connected citation cluster in the last 2 years. Does this indicate the birth of a new research frontier?

Citations and Abstracts:
{{citation_graph_summary}}

Answer:
- Is this a new research frontier? (Yes/No)
- Summary of the frontier (2–3 sentences)
- What distinguishes it from adjacent areas?
```


---

7. Early-Stage Researcher Activity Detection

Prompt:
```plaintext
Analyze the research activity of new authors (first publications in last 2 years) and identify whether they are concentrating on a potentially emerging topic.

Researcher Publications:
{{documents}}

Output:
- Common topic(s) among early-stage researchers
- Novel methods or ideas they’re exploring
- Potential for emergence
```




---

8. Funding-to-Publication Pipeline Analysis

Prompt:
```plaintext
Given a set of funded project titles and descriptions with minimal publication output so far, identify which of them may represent early-stage, high-impact research areas.

Grants:
{{documents}}

Answer:
- Topic(s) with strong potential
- Why these topics haven’t yet saturated publication
- Leading institutions or teams
```



---

9. Geographic & Institutional Emergence

Prompt:
```plaintext
Analyze the metadata and abstracts to determine which countries or institutions are pioneering work in this emerging topic.

Abstracts and Metadata:
{{documents}}

Answer:
- Top 3 pioneering institutions
- Country-level leadership (if applicable)
- Emerging hubs or collaborations
```


---

10. Emergence Alert Feed / Topic Radar

Prompt:
```plaintext
You are generating a weekly emerging topic alert for researchers. Based on this cluster of papers from the last 6 months, summarize the emerging topic in newsletter form.

Input Papers:
{{documents}}

Output:
- 📌 Topic Title:
- 🔍 Summary (2–3 sentences):
- 📈 Growth indicators (keywords, citations, spread):
- 🧠 Why this matters:
- 🔗 Links to key papers:
```

---

### 🧩 Optional: Use with LangChain or LlamaIndex


For example, with LangChain PromptTemplate

```python
from langchain.prompts import PromptTemplate

novelty_prompt = PromptTemplate(
    input_variables=["documents"],
    template="""
You are analyzing the originality of a research topic cluster. Read the following paper abstracts and rate the novelty of the topic based on:
- Conceptual originality
- Interdisciplinary connections
- Departure from established literature

Abstracts:
{documents}

Respond with:
- Overall novelty score: (High / Medium / Low)
- Key reasons
- Prior fields or paradigms it breaks from
"""
)
```
