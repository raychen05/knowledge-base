## Entity Matching


Yes, using vector semantic search is a good and efficient idea for matching ~20K organization or funder names, especially when the user input is messy: abbreviations, variants, typos, etc.

But to get high accuracy and speed, vector search should be used with normalization and optional hybrid techniques.

---

### ✅ Why Vector Search Helps


| Problem                        | How Vector Search Helps                                                                                  |
|---------------------------------|---------------------------------------------------------------------------------------------------------|
| Abbreviations                   | Learns semantic similarity (e.g., “NIH” ↔ “National Institutes of Health”)                             |
| Typos / Variants                | Embeddings are fuzzy, so “Stanford Univrsity” is still near “Stanford University”                      |
| Different languages/transliterations | Captures semantic similarity better than strict string matching                                 |



---

### ✅ Design Recommendations


#### 1. Normalize input + names before embedding

Yes, always normalize before vectorization:

Before embedding:
- Lowercase
- Strip special characters
- Replace synonyms (e.g., "Univ." → "University")
- Optional: stopwords removal ("of", "for", etc.)

This reduces embedding noise and improves recall dramatically.

---

#### 2. Optimal Vector Size for Org Name Matching


| Vector Size | Comment |
|-------------|---------|
| 384         | Good tradeoff for name-like strings; fast and compact (e.g., all-MiniLM-L6-v2) |
| 512–768     | Better accuracy for complex or multilingual inputs (e.g., bge-base, mpnet, e5-base) |
| 1024+       | Rarely needed for short org names; slower indexing and retrieval, minimal benefit |



✅ Recommended: 384 or 512 dimensions for this use case.

---

#### 3. Embedding Model Choices


| Model               | Pros                                 | Comment                                             |
|---------------------|--------------------------------------|-----------------------------------------------------|
| all-MiniLM-L6-v2    | Fast, small (384D)                   | Great baseline, very efficient for short names      |
| bge-base-en         | Strong semantic search (768D)         | Better for multilingual and variant-rich inputs     |
| e5-base / e5-small  | Good retrieval performance           | Optionally prepend: `query: <name>` for best results |



---

#### 4. Combine with Filtering or Exact Matching

For best performance and accuracy, combine:
- 	✅ Vector search (FAISS, Qdrant): Top-K candidates
- 	➕ Levenshtein / fuzzy match reranking on top-K (e.g., fuzzywuzzy, rapidfuzz)
- 	✅ Canonical DB: For ground truth names + aliases

---


### ✅ Optimal Matching Pipeline

```plaintext
graph TD;
    A[User Input Name] --> B[Normalize Text];
    B --> C[Generate Embedding];
    C --> D[FAISS/Qdrant Vector Search];
    D --> E[Top-K Candidates];
    E --> F[Rerank with Fuzzy Match];
    F --> G[Return Best Match + Canonical Name];
```


---

### ⏱️ Performance

- 	20K vectors is tiny — FAISS or Qdrant returns matches in <10ms even on CPU.
- 	Store all canonical names + known variants in metadata for filtering or deduplication.


---

### 🧪 Example

```plaintext
User input:
"UCLA Med Ctr"

Normalized:
"ucla medical center"

Embedding match → "University of California Los Angeles Medical Center"

Fuzzy score + metadata match confirms canonical ID.
```


---

### ✅ Final Recommendations


| Aspect                  | Recommendation                                             |
|-------------------------|-----------------------------------------------------------|
| Vector size             | 384 or 512                                                |
| Normalize before embedding | ✅ Yes                                                 |
| Embedding model         | all-MiniLM, bge-base, e5-base                             |
| DB size (20k)           | Ideal for FAISS/Qdrant                                    |
| Reranking               | Use fuzzy match on top-K vector results                   |
| Ground truth            | Keep canonical → variants map for validation              |



---

## Starter Module to Build an Organization/Funder Name Matcher


Great! Here’s a starter module to build an organization/funder name matcher using:

