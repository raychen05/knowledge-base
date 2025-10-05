## Name Disambiguation


To support grant or author disambiguation, especially in large-scale academic systems, you’ll want to combine preprocessing, semantic understanding, structured metadata comparison, and clustering or classification techniques. Below is a practical overview of approaches you can use:


---

### 🔍 Author Disambiguation Support


✅ Common Challenges

-	Name ambiguity (e.g., “J. Smith” could refer to many people)
-	Variants (e.g., “John A. Smith” vs. “J. A. Smith”)
-	Affiliations and coauthors may change over time
-	Incomplete or noisy data in publication records

🧠 Disambiguation Signals

Use combinations of the following fields for probabilistic matching:
-	Full name, name variants
-	Email addresses
-	Affiliations
-	Coauthors
-	ORCID or researcher IDs
-	Publication venues and topics
-	Publication time and patterns


📦 Approaches

1. Rule-Based Matching
-	Normalize names
-	Compare coauthor sets
-	Use affiliation matching heuristics

2. Vector-Based Matching (Embedding)
-	Encode metadata (authors, coauthors, affiliations, topics) using a sentence transformer (e.g., all-mpnet-base-v2)
-	Use FAISS or Annoy to find nearest neighbors
-	Rerank with metadata similarity

3. Graph-Based Clustering
-	Build a coauthorship graph
-	Cluster based on structural similarity, e.g., Louvain or Chinese Whispers
-	Use additional node features: affiliation, topic distribution

4. Supervised Classification
-	Train on known labeled pairs of “same person” vs “different”
-	Features: name similarity, affiliation overlap, coauthor Jaccard, topic embedding similarity

5. ORCID Integration
-	Use ORCID IDs as gold data (for training or bootstrapping)

---

### 💰 Grant Disambiguation Support


✅ Common Challenges

-	Grants from different funders may have similar or overlapping names
-	Grant numbers are not standardized across agencies
-	Funders may have multiple name variants

🧠 Disambiguation Signals

-	Funder name and aliases
-	Grant number (standardized)
-	Associated PI name / institution
-	Award amount, start/end dates
-	Project title and abstract (textual match)
-	Program or funding mechanism (e.g., R01, ERC Starting)

📦 Approaches

1. Funder Name Normalization
-	Use an alias table (e.g., “NSF”, “National Science Foundation”)
-	Use fuzzy matching + embedding reranking

2. Grant ID + PI Name Matching
-	If grant number is available, match directly
-	Validate with PI name + institution

3. Textual Semantic Matching
-	Encode title + abstract using embeddings
-	Match against known grants from a curated database

4. Metadata-Based Clustering
-	Cluster by title + PI + time period
-	For noisy or duplicate records, choose canonical representative

---

### 🛠️ Tools & Libraries

-	FAISS or Annoy for approximate nearest neighbor search
-	Scikit-learn or HDBSCAN for clustering
-	Transformers (HuggingFace) for embedding generation
-	Dedupe.io (or dedupe library) for entity resolution
-	NetworkX for graph-based disambiguation
-	LangChain or LLMs for edge-case disambiguation and explanation

---


### ✅ Recommended Workflow


For author disambiguation:

1.	Preprocess names, affiliations, coauthors
2.	Compute embedding-based similarity
3.	Rerank using metadata heuristics
4.	Cluster or match to canonical author IDs (e.g., ORCID, institutional profiles)

For grant disambiguation:

1.	Normalize funder names
2.	Parse and validate grant numbers
3.	Use PI name and institution to aid match
4.	Apply LLM or embedding reranking for abstracts and titles


---


## A Working Prototype Structure


Great! Here’s a working prototype structure and key components for an Author & Grant Disambiguation System using embeddings, graph clustering, and optional LLM fallback.


---

### 🗂️ Repo Structure


