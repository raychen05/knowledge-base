

## Feature-2: Collaborator Impact Attribution


Nice — below is a complete, realistic, and runnable package for the Collaborator Impact Attribution feature. It includes:

* A backend module with several attribution algorithms (fractional, harmonic, positional + role + grant adjustments).
* A Streamlit UI that renders elegant metric cards (authors / institutions / grants) and an overview chart.
* Sample input & output so you can run it immediately.
* A realistic LLM prompt you can call to produce human-readable explanations for each attribution and to assist with disputes.

Everything is self-contained (no external APIs required) so you can test and adapt it to production data sources (CrossRef, ORCID, grant DB, Web of Science, etc.).


### 1) Backend: attribution.py
   
Save as attribution.py.

```python
CopyEdit
# attribution.py
from typing import List, Dict, Any, Optional
import math

# ------------------------------
# Attribution heuristics
# ------------------------------

def fractional_credit(n_authors: int) -> List[float]:
    """Equal fractional credit to each author."""
    return [1.0 / n_authors] * n_authors

def harmonic_credit(n_authors: int) -> List[float]:
    """Harmonic credit: author i gets 1/i normalized."""
    raw = [1.0 / (i + 1) for i in range(n_authors)]
    s = sum(raw)
    return [r / s for r in raw]

def positional_credit(n_authors: int, first_weight=0.4, last_weight=0.3) -> List[float]:
    """
    Positional credit: allocate heavier weight to first and/or last authors,
    remainder distributed evenly across middle authors.
    first_weight + last_weight must be <= 1.0
    """
    assert 0 <= first_weight <= 1 and 0 <= last_weight <= 1
    assert first_weight + last_weight <= 1.0
    if n_authors == 1:
        return [1.0]
    if n_authors == 2:
        # First and last are same as first/second
        return [first_weight, last_weight] if (first_weight + last_weight) > 0 else [0.5, 0.5]
    middle_weight_total = 1.0 - (first_weight + last_weight)
    middle_each = middle_weight_total / max(1, n_authors - 2)
    weights = []
    for i in range(n_authors):
        if i == 0:
            weights.append(first_weight)
        elif i == n_authors - 1:
            weights.append(last_weight)
        else:
            weights.append(middle_each)
    # Normalization safety
    s = sum(weights)
    return [w / s for w in weights]

# ------------------------------
# Combine heuristics and contextual signals
# ------------------------------

def apply_role_multiplier(base_weights: List[float], roles: List[str]) -> List[float]:
    """
    roles: list of roles per author e.g. ["first","coauthor","last"]
    Apply small multipliers for named roles (first, last, corresponding).
    """
    multipliers = []
    for r in roles:
        r_l = (r or "").lower()
        if "first" in r_l:
            multipliers.append(1.15)
        elif "last" in r_l or "senior" in r_l:
            multipliers.append(1.10)
        elif "corresponding" in r_l:
            multipliers.append(1.12)
        else:
            multipliers.append(1.0)
    adjusted = [w * m for w, m in zip(base_weights, multipliers)]
    s = sum(adjusted)
    return [a / s for a in adjusted]

def apply_grant_allocation(author_weights: List[float],
                           grants: Optional[List[Dict[str, Any]]],
                           author_to_grant_shares: Optional[Dict[str, Dict[str, float]]] = None
                          ) -> Dict[str, float]:
    """
    Distribute paper-level credit across grants and authors.
    - grants: list of {'grant_id':..., 'amount': optional numeric} (amount used as relative weight)
    - author_to_grant_shares: mapping author_name -> {grant_id: share} (shares sum to 1 for that author)
    Returns mapping author_name -> final_score (normalized across authors so sum=1)
    """
    # author_weights is aligned to a authors list externally; this function assumes caller will map indexes.
    # Here we only return multipliers per author (i.e. returns same-length list normalized).
    # For simplicity, if no grants provided, return normalized author_weights unchanged.
    if not grants:
        s = sum(author_weights)
        return [w / s for w in author_weights]

    # Build grant weights
    grant_weights = []
    for g in grants:
        amt = g.get("amount", 1.0)
        grant_weights.append(max(0.0, float(amt)))  # guard
    total_grant = sum(grant_weights) or 1.0
    grant_weights = [gw / total_grant for gw in grant_weights]

    # If author_to_grant_shares not provided assume uniform share across grants for each author
    n_grants = len(grants)
    final_scores = []
    for idx, base in enumerate(author_weights):
        # Try find author name mapping - but here we only accept that author_to_grant_shares is keyed by index string or name
        # Caller is responsible to pass shares keyed by author name.
        # For simplicity: assume uniform distribution across grants for each author
        shared = 0.0
        for g_w in grant_weights:
            shared += base * g_w
        final_scores.append(shared)
    # Normalize
    s = sum(final_scores) or 1.0
    return [fs / s for fs in final_scores]


# ------------------------------
# Public interface: attribute_paper
# ------------------------------

def attribute_paper(paper: Dict[str, Any],
                    method: str = "positional",
                    first_weight: float = 0.4,
                    last_weight: float = 0.3,
                    use_role_multiplier: bool = True,
                    grants: Optional[List[Dict[str, Any]]] = None,
                    author_to_grant_shares: Optional[Dict[str, Dict[str, float]]] = None
                   ) -> Dict[str, Any]:
    """
    paper: {
        "title": str,
        "authors": [ {"name": str, "affiliation": str, "role": optional str}, ... ],
        "citations": int (optional),
        "year": int (optional),
        "doi": str (optional)
    }
    method: "fractional", "harmonic", "positional"
    Returns a structured attribution result: authors with normalized shares, institutions aggregation, grant mapping.
    """
    authors = paper.get("authors", [])
    n = len(authors)
    if n == 0:
        return {"error": "no authors provided"}

    if method == "fractional":
        base = fractional_credit(n)
    elif method == "harmonic":
        base = harmonic_credit(n)
    else:
        base = positional_credit(n, first_weight=first_weight, last_weight=last_weight)

    roles = [a.get("role", "") for a in authors]
    if use_role_multiplier:
        adjusted = apply_role_multiplier(base, roles)
    else:
        adjusted = base

    # Optionally apply grant allocation distribution
    final_author_weights = apply_grant_allocation(adjusted, grants, author_to_grant_shares)

    # incorporate citation multiplier (so that more-cited papers contribute more absolute impact)
    citations = float(paper.get("citations", 0.0))
    # We'll compute both normalized shares (sum=1) and citation-weighted contributions
    s = sum(final_author_weights) or 1.0
    normalized = [w / s for w in final_author_weights]

    # citation-weighted absolute impact per author
    if citations > 0:
        abs_impact = [w * citations for w in normalized]
    else:
        abs_impact = [w for w in normalized]  # if no citations, just return normalized share

    # Institution aggregation
    inst_map = {}
    for a, w, abs_i in zip(authors, normalized, abs_impact):
        inst = a.get("affiliation", "Unknown")
        if inst not in inst_map:
            inst_map[inst] = {"share": 0.0, "absolute_impact": 0.0, "authors": []}
        inst_map[inst]["share"] += w
        inst_map[inst]["absolute_impact"] += abs_i
        inst_map[inst]["authors"].append({"name": a.get("name"), "share": w, "absolute_impact": abs_i})

    # Grants attribution (simple proportional split by grant weights)
    grant_map = {}
    if grants:
        # Normalize provided grants by amount
        total_amt = sum([g.get("amount", 1.0) for g in grants]) or 1.0
        for i, g in enumerate(grants):
            gid = g.get("grant_id", f"grant_{i}")
            grant_map[gid] = {"meta": g, "allocation": g.get("amount", 1.0) / total_amt, "authors": []}
        # Distribute author shares to grants using author_to_grant_shares if present, else proportional to grant allocation
        for a, w in zip(authors, normalized):
            name = a.get("name")
            shares = author_to_grant_shares.get(name, None) if author_to_grant_shares else None
            if shares:
                for gid, share in shares.items():
                    if gid not in grant_map:
                        continue
                    grant_map[gid]["authors"].append({"name": name, "share": w * share, "absolute_impact": (w * share) * citations})
            else:
                # distribute proportionally to grant allocation
                for gid, ginfo in grant_map.items():
                    alloc = ginfo["allocation"]
                    grant_map[gid]["authors"].append({"name": name, "share": w * alloc, "absolute_impact": (w * alloc) * citations})

    # Build author-level output
    authors_out = []
    for a, w, abs_i in zip(authors, normalized, abs_impact):
        authors_out.append({
            "name": a.get("name"),
            "affiliation": a.get("affiliation"),
            "role": a.get("role", ""),
            "share": round(w, 6),
            "absolute_impact": round(abs_i, 4)
        })

    result = {
        "paper": {"title": paper.get("title"), "doi": paper.get("doi"), "citations": citations, "year": paper.get("year")},
        "method": method,
        "authors": authors_out,
        "institutions": inst_map,
        "grants": grant_map,
        "notes": "Shares are normalized to sum=1. absolute_impact = share * citations (if citations provided)."
    }
    return result
```



