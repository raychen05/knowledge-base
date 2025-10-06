## Categorized Critical Information from Title & Abstract


As an academic researcher or expert, when scanning titles and abstracts (summaries) of papers, you’re looking for specific critical information to judge relevance, quality, novelty, and utility. Below is a structured list of the major, categorized information that can be extracted from just the title and abstract.

---

### 🧠 Categorized Critical Information from Title & Abstract

---

#### 🔹 I. Research Context & Problem


Field | What to Extract
--- | ---
Research area | Which academic field or subfield does the paper belong to?
Motivation | Why is this research significant? What gap or challenge does it address?
Research question | What specific question or problem is the study investigating?
Application domain | What is the practical or applied area (e.g., healthcare, chemistry, NLP, robotics, social science)?


#### 🔹 II. Methodology & Approach


Field | What to Extract
--- | ---
Technique used | What algorithm, model, or method is applied? (e.g., GNN, LSTM, CRISPR)
Model architecture | Is there a specific or novel architecture mentioned? (e.g., Transformer, encoder-decoder)
Framework or tool | Which frameworks or tools are used? (e.g., PyTorch, TensorFlow, AutoML, R Shiny)
Experimental design | How are the experiments structured or evaluated?



---

#### 🔹 III. Novelty & Contribution


Field | What to Extract
--- | ---
Key contribution | What is new or unique in this work? (e.g., novel method, dataset, framework, metric)
First-of-its-kind? | Does the paper claim to be the first to achieve or propose something specific?
Improvement over prior | What improvements are reported compared to previous methods or baselines?
Comparison to past work | Are there direct comparisons or benchmarks against existing approaches?


#### IV. Data & Resources


Field | What to Extract
--- | ---
Dataset used | Which dataset(s) are utilized? Are they public or private? What are their names?
Data source | Where does the data originate? (e.g., clinical trial, open repository, proprietary collection)
Dataset availability | Is the dataset newly introduced? Is it publicly released or accessible?
Input data types | What types of data are used? (e.g., images, graphs, text, molecules, sensor data)


#### V. Results & Outcomes

Field | What to Extract
--- | ---
Performance metrics | What metrics are reported? (e.g., Accuracy, AUC, F1-score, BLEU, RMSE)
Quantitative gains | Are specific improvements or percentage gains mentioned? (e.g., "+4% over baseline")
Success claim | Does the paper claim superior or state-of-the-art results? (e.g., "We outperform...", "state-of-the-art", "significantly better")
Limitations | Are any limitations, failures, or areas needing further testing briefly mentioned?


#### VI. Research Type & Scope


Field | What to Extract
--- | ---
Paper type | Is the paper a survey, experimental study, theoretical work, applied research, or benchmark?
Research scope | Does the study take a broad overview or focus narrowly? Is it a deep dive or exploratory analysis?
Study scale | Is the research based on a small-scale experiment, a large dataset, or a real-world trial?
Reproducibility info | Does the abstract mention released code or data, or any information about reproducibility?



#### VII. Entity Mentions & Metadata

Field | What to Extract
--- | ---
Authors | Names of authors or institutions if mentioned in the abstract
Location/Region | Specific country, laboratory, or region referenced
Citations to Prior Work | Mentions of previous models, methods, or foundational work (e.g., "based on BERT", "following Smith et al.")
Year/Recency Clues | Phrases indicating time frame or novelty (e.g., "in recent years", "emerging", "newly proposed")


---


### 🧠 How LLM Can Extract This from Abstract

Example Prompt Instruction for Extraction:

Given the title and abstract, extract the following structured information:
1. Field or domain of research
2. Main problem or question addressed
3. Technique/method used
4. Novel contribution or uniqueness
5. Datasets used or introduced
6. Results or performance summary
7. Type of paper (survey, empirical, theoretical, applied)
8. Limitations or future work

Return as structured JSON.

Example Extracted Output from Abstract
```json
{
  "field": "Drug Discovery with Graph Neural Networks",
  "problem": "Predicting molecular properties using deep learning",
  "method": "Message-passing Graph Neural Network (MPNN)",
  "novelty": "Combines 2D and 3D molecular features into a unified GNN",
  "dataset": ["QM9", "Tox21"],
  "results": "Achieved +4% ROC-AUC improvement over baseline GCN",
  "type": "Empirical benchmark paper",
  "limitations": "Does not address scalability to very large molecular graphs"
}

```


Summary: Why This Matters

By extracting these fields, your AI assistant enables:

-	Fast filtering of irrelevant papers
-	Clustering by method, dataset, or novelty
-	Summarization across 100s of papers
-	Smart highlighting for researcher decision-making



---


## A Full Solution


Here’s a full solution: prompt templates + Python functions that use GPT (e.g., via OpenAI API) to extract structured academic paper metadata from title and abstract.


---

### 🧠 Goal

From just the title + abstract, extract key structured fields:
-	Field/domain
-	Problem statement
-	Method
-	Contribution
-	Dataset
-	Results
-	Paper type
-	Limitations

---

### 🧾 Prompt Template (Few-Shot Ready)


