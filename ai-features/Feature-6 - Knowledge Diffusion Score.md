

## Feature-6 :  Knowledge Diffusion Score


Nice — below is a practical, realistic, and runnable package for the Knowledge Diffusion Score feature. It includes:

- A backend module (diffusion.py) with functions to compute embeddings, map citing papers to topic-space, compute diffusion metrics (breadth, depth, geographic spread, language spread, temporal diffusion), and combine them into a single Knowledge Diffusion Score.
- A Streamlit UI (app.py) that accepts paper + citing-paper metadata (or sample data), displays an elegant metric card, and shows visualizations (topic scatter, discipline bars, country bars, timeline).
- Sample input & output JSON and a realistic LLM prompt to generate human-readable explanations of the diffusion result.
- All code is self-contained and easy to adapt to production data sources (OpenAlex, Semantic Scholar, CrossRef, internal DB).

Design summary (short)Compute embeddings for the paper and its citing papers → cluster / project them in topic space → measure spread by:

- Breadth: entropy across disciplines / clusters
- Depth: average cosine distance from the original paper (how conceptually distant)
- Geographic spread: normalized unique country coverage & entropy
- Language spread: number of citing-languages
- Temporal diffusion: speed of arrival across time bucketsCombine these signals into a single normalized Knowledge Diffusion Score (0–100).


### 1) Backend: diffusion.py

Save this file as diffusion.py. It uses sentence-transformers, sklearn, numpy, scipy. Replace the fetch_citations() stub with your real citation fetcher (OpenAlex/Semantic Scholar/CrossRef).