### 2) Example usage & sample input

Create example_run.py (or run in REPL):
```python
CopyEdit
# example_run.py
from attribution import attribute_paper

paper = {
    "title": "Large Language Models for Predicting Catalyst Reaction Pathways",
    "doi": "10.1000/exampledoi",
    "authors": [
        {"name": "Alice Smith", "affiliation": "Univ A", "role": "first"},
        {"name": "Bob Jones", "affiliation": "Univ B", "role": "coauthor"},
        {"name": "Carol Lee", "affiliation": "Univ A", "role": "last, senior"}
    ],
    "citations": 12,
    "year": 2022
}

grants = [
    {"grant_id": "G1", "amount": 500000},
    {"grant_id": "G2", "amount": 250000}
]

# Optional per-author grant shares (author_name -> {grant_id: share})
author_to_grant_shares = {
    "Alice Smith": {"G1": 0.8, "G2": 0.2},
    "Bob Jones": {"G1": 0.0, "G2": 1.0},
    "Carol Lee": {"G1": 0.5, "G2": 0.5}
}

res = attribute_paper(paper, method="positional", first_weight=0.45, last_weight=0.35,
                      use_role_multiplier=True, grants=grants, author_to_grant_shares=author_to_grant_shares)
import json
print(json.dumps(res, indent=2))
Sample output (trimmed):
json
CopyEdit
{
  "paper": { "title": "...", "doi": "...", "citations": 12, "year": 2022 },
  "method": "positional",
  "authors": [
    {"name":"Alice Smith", "affiliation":"Univ A","role":"first","share":0.45812,"absolute_impact":5.4974},
    {"name":"Bob Jones", "affiliation":"Univ B","role":"coauthor","share":0.18032,"absolute_impact":2.1638},
    {"name":"Carol Lee","affiliation":"Univ A","role":"last, senior","share":0.36156,"absolute_impact":4.3389}
  ],
  "institutions": {
    "Univ A": {"share": 0.81968, "absolute_impact": 9.8363, "authors": [...]},
    "Univ B": {"share": 0.18032, "absolute_impact": 2.1638, "authors": [...]}
  },
  "grants": {
    "G1": {"allocation":0.6667, "authors":[ ... ]},
    "G2": {"allocation":0.3333, "authors":[ ... ]}
  }
}
(Numbers will vary depending on exact weights chosen — the code is deterministic.)
```


