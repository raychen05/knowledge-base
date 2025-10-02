
## Feature-7 : 🧠  Concept Adoption Index


Nice — below is a complete, practical, and runnable package for the Concept Adoption Index feature: backend code to extract novel concepts (n-grams + NLP), compute embeddings, detect reuse across citing papers, and a polished Streamlit UI that displays an elegant metric card, top concepts, adoption timeline, and explanation. I also include realistic LLM prompts (for human-readable explanations or to validate novelty).

High-level flow
1. Extract candidate concepts from the focal paper (n-grams, noun-phrases, formulas).
2. Filter / deduplicate candidates using embedding similarity (keeps representative phrases).
3. For each candidate, scan citing papers for reuse: exact n-gram matches + semantic matches via embeddings.
4. Produce per-concept adoption stats (count, first reuse year, adoption velocity) and aggregate a Concept Adoption Index.


### 🚀 Quick setup (requirements)

```bash
CopyEdit
pip install streamlit sentence-transformers scikit-learn pandas matplotlib spacy nltk
# and for spaCy noun phrases (optional but recommended):
python -m spacy download en_core_web_sm
```

### 1) Backend: concept_adoption.py

Save this as concept_adoption.py. Replace fetch_citations() with your real citation fetcher (OpenAlex, Semantic Scholar, your DB).
```python
CopyEdit
# concept_adoption.py
from typing import List, Dict, Any, Tuple
import re
import numpy as np
import math
from collections import Counter, defaultdict
from sentence_transformers import SentenceTransformer, util

# Optional: spaCy for noun-phrase extraction (fallback to regex n-grams if not available)
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

# Embedding model (lightweight for demo; swap for higher-capacity in prod)
EMB_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# ----------------------
# Utilities / Extraction
# ----------------------

def simple_tokenize(text: str) -> List[str]:
    # simple whitespace tokenizer + lower
    return [t.lower() for t in re.findall(r"\b\w[\w\-\_]+\b", text)]

def extract_ngrams(text: str, n_min=1, n_max=4, min_freq=1) -> Counter:
    """
    Extract candidate n-grams from text.
    Returns Counter(ngram -> count).
    """
    tokens = simple_tokenize(text)
    c = Counter()
    L = len(tokens)
    for n in range(n_min, min(n_max, L)+1):
        for i in range(L - n + 1):
            ng = " ".join(tokens[i:i+n])
            # simple filter: remove stop-ish tokens and extremely common single words
            if re.search(r'^[0-9]+$', ng):
                continue
            if len(ng) < 3:
                continue
            c[ng] += 1
    # filter by min_freq
    return Counter({k:v for k,v in c.items() if v >= min_freq})

def extract_noun_phrases(text: str, min_len=2) -> List[str]:
    """
    Extract noun phrases using spaCy if available; fallback to n-grams.
    """
    if nlp:
        doc = nlp(text)
        phrases = []
        for np in doc.noun_chunks:
            s = np.text.strip().lower()
            if len(s.split()) >= min_len:
                phrases.append(s)
        return phrases
    else:
        # fallback: return common 2-3 grams
        ng = extract_ngrams(text, n_min=2, n_max=3, min_freq=1)
        return list(ng.keys())

def detect_formulae(text: str) -> List[str]:
    """
    Quick heuristic to find formula-like patterns e.g., "Eq. (1)", "E=mc^2", "f(x) =".
    """
    patterns = [
        r"[A-Za-z]\s*=\s*[A-Za-z0-9\^\+\-\*\/\(\)\[\]\.]+",
        r"Eq\.\s*\(?\d+\)?",
        r"equation\s*\(?\d+\)?",
        r"\\begin\{equation\}.*?\\end\{equation\}"
    ]
    found = set()
    for p in patterns:
        for m in re.findall(p, text, flags=re.IGNORECASE | re.DOTALL):
            found.add(m.strip())
    return list(found)

# ----------------------
# Embedding helpers
# ----------------------

def embed_texts(texts: List[str]) -> np.ndarray:
    if not texts:
        return np.zeros((0, EMB_MODEL.get_sentence_embedding_dimension()))
    return EMB_MODEL.encode(texts, convert_to_numpy=True, show_progress_bar=False)

def deduplicate_candidates(candidates: List[str], threshold: float = 0.85) -> List[str]:
    """
    Deduplicate list of phrase candidates using embeddings:
      - If two candidates have cosine similarity >= threshold, keep the longer/more frequent one.
    Returns list of representative candidates.
    """
    if not candidates:
        return []
    embs = embed_texts(candidates)
    keep = []
    used = set()
    sims = util.cos_sim(embs, embs).cpu().numpy()
    # score by length (longer / more tokens prioritized)
    scores = [len(c.split()) for c in candidates]
    order = sorted(range(len(candidates)), key=lambda i: (-scores[i], i))
    for idx in order:
        if idx in used:
            continue
        keep.append(candidates[idx])
        # mark others as used if similar
        for j in range(len(candidates)):
            if j == idx or j in used:
                continue
            if sims[idx, j] >= threshold:
                used.add(j)
    return keep

# ----------------------
# Matching / reuse detection
# ----------------------

def exact_ngram_match_count(ngram: str, doc_text: str) -> int:
    """
    Count exact n-gram occurrences (case-insensitive) in doc_text.
    """
    return len(re.findall(r"\b" + re.escape(ngram) + r"\b", doc_text, flags=re.IGNORECASE))

def semantic_match(phrase: str, doc_text: str, doc_emb: np.ndarray, phrase_emb: np.ndarray, sim_threshold: float = 0.72) -> bool:
    """
    Heuristic semantic match: embed (phrase) and doc_text (or its sentences) and check if any sentence has sim>=threshold.
    doc_emb can be a precomputed array of sentence embeddings for the doc.
    For speed, we provide doc_emb (num_sentences x D).
    """
    if doc_emb is None or doc_emb.shape[0] == 0:
        return False
    sims = util.cos_sim(phrase_emb, doc_emb).cpu().numpy().flatten()
    return bool((sims >= sim_threshold).any())

def build_doc_sentence_embeddings(doc_text: str) -> Tuple[List[str], np.ndarray]:
    """
    Split doc into sentences and embed them. Return (sentences, embeddings).
    Uses a naive sentence splitter.
    """
    # naive split by punctuation; swap to nltk.sent_tokenize if available
    sents = [s.strip() for s in re.split(r'(?<=[\.\?\!])\s+', doc_text) if s.strip()]
    if not sents:
        return [], np.zeros((0, EMB_MODEL.get_sentence_embedding_dimension()))
    embs = embed_texts(sents)
    return sents, embs

# ----------------------
# Main function
# ----------------------

def build_candidate_concepts(paper_text: str, top_k_ngrams=60, ngram_min_freq=1) -> List[str]:
    """
    Extract candidate concept phrases combining noun-phrases, n-grams, formulae.
    Returns deduplicated representative candidates.
    """
    ngram_counts = extract_ngrams(paper_text, n_min=1, n_max=4, min_freq=ngram_min_freq)
    top_ngrams = [ng for ng,_ in ngram_counts.most_common(top_k_ngrams)]

    noun_phrases = extract_noun_phrases(paper_text, min_len=1)
    formulae = detect_formulae(paper_text)

    combined = list(dict.fromkeys(top_ngrams + noun_phrases + formulae))  # preserve order, dedupe
    # dedupe semantically
    candidates = deduplicate_candidates(combined, threshold=0.86)
    return candidates

def compute_concept_adoption(paper: Dict[str, Any], citations: List[Dict[str, Any]],
                             sim_threshold_semantic: float = 0.72,
                             semantic_count_threshold: int = 1) -> Dict[str, Any]:
    """
    Main pipeline:
      - extract candidate concepts from the focal paper
      - for each candidate, compute exact and semantic reuse counts across citations
    citations: list of dicts with keys: 'title','abstract','year','text' (optional), etc.
    Returns detailed per-concept stats and overall index.
    """
    paper_text = (paper.get("title","") + "\n\n" + paper.get("abstract","")).strip()
    candidates = build_candidate_concepts(paper_text)

    # precompute embeddings for candidates
    cand_embs = embed_texts(candidates)

    # prepare citations: for each citation build a combined text and sentence embeddings
    prepared = []
    for c in citations:
        text = c.get("text") or (c.get("title","") + "\n\n" + c.get("abstract",""))
        sents, sent_embs = build_doc_sentence_embeddings(text)
        prepared.append({"meta": c, "text": text, "sents": sents, "sent_embs": sent_embs})

    # per-concept stats
    concept_stats = {}
    for idx, concept in enumerate(candidates):
        cemb = cand_embs[idx:idx+1]
        exact_count = 0
        semantic_count = 0
        first_year = None
        years = []
        matched_docs = []
        for doc in prepared:
            ex = exact_ngram_match_count(concept, doc["text"])
            sem = 0
            if not ex:
                # semantic match
                if semantic_match(concept, doc["text"], doc["sent_embs"], cemb, sim_threshold_semantic):
                    sem = 1
            used = ex or sem
            if used:
                semantic_count += sem
                exact_count += ex
                y = doc["meta"].get("year")
                if y:
                    years.append(y)
                    if first_year is None or y < first_year:
                        first_year = y
                matched_docs.append({"meta": doc["meta"], "exact_matches": ex, "semantic_match": bool(sem)})
        total_matches = len(matched_docs)
        # adoption velocity: matches per year since publication (if year present)
        pub_year = paper.get("year")
        if pub_year and years:
            span_years = max(1, max(years) - min(years) + 1)
            velocity = total_matches / span_years
        elif years:
            velocity = total_matches / max(1, len(set(years)))
        else:
            velocity = 0.0

        concept_stats[concept] = {
            "concept": concept,
            "exact_count": exact_count,
            "semantic_count": semantic_count,
            "total_matches": total_matches,
            "first_year": first_year,
            "years": sorted(list(set(years))),
            "velocity": round(velocity, 3),
            "matched_docs": matched_docs
        }

    # Aggregate into a Concept Adoption Index (CAI)
    # idea: weight concepts by novelty (longer / rare) and adoption frequency
    # novelty proxy: inverse frequency of concept across external corpus unknown => use concept length as proxy
    def novelty_proxy(concept_str: str) -> float:
        # length & token uniqueness heuristic
        toks = concept_str.split()
        return min(1.0, (len(toks) / 6.0))  # 1.0 for phrases >=6 tokens

    # compute raw component per concept
    raw_scores = []
    for c, stats in concept_stats.items():
        adoption = stats["total_matches"]  # raw reuse
        novelty = novelty_proxy(c)
        raw = novelty * (1 + math.log(1 + adoption))  # logarithmic scaling on adoption
        raw_scores.append((c, raw))

    # normalize raw to 0..1
    if raw_scores:
        vals = np.array([r for _,r in raw_scores], dtype=float)
        minv, maxv = vals.min(), vals.max()
        rangev = max(1e-9, maxv - minv)
        norm = {c: float((r-minv)/rangev) for (c,r) in raw_scores}
    else:
        norm = {}

    # concept adoption index = weighted average of normalized concept scores (weights: novelty)
    weights = []
    for c in concept_stats:
        w = novelty_proxy(c)
        weights.append(w)
    total_w = sum(weights) or 1.0
    cai = 0.0
    for c in concept_stats:
        cai += (weights.pop(0) / total_w) * norm.get(c, 0.0)
    cai = round(float(cai) * 100, 2)  # scale 0..100

    # Prepare top concepts sorted by total_matches then semantic_count
    top_concepts = sorted(concept_stats.values(), key=lambda x: (x["total_matches"], x["semantic_count"], len(x["concept"].split())), reverse=True)

    return {
        "paper": {"title": paper.get("title"), "doi": paper.get("doi"), "year": paper.get("year")},
        "n_candidates": len(candidates),
        "n_citations": len(citations),
        "cai": cai,
        "concepts": top_concepts,
        "normalized_scores": norm
    }
```

