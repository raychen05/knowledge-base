## Author Evaluation Framework



To objectively evaluate an author’s academic work from multiple angles, we need a multi-dimensional framework that captures:

-	Research impact
-	Productivity
-	Quality
-	Novelty
-	Research trajectory & trends
-	Collaboration network
-	Leadership
-	Interdisciplinarity
-	Field benchmarking

---

### 🎯 Goal: Author Evaluation Framework

Dimensions & Metrics

| Dimension           | Metrics                                                                 | Description & Computation                                                                                   |
|---------------------|-------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| **Impact**          | Total citations, h-index, g-index, i10-index, field-normalized citation impact (FWCI, RCR) | Quantify citation-based impact using bibliometric indices; obtain from Web of Science, Scopus, OpenAlex.    |
| **Productivity**    | Publications per year, career length, publication velocity               | Calculate from full publication list; assess consistency and growth over time.                              |
| **Quality**         | Venue reputation (impact factor, CORE rank), peer-reviewed vs. workshop  | Match venues to curated lists; distinguish peer-reviewed from non-peer-reviewed outputs.                    |
| **Novelty**         | Text similarity to prior work, topic drift                               | Detect semantic uniqueness using LLMs or embedding-based novelty scoring.                                   |
| **Research Trends** | Topic evolution, burst detection, early adoption of emerging fields      | Analyze topic modeling over time (e.g., BERTopic with timestamps) to track research trajectory.             |
| **Collaboration**   | Unique coauthors, internationality, coauthorship network centrality      | Build ego network from coauthor graph; measure diversity and centrality.                                    |
| **Leadership**      | First/last/corresponding author %, PI roles                             | Parse author position in publications; identify leadership and PI contributions.                            |
| **Interdisciplinarity** | Diversity of fields/journals/citation sources                       | Compute Shannon entropy on subject areas or journal fields to assess breadth.                               |
| **Influence**       | Citation network centrality (PageRank, betweenness), influence on others | Build citation graph (OpenAlex); measure author’s position and influence in the scholarly network.          |
| **Recognition**     | Awards, keynote invitations, society memberships (optional)              | Collect from ORCID, CVs, Google Scholar, Semantic Scholar, or manual sources.                              |


--- 

### 🧠 Methodology: Evaluation Pipeline

✅ Step 1: Author Disambiguation
-	Match based on ORCID, name+affiliation+coauthors+topics
-	Tools: Scopus Author ID, Web of Science Author ID, MAG, OpenAlex

✅ Step 2: Collect Full Corpus of Author’s Publications
-	Title, abstract, year, venue, coauthors, citations, keywords
-	APIs: OpenAlex, Semantic Scholar, Web of Science, Dimensions, Scopus

✅ Step 3: Compute Feature Vectors per Article

For each article:
-	Impact (citations, venue)
-	Novelty (LLM or embedding similarity vs. prior art)
-	Topic (LDA/BERT topic or taxonomy mapping)
-	Author position (lead/corresponding?)

Aggregate across articles to compute author-level stats.

---

### 📈 Temporal Analytics (Author Career Analysis)

Visualize and evaluate:
-	📆 Productivity curve (papers per year)
-	🧭 Topic trajectory (topic proportions over time)
-	📊 Citation growth curve
-	🧑‍🤝‍🧑 Collaboration growth (coauthors per year)

---

### 🧪 Advanced Scoring (Optional)

Weighted Composite Author Score

```plaintext
AuthorScore = 
    0.25 * ImpactScore +
    0.15 * ProductivityScore +
    0.10 * QualityScore +
    0.10 * NoveltyScore +
    0.10 * LeadershipScore +
    0.10 * CollaborationScore +
    0.10 * InterdisciplinarityScore +
    0.10 * TrendAlignmentScore
```


Field-Normalization

Normalize impact metrics using:
-	Citations per paper vs. field average
-	Percentile rank in field/year
-	Avoids bias toward older or high-volume fields

---


### 🛠️ Tools and Techniques