```plaintext

author_grant_disambiguation/
├── data/
│   ├── authors.csv                # Raw author metadata
│   ├── grants.csv                 # Raw grant metadata
│   ├── funders_aliases.json       # Funder name aliases
├── scripts/
│   ├── preprocess.py              # Name/affiliation normalization
│   ├── embed.py                   # Embedding generation (authors, grants)
│   ├── search_faiss.py            # FAISS search setup
│   ├── cluster_authors.py         # Graph-based author clustering
│   ├── disambiguate_grants.py     # Grant ID + PI disambiguation logic
│   ├── llm_fallback.py            # LLM fallback for edge cases
├── models/
│   ├── faiss_index_authors.idx    # FAISS index for author embeddings
│   ├── faiss_index_grants.idx     # FAISS index for grants
├── utils/
│   ├── normalize.py               # Text normalization functions
│   ├── similarity.py              # Name/affiliation/cosine similarity
│   ├── graph_utils.py             # Graph clustering helpers
├── notebooks/
│   ├── evaluate_disambiguation.ipynb
├── requirements.txt
├── README.md

```

---

###  🔧 Core Functionality Overview


✅ Author Disambiguation Pipeline

1.	Preprocess:
-	Normalize names, coauthor sets, affiliations
-	Build a coauthor graph

2.	Embed:
-	Use sentence-transformers to embed names + metadata
-	Store in FAISS

3.	Search & Cluster:
-	Search for similar authors
-	Cluster via:
-	Affiliation + coauthor overlap
-	Graph clustering (networkx, louvain)

4.	LLM Fallback (Optional):
-	If similarity/confidence score is low
-	Use prompt:
“Do these two authors likely refer to the same researcher? Provide reasoning. Metadata: [..]”

---

### ✅ Grant Disambiguation Pipeline

1.	Normalize funder names using alias file
2.	Match by grant number (if structured)
3.	Validate by PI + institution
4.	Embed title + abstract and use FAISS or cosine similarity
5.	LLM Fallback (Optional) to resolve close calls (e.g. similar titles but different funders)


---

###🧠 Technologies Used


-	sentence-transformers (all-MiniLM, mpnet-base)
-	FAISS for nearest-neighbor
-	NetworkX for graph clustering
-	HuggingFace Transformers for fallback LLM
-	ORCID / GRID / ROR for canonical identifiers
-	OpenAI or LlamaIndex for reasoning fallback

---

### ✅ Sample LLM Prompt


```plaintext
You are an expert at academic author disambiguation.

Two author records:
Author A: "J. Smith", Affiliation: "MIT", Coauthors: ["A. Brown", "Y. Liu"], Field: "Machine Learning"
Author B: "John Smith", Affiliation: "Massachusetts Institute of Technology", Coauthors: ["Y. Liu"], Field: "AI"

Do these records refer to the same person? Explain why or why not.

```

---

Perfect — let’s build the full author and grant disambiguation system prototype directly in this chat.

---

### ✅ 1. requirements.txt

```plaintext
pandas
numpy
faiss-cpu
sentence-transformers
scikit-learn
networkx
fuzzywuzzy
python-Levenshtein
openai  # optional, for LLM fallback
```            


### ✅ 2. utils/normalize.py


```python
import re
from unidecode import unidecode

def normalize_name(name: str) -> str:
    name = unidecode(name.lower())
    name = re.sub(r'[^a-z0-9\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def normalize_affiliation(affil: str) -> str:
    return normalize_name(affil)
```



### ✅ 3. scripts/embed.py


```python
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_authors(df):
    texts = df["name"] + " | " + df["affiliation"].fillna("")
    embeddings = model.encode(texts.tolist(), show_progress_bar=True)
    return embeddings

def embed_grants(df):
    texts = df["title"] + " | " + df["abstract"].fillna("")
    embeddings = model.encode(texts.tolist(), show_progress_bar=True)
    return embeddings
```


#### ✅ 4. scripts/search_faiss.py


