## Reviewer locator


To build a Reviewer Locator that accurately recommends the best-suited experts to review a paper based on its title, abstract, and optionally full text, here’s the methodology:

---

### 🎯 Goal:

Given a new submission (title, abstract, etc.), find top experts who:

-	Work on similar topics (semantic match)
-	Have strong publication record (impact/quality)
-	Are not collaborators of the submitting authors (conflict avoidance)

---

### 🧠 Methodology: Reviewer Recommendation Pipeline


#### 1. Preprocessing (Paper Representation)

Extract the semantic representation of the input paper:
-	Input: title, abstract, keywords (optional: body, references)
-	Output: Dense embedding vector

✅ Best embeddings:
-	Specter2, SciBERT, OpenAI ada-002, Instructor, Cohere embeddings
-	Optional: Use BERTopic for topic-aware representation

---

#### 2. Candidate Author Pool (Retriever)


Option A: Pre-built Index (Efficient)

-	Index all authors with:
-	Top N most recent or relevant papers
-	Author profile embedding = avg of paper embeddings
-	Store in FAISS, Weaviate, or Elasticsearch

Option B: Real-time API Query (Slower, flexible)

-	Use OpenAlex, Semantic Scholar, or Lens to find top authors for similar papers using:
-	keyword/topic overlap
-	citations to similar papers
-	field tags (e.g., “Graph Neural Networks”)

---

#### 3. Ranking Criteria (Multi-Factor Scoring)


For each candidate author:


| Score            | Description                                                                                   |
|------------------|-----------------------------------------------------------------------------------------------|
| Topic Similarity | Cosine similarity between the input paper embedding and the candidate's top paper embeddings.  |
| Expertise Depth  | Number of papers the candidate has published in the same topic cluster (e.g., "multimodal learning"). |
| Recency          | Emphasis on recent activity—number of relevant papers published in the last 3–5 years.        |
| Impact           | Measures such as citation count, h-index, and journal/conference tier.                        |
| Novelty/Match    | Whether the candidate has worked on similar methods, datasets, or problems as the input paper.|
| Conflict Check   | Exclude collaborators or recent coauthors using a coauthorship network.                        |



✅ Final Reviewer Score Formula (Example)


```plaintext
ReviewerScore = 
    0.30 * TopicSimilarity +
    0.20 * ExpertiseDepth +
    0.15 * RecencyScore +
    0.15 * ImpactScore +
    0.10 * MethodMatch +
    0.10 * DatasetMatch
```


Output Format (Example JSON)

```json
[
  {
    "author_name": "Dr. Alice Smith",
    "affiliation": "MIT CSAIL",
    "topic_similarity": 0.91,
    "expertise_depth": 0.85,
    "recent_publications": 7,
    "h_index": 42,
    "impact_score": 0.72,
    "top_paper": {
      "title": "Contrastive Graph Neural Networks for Knowledge Distillation",
      "doi": "10.1234/xyz"
    }
  },
  ...
]
```

---

### 🧱 Technologies & Tools


| Component             | Tools                                                                 |
|-----------------------|----------------------------------------------------------------------|
| Embedding             | Specter, SciBERT, Instructor, OpenAI ada-002                         |
| Indexing & Search     | FAISS, Weaviate, Elasticsearch                                       |
| Metadata              | OpenAlex, Semantic Scholar, CrossRef                                 |
| Author Disambiguation | ORCID, OpenAlex ID, Coauthor Network                                 |
| Conflict Detection    | Graph-based author network, coauthorship matching                    |



### 🧪 Prototype Plan

1.	Input: title, abstract
2.	Compute embedding of input paper
3.	Retrieve top N authors using FAISS + paper embeddings
4.	Filter out conflicts (optional input: submitting authors)
5.	Compute scores and rank reviewers
6.	Return top reviewers with profile summary


---



## A Prototype for  Reviewer Locator Tool


Great! We’ll build a Reviewer Locator Tool using the following modular structure:

---

### 📁 Folder Structure


```plaintext
reviewer_locator/
│
├── main.py                  # Streamlit or CLI entry point
├── embedder.py              # Embeds paper title + abstract
├── indexer.py               # Builds or loads author-paper index (FAISS)
├── searcher.py              # Semantic search & filtering
├── scorer.py                # Reviewer scoring: topic match, expertise, impact
├── data_loader.py           # Pulls author-paper data from OpenAlex or Semantic Scholar
├── conflict_checker.py      # Filters collaborators if needed
├── example_query.json       # Sample paper title + abstract
└── requirements.txt
```


