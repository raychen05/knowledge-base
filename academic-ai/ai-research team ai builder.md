## Create a Research Team with AI Technologies


**Refined Prompt**:

```text
I want to create a research team composed of top researchers—either from the same or from complementary research areas—for a major funding application or a large academic/industry project.

I should be able to specify parameters such as:
- Research area or topic
- Region or country
- University or institution
- Authors with publications in top-tier journals

Please:

1. List the critical and commonly used criteria for selecting researchers for such high-impact teams (e.g., academic excellence, collaboration history, citation impact, interdisciplinarity, etc.).

2. Propose an AI- or data-driven approach that uses publication metrics, collaboration networks, and related data to:
- Recommend the best candidates for team formation,
- Identify top-level researchers or peers of similar caliber, and
- Suggest potential collaborators who can fill missing skills or expertise gaps within the existing team

```


**ChatGPT**:
Excellent — this is a highly strategic and data-rich task, and it’s one of the best use cases for an AI-assisted research intelligence system.
Let’s break this down systematically into three parts:


---

### 1. Core & Critical Criteria for Team Selection

To build a high-performing research or innovation team (academic or industry), you want a multi-dimensional profile of each candidate that balances scientific excellence, relevance, and complementarity.

Here’s a comprehensive list of common and critical selection dimensions grouped by category:

#### 🧠 A. Research Excellence

| Criterion           | Description                                      | Typical Metric/Data Source                                 |
|---------------------|--------------------------------------------------|------------------------------------------------------------|
| Publication quality | Output in top-tier journals in the target field(s)| Journal impact factor, percentile rank, quartile (Q1–Q4)   |
| Citation impact     | Scientific influence and recognition              | Total citations, average citations per paper, H-index, CNCI/FNCI |
| Top-field ranking   | Standing within field                             | Highly Cited Researcher (HCR) list, InCites percentile     |
| Grant record        | Proven ability to attract funding                 | Total funded projects, funding amount, diversity of funders |


#### 🤝 B. Collaboration & Network Strength


| Criterion                    | Description                                   | Metric/Data Source                                    |
|------------------------------|-----------------------------------------------|-------------------------------------------------------|
| Co-authorship network        | Breadth and density of collaborations         | Co-author graph centrality, PageRank, betweenness     |
| Cross-institution collaboration | Collaborations beyond home institution      | % of international co-authorships                     |
| Interdisciplinarity          | Breadth across fields                         | Publication field diversity index, entropy-based interdisciplinarity |
| Complementary expertise      | Match or fill gaps in existing team’s skills  | Topic vector similarity/distance to existing team      |


#### 🧩 C. Relevance & Fit


| Criterion             | Description                                         | Metric/Data Source                                                      |
|-----------------------|-----------------------------------------------------|-------------------------------------------------------------------------|
| Topical alignment     | Expertise overlap with project keywords             | Embedding similarity between author’s publications and project description |
| Recent activity       | Active publication or project in last 3–5 years     | Recent output count                                                     |
| Institutional affiliation | University, region, or industry relevance       | Institution reputation (THE/QS rank), geographic coverage               |
| Role suitability      | Ability to serve as PI, Co-PI, or collaborator      | Seniority level, experience, leadership roles                           |

#### 🌍 D. Diversity & Strategic Coverage


| Criterion                  | Description                                      | Metric/Data Source                                  |
|----------------------------|--------------------------------------------------|-----------------------------------------------------|
| Geographic diversity       | Representation from target countries or regions  | Country/region fields, diversity index               |
| Gender or career-stage balance | For policy or funding compliance             | Gender/career metadata, balance ratio                |
| Complementary sector       | Academic–industry mix for translational projects | Sector/institution type, industry–academic ratio     |

---

### 2. AI/Data-Driven Approach to Recommend the Team

You can model this as a multi-objective optimization and matching problem over large-scale author/institution data.

Here’s a stepwise AI + metric approach:

#### Step 1: Define the Project Profile

Input fields:
- Research area(s) or keywords
- Funding call description or topic summary
- Target region(s) or sectors (e.g. EU, US, Asia, biotech industry)
- Optional seed authors or institutions (existing team)

➡️ Embed the text using a scientific language model (e.g., SciBERT, Specter2, or OpenAI embeddings) to create a topic vector representing the project scope.

---

#### Step 2: Candidate Retrieval

Use your existing academic graph (or a platform like Web of Science + InCites) to:
- Retrieve authors with high topic similarity to the project vector (cosine similarity)
- Filter by:
    - Affiliation country/university
    - Recent output (last 5 years)
    - Journal tier (Q1 or top 10%)
- Optionally, weight higher for those with:
    - High CNCI / FNCI
    - Leadership in large consortia

---

#### Step 3: Multi-Criteria Scoring

Compute a composite score per candidate using normalized metrics:

```yaml
CompositeScore = 
    0.30 - TopicSimilarity + 
    0.25 - ImpactScore (FNCI, H-index) + 
    0.20 - CollaborationScore + 
    0.15 - RecentActivity + 
    0.10 - DiversityOrInstitutionWeight
```

Each subscore can be derived as:

- ImpactScore = min(1, FNCI / 2)
- CollaborationScore = log(1 + international_coauthors / total_coauthors)
- TopicSimilarity = cosine(project_vector, author_vector)

---

#### Step 4: Team Optimization / Complementarity

Once you have a pool of high-ranking candidates:

- Use clustering or graph optimization to select a complementary set:
    - Maximize total composite score
    - Minimize topic overlap between selected members
    - Ensure coverage across all sub-topics in the project
- Tools:
    - k-means or spectral clustering on author topic embeddings
    - Maximum coverage problem solver (integer programming)
    - Graph-based team formation algorithms (e.g., minimum Steiner tree for connectivity)

---

### Step 5: Role Assignment & Explanation

Assign roles such as:
- Principal Investigator (PI): top impact + strong funding history
- Co-PI(s): same-level peers with adjacent expertise
- Collaborators: complement missing skills or regional coverage
- Industry Partner: applied expertise or technology transfer potential

Provide AI-generated justification per candidate:
```text
“Dr. Li ranks in the top 5% globally in nanomaterials research, has collaborated with three EU partners, and complements the team’s computational modeling gap.”
```

---

### 3. System Design for Implementation

A robust AI-driven Team Builder module could look like this:

```yaml
TeamBuilderPipeline:
  Inputs:
    - project_description
    - target_fields
    - seed_team (optional)
    - filters: region, institution, year, journal_tier
  Steps:
    1. Embed project → project_vector
    2. Retrieve authors → candidate_set (ES + FAISS)
    3. Compute metrics → normalized_scores
    4. Optimize team composition → top_k diversified candidates
    5. Generate explanation & report
  Outputs:
    - ranked candidate list
    - role recommendations
    - coverage map (topic/institution/region)
    - team synergy metrics
```

---

4. Optional Advanced Additions

- **Graph-based reasoning**: use coauthorship + citation graph to infer collaboration feasibility
- **LLM reranker**: contextual reranking for nuanced fit
- **Diversity or skill-gap reasoning**: identify missing areas in current team embeddings
- **Interactive UI**: visualize author-topic graph, click to add/remove candidates

Would you like me to:
1. Produce a JSON schema for this “AI Team Builder” (inputs, metrics, outputs), or
2. Design a LangGraph / pipeline architecture showing how retrieval, scoring, and optimization flow work together?


---


Perfect 👍 — here’s a normalized JSON schema for your AI Team Builder system (for funding or collaborative project team formation).
This schema captures all key inputs, criteria, metrics, scoring logic, and outputs, and it’s designed to integrate seamlessly with analytic or AI agent pipelines (e.g., LangChain, LangGraph, or custom backend).

### 🧩 AI Team Builder JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "AITeamBuilder",
  "description": "Schema for recommending a set of researchers for project or funding collaboration",
  "type": "object",
  "properties": {
    "project_profile": {
      "type": "object",
      "description": "Information describing the target project or funding topic",
      "properties": {
        "project_title": { "type": "string" },
        "project_summary": { "type": "string" },
        "keywords": { "type": "array", "items": { "type": "string" } },
        "target_fields": { "type": "array", "items": { "type": "string" } },
        "target_regions": { "type": "array", "items": { "type": "string" } },
        "target_institutions": { "type": "array", "items": { "type": "string" } },
        "project_duration_years": { "type": "number" },
        "funding_amount_estimate": { "type": "number" },
        "existing_team": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "author_id": { "type": "string" },
              "name": { "type": "string" },
              "affiliation": { "type": "string" },
              "role": { "type": "string" }
            }
          }
        }
      },
      "required": ["project_summary", "keywords"]
    },

    "filters": {
      "type": "object",
      "description": "Optional constraints for search and ranking",
      "properties": {
        "region": { "type": "string" },
        "institution": { "type": "string" },
        "min_publications": { "type": "number" },
        "journal_tier": { "type": "string", "enum": ["Q1", "Q2", "Top10%"] },
        "publication_year_range": {
          "type": "object",
          "properties": {
            "from": { "type": "number" },
            "to": { "type": "number" }
          }
        }
      }
    },

    "metrics": {
      "type": "object",
      "description": "Quantitative indicators used for scoring and ranking",
      "properties": {
        "topic_similarity": { "type": "number", "description": "Cosine similarity between project and author topic vectors (0–1)" },
        "impact_metrics": {
          "type": "object",
          "properties": {
            "h_index": { "type": "number" },
            "fnci": { "type": "number" },
            "citations": { "type": "number" },
            "top_journal_ratio": { "type": "number", "description": "Fraction of papers in top-tier journals (0–1)" }
          }
        },
        "collaboration_metrics": {
          "type": "object",
          "properties": {
            "coauthor_network_size": { "type": "number" },
            "international_collab_ratio": { "type": "number" },
            "network_centrality": { "type": "number" }
          }
        },
        "activity_metrics": {
          "type": "object",
          "properties": {
            "recent_publications_5yr": { "type": "number" },
            "active_years": { "type": "number" }
          }
        },
        "interdisciplinarity": {
          "type": "number",
          "description": "Field diversity index based on subject category entropy (0–1)"
        }
      }
    },

    "scoring_model": {
      "type": "object",
      "description": "Weights for computing composite scores",
      "properties": {
        "weights": {
          "type": "object",
          "properties": {
            "topic_similarity": { "type": "number", "default": 0.30 },
            "impact_score": { "type": "number", "default": 0.25 },
            "collaboration_score": { "type": "number", "default": 0.20 },
            "recent_activity": { "type": "number", "default": 0.15 },
            "diversity_weight": { "type": "number", "default": 0.10 }
          }
        },
        "formula": {
          "type": "string",
          "description": "Human-readable formula for composite scoring",
          "default": "CompositeScore = 0.3*TopicSimilarity + 0.25*Impact + 0.2*Collab + 0.15*Activity + 0.1*Diversity"
        }
      }
    },

    "candidate_profile": {
      "type": "object",
      "description": "Per-author profile retrieved and scored",
      "properties": {
        "author_id": { "type": "string" },
        "name": { "type": "string" },
        "affiliation": { "type": "string" },
        "country": { "type": "string" },
        "research_fields": { "type": "array", "items": { "type": "string" } },
        "metrics": { "$ref": "#/properties/metrics" },
        "scores": {
          "type": "object",
          "properties": {
            "impact_score": { "type": "number" },
            "collaboration_score": { "type": "number" },
            "activity_score": { "type": "number" },
            "composite_score": { "type": "number" }
          }
        },
        "role_recommendation": {
          "type": "string",
          "enum": ["PI", "Co-PI", "Collaborator", "Advisor", "Industry Partner"]
        },
        "explanation": { "type": "string" }
      }
    },

    "output": {
      "type": "object",
      "description": "Final AI-generated team recommendation output",
      "properties": {
        "recommended_team": {
          "type": "array",
          "items": { "$ref": "#/properties/candidate_profile" }
        },
        "team_summary": {
          "type": "object",
          "properties": {
            "total_candidates": { "type": "number" },
            "average_composite_score": { "type": "number" },
            "field_coverage": { "type": "array", "items": { "type": "string" } },
            "region_coverage": { "type": "array", "items": { "type": "string" } },
            "complementarity_index": { "type": "number", "description": "Diversity or skill gap coverage metric (0–1)" }
          }
        }
      }
    }
  },
  "required": ["project_profile", "scoring_model", "output"]
}

```

---

### 🔍 Usage Example

You can pass this schema into:
- A LangGraph node or LangChain tool that retrieves, scores, and ranks researchers.
- An Elasticsearch/FAISS retrieval layer for author candidates.
- A Streamlit UI to visualize the top-20 recommended researchers with justifications.


---

ChatGPT:
Excellent — here’s a LangGraph / LangChain node design for your AI Team Builder module that retrieves, scores, and ranks researchers using the JSON schema we defined.
This implementation outline shows how the AI Team Builder fits as a retriever–analyzer node in a larger LangGraph or agent pipeline.


### 🧠 LangGraph Node: TeamBuilderNode


**Purpose**
Retrieve candidate researchers, compute multi-metric scores (topic match, impact, collaboration, activity), and recommend a ranked list of team members for a project or funding proposal.

---

### ⚙️ Conceptual Flow (Graph-level)

```text
(Project/Topic Input)
        │
        ▼
[ProjectVectorNode] → embeds project keywords, abstract, or call text
        │
        ▼
[ResearcherRetrieverNode] → retrieves candidate authors (ES/FAISS)
        │
        ▼
[MetricScorerNode] → calculates FNCI, H-index, collab, activity, etc.
        │
        ▼
[TeamOptimizerNode] → ranks, balances, and assigns roles
        │
        ▼
[OutputFormatterNode] → JSON team report + justifications

```

Each box is a LangGraph node; the one we focus on below combines retrieval + scoring logic.

---


### 🧩 LangGraph Node Specification (YAML)


```yaml
id: TeamBuilderNode
description: >
  Retrieve and rank researchers for a funding or collaborative project based on
  topic similarity, impact, collaboration, and complementarity metrics.

input_schema:
  $ref: "AITeamBuilder.project_profile"

output_schema:
  $ref: "AITeamBuilder.output"

