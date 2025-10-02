## 🧠 Feature: Novelty vs Impact Analyzer


### Goal: Classify and explain whether a paper is:

* 🧪 Novel but Low-Cited
* 🏆 Incremental but Highly-Cited
* ✅ Both Novel and High Impact
* ⚠️ Neither Novel nor High Impact



### ✅ Use Case

Helps researchers, reviewers, and funders understand:

* Why a paper is undercited despite originality
* Which papers may be overvalued due to incremental work on hot topics
* Whether to support follow-up work based on true innovation



### 🔍 Inputs (Required and Optional)

```json
CopyEdit
{
  "title": "Large Language Models for Predicting Catalyst Reaction Pathways",
  "abstract": "This work applies transformer-based models to simulate catalytic reaction pathways with high accuracy. The approach replaces traditional DFT calculations with learned models.",
  "keywords": ["catalysis", "transformer", "reaction prediction", "DFT replacement", "chemical AI"],
  "citation_count": 12,
  "publication_year": 2022,
  "field_baseline_citations": 48,
  "similarity_to_existing_work": 0.23,   // (0 = highly novel, 1 = very similar)
  "paper_length_tokens": 4321,
  "num_references": 75,
  "num_figures": 12
}
```


### 🎯 Output

```json
CopyEdit
{
  "classification": "Novel but Low-Cited",
  "score_breakdown": {
    "novelty_score": 0.84,
    "impact_score": 0.25
  },
  "explanation": "The paper introduces a new idea (transformers replacing DFT) in a domain where this is uncommon. Despite low citations (12 vs 48 field average), its high novelty score indicates originality. Time-lag may be a factor in citation delay."
}
```    




### 🔧 Backend Logic Breakdown

🧮 Step 1: Compute Novelty and Impact Scores (Heuristic or ML)

```python
CopyEdit
def compute_scores(input: dict) -> dict:
    # Simple novelty score: inverse of similarity to known work
    novelty_score = 1 - input.get("similarity_to_existing_work", 1.0)

    # Impact score: normalized by field citation baseline
    impact_score = input["citation_count"] / max(input["field_baseline_citations"], 1)

    return {
        "novelty_score": round(novelty_score, 2),
        "impact_score": round(impact_score, 2)
    }
```


🧠 Step 2: Classify and Explain with LLM

LLM Prompt Template:
```txt
CopyEdit
You are a research metrics expert. A paper has been analyzed for novelty and impact using citation data and similarity scores.

Given the following metadata:
- Title: {title}
- Abstract: {abstract}
- Citation Count: {citation_count}
- Average Citation in Field: {field_baseline_citations}
- Novelty Score (0-1): {novelty_score}
- Impact Score (0-1): {impact_score}

Classify the paper into one of:
1. "Novel but Low-Cited"
2. "Incremental but Highly-Cited"
3. "Both Novel and High Impact"
4. "Neither Novel nor High Impact"

Then explain the reasoning briefly.

Respond in JSON format:
{
  "classification": "...",
  "score_breakdown": {
    "novelty_score": ...,
    "impact_score": ...
  },
  "explanation": "..."
}
```


### 🧑‍💻 Python Backend (Full Example Using OpenAI)

```python
CopyEdit
import openai
import json
from typing import Dict

def compute_scores(input: dict) -> Dict:
    novelty_score = 1 - input.get("similarity_to_existing_work", 1.0)
    impact_score = input["citation_count"] / max(input["field_baseline_citations"], 1)

    return {
        "novelty_score": round(novelty_score, 2),
        "impact_score": round(impact_score, 2)
    }

def classify_novelty_impact(input: dict) -> dict:
    scores = compute_scores(input)

    prompt = f"""
You are a research metrics expert. A paper has been analyzed for novelty and impact using citation data and similarity scores.

Given the following metadata:
- Title: {input["title"]}
- Abstract: {input["abstract"]}
- Citation Count: {input["citation_count"]}
- Average Citation in Field: {input["field_baseline_citations"]}
- Novelty Score (0-1): {scores['novelty_score']}
- Impact Score (0-1): {scores['impact_score']}

Classify the paper into one of:
1. "Novel but Low-Cited"
2. "Incremental but Highly-Cited"
3. "Both Novel and High Impact"
4. "Neither Novel nor High Impact"

Then explain the reasoning briefly.

Respond in JSON format:
{{
  "classification": "...",
  "score_breakdown": {{
    "novelty_score": {scores['novelty_score']},
    "impact_score": {scores['impact_score']}
  }},
  "explanation": "..."
}}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return json.loads(response.choices[0].message["content"])

# Sample input
if __name__ == "__main__":
    paper_input = {
        "title": "Large Language Models for Predicting Catalyst Reaction Pathways",
        "abstract": "This work applies transformer-based models to simulate catalytic reaction pathways...",
        "keywords": ["catalysis", "transformer", "reaction prediction", "DFT replacement", "chemical AI"],
        "citation_count": 12,
        "publication_year": 2022,
        "field_baseline_citations": 48,
        "similarity_to_existing_work": 0.23,
        "paper_length_tokens": 4321,
        "num_references": 75,
        "num_figures": 12
    }

    result = classify_novelty_impact(paper_input)
    print(json.dumps(result, indent=2))
```


### 💡 Extension Ideas

Advanced:

* Use SciBERT or embedding similarity to calculate similarity to prior works.
* Integrate Web of Science, Scopus, or Semantic Scholar API for:
    * field-level citation benchmarks
    * novelty via concept co-occurrence rarity
    * time-normalized citation velocity

Scoring Ideas:

* Novelty:
    * (1 - cosine_similarity(embedding, nearest_neighbor))
    * TF-IDF rarity of keywords/concepts
* Impact:
    * (citations / expected citations)
    * citations per year
    * Altmetric / policy impact / downstream usage


### Want More?

I can provide:
* 📊 A Streamlit UI to paste a paper and see novelty/impact map
* 📈 Plot of papers on a 2D plane (Novelty vs Impact)
* 🔁 LangChain agent to handle multi-paper analysis in batch