- 	✅ Text normalization
- 	✅ Embedding-based vector search (FAISS)
- 	✅ Optional fuzzy reranking
- 	✅ Canonical name resolution

---

### 🗂️ Project Structure

```plintext
org_name_matcher/
├── data/
│   └── org_names.csv              # Canonical names + variants
├── match/
│   ├── normalize.py               # Text normalization
│   ├── embed.py                   # Embedding model loader
│   ├── vector_index.py            # Build + query FAISS index
│   ├── rerank.py                  # Optional fuzzy reranking
│   └── matcher.py                 # Main match pipeline
├── app.py                         # Simple test runner
├── requirements.txt
```


📄 Example org_names.csv

```csv
canonical,variant
National Institutes of Health,NIH
Stanford University,Stanford Univ.
Stanford University,Stanford U
UCLA Medical Center,UCLA Med Ctr
Massachusetts Institute of Technology,MIT
```



---

### 🧼 normalize.py

```python
import re

def normalize_name(name: str) -> str:
    name = name.lower()
    name = re.sub(r'[^a-z0-9 ]+', '', name)
    name = re.sub(r'\buniv\b', 'university', name)
    name = re.sub(r'\bctr\b', 'center', name)
    name = re.sub(r'\bmed\b', 'medical', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name
```


---

### 🔢 embed.py

```python
from sentence_transformers import SentenceTransformer

_model = None

def get_embedder(model_name="all-MiniLM-L6-v2"):
    global _model
    if _model is None:
        _model = SentenceTransformer(model_name)
    return _model

def encode(texts):
    model = get_embedder()
    return model.encode(texts, normalize_embeddings=True)
```

---

### 📦 vector_index.py


```python
import faiss
import numpy as np
import pandas as pd
from .embed import encode

class OrgVectorIndex:
    def __init__(self):
        self.names = []
        self.index = None

    def build(self, name_list):
        self.names = name_list
        embeddings = encode(name_list)
        self.index = faiss.IndexFlatIP(embeddings.shape[1])
        self.index.add(embeddings.astype('float32'))

    def search(self, query: str, top_k=5):
        query_vec = encode([query])
        D, I = self.index.search(query_vec.astype('float32'), top_k)
        return [(self.names[i], float(D[0][j])) for j, i in enumerate(I[0])]
```

---

### 🔁 rerank.py (optional)


```python
from rapidfuzz import fuzz

def fuzzy_rerank(query, candidates, limit=3):
    return sorted(
        candidates,
        key=lambda x: fuzz.token_sort_ratio(query, x[0]),
        reverse=True
    )[:limit]
```

---

### 🔍 matcher.py

```python
import pandas as pd
from .normalize import normalize_name
from .vector_index import OrgVectorIndex
from .rerank import fuzzy_rerank

class OrgMatcher:
    def __init__(self, csv_path="data/org_names.csv"):
        df = pd.read_csv(csv_path)
        self.canon_map = {}
        all_names = []
        for _, row in df.iterrows():
            norm = normalize_name(row["variant"])
            self.canon_map[norm] = row["canonical"]
            all_names.append(norm)
        self.index = OrgVectorIndex()
        self.index.build(all_names)

    def match(self, user_input):
        norm = normalize_name(user_input)
        top_candidates = self.index.search(norm, top_k=10)
        reranked = fuzzy_rerank(norm, top_candidates)
        best = reranked[0][0] if reranked else top_candidates[0][0]
        return {
            "input": user_input,
            "normalized": norm,
            "match": best,
            "canonical": self.canon_map.get(best, best)
        }
```

---

### 🚀 app.py (Test runner)

```python
from match.matcher import OrgMatcher

if __name__ == "__main__":
    matcher = OrgMatcher()
    while True:
        name = input("\nEnter organization name: ")
        result = matcher.match(name)
        print("→ Match:", result["match"])
        print("→ Canonical:", result["canonical"])

```


---

### 📦 requirements.txt

```plaintext
sentence-transformers
faiss-cpu
pandas
rapidfuzz

streamlit
```