###  2) Sample usage (quick test)

```python
CopyEdit
from concept_adoption import compute_concept_adoption

paper = {
    "title": "Transformer-Accelerated Reaction Prediction",
    "abstract": "We introduce TransReact, a transformer-based architecture that predicts catalytic reaction pathways with a novel loss function 'react-loss' that improves selectivity.",
    "year": 2022,
    "doi": "10.1000/transreact"
}

# demo citations: in production you would fetch OpenAlex/Semantic Scholar citing papers
citations = [
    {"title": "Applying TransReact to Photocatalysis", "abstract":"We use TransReact and react-loss ...", "year":2023, "text": "We use TransReact and the react-loss introduced by ..."},
    {"title": "A Survey of reaction predictors", "abstract":"This survey discusses TransReact among others", "year":2024, "text": "TransReact ..."},
    {"title": "Transformer models in catalysis", "abstract":"No direct reuse", "year":2023, "text": "This paper mentions transformers but not TransReact specifically."}
]

res = compute_concept_adoption(paper, citations)
import json
print(json.dumps(res, indent=2))
```

###  3) Streamlit app: elegant metric display and cards (app.py)

Save as app.py. This UI lets you paste a paper, optionally upload a CSV of citing papers (columns: title,abstract,year,text), run analysis, and renders a clean metric card, top concepts as cards, and a timeline/bar chart.

