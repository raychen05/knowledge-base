

## Templates for academic entity extraction and user intent detection


Here are templates for academic entity extraction and user intent detection, tailored to support intelligent assistants or research analysis systems that use data from Web of Science, InCites, and Web of Science Research Intelligence.


---

📄 Template 1: User Intent Detection (Structured Prompt for LLM)

🔍 Purpose

To extract key components from a user’s academic research query such as intent, subject, entities, metrics, and time range.

✅ Prompt Template

```text
You are an expert in academic research analysis. Given a user question, extract structured information in JSON format.

Extract the following fields:
- "intent_type": one of [trend, compare, list, summary, impact, collaboration, funding, productivity, performance]
- "subject": the main research topic(s) or scientific field(s)
- "metric": research-related metric(s) such as publication count, citations, funding amount, H-index, collaboration rate
- "entity_type": one of [author, institution, funder, country, journal, region]
- "entity_name": list of specific names mentioned (e.g. "MIT", "Wellcome Trust", "China", "Nature")
- "time_range": time range mentioned, formatted as {"start_year": ..., "end_year": ...} or {"relative": "last 5 years"}
- "output_format": what the user is asking for (e.g., summary, table, chart, map, top list)

Query: "{user_query}"

Return the result in this format:
{
  "intent_type": "...",
  "subject": "...",
  "metric": "...",
  "entity_type": "...",
  "entity_name": [...],
  "time_range": {...},
  "output_format": "..."
}
```

🧪 Example Input

```text
Show the top institutions in AI research in the last 5 years in the US.
```

🧾 Example Output


```json
{
  "intent_type": "list",
  "subject": "artificial intelligence",
  "metric": "publication count",
  "entity_type": "institution",
  "entity_name": ["United States"],
  "time_range": {
    "relative": "last 5 years"
  },
  "output_format": "top list"
}

```

---

📄 Template 2: Academic Entity Extraction

🔍 Purpose

To extract named entities from research-related queries, classify them into types, and normalize them where possible.

✅ Prompt Template

```text
You are a research metadata extraction agent. Extract all named entities mentioned in the input query, and classify them into the following types:
- "author"
- "institution"
- "country"
- "region"
- "journal"
- "funder"
- "subject"

Also normalize any known variations to their standard names where possible (e.g., "MIT" → "Massachusetts Institute of Technology").

Return the result as a list of dictionaries in the following format:

[
  {
    "name": "Original Mention",
    "type": "entity_type",
    "normalized_name": "Standardized Name"
  },
  ...
]

Input query: "{user_query}"
```

🧪 Example Input

```text
How much funding has the NIH and the Wellcome Trust given to cancer research at Harvard and Oxford?
```


🧾 Example Output

```text
[
  {
    "name": "NIH",
    "type": "funder",
    "normalized_name": "National Institutes of Health"
  },
  {
    "name": "Wellcome Trust",
    "type": "funder",
    "normalized_name": "Wellcome Trust"
  },
  {
    "name": "cancer research",
    "type": "subject",
    "normalized_name": "cancer"
  },
  {
    "name": "Harvard",
    "type": "institution",
    "normalized_name": "Harvard University"
  },
  {
    "name": "Oxford",
    "type": "institution",
    "normalized_name": "University of Oxford"
  }
]

```


---

🔄 Integration Flow (Recommended)

1.	Run Intent Detection First → Use Template 1 to extract query structure
2.	Run Entity Extraction with Normalization → Use Template 2 to standardize funders, institutions, etc.
3.	Pass Result to Search & Retrieval System → Use values for query building in Elasticsearch, SQL, or RAG retrievers
4.	Generate Final Response Based on Output Format → Call LLM summarizer or renderer for summary/table/chart



🛠️ Bonus: Prompt for Time Range Normalization

```text
Extract the time range mentioned in the input and return the result as:
- {"start_year": ..., "end_year": ...} OR
- {"relative": "last N years"}

Input: "{user_query}"

```

Improvement

- 	Few-shot examples to improve accuracy
- 	Fine-tuning strategies on domain queries
- 	Python wrappers for calling these templates using OpenAI or Anthropic APIs


---

### 🔍 Few-shot Prompt Examples for Intent Detection


Here are few-shot examples to improve the accuracy of user intent detection and academic entity extraction using GPT-style LLMs. You can embed these examples in a prompt (before or after the instruction) to guide the model toward consistent and structured outputs.