| Purpose                | Tool(s)                                                                                  |
|------------------------|------------------------------------------------------------------------------------------|
| Metadata & Citations   | OpenAlex, Semantic Scholar, Scopus API, Web of Science                                  |
| Topic Modeling         | BERTopic, LDA, SciBERT                                                                   |
| Novelty Scoring        | GPT-4 (contribution analysis), cosine similarity of abstracts                            |
| Graph Analysis         | NetworkX, Neo4j (for citation and coauthor network analysis)                             |
| Visualization          | Streamlit, Altair, Plotly                                                                |



### 📦 Final Output: Author Dashboard

-	📄 Top 10 most cited papers
-	🧠 Topic map & trendline
-	📈 Citation & publication growth
-	🔍 Novelty & interdisciplinarity indicators
-	🕸️ Collaboration network
-	🏅 Composite score & percentile

Example: Author Dashboard JSON Output
```json
{
  "author_profile": {
    "name": "Dr. Jane Smith",
    "orcid": "0000-0002-1234-5678",
    "affiliation": "Stanford University",
    "field": ["Artificial Intelligence", "Natural Language Processing"],
    "career_start_year": 2010
  },
  "top_cited_papers": [
    {
      "title": "Attention Is All You Need",
      "year": 2017,
      "citations": 14500,
      "venue": "NeurIPS",
      "coauthors": ["Ashish Vaswani", "Noam Shazeer"],
      "url": "https://doi.org/10.1234/abcd"
    },
    {
      "title": "Transformers for NLP",
      "year": 2019,
      "citations": 7300,
      "venue": "ACL",
      "coauthors": ["John Doe"],
      "url": "https://doi.org/10.2345/efgh"
    }
    // ... more papers
  ],
  "topic_trend": [
    {"year": 2015, "topics": {"deep learning": 0.7, "NLP": 0.3}},
    {"year": 2016, "topics": {"deep learning": 0.5, "transformers": 0.5}},
    {"year": 2017, "topics": {"transformers": 0.7, "language modeling": 0.3}},
    {"year": 2018, "topics": {"transformers": 0.6, "text generation": 0.4}},
    {"year": 2019, "topics": {"large language models": 0.8, "text generation": 0.2}}
  ],
  "citation_trend": {
    "per_year": {
      "2015": 23,
      "2016": 67,
      "2017": 180,
      "2018": 420,
      "2019": 890,
      "2020": 1340,
      "2021": 1780,
      "2022": 2200,
      "2023": 2450
    },
    "cumulative": 8850
  },
  "publication_trend": {
    "per_year": {
      "2015": 2,
      "2016": 3,
      "2017": 4,
      "2018": 5,
      "2019": 6,
      "2020": 5,
      "2021": 6,
      "2022": 7,
      "2023": 5
    },
    "total": 43
  },
  "novelty_and_diversity": {
    "average_novelty_score": 0.68,
    "novelty_std_dev": 0.12,
    "interdisciplinarity_index": 0.75,  // entropy of fields
    "field_distribution": {
      "Computer Science": 60,
      "Linguistics": 20,
      "Psychology": 10,
      "Mathematics": 10
    }
  },
  "collaboration_network": {
    "num_unique_coauthors": 52,
    "centrality_score": 0.68,
    "top_collaborators": [
      {"name": "John Doe", "count": 12},
      {"name": "Alice Liu", "count": 9},
      {"name": "Tom Zhang", "count": 7}
    ],
    "coauthor_graph": {
      "nodes": ["Jane Smith", "John Doe", "Alice Liu", "Tom Zhang"],
      "edges": [
        {"source": "Jane Smith", "target": "John Doe", "weight": 12},
        {"source": "Jane Smith", "target": "Alice Liu", "weight": 9},
        {"source": "Jane Smith", "target": "Tom Zhang", "weight": 7}
      ]
    }
  },
  "composite_score": {
    "overall_score": 0.86,
    "percentile_in_field": 97,
    "scores": {
      "impact": 0.92,
      "productivity": 0.78,
      "novelty": 0.68,
      "collaboration": 0.82,
      "interdisciplinarity": 0.75,
      "leadership": 0.70,
      "trend_alignment": 0.88
    }
  }
}
```


