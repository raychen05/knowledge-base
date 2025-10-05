## Academic Paper Search AI Agent 

Designing an Academic Paper Search AI Agent powered by LLMs (like GPT-4 or Claude) enables not just keyword-based search, but semantic, contextual, citation-aware, and task-specific retrieval. Below is a curated list of top features that such an agent can offer—categorized by functionality and enhanced by LLM capabilities.


---

### 🔍 Top LLM-Powered Features for Academic Paper Search AI Agent

1. Semantic Paper Search
- 	Understands natural language queries and retrieves papers even without exact keyword matches.
- 	✅ LLM Role: Reformulate vague, incomplete, or complex questions into precise search queries.

2. Query Expansion & Refinement
- 	Suggests broader, narrower, or related terms to improve recall or precision.
- 	✅ LLM Role: Expand terms (e.g., “LLMs in medicine” → “GPT, BERT, clinical NLP, EHR analysis”).

3. Task-Aware Search
- 	Tailors results based on intent: literature review, method benchmarking, novelty scouting, etc.
- 	✅ LLM Role: Classify and reformulate queries according to task intent.

4. Citation-Aware Ranking
- 	Ranks papers based on citation graph, co-citation clusters, or impact metrics.
- 	✅ LLM Role: Interpret citation networks and explain why certain papers are foundational or trending.

5. Topic Clustering & Faceted Search
- 	Groups search results into thematic clusters or facets (e.g., methods, domains, applications).
- 	✅ LLM Role: Classify and summarize paper clusters with labels like “transformer-based methods”, “clinical trials”, etc.

6. Key Insights Extraction
- 	Extracts and summarizes key contributions, methods, datasets, and results from each paper.
- 	✅ LLM Role: Parse abstract + body to generate structured summaries.

7. Comparative Analysis of Papers
- 	Compares 2–5 papers side by side: methods, results, strengths/weaknesses.
- 	✅ LLM Role: Generate tabular or bullet-format comparisons.

8. Trend and Hot Topic Detection
- 	Identifies emerging themes or rising topics in a field.
- 	✅ LLM Role: Analyze time-stamped abstracts and keywords to identify novel clusters or terms.

9. Find Related Work (Paper Graph Traversal)
- 	Discover related work based on semantic content, citations, co-authorship, or venues.
- 	✅ LLM Role: Recommend “papers you should read next” with justification.

10. Zero-Shot Domain Adaptation
- 	Handles queries across interdisciplinary fields without prior tuning.
- 	✅ LLM Role: Understand context from multiple domains simultaneously (e.g., AI for neuroscience).

11. Explain Search Result Relevance
- 	Justify why each paper was retrieved—e.g., “This paper applies BERT to clinical note classification.”
- 	✅ LLM Role: Generate natural-language rationale from title + abstract + match score.

12. Multilingual Paper Discovery
- 	Finds papers written in multiple languages and summarizes in user’s language.
- 	✅ LLM Role: Translate and summarize foreign-language papers.

13. Author and Institution-Based Filtering
- 	Search by specific authors, affiliations, or academic groups.
- 	✅ LLM Role: Resolve name disambiguation and group by canonical entities.

14. Graph-Based Exploration
- 	Explore the citation/co-authorship graph interactively.
- 	✅ LLM Role: Generate natural language summaries of citation neighborhoods.

15. Personalized Paper Recommendations
- 	Learns your interests over time to suggest relevant and novel papers.
- 	✅ LLM Role: Combine embeddings of user’s saved papers with retrieval-based generation.

---

### 🧠 Bonus LLM-Enhanced UX Features

| Feature                   | Description                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| Natural Language Interface | Ask “What’s the latest on causal inference in policy evaluation?” and get smart results. |
| Follow-up Query Memory     | Supports back-and-forth refinement: “What about those using RCTs?”          |
| Summarize Reading List     | Bulk summarize 10+ papers to speed up literature review.                     |
| Method Card Generator      | Auto-create cheat sheets for techniques like “Diffusion Models” or “Masked Autoencoders.” |
| Dataset Finder             | Detect datasets used across search results.                                  |
| Code & Resource Linking    | Identifies if code is linked (e.g., via GitHub, HuggingFace).               |