---

### 🧪 Example

```plaintext
Input: "UCLA Med Ctr"
→ Match: ucla medical center
→ Canonical: UCLA Medical Center

Input: "Stanford Univ"
→ Match: stanford university
→ Canonical: Stanford University

Input: "NIH"
→ Match: national institutes of health
→ Canonical: National Institutes of Health
```


---

### 🖼️ streamlit_app/app.py

```python
import streamlit as st
from match.matcher import OrgMatcher

# Initialize matcher
@st.cache_resource
def load_matcher():
    return OrgMatcher()

matcher = load_matcher()

st.set_page_config(page_title="Organization Name Matcher", layout="centered")
st.title("🏢 Organization Name Matcher")
st.markdown("""
Enter any organization or funder name.  
The system will normalize, match it using vector similarity, and return the canonical name.
""")

org_input = st.text_input("🔍 Enter organization/funder name", placeholder="e.g., NIH, Stanford Univ., UCLA Med Ctr")

if org_input:
    with st.spinner("Matching..."):
        result = matcher.match(org_input)
    
    st.markdown("### 🧾 Match Result")
    st.write(f"**Input:** `{result['input']}`")
    st.write(f"**Normalized:** `{result['normalized']}`")
    st.write(f"**Top Match:** `{result['match']}`")
    st.write(f"**Canonical:** `{result['canonical']}`")
```

---

### ✅ How to Run

```bash
cd org_name_matcher/
streamlit run streamlit_app/app.py
```

---

## Hybrid Normalization for Author Name Matcher


Great question — and author name matching is surprisingly hard due to:

- 	Varying input formats (e.g., “Li, Wei”, “Wei Li”, “W. Li”)
- 	Mixed language/character sets
- 	Abbreviations or initials
- 	Misspellings or alternate romanizations
- 	Order reversals (especially with East Asian names)

---

### ✅ Best, Most Accurate Approach: Hybrid Normalization + Vector Matching + Rules

The most accurate setup for matching free-text author names combines:
	1.	✅ Name normalization (handle order, initials, accents)
	2.	✅ Embedding-based semantic similarity
	3.	✅ Fuzzy matching on token order
	4.	✅ Canonical name DB (e.g., ORCID, institution-linked identities)
	5.	✅ Optional context-aware reranking (e.g., by paper, affiliation)

---

### 🧠 Core Design Strategy

🪄 1. Normalize Input

- 	Lowercase, remove punctuation
- 	Normalize initials: W. Li → Wei Li
- 	Standardize order: "Li, Wei" → "Wei Li" (or store both forms)
- 	Remove accents (e.g., “José Niño” → “jose nino”)
- 	Unicode normalization: 𝓦𝓮𝓲 𝓛𝓲 → Wei Li

---

🔍 2. Build Canonical Author DB

For each canonical author:
- 	Store:
- 	Full name (with variants, initials, romanizations)
- 	Normalized names
- 	ORCID (if available)
- 	Embeddings (optional)
- 	Context: papers, institution, topics

---

🧠 3. Embed Full Names (Optional)

Use sentence-transformers models fine-tuned for names or entity resolution:

| Model                    | Why Use                                         |
|--------------------------|-------------------------------------------------|
| all-MiniLM-L6-v2         | Fast and effective for short names              |
| bge-base / e5-base       | Strong general-purpose semantic embeddings      |
| nomic-embed-text-v1      | Handles name-like strings and variants well     |

Normalize and embed all author name variants in advance and index in FAISS / Qdrant.

---

🎯 4. Matching Pipeline

```plaintext
graph TD;
    A[User Input Name] --> B[Normalize Name];
    B --> C[Vector Search (Top-K)];
    C --> D[Fuzzy Match (Levenshtein / Token Sort)];
    D --> E[Rerank by Context (Affiliation / Coauthors / Topics)];
    E --> F[Return Canonical Author]

```

---


### 🔁 Examples