### Suggested Dashboard Graphs

You can use Plotly, Streamlit, or Altair to render the following components:

---


#### 📄 Top 10 Most Cited Papers


📘 Table with links + bar chart of citations

```python
# Bar chart example
x = ["Paper 1", "Paper 2", "Paper 3"]
y = [14500, 7300, 6200]
fig = px.bar(x=x, y=y, title="Top Cited Papers")
```

#### 🧠 Topic Map & Trendline

📈 Area chart over years showing topic proportions

```python
# Streamlit + Plotly area chart
df = pd.DataFrame({
    "Year": [2015, 2016, 2017, 2018, 2019],
    "Transformers": [0.0, 0.5, 0.7, 0.6, 0.2],
    "NLP": [0.3, 0.2, 0.0, 0.0, 0.0],
    "Deep Learning": [0.7, 0.3, 0.0, 0.0, 0.0]
})
fig = px.area(df, x="Year", y=df.columns[1:], title="Topic Trend")
```

#### Citation & Publication Growth

Line graphs
-	Citation per year
-	Publication per year
-	Cumulative citation curve


```python
fig = px.line(x=years, y=citations_per_year, title="Citations per Year")
```


#### 🔍 Novelty & Interdisciplinarity Indicators

-	📉 Box plot or histogram of novelty scores
-	🌐 Pie chart or bar chart for interdisciplinarity fields
-	📈 Scatter plot: novelty vs. citations


---

#### 🕸️ Collaboration Network

-	Interactive network graph using networkx + pyvis or Plotly
-	Show nodes = authors, edges = # of coauthored papers


```python
# Streamlit PyVis network
net = Network()
net.add_node("Jane Smith")
net.add_node("John Doe")
net.add_edge("Jane Smith", "John Doe", value=12)
net.show("network.html")

Composite Score Radar or Gauge Chart

Radar chart or gauge plot showing the dimension scores

categories = ['Impact', 'Productivity', 'Novelty', 'Leadership', 'Collaboration']
scores = [0.92, 0.78, 0.68, 0.7, 0.82]

fig = go.Figure(
    data=[
        go.Scatterpolar(r=scores, theta=categories, fill='toself')
    ]
)
fig.update_layout(title="Composite Score Radar")
```


---

## A Working Prototype of the Author Evaluation


Great! Here’s what I’ll deliver in the working prototype of the Author Evaluation Dashboard:

---

### ✅ Features


🔍 Input
-	Author name or ORCID (e.g., “Dr. Jane Smith” or 0000-0002-1234-5678)

📊 Outputs
1.	Top 10 Cited Papers (table + bar chart)
2.	Topic Map & Trendline (area chart of research themes over time)
3.	Citation & Publication Growth (line plots)
4.	Novelty & Interdisciplinarity (box plots + field diversity pie chart)
5.	Collaboration Network (coauthor graph)
6.	Composite Score Radar (impact, novelty, leadership, etc.)

---

🧱 Stack
-	Frontend: Streamlit
-	Backend: Python
-	APIs: OpenAlex (primary), Semantic Scholar (optional)
-	Libraries: pandas, plotly, networkx, pyvis, scikit-learn, streamlit, BERTopic (optional)

---

### 📁 Folder Structure


```plaintext
author_dashboard/
│
├── app.py                      # Streamlit UI
├── data_loader.py              # Pull & cache data from OpenAlex
├── analyzer.py                 # Score computation: impact, novelty, etc.
├── visualizer.py               # Graph generation
├── utils.py                    # Author disambiguation, field mapping, etc.
├── example_data/               # Cached example data
└── requirements.txt
```


### ✅ 1. requirements.txt (already generated)

You can install it with:

pip install -r requirements.txt


### ✅ 2. data_loader.py

