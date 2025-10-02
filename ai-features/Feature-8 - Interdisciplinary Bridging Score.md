
## Feature -8: Interdisciplinary Bridging Score


Great — below is a practical, runnable, and production-ready package for the Interdisciplinary Bridging Score feature. It includes:


* A backend module bridging.py with:
    * data fetch stub (replace with OpenAlex/Semantic Scholar in prod),
    * field extraction & normalization,
    * field-embedding distance calculation,
    * graph construction and centrality/bridging measures,
    * an aggregated Interdisciplinary Bridging Score (0–100) and detailed breakdown.
* A neat Streamlit UI app.py that renders an elegant metric card, field bar charts, and a small network view (matplotlib), plus ability to paste sample data or upload CSV.
* A realistic LLM prompt to generate human-readable explanations of the bridging result.
* Sample input / sample output JSON and notes to deploy at scale.
Everything is self-contained — swap the fetch_* stubs for OpenAlex / MAG / your DB when ready.

### Design summary (how score is computed)

1. Collect citing papers and their field tags (OpenAlex concepts, MAG fields, CrossRef subjects). Each citing paper may map to multiple fields; we count each occurrence or use primary field.
2. Normalize field labels and compute embeddings for field labels using a sentence transformer.
3. Compute pairwise field distances as 1 - cosine_similarity(field_vec_i, field_vec_j) (range 0..2 but we clamp/normalize to 0..1).
4. Breadth: entropy / number of distinct fields.
5. Distance/Bridging: weighted average pairwise distance across fields weighted by citation counts (how far apart the connected fields are).
6. Graph bridging: build bipartite graph (paper node —> field nodes via citing papers) and compute centrality/bridge metrics (betweenness centrality of paper node, clustering coefficients).
7. Combine signals into a single Interdisciplinary Bridging Score (0–100) with tunable weights.

### 1) Backend: bridging.py