### ✅ Components to Build

1.	embedder.py:
    -	Use InstructorEmbedding or Specter to turn title+abstract into a dense vector.
2.	indexer.py:
    -	Build author-level index:
    -	Author profile = avg of their paper embeddings
    -	Store with FAISS
3.	searcher.py:
    -	Perform similarity search
    -	Return top N matching authors
4.	scorer.py:
    -	Calculate ReviewerScore using:
    -	Topic similarity
    -	Topical depth
    -	Impact (citations, h-index)
    -	Recency
    -	Dataset/method overlap (optional)
5.	main.py:
    -	Input: paper title + abstract
    -	Output: list of reviewer candidates with JSON + optional visualization



Embedder.py

```python
from InstructorEmbedding import INSTRUCTOR
import numpy as np

# Load once
model = INSTRUCTOR('hkunlp/instructor-large')

def embed_paper(title: str, abstract: str) -> np.ndarray:
    instruction = "Represent the scientific paper for finding related experts"
    text = title + " " + abstract
    embedding = model.encode([[instruction, text]])
    return embedding[0]
```            

Indexer.py

```python
import faiss
import numpy as np
import pickle

def load_faiss_index(index_path: str, metadata_path: str):
    index = faiss.read_index(index_path)
    with open(metadata_path, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata
```

Searcher.py


```python
import numpy as np
from typing import List, Tuple

def search_top_k(query_vec: np.ndarray, index, metadata, k=10) -> List[Tuple[dict, float]]:
    query_vec = np.array([query_vec]).astype("float32")
    D, I = index.search(query_vec, k)
    results = []
    for score, idx in zip(D[0], I[0]):
        author_info = metadata[idx]
        results.append((author_info, float(score)))
    return results
```

Scorer.py


```python
def score_author(author, topic_similarity):
    expertise_depth = author.get("topic_paper_count", 5)
    recent_papers = author.get("recent_publications", 3)
    h_index = author.get("h_index", 20)

    score = (
        0.30 * topic_similarity +
        0.20 * min(expertise_depth / 10, 1.0) +
        0.15 * min(recent_papers / 5, 1.0) +
        0.15 * min(h_index / 50, 1.0) +
        0.10 * author.get("method_overlap", 0.5) +
        0.10 * author.get("dataset_overlap", 0.5)
    )
    return score
```

Conflict_checker.py


```python
def filter_conflicts(candidates, submitting_authors: set):
    filtered = []
    for author, score in candidates:
        if author["author_id"] not in submitting_authors:
            filtered.append((author, score))
    return filtered
```

Main.py

```python
from embedder import embed_paper
from indexer import load_faiss_index
from searcher import search_top_k
from scorer import score_author
from conflict_checker import filter_conflicts

def recommend_reviewers(title, abstract, submitting_authors=None):
    vec = embed_paper(title, abstract)
    index, metadata = load_faiss_index("faiss_index.bin", "metadata.pkl")
    top_matches = search_top_k(vec, index, metadata, k=30)
    if submitting_authors:
        top_matches = filter_conflicts(top_matches, submitting_authors)

    results = []
    for author, sim in top_matches:
        score = score_author(author, sim)
        results.append({
            "author_name": author["name"],
            "affiliation": author["affiliation"],
            "author_id": author["author_id"],
            "top_paper": author["papers"][0]["title"],
            "topic_similarity": sim,
            "reviewer_score": score
        })

    results = sorted(results, key=lambda x: -x["reviewer_score"])
    return results[:10]

# Example usage
if __name__ == "__main__":
    paper_title = "Contrastive Learning for Multimodal Representation"
    paper_abstract = "We propose a novel contrastive learning framework for aligning audio and video embeddings..."
    reviewers = recommend_reviewers(paper_title, paper_abstract, submitting_authors={"0000-0002-1234-5678"})
    for r in reviewers:
        print(f"{r['author_name']} ({r['affiliation']}): score={r['reviewer_score']:.3f}")
```            

Moke_data_generator.py