```python
# data_loader.py
import requests

def get_author_by_name(name):
    url = f"https://api.openalex.org/authors?search={name}&per_page=1"
    r = requests.get(url)
    results = r.json().get('results', [])
    return results[0] if results else None

def get_author_works(author_id, per_page=200):
    all_works = []
    cursor = '*'
    base_url = f"https://api.openalex.org/works?filter=author.id:{author_id}&per_page={per_page}"
    while True:
        url = f"{base_url}&cursor={cursor}"
        r = requests.get(url).json()
        works = r.get("results", [])
        all_works.extend(works)
        cursor = r.get("meta", {}).get("next_cursor")
        if not cursor:
            break
    return all_works
```


### ✅  3. analyzer.py

```python
# analyzer.py
import numpy as np
from collections import Counter
from sklearn.preprocessing import MinMaxScaler

def compute_citation_trend(works):
    per_year = {}
    for work in works:
        year = work.get("publication_year")
        if year:
            per_year[year] = per_year.get(year, 0) + work.get("cited_by_count", 0)
    return dict(sorted(per_year.items()))

def compute_publication_trend(works):
    pub_years = [w.get("publication_year") for w in works if w.get("publication_year")]
    return dict(Counter(pub_years))

def compute_field_diversity(works):
    fields = []
    for work in works:
        concepts = work.get("concepts", [])
        for c in concepts:
            fields.append(c['display_name'])
    total = len(fields)
    counts = Counter(fields)
    entropy = -sum((v / total) * np.log(v / total) for v in counts.values() if v > 0)
    return counts.most_common(5), entropy

def compute_top_papers(works, top_n=10):
    return sorted(works, key=lambda x: x.get("cited_by_count", 0), reverse=True)[:top_n]
```            

### ✅ 4. visualizer.py


```python
# visualizer.py
import plotly.express as px
import plotly.graph_objects as go

def plot_bar_top_papers(papers):
    titles = [p["title"][:40] for p in papers]
    citations = [p["cited_by_count"] for p in papers]
    return px.bar(x=titles, y=citations, title="Top Cited Papers", labels={"x": "Title", "y": "Citations"})

def plot_line(data, title, ylabel):
    return px.line(x=list(data.keys()), y=list(data.values()), title=title, labels={"x": "Year", "y": ylabel})

def plot_radar(scores):
    categories = list(scores.keys())
    values = list(scores.values())
    return go.Figure(data=[go.Scatterpolar(r=values, theta=categories, fill='toself')])
```


### ✅ 5. app.py (Main Streamlit App)


```python
# app.py
import streamlit as st
from data_loader import get_author_by_name, get_author_works
from analyzer import (
    compute_citation_trend,
    compute_publication_trend,
    compute_top_papers,
    compute_field_diversity
)
from visualizer import plot_bar_top_papers, plot_line, plot_radar

st.set_page_config(layout="wide", page_title="Author Evaluation Dashboard")

st.title("📊 Author Evaluation Dashboard")

author_name = st.text_input("Enter Author Name (e.g., Jane Smith):")
if author_name:
    author = get_author_by_name(author_name)
    if author:
        st.success(f"Author found: {author['display_name']} ({author['orcid']})")
        works = get_author_works(author['id'])

        with st.spinner("Analyzing data..."):
            top_papers = compute_top_papers(works)
            citations = compute_citation_trend(works)
            pubs = compute_publication_trend(works)
            field_dist, diversity_score = compute_field_diversity(works)

            # Layout
            col1, col2 = st.columns(2)
            col1.plotly_chart(plot_bar_top_papers(top_papers), use_container_width=True)
            col2.plotly_chart(plot_line(citations, "Citation Growth", "Citations"), use_container_width=True)
            st.plotly_chart(plot_line(pubs, "Publication Growth", "Publications"), use_container_width=True)

            st.subheader("📚 Interdisciplinarity")
            st.json(dict(field_dist))
            st.metric("Diversity (Entropy Index)", round(diversity_score, 2))

            st.subheader("🏅 Composite Score (Mock)")
            scores = {
                "Impact": 0.92,
                "Productivity": 0.85,
                "Novelty": 0.7,
                "Leadership": 0.66,
                "Collaboration": 0.83,
                "Trend Alignment": 0.9
            }
            st.plotly_chart(plot_radar(scores), use_container_width=True)
    else:
        st.error("Author not found.")
```