🛠 Tips for Using Few-shot Examples in Prompts
1.	Start with instruction, then give 2–4 diverse examples, then your input.
2.	Cover common cases: single entity, multiple entities, different entity types (institution, funder, country).
3.	Normalize to canonical names using your controlled vocabulary (e.g., NIH → National Institutes of Health).
4.	Use "relative" and "start_year"–"end_year" to teach both time range forms.

🧩 Instruction Template:
```text
Extract structured information from the user query in the following format:

{
  "intent_type": "...",
  "subject": "...",
  "metric": "...",
  "entity_type": "...",
  "entity_name": [...],
  "time_range": {...},
  "output_format": "..."
}

Below are some examples:

```

✅ Few-shot Examples:

Example 1

- User Query:  How has the AI research output changed in China since 2018?
- Structured Output:
```json
{
  "intent_type": "trend",
  "subject": "artificial intelligence",
  "metric": "publication count",
  "entity_type": "country",
  "entity_name": ["China"],
  "time_range": {
    "start_year": 2018,
    "end_year": 2024
  },
  "output_format": "trend line"
}
```

Example 2

- User Query:  Compare NIH and Wellcome Trust in terms of cancer research funding over the last 10 years.
- Structured Output:
```json
{
  "intent_type": "compare",
  "subject": "cancer",
  "metric": "funding amount",
  "entity_type": "funder",
  "entity_name": ["National Institutes of Health", "Wellcome Trust"],
  "time_range": {
    "relative": "last 10 years"
  },
  "output_format": "comparison table"
}
```

Example 3

- User Query: Give me a summary of top institutions publishing in Nature about climate change in the last 5 years.
- Structured Output:
```json
{
  "intent_type": "summary",
  "subject": "climate change",
  "metric": "publication count",
  "entity_type": "institution",
  "entity_name": ["Nature"],
  "time_range": {
    "relative": "last 5 years"
  },
  "output_format": "summary"
}
```

---

###  Few-shot Examples for Academic Entity Extraction

🧩 Instruction Template:

```text
Extract named entities from the user query and classify each by type. Normalize known variations.

Return format:
[
  {
    "name": "...",
    "type": "...",
    "normalized_name": "..."
  }
]

Examples:
```

✅ Few-shot Examples:

Example 1

- User Query:  What has MIT published on machine learning in the past 5 years?
- Structured Output:
```json
[
  {
    "name": "MIT",
    "type": "institution",
    "normalized_name": "Massachusetts Institute of Technology"
  },
  {
    "name": "machine learning",
    "type": "subject",
    "normalized_name": "machine learning"
  }
]
```

Example 2

- User Query:  List collaboration between Harvard and Stanford in neuroscience.
- Structured Output:
```json
[
  {
    "name": "Harvard",
    "type": "institution",
    "normalized_name": "Harvard University"
  },
  {
    "name": "Stanford",
    "type": "institution",
    "normalized_name": "Stanford University"
  },
  {
    "name": "neuroscience",
    "type": "subject",
    "normalized_name": "neuroscience"
  }
]
```

Example 3

- User Query: Show impact of cancer research funded by the ERC and DFG in Europe.
- Structured Output:
```json
[
  {
    "name": "cancer research",
    "type": "subject",
    "normalized_name": "cancer"
  },
  {
    "name": "ERC",
    "type": "funder",
    "normalized_name": "European Research Council"
  },
  {
    "name": "DFG",
    "type": "funder",
    "normalized_name": "Deutsche Forschungsgemeinschaft"
  },
  {
    "name": "Europe",
    "type": "region",
    "normalized_name": "Europe"
  }
]
```

--- 

🛠 Tips for Using Few-shot Examples in Prompts

1.	Start with instruction, then give 2–4 diverse examples, then your input.
2.	Cover common cases: single entity, multiple entities, different entity types (institution, funder, country).
3.	Normalize to canonical names using your controlled vocabulary (e.g., NIH → National Institutes of Health).
4.	Use "relative" and "start_year"–"end_year" to teach both time range forms.


---

### Complete Python Example

Here’s a complete Python example to:

1.	🧠 Automatically build few-shot prompts for:
  - 	User intent detection
  - 	Academic entity extraction
2.	🔌 Call OpenAI API to process queries
3.	🖱️ Optionally let users correct extracted results via a simple Streamlit UI

---

⚙️ Step 1: Install Dependencies

```bash
pip install openai streamlit
```