Great! Below are LLM Prompt Templates for each of the top features of an Academic Paper Search AI Agent — designed to be used with models like GPT-4, Claude, or others via LangChain or other frameworks.

---

### 🧠 LLM Prompt Templates for Paper Search Features

1. Semantic Paper Search

Given the user's query: "{user_query}", rewrite it as a precise academic search query that captures the key intent, terminology, and related fields, suitable for retrieving academic papers.

Output: Reformulated query with keywords and short explanation.


---

2. Query Expansion & Refinement

Expand the search query: "{user_query}" with semantically related keywords, synonyms, broader and narrower terms commonly used in academic literature.

Output format:
- Original query:
- Broader terms:
- Narrower terms:
- Related keywords:


---

3. Task-Aware Search

Classify the intent of this academic search query: "{user_query}"

Choose from:
- Literature review
- Method comparison
- Novelty scouting
- Benchmarking
- Finding datasets
- Tutorial/introductory
- Reproduction or replication

Then, rephrase the query to match the intent.


---

4. Citation-Aware Ranking Explanation


Explain why the following paper is relevant or important in its research area:

Title: {paper_title}
Abstract: {paper_abstract}
Citations: {citation_count}
Year: {publication_year}

Output: A short explanation of its significance and impact.



---

5. Topic Clustering and Labeling


You are given a list of academic paper titles and abstracts. Group them into thematic clusters and give each cluster a concise, descriptive label.

Input:
[{title: ..., abstract: ...}, {...}, ...]

Output:
Clustered groups with labels and representative keywords.



---

6. Key Insights Extraction


Extract the following from the paper:
- Research problem
- Proposed method
- Key results
- Dataset(s) used
- Any novel contribution

Paper:
Title: {title}
Abstract: {abstract}

Output format:
Problem:
Method:
Results:
Datasets:
Novelty:



---

7. Comparative Analysis of Papers


Compare the following academic papers. Identify similarities and differences in their methods, datasets, and findings.

Paper A: {title_a} - {abstract_a}
Paper B: {title_b} - {abstract_b}

Output: Comparative summary in table or bullet format.



---

8. Trend and Hot Topic Detection

You are given paper titles, abstracts, and publication years from 2015–2025 in {domain}. Identify emerging research trends and growing areas of interest over time.

Output:
- Topic clusters
- Trend trajectory (rising/stable/declining)
- Keywords



---

9. Find Related Work


Find 3–5 papers that are most semantically similar to the following input paper, and explain how each is related.

Input paper:
{title}
{abstract}

Related papers:
[{title, abstract}, ...]

Output: Paper list + 1-sentence justification for each.



---

10. Zero-Shot Domain Adaptation

Interpret the query "{user_query}" in the context of academic literature. Identify:
- Relevant domains
- Key concepts
- Any implicit assumptions

Then output a structured query suitable for cross-disciplinary search.



---

11. Explain Search Result Relevance

Given this user query: "{user_query}"
And the retrieved paper:
Title: {title}
Abstract: {abstract}

Explain in 2–3 sentences why this paper is relevant to the query.



---

12. Multilingual Paper Discovery


Translate this non-English academic paper abstract into fluent English and summarize its key contributions.

Language: {language}
Title: {title}
Abstract: {abstract}


---

13. Author & Institution Disambiguation


Given a list of author names and affiliations from search results, cluster them by likely canonical identities. Resolve name variants and group by institution.

Input: [{name: ..., affiliation: ...}, ...]

Output: Cleaned canonical list grouped by person and organization.


---

14. Citation Graph Neighborhood Summary

You are given a paper and its citation network (cited and citing papers). Summarize the research context and academic lineage.

Input:
- Paper: {title + abstract}
- Cited papers: [{title, abstract}]
- Citing papers: [{title, abstract}]

Output: Summary of research lineage and how the paper fits into the field.



---