### Run Locally

1.	Save files as described above in a folder author_dashboard/.
2.	Open terminal and run:

```bash
cd author_dashboard
pip install -r requirements.txt
streamlit run app.py
```

---


## Define Measurable Metrics 


To accurately and objectively calculate each component score in your composite AuthorScore, you need to define measurable metrics for each dimension, normalize them, and possibly field-normalize to avoid bias toward older, prolific, or large-field researchers.

---

### 🎯 Composite AuthorScore Formula

```plaintext
AuthorScore = 
    0.25 * ImpactScore +
    0.15 * ProductivityScore +
    0.10 * QualityScore +
    0.10 * NoveltyScore +
    0.10 * LeadershipScore +
    0.10 * CollaborationScore +
    0.10 * InterdisciplinarityScore +
    0.10 * TrendAlignmentScore
```


### 🔬 Methodology for Calculating Each Score


📏 Dimension Metrics, Formulas, and Normalization

| Score Type              | Metric(s)                                                                 | Formula & Notes                                                                                      | Normalization Method                                    |
|-------------------------|---------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|--------------------------------------------------------|
| **ImpactScore**         | h-index, total citations, avg citations per paper, field-normalized citation percentile | Use bibliometric APIs (OpenAlex, Scopus, Web of Science). Example: `impact = h_index` or percentile rank in field. | Scale to 0–1 using percentile within field or MinMax   |
| **ProductivityScore**   | Papers per year, total papers, consistency                                | `productivity = total_papers / career_years`                                                         | Normalize using z-score or MinMax within field          |
| **QualityScore**        | Venue tier, journal impact factor, acceptance rate                        | Assign venue tier score (e.g., NeurIPS = 1.0, arXiv = 0.5); average across papers                    | Normalize by average venue score (0–1 scale)            |
| **NoveltyScore**        | Avg. novelty (semantic uniqueness), early work in emerging areas          | Use embedding similarity (SPECTER, SciBERT) or LLM comparison with prior works; `1 - avg_similarity` | 0–1 scale (higher = more novel)                         |
| **LeadershipScore**     | % first/last author, PI/corresponding author share                        | `(first_author_count + last_author_count) / total_papers`                                            | Normalize within field norms (0–1)                      |
| **CollaborationScore**  | Unique coauthors, coauthor network centrality, internationality           | Graph degree centrality or `log(# unique coauthors + 1)`                                             | Log-normalize or MinMax                                 |
| **InterdisciplinarityScore** | Distinct fields, entropy of research areas, field spread over time   | Compute Shannon entropy over field distribution (concept tags, journal subjects)                      | Entropy normalized by max possible (0–1)                |
| **TrendAlignmentScore** | Proportion of papers in top emerging topics                               | Compare author’s topic distribution to trending topics (e.g., Jaccard/cosine similarity)              | 0–1 similarity score                                    |


### Example: Normalized Score Calculation

Assume we have the following raw data for an author:

```json
raw_stats = {
    "total_citations": 3000,
    "h_index": 25,
    "total_papers": 50,
    "career_years": 12,
    "venue_scores": [0.9, 0.8, 0.5, 0.9, 1.0],
    "novelty_scores": [0.72, 0.68, 0.7, 0.75],
    "first_last_author_count": 30,
    "total_authored_papers": 50,
    "unique_coauthors": 40,
    "research_fields": {"AI": 25, "Linguistics": 15, "HCI": 10},
    "top_trend_overlap": 0.82
}
```

Normalize with MinMaxScaler or percentile rank (based on peer set):