steps:
  - name: embed_project
    description: "Embed the project description and keywords into a semantic vector."
    tool: "openai_embeddings"
    inputs:
      text: "{{ project_profile.project_summary }}"
    outputs:
      project_vector: "$.embedding"

  - name: retrieve_candidates
    description: "Retrieve top candidate researchers from the author index."
    tool: "elasticsearch_retriever"
    inputs:
      index: "authors_index"
      query_vector: "{{ project_vector }}"
      fields: ["name", "affiliation", "country", "research_fields", "author_vector"]
      size: 200
    outputs:
      candidates: "$.hits"

  - name: compute_metrics
    description: "Compute topic similarity, impact, collaboration, and activity metrics."
    tool: "metric_calculator"
    inputs:
      project_vector: "{{ project_vector }}"
      candidates: "{{ candidates }}"
    outputs:
      scored_candidates: "$.metrics"

  - name: rank_candidates
    description: "Rank candidates by weighted composite score."
    tool: "composite_ranker"
    inputs:
      scored_candidates: "{{ scored_candidates }}"
      weights:
        topic_similarity: 0.30
        impact_score: 0.25
        collaboration_score: 0.20
        recent_activity: 0.15
        diversity_weight: 0.10
    outputs:
      ranked_candidates: "$.ranked"

  - name: optimize_team
    description: "Select top N researchers ensuring complementary expertise and diversity."
    tool: "team_optimizer"
    inputs:
      ranked_candidates: "{{ ranked_candidates }}"
      max_team_size: 10
      diversity_objective: true
    outputs:
      recommended_team: "$.team"

  - name: format_output
    description: "Format recommended team into standardized JSON output with explanations."
    tool: "llm_formatter"
    model: "gpt-5"
    inputs:
      template: |
        Generate structured JSON using AITeamBuilder.output schema.
        Include recommended_team, average score, field coverage, and explanation per author.
      data: "{{ recommended_team }}"
    outputs:
      output: "$.json"


```

---

### 🧩 Python (LangChain / LangGraph-Compatible Pseudocode)

Here’s a modular implementation snippet:

```python
from langchain.schema import BaseTool, Tool
from typing import List, Dict
import numpy as np

# --- Step 1: Embed Project ---
def embed_project(project_summary: str):
    from openai import OpenAIEmbeddings
    embedder = OpenAIEmbeddings(model="text-embedding-3-large")
    return embedder.embed_query(project_summary)

# --- Step 2: Retrieve Candidates ---
def retrieve_candidates(project_vector):
    from elasticsearch import Elasticsearch
    es = Elasticsearch("http://localhost:9200")
    query = {
        "knn": {
            "field": "author_vector",
            "query_vector": project_vector,
            "k": 200
        }
    }
    res = es.search(index="authors_index", body=query)
    return [hit["_source"] for hit in res["hits"]["hits"]]

# --- Step 3: Compute Metrics ---
def compute_metrics(project_vector, candidates):
    for c in candidates:
        c["metrics"] = {
            "topic_similarity": float(np.dot(project_vector, c["author_vector"]) /
                                      (np.linalg.norm(project_vector)*np.linalg.norm(c["author_vector"]))),
            "impact_score": np.log1p(c.get("citations", 0)) / 10,
            "collaboration_score": c.get("intl_collab_ratio", 0.5),
            "activity_score": np.log1p(c.get("recent_publications_5yr", 1)) / 5
        }
    return candidates

# --- Step 4: Rank and Optimize ---
def rank_candidates(candidates, weights):
    for c in candidates:
        m = c["metrics"]
        c["composite_score"] = (
            weights["topic_similarity"] - m["topic_similarity"] +
            weights["impact_score"] - m["impact_score"] +
            weights["collaboration_score"] - m["collaboration_score"] +
            weights["recent_activity"] - m["activity_score"]
        )
    return sorted(candidates, key=lambda x: x["composite_score"], reverse=True)

# --- Step 5: Format Output ---
def format_output(ranked_candidates, top_k=10):
    team = ranked_candidates[:top_k]
    return {
        "recommended_team": team,
        "team_summary": {
            "total_candidates": len(team),
            "average_composite_score": np.mean([c["composite_score"] for c in team]),
            "field_coverage": list({f for c in team for f in c.get("research_fields", [])}),
            "region_coverage": list({c.get("country") for c in team})
        }
    }

```

---

### 🧮 Result Example

```json
{
  "recommended_team": [
    {
      "name": "Prof. Alice Zhang",
      "affiliation": "MIT",
      "country": "USA",
      "research_fields": ["AI Materials Discovery"],
      "metrics": {
        "topic_similarity": 0.91,
        "impact_score": 0.87,
        "collaboration_score": 0.76,
        "activity_score": 0.82
      },
      "composite_score": 0.85,
      "role_recommendation": "PI",
      "explanation": "High topical match with AI materials science, strong citation record, broad collaboration network."
    },
    {
      "name": "Dr. Kei Tanaka",
      "affiliation": "University of Tokyo",
      "role_recommendation": "Co-PI",
      "composite_score": 0.82
    }
  ],
  "team_summary": {
    "total_candidates": 10,
    "average_composite_score": 0.79,
    "field_coverage": ["AI", "Materials Science", "Computational Chemistry"],
    "region_coverage": ["USA", "Japan", "Germany"]
  }
}

```

### 🧭 Integration Notes

- Works well as a LangGraph node connected to:
    - ProjectVectorNode (embedding)
    - ElasticSearchRetrieverNode or FAISS retriever
    - MetricScorerNode for derived metrics
- Outputs standardized JSON for downstream tasks:
    - Report generation
    - Proposal team visualization
    - “Skill gap” analysis (to identify missing expertise)


---

**ChatGPT**:

Here’s a complete working design for your AI Team Builder LangGraph pipeline, integrating retrieval, scoring, optimization, and explanation generation.
It’s structured so you can plug it into your existing author index (Elasticsearch, FAISS, or similar) and academic metric database (InCites, internal tables, etc.).


### 🧩 1. LangGraph Pipeline Overview

```text
 ┌─────────────────────┐
 │  Input: Project Info │
 └──────────┬───────────┘
            ▼
 ┌─────────────────────┐
 │  Node 1: ProjectVectorNode │
 │  → Embed project text     │
 └──────────┬───────────┘
            ▼
 ┌─────────────────────┐
 │  Node 2: ResearcherRetrieverNode │
 │  → Retrieve top candidate authors │
 └──────────┬───────────┘
            ▼
 ┌─────────────────────┐
 │  Node 3: MetricScorerNode │
 │  → Compute metrics (topic, impact, collab, activity) │
 └──────────┬───────────┘
            ▼
 ┌─────────────────────┐
 │  Node 4: TeamOptimizerNode │
 │  → Rank, balance, and select top-N researchers │
 └──────────┬───────────┘
            ▼
 ┌─────────────────────┐
 │  Node 5: LLMExplanationNode │
 │  → Generate human-readable justifications │
 └──────────┬───────────┘
            ▼
 ┌─────────────────────┐
 │  Output: Recommended Team JSON │
 └─────────────────────┘

```

---

### 🧠 2. LangGraph YAML Pipeline Definition

```yaml
id: AI_TeamBuilder_Pipeline
description: >
  A LangGraph pipeline to retrieve, score, and recommend an optimal research team for
  a funding project or collaboration using project text, embeddings, and author metrics.

inputs:
  project_title: string
  project_summary: string
  keywords: array
  target_fields: array
  target_regions: array
  existing_team: array

outputs:
  recommended_team: array
  team_summary: object

nodes:
  - id: ProjectVectorNode
    type: llm_embedding
    description: "Embed project summary into vector space."
    model: text-embedding-3-large
    input: "{{ project_summary }}"
    output: project_vector

  - id: ResearcherRetrieverNode
    type: retriever
    description: "Retrieve top author candidates by topic similarity."
    retriever_type: elasticsearch
    params:
      index: authors_index
      vector_field: author_vector
      return_fields: [author_id, name, affiliation, country, research_fields, author_vector, h_index, fnci, citations, intl_collab_ratio, recent_publications_5yr]
      size: 200
    input:
      query_vector: "{{ project_vector }}"
    output: candidates

  - id: MetricScorerNode
    type: python_function
    description: "Compute topic similarity and research performance metrics."
    function: compute_author_metrics
    input:
      project_vector: "{{ project_vector }}"
      candidates: "{{ candidates }}"
    output: scored_candidates

  - id: TeamOptimizerNode
    type: python_function
    description: "Rank candidates and select optimal team with diversity and complementarity."
    function: optimize_team
    input:
      scored_candidates: "{{ scored_candidates }}"
      max_team_size: 10
    output: optimized_team

  - id: LLMExplanationNode
    type: llm
    description: "Generate concise justifications for each recommended researcher."
    model: gpt-5
    prompt_template: |
      For each researcher, summarize 2–3 reasons why they are well-suited for the project.
      Use their topic alignment, impact metrics, collaboration network, and role suitability.
      Output JSON using the schema AITeamBuilder.output.
    input:
      data: "{{ optimized_team }}"
    output: recommended_team

edges:
  - source: ProjectVectorNode
    target: ResearcherRetrieverNode
  - source: ResearcherRetrieverNode
    target: MetricScorerNode
  - source: MetricScorerNode
    target: TeamOptimizerNode
  - source: TeamOptimizerNode
    target: LLMExplanationNode

```

---

### 🧮 3. Python Implementation of Core Functions


Below is the minimal working version of the main computation functions used in MetricScorerNode and TeamOptimizerNode.

```python
import numpy as np

# ---------- Metric Computation Node ----------
def compute_author_metrics(project_vector, candidates):
    for c in candidates:
        author_vec = np.array(c.get("author_vector", np.zeros(len(project_vector))))
        sim = float(np.dot(project_vector, author_vec) / (np.linalg.norm(project_vector)*np.linalg.norm(author_vec) + 1e-9))
        fnci = c.get("fnci", 1.0)
        citations = c.get("citations", 0)
        intl_ratio = c.get("intl_collab_ratio", 0.5)
        recent_pubs = c.get("recent_publications_5yr", 1)
        
        c["metrics"] = {
            "topic_similarity": sim,
            "impact_score": np.log1p(citations) / 10 + fnci / 2,
            "collaboration_score": intl_ratio,
            "activity_score": np.log1p(recent_pubs) / 5
        }
    return candidates


# ---------- Team Optimization Node ----------
def optimize_team(scored_candidates, max_team_size=10):
    weights = {
        "topic_similarity": 0.30,
        "impact_score": 0.25,
        "collaboration_score": 0.20,
        "activity_score": 0.15,
        "diversity_weight": 0.10
    }

    for c in scored_candidates:
        m = c["metrics"]
        c["composite_score"] = (
            weights["topic_similarity"] - m["topic_similarity"] +
            weights["impact_score"] - m["impact_score"] +
            weights["collaboration_score"] - m["collaboration_score"] +
            weights["activity_score"] - m["activity_score"]
        )
    
    ranked = sorted(scored_candidates, key=lambda x: x["composite_score"], reverse=True)
    top_team = ranked[:max_team_size]
    
    field_cov = list({f for c in top_team for f in c.get("research_fields", [])})
    regions = list({c.get("country") for c in top_team})
    
    return {
        "recommended_team": top_team,
        "team_summary": {
            "total_candidates": len(top_team),
            "average_composite_score": float(np.mean([c["composite_score"] for c in top_team])),
            "field_coverage": field_cov,
            "region_coverage": regions
        }
    }

```

---


### 📊 4. Example Run (AI Materials Discovery Project)

```json
{
  "project_summary": "AI-driven materials discovery for sustainable batteries and catalysts.",
  "recommended_team": [
    {
      "name": "Prof. Alice Zhang",
      "affiliation": "MIT",
      "country": "USA",
      "metrics": {
        "topic_similarity": 0.92,
        "impact_score": 0.88,
        "collaboration_score": 0.81,
        "activity_score": 0.80
      },
      "composite_score": 0.86,
      "role_recommendation": "PI",
      "explanation": "Strong alignment with AI materials design, highly cited, broad international collaboration."
    },
    {
      "name": "Dr. Kenji Tanaka",
      "affiliation": "University of Tokyo",
      "role_recommendation": "Co-PI",
      "composite_score": 0.83,
      "explanation": "Expert in computational catalysis and complementary modeling expertise."
    }
  ],
  "team_summary": {
    "total_candidates": 10,
    "average_composite_score": 0.79,
    "field_coverage": ["AI", "Materials Science", "Catalysis", "Battery Research"],
    "region_coverage": ["USA", "Japan", "Germany"]
  }
}

```

---

### 🧭 5. Integration Tips


| Component           | Recommended Implementation Options                                   |
|---------------------|---------------------------------------------------------------------|
| Retriever backend   | Elasticsearch (dense vector search) or FAISS                        |
| Embeddings          | `text-embedding-3-large` or domain-specific models like Specter2     |
| Metric source       | Web of Science + InCites API, or internal researcher database        |
| Graph reasoning     | Neo4j or in-memory coauthor/citation graph                          |
| UI                  | Streamlit dashboard with radar chart and collaboration graph         |



Would you like me to extend this next into a Streamlit-based UI that connects to this pipeline — allowing you to enter project text, view the top-10 recommended researchers, visualize team balance, and export the JSON result?

---

**ChatGPT**:
Perfect — here’s the complete design + working skeleton for a system that recommends and visualizes top researchers using LangGraph (for reasoning), LangChain tools (for retrieval & scoring), and a Streamlit UI (for visualization).


### 🧠 System Overview

Goal: Build a smart “Team Builder” that recommends researchers based on:
- Topic/discipline match
- Publication quality & impact
- Collaboration compatibility
- Missing-skill complementarity
- Regional/institutional fit

---

### ⚙️ Architecture Diagram

```pqsql
User Input → LangGraph Agent → ResearcherRetriever Tool
                             → MetricScorer Tool
                             → TeamBalancer Tool
                             → Ranker Node → Streamlit UI
```

---

### 🧩 1. LangGraph Nodes / Tools

#### Tool 1: ResearcherRetriever

Retrieves candidate researchers from ElasticSearch / API based on topic, region, or university.

```python
from langchain.tools import BaseTool
from typing import List, Dict

class ResearcherRetriever(BaseTool):
    name = "researcher_retriever"
    description = "Retrieve researchers by topic, region, university, or journal publication quality."

    def _run(self, query: str) -> List[Dict]:
        # Example stub: Replace with Elasticsearch / WoS query
        candidates = [
            {"name": "Dr. Alice Zhang", "affiliation": "Stanford", "field": "AI", "h_index": 62, "fnci": 1.9},
            {"name": "Dr. Bob Lee", "affiliation": "MIT", "field": "Robotics", "h_index": 58, "fnci": 1.7},
            # ...
        ]
        return candidates

```

---

#### Tool 2: MetricScorer

Computes quantitative impact metrics and field-normalized scores.

```python
class MetricScorer(BaseTool):
    name = "metric_scorer"
    description = "Compute impact, collaboration, and complementarity scores for each researcher."

    def _run(self, researchers: List[Dict], team_context: Dict) -> List[Dict]:
        scored = []
        for r in researchers:
            impact = (r["h_index"] / 100) - 0.5 + r["fnci"] - 0.5
            collaboration_gap = 1.0 - team_context.get("skill_coverage", {}).get(r["field"], 0.5)
            total = 0.7 - impact + 0.3 - collaboration_gap
            r["score"] = round(total, 3)
            scored.append(r)
        return scored

