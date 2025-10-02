## ✅ Feature Overview: Policy & Patent Impact Detector

Here's a realistic and detailed implementation plan for the “Policy & Patent Impact Detector” feature, including backend support code, inputs/outputs, and LLM prompts.


### Goal:

Detect whether a research paper has had a real-world impact by being cited in:

* Government policy documents
* Patents
* Industry whitepapers
* News or technical reports


### 🧩 Architecture Overview

```plaintext
CopyEdit
[Input: Paper (title + abstract or DOI)]
        ↓
[Data sources: Policy docs, Patents, etc. via APIs or index]
        ↓
[Matching Module: Exact + Semantic Matching (embedding/LLM)]
        ↓
[LLM Scorer/Explainer: Why this counts as real-world impact?]
        ↓
[Output: Structured Report]
```


### 🧪 Input / Output Example

Input:
```json
CopyEdit
{
  "title": "A Transformer-based Approach for Quantum Chemistry",
  "abstract": "We propose a transformer architecture that replaces density functional theory in molecular property prediction."
}
```

Output:
```json
CopyEdit
{
  "impact_detected": true,
  "sources": [
    {
      "type": "patent",
      "title": "System and method for neural network-based quantum simulations",
      "url": "https://patents.google.com/patent/US2024032193A1"
    },
    {
      "type": "policy",
      "title": "US DOE Strategic Plan on AI in Science",
      "url": "https://energy.gov/ai-plan"
    }
  ],
  "llm_explanation": "The paper has been referenced in a patent filed by XYZ Corp and a U.S. Department of Energy strategic document. This indicates its influence in both commercial innovation and government policy."
}
```


### 🛠️ Backend Code (Python Module)

#### Step 1: Embedding-based Semantic Matching

```python
CopyEdit
from sentence_transformers import SentenceTransformer, util
import requests

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed(text):
    return model.encode(text, convert_to_tensor=True)

def match_sources(paper_text, candidate_sources, threshold=0.75):
    paper_vec = embed(paper_text)
    matches = []

    for source in candidate_sources:
        score = util.cos_sim(paper_vec, embed(source["text"])).item()
        if score > threshold:
            source["score"] = score
            matches.append(source)

    return sorted(matches, key=lambda x: -x["score"])
```


#### Step 2: Example Data Source Loader


In production, this should be connected to:
* PatentsView API
* Google Patents
* Overton.io (policy citations)
* CORE
* CORDIS
* Crossref Event Data

```python
CopyEdit
# Dummy local sample data (mock)
candidate_sources = [
    {
        "type": "patent",
        "title": "System and method for neural network-based quantum simulations",
        "text": "A transformer model replacing DFT in molecular property prediction...",
        "url": "https://patents.google.com/patent/US2024032193A1"
    },
    {
        "type": "policy",
        "title": "US DOE Strategic Plan on AI in Science",
        "text": "Recent advances in transformer models for chemistry have motivated further R&D...",
        "url": "https://energy.gov/ai-plan"
    }
]
```

#### Step 3: Full Pipeline

```python
CopyEdit
def detect_policy_patent_impact(title, abstract, sources=candidate_sources):
    paper_text = f"{title}\n\n{abstract}"
    matched = match_sources(paper_text, sources)

    result = {
        "impact_detected": len(matched) > 0,
        "sources": matched,
    }

    return result
```


### 🤖 Optional: LLM Prompt (for Explanation)

If you'd like the system to generate a reason why these matches count as practical impact:

🧠 Prompt Template

```python
CopyEdit
from openai import OpenAI

def explain_impact_with_llm(title, abstract, matches):
    context = "\n".join([f"{m['type'].title()}: {m['title']} - {m['url']}" for m in matches])
    
    prompt = f"""
You are an expert in science communication and impact analysis.
Given the paper:

Title: {title}

Abstract: {abstract}

And the following matched real-world citations:
{context}

Explain in 2-3 sentences how these matches indicate real-world impact (e.g., cited in patent or government policy).
"""

    response = OpenAI().chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    return response.choices[0].message.content.strip()
```

### ✅ Final Output Generator

```python
CopyEdit
def detect_with_llm_explanation(title, abstract):
    raw_result = det

ect_policy_patent_impact(title, abstract)
    if raw_result["impact_detected"]:
        raw_result["llm_explanation"] = explain_impact_with_llm(
            title, abstract, raw_result["sources"]
        )
    return raw_result
```


### 🧪 Example Test Run

```python
CopyEdit
if __name__ == "__main__":
    title = "A Transformer-based Approach for Quantum Chemistry"
    abstract = "We propose a transformer architecture that replaces density functional theory in molecular property prediction."
    
    result = detect_with_llm_explanation(title, abstract)
    from pprint import pprint
    pprint(result)
```


### ✅ Optional: Streamlit Viewer (Card View)

```python
CopyEdit
import streamlit as st

st.title("Policy & Patent Impact Detector")

title = st.text_input("Paper Title")
abstract = st.text_area("Paper Abstract")

if st.button("Analyze Impact"):
    result = detect_with_llm_explanation(title, abstract)
    if result["impact_detected"]:
        st.success("Real-world impact detected!")
        for src in result["sources"]:
            st.markdown(f"**{src['type'].title()}**: [{src['title']}]({src['url']}) (Score: {src['score']:.2f})")
        st.markdown("**Explanation:**")
        st.info(result["llm_explanation"])
    else:
        st.warning("No real-world impact found in known policy or patent sources.")
```


###Let me know if you want:

* 🔍 API integration with PatentsView or Overton
* 📊 Citation graph overlay
* 🧾 Output as JSON or exportable report
* 
Would you like this packaged into a microservice or integrated with your other research tools?