```python
import numpy as np
import pickle
import faiss
import random

# Simulate 100 authors with mock metadata
def generate_mock_authors(n=100):
    authors = []
    for i in range(n):
        authors.append({
            "author_id": f"0000-0002-{i:04d}-{random.randint(1000,9999)}",
            "name": f"Author {i}",
            "affiliation": f"University {i % 10}",
            "h_index": random.randint(10, 80),
            "topic_paper_count": random.randint(3, 20),
            "recent_publications": random.randint(0, 8),
            "method_overlap": round(random.uniform(0, 1), 2),
            "dataset_overlap": round(random.uniform(0, 1), 2),
            "papers": [{"title": f"Sample Paper {i}", "year": 2020 + i % 5}]
        })
    return authors

# Generate random 768-dim vectors for authors
def generate_embeddings(n=100, dim=768):
    return np.random.rand(n, dim).astype("float32")

if __name__ == "__main__":
    authors = generate_mock_authors()
    embeddings = generate_embeddings(len(authors))

    # Save metadata
    with open("metadata.pkl", "wb") as f:
        pickle.dump(authors, f)

    # Build FAISS index
    index = faiss.IndexFlatL2(768)
    index.add(embeddings)
    faiss.write_index(index, "faiss_index.bin")

    print("â Mock data generated: metadata.pkl + faiss_index.bin")
```

streamlit_app.py

```python
import streamlit as st
from main import recommend_reviewers

st.set_page_config(page_title="Reviewer Recommender", layout="wide")

st.title("🔍 Reviewer Recommender System")

title = st.text_input("📄 Paper Title", "Contrastive Learning for Multimodal Representation")
abstract = st.text_area("🧠 Paper Abstract", 
    "We propose a novel contrastive learning framework for aligning audio and video embeddings..."
)

submitting_ids = st.text_input("✍️ Submitting Author IDs (comma-separated)", "0000-0002-0010-1234")

if st.button("🔎 Recommend Reviewers"):
    submitting_set = set(submitting_ids.strip().split(","))
    results = recommend_reviewers(title, abstract, submitting_set)
    
    if not results:
        st.warning("No suitable reviewers found.")
    else:
        st.success(f"Top {len(results)} recommended reviewers:")
        for idx, r in enumerate(results, 1):
            st.markdown(f"""
                **{idx}. {r['author_name']}**  
                📍 *{r['affiliation']}*  
                🧪 *Similarity:* {r['topic_similarity']:.2f} | 🧮 *Score:* **{r['reviewer_score']:.3f}**  
                📄 *Top Paper:* _{r['top_paper']}_  
                """)
```

---

##  A Complete Methodology and Implementation Recommendation


To efficiently index and retrieve authors based on top papers and build accurate profile embeddings, here’s a complete methodology and implementation recommendation, comparing Elasticsearch vs FAISS (or other vector DBs), with pros/cons and practical examples.

---

### ✅ GOAL

You want to:
1.	Index authors with their top N papers (recent or most relevant).
2.	Compute author profile embeddings based on these papers.
3.	Enable accurate, fast matching of input paper → best matching authors.

---

### 🔁 Step-by-Step Methodology


#### 1. Choose Top N Papers per Author

Selection strategy:
-	Recent papers → capture current research focus.
-	High citation/relevance → capture core expertise.
-	Filter by relevance to input topic using keyword/topic similarity.

```python
def select_top_n_papers(papers, n=5):
    papers = sorted(papers, key=lambda p: (p['year'], p['citations']), reverse=True)
    return papers[:n]
```

#### 2. Compute Author Profile Embedding

Each author profile = average of embeddings from selected N papers.


```python
import numpy as np

def compute_author_embedding(papers, embed_fn):
    paper_embeddings = [embed_fn(p['title'] + " " + p['abstract']) for p in papers]
    return np.mean(paper_embeddings, axis=0)
```


#### 3. Elasticsearch vs FAISS for Indexing


🧠 Option A: Use Elasticsearch (ES)

You can index each author with:

```json
{
  "author_id": "123",
  "name": "Alice Smith",
  "affiliation": "MIT",
  "top_papers": ["title1", "abstract1", "keywords1", ..., "titleN", "abstractN", "keywordsN"],
  "embedding": [0.12, 0.33, ..., 0.04]
}
```

✅ Flatten top_papers fields (titles/abstracts/keywords as array of strings) instead of nested objects — improves performance.

🔹 Why avoid nested in ES?
-	Slower due to nested doc lookups.
-	Harder to score relevance across multiple nested fields.
-	Keyword array or copy_to flattening is faster for search.

Recommended ES Mapping
```json
{
  "mappings": {
    "properties": {
      "author_id": { "type": "keyword" },
      "name": { "type": "text" },
      "top_papers_text": { "type": "text", "analyzer": "english" },
      "embedding": { "type": "dense_vector", "dims": 768, "index": true }
    }
  }
}
```