```

---

#### Tool 3: TeamBalancer

Analyzes the existing team’s expertise and recommends missing skills.

```python
class TeamBalancer(BaseTool):
    name = "team_balancer"
    description = "Detects missing expertise areas and recommends complementary candidates."

    def _run(self, team_context: Dict, candidates: List[Dict]) -> List[Dict]:
        missing_fields = [f for f, cov in team_context.get("skill_coverage", {}).items() if cov < 0.6]
        for c in candidates:
            c["fit_reason"] = "fills missing expertise" if c["field"] in missing_fields else "strong in same area"
        return candidates

```

---

### LangGraph Definition

```python
from langgraph import StateGraph

graph = StateGraph()
graph.add_node("retriever", ResearcherRetriever())
graph.add_node("scorer", MetricScorer())
graph.add_node("balancer", TeamBalancer())

graph.add_edge("retriever", "scorer")
graph.add_edge("scorer", "balancer")

graph.set_entry_point("retriever")
graph.set_exit_point("balancer")

team_builder_agent = graph.compile()
```

---

#### 💡 Example Workflow

```python
query = "AI safety, Europe, top journal authors"
team_context = {"skill_coverage": {"AI safety": 0.8, "robotics": 0.3}}

results = team_builder_agent.invoke({"query": query, "team_context": team_context})

```

---

### 📊 Streamlit UI


```python
import streamlit as st
import pandas as pd

st.title("🔬 AI Research Team Builder")

query = st.text_input("Enter research area / topic:")
region = st.selectbox("Select region:", ["Global", "Europe", "US", "Asia"])
university = st.text_input("University (optional):")

if st.button("Recommend Researchers"):
    # Simulate backend call
    data = [
        {"name": "Dr. Alice Zhang", "affiliation": "Stanford", "field": "AI", 
         "score": 0.93, "fit_reason": "strong in same area"},
        {"name": "Dr. Bob Lee", "affiliation": "MIT", "field": "Robotics",
         "score": 0.88, "fit_reason": "fills missing expertise"},
        # ...
    ]
    df = pd.DataFrame(data)
    st.dataframe(df)

    st.markdown("### Justifications")
    for _, row in df.iterrows():
        st.markdown(f"**{row['name']}*- ({row['affiliation']}) — {row['fit_reason']} (score: {row['score']})")

```

---

### 🧮 Scoring Formula Example


| Dimension               | Metric(s)                        | Formula / Logic                       | Weight |
|-------------------------|----------------------------------|---------------------------------------|--------|
| **Research Impact*-     | h-index, FNCI                    | 0.5 × normalized h-index + 0.5 × FNCI | 0.4    |
| **Collaboration Potential*- | Coauthor overlap, network distance | 1 / (1 + distance to team)            | 0.3    |
| **Complementarity*-     | Missing-skill match              | 1 if fills gap, else 0                | 0.2    |
| **Institutional Fit*-   | Same region or partner org       | 1 if match, else 0                    | 0.1    |

Total Score = Σ(weight × metric)

---

### 🧠 Extension Ideas

- Integrate with Web of Science API or Semantic Scholar Graph
- Add LLM-based explanation node to justify top-10 ranking
- Use vector embeddings (FAISS/Qdrant) for topic similarity
- Add collaboration graph (Neo4j) for coauthor network scoring
- Deploy as a LangGraph chain in LangServe for API-based use

Would you like me to extend this with a justification generator node (LLM-based explanation for why each researcher is chosen)?
 - That would complete the system end-to-end for both scoring + reasoning.


---

**ChatGPT**:

Excellent ✅ — we’ll extend your Research Team Builder LangGraph pipeline with an LLM-based Explanation Node called JustificationGenerator.

This new node will:
- Read the top-10 scored researchers
- Analyze their metrics, fit, and complementarity
- Generate natural-language justifications summarizing why they’re ideal candidates
- Optionally output a structured JSON summary for UI or report display

---

### 🧩 Updated LangGraph Design

```css
User Query 
   ↓
ResearcherRetriever → MetricScorer → TeamBalancer → JustificationGenerator
   ↓
 Streamlit UI (top-20 visualization + justifications)
```

---

### 🧠 1. Add the JustificationGenerator Node

```python
from langchain.tools import BaseTool
from langchain.chat_models import ChatOpenAI
from typing import List, Dict

class JustificationGenerator(BaseTool):
    name = "justification_generator"
    description = "Generate human-readable justifications for top-ranked researchers."

    def __init__(self, model_name="gpt-4o-mini"):
        super().__init__()
        self.llm = ChatOpenAI(model=model_name, temperature=0.3)

    def _run(self, researchers: List[Dict]) -> List[Dict]:
        results = []
        for r in researchers[:10]:
            prompt = f"""
            You are selecting researchers for a high-profile interdisciplinary project.
            Explain briefly (in 2–3 sentences) why this researcher is an excellent fit.
            
            Researcher:
            - Name: {r['name']}
            - Affiliation: {r['affiliation']}
            - Field: {r['field']}
            - Score: {r['score']}
            - Reason: {r.get('fit_reason', 'N/A')}
            - Impact: h-index {r.get('h_index', 'N/A')}, FNCI {r.get('fnci', 'N/A')}
            
            Provide a concise, professional justification.
            """
            response = self.llm.invoke(prompt).content
            r["justification"] = response.strip()
            results.append(r)
        return results
```

---

### 🧩 2. Integrate It Into the Graph

```python
from langgraph import StateGraph

graph = StateGraph()
graph.add_node("retriever", ResearcherRetriever())
graph.add_node("scorer", MetricScorer())
graph.add_node("balancer", TeamBalancer())
graph.add_node("justifier", JustificationGenerator())

graph.add_edge("retriever", "scorer")
graph.add_edge("scorer", "balancer")
graph.add_edge("balancer", "justifier")

graph.set_entry_point("retriever")
graph.set_exit_point("justifier")

team_builder_agent = graph.compile()

```

---

### ⚙️ Example End-to-End Run

```python
query = "AI Safety and Robotics, Europe"
team_context = {"skill_coverage": {"AI safety": 0.8, "robotics": 0.4}}

results = team_builder_agent.invoke({"query": query, "team_context": team_context})

```

---


### 📊 3. Streamlit Visualization (Updated)

```python
import streamlit as st
import pandas as pd

st.title("🏆 Research Team Builder (AI-Powered)")

query = st.text_input("Enter research area / topic:")
region = st.selectbox("Select region:", ["Global", "Europe", "US", "Asia"])
if st.button("Recommend Researchers"):

    # Simulated output
    data = [
        {"name": "Dr. Alice Zhang", "affiliation": "Stanford", "field": "AI",
         "score": 0.93, "fit_reason": "strong in same area",
         "justification": "Dr. Zhang leads impactful AI research at Stanford with strong citations and complementary expertise for the proposed AI Safety project."},
        {"name": "Dr. Bob Lee", "affiliation": "MIT", "field": "Robotics",
         "score": 0.89, "fit_reason": "fills missing expertise",
         "justification": "Dr. Lee is a robotics expert whose experience bridges human–machine safety and multi-agent systems, filling a critical skill gap in the team."},
        # ...
    ]
    df = pd.DataFrame(data)
    st.dataframe(df[["name", "affiliation", "field", "score"]])

    st.markdown("### 📋 AI-Generated Justifications")
    for _, row in df.iterrows():
        st.markdown(f"""
        **{row['name']}*- ({row['affiliation']}, {row['field']})  
        🧩 *{row['fit_reason']}-  
        💬 _{row['justification']}_  
        **Score:*- {row['score']}
        """)

```

---

### 🧮 Extended Scoring Logic Example

| **Dimension*-            | **Metric(s)*-                        | **Source*-                | **Weight*- |
|--------------------------|--------------------------------------|---------------------------|------------|
| **Impact*-               | h-index, FNCI                        | WoS / Scopus              | 0.4        |
| **Expertise Fit*-        | Topic similarity (embedding cosine)   | FAISS / OpenAI embeddings | 0.25       |
| **Complementarity*-      | Missing-skill match                   | Team context              | 0.15       |
| **Collaboration Potential*- | Co-author network overlap          | Neo4j / WoS data          | 0.10       |
| **Institutional Fit*-    | Same or partner organization          | Registry                  | 0.10       |


Final Score = weighted sum normalized to [0,1]

---

### 🧠 Optional Next Step — “Explainable Ranking Report” Node

You can extend the JustificationGenerator to output a structured JSON report like:

```json
{
  "summary": "Top researchers for AI Safety and Robotics in Europe",
  "top_researchers": [
    {
      "name": "Dr. Alice Zhang",
      "affiliation": "Stanford",
      "score": 0.93,
      "justification": "Leads top-tier AI safety research with proven cross-disciplinary success.",
      "fit_tags": ["High impact", "Domain alignment", "Collaboration-ready"]
    }
  ]
}


```

Would you like me to add this final Explainable Ranking Report node (outputs JSON summary with LLM-generated insights on team diversity, strengths, and risks)?
 - That would complete the AI-driven, report-ready system.


---

**ChatGPT**:

Perfect 🔥 — now we’ll complete the system by adding the final node:
 - an LLM-based Explainable Ranking Report Generator, which takes the top-ranked researchers and their justifications, and produces a structured JSON report summarizing:
- Overall summary of the team
- Diversity and complementarity
- Key strengths and potential gaps
- Ranked list of top researchers with justification tags


### 🧩 1. ExplainableReportGenerator Node

```python
from langchain.tools import BaseTool
from langchain.chat_models import ChatOpenAI
from typing import List, Dict
import json

class ExplainableReportGenerator(BaseTool):
    name = "explainable_report_generator"
    description = "Generate a structured JSON report summarizing the recommended team composition and reasoning."

    def __init__(self, model_name="gpt-4o-mini"):
        super().__init__()
        self.llm = ChatOpenAI(model=model_name, temperature=0.4)

    def _run(self, researchers: List[Dict]) -> Dict:
        summary_prompt = f"""
        You are an AI research evaluation assistant.
        Given the following ranked researchers, produce a concise and structured JSON report including:
        1. A one-paragraph summary describing the overall strength and focus of the team.
        2. Key strengths (list of 3–5 short points).
        3. Potential gaps or missing skills.
        4. A table-like array "ranked_candidates" with fields:
            - name
            - affiliation
            - field
            - score
            - justification
            - tags: a short list of categories such as ["High Impact", "Complementary Skill", "Emerging Leader"]

        Researchers:
        {json.dumps(researchers[:10], indent=2)}
        """

        response = self.llm.invoke(summary_prompt).content.strip()
        try:
            report = json.loads(response)
        except Exception:
            # Fallback if LLM outputs text instead of JSON
            report = {"summary_text": response}
        return report

```

---

### 🧩 2. Integrate into the LangGraph

```python
graph = StateGraph()
graph.add_node("retriever", ResearcherRetriever())
graph.add_node("scorer", MetricScorer())
graph.add_node("balancer", TeamBalancer())
graph.add_node("justifier", JustificationGenerator())
graph.add_node("reporter", ExplainableReportGenerator())

graph.add_edge("retriever", "scorer")
graph.add_edge("scorer", "balancer")
graph.add_edge("balancer", "justifier")
graph.add_edge("justifier", "reporter")

graph.set_entry_point("retriever")
graph.set_exit_point("reporter")

team_builder_agent = graph.compile()
```

---

### ⚙️ 3. Example End-to-End Run


```python
query = "Quantum Materials and Nanotechnology, Asia"
team_context = {"skill_coverage": {"quantum materials": 0.7, "nanotechnology": 0.5}}

report = team_builder_agent.invoke({"query": query, "team_context": team_context})
print(json.dumps(report, indent=2))

```

---

### 🧾 Example Output (LLM JSON Summary)

```json
{
  "team_summary": "This proposed team combines leading experts in quantum materials and nanoscale devices across top Asian institutions. The researchers demonstrate high impact, interdisciplinary reach, and complementary skills in materials characterization and device engineering.",
  "key_strengths": [
    "Strong publication record in Nature and Science journals",
    "Balanced expertise across theory and experimentation",
    "High citation impact and FNCI > 1.5 for most candidates",
    "Geographically diverse collaboration potential",
    "Excellent alignment with funding priorities in advanced materials"
  ],
  "potential_gaps": [
    "Limited expertise in large-scale fabrication",
    "Underrepresentation of early-career emerging leaders"
  ],
  "ranked_candidates": [
    {
      "name": "Dr. Yuki Tanaka",
      "affiliation": "University of Tokyo",
      "field": "Quantum Materials",
      "score": 0.94,
      "justification": "Dr. Tanaka leads groundbreaking work in superconducting materials with strong publication impact and collaborative leadership.",
      "tags": ["High Impact", "Domain Expert", "Collaborative Leader"]
    },
    {
      "name": "Dr. Min Li",
      "affiliation": "Tsinghua University",
      "field": "Nanotechnology",
      "score": 0.91,
      "justification": "Dr. Li brings nanoscale synthesis expertise critical to bridging material design and device applications.",
      "tags": ["Complementary Skill", "Applied Researcher"]
    }
  ]
}


````

---

### 🖥️ 4. Streamlit Visualization (Updated)


```python
import streamlit as st
import pandas as pd
import json

st.title("🤖 Research Team Builder with Explainable AI Report")

if st.button("Generate AI-Driven Team Report"):
    # Simulated output for UI demo
    report = {
        "team_summary": "Top experts across AI safety and robotics, combining strong impact and diverse expertise.",
        "key_strengths": ["High impact publications", "Interdisciplinary collaboration", "Geographical diversity"],
        "potential_gaps": ["Need more junior researchers"],
        "ranked_candidates": [
            {
                "name": "Dr. Alice Zhang",
                "affiliation": "Stanford University",
                "field": "AI Safety",
                "score": 0.93,
                "justification": "Leads impactful AI safety research bridging ethics and technical safety.",
                "tags": ["High Impact", "Domain Expert"]
            },
            {
                "name": "Dr. Bob Lee",
                "affiliation": "MIT",
                "field": "Robotics",
                "score": 0.89,
                "justification": "Specializes in human-robot interaction and collaborative systems.",
                "tags": ["Complementary Skill", "Emerging Leader"]
            }
        ]
    }

    st.subheader("📘 Team Summary")
    st.write(report["team_summary"])

    st.subheader("💪 Key Strengths")
    for s in report["key_strengths"]:
        st.markdown(f"- {s}")

    st.subheader("⚠️ Potential Gaps")
    for g in report["potential_gaps"]:
        st.markdown(f"- {g}")

    st.subheader("🏆 Ranked Researchers")
    df = pd.DataFrame(report["ranked_candidates"])
    st.dataframe(df[["name", "affiliation", "field", "score", "tags"]])

    st.subheader("💬 AI Justifications")
    for c in report["ranked_candidates"]:
        st.markdown(f"**{c['name']}*- ({c['affiliation']}, {c['field']})  — _{c['justification']}_")

```

---

### 🧠 Future Enhancements

- ✅ Integrate real metrics from Web of Science, InCites, or Semantic Scholar
- 🧩 Add embedding-based topic similarity scoring (FAISS / Qdrant)
- 🔗 Connect coauthor graph (Neo4j) for collaboration potential
- 📊 Include interactive radar charts in Streamlit for team balance visualization
- 📑 Export explainable team reports as PDF or JSON for grant submissions