| Input       | Normalized | Matched Canonical             |
|-------------|------------|-------------------------------|
| "Li, Wei"   | "wei li"   | Wei Li (ORCID:0000-0001…)     |
| "W. Li"     | "wei li"   | Wei Li                        |
| "Li Wei"    | "wei li"   | Wei Li                        |
| "Weili"     | "wei li"   | Wei Li                        |
| "J García"  | "j garcia" | José García (normalized)       |




---

### ✅ Best Practice Summary



| Step                  | Tool / Method                                      |
|-----------------------|----------------------------------------------------|
| Normalization         | Custom Python + `unidecode`                        |
| Embedding (optional)  | SentenceTransformers + FAISS/Qdrant                |
| Fuzzy Matching        | `rapidfuzz.fuzz.token_sort_ratio`                  |
| Canonical Resolution  | Author DB + ORCID                                  |
| Reranking (optional)  | Context-based (institution, papers)                |


---

## A Starter Module Structure



Great — here’s a starter module structure for an accurate and efficient author name matcher using normalization, vector search, and fuzzy reranking:


### 🗂️ Project Structure

```plaintext
author_matcher/
│
├── normalize.py               # Author name normalization
├── embed_names.py             # Embed canonical author names
├── match_author.py            # Matching logic (FAISS + fuzzy reranking)
├── author_db.json             # Sample canonical author dataset
├── test_matcher.py            # Example test cases
└── README.md

```

---

### 🔧 1. normalize.py

```python
import re
import unidecode

def normalize_name(name: str) -> str:
    name = unidecode.unidecode(name)  # Remove accents
    name = name.lower()
    name = re.sub(r'[^\w\s]', '', name)  # Remove punctuation
    tokens = name.split()
    # Reorder if comma used: "Li, Wei" → "Wei Li"
    if ',' in name:
        tokens = tokens[::-1]
    return ' '.join(tokens).strip()
```


---

###🔧 2. embed_names.py

```python
from sentence_transformers import SentenceTransformer
import faiss
import json

model = SentenceTransformer('all-MiniLM-L6-v2')

def load_author_db(path="author_db.json"):
    with open(path) as f:
        return json.load(f)

def build_faiss_index(authors):
    names = [normalize_name(a["name"]) for a in authors]
    embeddings = model.encode(names)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index, names
```

---

### 🔧 3. match_author.py

```python
from normalize import normalize_name
from embed_names import model
from rapidfuzz import fuzz

def match_author(query, index, names, authors, top_k=5):
    query_norm = normalize_name(query)
    query_vec = model.encode([query_norm])
    D, I = index.search(query_vec, top_k)

    candidates = [(i, fuzz.token_sort_ratio(query_norm, normalize_name(authors[i]["name"]))) for i in I[0]]
    candidates.sort(key=lambda x: -x[1])  # Sort by fuzzy match score

    best_idx, best_score = candidates[0]
    return authors[best_idx], best_score
```


---

### 🔧 4. author_db.json (Example Canonical DB)


```json
[
  {"id": "0001", "name": "Wei Li", "orcid": "0000-0001-2345-6789"},
  {"id": "0002", "name": "David Smith", "orcid": "0000-0002-9876-5432"},
  {"id": "0003", "name": "José García", "orcid": "0000-0003-2222-3333"}
]
```

---

### 🧪 5. test_matcher.py

```python
from embed_names import load_author_db, build_faiss_index
from match_author import match_author

authors = load_author_db()
index, names = build_faiss_index(authors)

test_queries = ["W. Li", "Li Wei", "Jose Garcia", "D. Smith"]

for query in test_queries:
    match, score = match_author(query, index, names, authors)
    print(f"Input: {query} → Match: {match['name']} (Score: {score})")
```

---

### ✅ Output Example

```plaintext
Input: W. Li → Match: Wei Li (Score: 100)
Input: Li Wei → Match: Wei Li (Score: 96)
Input: Jose Garcia → Match: José García (Score: 94)
```

📈 Next Steps