Scoring Strategy

Use hybrid:
-	BM25 over top_papers_text
-	Cosine similarity over embedding

Combine:

```json
"function_score": {
  "query": { "match": { "top_papers_text": "contrastive learning..." }},
  "script_score": {
    "script": {
      "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
      "params": { "query_vector": [0.12, 0.33, ...] }
    }
  }
}
```


🧪 Option B: Use FAISS or Vector DB (Weaviate, Qdrant, etc.)

-	Store author profile vectors in FAISS.
-	Use vector search (cosine or L2).
-	Attach metadata (author_id, name, top_paper, etc.) in a separate mapping file (e.g., pickle, SQLite, or Redis).

Best for high-speed similarity search without needing full ES stack.

---

### ⚖️ Tradeoffs


| Feature              | Elasticsearch                        | FAISS / Vector DB                |
|----------------------|--------------------------------------|----------------------------------|
| Text + Vector Search | ✅ Hybrid BM25 + dense                | ❌ Text fallback must be manual   |
| Scale                | ✅ Production-ready                   | ✅ For vector search only         |
| Update Frequency     | 🔸 Slower for frequent updates        | ✅ Fast                           |
| Author Metadata      | ✅ Fully indexed and queryable        | ❌ Must manage separately         |



### 🔍 Best Matching Strategy

1.	Embed input paper (title + abstract).
2.	Retrieve top-k authors:
    -	ES: use hybrid function_score query.
    -	FAISS: use cosine similarity over author vectors.
3.	Optional reranking:
    -	Score overlap in keywords, methods, datasets, topic distributions (via LDA or BERTopic).
    -	Boost by h-index or recency.

---

### 🛠️ Example Code: Build Author Index with FAISS


```python
import faiss
import numpy as np
import pickle

author_vectors = []
metadata = []

for author in all_authors:
    papers = select_top_n_papers(author['papers'])
    emb = compute_author_embedding(papers, embed_fn)
    author_vectors.append(emb)
    metadata.append({
        "id": author['author_id'],
        "name": author['name'],
        "affiliation": author['affiliation'],
        "top_paper": papers[0]['title']
    })

index = faiss.IndexFlatIP(768)
index.add(np.vstack(author_vectors))

faiss.write_index(index, "author_index.faiss")
with open("author_metadata.pkl", "wb") as f:
    pickle.dump(metadata, f)

```

### ✅ Summary: Recommended Best Practices



| Component         | Recommendation                                      |
|-------------------|-----------------------------------------------------|
| Top Papers        | Use top 5 recent or most relevant papers            |
| Profile Embedding | Average of selected paper embeddings (cached)       |
| Text Index        | Flatten keywords, title, and abstract into one field|
| Embedding Store   | Use FAISS or Elasticsearch dense_vector             |
| Matching          | Hybrid search: BM25 + embedding similarity          |
| Reranking         | Incorporate impact, topic match, novelty, and coauthor diversity |




---

## Algorithms for Best Matching 


Excellent question — the choice between averaging paper embeddings vs. using individual paper embeddings depends on your goals, data scale, and infrastructure.

Let’s break it down:

---

### ✅ Problem

Given a paper (title + abstract), find the best matching authors who are experts on similar topics.

---

### 🧠 Option 1: Author Profile = Average of Top-N Paper Embeddings

How it works:
-	Select top N representative papers per author (recent or high-impact).
-	Embed each paper (title + abstract).
-	Compute the average vector → this becomes the author’s profile embedding.
-	Match query paper embedding to author profiles.

✅ Pros:
-	Fast: Index once → fewer vectors to store (1 per author).
-	Simple to implement.
-	Works well if author has a focused research area.

❌ Cons:
-	May lose fine-grained specificity (e.g., author works in multiple subfields).
-	Author embedding can be diluted if papers are diverse.

---

### 🧠 Option 2: Store and Search Over Individual Paper Embeddings

How it works:
-	Store vector embedding for each paper (title + abstract).
-	At query time: embed input paper → search over all papers.
-	Retrieve top-matching papers → map to authors.

✅ Pros:
-	More accurate and fine-grained.
-	Works better when authors span multiple topics.

❌ Cons:
-	Requires more storage (1 embedding per paper).
-	Slightly slower: need to resolve paper-to-author at runtime.
-	More complex indexing (especially if you want to exclude conflicts).

---

### ✅ Recommended Strategy