15. Personalized Paper Recommendations

You are a research assistant. Based on the following papers the user has saved, recommend 3 new papers likely to interest them.

User's reading list: [{title, abstract}]
Candidate pool: [{title, abstract}]

Output: 3 paper recommendations with short rationales.


---

### 🔧 Bonus UX Prompts

#### A. Summarize Reading List

Summarize the following list of papers into key takeaways grouped by topic and contribution.

Input: List of titles + abstracts

Output: Thematic summary with grouped insights.



---

#### B. Method Card Generator

Create a concise method card for "{method_name}" including:

- Description
- Use cases
- Strengths
- Key papers
- Tools/libraries

---

#### C. Dataset Finder

From the following papers, extract any dataset names used and briefly describe them.

Input: List of paper abstracts

Output: Dataset name, source, and use case per paper.


---

Great question. When researchers receive a list of academic papers (from a search, recommendation, or bulk export), they don’t just read them linearly. Instead, they extract, compare, and synthesize key information to serve different goals like writing a literature review, designing experiments, or identifying trends.

Here’s a ranked list of the most important pieces of information that researchers want to extract and highlight from a set of papers—especially those that can be automatically powered and enhanced by LLMs:

---

### 🧠 Top Items Researchers Want to Extract from Papers (LLM-Powered)


1. Research Objective / Problem Statement
- 	What is the central research question or problem the paper addresses?
- 	✅ LLM: Summarizes the aim concisely from title + abstract + intro.

---

2. Proposed Method / Approach
- 	What technique, algorithm, or framework is introduced or used?
- 	✅ LLM: Distills method from method sections or descriptions in abstract.

---

3. Key Results / Findings
- 	What did the authors discover, prove, or demonstrate?
- 	✅ LLM: Extracts core results (metrics, statistical significance, conclusions).

---

4. Datasets Used
- 	What datasets were used or introduced?
- 	✅ LLM: Identifies named datasets (e.g., ImageNet, MIMIC-III) and describes them.

---

5. Model or Tools Used
- 	What models, libraries, or frameworks were used (e.g., BERT, PyTorch)?
- 	✅ LLM: Extracts models/tools from methods section or keywords.

---

6. Contribution Summary / Novelty
- 	What is new or different about this paper compared to prior work?
- 	✅ LLM: Highlights novelty (e.g., “first to apply X to Y”).

---

7. Comparison to Prior Work
- 	How does the paper perform or differ compared to previous research?
- 	✅ LLM: Detects baselines and improvement margins.

---

8. Evaluation Metrics
- 	What metrics were used to evaluate performance (e.g., F1, BLEU, AUC)?
- 	✅ LLM: Lists and explains relevance of each metric.

---

9. Limitations / Future Work
- 	What are the weaknesses or open questions noted by the authors?
- 	✅ LLM: Identifies areas for improvement or research gaps.

---

10. Application Domain
- 	What field or domain does the research target (e.g., healthcare, NLP, robotics)?
- 	✅ LLM: Infers application domain from keywords and use cases.

---

11. Paper Type / Intent
- 	Is it a survey, experimental paper, theory, benchmark, tool, or application?
- 	✅ LLM: Classifies based on structure and keywords.

---

12. Reproducibility Info
- 	Is the code, data, or experimental setup available?
- 	✅ LLM: Extracts links, statements like “code available at…”

---

13. Author Affiliation & Collaborations
- 	Who conducted the work and at what institution?
- 	✅ LLM: Normalizes names and affiliations for clustering or impact analysis.

---

14. Citations / References Highlights
- 	What influential works are cited and built upon?
- 	✅ LLM: Extracts and explains citation context (e.g., foundational vs. comparative).

---

15. Research Timeline / Recency
- 	Is the work recent? Are the ideas still current or outdated?
- 	✅ LLM: Can flag time-sensitive techniques or shifts in trend.

---

16. Clustering / Similar Paper Grouping
- 	Which other papers in the list are related in method, topic, or results?
- 	✅ LLM: Can organize large result sets into thematic clusters.

---