You can extend this with:
- 	ORCID lookup fallback
- 	Institutional context (e.g., paper or coauthor matching)
- 	Author cluster embeddings (average of paper vectors)
- 	Fast search using Qdrant with metadata filters


---

## Hybrid Author Name Matching


For high-accuracy author name matching, especially in noisy real-world data (free text inputs, mixed name order, typos, variants), a hybrid AI-powered approach combining semantic similarity, context reasoning, and graph features is optimal. Here’s an advanced architecture:

---

### ✅ Overview: Hybrid Author Name Matching Pipeline


```plaintext
Input Query (Free Text Name, Optional Affiliation)
       ↓
[1] Name Normalization & Parsing
       ↓
[2] Candidate Generation (Fast Filter)
       ↓
[3] Semantic Embedding Matching (Name + Context)
       ↓
[4] Contextual Reranking (Affiliation, ORCID, Topics, Coauthors)
       ↓
[5] Disambiguation via Graph Reasoning or LLM
       ↓
Output: Best Canonical Author Match
```


---

### 🔍 1. Normalization & Parsing

- 	Strip punctuation, accents, common suffixes (Dr., Prof.)
- 	Handle order permutations: “Li Wei”, “Wei Li”, “W. Li”
- 	Named entity recognition (NER) to isolate person names

📦 Tools:
- 	nameparser, unidecode, spaCy, or custom rules

---

### ⚡ 2. Candidate Generation (Fast Filters)

Reduce 20M authors → top-K candidates using:

- 	FAISS or Qdrant over normalized name embeddings
- 	Optional metadata filters:
- 	Institutional name (if provided)
- 	Country, affiliation, coauthor match

📦 Embedding Model:
- 	all-MiniLM-L6-v2 or e5-base-v2 (trained for entity search)
- 	Embed name variants + context like:


f"Author: Wei Li | Affiliation: Tsinghua"


---

### 🧠 3. Semantic Matching (Vector Embeddings)

Use hybrid embedding similarity:

- 	Name-only vector: for direct match
- 	Contextual vector: average of top N papers (title + abstract)
- 	Combine both for matching:

```plaintext
sim = α * cosine(name_vector, query_vector) + (1 - α) * cosine(paper_vector, query_topic_vector)
```
🔁 α balances name vs topic similarity.

---

### 📌 4. Contextual Reranking

Improve confidence by reranking top matches using:

a. Affiliation Matching
- 	Normalize and compare affiliation similarity (Jaccard or fuzzy)

b. ORCID Lookup
- 	Lookup known aliases or coauthors tied to ORCID

c. Topical Profile Matching
- 	Compute topic embeddings from author’s recent papers
- 	Embed query abstract or keywords and match topic vector

d. Coauthor Graph Overlap
- 	Graph score = # of shared coauthors / total known coauthors

---

### 🧠 5. LLM-Assisted Disambiguation (Optional)

Use an LLM like GPT or Claude for fine-grained decisions:

```yaml
prompt = f"""
You are matching author identities. Given this query:

Input Name: "W. Li"
Institution Hint: "Stanford"
Field: "Machine Learning"

Top Candidates:
1. Wei Li, Stanford, ORCID: xxxx
2. Wenhao Li, Berkeley, ORCID: yyyy
3. Wei Li, Cambridge, ORCID: zzzz

Who is most likely the correct match and why?
"""


Use this to justify or confirm ambiguous match decisions.
```

---

### 🕸️ 6. (Optional) Graph-Based Reasoning

Use an author-paper-coauthor graph:

- 	Nodes: Authors, Papers
- 	Edges: Coauthor, Institution, Authorship
- 	Use graph similarity (e.g., Personalized PageRank) to improve confidence.

📦 Tools: Neo4j, NetworkX, Deep Graph Library (DGL)

---

### 🧪 Evaluation Metrics

| Metric                | Purpose                                                         |
|-----------------------|-----------------------------------------------------------------|
| Top-1 Accuracy        | Measures how often the top returned match is correct            |
| Mean Reciprocal Rank (MRR) | Evaluates ranking quality across all candidate matches     |
| Disambiguation F1     | Assesses accuracy when multiple authors share the same name     |
| ORCID Match Rate      | Precision of matches when ORCID fallback is used                |