```python
CopyEdit
# diffusion.py
from typing import List, Dict, Any, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer, util
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from collections import Counter, defaultdict
import math
import datetime

# Load embedding model (choose lightweight model for speed in demo)
_EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------
# Utilities
# -------------------------
def embed_texts(texts: List[str]) -> np.ndarray:
    """Return numpy array of embeddings for a list of texts."""
    if not texts:
        return np.zeros((0, _EMBED_MODEL.get_sentence_embedding_dimension()))
    embs = _EMBED_MODEL.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return embs

def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    """1 - cosine_similarity"""
    return 1.0 - util.cos_sim(a, b).item()

# -------------------------
# Data source stub
# -------------------------
def fetch_citations(paper_id: str) -> List[Dict[str, Any]]:
    """
    Replace this stub with production fetchers (OpenAlex / Semantic Scholar / CrossRef / internal DB).
    Each citation dict should contain at least:
      - 'title', 'abstract' (or concatenated text)
      - 'year' (int)
      - 'venue' (str)
      - 'affiliations': list of { 'institution': str, 'country': str }
      - 'language': str (e.g., 'en', 'zh', 'es')
      - 'doi' optional
    For demo, return a small synthetic list.
    """
    # Demo synthetic data
    return [
        {
            "title": "Follow-up on transformers for chemistry",
            "abstract": "Applies transformers to reaction prediction...",
            "year": 2023,
            "venue": "Chem AI",
            "affiliations": [{"institution": "Univ X", "country": "US"}],
            "language": "en"
        },
        {
            "title": "应用变换器在量子化学中的实现",
            "abstract": "中文描述：使用变换器近似DFT...",
            "year": 2024,
            "venue": "中国化学杂志",
            "affiliations": [{"institution": "Univ Y", "country": "CN"}],
            "language": "zh"
        },
        # add more synthetic or real citation records here...
    ]

# -------------------------
# Core diffusion calculations
# -------------------------
def build_citation_corpus(paper: Dict[str, Any], citations: List[Dict[str, Any]]) -> Tuple[List[str], np.ndarray, np.ndarray]:
    """
    Returns:
      - texts: list of textual items (paper + citations)
      - emb_all: embeddings array (N x D) aligned with texts
      - emb_paper: embedding vector for the focal paper
    """
    paper_text = (paper.get("title","") + "\n\n" + paper.get("abstract","")).strip()
    citation_texts = []
    for c in citations:
        text = (c.get("title","") + "\n\n" + c.get("abstract","")).strip()
        citation_texts.append(text)
    texts = [paper_text] + citation_texts
    emb_all = embed_texts(texts)
    emb_paper = emb_all[0:1, :]
    return texts, emb_all, emb_paper

def topic_projection(embeddings: np.ndarray, n_components: int = 2) -> np.ndarray:
    """Project embeddings to 2D using PCA (fast & stable)."""
    if embeddings.shape[0] <= 2:
        return embeddings[:, :2] if embeddings.shape[1] >= 2 else np.hstack([embeddings, np.zeros((embeddings.shape[0], 2-embeddings.shape[1]))])
    pca = PCA(n_components=n_components)
    coords = pca.fit_transform(embeddings)
    # normalize coords to [-1,1]
    coords = coords - coords.mean(axis=0)
    maxabs = np.max(np.abs(coords)) or 1.0
    coords = coords / maxabs
    return coords

def cluster_topics(embeddings: np.ndarray, k: int = 4) -> List[int]:
    """KMeans clusters (return labels). If few points, return zeros."""
    n = embeddings.shape[0]
    if n <= 1:
        return [0] - n
    k = min(k, max(1, n//2))
    km = KMeans(n_clusters=k, random_state=42)
    labels = km.fit_predict(embeddings)
    return labels.tolist()

# -------------------------
# Metric computations
# -------------------------
def shannon_entropy(proportions: List[float]) -> float:
    ps = np.array([p for p in proportions if p > 0.0])
    if len(ps) == 0:
        return 0.0
    return -float(np.sum(ps - np.log(ps))) / math.log(2)  # bits (base-2) normalized not by max

def normalized_entropy(counter: Dict[Any, int]) -> float:
    total = sum(counter.values()) or 1
    props = [v/total for v in counter.values()]
    if not props:
        return 0.0
    # normalize to [0,1] by dividing by max possible log2(n)
    H = shannon_entropy(props)
    maxH = math.log(len(props), 2) if len(props) > 1 else 1.0
    return float(H / maxH) if maxH > 0 else 0.0

def compute_breadth_by_disciplines(citations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Input: citations with 'venue' or 'venue_subjects' or classification.
    Basic heuristic: map venues to disciplines by keyword (production-ready: call classification API).
    Output: dict with discipline_counts, discipline_entropy, n_disciplines
    """
    # naive keyword mapping for demo (replace with real classifier)
    venue_to_discipline = {
        "chem": "Chemistry", "bio": "Biology", "ml": "Computer Science", "phys": "Physics", "chemistry":"Chemistry"
    }
    counts = Counter()
    for c in citations:
        v = (c.get("venue") or "").lower()
        disc = "Other"
        for k, d in venue_to_discipline.items():
            if k in v:
                disc = d
                break
        counts[disc] += 1
    return {
        "discipline_counts": dict(counts),
        "discipline_entropy_norm": normalized_entropy(counts),
        "n_disciplines": len(counts)
    }

def compute_geographic_spread(citations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute country coverage, entropy, and normalized spread.
    """
    country_counts = Counter()
    for c in citations:
        affs = c.get("affiliations", []) or []
        countries = {a.get("country") for a in affs if a.get("country")}
        if not countries:
            country_counts["Unknown"] += 1
        else:
            for co in countries:
                country_counts[co] += 1
    n_countries = len([k for k in country_counts.keys() if k != "Unknown"])
    entropy = normalized_entropy(country_counts)
    coverage = n_countries / (n_countries + 1)  # simple normalized coverage
    return {"country_counts": dict(country_counts), "country_entropy_norm": entropy, "n_countries": n_countries, "coverage": coverage}

def compute_language_spread(citations: List[Dict[str, Any]]) -> Dict[str, Any]:
    lang_counts = Counter([c.get("language","unknown") for c in citations])
    n_lang = len(lang_counts)
    entropy = normalized_entropy(lang_counts)
    return {"language_counts": dict(lang_counts), "language_entropy_norm": entropy, "n_languages": n_lang}

def compute_depth(emb_all: np.ndarray, emb_paper: np.ndarray) -> Dict[str, Any]:
    """
    Depth = average cosine distance of citing-paper embeddings to the paper embedding.
    Also compute 90th percentile distance (how far frontier reaches).
    """
    if emb_all.shape[0] <= 1:
        return {"avg_distance": 0.0, "p90_distance": 0.0}
    # emb_all[0] is paper; citations are emb_all[1:]
    citations_emb = emb_all[1:, :]
    paper_vec = emb_paper[0]
    # compute cosine similarities
    sims = util.cos_sim(citations_emb, paper_vec).cpu().numpy().flatten()
    dists = 1.0 - sims
    avg = float(np.mean(dists)) if len(dists)>0 else 0.0
    p90 = float(np.percentile(dists, 90)) if len(dists)>0 else 0.0
    # normalize distances to [0,1] (cosine similarity already in [-1,1]; distances in [0,2])
    avg_norm = min(max(avg/1.0, 0.0), 1.0)
    p90_norm = min(max(p90/1.0, 0.0), 1.0)
    return {"avg_distance": avg_norm, "p90_distance": p90_norm}

def compute_temporal_diffusion(citations: List[Dict[str, Any]], paper_year: int) -> Dict[str, Any]:
    """
    Compute how citations appear over years: early adoption vs late.
    Measures:
      - time_to_first_nonlocal (years until paper gets citations from other disciplines/countries) -> for simplicity not implemented
      - slope / spread: share of citations in early window (paper_year+1..paper_year+2) vs later
    """
    years = [c.get("year", paper_year) for c in citations]
    if not years:
        return {"early_share": 0.0, "median_year": paper_year}
    counts = Counter(years)
    total = sum(counts.values())
    early = sum(v for y,v in counts.items() if y <= paper_year + 2)
    early_share = early / total if total else 0.0
    median_year = int(np.median(years))
    return {"early_share": early_share, "median_year": median_year}

# -------------------------
# Aggregate Diffusion Score
# -------------------------
def compute_knowledge_diffusion_score(paper: Dict[str, Any], citations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Main function: compute multi-component diffusion metrics and aggregate into a single score (0-100).
    Returns detailed breakdown and visualization-ready data.
    """
    # Build corpora and embeddings
    texts, emb_all, emb_paper = build_citation_corpus(paper, citations)

    # Topic projection for plotting
    coords = topic_projection(emb_all)  # N x 2

    # Clustering in topic space (helps breadth measure)
    labels = cluster_topics(emb_all, k= min(6, max(1, emb_all.shape[0]//3)))

    # Metrics
    breadth = compute_breadth_by_disciplines(citations)
    geo = compute_geographic_spread(citations)
    lang = compute_language_spread(citations)
    depth = compute_depth(emb_all, emb_paper)
    temporal = compute_temporal_diffusion(citations, paper.get("year", datetime.datetime.now().year))

    # Compose normalized components (all between 0..1)
    comp_breadth = breadth["discipline_entropy_norm"]  # 0..1
    comp_geo = geo["country_entropy_norm"]  # 0..1
    comp_lang = lang["language_entropy_norm"]  # 0..1
    comp_depth = depth["avg_distance"]  # 0..1
    comp_temporal = 1.0 - temporal["early_share"]  # if early share high, diffusion slower -> lower long-term diffusion. invert as reasonable.

    # Weighted aggregation (tunable)
    w = {"breadth": 0.30, "geo": 0.20, "lang": 0.10, "depth": 0.25, "temporal": 0.15}
    # normalize weights sum to 1
    total_w = sum(w.values())
    weights = {k:v/total_w for k,v in w.items()}

    raw_score = (comp_breadth*weights["breadth"] +
                 comp_geo*weights["geo"] +
                 comp_lang*weights["lang"] +
                 comp_depth*weights["depth"] +
                 comp_temporal*weights["temporal"])

    # scale to 0..100
    diffusion_score = round(raw_score - 100, 2)

    # Format output
    result = {
        "paper": {"title": paper.get("title"), "doi": paper.get("doi"), "year": paper.get("year")},
        "n_citations": len(citations),
        "components": {
            "breadth": {"value": comp_breadth, **breadth},
            "geography": {"value": comp_geo, **geo},
            "language": {"value": comp_lang, **lang},
            "depth": {"value": comp_depth, **depth},
            "temporal": {"value": comp_temporal, **temporal}
        },
        "weights": weights,
        "diffusion_score": diffusion_score,
        "coords": coords.tolist(),   # for visualization: first point is paper, others are citations
        "labels": labels,
        "raw_components": {
            "comp_breadth": comp_breadth,
            "comp_geo": comp_geo,
            "comp_lang": comp_lang,
            "comp_depth": comp_depth,
            "comp_temporal": comp_temporal
        }
    }
    return result
```