17. Impact and Influence Summary
- 	How influential is this paper (citation, application, downstream usage)?
- 	✅ LLM: Explains impact even without citation counts, by semantic reasoning.

---

18. Task/Formal Problem Category
- 	Is this about classification, generation, segmentation, prediction, etc.?
- 	✅ LLM: Identifies formal task types from text.

---

19. Visual Summaries (Optional with LLM+V or Captioning)
- 	Convert figure captions and tables into textual summaries.
- 	✅ LLM+Vision: Extracts meaning from charts and results tables.

---

20. Lay Summary (for Non-Experts)
- 	Can the paper be summarized in layperson terms?
- 	✅ LLM: Writes accessible summaries for interdisciplinary readers.

---

### ✅ Summary Output Types Researchers Want

| Info Type         | Output Format                |
|-------------------|-----------------------------|
| Key findings      | Bullet points                |
| Comparison table  | Tabular                     |
| Method + dataset list | Structured JSON          |
| Trends & clusters | Thematic groups              |
| Summary paragraph | Natural language             |
| Graph insights    | Nodes + edges (text)         |
| Recommendations   | Ranked list                  |


---

Here’s a comprehensive LLM prompt designed to extract the most important research information from a list of academic papers. This prompt is structured to work well with a powerful LLM (e.g., GPT-4, Claude, Gemini) and can be used with tools like LangChain, LlamaIndex, or custom RAG pipelines.

---

### 🧠🔍 LLM Prompt: Extract Key Information from Academic Papers



You are an expert research assistant AI.

Your task is to analyze academic papers and extract structured summaries of the most important information researchers need for literature review, comparison, and synthesis.

For each paper, extract the following fields:

1. Title
2. Research Objective / Problem Statement
3. Proposed Method or Approach
4. Key Results and Findings
5. Dataset(s) Used (if any)
6. Models, Tools, or Frameworks Used
7. Contribution Summary / Novelty
8. Comparison to Prior Work or Baselines
9. Evaluation Metrics
10. Limitations and Future Work
11. Application Domain or Use Case
12. Paper Type (e.g., survey, benchmark, theoretical, application)
13. Code/Data Availability (URL or note)
14. Author(s) and Affiliation(s)
15. Year of Publication
16. Citations (if available)
17. Keywords or Tags
18. Related Work Suggestions (optional)
19. Lay Summary (1–2 sentence summary in accessible language)

---

Input:
Title: {paper_title}
Abstract: {paper_abstract}
(optional full text or introduction if available)

Output format (structured JSON):
{
  "title": "...",
  "year": "...",
  "authors": ["...", "..."],
  "affiliations": ["...", "..."],
  "objective": "...",
  "method": "...",
  "results": "...",
  "datasets": ["..."],
  "models_or_tools": ["..."],
  "contributions": "...",
  "comparison_to_prior_work": "...",
  "evaluation_metrics": ["..."],
  "limitations": "...",
  "application_domain": "...",
  "paper_type": "...",
  "code_or_data_link": "...",
  "citation_count": "...",
  "keywords": ["..."],
  "related_papers": ["..."],
  "lay_summary": "..."
}



---

### 🧪 Example Use in LangChain


```python
from langchain.prompts import PromptTemplate

paper_extraction_prompt = PromptTemplate(
    input_variables=["paper_title", "paper_abstract"],
    template="""
You are a scholarly AI assistant that extracts structured insights from academic papers.

Title: {paper_title}
Abstract: {paper_abstract}

Extract and summarize the following information:
[...same fields as above...]

Return your output as a well-formed JSON.
"""
)

```

---

### 🧠 Optional Enhancements

- 	Add citation graph context (e.g., papers cited, papers citing).
- 	Add full-text ingestion for deeper extraction (with chunking and RAG).
- 	Integrate with FAISS or Elasticsearch for related work search.
- 	Add confidence scores for extracted fields.


---

## Complete LangChain OutputParser Schema


Here is a complete LangChain OutputParser schema for the structured academic paper extraction prompt you requested. This uses the PydanticOutputParser for automatic validation and structured output, fully compatible with LangChain agents, chains, or RAG pipelines.