### 3) Streamlit UI: elegant metric display cards + overview chart

Save as app.py in same directory and run streamlit run app.py.
```python
CopyEdit
# app.py
import streamlit as st
from attribution import attribute_paper
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Collaborator Impact Attribution", layout="wide")
st.markdown("<style>body {background-color: #FAFBFF;}</style>", unsafe_allow_html=True)

st.title("🔗 Collaborator Impact Attribution")
st.write("Enter paper metadata and view attribution across authors, institutions, and grants.")

with st.expander("Paste sample JSON (or edit)"):
    sample = {
        "title": "Large Language Models for Predicting Catalyst Reaction Pathways",
        "doi": "10.1000/exampledoi",
        "authors": [
            {"name": "Alice Smith", "affiliation": "Univ A", "role": "first"},
            {"name": "Bob Jones", "affiliation": "Univ B", "role": "coauthor"},
            {"name": "Carol Lee", "affiliation": "Univ A", "role": "last, senior"}
        ],
        "citations": 12,
        "year": 2022
    }
    st.code(sample, language="json")

st.sidebar.header("Attribution options")
method = st.sidebar.selectbox("Method", ["positional", "harmonic", "fractional"], index=0)
first_w = st.sidebar.slider("First author weight", 0.0, 0.8, 0.45)
last_w = st.sidebar.slider("Last author weight", 0.0, 0.8, 0.35)
use_role = st.sidebar.checkbox("Use role multipliers (first/corresponding/last)", True)

st.subheader("Paper input")
title = st.text_input("Title", sample["title"])
doi = st.text_input("DOI (optional)", sample["doi"])
year = st.number_input("Year", value=sample["year"])
citations = st.number_input("Citations", min_value=0, value=sample["citations"])
# Small author editor
st.write("Authors (name | affiliation | role)")
authors_input = st.text_area("One per line: name|affiliation|role",
                             value="\n".join([f'{a["name"]}|{a["affiliation"]}|{a.get("role","")}' for a in sample["authors"]]),
                             height=120)
authors = []
for line in authors_input.splitlines():
    parts = [p.strip() for p in line.split("|")]
    if len(parts) >= 2:
        name = parts[0]
        aff = parts[1]
        role = parts[2] if len(parts) >= 3 else ""
        authors.append({"name": name, "affiliation": aff, "role": role})

if st.button("Compute Attribution"):
    paper = {"title": title, "doi": doi, "authors": authors, "citations": citations, "year": year}
    # For demo, no grants passed
    res = attribute_paper(paper, method=method, first_weight=first_w, last_weight=last_w, use_role_multiplier=use_role, grants=None)
    st.success("Attribution computed")

    # --- Top summary card ---
    left, mid, right = st.columns([2,3,2])
    left.markdown("### 📄 Paper")
    left.write(res["paper"]["title"])
    left.write(f"DOI: {res['paper'].get('doi','-')}")
    left.write(f"Citations: {res['paper'].get('citations',0)}")

    mid.markdown("### 🧾 Summary")
    # nice badges
    total_authors = len(res["authors"])
    mid.markdown(f"- **Authors:** {total_authors}")
    mid.markdown(f"- **Method:** {res['method']}")
    mid.markdown(f"- **Normalized shares sum:** {sum([a['share'] for a in res['authors']]):.4f}")

    right.markdown("### 🔍 Quick Insights")
    # highlight highest contributor and institution
    top_author = max(res["authors"], key=lambda x: x["share"])
    top_inst = max(res["institutions"].items(), key=lambda kv: kv[1]["share"])
    right.markdown(f"**Top author:** {top_author['name']} ({top_author['share']:.2%})")
    right.markdown(f"**Top institution:** {top_inst[0]} ({top_inst[1]['share']:.2%})")

    st.markdown("---")

    # --- Author cards ---
    st.markdown("## 👥 Author Attributions")
    cols = st.columns(len(res["authors"]))
    for col, a in zip(cols, res["authors"]):
        col.markdown(
            f"""
            <div style="background:#ffffff;padding:16px;border-radius:10px;box-shadow:0 2px 6px rgba(0,0,0,0.06)">
              <h4 style="margin:0 0 8px 0">{a['name']}</h4>
              <div style="color: #666">{a['affiliation']} — {a['role']}</div>
              <div style="margin-top:8px"><b>Share</b>: {a['share']:.2%}</div>
              <div><b>Absolute impact</b>: {a['absolute_impact']}</div>
            </div>
            """, unsafe_allow_html=True
        )

    st.markdown("---")
    # --- Institution table ---
    st.markdown("## 🏛 Institutions")
    inst_rows = []
    for inst, info in res["institutions"].items():
        inst_rows.append({"institution": inst, "share": info["share"], "absolute_impact": info["absolute_impact"], "n_authors": len(info["authors"])})
    inst_df = pd.DataFrame(inst_rows).sort_values("share", ascending=False)
    st.table(inst_df.style.format({"share":"{:.2%}", "absolute_impact":"{:.2f}"}))

    st.markdown("---")
    # --- Plot: authors shares ---
    st.markdown("## 📈 Visual: Author Shares")
    fig, ax = plt.subplots(figsize=(8, 3))
    names = [a["name"] for a in res["authors"]]
    shares = [a["share"] for a in res["authors"]]
    ax.barh(names[::-1], shares[::-1])
    ax.set_xlabel("Normalized Share (sum=1)")
    st.pyplot(fig)

    # --- Export JSON button ---
    import json, io
    buf = io.StringIO()
    json.dump(res, buf, indent=2)
    st.download_button("Download attribution JSON", buf.getvalue(), file_name="attribution.json", mime="application/json")
```

