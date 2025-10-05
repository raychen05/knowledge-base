
## Identify Academic institutions and Funding Agencies


To identify whether a user input refers to an academic institution or a funder, and then normalize it to the correct name from either list (10k institutions, 20k funders), the best approach is a multi-stage hybrid pipeline, combining classification + name normalization, ideally with embeddings + LLM for fallback.


---


### ✅ Overall Pipeline:

Input:
-	User-freeform input like harvard med, gates foundation, NSF, Cambridge uni, etc.

Goal:
1.	Classify: Is the input likely an academic institution or funder?
2.	Normalize: Map it to the correct canonical name from the respective list.

---

### 🔍 Step 1: Preprocessing & Canonicalization (Shared)

-	Normalize casing, punctuation, whitespace
-	Expand common abbreviations: NSF → National Science Foundation
-	Strip suffixes/prefixes like univ, foundation, institute, dept., lab, etc.

Also prepare:
-	Alias dictionaries for both academic and funders ("NSF" → National Science Foundation, "Gates Fnd" → Bill and Melinda Gates Foundation, "UCB" → University of California, Berkeley)

---

### 🧠 Step 2: Classification — Is it a funder or an academic institution?


🔸 Approach A (Recommended): Embedding Similarity Classifier

1.	Use an embedding model like all-MiniLM-L6-v2 or OpenAI’s text-embedding-3-small.
2.	Embed:
    -	The user input
    -	A centroid vector (or representative average) of all institution names and another for funders
3.	Compute cosine similarity to both groups
4.	Choose the label (institution vs funder) based on higher similarity score


🔸 Approach B (Fallback/Boosting): LLM Classifier

Prompt GPT:

“Classify the following as either a funding agency or academic institution: ‘Wellcome Trust’”

Use this as a fallback or for ambiguous similarity scores.

---

### 🗂 Step 3: Normalize to Canonical Name (Based on Classified Type)

Once you classify the input:

-	Use vector search (FAISS or similar) over pre-computed embeddings of institution names or funder names
-	Optionally combine with fuzzy matching and alias dictionary

Output:
-	{ type: "funder", name: "National Science Foundation" }
-	{ type: "institution", name: "Harvard University" }


---


### 🛠 Architecture Summary


| Component                | Tool/Library/Service                                      |
|--------------------------|----------------------------------------------------------|
| **Embeddings**           | SentenceTransformers, OpenAI Embeddings                  |
| **Vector Search**        | FAISS, Pinecone, Weaviate                                |
| **Fuzzy Matching**       | rapidfuzz                                                |
| **LLM Classification**   | GPT-4, GPT-3.5 (fallback for ambiguous/low-confidence)   |
| **Alias Lookup**         | Manual & crowdsourced alias dictionary                   |
| **Final Score Ranker**   | Weighted fusion of embedding similarity, fuzzy match, and alias hit |



🧪 Optional: Confidence Score & Human-in-the-Loop

-	If no match > threshold, flag for human review or LLM fallback
-	Store past queries and resolved labels to improve alias and training data

---

### 🚀 Example

Input: "Gates Found"

1.	Preprocess: "gates found"
2.	Classify: Funder (via embedding centroid similarity or alias)
3.	Normalize (funder vector DB): Match → "Bill & Melinda Gates Foundation"

---

### ✅ Final Notes

This hybrid system is:

-	Scalable (precompute embeddings)
-	Accurate (semantic search beats pure string match)
-	Extensible (can add new funders or institutions over time)
-	LLM-boosted (for ambiguity and rare/creative inputs)

---

Let me know if you’d like:

-	Sample code for embedding-based classification
-	An alias dictionary template
-	LLM prompts for fallback classification/normalization