```python
CopyEdit
# app.py
import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
from concept_adoption import compute_concept_adoption, build_candidate_concepts

st.set_page_config(page_title="Concept Adoption Index", layout="wide")
st.markdown("""
<style>
.card {background:#fff;padding:16px;border-radius:10px;box-shadow:0 6px 18px rgba(0,0,0,0.06);margin-bottom:12px;}
.concept-title {font-weight:700;font-size:1.05rem;}
.small-muted {color:#666;font-size:0.9rem;}
</style>
""", unsafe_allow_html=True)

st.title("🧠 Concept Adoption Index")
st.write("Detect novel terms/methods from a paper and measure how often they are reused in subsequent publications.")

with st.expander("Sample paper"):
    st.code({
        "title": "Transformer-Accelerated Reaction Prediction",
        "abstract": "We introduce TransReact, a transformer-based architecture... introduces 'react-loss' as a novel objective.",
        "year": 2022
    }, language="json")

col1, col2 = st.columns([3,1])
with col1:
    title = st.text_input("Paper Title", value="Transformer-Accelerated Reaction Prediction")
    abstract = st.text_area("Abstract", value="We introduce TransReact, a transformer-based architecture that predicts catalytic reaction pathways with a novel loss function 'react-loss' that improves selectivity.", height=160)
    year = st.number_input("Year", value=2022, min_value=1900, max_value=2100)
    doi = st.text_input("DOI (optional)")
    paper = {"title": title, "abstract": abstract, "year": year, "doi": doi}

    st.markdown("### Citing papers (demo / upload CSV)")
    uploaded = st.file_uploader("Upload CSV with columns: title, abstract, year, text (optional)", type="csv")
    if uploaded:
        df = pd.read_csv(uploaded)
        citations = df.to_dict(orient="records")
    else:
        # demo citations
        citations = [
            {"title": "Applying TransReact to Photocatalysis", "abstract":"We use TransReact and react-loss ...", "year":2023, "text": "We use TransReact and the react-loss introduced by ..."},
            {"title": "A Survey of reaction predictors", "abstract":"This survey discusses TransReact among others", "year":2024, "text": "TransReact ..."},
            {"title": "Transformer models in catalysis", "abstract":"No direct reuse", "year":2023, "text": "This paper mentions transformers but not TransReact specifically."}
        ]

    if st.button("Compute Concept Adoption"):
        with st.spinner("Extracting concepts and scanning citations..."):
            res = compute_concept_adoption(paper, citations)
        st.session_state["res"] = res
        st.success("Analysis complete")

with col2:
    st.markdown("## Options")
    st.write("Semantic match threshold: 0.72 (tunable)")
    st.write("Embedding model: all-MiniLM-L6-v2")
    if st.button("Show candidate concepts"):
        candidates = build_candidate_concepts((paper["title"] + "\n\n" + paper["abstract"]))
        st.write("Top candidates:")
        for c in candidates[:40]:
            st.markdown(f"- {c}")

# Display results elegantly
if "res" in st.session_state:
    res = st.session_state["res"]
    # Top metric card
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([3,1,1])
    with c1:
        st.subheader(res["paper"]["title"])
        st.markdown(f"**DOI:** {res['paper'].get('doi','-')}")
        st.markdown(f"**Candidates extracted:** {res['n_candidates']}")
        st.markdown(f"**Citations analyzed:** {res['n_citations']}")
    with c2:
        st.metric("Concept Adoption Index", f"{res['cai']} / 100")
    with c3:
        # quick guidance
        st.markdown("**Interpretation**")
        st.write("• Higher CAI = concepts from the paper are more widely reused.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Top concepts cards
    st.markdown("### 🔎 Top concepts (by reuse)")
    cols = st.columns(3)
    top = res["concepts"][:9]
    for i, c in enumerate(top):
        col = cols[i % 3]
        col.markdown(f"""
        <div class='card'>
          <div class='concept-title'>{c['concept']}</div>
          <div class='small-muted'>Total matches: {c['total_matches']} • Exact: {c['exact_count']} • Semantic: {c['semantic_count']}</div>
          <div style="margin-top:8px;">First reuse year: {c.get('first_year') or '—'}</div>
          <div style="margin-top:8px;font-size:0.95rem;color:#333">Velocity: {c['velocity']} matches/year</div>
          <details style="margin-top:8px"><summary>Matched documents ({len(c['matched_docs'])})</summary>
            <ul>
            {''.join([f\"<li>{md['meta'].get('title','-')} ({md['meta'].get('year','-')}) — exact:{md['exact_matches']} sem:{int(md['semantic_match'])}</li>\" for md in c['matched_docs']])}
            </ul>
          </details>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    # Adoption timeline
    st.markdown("### 📈 Adoption timeline")
    # build year counts per top concept
    all_years = []
    for c in res["concepts"]:
        for y in c.get("years", []):
            all_years.append(y)
    if all_years:
        year_counts = pd.Series(all_years).value_counts().sort_index()
        fig, ax = plt.subplots()
        ax.plot(year_counts.index, year_counts.values, marker='o')
        ax.set_xlabel("Year")
        ax.set_ylabel("Reuse count")
        ax.set_title("Concept reuse count over time (all concepts)")
        st.pyplot(fig)
    else:
        st.write("No reuse years found.")

    st.markdown("---")
    st.subheader("Component details JSON")
    st.json(res)

    # Download
    st.download_button("Download result JSON", json.dumps(res, indent=2), file_name="concept_adoption.json")
```