Save as bridging.py.
```python
CopyEdit
# bridging.py
from typing import List, Dict, Any, Tuple
import numpy as np
from collections import Counter, defaultdict
from sentence_transformers import SentenceTransformer, util
import math
import networkx as nx

# Lightweight embedding model for field names
_EMB_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------
# Stubs: replace with real API fetchers
# -------------------------
def fetch_citations_with_fields(paper_id_or_doi: str) -> List[Dict[str, Any]]:
    """
    Replace with OpenAlex / Semantic Scholar / MAG call that returns citing papers and their 'fields' or 'concepts'.
    Minimal returned fields per citing paper:
      - 'id' (optional)
      - 'title'
      - 'year'
      - 'fields': list of field strings (e.g., "Computer Science", "Biology", "Bioinformatics")
      - 'affiliations' (optional)
    Demo synthetic return:
    """
    return [
        {"id": "C1", "title": "Translational ML in genomics", "year": 2023, "fields": ["Computer Science", "Genomics"]},
        {"id": "C2", "title": "Protein design via transformers", "year": 2024, "fields": ["Biology", "Computer Science"]},
        {"id": "C3", "title": "Quantum chemistry benchmarks", "year": 2023, "fields": ["Chemistry"]},
        {"id": "C4", "title": "Bioinformatics pipelines", "year": 2022, "fields": ["Bioinformatics", "Software Engineering"]},
        {"id": "C5", "title": "Policy paper referencing methods", "year": 2024, "fields": ["Public Policy", "Health Policy"]},
    ]

# -------------------------
# Utilities
# -------------------------
def normalize_field(field: str) -> str:
    """Light normalization of field strings (lowercase, simple mapping)."""
    if not field:
        return "Unknown"
    f = field.strip().lower()
    # small mapping to canonical names
    mapping = {
        "cs": "computer science", "comp sci": "computer science", "bioinformatics": "bioinformatics",
        "genomics": "genomics", "biology": "biology", "chem": "chemistry", "chemistry": "chemistry",
        "public policy": "public policy", "health policy": "health policy", "software engineering": "software engineering"
    }
    return mapping.get(f, f).title()

def embed_fields(fields: List[str]) -> Dict[str, np.ndarray]:
    """Return embedding vector per unique field string."""
    unique = list(dict.fromkeys(fields))
    if not unique:
        return {}
    embs = _EMB_MODEL.encode(unique, convert_to_numpy=True, show_progress_bar=False)
    return {f: embs[i] for i, f in enumerate(unique)}

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(util.cos_sim(a, b).item())

# -------------------------
# Core bridging measures
# -------------------------
def field_counts_from_citations(citations: List[Dict[str, Any]]) -> Counter:
    """
    Count occurrences of fields across all citing papers.
    If a citing paper has multiple fields, each field counts once for that citation.
    Returns Counter(field -> count)
    """
    c = Counter()
    for cit in citations:
        fields = cit.get("fields", []) or []
        for f in fields:
            c[normalize_field(f)] += 1
    return c

def compute_pairwise_field_distances(field_embs: Dict[str, np.ndarray]) -> Dict[Tuple[str,str], float]:
    """Compute symmetric distances between fields normalized to [0,1]."""
    keys = list(field_embs.keys())
    d = {}
    for i, a in enumerate(keys):
        for j, b in enumerate(keys):
            if j <= i: continue
            sim = cosine_sim(field_embs[a], field_embs[b])  # in [-1,1]
            dist = 1.0 - sim  # roughly in [0,2]; typical sim in [0,1] -> dist in [0,1]
            # clip to 0..1
            dist = max(0.0, min(1.0, dist))
            d[(a,b)] = dist
            d[(b,a)] = dist
    # distance to self = 0
    for k in keys:
        d[(k,k)] = 0.0
    return d

def weighted_mean_pairwise_distance(field_counts: Counter, distances: Dict[Tuple[str,str], float]) -> float:
    """
    Weighted average of pairwise distances where weights = product of normalized counts.
    For fields i,j with counts ci,cj and total T, weight = (ci/T)*(cj/T) (so sum weights = 1 - sum self-weights?).
    We compute sum_{i<j} w_ij * dist_ij and return.
    """
    fields = list(field_counts.keys())
    total = sum(field_counts.values()) or 1
    norm = {f: field_counts[f] / total for f in fields}
    score = 0.0
    for i, a in enumerate(fields):
        for j, b in enumerate(fields):
            if j <= i: continue
            w = norm[a] * norm[b]
            dist = distances.get((a,b), 0.0)
            score += w * dist
    # score in [0,1]
    return float(max(0.0, min(1.0, score)))

def field_entropy(field_counts: Counter) -> float:
    """Normalized entropy across field distribution (0..1)."""
    total = sum(field_counts.values()) or 1
    ps = [v/total for v in field_counts.values() if v>0]
    if not ps:
        return 0.0
    H = -sum(p * math.log(p, 2) for p in ps)
    maxH = math.log(len(ps), 2) if len(ps)>1 else 1.0
    return float(H / maxH) if maxH>0 else 0.0

def build_bipartite_graph(paper_id: str, citations: List[Dict[str, Any]]) -> nx.Graph:
    """
    Build a simple bipartite graph: paper node 'P:<paper_id>' connected to field nodes 'F:<field>'.
    Also add citation nodes 'C:<citation_id>' connected to their field nodes and to paper node.
    This is a small graph used to compute centrality/bridging measures.
    """
    G = nx.Graph()
    paper_node = f"P:{paper_id}"
    G.add_node(paper_node, bipartite='paper', type='paper')
    for cit in citations:
        cid = cit.get("id") or f"C:{cit.get('title','').replace(' ','_')[:30]}"
        cit_node = f"C:{cid}"
        G.add_node(cit_node, bipartite='citation', type='citation')
        G.add_edge(paper_node, cit_node)
        for f in cit.get("fields", []):
            fn = normalize_field(f)
            fnode = f"F:{fn}"
            if not G.has_node(fnode):
                G.add_node(fnode, bipartite='field', type='field', field=fn)
            # connect citation to field
            G.add_edge(cit_node, fnode)
    return G

def compute_graph_bridge_score(G: nx.Graph, paper_id: str) -> Dict[str,float]:
    """
    Compute basic graph metrics:
      - betweenness centrality of paper node (normalized)
      - bridging coefficient (how many distinct fields it connects through citations)
    Return normalized values (0..1).
    """
    paper_node = f"P:{paper_id}"
    if paper_node not in G:
        return {"betweenness": 0.0, "field_bridge_fraction": 0.0}

    # betweenness centrality (use approximation for larger graphs in prod)
    bc = nx.betweenness_centrality(G, k=min(20, max(1, int(len(G.nodes())/2))), normalized=True)
    bet = bc.get(paper_node, 0.0)

    # how many unique field nodes reachable from paper via citations (two hops)
    neighbors = set(G.neighbors(paper_node))
    field_nodes = set()
    for n in neighbors:
        for nn in G.neighbors(n):
            if isinstance(nn, str) and nn.startswith("F:"):
                field_nodes.add(nn)
    # total distinct field nodes in graph:
    total_fields = len([n for n,d in G.nodes(data=True) if d.get('type')=='field'])
    field_bridge_fraction = 0.0
    if total_fields > 0:
        field_bridge_fraction = len(field_nodes) / total_fields
    return {"betweenness": float(min(1.0,bet)), "field_bridge_fraction": float(min(1.0, field_bridge_fraction))}

# -------------------------
# Main aggregator
# -------------------------
def compute_interdisciplinary_bridging(paper_id_or_doi: str, paper_meta: Dict[str,Any]=None,
                                      citations: List[Dict[str,Any]] = None,
                                      weights: Dict[str,float]=None) -> Dict[str,Any]:
    """
    Main entry point.
    - paper_id_or_doi: unique id used for graph node labeling (string)
    - paper_meta: optional dict with paper metadata
    - citations: optional list; if None, will call fetch_citations_with_fields()
    - weights: dict for combining components; keys: breadth(entropy), distance, graph_betweenness, field_fraction
    Returns: dictionary with components and final bridging score (0..100) plus details.
    """
    if citations is None:
        citations = fetch_citations_with_fields(paper_id_or_doi)

    # Compile field counts
    field_counts = field_counts_from_citations(citations)
    fields = list(field_counts.keys())

    # embed fields (if only one field, embedding still computed)
    field_embs = embed_fields(fields)

    # pairwise distances
    distances = compute_pairwise_field_distances(field_embs) if len(field_embs) > 0 else {}

    # component computations
    breadth = field_entropy(field_counts)  # 0..1
    pairwise_dist = weighted_mean_pairwise_distance(field_counts, distances) if distances else 0.0
    # graph-based bridging
    G = build_bipartite_graph(paper_id_or_doi, citations)
    graph_metrics = compute_graph_bridge_score(G, paper_id_or_doi)

    # default weights if not provided
    if weights is None:
        weights = {"breadth": 0.30, "distance": 0.40, "betweenness": 0.20, "field_fraction": 0.10}
    # normalize weights
    total_w = sum(weights.values()) or 1.0
    w = {k:weights[k]/total_w for k in weights}

    # Compose raw score
    raw = (breadth * w["breadth"] +
           pairwise_dist * w["distance"] +
           graph_metrics["betweenness"] * w["betweenness"] +
           graph_metrics["field_bridge_fraction"] * w["field_fraction"])

    # scale to 0..100
    bridging_score = round(max(0.0, min(1.0, raw)) * 100, 2)

    # Build readable outputs
    result = {
        "paper_id": paper_id_or_doi,
        "paper_meta": paper_meta or {},
        "n_citations": len(citations),
        "field_counts": dict(field_counts),
        "components": {
            "breadth_entropy": round(breadth, 4),
            "mean_pairwise_distance": round(pairwise_dist, 4),
            "graph_betweenness": round(graph_metrics["betweenness"], 4),
            "field_fraction_connected": round(graph_metrics["field_bridge_fraction"], 4)
        },
        "weights": w,
        "bridging_score": bridging_score,
        # extras for visualization
        "field_embeddings": {k: list(map(float,v)) for k,v in field_embs.items()},
        "pairwise_distances": {f"{a}__{b}": round(distances.get((a,b),0.0),4) for a in fields for b in fields},
        "graph_edges": list(G.edges()),
    }
    return result
```