Would you like me to extend this Streamlit UI to include:
1. A radar or heatmap visualization of the team’s skill balance, and
2. A “Generate PDF Report” button that outputs the AI report in a formatted, submission-ready document?


---

**ChatGPT**:

Excellent — let’s finalize your AI-Powered Research Team Builder with:

- ✅ Interactive Radar / Heatmap visualization of team skill balance
- ✅ One-click “Generate PDF Report” for funding or proposal submission

Below is the complete, production-ready Streamlit UI + backend integration skeleton.

---

### 🧩 1. Extended Streamlit UI – Overview

The new UI now includes:
- Filters for topic, region, and university
- Display of team summary, strengths, and gaps
- Radar/heatmap visualization of expertise coverage
- Ranked researcher table + AI justifications
- “Generate PDF Report” export

---

### 🧱 2. Complete Streamlit Code

```python
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from math import pi
from fpdf import FPDF
import json

# === Mock data: replace with output from your LangGraph pipeline ===
sample_report = {
    "team_summary": "Top experts across AI safety, robotics, and autonomous systems, combining strong impact and diverse expertise from top institutions.",
    "key_strengths": [
        "High publication impact (avg FNCI > 1.8)",
        "Cross-domain expertise in AI safety, robotics, and control systems",
        "Established collaboration networks across Stanford, MIT, and ETH Zurich"
    ],
    "potential_gaps": [
        "Limited coverage in human factors engineering",
        "Few early-career researchers for innovation diversity"
    ],
    "skill_balance": {
        "AI Safety": 0.9,
        "Robotics": 0.8,
        "Control Systems": 0.7,
        "Human Factors": 0.4,
        "Ethics": 0.6
    },
    "ranked_candidates": [
        {
            "name": "Dr. Alice Zhang",
            "affiliation": "Stanford University",
            "field": "AI Safety",
            "score": 0.93,
            "justification": "Leads impactful AI safety research bridging ethics and technical safety.",
            "tags": ["High Impact", "Domain Expert"]
        },
        {
            "name": "Dr. Bob Lee",
            "affiliation": "MIT",
            "field": "Robotics",
            "score": 0.89,
            "justification": "Specializes in human-robot interaction and collaborative systems.",
            "tags": ["Complementary Skill", "Emerging Leader"]
        },
        {
            "name": "Dr. Marie Keller",
            "affiliation": "ETH Zurich",
            "field": "Control Systems",
            "score": 0.85,
            "justification": "Strong expertise in real-time control and system stability.",
            "tags": ["Core Method Expert"]
        }
    ]
}

# === Streamlit UI ===
st.set_page_config(page_title="AI Research Team Builder", layout="wide")
st.title("🤖 AI Research Team Builder")
st.markdown("Generate an explainable team recommendation for funding or industry projects.")

topic = st.text_input("🎯 Research area:", "AI Safety and Robotics")
region = st.selectbox("🌍 Region:", ["Global", "North America", "Europe", "Asia"])
university = st.text_input("🏛️ Target university (optional):", "")

if st.button("🔍 Generate Recommendations"):
    report = sample_report  # Replace with `team_builder_agent.invoke(...)`

    st.subheader("📘 Team Summary")
    st.write(report["team_summary"])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 💪 Key Strengths")
        for s in report["key_strengths"]:
            st.markdown(f"- {s}")
    with col2:
        st.markdown("### ⚠️ Potential Gaps")
        for g in report["potential_gaps"]:
            st.markdown(f"- {g}")

    # === Radar Chart for Skill Balance ===
    st.subheader("📊 Team Skill Balance Radar Chart")

    labels = list(report["skill_balance"].keys())
    values = list(report["skill_balance"].values())
    values += values[:1]
    angles = [n / float(len(labels)) - 2 - pi for n in range(len(labels))]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    plt.xticks(angles[:-1], labels)
    ax.plot(angles, values, linewidth=2, linestyle="solid")
    ax.fill(angles, values, alpha=0.25)
    st.pyplot(fig)

    # === Ranked Researchers ===
    st.subheader("🏆 Ranked Researchers")
    df = pd.DataFrame(report["ranked_candidates"])
    st.dataframe(df[["name", "affiliation", "field", "score", "tags"]])

    st.subheader("💬 AI Justifications")
    for c in report["ranked_candidates"]:
        st.markdown(f"**{c['name']}*- ({c['affiliation']}, {c['field']})  — _{c['justification']}_")

    # === PDF Export Button ===
    if st.button("📄 Generate PDF Report"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, txt="AI Research Team Builder Report", ln=True, align="C")

        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, txt="Team Summary:\n" + report["team_summary"])
        pdf.ln(5)

        pdf.multi_cell(0, 10, txt="Key Strengths:")
        for s in report["key_strengths"]:
            pdf.cell(10)
            pdf.multi_cell(0, 8, f"- {s}")

        pdf.ln(3)
        pdf.multi_cell(0, 10, txt="Potential Gaps:")
        for g in report["potential_gaps"]:
            pdf.cell(10)
            pdf.multi_cell(0, 8, f"- {g}")

        pdf.ln(5)
        pdf.multi_cell(0, 10, txt="Top Candidates:")
        for c in report["ranked_candidates"]:
            pdf.cell(10)
            pdf.multi_cell(0, 8, f"{c['name']} ({c['affiliation']}, {c['field']}) — {c['justification']}")

        file_path = "/tmp/team_report.pdf"
        pdf.output(file_path)
        with open(file_path, "rb") as f:
            st.download_button("⬇️ Download PDF", f, file_name="AI_Team_Report.pdf")

```

---

### 🧮 3. Radar Chart = Skill Coverage Snapshot

- Shows team expertise coverage by research subfield
- Identifies imbalances or missing domains visually
- Can be generated dynamically from your metric model or skill_coverage field in LangGraph pipeline

**Example**:
- High coverage in AI Safety, Robotics, Control Systems
- Low coverage in Human Factors, Ethics

---

### 📄 4. PDF Report Features

- Title, summary, and team rationale
- Auto-generated list of strengths, gaps, and justifications
- Downloadable AI_Team_Report.pdf for grant or proposal use
- Extendable to include:
    - Institution logos
    - Ranking charts
    - Metric tables
    - LLM-signed justification footnotes

---

### 🧠 5. Optional Future Extensions



| Feature                  | Description                                                         |
|--------------------------|---------------------------------------------------------------------|
| **Interactive Heatmap*-  | Show an expertise overlap matrix between team members and skills    |
| **Diversity Index*-      | Compute and display diversity scores (institution, region, gender)  |
| **Team Synergy Simulation*- | Predict collaboration impact using citation/coauthor networks    |
| **PDF Branding*-         | Add funding program logos or metadata (e.g., Horizon Europe, NSF)   |
| **Multi-Team Comparison**| Compare several possible teams for proposal optimization            |


Would you like me to extend this next with the heatmap visualization (expertise overlap matrix between existing team & candidate researchers)?
That’s often very powerful for visualizing complementarity and missing skills.


---


**ChatGPT**:

Perfect ✅ — here’s the final extended architecture for your AI-powered Research Team Recommender System with an LLM justification generator built on LangGraph + Streamlit:


### 🧠 System Overview

*Goal*:
 - Automatically identify, score, rank, and justify top researchers suitable for a funding call, industry collaboration, or academic project.

---

### ⚙️ LangGraph Pipeline Overview

```css
[Input Node] → [Researcher Retriever] → [Scoring Node] → [Reranker Node] → [LLM Justification Generator] → [Streamlit Visualization]
```

---

### 🧩 Node 1: Input Node (TeamSelectionInput)

**Purpose**: Accepts user-defined criteria for team formation.

**Inputs**:
```json
{
  "research_area": "AI for drug discovery",
  "region": "Europe",
  "university": "ETH Zurich",
  "publication_source": "Nature, Science, NeurIPS",
  "team_goal": "Build an interdisciplinary team for AI-enabled pharmacology"
}

```


---

### 🧩 Node 2: Researcher Retriever (ResearcherRetriever)


**Purpose**: Retrieves candidate researchers from knowledge graph, Elasticsearch, or API (Web of Science, Dimensions, Scopus, etc.).

**Logic**:
- Semantic + keyword search using embeddings
- Filters by region, field, journal, affiliation

**Output Example**:

```json
[
  {"author_id": "A123", "name": "Prof. Alice Smith", "affiliation": "ETH Zurich", "h_index": 85, "topics": ["AI", "Molecular Modeling"], "papers": 120},
  {"author_id": "A456", "name": "Dr. Carlos Gomez", "affiliation": "Cambridge", "h_index": 62, "topics": ["Chemoinformatics", "ML"], "papers": 90}
]

```

---

### 🧩 Node 3: Scoring Node (ResearcherScorer)


**Purpose**: Computes composite metric scores.

**Scoring Metrics**:

| Metric              | Formula                                             | Weight |
|---------------------|-----------------------------------------------------|--------|
| Productivity        | log(paper_count)                                    | 0.2    |
| Impact              | normalized_citation_index                           | 0.3    |
| Prestige            | journal_quality_score                               | 0.2    |
| Collaboration Fit   | cosine_similarity(team_embedding, author_embedding) | 0.2    |
| Interdisciplinarity | topic_diversity_index                               | 0.1    |

**Output Example**:

```json
[
  {"author_id": "A123", "total_score": 0.91, "impact": 0.93, "fit": 0.88},
  {"author_id": "A456", "total_score": 0.83, "impact": 0.78, "fit": 0.85}
]

```

---

### 🧩 Node 4: Reranker Node (HybridReranker)

**Purpose**: Combines quantitative + semantic scores.

**Logic**:
- Rank by weighted average
- Optionally include LLM reranker for contextual refinement
- Penalize redundant expertise to maximize team diversity

**Output Example**:

```json
{
  "ranked_candidates": [
    {"author_id": "A123", "rank": 1},
    {"author_id": "A456", "rank": 2}
  ]
}
```


---

### 🧩 Node 5: Justification Generator Node (LLMJustifier)


**Purpose**: Uses LLM to produce natural-language explanations for top-10 researchers.

**Prompt Template Example**:

```python
prompt = """
    You are an AI research team builder. 
    Explain why each researcher was chosen given their metrics and expertise.

    Input:
    - Project Goal: {team_goal}
    - Researcher Profile: {profile_json}
    - Score Breakdown: {score_json}

    Output: A concise explanation highlighting expertise fit, impact, and collaboration complementarity.
    """

```

**Example Output**:

```json
[
  {
    "author": "Prof. Alice Smith",
    "justification": "Alice Smith leads AI-driven drug modeling with 120 papers and a strong cross-domain profile in machine learning and chemistry. Her high citation index and ETH Zurich affiliation make her ideal for the proposed team."
  }
]

```

---

### 💻 Streamlit UI (team_recommender_app.py)


**Main Features**:

- Input panel for criteria (area, region, team goal)
- Interactive chart (bar or radar) for metric comparison
- Table of top-20 ranked researchers
- Expandable justification cards for top-10
- Export to CSV / JSON / PDF

**Sample Layout**:

```python
import streamlit as st
import pandas as pd

st.title("AI Research Team Recommender")

criteria = st.sidebar.text_area("Enter your project criteria:")
if st.button("Find Researchers"):
    # call LangGraph pipeline
    ranked = run_langgraph_pipeline(criteria)
    df = pd.DataFrame(ranked)
    st.dataframe(df[["rank", "name", "affiliation", "total_score"]])
    for row in df.head(10).to_dict(orient="records"):
        with st.expander(f"{row['rank']}. {row['name']} ({row['affiliation']})"):
            st.markdown(row["justification"])

```

---

### 🔍 Extended Capabilities

- 🧩 “Skill Gap” detection: Compare existing team vs new candidates to fill missing expertise.
- 🌍 Multi-region balance scoring (diversity index).
- 🤝 Collaboration potential metric (shared coauthors, citation links).
- 💬 Explainable AI node (LLM justification with citations).
- 🧾 Exportable team dossier (PDF/JSON for funding proposal annex).

Would you like me to generate the LangGraph YAML + Python implementation skeleton (ready to run) for this pipeline — including LLMJustifier node integration?


---

**ChatGPT**:

Great — below is a ready-to-use LangGraph-style YAML pipeline plus a Python implementation skeleton you can drop into your codebase. It wires retrieval → scoring → reranking → LLM-based justification → explainable report. All heavy integration points (Elasticsearch/FAISS, metric DB, embedding service, LLM) are clearly marked as replaceable stubs so you can hook your real data and secrets.

**Notes**:
- Replace all TODO placeholders with your real connectors (Elasticsearch/FAISS, Web of Science / InCites / internal metrics, and your LLM/embedding client).
- The LLM code uses a generic ChatModel wrapper so you can swap in your provider (OpenAI / Anthropic / internal).
- This is a skeleton for clarity and quick integration — you can expand individual nodes with async I/O, caching, and batching as needed.


---

### 1) LangGraph Pipeline (YAML)

```yaml
id: ai_team_builder_pipeline
description: LangGraph pipeline to retrieve, score, rerank and justify recommended researchers.

inputs:
  project_title: string
  project_summary: string
  keywords: array
  target_regions: array
  target_institutions: array
  existing_team: array

outputs:
  report: object

nodes:
  - id: ProjectVectorNode
    type: embedding
    description: "Embed project text into a vector"
    model: text-embedding-3-large
    input: "{{ project_summary || keywords }}"
    output: project_vector

  - id: ResearcherRetrieverNode
    type: retriever
    description: "Dense retriever over authors index (ES/FAISS)"
    params:
      index: authors_index
      vector_field: author_vector
      size: 500
    input:
      query_vector: "{{ project_vector }}"
      filters:
        regions: "{{ target_regions }}"
        institutions: "{{ target_institutions }}"
    output: candidates

  - id: MetricScorerNode
    type: function
    description: "Compute normalized metrics (impact, activity, collab, interdisciplinarity)"
    function: compute_author_metrics
    input:
      candidates: "{{ candidates }}"
      existing_team: "{{ existing_team }}"
    output: scored_candidates

  - id: HybridRerankerNode
    type: function
    description: "Combine metrics + semantic fit and penalize redundancy"
    function: rerank_and_deduplicate
    input:
      scored_candidates: "{{ scored_candidates }}"
      max_candidates: 50
    output: reranked_candidates

  - id: LLMJustifierNode
    type: llm
    description: "Generate human-readable justifications for top-N researchers"
    model: gpt-5
    input:
      top_candidates: "{{ reranked_candidates[:10] }}"
      project_summary: "{{ project_summary }}"
    output: justified_candidates

  - id: ExplainableReportGeneratorNode
    type: llm
    description: "Produce structured JSON report summarizing team, strengths, gaps"
    model: gpt-5
    input:
      justified_candidates: "{{ justified_candidates }}"
      project_summary: "{{ project_summary }}"
      existing_team: "{{ existing_team }}"
    output: report

edges:
  - source: ProjectVectorNode
    target: ResearcherRetrieverNode
  - source: ResearcherRetrieverNode
    target: MetricScorerNode
  - source: MetricScorerNode
    target: HybridRerankerNode
  - source: HybridRerankerNode
    target: LLMJustifierNode
  - source: LLMJustifierNode
    target: ExplainableReportGeneratorNode

```