| Use Case                         | Recommendation                                                      |
|-----------------------------------|---------------------------------------------------------------------|
| ⚡ Fast lookup, limited infra      | Average top-N embeddings per author                                 |
| 🎯 High accuracy, larger scale    | Index each paper separately and map results back to authors         |
| 🧠 Mixed: fast but accurate       | Hybrid: cluster papers per author, embed by topic                   |



### 🛠️ Best Practice (Hybrid)

-	Group each author’s papers by topic clusters (e.g., using BERTopic or spectral clustering on embeddings).
-	Average embeddings per topic cluster.
-	Store multiple profile vectors per author (1 per cluster).
-	At query time: match to closest topic-cluster vector → author.

This offers:

-	High accuracy (per-topic match)
-	Scalability (fewer vectors than all papers)
-	Explainability (why author X matches — their work on topic Y)

---

### 📊 Summary Table

| Strategy                      | Accuracy   | Speed      | Scalability | When to Use                                         |
|-------------------------------|------------|------------|-------------|-----------------------------------------------------|
| Avg of N papers per author    | Medium     | ✅ Fast    | ✅ Easy     | Lightweight systems or narrow research areas        |
| Index all paper embeddings    | ✅ High    | Slower     | ❌ Heavy    | Need best match accuracy (multi-topic authors)      |
| Author-topic cluster embeddings| ✅ High    | ✅ Fast    | ✅ Scalable | Best of both — accurate, scalable, and fast         |


---


## Filtered Semantic Search


Yes — filtered semantic search can significantly improve both performance and accuracy in your reviewer recommender system or paper matching engine. Here’s how and why:

---

### ✅ Why It Improves Performance

1.	Smaller Candidate Set = Faster Embedding Matching
    -	Instead of computing semantic similarity against millions of author embeddings, filtering (e.g., by field, topic, time, geography) can reduce candidates to hundreds or thousands, improving latency and throughput.
2.	Reduced Memory / Vector Store Load
    -	You avoid loading or querying a huge embedding index (FAISS, Elasticsearch, etc.) unnecessarily.
    -	This is critical in low-latency applications.

---


### ✅ Why It Improves Accuracy / Precision


1.	Topical Relevance
    -	Filtering by keywords, categories, or ontology (e.g., MeSH terms, ACM fields, MAG topics) ensures you’re only comparing to authors likely to be relevant.
    -	This avoids “false positive” matches from generalist authors or unrelated work with coincidental textual similarity.
2.	Recency / Domain Trends
    -	Filtering by recent activity ensures authors are actively publishing in the field, improving the match quality and reviewer suitability.
3.	Metadata-aware Matching
    -	Filters based on:
    -	Venue (e.g., only journals in AI, or exclude preprints)
    -	Author-level attributes (e.g., h-index > X, verified profiles)
    -	Institution (e.g., avoid same university or conflicts)
    -	These can drastically improve trustworthiness and fairness.

---

### 🔧 How to Implement Filtered Semantic Search (Best Practice)


| Step                      | Description                                                                                                 |
|---------------------------|-------------------------------------------------------------------------------------------------------------|
| 1. Metadata Filtering     | Apply structured filters (e.g., topic tags, domain, publication year) in Elasticsearch or your database before running vector search to reduce the candidate pool. |
| 2. Hierarchical Index     | Organize your FAISS or Elasticsearch indices by field or subdomain (e.g., NLP, bioinformatics) and query only the relevant index for the input paper. |
| 3. Hybrid Filtering       | Use a fast keyword or BM25 match to filter candidates, then rerank the filtered set using vector similarity for higher accuracy. |
| 4. Topic Embedding Filter | Embed the input paper's topic and compare it to precomputed author/topic cluster vectors to further narrow down candidates before detailed matching. |


#### 🧠 Example: Author Recommender Pipeline

seudo Steps:

1. Filter candidate authors by:
    - Field = "Computer Vision"
    - Last pub date > 2020
    - Institution != input author institution
    - Exclude known collaborators

2. Retrieve candidate author profiles (top N papers or topic embeddings)

3. Embed input paper title+abstract

4. Compute cosine similarity with each candidate (author vector = avg of paper vectors)

5. Rank top K authors by similarity


### ✅ Summary