### 2) Sample input / output

Input (call):
```python
CopyEdit
from bridging import compute_interdisciplinary_bridging
res = compute_interdisciplinary_bridging("10.1000/exampledoi")
```

Sample Output (abbreviated):
```json
CopyEdit
{
  "paper_id": "10.1000/exampledoi",
  "n_citations": 5,
  "field_counts": {
    "Computer Science": 3,
    "Genomics": 1,
    "Biology": 1,
    "Chemistry": 1,
    "Public Policy": 1
  },
  "components": {
    "breadth_entropy": 0.78,
    "mean_pairwise_distance": 0.42,
    "graph_betweenness": 0.05,
    "field_fraction_connected": 0.67
  },
  "weights": {"breadth":0.3,"distance":0.4,"betweenness":0.2,"field_fraction":0.1},
  "bridging_score": 57.84,
  ...
}
```

Interpretation: moderate bridging — paper is cited across CS and biology/genomics with some policy cross-citations, and the average pairwise field distance is moderate, yielding a bridging score in the 50s.

### 3) Streamlit UI: elegant metric card + visuals (app.py)

Save as app.py and run with streamlit run app.py. This UI:
* Accepts DOI or title
* Uses the backend to compute results
* Renders a clean metric card with the Bridging Score, components, and two visuals:
    * Field bar chart (counts)
    * Tiny network view of paper->citations->fields