---

### 2) Python Implementation Skeleton


Save as team_builder_nodes.py (or split into modules). This is intentionally synchronous/simple so you can run and test locally; production systems should add batching, retries, robust error handling.

```python
# team_builder_nodes.py
import json
import math
import numpy as np
from typing import List, Dict, Any

# --------------------
# Helpers: Replace these stubs with real clients
# --------------------
class EmbeddingClient:
    def embed(self, texts: List[str]) -> List[List[float]]:
        # TODO: call your embedding provider (OpenAI/other)
        # Example: return [np.random.rand(1536).tolist() for _ in texts]
        return [[0.0]*1536 for _ in texts]

class VectorDB:
    def knn_search(self, index: str, vector: List[float], k: int = 200, filters: Dict[str, Any] = None) -> List[Dict]:
        # TODO: implement Elasticsearch or FAISS search
        # Each hit should include: author_id, name, affiliation, country, research_fields,
        # author_vector (dense), h_index, fnci, citations, intl_collab_ratio, recent_pubs_5yr
        return []

class MetricsDB:
    def fetch_author_metrics(self, author_ids: List[str]) -> Dict[str, Dict]:
        # TODO: query Web of Science/InCites or internal metrics DB
        return {}

class ChatModel:
    def __init__(self, model_name: str = "gpt-5"):
        # TODO: init your LLM client with API key / config
        self.model_name = model_name

    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.3) -> str:
        # TODO: call your LLM inference endpoint and return text
        return "LLM response for prompt."

# --------------------
# Node implementations
# --------------------
def embed_project(project_summary: str, keywords: List[str], embedder: EmbeddingClient):
    text = project_summary
    if keywords:
        text += " " + " ".join(keywords)
    emb = embedder.embed([text])[0]
    # normalize
    arr = np.array(emb, dtype=float)
    nrm = arr / (np.linalg.norm(arr) + 1e-9)
    return nrm.tolist()

def retrieve_candidates(project_vector: List[float], vectordb: VectorDB, index: str = "authors_index", filters: Dict = None, top_k: int = 500):
    hits = vectordb.knn_search(index=index, vector=project_vector, k=top_k, filters=filters)
    # ensure vectors are numpy arrays for later
    for h in hits:
        h["author_vector"] = np.array(h.get("author_vector", [0.0]*len(project_vector)), dtype=float)
    return hits

def compute_author_metrics(candidates: List[Dict], metrics_db: MetricsDB, existing_team: List[Dict] = None):
    """
    Compute normalized metrics for each candidate.
    Returns candidates with added 'metrics' dict.
    """
    author_ids = [c["author_id"] for c in candidates]
    metrics_map = metrics_db.fetch_author_metrics(author_ids)  # {author_id: {h_index:.., fnci:.., citations:..}}
    # build existing team embedding if provided
    existing_topics = {}
    if existing_team:
        for m in existing_team:
            for t in m.get("research_fields", []):
                existing_topics[t] = existing_topics.get(t, 0) + 1

    for c in candidates:
        mid = c["author_id"]
        m = metrics_map.get(mid, {})
        h_index = m.get("h_index", 0)
        fnci = m.get("fnci", 1.0)
        citations = m.get("citations", 0)
        recent_pubs = m.get("recent_pubs_5yr", 0)
        intl_ratio = m.get("intl_collab_ratio", 0.2)

        # compute normalized sub-scores (0..1)
        impact_score = min(1.0, (math.log1p(citations) / 10.0) + (fnci / 3.0))
        activity_score = min(1.0, math.log1p(recent_pubs) / 3.0)
        collaboration_score = min(1.0, intl_ratio)  # assume ratio in 0..1

        # topic similarity later computed with project vector
        c["metrics"] = {
            "h_index": h_index,
            "fnci": fnci,
            "citations": citations,
            "impact_score": impact_score,
            "activity_score": activity_score,
            "collaboration_score": collaboration_score,
            # placeholder: topic_similarity filled later
            "topic_similarity": 0.0
        }

    return candidates

def compute_topic_similarity(project_vector: np.ndarray, candidates: List[Dict]):
    p = np.array(project_vector, dtype=float)
    p_norm = p / (np.linalg.norm(p) + 1e-9)
    for c in candidates:
        a = c["author_vector"]
        a_norm = a / (np.linalg.norm(a) + 1e-9)
        sim = float(np.dot(p_norm, a_norm))
        c["metrics"]["topic_similarity"] = sim
    return candidates

def composite_score(c: Dict, weights: Dict = None):
    if weights is None:
        weights = {
            "topic_similarity": 0.30,
            "impact_score": 0.30,
            "collaboration_score": 0.20,
            "activity_score": 0.20
        }
    m = c["metrics"]
    score = (
        weights["topic_similarity"] - m.get("topic_similarity", 0.0) +
        weights["impact_score"] - m.get("impact_score", 0.0) +
        weights["collaboration_score"] - m.get("collaboration_score", 0.0) +
        weights["activity_score"] - m.get("activity_score", 0.0)
    )
    return score

def rerank_and_deduplicate(candidates: List[Dict], max_candidates: int = 50):
    # compute composite
    for c in candidates:
        c["composite_score"] = composite_score(c)
    # sort
    ranked = sorted(candidates, key=lambda x: x["composite_score"], reverse=True)
    # simple dedup by affiliation+name
    seen = set()
    filtered = []
    for r in ranked:
        key = (r.get("name", "").lower(), r.get("affiliation", "").lower())
        if key in seen:
            continue
        seen.add(key)
        filtered.append(r)
        if len(filtered) >= max_candidates:
            break

    return filtered

# LLM Justifier
def llm_justify(top_candidates: List[Dict], project_summary: str, llm: ChatModel, max_items: int = 10):
    justifications = []
    for c in top_candidates[:max_items]:
        prompt = f"""
You are an expert research program advisor.
Project brief:
{project_summary}

Researcher profile (json):
{json.dumps(c, indent=2)}

Produce a concise justification (2-3 sentences) explaining:
- Why this researcher fits the project (topics)
- What strengths (impact, collaboration) they bring
- Suggested role (PI / Co-PI / Collaborator)
Return ONLY the justification text.
"""
        text = llm.generate(prompt)
        c_out = dict(c)
        c_out["justification"] = text.strip()
        # role suggestion heuristics
        if c["metrics"]["impact_score"] > 0.8 and c["metrics"]["topic_similarity"] > 0.7:
            c_out["suggested_role"] = "PI"
        elif c["metrics"]["topic_similarity"] > 0.6:
            c_out["suggested_role"] = "Co-PI"
        else:
            c_out["suggested_role"] = "Collaborator"
        justifications.append(c_out)
    return justifications

def explainable_report(justified_candidates: List[Dict], project_summary: str, llm: ChatModel, existing_team: List[Dict] = None):
    # Build prompt for structured JSON report
    prompt = f"""
You are an AI assistant that generates an explainable team report.
Project summary:
{project_summary}

Top candidates (json):
{json.dumps(justified_candidates, indent=2)}

Existing team:
{json.dumps(existing_team or [], indent=2)}

Produce a JSON object with keys:
- team_summary: one-paragraph summary
- key_strengths: list of 3-5 short items
- potential_gaps: list of 1-4 short items
- ranked_candidates: array of {{"name","affiliation","field","score","justification","suggested_role","tags"}}

Return valid JSON only.
"""
    resp = llm.generate(prompt, max_tokens=800)
    try:
        report = json.loads(resp)
    except Exception:
        # fallback: return a basic summarization
        report = {
            "team_summary": "Unable to parse LLM JSON. See raw text.",
            "raw_text": resp
        }
    return report

# --------------------
# Orchestration function
# --------------------
def run_team_builder_pipeline(inputs: Dict[str, Any],
                              embedder: EmbeddingClient,
                              vectordb: VectorDB,
                              metrics_db: MetricsDB,
                              llm: ChatModel,
                              config: Dict = None) -> Dict:
    # 1. embed
    project_vector = embed_project(inputs.get("project_summary",""), inputs.get("keywords", []), embedder)
    # 2. retrieve
    filters = {"regions": inputs.get("target_regions"), "institutions": inputs.get("target_institutions")}
    candidates = retrieve_candidates(project_vector=project_vector, vectordb=vectordb, filters=filters, top_k=500)
    # 3. metrics
    candidates = compute_author_metrics(candidates, metrics_db, existing_team=inputs.get("existing_team"))
    # 4. topic similarity
    candidates = compute_topic_similarity(np.array(project_vector, dtype=float), candidates)
    # 5. rerank & dedupe
    reranked = rerank_and_deduplicate(candidates, max_candidates=100)
    # 6. LLM justifications for top N
    top_for_just = reranked[:20]
    justified = llm_justify(top_for_just, inputs.get("project_summary", ""), llm, max_items=10)
    # 7. explainable report
    report = explainable_report(justified, inputs.get("project_summary", ""), llm, existing_team=inputs.get("existing_team"))
    return report


```

---

### 3) Example Runner / Minimal CLI

Save as run_pipeline.py:

```python
from team_builder_nodes import EmbeddingClient, VectorDB, MetricsDB, ChatModel, run_team_builder_pipeline

if __name__ == "__main__":
    embedder = EmbeddingClient()
    vectordb = VectorDB()
    metrics_db = MetricsDB()
    llm = ChatModel(model_name="gpt-5")

    inputs = {
        "project_title": "AI-driven materials discovery for sustainable batteries",
        "project_summary": "We aim to discover new cathode materials using ML + high-throughput experiments...",
        "keywords": ["materials discovery", "batteries", "machine learning"],
        "target_regions": ["Global"],
        "target_institutions": [],
        "existing_team": []
    }

    report = run_team_builder_pipeline(inputs, embedder, vectordb, metrics_db, llm)
    print(json.dumps(report, indent=2))

```

---


### 4) Streamlit UI (Quick-connect)

You can reuse the Streamlit code I provided earlier; here’s how to call the pipeline from Streamlit:

```python
# streamlit_app.py (excerpt)
import streamlit as st
import json
from run_pipeline import run_team_builder_pipeline, EmbeddingClient, VectorDB, MetricsDB, ChatModel

st.title("AI Team Builder")

project_summary = st.text_area("Project summary")
if st.button("Generate"):
    with st.spinner("Running pipeline..."):
        embedder = EmbeddingClient()
        vectordb = VectorDB()
        metrics_db = MetricsDB()
        llm = ChatModel()
        inputs = {"project_summary": project_summary, "keywords": [], "target_regions": []}
        report = run_team_builder_pipeline(inputs, embedder, vectordb, metrics_db, llm)
    st.json(report)

```

---

### 5) Deployment & Security Notes

- Keep API keys and credentials in environment variables or a secure secret manager. Don’t hardcode.
- Add rate limiting and batching for LLM/embedding calls to control costs.
- For reproducibility, persist retrieved candidate lists and metrics for audit / show-cause during proposal review.
- Add a logging/audit trail showing exact metrics used to justify each candidate (helpful for reviewers).

---

### 6) Next steps I can help with (pick any)

- Provide a concrete ES query and mapping for an authors_index compatible with the code.
- Implement the EmbeddingClient and ChatModel for a specific provider (OpenAI / Anthropic) with sample code.
- Add unit tests and a small sample dataset to demo end-to-end.
- Build the Streamlit app fully integrated with your data sources and deploy instructions (Docker/Cloud Run).

If you want, I can now generate the Elasticsearch index mapping and an example ES query to run the ResearcherRetriever (very useful next step). Which integration would you like me to produce now?


---

**ChatGPT**:

Perfect — let’s create a concrete Elasticsearch index mapping for your authors_index and an example query compatible with the LangGraph pipeline we just built. This will let you plug in your academic/researcher data and perform vector + filtered searches.

---

### 1) Elasticsearch Index Mapping (authors_index)


```json
PUT /authors_index
{
  "mappings": {
    "properties": {
      "author_id": { "type": "keyword" },
      "name": { "type": "text" },
      "affiliation": { "type": "text" },
      "country": { "type": "keyword" },
      "research_fields": { "type": "keyword" },
      "author_vector": { "type": "dense_vector", "dims": 1536 },
      "h_index": { "type": "integer" },
      "fnci": { "type": "float" },
      "citations": { "type": "integer" },
      "recent_pubs_5yr": { "type": "integer" },
      "intl_collab_ratio": { "type": "float" },
      "top_journal_papers": { "type": "integer" }
    }
  }
}


```

**Notes**:
- author_vector: 1536-dimensional embedding (from your embedding model).
- research_fields: keyword array for filtering by area.
- Metrics (h_index, FNCI, citations) used for scoring.

---

### 2) Example ES Query – Vector + Filters

Assume project_vector is a 1536-dimensional array from the embedding model.

```json
POST /authors_index/_search
{
  "size": 50,
  "_source": ["author_id","name","affiliation","country","research_fields","h_index","fnci","citations","recent_pubs_5yr","intl_collab_ratio","author_vector"],
  "query": {
    "script_score": {
      "query": {
        "bool": {
          "filter": [
            { "terms": { "country": ["USA","Europe"] } },
            { "terms": { "research_fields": ["AI","Machine Learning"] } }
          ]
        }
      },
      "script": {
        "source": "cosineSimilarity(params.project_vector, 'author_vector') + 1.0",
        "params": {
          "project_vector": [0.01, 0.23, 0.45, "..."]  // 1536-d vector
        }
      }
    }
  },
  "sort": [
    { "_score": { "order": "desc" } }
  ]
}

```

**Explanation**:
- script_score: ranks candidates by cosine similarity to the project embedding.
- Filters: restrict by region/country and research fields.
- _source: retrieves all metadata needed for scoring and LLM justification.


---

### 3) Python Elasticsearch Query Wrapper

```python
from elasticsearch import Elasticsearch

es = Elasticsearch(hosts=["http://localhost:9200"])

def search_authors(project_vector, countries=None, fields=None, top_k=50):
    query = {
        "size": top_k,
        "_source": ["author_id","name","affiliation","country","research_fields","h_index","fnci","citations","recent_pubs_5yr","intl_collab_ratio","author_vector"],
        "query": {
            "script_score": {
                "query": {
                    "bool": {
                        "filter": [
                            {"terms": {"country": countries or []}},
                            {"terms": {"research_fields": fields or []}}
                        ]
                    }
                },
                "script": {
                    "source": "cosineSimilarity(params.project_vector, 'author_vector') + 1.0",
                    "params": {"project_vector": project_vector}
                }
            }
        },
        "sort": [{"_score": {"order": "desc"}}]
    }
    res = es.search(index="authors_index", body=query)
    return [hit["_source"] for hit in res["hits"]["hits"]]

```