| Benefit                | Filtered Semantic Search                                      |
|------------------------|--------------------------------------------------------------|
| 🔄 Faster Matching     | ✅ Yes — smaller candidate set                                |
| 🎯 Higher Precision    | ✅ Yes — domain-aligned                                       |
| ⚖️ Fairness Controls   | ✅ Yes — via metadata filtering                               |
| 🔍 Explainability      | ✅ Easier due to structured pre-filtering                     |



---


## A Complete Working Example



Great. Below is a complete working example of how to integrate filtered semantic search using Elasticsearch + FAISS reranking for a reviewer recommendation system.

---

### 🧠 Goal:

Given a paper (title + abstract), recommend authors who have published semantically similar work, filtered by field, recency, and conflict exclusion.

---

### 🔧 System Components:

-	Elasticsearch: metadata filter & initial BM25 retrieval
-	FAISS: semantic reranking based on paper embeddings
-	SentenceTransformers: to generate embeddings
-	Paper-author metadata index: links papers to authors

---

### 📁 Project Structure

```plaintext
reviewer_recommender/
├── main.py
├── data/
│   ├── authors.json
│   ├── papers.json
├── embedding/
│   └── embedder.py
├── index/
│   ├── elastic_index.py
│   └── faiss_index.py
├── search/
│   └── recommend.py

```


### embedding/embedder.py

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_text(text: str):
    return model.encode(text, normalize_embeddings=True)

```

### 🔍 index/elastic_index.py

```python

from elasticsearch import Elasticsearch

es = Elasticsearch()

def search_filtered_candidates(query, field, since_year):
    return es.search(index="papers", query={
        "bool": {
            "must": [
                {"multi_match": {
                    "query": query,
                    "fields": ["title^2", "abstract", "keywords"]
                }},
                {"term": {"field.keyword": field}},
                {"range": {"year": {"gte": since_year}}}
            ]
        }
    })["hits"]["hits"]
```


### index/faiss_index.py


```python

import faiss
import numpy as np
import pickle

# Load precomputed paper vectors and map to paper_id
index = faiss.read_index("data/faiss_papers.index")
with open("data/paper_id_map.pkl", "rb") as f:
    paper_id_map = pickle.load(f)  # index -> paper_id
with open("data/paper_to_author.json", "r") as f:
    paper_to_author = json.load(f)

def search_semantic_neighbors(query_vec, top_k=10):
    D, I = index.search(np.array([query_vec]), top_k)
    return [(paper_id_map[i], D[0][rank]) for rank, i in enumerate(I[0])]
```

### search/recommend.py

```python

from embedding.embedder import embed_text
from index.elastic_index import search_filtered_candidates
from index.faiss_index import search_semantic_neighbors

def recommend_authors(title, abstract, field="Computer Vision", since_year=2020):
    query = f"{title}. {abstract}"
    
    # Step 1: Initial filtered search from Elasticsearch
    candidates = search_filtered_candidates(query, field, since_year)
    candidate_ids = [c["_id"] for c in candidates]
    
    # Step 2: Embed input paper
    query_vec = embed_text(query)
    
    # Step 3: Semantic similarity via FAISS (reranking)
    ranked = search_semantic_neighbors(query_vec, top_k=50)

    # Step 4: Filter ranked papers based on candidate pool
    filtered_ranked = [(pid, score) for pid, score in ranked if pid in candidate_ids]
    
    # Step 5: Map to authors
    author_scores = {}
    for pid, score in filtered_ranked:
        for author in paper_to_author.get(pid, []):
            author_scores[author] = author_scores.get(author, 0) + score
    
    # Sort by total similarity
    sorted_authors = sorted(author_scores.items(), key=lambda x: -x[1])
    return sorted_authors[:10]
```


### Example Usage: main.py

```python

from search.recommend import recommend_authors

title = "Transformer-Based Vision Models for Medical Imaging"
abstract = "This paper proposes a new architecture combining CNN and ViT for medical image segmentation..."

authors = recommend_authors(title, abstract)
for author, score in authors:
    print(f"{author}: {score:.4f}")
```


### ✅ Benefits


| Feature                                      | Included? |
|-----------------------------------------------|-----------|
| Metadata filtering (domain, recency)          | ✅        |
| Full-text semantic reranking                  | ✅        |
| Multi-paper to multi-author mapping           | ✅        |
| Efficient at scale with FAISS + Elasticsearch | ✅        |
| Extendable with conflict filter, impact score | 🔜        |


### ➕ Optional Enhancements

-	Add conflict filter: exclude co-authors or same affiliation.
-	Use author-topic cluster embeddings.
-	Add novelty/impact/leadership weights in ranking.