---

### ✅ Step 1: Define the Pydantic Model

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class AcademicPaperSummary(BaseModel):
    title: str
    year: Optional[str] = Field(description="Year of publication")
    authors: List[str]
    affiliations: List[str]
    objective: str
    method: str
    results: str
    datasets: List[str]
    models_or_tools: List[str]
    contributions: str
    comparison_to_prior_work: str
    evaluation_metrics: List[str]
    limitations: str
    application_domain: str
    paper_type: str  # e.g., 'survey', 'experimental', 'theoretical'
    code_or_data_link: Optional[str]
    citation_count: Optional[int]
    keywords: List[str]
    related_papers: List[str]
    lay_summary: str

```

---

### ✅ Step 2: Create the LangChain Output Parser

```python
from langchain.output_parsers import PydanticOutputParser

paper_summary_parser = PydanticOutputParser(pydantic_object=AcademicPaperSummary)

```

---

### ✅ Step 3: Integrate with Prompt Template

```python
from langchain.prompts import PromptTemplate

prompt = PromptTemplate(
    template="""
You are an AI assistant that extracts structured insights from academic papers for researchers.

Analyze the paper below and extract the following fields:
- Title
- Year
- Authors
- Affiliations
- Research Objective
- Method
- Key Results
- Datasets Used
- Models or Tools
- Contributions / Novelty
- Comparison to Prior Work
- Evaluation Metrics
- Limitations / Future Work
- Application Domain
- Paper Type
- Code or Data Link
- Citation Count
- Keywords
- Related Papers
- Lay Summary (for non-experts)

Return your output as a valid JSON matching this format:
{format_instructions}

--- Paper Start ---
Title: {paper_title}
Abstract: {paper_abstract}
--- Paper End ---
""",
    input_variables=["paper_title", "paper_abstract"],
    partial_variables={"format_instructions": paper_summary_parser.get_format_instructions()}
)
```

---

### ✅ Step 4: Use in a Chain

```python
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain

llm = ChatOpenAI(temperature=0, model="gpt-4")

chain = LLMChain(
    llm=llm,
    prompt=prompt,
    output_parser=paper_summary_parser
)

# Example usage
response = chain.run({
    "paper_title": "Efficient Transformers for Long Document Classification",
    "paper_abstract": "We propose a new transformer variant called LongFormer..."
})

# Structured output
print(response.dict())
```

### 🧠 Notes:

- 	You can extend the model to include full_text_chunks: List[str] if doing RAG-style extraction.
- 	This setup is compatible with LangGraph or tool-using agents that chain search → summarization.
- 	Add a validator if you want to ensure values like citation_count are non-negative or paper_type is in a list.


---

## A Complete Working Example of a Streamlit UI 


Here is a complete working example of a Streamlit UI that lets you:

1.	Upload a CSV or JSON file (or you can extend it to PDF/HTML parsing).
2.	Extract structured academic metadata using your LangChain LLMChain and OutputParser.
3.	Display the extracted fields in an interactive, user-friendly format.

---

### ✅ Features

- 	Upload a paper (title + abstract).
- 	Run extraction via LangChain (GPT or other model).
- 	Display the results as:
- 	Expandable cards
- 	JSON format (optional)
- 	Downloadable results


---

### 📁 File Structure

```text
academic_paper_summary_app/
├── app.py                   # Streamlit UI
├── parser.py                # OutputParser + Pydantic model
├── chain.py                 # LangChain chain setup
└── requirements.txt
```



---

### 📄 parser.py

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain.output_parsers import PydanticOutputParser

class AcademicPaperSummary(BaseModel):
    title: str
    year: Optional[str]
    authors: List[str]
    affiliations: List[str]
    objective: str
    method: str
    results: str
    datasets: List[str]
    models_or_tools: List[str]
    contributions: str
    comparison_to_prior_work: str
    evaluation_metrics: List[str]
    limitations: str
    application_domain: str
    paper_type: str
    code_or_data_link: Optional[str]
    citation_count: Optional[int]
    keywords: List[str]
    related_papers: List[str]
    lay_summary: str

parser = PydanticOutputParser(pydantic_object=AcademicPaperSummary)
```