**Notes**:
- Replace countries or fields with your pipeline inputs.
- cosineSimilarity in ES returns similarity in [-1,1]; adding +1 ensures positive scores.
- You can extend this with pagination for large datasets.

---

### ✅ Integration Tips

1. Embeddings: Precompute author vectors using the same embedding model as project embeddings.
2. Metric DB: Retrieve h_index, FNCI, citations, etc., after ES retrieval for scoring.
3. Filters: Can include region, university, career stage, or top journal publications.
4. Performance: For large datasets, consider hybrid approach: ES for filtering + FAISS for exact vector search.
5. Pipeline plug-in: Use search_authors in the ResearcherRetrieverNode in your Python LangGraph pipeline.

If you want, I can produce a complete Python example that plugs this ES query directly into the LangGraph pipeline end-to-end with embedding, scoring, LLM justification, and final JSON report — fully runnable with mock data.
Do you want me to do that next?


---

**ChatGPT**:

Perfect — let’s build a fully runnable Python example integrating Elasticsearch retrieval → metric scoring → reranking → LLM justification → final JSON report. We’ll use mock embeddings and metrics so you can run it end-to-end immediately and replace with real data later.


### 1️⃣ Full Python Pipeline Example

Save as run_full_pipeline.py:

```python
import numpy as np
import json
from elasticsearch import Elasticsearch

# -----------------------------
# 1) Mock / Stub Clients
# -----------------------------
class EmbeddingClient:
    def embed(self, texts):
        # returns fixed-dim vector (1536) for demo
        return [np.random.rand(1536).tolist() for _ in texts]

class MetricsDB:
    def fetch_author_metrics(self, author_ids):
        # return mock metrics
        return {aid: {"h_index": np.random.randint(20, 100),
                      "fnci": np.random.rand()*3,
                      "citations": np.random.randint(50,1000),
                      "recent_pubs_5yr": np.random.randint(5,30),
                      "intl_collab_ratio": np.random.rand()} for aid in author_ids}

class ChatModel:
    def generate(self, prompt, max_tokens=512, temperature=0.3):
        # mock LLM response
        return "This researcher is selected for their strong expertise and impact in the field."

# -----------------------------
# 2) Elasticsearch Search
# -----------------------------
def search_authors(project_vector, es_client, countries=None, fields=None, top_k=50):
    # For demo, return mock authors
    authors = []
    for i in range(top_k):
        authors.append({
            "author_id": f"A{i+1}",
            "name": f"Researcher {i+1}",
            "affiliation": np.random.choice(["MIT", "ETH Zurich", "Stanford"]),
            "country": np.random.choice(["USA","Europe"]),
            "research_fields": np.random.choice(["AI","ML","Robotics","Control Systems"],2).tolist(),
            "author_vector": np.random.rand(1536),
            "h_index": np.random.randint(30, 100),
            "fnci": np.random.rand()*3,
            "citations": np.random.randint(100,2000),
            "recent_pubs_5yr": np.random.randint(5,30),
            "intl_collab_ratio": np.random.rand()
        })
    return authors

# -----------------------------
# 3) Compute metrics & composite score
# -----------------------------
def compute_topic_similarity(project_vector, candidates):
    p = np.array(project_vector)
    p_norm = p / (np.linalg.norm(p)+1e-9)
    for c in candidates:
        a = np.array(c["author_vector"])
        a_norm = a / (np.linalg.norm(a)+1e-9)
        sim = float(np.dot(p_norm, a_norm))
        c["topic_similarity"] = sim
    return candidates

def composite_score(c):
    # weights: topic_similarity=0.3, impact=0.3, collaboration=0.2, activity=0.2
    impact = min(1.0, (np.log1p(c["citations"])/10.0) + (c["fnci"]/3.0))
    activity = min(1.0, np.log1p(c["recent_pubs_5yr"])/3.0)
    collaboration = min(1.0, c["intl_collab_ratio"])
    score = 0.3*c["topic_similarity"] + 0.3*impact + 0.2*collaboration + 0.2*activity
    return score

def rerank_and_deduplicate(candidates, max_candidates=50):
    for c in candidates:
        c["composite_score"] = composite_score(c)
    ranked = sorted(candidates, key=lambda x: x["composite_score"], reverse=True)
    seen = set()
    filtered = []
    for r in ranked:
        key = (r["name"].lower(), r["affiliation"].lower())
        if key in seen:
            continue
        seen.add(key)
        filtered.append(r)
        if len(filtered)>=max_candidates:
            break
    return filtered

# -----------------------------
# 4) LLM Justification
# -----------------------------
def llm_justify(top_candidates, project_summary, llm, max_items=10):
    justified = []
    for c in top_candidates[:max_items]:
        prompt = f"""
Project Summary: {project_summary}
Researcher profile: {json.dumps(c)}
Explain why this researcher is selected (2-3 sentences).
"""
        c_out = dict(c)
        c_out["justification"] = llm.generate(prompt)
        # simple role heuristic
        if c["composite_score"]>0.8 and c["topic_similarity"]>0.7:
            c_out["suggested_role"] = "PI"
        elif c["topic_similarity"]>0.6:
            c_out["suggested_role"] = "Co-PI"
        else:
            c_out["suggested_role"] = "Collaborator"
        justified.append(c_out)
    return justified

# -----------------------------
# 5) Explainable Report
# -----------------------------
def explainable_report(justified_candidates, project_summary):
    report = {
        "team_summary": f"Top experts selected for the project: {project_summary[:80]}...",
        "key_strengths": ["High impact", "Cross-domain expertise", "Strong collaborations"],
        "potential_gaps": ["Some emerging fields underrepresented"],
        "ranked_candidates": [{
            "name": c["name"],
            "affiliation": c["affiliation"],
            "field": ", ".join(c["research_fields"]),
            "score": round(c["composite_score"],3),
            "justification": c["justification"],
            "suggested_role": c["suggested_role"],
            "tags": ["Top Impact", "Domain Expert"]
        } for c in justified_candidates]
    }
    return report

# -----------------------------
# 6) Orchestration
# -----------------------------
def run_pipeline(project_summary):
    embedder = EmbeddingClient()
    es_client = Elasticsearch()
    metrics_db = MetricsDB()
    llm = ChatModel()

    # 1) embed project
    project_vector = embedder.embed([project_summary])[0]

    # 2) retrieve candidates
    candidates = search_authors(project_vector, es_client, countries=["USA","Europe"], fields=["AI","ML"], top_k=50)

    # 3) compute topic similarity
    candidates = compute_topic_similarity(project_vector, candidates)

    # 4) rerank & deduplicate
    reranked = rerank_and_deduplicate(candidates, max_candidates=20)

    # 5) LLM justification
    justified = llm_justify(reranked, project_summary, llm, max_items=10)

    # 6) generate report
    report = explainable_report(justified, project_summary)
    return report

# -----------------------------
# 7) Run Example
# -----------------------------
if __name__=="__main__":
    project_summary = "We aim to develop an AI-driven framework for sustainable battery materials discovery using machine learning and high-throughput simulations."
    report = run_pipeline(project_summary)
    print(json.dumps(report, indent=2))

```

---

### ✅ Key Features in This Example

1. Elasticsearch-style retrieval (mocked here; replace with real ES client).
2. Composite scoring based on topic similarity, impact, collaboration, activity.
3. Reranking & deduplication to remove redundant candidates.
4. LLM justification for top 10 researchers.
5. Structured JSON report with team summary, strengths, gaps, and top candidates.

You can now run this file directly:
```bash
python run_full_pipeline.py
```
…to see a fully mocked top-10 researcher team report, ready to integrate into Streamlit.

If you want, I can also provide a fully integrated Streamlit app using this pipeline that shows top-20 candidates with radar/heatmap skill coverage and LLM justifications, ready for interactive use.
Do you want me to do that next?


---


**ChatGPT**:
Perfect — let’s build a fully interactive Streamlit app that integrates the pipeline you already have. It will:
- Accept project criteria (summary, keywords, region, institutions)
- Run the retrieval → scoring → reranking → LLM justification pipeline
- Show top-20 researchers in a table
- Include expandable cards for LLM justifications
- Optionally display skill/topic coverage with a radar chart

---

### 1️⃣ Streamlit App Code (streamlit_team_builder.py)

```python
import streamlit as st
import pandas as pd
import numpy as np
from run_full_pipeline import run_pipeline

# -----------------------------
# 1) Page setup
# -----------------------------
st.set_page_config(page_title="AI Research Team Builder", layout="wide")
st.title("AI-Powered Research Team Builder")
st.markdown("""
This tool recommends top researchers for your project based on expertise, impact, collaboration, and topic fit.
""")

# -----------------------------
# 2) Sidebar inputs
# -----------------------------
with st.sidebar:
    st.header("Project Input")
    project_summary = st.text_area("Project Summary", height=150)
    keywords = st.text_input("Keywords (comma separated)", "")
    target_regions = st.text_input("Target Regions (comma separated, optional)", "")
    target_institutions = st.text_input("Target Institutions (comma separated, optional)", "")

# -----------------------------
# 3) Run pipeline button
# -----------------------------
if st.button("Generate Team Recommendations"):
    if not project_summary.strip():
        st.warning("Please enter a project summary.")
    else:
        with st.spinner("Running pipeline..."):
            inputs = {
                "project_summary": project_summary,
                "keywords": [k.strip() for k in keywords.split(",") if k.strip()],
                "target_regions": [r.strip() for r in target_regions.split(",") if r.strip()],
                "target_institutions": [i.strip() for i in target_institutions.split(",") if i.strip()],
            }
            report = run_pipeline(project_summary)

        # -----------------------------
        # 4) Show team summary and strengths
        # -----------------------------
        st.subheader("Team Summary")
        st.markdown(report.get("team_summary", ""))
        st.markdown("**Key Strengths:*- " + ", ".join(report.get("key_strengths", [])))
        st.markdown("**Potential Gaps:*- " + ", ".join(report.get("potential_gaps", [])))

        # -----------------------------
        # 5) Show top candidates in a table
        # -----------------------------
        st.subheader("Top 20 Recommended Researchers")
        candidates_df = pd.DataFrame(report.get("ranked_candidates", []))
        display_cols = ["name","affiliation","field","score","suggested_role"]
        st.dataframe(candidates_df[display_cols].sort_values(by="score", ascending=False))

        # -----------------------------
        # 6) Expandable LLM justifications
        # -----------------------------
        st.subheader("LLM Justifications")
        for idx, row in candidates_df.head(10).iterrows():
            with st.expander(f"{row['name']} ({row['affiliation']}) - {row['suggested_role']}"):
                st.markdown(f"**Score:*- {row['score']}")
                st.markdown(f"**Field(s):*- {row['field']}")
                st.markdown(f"**Justification:*- {row['justification']}")

        # -----------------------------
        # 7) Optional radar chart for topic coverage
        # -----------------------------
        st.subheader("Skill / Topic Coverage")
        all_fields = set()
        for f in candidates_df["field"]:
            for ff in f.split(","):
                all_fields.add(ff.strip())
        all_fields = list(all_fields)

        field_scores = {f:0 for f in all_fields}
        for idx, row in candidates_df.iterrows():
            for f in row["field"].split(","):
                f = f.strip()
                field_scores[f] += row["score"]

        # Normalize
        max_score = max(field_scores.values()) if field_scores else 1
        normalized_scores = [field_scores[f]/max_score for f in all_fields]

        import matplotlib.pyplot as plt

        # Radar chart
        angles = np.linspace(0, 2*np.pi, len(all_fields), endpoint=False).tolist()
        normalized_scores += normalized_scores[:1]  # close the loop
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
        ax.plot(angles, normalized_scores, 'o-', linewidth=2)
        ax.fill(angles, normalized_scores, alpha=0.25)
        ax.set_thetagrids(np.degrees(angles[:-1]), all_fields)
        ax.set_title("Aggregate Field Coverage")
        ax.set_ylim(0,1)
        st.pyplot(fig)

```

---

### 2️⃣ How to Run

1. Make sure your pipeline run_full_pipeline.py is in the same folder.
2. Install dependencies:
```bash
pip install streamlit pandas matplotlib numpy elasticsearch
```
3. Run the Streamlit app:
```bash
streamlit run streamlit_team_builder.py
```
4. Enter a project summary, optional keywords, regions, and institutions.
5. Click Generate Team Recommendations.

You will see:
- Team summary + key strengths / gaps
- Top-20 researchers table (sortable by score)
- Expandable LLM justifications for top 10
- Radar chart of skill/topic coverage

---

### ✅ Key Features

- End-to-end retrieval → scoring → rerank → LLM justification
- Interactive visualization of candidate scores
- Expandable explanations for reviewer/funder-ready reports
- Radar chart for gaps / strengths in research fields
- Fully modular; can replace mock ES / LLM with real services

If you want, I can also extend this app to include:

1. Existing team input → show missing skills automatically
2. Auto role assignment: PI / Co-PI / Collaborator
3. Export PDF / CSV for funding applications
Do you want me to add these next?


---



**ChatGPT**:

Perfect — let’s extend the Streamlit app to include:

1. Existing team input → auto-detect missing skills / gaps
2. Auto role assignment → PI / Co-PI / Collaborator based on score and topic fit
   
This will make your tool truly funding/proposal-ready.

---

### 1️⃣ Updated Streamlit App (streamlit_team_builder_extended.py)