### 4) Realistic LLM prompts

Use the LLM to produce concise human-friendly summaries of the adoption findings, or to validate whether a phrase is genuinely novel (use with caution — combine with heuristics).

#### A) Summary prompt (explain top concepts & adoption)

```diff
CopyEdit
You are an expert science communicator. Given this Concept Adoption analysis output (JSON), produce a concise 3–4 sentence summary describing:
- whether the paper introduced concepts that are being reused,
- which concepts are most adopted,
- how quickly adoption occurred,
- any caveats (small sample, semantic matches).

Input: {paste JSON}
Output: 2-4 sentences, plain text.
```

#### B) Novelty validation prompt (check if a phrase already exists broadly)

```cpp
CopyEdit
You are a research librarian. Given a short phrase or term, determine whether it likely represents a novel concept (coinage) or an existing common term. Return JSON: {"phrase":"...", "likely_novel": true/false, "explanation":"2-sentence justification and suggested search keywords to verify"}.
Phrase: "react-loss"
```

Note: When using LLMs to judge novelty, always cross-check with external search (Google Scholar, CrossRef, Semantic Scholar) — LLMs can hallucinate.


### 5) Notes, tuning & production advice

* Embeddings & thresholds: sim_threshold_semantic ~ 0.70–0.78 works for sentence-transformers on short phrase→sentence matching; calibrate on your data. For phrase→document semantic match, embedding sentences and checking max similarity is robust.
* Speed / scale:
    * Cache embeddings for citations.
    * For thousands of citations, sample stratified by year/venue or pre-filter likely matches via cheap keyword search before semantic checks.