---

### ⚙️ chain.py

```python
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from parser import parser

llm = ChatOpenAI(model="gpt-4", temperature=0)

prompt = PromptTemplate(
    template="""
You are a research assistant. Extract the following structured fields from the academic paper:

- Title, Year, Authors, Affiliations
- Research Objective
- Method
- Key Results
- Datasets
- Models or Tools
- Contributions / Novelty
- Comparison to Prior Work
- Evaluation Metrics
- Limitations
- Application Domain
- Paper Type
- Code/Data Link
- Citation Count
- Keywords
- Related Papers
- Lay Summary

Return as JSON with this format:
{format_instructions}

--- Paper Start ---
Title: {paper_title}
Abstract: {paper_abstract}
--- Paper End ---
""",
    input_variables=["paper_title", "paper_abstract"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

chain = LLMChain(llm=llm, prompt=prompt, output_parser=parser)
```

---

### 🖥️ app.py

``` python
import streamlit as st
from chain import chain

st.set_page_config(page_title="Academic Paper Extractor", layout="wide")
st.title("📄 Academic Paper Summary Extractor")

with st.sidebar:
    st.header("Upload Paper Info")
    uploaded_file = st.file_uploader("Upload a CSV or JSON file (title + abstract)", type=["csv", "json"])
    run_button = st.button("🚀 Extract Insights")

if run_button and uploaded_file:
    import pandas as pd
    import json

    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_json(uploaded_file)

        for idx, row in df.iterrows():
            with st.expander(f"📘 {row['title']}", expanded=False):
                with st.spinner("Extracting..."):
                    try:
                        response = chain.run({
                            "paper_title": row['title'],
                            "paper_abstract": row['abstract']
                        })

                        st.markdown("### 🧠 Summary")
                        st.markdown(f"**Objective**: {response.objective}")
                        st.markdown(f"**Method**: {response.method}")
                        st.markdown(f"**Results**: {response.results}")
                        st.markdown(f"**Contributions**: {response.contributions}")
                        st.markdown(f"**Datasets**: {', '.join(response.datasets)}")
                        st.markdown(f"**Tools**: {', '.join(response.models_or_tools)}")
                        st.markdown(f"**Metrics**: {', '.join(response.evaluation_metrics)}")
                        st.markdown(f"**Keywords**: {', '.join(response.keywords)}")
                        st.markdown(f"**Paper Type**: {response.paper_type}")
                        st.markdown(f"**Lay Summary**: {response.lay_summary}")

                        with st.expander("📊 Full Extracted JSON"):
                            st.json(response.dict())

                    except Exception as e:
                        st.error(f"Failed to extract paper: {e}")

    except Exception as e:
        st.error(f"Error loading file: {e}")
```

---

### 📦 requirements.txt

```text
streamlit
langchain>=0.1.15
openai
pydantic
pandas
```

---

### 🚀 To Run

1.	Set your OpenAI API key in .env or environment variable:

export OPENAI_API_KEY=your-key-here

2.	Run the app:

streamlit run app.py

Would you like to add:

- 	PDF upload and parsing?
- 	Multi-paper clustering and summarization?
- 	Download button for all extracted summaries?


---

## A Complete end-to-end Retrieval-Augmented Generation (RAG) Pipeline


Here’s a complete end-to-end Retrieval-Augmented Generation (RAG) pipeline using your structured academic paper summary prompt. This setup lets you:

---

✅ Upload academic papers (PDF, CSV, JSON, or plaintext)
✅ Ingest and chunk them into a vector store (FAISS or Chroma)
✅ Search semantically with a user query
✅ Use LLM to extract structured insights from the retrieved documents
✅ Display extracted metadata in structured format (JSON / UI)

---

### 📦 Architecture Overview