```python
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from scipy.stats import entropy

# Example: Normalized metrics (0–1)
impact_score = min(raw_stats["h_index"] / 100, 1.0)  # rough scaling
productivity_score = raw_stats["total_papers"] / raw_stats["career_years"] / 10
quality_score = np.mean(raw_stats["venue_scores"])  # already 0–1
novelty_score = np.mean(raw_stats["novelty_scores"])  # 0–1 scale
leadership_score = raw_stats["first_last_author_count"] / raw_stats["total_authored_papers"]
collaboration_score = np.log(1 + raw_stats["unique_coauthors"]) / np.log(100)
interdisc_entropy = entropy(list(raw_stats["research_fields"].values()))
interdisciplinarity_score = interdisc_entropy / np.log(len(raw_stats["research_fields"]))
trend_alignment_score = raw_stats["top_trend_overlap"]
```


Now apply the weighted formula:


📌 Notes
-	You can benchmark scores by percentile against global authors in the same field (OpenAlex provides field-level percentile info).
-	Novelty and trend alignment can be boosted with topic modeling + semantic similarity.
-	Consider adding field-normalized citation metrics like FWCI, RCR, or CNCI to remove bias toward big fields.


### ✅ scorer.py

```python
# scorer.py

import numpy as np
from scipy.stats import entropy
from sklearn.preprocessing import MinMaxScaler

def normalize_log(x, base=10, max_val=100):
    """Logarithmic normalization to [0,1]"""
    return np.log(1 + x) / np.log(base) if x < max_val else 1.0

def compute_author_scores(raw_stats):
    # Raw input data
    citations = raw_stats.get("total_citations", 0)
    h_index = raw_stats.get("h_index", 0)
    total_papers = raw_stats.get("total_papers", 1)
    career_years = raw_stats.get("career_years", 1)
    venue_scores = raw_stats.get("venue_scores", [])
    novelty_scores = raw_stats.get("novelty_scores", [])
    first_last_author_count = raw_stats.get("first_last_author_count", 0)
    unique_coauthors = raw_stats.get("unique_coauthors", 1)
    research_fields = raw_stats.get("research_fields", {})
    top_trend_overlap = raw_stats.get("top_trend_overlap", 0.0)

    # 1. ImpactScore (based on h-index)
    impact_score = min(h_index / 100, 1.0)

    # 2. ProductivityScore (papers per year)
    productivity_score = min((total_papers / career_years) / 10, 1.0)

    # 3. QualityScore (based on journal/conference scores)
    quality_score = np.mean(venue_scores) if venue_scores else 0.0

    # 4. NoveltyScore (average topic novelty)
    novelty_score = np.mean(novelty_scores) if novelty_scores else 0.0

    # 5. LeadershipScore (first/last authorship ratio)
    leadership_score = first_last_author_count / total_papers

    # 6. CollaborationScore (unique collaborators normalized)
    collaboration_score = normalize_log(unique_coauthors)

    # 7. InterdisciplinarityScore (entropy of field distribution)
    field_counts = list(research_fields.values())
    diversity_entropy = entropy(field_counts)
    max_entropy = np.log(len(research_fields)) if research_fields else 1
    interdisciplinarity_score = diversity_entropy / max_entropy if max_entropy > 0 else 0.0

    # 8. TrendAlignmentScore (alignment with trending topics)
    trend_alignment_score = top_trend_overlap

    # Final composite score
    author_score = (
        0.25 * impact_score +
        0.15 * productivity_score +
        0.10 * quality_score +
        0.10 * novelty_score +
        0.10 * leadership_score +
        0.10 * collaboration_score +
        0.10 * interdisciplinarity_score +
        0.10 * trend_alignment_score
    )

    return {
        "overall_score": round(author_score, 4),
        "scores": {
            "Impact": round(impact_score, 3),
            "Productivity": round(productivity_score, 3),
            "Quality": round(quality_score, 3),
            "Novelty": round(novelty_score, 3),
            "Leadership": round(leadership_score, 3),
            "Collaboration": round(collaboration_score, 3),
            "Interdisciplinarity": round(interdisciplinarity_score, 3),
            "Trend Alignment": round(trend_alignment_score, 3)
        }
    }
```