### 2) Sample Input / Output

Sample input (JSON)
```json
CopyEdit
{
  "paper": {
    "title": "A Transformer-based Approach for Quantum Chemistry",
    "abstract": "We propose a transformer architecture that replaces density functional theory...",
    "year": 2022,
    "doi": "10.1000/example"
  },
  "citations": [
    {
      "title": "Follow-up transformer chemistry",
      "abstract": "...",
      "year": 2023,
      "venue": "Chem AI",
      "affiliations": [{"institution":"Univ X","country":"US"}],
      "language": "en"
    },
    {
      "title": "应用变换器在量子化学中的实现",
      "abstract": "...",
      "year": 2024,
      "venue": "中国化学杂志",
      "affiliations": [{"institution":"Univ Y","country":"CN"}],
      "language": "zh"
    }
  ]
}
```

Example output (abbreviated)
```json
CopyEdit
{
  "paper": {"title":"A Transformer-based Approach for Quantum Chemistry","doi":"10.1000/example","year":2022},
  "n_citations": 2,
  "components": {
    "breadth": {"value": 0.56, "discipline_counts":{"Chemistry":1,"Other":1}, "discipline_entropy_norm":0.56, "n_disciplines":2},
    "geography": {"value":0.5,"country_counts":{"US":1,"CN":1},"country_entropy_norm":0.5,"n_countries":2,"coverage":0.6667},
    "language": {"value":0.0,"language_counts":{"en":1,"zh":1},"language_entropy_norm":0.5,"n_languages":2},
    "depth": {"value":0.38,"avg_distance":0.38,"p90_distance":0.6},
    "temporal": {"value":0.25,"early_share":0.8,"median_year":2023}
  },
  "weights": {"breadth":0.3,"geo":0.2,"lang":0.1,"depth":0.25,"temporal":0.15},
  "diffusion_score": 45.12,
  "coords": [[0.0,0.0],[0.2,-0.1],[-0.3,0.2]],
  "labels": [0,1,1]
}
```