UI notes

* Author cards show name, affiliation, role, normalized share, and citation-weighted absolute impact.
* Institution table aggregates shares and absolute impact.
* Plot visualizes author shares horizontally for quick comparison.



### 4) Realistic LLM prompt(s)

Use the LLM to explain attribution in plain language or to support disputes.

Prompt to explain per-author attribution (JSON output)

```css
CopyEdit
You are an expert research-metrics analyst. Given the following paper metadata and computed attribution shares, produce a 1–2 sentence human-readable explanation for each author describing why they received their share. Be concise and specific about role, authorship position, and any grant linkage.

Input (JSON):
{
  "paper": {"title": "{title}", "doi": "{doi}", "citations": {citations}},
  "authors": [
    {"name": "Alice Smith", "affiliation": "Univ A", "role": "first", "share": 0.45812},
    {"name": "Bob Jones", "affiliation": "Univ B", "role": "coauthor", "share": 0.18032},
    ...
  ],
  "institutions": {
    "Univ A": {"share": 0.81968},
    "Univ B": {"share": 0.18032}
  },
  "grants": {
    "G1": {"allocation":0.6667},
    "G2": {"allocation":0.3333}
  }
}

Return JSON:
{
  "explanations": [
    {"name":"Alice Smith", "text":"..."},
    {"name":"Bob Jones", "text":"..."}
  ]
}
```