---

📁 Step 2: Project Structure

```text
academic_assistant/
├── intent_examples.json
├── entity_examples.json
├── app.py
```

📄 intent_examples.json (few-shot data for intent detection)

```json
[
  {
    "query": "Compare NIH and Wellcome Trust in cancer research funding.",
    "output": {
      "intent_type": "compare",
      "subject": "cancer",
      "metric": "funding amount",
      "entity_type": "funder",
      "entity_name": ["National Institutes of Health", "Wellcome Trust"],
      "time_range": {"relative": "last 10 years"},
      "output_format": "comparison table"
    }
  }
]
```

📄 entity_examples.json (few-shot data for entity extraction)

```json
[
  {
    "query": "What has MIT published on machine learning?",
    "output": [
      {
        "name": "MIT",
        "type": "institution",
        "normalized_name": "Massachusetts Institute of Technology"
      },
      {
        "name": "machine learning",
        "type": "subject",
        "normalized_name": "machine learning"
      }
    ]
  }
]
```

---

🧠 Step 3: Core App – app.py

```json
import openai
import json
import streamlit as st

openai.api_key = "your-api-key"

def build_few_shot_prompt(template, examples, query):
    shots = "\n\n".join(
        f"Query: {ex['query']}\nOutput:\n{json.dumps(ex['output'], indent=2)}"
        for ex in examples
    )
    return f"{template}\n\n{shots}\n\nQuery: {query}\nOutput:\n"

def call_openai(prompt, model="gpt-4", max_tokens=500):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=max_tokens
    )
    return response.choices[0].message['content']

def load_examples(file):
    with open(file) as f:
        return json.load(f)

st.title("Academic Query Analyzer 🧠📚")

query = st.text_input("Enter your academic research question:")

if query:
    intent_template = (
        "Extract the following fields:\n"
        "- intent_type\n- subject\n- metric\n- entity_type\n- entity_name\n- time_range\n- output_format\n"
        "Respond in JSON."
    )

    entity_template = (
        "Extract named entities from the user query and classify each by type. "
        "Normalize known names. Format as a JSON list."
    )

    intent_examples = load_examples("intent_examples.json")
    entity_examples = load_examples("entity_examples.json")

    intent_prompt = build_few_shot_prompt(intent_template, intent_examples, query)
    entity_prompt = build_few_shot_prompt(entity_template, entity_examples, query)

    with st.spinner("Analyzing intent..."):
        intent_result = call_openai(intent_prompt)
    st.subheader("📌 Detected Intent")
    st.code(intent_result, language="json")

    with st.spinner("Extracting academic entities..."):
        entity_result = call_openai(entity_prompt)
    st.subheader("🏷️ Extracted Entities")
    st.code(entity_result, language="json")

    st.success("Done! You can edit and copy the outputs.")
```


🧪 Example Use

- Input query:  What is the trend of AI research funding in Germany over the last 5 years?
- Intent Output:
```json
{
  "intent_type": "trend",
  "subject": "artificial intelligence",
  "metric": "funding amount",
  "entity_type": "country",
  "entity_name": ["Germany"],
  "time_range": {
    "relative": "last 5 years"
  },
  "output_format": "trend line"
}
```

Entity Output:
```json
[
  {
    "name": "AI",
    "type": "subject",
    "normalized_name": "artificial intelligence"
  },
  {
    "name": "Germany",
    "type": "country",
    "normalized_name": "Germany"
  }
]
```


✅ Optional Enhancements

| Feature                     | How to Add                                               |
|-----------------------------|-----------------------------------------------------------|
| Correction UI               | Use `st.json_editor` in Streamlit (beta feature)         |
| Save output                 | Add a “Download JSON” button                             |
| Connect to retrieval        | Trigger document search with parsed values               |
| Add intent classification model | Use `scikit-learn` or `transformers` for local inference |



### 🧩 Prompt Example (Optimized Research Query Extractor)

```text
You are a research assistant. Extract structured fields from the user query:

Fields:
- intent_type
- subject
- entity_type
- entity_name
- metric
- time_range

Respond in JSON.

Few-shot examples:
Query: "Show top universities in cancer research in 2020"
→ Output: {
  "intent_type": "list",
  "subject": "cancer",
  "entity_type": "institution",
  "entity_name": [],
  "metric": "publication count",
  "time_range": {"start_year": 2020, "end_year": 2020}
}

Query: {user_query}
→ Output:

```