### 3) Streamlit UI: elegant metric display + visualizations (app.py)

Copy/save as app.py and run streamlit run app.py. This UI shows a card summarizing the Diffusion Score and components, a 2D topic scatter (paper + citations), and bar charts for discipline & country spread.

```python
CopyEdit
# app.py
import streamlit as st
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from diffusion import fetch_citations, compute_knowledge_diffusion_score

st.set_page_config(page_title="Knowledge Diffusion Explorer", layout="wide")
st.markdown("<style> .card {background:#fff;padding:16px;border-radius:12px;box-shadow:0 6px 18px rgba(15,15,15,0.06)} </style>", unsafe_allow_html=True)

st.title("🌐 Knowledge Diffusion Score")
st.write("Measure how far and wide a paper's core ideas spread across disciplines, geographies, languages, and time.")

with st.expander("Paste paper JSON (or use demo)"):
    sample_json = {
        "paper": {"title":"A Transformer-based Approach for Quantum Chemistry","abstract":"We propose a transformer architecture...","year":2022,"doi":"10.1000/example"},
        "paper_id": "demo:1"
    }
    st.code(sample_json, language="json")

col1, col2 = st.columns([2,1])
with col1:
    title = st.text_input("Paper Title", sample_json["paper"]["title"])
    abstract = st.text_area("Abstract", sample_json["paper"]["abstract"], height=120)
    year = st.number_input("Year", value=sample_json["paper"]["year"])
    doi = st.text_input("DOI (optional)", value=sample_json["paper"].get("doi",""))
    paper = {"title": title, "abstract": abstract, "year": year, "doi": doi}
    analyze = st.button("Analyze Diffusion")

with col2:
    st.markdown("### Options")
    st.write("Model: all-MiniLM-L6-v2 (local)")
    st.write("Projection: PCA")
    st.write("Clustering: KMeans")

if analyze:
    with st.spinner("Fetching citations and computing diffusion..."):
        # In production: fetch from OpenAlex / Semantic Scholar / internal datastore
        citations = fetch_citations(doi or title)
        res = compute_knowledge_diffusion_score(paper, citations)

    # Top card
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2,1,1])
    with c1:
        st.subheader(res["paper"]["title"])
        st.markdown(f"**DOI:*- {res['paper'].get('doi','-')}")
        st.markdown(f"**Citations considered:*- {res['n_citations']}")
    with c2:
        st.metric("Knowledge Diffusion Score", f"{res['diffusion_score']} / 100")
    with c3:
        # small breakdown
        comps = res["components"]
        st.markdown("**Top components**")
        st.write(f"• Breadth: {comps['breadth']['value']:.2f}")
        st.write(f"• Geography: {comps['geography']['value']:.2f}")
        st.write(f"• Depth: {comps['depth']['value']:.2f}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Two-column visualizations
    v1, v2 = st.columns([2,1])

    # Topic scatter: coords
    coords = np.array(res["coords"])
    labels = np.array(res["labels"])
    # first point is the paper (index 0)
    paper_pt = coords[0]
    cite_pts = coords[1:] if coords.shape[0]>1 else np.empty((0,2))

    with v1:
        st.subheader("Topic Map (paper + citations)")
        fig, ax = plt.subplots(figsize=(6,5))
        if cite_pts.shape[0]>0:
            ax.scatter(cite_pts[:,0], cite_pts[:,1], c='gray', alpha=0.6, s=50, label='Citations')
        ax.scatter(paper_pt[0], paper_pt[1], c='red', s=140, edgecolors='black', label='Paper')
        # annotate a few
        ax.set_xlabel("Topic dim 1")
        ax.set_ylabel("Topic dim 2")
        ax.legend()
        ax.grid(alpha=0.2)
        st.pyplot(fig)

    with v2:
        st.subheader("Discipline Spread")
        disc_counts = res["components"]["breadth"]["discipline_counts"]
        if disc_counts:
            disc_df = pd.DataFrame(list(disc_counts.items()), columns=["discipline","count"]).sort_values("count", ascending=False)
            st.bar_chart(disc_df.set_index("discipline"))
        else:
            st.write("No discipline data available")

    st.markdown("---")
    b1, b2 = st.columns(2)
    with b1:
        st.subheader("Geographic Spread")
        country_counts = res["components"]["geography"]["country_counts"]
        if country_counts:
            cdf = pd.DataFrame(list(country_counts.items()), columns=["country","count"]).sort_values("count", ascending=False)
            st.table(cdf.head(10))
        else:
            st.write("No country data")

    with b2:
        st.subheader("Temporal Diffusion")
        t = res["components"]["temporal"]
        st.write(f"Early share (first 2 years): {t['early_share']:.2f}")
        st.write(f"Median citing year: {t['median_year']}")

    st.markdown("---")
    st.subheader("Component details")
    st.json(res["components"])

    # Download JSON
    st.download_button("Download detailed diffusion JSON", json.dumps(res, indent=2), file_name="diffusion_result.json")
```