---

### 🧰 Tool Stack Recommendation


| Component      | Tools/Frameworks                                  |
|----------------|---------------------------------------------------|
| Normalization  | `unidecode`, `regex`, `nameparser`                |
| Embedding      | `sentence-transformers`, `e5`, `cohere`           |
| Vector Search  | `FAISS`, `Qdrant`                                 |
| Fuzzy Match    | `RapidFuzz`                                       |
| Graph Reasoning| `Neo4j`, `NetworkX`                               |
| LLM Reranker   | `GPT-4o`, `Claude 3`                              |
| Optional UI    | `Streamlit`, `Gradio`                             |


---


## high-level Structure for Hybrid Author Name Matching


Great — here’s a high-level structure for the modular hybrid author name matching system you can build on.

---

### 🧱 Folder Structure

```plaintext
author_matcher/
├── data/
│   ├── authors.csv                # Canonical author list: name, ID, ORCID, affiliation, papers
│   ├── papers.csv                 # Paper metadata: title, abstract, authors, topics
│   └── embeddings/                # Precomputed vectors (author, papers, etc.)
├── embeddings/
│   └── embedder.py               # Sentence-transformer or E5 embedding wrapper
├── graph/
│   └── author_graph.py           # Author-paper-coauthor graph + similarity methods
├── llm/
│   └── disambiguator.py          # Optional LLM disambiguation module
├── matcher/
│   ├── normalize.py              # Name normalization + variants
│   ├── vector_search.py          # FAISS/Qdrant vector search
│   ├── reranker.py               # Affiliation, ORCID, paper/topic, coauthor matching
│   └── match_pipeline.py         # Main match flow: normalize → search → rerank → disambiguate
├── ui/
│   └── streamlit_app.py          # Optional demo UI
├── tests/
│   └── test_pipeline.py
└── main.py                       # Entrypoint or API
```


---

### 🧠 Core Matching Pipeline

match_pipeline.py

```python
from matcher.normalize import normalize_name
from matcher.vector_search import vector_search_candidates
from matcher.reranker import rerank_with_context
from llm.disambiguator import resolve_with_llm

def match_author(input_name, affiliation_hint=None, paper_text=None, use_llm=True):
    norm = normalize_name(input_name)
    
    candidates = vector_search_candidates(norm, affiliation_hint)
    reranked = rerank_with_context(candidates, input_name, affiliation_hint, paper_text)
    
    if use_llm and reranked["ambiguous"]:
        final = resolve_with_llm(input_name, affiliation_hint, paper_text, reranked["top_k"])
    else:
        final = reranked["top_k"][0]
    
    return {
        "input": input_name,
        "normalized": norm,
        "match": final["canonical_name"],
        "score": final["score"],
        "orcid": final.get("orcid"),
        "confidence": final.get("confidence_reasoning"),
    }
```


---

### ✅ Components to Fill

normalize.py
- 	Lowercase, remove punctuation/diacritics
- 	Reorder first/last names
- 	Generate common variants

vector_search.py
- 	Use FAISS or Qdrant
- 	Combine:
- 	Author name embeddings
- 	Optional topic/context embeddings (average of N paper vectors)

reranker.py
- 	Combine multiple signals:
- 	Affiliation match (fuzzy)
- 	ORCID match
- 	Topic similarity
- 	Coauthor overlap (via graph)

author_graph.py
- 	Use NetworkX or Neo4j
- 	Compute coauthor overlap, path distance, pagerank around candidates

disambiguator.py (LLM)
- 	Provide prompt template for GPT/Claude
- 	Rerank/resolve from top-K candidates

---

🔌 Optional: Add FastAPI or Streamlit
- 	Streamlit UI: streamlit_app.py
- 	FastAPI endpoint: POST /match_author

---

🧪 Sample Author Query