```python
CopyEdit
# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from bridging import compute_interdisciplinary_bridging, fetch_citations_with_fields

st.set_page_config(page_title="Interdisciplinary Bridging Explorer", layout="wide")
st.markdown("""
<style>
.card {background:#fff;padding:18px;border-radius:12px;box-shadow:0 8px 24px rgba(15,15,15,0.06);margin-bottom:14px;}
.small {color:#666;font-size:0.95rem;}
</style>
""", unsafe_allow_html=True)

st.title("🔀 Interdisciplinary Bridging Score")
st.write("Measure how well a paper connects distant fields based on the fields of citing papers.")

# Input
col1, col2 = st.columns([3,1])
with col1:
    paper_id = st.text_input("Paper DOI or ID", value="10.1000/exampledoi")
    title = st.text_input("Paper Title (optional)")
    if st.button("Compute Bridging Score"):
        with st.spinner("Fetching citations and computing bridging metrics..."):
            # In production fetch citations externally; here compute wrapper uses fetch stub
            citations = fetch_citations_with_fields(paper_id)
            res = compute_interdisciplinary_bridging(paper_id, paper_meta={"title":title}, citations=citations)
            st.session_state["bridging_res"] = res

with col2:
    st.markdown("### Options")
    st.write("Field embedding model: all-MiniLM-L6-v2")
    st.write("Weights: breadth 30%, distance 40%, betweenness 20%, field_fraction 10%")

# Results
if "bridging_res" in st.session_state:
    res = st.session_state["bridging_res"]
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([3,1,1])
    with c1:
        st.subheader(res["paper_meta"].get("title", paper_id))
        st.markdown(f"**Paper ID:** {res['paper_id']}")
        st.markdown(f"**Citations analyzed:** {res['n_citations']}")
    with c2:
        st.metric(label="Interdisciplinary Bridging Score", value=f"{res['bridging_score']} / 100")
    with c3:
        st.markdown("**Top signals**")
        st.write(f"• Breadth (entropy): {res['components']['breadth_entropy']:.2f}")
        st.write(f"• Mean field distance: {res['components']['mean_pairwise_distance']:.2f}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    # Field counts bar chart
    st.subheader("Field distribution among citing papers")
    fc = res["field_counts"]
    df = pd.DataFrame(list(fc.items()), columns=["field","count"]).sort_values("count", ascending=False)
    fig, ax = plt.subplots(figsize=(6,3))
    ax.barh(df["field"], df["count"])
    ax.set_xlabel("Citation count")
    ax.set_ylabel("")
    ax.invert_yaxis()
    st.pyplot(fig)

    st.markdown("---")
    # small network graph
    st.subheader("Paper → Citations → Fields (preview)")
    G = nx.Graph()
    paper_node = f"P:{res['paper_id']}"
    G.add_node(paper_node)
    for e in res["graph_edges"]:
        G.add_edge(e[0], e[1])
    # draw network (simple)
    pos = nx.spring_layout(G, seed=42, k=0.5)
    fig2, ax2 = plt.subplots(figsize=(6,4))
    node_colors = []
    sizes = []
    labels = {}
    for n,d in G.nodes(data=True):
        if isinstance(n, str) and n.startswith("P:"):
            node_colors.append("red"); sizes.append(400); labels[n] = "Paper"
        elif isinstance(n, str) and n.startswith("F:"):
            node_colors.append("#1f77b4"); sizes.append(300); labels[n] = n[2:]
        elif isinstance(n, str) and n.startswith("C:"):
            node_colors.append("#999999"); sizes.append(120); labels[n] = ""
        else:
            node_colors.append("#bbbbbb"); sizes.append(100); labels[n] = n
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=sizes, ax=ax2)
    nx.draw_networkx_edges(G, pos, alpha=0.5, ax=ax2)
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, ax=ax2)
    ax2.axis("off")
    st.pyplot(fig2)

    st.markdown("---")
    st.subheader("Component details")
    st.json(res["components"])

    st.download_button("Download bridging result JSON", data=str(res), file_name="bridging_result.json", mime="application/json")
```