```python
import faiss
import numpy as np

def build_faiss_index(embeddings: np.ndarray):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index

def search_index(index, query_vec, top_k=5):
    distances, indices = index.search(np.array([query_vec]), top_k)
    return distances[0], indices[0]
```


#### ✅ 5. scripts/cluster_authors.py


```python
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def build_similarity_graph(embeddings, threshold=0.85):
    sim = cosine_similarity(embeddings)
    g = nx.Graph()
    for i in range(len(sim)):
        for j in range(i+1, len(sim)):
            if sim[i, j] > threshold:
                g.add_edge(i, j)
    return g

def cluster_graph(g):
    clusters = list(nx.connected_components(g))
    return clusters
```


### ✅ 6. scripts/disambiguate_grants.py


```python
from fuzzywuzzy import fuzz

def fuzzy_match_funder(name, aliases):
    for canonical, alias_list in aliases.items():
        for alias in alias_list:
            if fuzz.token_set_ratio(name.lower(), alias.lower()) > 90:
                return canonical
    return name

def match_grant_by_number(df, query_grant_number):
    match = df[df["grant_number"].str.lower() == query_grant_number.lower()]
    return match
```


### ✅ 7. scripts/llm_fallback.py


```python
import openai

openai.api_key = "YOUR_API_KEY"

def resolve_ambiguity_llm(author1, author2):
    prompt = f"""
Are these two authors the same person?

Author A: {author1}
Author B: {author2}

Consider names, affiliations, and coauthors. Return 'Yes' or 'No' and explain.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message['content']
```


### ✅ 8. scripts/preprocess.py


```python
import pandas as pd
from utils.normalize import normalize_name, normalize_affiliation

def preprocess_authors(df):
    df["name"] = df["name"].apply(normalize_name)
    df["affiliation"] = df["affiliation"].fillna("").apply(normalize_affiliation)
    return df

def preprocess_grants(df):
    df["grant_number"] = df["grant_number"].astype(str).str.lower()
    df["title"] = df["title"].fillna("")
    df["abstract"] = df["abstract"].fillna("")
    return df
```


### ✅ 9. notebooks/evaluate_disambiguation.ipynb


This notebook would load data, embed authors, search or cluster, and evaluate:

```python
# Load
import pandas as pd
from scripts.embed import embed_authors
from scripts.search_faiss import build_faiss_index, search_index
from scripts.cluster_authors import build_similarity_graph, cluster_graph

df = pd.read_csv("../data/authors.csv")
embeddings = embed_authors(df)
index = build_faiss_index(embeddings)

# Search example
query_vec = embeddings[0]
dists, idxs = search_index(index, query_vec)

print("Top matches:", df.iloc[idxs])

# Clustering
g = build_similarity_graph(embeddings)
clusters = cluster_graph(g)
print(f"Found {len(clusters)} author clusters")
```


### ✅ 10. scripts/grant_deduplicator.py — Grant Deduplication Logic

This deduplicates grants using funder name normalization, grant number, PI, and title similarity.

```python
import pandas as pd
from scripts.disambiguate_grants import fuzzy_match_funder
from scripts.embed import embed_grants
from scripts.search_faiss import build_faiss_index, search_index
from utils.normalize import normalize_name
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json

def deduplicate_grants(grants_df: pd.DataFrame, aliases_path: str, similarity_threshold=0.9):
    # Load funder aliases
    with open(aliases_path, "r") as f:
        funder_aliases = json.load(f)

    # Normalize funder names
    grants_df["funder_normalized"] = grants_df["funder"].apply(lambda x: fuzzy_match_funder(x, funder_aliases))
    grants_df["pi_name_normalized"] = grants_df["pi_name"].apply(normalize_name)

    # Embeddings
    embeddings = embed_grants(grants_df)
    index = build_faiss_index(embeddings)

    # Deduplicate by semantic match
    matches = []
    for i, emb in enumerate(embeddings):
        dists, idxs = search_index(index, emb, top_k=5)
        for dist, j in zip(dists, idxs):
            if i != j and cosine_similarity([emb], [embeddings[j]])[0][0] > similarity_threshold:
                matches.append((i, j))

    # Union-find style clustering
    from collections import defaultdict

    parent = list(range(len(grants_df)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[py] = px

    for i, j in matches:
        union(i, j)

    clusters = defaultdict(list)
    for i in range(len(grants_df)):
        clusters[find(i)].append(i)

    return list(clusters.values())  # list of index clusters
```