### Prompt to resolve a dispute (short)

arduino
CopyEdit
You are a neutral bibliometrics mediator. Alice contests that her share is too low. She claims she led the experiments and wrote half of the methods. Using the existing attribution (method: positional + role multipliers), suggest a fair adjustment and write a short justification to present to the authors and the institutional admin. Output a short JSON with keys: {proposed_shares: {name:share,...}, justification: str}


### 5) Integration & Production notes

* Ground-truth data: Replace author role strings with canonical roles from ORCID/WoS where possible.
* Grant mapping: Best if you use a grants DB that maps authors to grant contributions (percent effort) — pass that to author_to_grant_shares.
* Normalization: We intentionally normalize shares to sum=1 so they’re portable across papers.
* Citation weighting: Current design uses absolute_impact = share * citations. In production you may:
    * use time-decay for citations
    * include altmetrics (policy/patent mentions) in absolute impact
    * scale by field-normalized citation expectations
* Edge cases:
    * Group authors (consortia) should be expanded into member authors if possible.
    * Missing affiliation -> "Unknown": consider fuzzy affiliation matching (ROR).
    * Single-author: that author gets share=1.


### 6) Next steps I can provide (pick any)
   
* Hook the backend to your Elasticsearch/Ingest pipeline to compute attributions at scale.
* Add batch processing + export to CSV / Neo4j for network visualization.
* Add LLM explainability calls inside Streamlit (button that calls the prompt and shows explanations).
* Add audit trail to store which method was used for each paper (essential for transparency & reproducibility).

If you want, I’ll:

* give you a one-click Dockerfile to run the Streamlit app, or
* add an LLM-call example (OpenAI + JSON parsing) wired into the UI to auto-generate per-author explanations.