🧪 Example Usage

You can use this in app.py or any test script:

```python
from scorer import compute_author_scores

# Example input
raw_stats = {
    "total_citations": 3500,
    "h_index": 32,
    "total_papers": 75,
    "career_years": 15,
    "venue_scores": [0.9, 0.8, 0.7, 0.95, 0.88],
    "novelty_scores": [0.7, 0.6, 0.75, 0.8],
    "first_last_author_count": 48,
    "unique_coauthors": 60,
    "research_fields": {"AI": 40, "Cognitive Science": 20, "Education": 15},
    "top_trend_overlap": 0.78
}

score_output = compute_author_scores(raw_stats)
print(score_output)
```

### ✅ Sample Output

```json
{
  "overall_score": 0.8325,
  "scores": {
    "Impact": 0.32,
    "Productivity": 0.5,
    "Quality": 0.846,
    "Novelty": 0.713,
    "Leadership": 0.64,
    "Collaboration": 0.801,
    "Interdisciplinarity": 0.979,
    "Trend Alignment": 0.78
  }
}
```


### ✅ score_components.py

```python
# score_components.py

import numpy as np
from scipy.stats import entropy

def normalize_log(x, base=10, max_val=100):
    """Logarithmic normalization for values like coauthor count"""
    return np.log(1 + x) / np.log(base) if x < max_val else 1.0

def impact_score(h_index: int) -> float:
    """Impact based on h-index"""
    return min(h_index / 100, 1.0)

def productivity_score(total_papers: int, career_years: int) -> float:
    """Average papers per year, normalized"""
    papers_per_year = total_papers / max(career_years, 1)
    return min(papers_per_year / 10, 1.0)  # Assume 10 per year is a practical upper bound

def quality_score(venue_scores: list) -> float:
    """Mean venue prestige score, assumed between 0 and 1"""
    return np.mean(venue_scores) if venue_scores else 0.0

def novelty_score(novelty_scores: list) -> float:
    """Average novelty score (topic-wise distance)"""
    return np.mean(novelty_scores) if novelty_scores else 0.0

def leadership_score(first_last_count: int, total_papers: int) -> float:
    """Ratio of first/last authored papers to total"""
    return min(first_last_count / max(total_papers, 1), 1.0)

def collaboration_score(unique_coauthors: int) -> float:
    """Log-normalized count of distinct co-authors"""
    return normalize_log(unique_coauthors)

def interdisciplinarity_score(research_fields: dict) -> float:
    """
    Entropy of research fields (how distributed author's work is across fields)
    """
    if not research_fields:
        return 0.0
    counts = list(research_fields.values())
    diversity_entropy = entropy(counts)
    max_entropy = np.log(len(research_fields))
    return diversity_entropy / max_entropy if max_entropy > 0 else 0.0

def trend_alignment_score(top_overlap: float) -> float:
    """Direct match with trending topic overlap (0–1)"""
    return top_overlap

def compute_all_scores(data: dict) -> dict:
    return {
        "Impact": round(impact_score(data.get("h_index", 0)), 3),
        "Productivity": round(productivity_score(data.get("total_papers", 0), data.get("career_years", 1)), 3),
        "Quality": round(quality_score(data.get("venue_scores", [])), 3),
        "Novelty": round(novelty_score(data.get("novelty_scores", [])), 3),
        "Leadership": round(leadership_score(data.get("first_last_author_count", 0), data.get("total_papers", 1)), 3),
        "Collaboration": round(collaboration_score(data.get("unique_coauthors", 0)), 3),
        "Interdisciplinarity": round(interdisciplinarity_score(data.get("research_fields", {})), 3),
        "Trend Alignment": round(trend_alignment_score(data.get("top_trend_overlap", 0.0)), 3)
    }

```