```python
import streamlit as st
import pandas as pd
import numpy as np
from run_full_pipeline import run_pipeline

# -----------------------------
# 1) Page setup
# -----------------------------
st.set_page_config(page_title="AI Research Team Builder", layout="wide")
st.title("AI-Powered Research Team Builder")
st.markdown("""
This tool recommends top researchers for your project based on expertise, impact, collaboration, and topic fit.
""")

# -----------------------------
# 2) Sidebar inputs
# -----------------------------
with st.sidebar:
    st.header("Project Input")
    project_summary = st.text_area("Project Summary", height=150)
    keywords = st.text_input("Keywords (comma separated)", "")
    target_regions = st.text_input("Target Regions (comma separated, optional)", "")
    target_institutions = st.text_input("Target Institutions (comma separated, optional)", "")
    
    st.header("Existing Team")
    existing_team_text = st.text_area("Enter existing team members (Name, Affiliation, Field) one per line")

# -----------------------------
# 3) Run pipeline button
# -----------------------------
if st.button("Generate Team Recommendations"):
    if not project_summary.strip():
        st.warning("Please enter a project summary.")
    else:
        with st.spinner("Running pipeline..."):
            inputs = {
                "project_summary": project_summary,
                "keywords": [k.strip() for k in keywords.split(",") if k.strip()],
                "target_regions": [r.strip() for r in target_regions.split(",") if r.strip()],
                "target_institutions": [i.strip() for i in target_institutions.split(",") if i.strip()],
                "existing_team": []
            }
            # parse existing team
            existing_team = []
            for line in existing_team_text.strip().split("\n"):
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 3:
                    existing_team.append({
                        "name": parts[0],
                        "affiliation": parts[1],
                        "field": parts[2]
                    })
            inputs["existing_team"] = existing_team

            # Run pipeline
            report = run_pipeline(project_summary)

        # -----------------------------
        # 4) Detect missing skills
        # -----------------------------
        st.subheader("Existing Team vs Missing Skills")
        existing_fields = set([m["field"].lower() for m in existing_team])
        top_fields = set()
        for c in report.get("ranked_candidates", []):
            for f in c["field"].split(","):
                top_fields.add(f.strip().lower())
        missing_fields = top_fields - existing_fields
        st.markdown(f"**Existing Fields:*- {', '.join(existing_fields) if existing_fields else 'None'}")
        st.markdown(f"**Missing / Needed Fields:*- {', '.join(missing_fields) if missing_fields else 'None'}")

        # -----------------------------
        # 5) Show team summary and strengths
        # -----------------------------
        st.subheader("Team Summary")
        st.markdown(report.get("team_summary", ""))
        st.markdown("**Key Strengths:*- " + ", ".join(report.get("key_strengths", [])))
        st.markdown("**Potential Gaps:*- " + ", ".join(report.get("potential_gaps", [])))

        # -----------------------------
        # 6) Show top candidates in a table
        # -----------------------------
        st.subheader("Top 20 Recommended Researchers")
        candidates_df = pd.DataFrame(report.get("ranked_candidates", []))

        # Auto role assignment based on composite score & topic fit
        for idx, row in candidates_df.iterrows():
            score = row["score"]
            topic_overlap = len(set([f.strip().lower() for f in row["field"].split(",")]) & existing_fields)/max(1,len(row["field"].split(",")))
            if score>0.8 and topic_overlap>0.7:
                role = "PI"
            elif topic_overlap>0.5:
                role = "Co-PI"
            else:
                role = "Collaborator"
            candidates_df.at[idx,"auto_role"] = role

        display_cols = ["name","affiliation","field","score","suggested_role","auto_role"]
        st.dataframe(candidates_df[display_cols].sort_values(by="score", ascending=False))

        # -----------------------------
        # 7) Expandable LLM justifications
        # -----------------------------
        st.subheader("LLM Justifications")
        for idx, row in candidates_df.head(10).iterrows():
            with st.expander(f"{row['name']} ({row['affiliation']}) - {row['auto_role']}"):
                st.markdown(f"**Score:*- {row['score']}")
                st.markdown(f"**Field(s):*- {row['field']}")
                st.markdown(f"**Justification:*- {row['justification']}")

        # -----------------------------
        # 8) Optional radar chart for skill coverage
        # -----------------------------
        st.subheader("Skill / Topic Coverage")
        all_fields = set()
        for f in candidates_df["field"]:
            for ff in f.split(","):
                all_fields.add(ff.strip())
        all_fields = list(all_fields)

        field_scores = {f:0 for f in all_fields}
        for idx, row in candidates_df.iterrows():
            for f in row["field"].split(","):
                f = f.strip()
                field_scores[f] += row["score"]

        max_score = max(field_scores.values()) if field_scores else 1
        normalized_scores = [field_scores[f]/max_score for f in all_fields]

        import matplotlib.pyplot as plt
        angles = np.linspace(0, 2*np.pi, len(all_fields), endpoint=False).tolist()
        normalized_scores += normalized_scores[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
        ax.plot(angles, normalized_scores, 'o-', linewidth=2)
        ax.fill(angles, normalized_scores, alpha=0.25)
        ax.set_thetagrids(np.degrees(angles[:-1]), all_fields)
        ax.set_title("Aggregate Field Coverage")
        ax.set_ylim(0,1)
        st.pyplot(fig)

```

---

### 2️⃣ Key Features Added

1. Existing Team Input
    - Users can enter current team members with Name, Affiliation, Field
    - The app automatically computes missing fields/skills based on top candidate coverage
2. Auto Role Assignment
    - Based on composite score and topic overlap with existing team
    - Roles assigned as: PI, Co-PI, Collaborator
    - Displayed alongside LLM suggested role
3. Interactive & Proposal-ready
    - Top-20 table, top-10 LLM justifications, radar chart for field coverage
    - Helps detect gaps and decide team structure for funding applications

---


### 3️⃣ Next Steps / Optional Enhancements

- Add export CSV / PDF for funding proposal annex
- Highlight priority gaps in radar chart with color coding
- Integrate real ES + LLM for production deployment
- Add multi-region / interdisciplinarity scoring for diverse global teams

If you want, I can now add the CSV / PDF export feature directly into this app so the full recommended team with justifications can be downloaded ready for submission.


---


**ChatGPT**:

Absolutely! Here’s a full project structure for the AI Research Team Builder system we’ve been discussing. This includes the pipeline, Elasticsearch integration, LLM justification, Streamlit UI, and export functionality for a professional and maintainable setup.


### 1️⃣ Project Folder Structure


```css
ai_research_team_builder/
│
├── README.md
├── requirements.txt
├── setup.sh               # optional: install dependencies
│
├── data/
│   └── sample_authors.json  # optional mock data for testing
│
├── es_index/
│   └── authors_index_mapping.json  # Elasticsearch index mapping
│
├── pipeline/
│   ├── __init__.py
│   ├── run_full_pipeline.py        # pipeline: retrieval, scoring, LLM justification
│   ├── embeddings.py               # embedding client (mock or real)
│   ├── metrics_db.py               # metrics database / mock
│   ├── llm_client.py               # LLM justification client (mock or OpenAI)
│   ├── es_client.py                # Elasticsearch wrapper client
│
├── app/
│   ├── __init__.py
│   ├── streamlit_team_builder.py              # original Streamlit app
│   ├── streamlit_team_builder_extended.py     # extended app with existing team, role assignment
│   ├── export_utils.py                        # CSV / PDF export functions
│
├── utils/
│   ├── __init__.py
│   ├── scoring.py                    # composite score calculation, reranking
│   ├── similarity.py                  # vector / topic similarity utils
│   ├── report_generator.py            # JSON report & radar chart generation
│
└── tests/
    ├── test_pipeline.py
    ├── test_es_integration.py
    ├── test_streamlit_ui.py
```

---

### 2️⃣ Folder & File Responsibilities


### Folder & File Responsibilities

| Folder/File                              | Purpose                                                                                   |
|------------------------------------------|-------------------------------------------------------------------------------------------|
| `pipeline/`                             | Core AI logic: retrieval, scoring, reranking, LLM justification, embeddings               |
| `pipeline/run_full_pipeline.py`          | Orchestrates full end-to-end workflow                                                     |
| `pipeline/embeddings.py`                 | Embedding model client (mock or real)                                                     |
| `pipeline/metrics_db.py`                 | Author metrics retrieval (mock or DB query)                                               |
| `pipeline/llm_client.py`                 | Handles LLM calls for justifications                                                      |
| `pipeline/es_client.py`                  | Elasticsearch search wrapper                                                             |
| `app/`                                  | Streamlit applications & export utilities                                                 |
| `app/streamlit_team_builder.py`          | Original interactive UI                                                                  |
| `app/streamlit_team_builder_extended.py` | Extended UI with existing team input, auto roles                                          |
| `app/export_utils.py`                    | Export team data as CSV / PDF                                                             |
| `utils/scoring.py`                       | Composite score calculation & reranking logic                                             |
| `utils/similarity.py`                    | Vector similarity & topic overlap calculations                                            |
| `utils/report_generator.py`              | JSON report, radar charts, and visual summaries                                           |
| `es_index/authors_index_mapping.json`    | ES index mapping for `authors_index`                                                      |
| `data/sample_authors.json`               | Sample author metadata for testing/mock                                                   |
| `tests/`                                | Unit & integration tests for each module                                                  |
| `requirements.txt`                      | Python dependencies (Streamlit, Pandas, NumPy, Elasticsearch, Matplotlib, etc.)           |


---

### 3️⃣ Example requirements.txt

```text
streamlit>=1.26
pandas>=2.0
numpy>=1.25
matplotlib>=3.8
elasticsearch>=8.12
openai>=1.0   # if using OpenAI API for LLM justification
fpdf>=1.7     # for PDF export
```

---

### 4️⃣ Example setup.sh

```bash
#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt


```

---

### 5️⃣ Recommended Workflow

1. Prepare ES index

```bash
  curl -X PUT "localhost:9200/authors_index" -H 'Content-Type: application/json' -d @es_index/authors_index_mapping.json 
```

2. Load author data (real or mock) into ES.
3. Run Streamlit UI

```bash
  streamlit run app/streamlit_team_builder_extended.py 
```

4. Generate top-20 researcher team with LLM justifications.
5. Export as CSV / PDF using the buttons in the app (implemented via export_utils.py).
6. Unit tests available under tests/ to validate modules.


---

### 6️⃣ Notes

- Modular structure allows easy replacement of mock clients with production services (OpenAI embeddings/LLM, real ES, PostgreSQL metrics DB).
- Separation of utils/, pipeline/, and app/ ensures maintainability.
- Extended app supports existing team input → missing skill detection and auto role assignment.
- Can be integrated into a CI/CD pipeline for automated proposal preparation.


I can also provide a ready-to-use skeleton with placeholder code for each module (embeddings.py, metrics_db.py, llm_client.py, es_client.py, export_utils.py) so that you can run the full system immediately with mock data.
Do you want me to generate that full skeleton next?

---


**ChatGPT**:

Perfect! Let’s design a complete skeleton project that includes:

- Pipeline modules with placeholder/mock implementations
- Streamlit UI
- Backend API (FastAPI) to serve mock data
- Export utilities (CSV / PDF)
- Full folder structure
This will allow end-to-end testing locally, even before integrating real Elasticsearch, metrics DB, or LLM.


---

### 1️⃣ Project Folder Structure (Extended with Backend API)

```css
ai_research_team_builder/
│
├── README.md
├── requirements.txt
├── setup.sh
│
├── data/
│   └── sample_authors.json
│
├── es_index/
│   └── authors_index_mapping.json
│
├── pipeline/
│   ├── __init__.py
│   ├── run_full_pipeline.py
│   ├── embeddings.py
│   ├── metrics_db.py
│   ├── llm_client.py
│   ├── es_client.py
│
├── app/
│   ├── __init__.py
│   ├── streamlit_team_builder.py
│   ├── streamlit_team_builder_extended.py
│   ├── export_utils.py
│
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── api_routes.py            # API endpoints for mock data
│   └── mock_data.py             # Mock author/team data
│
├── utils/
│   ├── __init__.py
│   ├── scoring.py
│   ├── similarity.py
│   ├── report_generator.py
│
└── tests/
    ├── test_pipeline.py
    ├── test_es_integration.py
    ├── test_streamlit_ui.py
    ├── test_backend_api.py

```


---

### 2️⃣ Example Modules with Mock Implementations


#### 2.1 pipeline/embeddings.py

```python
import numpy as np

class EmbeddingClient:
    def embed(self, texts):
        """Return mock 1536-d embeddings"""
        return [np.random.rand(1536).tolist() for _ in texts]

```

#### 2.2 pipeline/metrics_db.py

```python
import numpy as np

class MetricsDB:
    def fetch_author_metrics(self, author_ids):
        """Return mock metrics for authors"""
        return {aid: {"h_index": np.random.randint(20, 100),
                      "fnci": np.random.rand()*3,
                      "citations": np.random.randint(50,1000),
                      "recent_pubs_5yr": np.random.randint(5,30),
                      "intl_collab_ratio": np.random.rand()} 
                for aid in author_ids}

```


#### 2.3 pipeline/llm_client.py


```python
class ChatModel:
    def generate(self, prompt, max_tokens=512, temperature=0.3):
        """Return mock justification"""
        return "This researcher is selected for their expertise and impact in the field."
```


#### 2.4 pipeline/es_client.py

```python
class ESClient:
    def search_authors(self, project_vector, countries=None, fields=None, top_k=50):
        """Return mock authors"""
        authors = []
        for i in range(top_k):
            authors.append({
                "author_id": f"A{i+1}",
                "name": f"Researcher {i+1}",
                "affiliation": "MIT" if i%2==0 else "Stanford",
                "country": "USA",
                "research_fields": ["AI","ML"],
                "author_vector": project_vector,
                "h_index": 50 + i,
                "fnci": 1.5,
                "citations": 200+i,
                "recent_pubs_5yr": 10+i,
                "intl_collab_ratio": 0.3
            })
        return authors
```


#### 2.5 app/export_utils.py

```python
import pandas as pd
from fpdf import FPDF

def export_to_csv(candidates, file_path="team.csv"):
    df = pd.DataFrame(candidates)
    df.to_csv(file_path, index=False)
    return file_path

def export_to_pdf(candidates, file_path="team.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Recommended Research Team", ln=True, align='C')
    for c in candidates:
        text = f"{c['name']} | {c['affiliation']} | {c['field']} | Score: {c['score']}"
        pdf.multi_cell(0, 10, txt=text)
        pdf.ln(2)
    pdf.output(file_path)
    return file_path

```

#### 2.6 backend/mock_data.py

```python
def get_mock_authors(n=10):
    authors = []
    for i in range(n):
        authors.append({
            "author_id": f"A{i+1}",
            "name": f"Researcher {i+1}",
            "affiliation": "MIT" if i%2==0 else "Stanford",
            "country": "USA",
            "research_fields": ["AI","ML"],
            "h_index": 50+i,
            "fnci": 1.5,
            "citations": 200+i,
            "recent_pubs_5yr": 10+i,
            "intl_collab_ratio": 0.3
        })
    return authors

```

#### 2.7 backend/api_routes.py

```python
from fastapi import APIRouter
from .mock_data import get_mock_authors

router = APIRouter()

@router.get("/authors")
def get_authors(limit: int = 10):
    return get_mock_authors(n=limit)

```

#### 2.8 backend/main.py

```python
from fastapi import FastAPI
from .api_routes import router

app = FastAPI(title="AI Research Team Builder API")

app.include_router(router, prefix="/api")

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

```

---

### 3️⃣ How to Run
1. Setup virtual environment
```bash
bash setup.sh
```
2. Run Streamlit app
```bash
streamlit run app/streamlit_team_builder_extended.py
```
3. Run backend API
```bash
uvicorn backend.main:app --reload
```
4. Access mock API at:
```bash
GET http://127.0.0.1:8000/api/authors?limit=10
```
5. Generate top-20 recommended team in Streamlit app, export CSV/PDF.


---

### ✅ Features Implemented

- Full project structure for modular AI research team builder
- Pipeline with mock ES, embeddings, metrics, LLM
- Streamlit UI with extended team input, missing skill detection, auto roles
- Export functionality (CSV / PDF)
- Backend API returning mock author data for testing / integration
- Ready for real data integration with Elasticsearch, OpenAI API, and production metrics DB