```python
BASE_EXTRACTION_PROMPT = """
You are an AI assistant helping academic researchers quickly understand academic papers.

Given the paper's title and abstract, extract the following structured fields:

1. **Field/domain**: What area of research is this? (e.g., NLP, genomics, education)
2. **Problem**: What problem or research question is addressed?
3. **Method/Approach**: What technique, model, or algorithm is used?
4. **Key Contribution**: What is new or different about this work?
5. **Datasets**: What datasets are used or introduced?
6. **Results**: What are the key performance outcomes or improvements?
7. **Paper Type**: Is it a survey, empirical study, theoretical, benchmark, etc.?
8. **Limitations**: Are any limitations or future directions mentioned?

### Format your response as JSON with field names.
### Keep answers concise (1–2 sentences each).

---

Title: {title}

Abstract: {abstract}

Extracted information:
"""
```


### Python Function Using OpenAI API (GPT-4 / GPT-4o)


```python
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_academic_metadata(title: str, abstract: str, model="gpt-4o") -> dict:
    prompt = BASE_EXTRACTION_PROMPT.format(title=title.strip(), abstract=abstract.strip())
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful academic assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    # Try parsing output
    import json
    try:
        content = response['choices'][0]['message']['content']
        extracted = json.loads(content)
        return extracted
    except Exception as e:
        print("Error parsing response:", e)
        return {"error": "Failed to parse GPT output", "raw": content}

```

Sample Input


```python

title = "Graph Neural Networks for Molecular Property Prediction"
abstract = """
We propose a message-passing neural network (MPNN) architecture for predicting molecular properties based on graph representations of molecules. 
Unlike previous approaches, our model integrates both 2D bond connectivity and 3D geometric features. We evaluate our method on the QM9 and Tox21 datasets, achieving state-of-the-art performance in molecular classification tasks.
"""

extracted = extract_academic_metadata(title, abstract)
print(extracted)
```


Sample Output

```json
{
  "Field/domain": "Computational Chemistry / Machine Learning",
  "Problem": "Predicting molecular properties using deep learning on molecular graphs",
  "Method/Approach": "Message-passing neural network (MPNN) with 2D and 3D features",
  "Key Contribution": "Combining 2D connectivity and 3D geometry in a single GNN architecture",
  "Datasets": ["QM9", "Tox21"],
  "Results": "Achieved state-of-the-art performance on molecular classification tasks",
  "Paper Type": "Empirical study",
  "Limitations": "No mention of generalizability to larger molecular datasets"
}
```


### 🧠 Optional Enhancements

-	Add few-shot examples to improve output consistency.
-	Add function calling to enforce JSON schema with OpenAI tools.
-	Extend fields (e.g., citation count, funding source, author institution) if full metadata is available.


### Streamlit UI – Upload paper list and extract summaries

📦 File Format

Expect a CSV with columns: title, abstract

```python
import streamlit as st
import pandas as pd
from academic_extractor import extract_academic_metadata  # from LangChain or OpenAI version

st.title("📚 Academic Paper Metadata Extractor")

uploaded_file = st.file_uploader("Upload CSV with 'title' and 'abstract' columns", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if "title" in df.columns and "abstract" in df.columns:
        st.success("File uploaded and validated.")
        
        if st.button("🚀 Extract Metadata"):
            results = []
            with st.spinner("Extracting info from papers..."):
                for idx, row in df.iterrows():
                    try:
                        metadata = extract_academic_metadata(row['title'], row['abstract'])
                        results.append(metadata)
                    except Exception as e:
                        results.append({"error": str(e)})
            
            results_df = pd.DataFrame(results)
            st.subheader("📄 Extracted Summaries")
            st.dataframe(results_df)

            st.download_button("Download Results as CSV", results_df.to_csv(index=False), "metadata_results.csv")
    else:
        st.error("CSV must contain 'title' and 'abstract' columns.")
```


### academic_extractor.py

```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage
import os
import json

with open("prompts/extract_prompt.txt") as f:
    prompt_template = f.read()

llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

def extract_academic_metadata(title, abstract):
    prompt = prompt_template.format(title=title.strip(), abstract=abstract.strip())
    response = llm([SystemMessage(content="You are a helpful academic assistant."),
                    HumanMessage(content=prompt)])
    content = response.content

    try:
        return json.loads(content)
    except:
        return {"error": "Failed to parse GPT output", "raw": content}
```


### prompts/extract_prompt.txt


```plaintext
You are an AI assistant helping academic researchers understand academic papers.

Extract the following fields:
1. Field/domain
2. Problem
3. Method
4. Contribution
5. Datasets
6. Results
7. Paper Type
8. Limitations

Use the following format:

json
{
  "Field/domain": "...",
  "Problem": "...",
  "Method/Approach": "...",
  "Key Contribution": "...",
  "Datasets": [...],
  "Results": "...",
  "Paper Type": "...",
  "Limitations": "..."
}
```



### Optional Features to Add

-	🔍 Semantic clustering (via sentence-transformers or OpenAI embeddings)
-	🧠 Save summaries to vector DB
-	🗂️ Group by methods, dataset, topic, or novelty
-	🧪 Add novelty score or citation-based analysis