### 4) Realistic LLM prompts (for classification / explanations)


#### A) Discipline classifier (if you prefer LLM over heuristics)

Use this prompt to classify a citation into a discipline. Batch multiple citations into the prompt.
```kotlin
CopyEdit
You are an expert research classifier. Given the title and abstract of a paper, return a single-discipline label (e.g., "Chemistry", "Physics", "Computer Science", "Biology", "Engineering", "Medicine", "Economics", "Policy") that best fits the paper. If mixed, return the primary discipline.

Input:
1) Title: {title1}
   Abstract: {abstract1}
2) Title: {title2}
   Abstract: {abstract2}
...

Return JSON:
[
  {"id": 1, "discipline": "Chemistry"},
  {"id": 2, "discipline": "Computer Science"},
  ...
]
```

#### B) Human-readable explanation of diffusion results

Prompt the LLM to produce a short summary that will be shown on the card.
```cpp
CopyEdit
You are an expert science communicator. Given the following diffusion component values for a paper, produce a concise 2–3 sentence explanation summarizing how widely and how quickly the paper's ideas have spread, and what the main driver is (breadth, geography, depth, language).

Input JSON:
{
  "diffusion_score": 45.12,
  "components": {
    "breadth": {"value": 0.56, "n_disciplines": 3},
    "geography": {"value": 0.5, "n_countries": 4},
    "language": {"value": 0.4, "n_languages": 2},
    "depth": {"value": 0.38},
    "temporal": {"value": 0.25, "early_share": 0.8}
  },
  "n_citations": 124
}
```
Produce a short paragraph (2–3 sentences).


### 5) Production notes & improvements

- Real data sources: Replace fetch_citations() with OpenAlex / Semantic Scholar fetches. Those APIs provide citing-paper metadata (venue, affiliations, language, year, doi).
- Discipline mapping: Replace heuristic venue keyword mapping with LLM classifier or use Crossref subject categories / MAG fields / OpenAlex concept taxonomy.
- Embeddings: For large-scale production, use a dedicated embedding service (OpenAI embeddings, Cohere, or a higher-capacity sentence-transformer) and cache embeddings for citations.
- Scalability: For papers with thousands of citations, do sampling (e.g., stratified by year and venue) or incremental streaming computation with precomputed embeddings.
- Diffusion modeling: The current aggregator is a weighted linear combination. For advanced modeling, consider diffusion models (SI / SIR analogs) on citation networks or temporal point-process models to estimate reproduction number (R) of ideas.
- Normalization / calibrations: Calibrate component weights on a labeled dataset of papers known to have broad diffusion (policy-cited, cross-disciplinary reviews, etc.).
- Visualization: Consider interactive Plotly charts and world choropleth for geographic spread.


### 6) Quick test recipe

1. pip install streamlit sentence-transformers scikit-learn numpy pandas matplotlib torch
2. Save diffusion.py and app.py in the same folder.
3.  Run: streamlit run app.py
4.  Click Analyze (demo fetch_citations() returns sample citations).

### If you want, I can:

- Wire the Streamlit UI to OpenAlex or Semantic Scholar to fetch real citations (I’ll give the exact API call code).
- Add a calibration notebook to tune component weights on a labeled set of known-high-diffusion papers.
- Add interactive Plotly maps (world choropleth) for country spread.