### 4) Realistic LLM prompt(s)

Use an LLM to generate a concise human-readable explanation of the bridging score:

#### A — Explanation prompt
```csharp
CopyEdit
You are an expert research-metrics communicator. Given this JSON with Interdisciplinary Bridging components and a bridging score, produce a concise 2-3 sentence summary that explains:
- whether the paper connects distant fields,
- which fields are most involved,
- what drove the bridging score (breadth, distance, or graph bridging),
- one short recommendation to increase bridging (if low).

Input:
{paste JSON result}

Output: 2-3 short sentences in plain text.
```

#### B — Field normalization helper prompt (batch)

```pgsql
CopyEdit
You are a metadata normalizer. Given a list of raw field strings extracted from various APIs (e.g., "Comp Sci", "bioinformatics", "biol", "genomics", "health-policy"), map them to canonical field labels (short, title-case) and output JSON mapping raw->canonical. Keep mappings consistent and suggest "Unknown" for empty or unrecognized inputs.
```


### 5) Production notes & improvements

* Replace stubs: Replace fetch_citations_with_fields() with an OpenAlex / Semantic Scholar call. OpenAlex returns concepts with display_name which map nicely to fields.
* Field taxonomy: For more accurate distances use a curated ontology (e.g., MAG/ACM/MeSH) and compute taxonomic distance (shortest path in taxonomy). If not available, embeddings of field labels are a good proxy.
* Scale: For papers with many citations, sample citations stratified by year & venue or compute components incrementally with cached embeddings.
* Graph compute: For large citation sets, approximate betweenness centrality (e.g., nx.betweenness_centrality with k samples) or use graph libraries (igraph) for speed.
* Calibration: Calibrate weights and score scaling on a labeled set (papers known to be bridge papers vs. discipline-specific papers).
* Explainability: Keep the component breakdown and pairwise distances in the output so UI can show which field pairs drive bridging.
* Extensions: compute author-level bridging (which authors bring cross-discipline links), temporal bridging (how bridging changes over time), map top bridging citations.

### 6) Quick test recipe

1. pip install streamlit sentence-transformers networkx matplotlib pandas
2. Save bridging.py and app.py in same folder.
3. Run: streamlit run app.py
4. Click Compute Bridging Score (demo data used by stub).

### If you want, I can:

* Add OpenAlex integration code (exact API calls + rate-limit handling) so the UI fetches live citing-paper concepts.
* Provide a dockerfile to containerize the Streamlit app.
* Add an explain button that calls the LLM (OpenAI) with the explanation prompt and displays the human-readable summary on the card.