### ✅ 11. scripts/cli_runner.py — Command Line Runner

```python
import argparse
import pandas as pd
from scripts.preprocess import preprocess_authors, preprocess_grants
from scripts.embed import embed_authors, embed_grants
from scripts.search_faiss import build_faiss_index, search_index
from scripts.cluster_authors import build_similarity_graph, cluster_graph
from scripts.grant_deduplicator import deduplicate_grants

def run_author_disambiguation(path):
    df = pd.read_csv(path)
    df = preprocess_authors(df)
    embeddings = embed_authors(df)
    g = build_similarity_graph(embeddings)
    clusters = cluster_graph(g)
    print(f"🧠 Author clusters: {len(clusters)}")
    for i, c in enumerate(clusters[:5]):
        print(f"Cluster {i+1}: {[df.iloc[j]['name'] for j in c]}")
    return clusters

def run_grant_deduplication(path, aliases):
    df = pd.read_csv(path)
    df = preprocess_grants(df)
    clusters = deduplicate_grants(df, aliases)
    print(f"💰 Deduplicated grant clusters: {len(clusters)}")
    for i, c in enumerate(clusters[:5]):
        print(f"Cluster {i+1}: {[df.iloc[j]['title'] for j in c]}")
    return clusters

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["author", "grant"], required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--aliases", default="data/funders_aliases.json")

    args = parser.parse_args()

    if args.mode == "author":
        run_author_disambiguation(args.data)
    elif args.mode == "grant":
        run_grant_deduplication(args.data, args.aliases)
```

### ✅ 12. Example data/funders_aliases.json

```json
{
  "National Institutes of Health": ["NIH", "N.I.H.", "U.S. NIH"],
  "National Science Foundation": ["NSF", "N.S.F.", "National Sci Foundation"],
  "European Research Council": ["ERC", "E.R.C.", "EU ERC"]
}
```


### ✅ 13. Example CLI Usage


```bash
- Author disambiguation
python scripts/cli_runner.py --mode author --data data/authors.csv

-  Grant deduplication
python scripts/cli_runner.py --mode grant --data data/grants.csv --aliases data/funders_aliases.json
```


### ✅ 14. Sample README.md Snippet


#### 🔍 Author & Grant Disambiguation System

This prototype provides:

- Author disambiguation via embedding + coauthor clustering
- Grant deduplication via funder normalization + semantic matching
- FAISS + Sentence-Transformers + NetworkX
- Optional LLM fallback

#### 🛠 Setup

```bash
pip install -r requirements.txt
```

#### 🚀 Run

```bash
# Disambiguate authors
python scripts/cli_runner.py --mode author --data data/authors.csv

# Deduplicate grants
python scripts/cli_runner.py --mode grant --data data/grants.csv --aliases data/funders_aliases.json
```


#### 📦 Inputs

-	authors.csv: name, affiliation, coauthors
-	grants.csv: title, abstract, grant_number, funder, pi_name
-	funders_aliases.json: normalized funder aliases

#### ✨ Extending
-	Plug in ORCID, Crossref, Dimensions, or Web of Science APIs
-	Add LLM fallback for ambiguous edge cases


---

Would you like me to:

- ✅ Zip all this into a downloadable repo?
- 📦 Add more real data mock files?
- 🤖 Help you integrate it with Elasticsearch / LangChain?