* Novelty ground-truth:
    * True novelty detection requires global corpus checks (big index or web search). Use your organization’s corpus or APIs (OpenAlex, CrossRef) to validate whether a phrase appears before the paper’s year.
* Formula detection:
    * Complex formulas are best parsed from PDFs / LaTeX sources and normalized (MathML) — our heuristics only catch simple patterns.
* False positives:
    * Exact n-gram matching finds many obvious reuses; semantic matching reduces missed paraphrases but can produce fuzzier matches — report both counts separately (we do).
* Explainability:
    * Show matched contexts (sentence snippets) for human review on the UI (we expose matched docs list).
* Privacy / Ethics:
    * If working with embargoed or unpublished citing-docs, ensure data access rights.


### 6) Example output (trimmed)

```json
CopyEdit
{
  "paper": {"title":"Transformer-Accelerated Reaction Prediction","doi":"10.1000/transreact","year":2022},
  "n_candidates": 12,
  "n_citations": 3,
  "cai": 42.18,
  "concepts": [
    {
      "concept":"transreact",
      "exact_count":2,
      "semantic_count":0,
      "total_matches":2,
      "first_year":2023,
      "years":[2023,2024],
      "velocity":1.0,
      "matched_docs":[{"meta": {"title":"Applying TransReact to Photocatalysis","year":2023}, "exact_matches":1, "semantic_match":false}, ...]
    },
    {
      "concept":"react-loss",
      "exact_count":1,
      "semantic_count":1,
      "total_matches":2,
      "first_year":2023,
      "years":[2023,2024],
      "velocity":1.0
    }
  ]
}
```

### If you want, I can:

* Wire this to OpenAlex / Semantic Scholar to fetch real citing-paper texts and show live results (I’ll provide the API integration code).
* Add a per-concept context viewer in the Streamlit UI showing matched sentence snippets with highlight.
* Provide a batch mode to compute CAI for thousands of papers and export CSV/Parquet.