```plaintext
    [PDF / CSV / JSON Upload]
              ↓
    [Text Preprocessing + Chunking]
              ↓
        [Embedding Model]
              ↓
       [Vector Store (FAISS)]
              ↓
    [User Search Query (Natural Language)]
              ↓
      [Retriever fetches top-k chunks]
              ↓
 [LLM Prompt (Structured Summary Extraction)]
              ↓
      [LangChain OutputParser → JSON]
              ↓
         [Streamlit or API Output]

```

---

### 🧱 Components


#### 1. rag_config.py – Basic Config

```python
# rag_config.py
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader, PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import os

embeddings = OpenAIEmbeddings()

def load_and_chunk_docs(file_path: str) -> list[Document]:
    if file_path.endswith(".pdf"):
        loader = PyMuPDFLoader(file_path)
    else:
        loader = TextLoader(file_path)

    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    return splitter.split_documents(docs)

def build_vectorstore(documents: list[Document]) -> FAISS:
    return FAISS.from_documents(documents, embeddings)
```


---

#### 2. structured_prompt.py – Your LLM Prompt and Parser

```python
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from parser import AcademicPaperSummary  # Pydantic model from earlier
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain

parser = PydanticOutputParser(pydantic_object=AcademicPaperSummary)

llm = ChatOpenAI(model="gpt-4", temperature=0)

template = PromptTemplate(
    input_variables=["context"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    template="""
You are an AI academic research assistant. Analyze the provided academic content
and extract structured metadata as follows:

{format_instructions}

Context:
{context}
"""
)

rag_chain = LLMChain(
    llm=llm,
    prompt=template,
    output_parser=parser
)
```

---

#### 3. rag_runner.py – Full RAG Flow

```python
from rag_config import load_and_chunk_docs, build_vectorstore
from structured_prompt import rag_chain

def run_rag_pipeline(file_path: str, user_query: str):
    print("📄 Loading and chunking document...")
    docs = load_and_chunk_docs(file_path)
    
    print("🧠 Building vector store...")
    vs = build_vectorstore(docs)

    print("🔍 Performing semantic search...")
    results = vs.similarity_search(user_query, k=3)
    context = "\n\n".join([doc.page_content for doc in results])

    print("📝 Running LLM for structured summary...")
    structured_output = rag_chain.run({"context": context})

    return structured_output
```


---

#### 4. app.py – Streamlit UI


```python
import streamlit as st
from rag_runner import run_rag_pipeline

st.set_page_config(page_title="Academic RAG Summarizer", layout="wide")
st.title("📚 End-to-End RAG for Academic Paper Summarization")

uploaded_file = st.file_uploader("Upload a paper (PDF or TXT)", type=["pdf", "txt"])
query = st.text_input("Enter your search query (e.g., 'novel methods for protein folding')")

if uploaded_file and query:
    with open(f"./tmp_input.{uploaded_file.name.split('.')[-1]}", "wb") as f:
        f.write(uploaded_file.read())

    with st.spinner("Running RAG pipeline..."):
        try:
            result = run_rag_pipeline(f.name, query)
            st.success("✅ Extracted Paper Summary:")
            st.json(result.dict())
        except Exception as e:
            st.error(f"Error: {e}")
```

---

#### 5. requirements.txt

```text
streamlit
langchain>=0.1.15
openai
pydantic
faiss-cpu
PyMuPDF
```

---


### 🧠 Possible Next Features

- 	Add PDF metadata extraction (title, authors) automatically.
- 	Integrate citation graph + CoCitation retrieval for improved relevance.
- 	Store results in SQLite / JSONL for persistence.
- 	Support multi-paper summaries and clustering (group by topic or method).


Example input

```json
{
  "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
  "abstract": "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations by jointly conditioning on both left and right context in all layers. As a result, the pre-trained BERT model can be fine-tuned with just one additional output layer to create state-of-the-art models for a wide range of NLP tasks. BERT is conceptually simple and empirically powerful. It obtains new state-of-the-art results on eleven NLP tasks, including question answering and language inference, without substantial task-specific architecture modifications."
}
```