If you want, I can also provide a ready-to-run run_full_pipeline.py fully integrated with this structure, so the Streamlit app + backend API + export all work together immediately with mock data.
Do you want me to do that next?


---


**ChatGPT**:

Perfect! Here’s a ready-to-run run_full_pipeline.py fully integrated with the project structure and mock services we created. This will allow your Streamlit app, backend API, and export utilities to work together immediately with mock data.

### pipeline/run_full_pipeline.py

```python
import numpy as np
from .embeddings import EmbeddingClient
from .metrics_db import MetricsDB
from .llm_client import ChatModel
from .es_client import ESClient
from ..utils.scoring import composite_score, rerank_and_deduplicate
from ..utils.similarity import compute_topic_similarity
from ..utils.report_generator import explainable_report

# -----------------------------
# 1) Full Pipeline
# -----------------------------
def run_pipeline(project_summary, existing_team=None, top_k=20):
    """
    End-to-end pipeline:
    - Embed project
    - Retrieve candidates (mock ES)
    - Compute similarity
    - Compute composite scores & rerank
    - LLM justification
    - Generate final JSON report
    """
    embedder = EmbeddingClient()
    es_client = ESClient()
    metrics_db = MetricsDB()
    llm = ChatModel()

    existing_team = existing_team or []

    # 1) Embed project
    project_vector = embedder.embed([project_summary])[0]

    # 2) Retrieve candidates
    candidates = es_client.search_authors(project_vector, top_k=top_k*2)

    # 3) Compute topic similarity
    candidates = compute_topic_similarity(project_vector, candidates)

    # 4) Compute composite score & rerank
    for c in candidates:
        # Merge mock metrics if needed
        metrics = metrics_db.fetch_author_metrics([c["author_id"]])[c["author_id"]]
        c.update(metrics)
    ranked_candidates = rerank_and_deduplicate(candidates, max_candidates=top_k)

    # 5) LLM Justification (top 10)
    justified = []
    for c in ranked_candidates[:10]:
        prompt = f"""
Project Summary: {project_summary}
Researcher profile: {c}
Explain why this researcher is selected (2-3 sentences).
"""
        c_out = dict(c)
        c_out["justification"] = llm.generate(prompt)
        # Simple auto role assignment
        if c["composite_score"]>0.8 and c["topic_similarity"]>0.7:
            c_out["auto_role"] = "PI"
        elif c["topic_similarity"]>0.6:
            c_out["auto_role"] = "Co-PI"
        else:
            c_out["auto_role"] = "Collaborator"
        justified.append(c_out)

    # 6) Fill remaining candidates without justification
    for c in ranked_candidates[10:]:
        c["justification"] = ""
        c["auto_role"] = "Collaborator"
        justified.append(c)

    # 7) Generate final JSON report
    report = explainable_report(justified, project_summary, existing_team=existing_team)
    return report

```

---

### pipeline/utils/report_generator.py

```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def explainable_report(justified_candidates, project_summary, existing_team=None):
    """
    Generate structured report with:
    - Team summary
    - Key strengths / gaps
    - Ranked candidates with justification and auto roles
    """
    existing_fields = set([m["field"].lower() for m in existing_team or []])
    top_fields = set()
    for c in justified_candidates:
        for f in c["field"].split(","):
            top_fields.add(f.strip().lower())
    missing_fields = top_fields - existing_fields

    report = {
        "team_summary": f"Top experts selected for the project: {project_summary[:80]}...",
        "key_strengths": ["High impact", "Cross-domain expertise", "Strong collaborations"],
        "potential_gaps": list(missing_fields),
        "ranked_candidates": [{
            "name": c["name"],
            "affiliation": c["affiliation"],
            "field": ", ".join(c["research_fields"]) if "research_fields" in c else c.get("field",""),
            "score": round(c.get("composite_score",0),3),
            "justification": c.get("justification",""),
            "suggested_role": c.get("auto_role","Collaborator"),
            "tags": ["Top Impact", "Domain Expert"]
        } for c in justified_candidates]
    }
    return report

```

---

### pipeline/utils/scoring.py

```python
import numpy as np

def composite_score(c):
    """Compute composite score using topic_similarity, impact, activity, collaboration"""
    impact = min(1.0, (np.log1p(c.get("citations",0))/10.0) + (c.get("fnci",0)/3.0))
    activity = min(1.0, np.log1p(c.get("recent_pubs_5yr",0))/3.0)
    collaboration = min(1.0, c.get("intl_collab_ratio",0))
    score = 0.3*c.get("topic_similarity",0) + 0.3*impact + 0.2*collaboration + 0.2*activity
    return score

def rerank_and_deduplicate(candidates, max_candidates=20):
    """Rerank candidates by composite_score and remove duplicates"""
    for c in candidates:
        c["composite_score"] = composite_score(c)
    ranked = sorted(candidates, key=lambda x: x["composite_score"], reverse=True)
    seen = set()
    filtered = []
    for r in ranked:
        key = (r["name"].lower(), r["affiliation"].lower())
        if key in seen:
            continue
        seen.add(key)
        filtered.append(r)
        if len(filtered) >= max_candidates:
            break
    return filtered

```

### pipeline/utils/similarity.py

```python
import numpy as np

def compute_topic_similarity(project_vector, candidates):
    p = np.array(project_vector)
    p_norm = p / (np.linalg.norm(p)+1e-9)
    for c in candidates:
        a = np.array(c.get("author_vector", np.zeros_like(p)))
        a_norm = a / (np.linalg.norm(a)+1e-9)
        sim = float(np.dot(p_norm, a_norm))
        c["topic_similarity"] = sim
    return candidates

```

---

### ✅ Key Notes

1. Streamlit apps (streamlit_team_builder_extended.py) call run_pipeline() directly.
2. Backend API can call run_pipeline() to return JSON recommendations.
3. All modules work with mock data, ready for replacing with real ES, metrics DB, embeddings, and LLM.
4. Export CSV / PDF via app/export_utils.py integrates with pipeline outputs.


You now have a fully integrated skeleton:
- Streamlit UI with existing team, missing skills, auto role assignment
- End-to-end pipeline (run_full_pipeline.py)
- Utilities for scoring, similarity, report generation
- Backend API serving mock data
- Export functionality ready

I can next provide a working FastAPI endpoint that calls run_pipeline() and returns the top-20 team as JSON, fully integrated with this skeleton.
Do you want me to do that next?



---


**ChatGPT**:

Perfect! Let’s add a FastAPI endpoint that calls run_pipeline() and returns the top-20 recommended research team as JSON. This will integrate fully with the skeleton we’ve built.

### backend/api_routes.py (Updated)

```python
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from ..pipeline.run_full_pipeline import run_pipeline

router = APIRouter()

# -----------------------------
# Request / Response Models
# -----------------------------
class TeamRequest(BaseModel):
    project_summary: str
    keywords: Optional[List[str]] = []
    target_regions: Optional[List[str]] = []
    target_institutions: Optional[List[str]] = []
    existing_team: Optional[List[dict]] = []  # [{"name":..,"affiliation":..,"field":..},...]

class Candidate(BaseModel):
    name: str
    affiliation: str
    field: str
    score: float
    suggested_role: str
    justification: str
    tags: Optional[List[str]] = []

class TeamResponse(BaseModel):
    team_summary: str
    key_strengths: List[str]
    potential_gaps: List[str]
    ranked_candidates: List[Candidate]

# -----------------------------
# Endpoint
# -----------------------------
@router.post("/recommend_team", response_model=TeamResponse)
def recommend_team(request: TeamRequest):
    if not request.project_summary.strip():
        raise HTTPException(status_code=400, detail="Project summary cannot be empty.")
    
    # Run the full pipeline
    report = run_pipeline(
        project_summary=request.project_summary,
        existing_team=request.existing_team,
        top_k=20
    )

    return report

# Optional: simple GET endpoint returning mock authors
@router.get("/authors")
def get_authors(limit: int = 10):
    from .mock_data import get_mock_authors
    return get_mock_authors(n=limit)

```

---

### backend/main.py (Updated)

```python
from fastapi import FastAPI
from .api_routes import router

app = FastAPI(title="AI Research Team Builder API")

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

```

---

### Usage Examples

1) Start the API
```bash
uvicorn backend.main:app --reload
```
2) POST request to get recommended team
```bash
POST http://127.0.0.1:8000/api/recommend_team
Content-Type: application/json

{
    "project_summary": "Developing AI methods for multi-modal biomedical research",
    "keywords": ["AI","biomedicine"],
    "target_regions": ["USA","Europe"],
    "target_institutions": ["MIT","Stanford"],
    "existing_team": [
        {"name":"Alice Smith","affiliation":"MIT","field":"AI"}
    ]
}

```

**Response**:
```json
{
    "team_summary": "Top experts selected for the project: Developing AI methods for multi-modal biomedic...",
    "key_strengths": ["High impact", "Cross-domain expertise", "Strong collaborations"],
    "potential_gaps": ["ML", "Bioinformatics"],
    "ranked_candidates": [
        {
            "name": "Researcher 1",
            "affiliation": "MIT",
            "field": "AI,ML",
            "score": 0.85,
            "suggested_role": "PI",
            "justification": "This researcher is selected for their expertise and impact in the field.",
            "tags": ["Top Impact","Domain Expert"]
        },
        ...
    ]
}

```

---

### ✅ Key Features of This Endpoint
1. POST /api/recommend_team: Accepts project summary, keywords, regions, institutions, and existing team.
2. Returns top-20 recommended researchers with:
    - Score
    - Auto role assignment (PI / Co-PI / Collaborator)
    - LLM-generated justification
    - Tags
3. Fully mock-data ready, can replace pipeline with real ES + LLM easily.
4. Includes GET /api/authors for testing / frontend integration.
5. Can be called directly from the Streamlit app, other dashboards, or external systems.

Next, we can integrate this API with the Streamlit app, so when the user clicks “Generate Team Recommendations”, it calls the backend instead of running the pipeline locally, keeping UI and backend fully decoupled.
Do you want me to do that next?


---


**ChatGPT**:

Excellent 👌 — now let’s connect your Streamlit UI to the backend FastAPI service we just created. This will make the frontend clean and scalable — the app calls the API instead of running heavy logic locally.

### ✅ Goal

When the user fills in:
- Project Summary
- Keywords / Target Region / Institutions
- Existing Team

and clicks “Generate Team Recommendations”,
- the Streamlit app will send a POST request to http://localhost:8000/api/recommend_team,
- then visualize the ranked researchers with justifications, scores, and auto roles.

---

### 📁 app/streamlit_team_builder_extended.py

```python
import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000/api/recommend_team"

st.set_page_config(page_title="AI Research Team Builder", layout="wide")

st.title("🧠 AI Research Team Builder")
st.write("Build an optimal interdisciplinary research team using metrics + AI reasoning.")

# -----------------------
# User Inputs
# -----------------------
with st.form("team_form"):
    st.subheader("🔍 Project & Requirements")

    project_summary = st.text_area(
        "Project Summary",
        placeholder="Describe your project (e.g., 'AI for sustainable materials design')",
        height=150,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        keywords = st.text_input("Keywords (comma-separated)", "AI, Materials, Sustainability")
    with col2:
        regions = st.text_input("Target Regions", "USA, Europe")
    with col3:
        institutions = st.text_input("Preferred Institutions", "MIT, Stanford, ETH Zurich")

    st.subheader("👥 Existing Team (optional)")
    existing_team_data = st.text_area(
        "List existing members (name, affiliation, field)...",
        "Alice Smith, MIT, AI\nJohn Wang, Stanford, Physics"
    )

    submitted = st.form_submit_button("🚀 Generate Team Recommendations")

# -----------------------
# Submit Request to API
# -----------------------
if submitted:
    if not project_summary.strip():
        st.warning("Please enter a project summary.")
    else:
        st.info("Generating recommendations... please wait ⏳")

        existing_team = []
        for line in existing_team_data.split("\n"):
            parts = [p.strip() for p in line.split(",") if p.strip()]
            if len(parts) >= 3:
                existing_team.append({"name": parts[0], "affiliation": parts[1], "field": parts[2]})

        payload = {
            "project_summary": project_summary,
            "keywords": [k.strip() for k in keywords.split(",") if k.strip()],
            "target_regions": [r.strip() for r in regions.split(",") if r.strip()],
            "target_institutions": [i.strip() for i in institutions.split(",") if i.strip()],
            "existing_team": existing_team,
        }

        try:
            res = requests.post(API_URL, json=payload, timeout=120)
            if res.status_code != 200:
                st.error(f"API error: {res.text}")
            else:
                result = res.json()

                st.subheader("📊 Team Summary")
                st.write(result["team_summary"])
                st.markdown(f"**Key Strengths:*- {', '.join(result['key_strengths'])}")
                st.markdown(f"**Potential Gaps:*- {', '.join(result['potential_gaps']) or 'None detected'}")

                df = pd.DataFrame(result["ranked_candidates"])
                st.subheader("🏆 Top 20 Recommended Researchers")
                st.dataframe(df[["name","affiliation","field","score","suggested_role","justification"]])

                with st.expander("📈 Detailed Candidate Insights"):
                    for c in result["ranked_candidates"]:
                        st.markdown(f"**{c['name']}*- — *{c['affiliation']}*")
                        st.markdown(f"Role: **{c['suggested_role']}**, Score: **{round(c['score'],3)}**")
                        st.markdown(f"_Field_: {c['field']}")
                        st.markdown(f"💡 **Why chosen:*- {c['justification'] or 'No justification available.'}")
                        st.markdown("---")

        except Exception as e:
            st.error(f"Connection error: {e}")
```

---

### ✅ How It Works

1. User fills form → Project summary + filters
2. Streamlit POSTs the JSON to backend FastAPI /api/recommend_team
3. API runs run_pipeline()
4. Returns a structured report JSON
5. Streamlit visualizes:
    - Summary + key strengths/gaps
    - Table of top-20 researchers
    - Expandable detailed justifications

---

### 💻 Run Instructions

```bash
1️⃣ Start FastAPI backend
```bash
uvicorn backend.main:app --reload
```
2️⃣ Start Streamlit UI
```bash
streamlit run app/streamlit_team_builder_extended.py
```
3️⃣ Open in browser
```bash
👉 http://localhost:8501
```

---

### ✅ Features of This Integration
| Feature         | Description                                                      |
|-----------------|------------------------------------------------------------------|
| 🔄 API Integration | Streamlit frontend is fully decoupled from backend logic via REST API |
| 🧠 AI Reasoning     | LLM-based justifications are displayed inline for each candidate      |
| ⚙️ Modular         | Compatible with both mock pipeline and real Elasticsearch/LLM data    |
| 📊 Visualization   | Presents a top-20 researcher table with expandable explanations       |
| 🧩 Extendable      | Easily supports filtering, export, and advanced role clustering in UI |


Would you like me to extend this UI further — for example to:
1. Add filtering and sorting (by role, field, or score)
2. Add “Export as CSV/PDF” button integrated with export_utils.py





