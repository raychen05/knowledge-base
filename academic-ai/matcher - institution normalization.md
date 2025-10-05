## Institution Normalization


To normalize user-entered institution names (which can include typos, abbreviations, or partial names) to a list of 10,000 academic institutions, you need a multi-stage approach that combines classic fuzzy matching techniques, embeddings, and optionally an LLM for difficult edge cases.


### 🔧 Step-by-Step Approach:

---

#### 1. Preprocess and Index the Institution List

-	Clean and normalize the 10,000 institution names:
-	Lowercase, strip whitespace
-	Remove stopwords like “university,” “college,” “institute,” etc., for embedding/fuzzy purposes (store original for final mapping)
-	Normalize abbreviations (e.g., “MIT” → “Massachusetts Institute of Technology”) using a curated alias dictionary
-	Build an inverted index with alternate names and abbreviations (e.g., aliases like “NYU”, “UC Berkeley”, etc.)

---

#### 2. Encode Institution Names (Offline)

-	Use sentence embeddings from a model like:
-	all-MiniLM-L6-v2 (via SentenceTransformers)
-	bge-small-en (very fast and accurate)
-	For more accuracy: OpenAI’s text-embedding-3-small or text-embedding-3-large
-	Store these embeddings in a vector index using FAISS or similar.

---

#### 3. At Query Time: User Input Normalization

-	Normalize the user input (same process as above)
-	Use the embedding model to encode the input
-	Search vector index for top-N most similar matches

---

#### 4. Rank and Match

-	Combine multiple scoring strategies:
-	Cosine similarity of embeddings
-	Fuzzy string match score (Levenshtein/Token Set Ratio using fuzzywuzzy or rapidfuzz)
-	Optional: Apply a BM25-based search using Elasticsearch for traditional keyword retrieval
-	Use a weighted score to re-rank top 5–10 candidates and select the best

---

#### 5. (Optional) LLM as Final Arbiter

For ambiguous or poor matches:
-	Use an LLM (e.g., GPT-4) to validate or disambiguate the top matches:
-	Prompt: “User entered ‘Harverd’. Which of these institutions is most likely meant: [Harvard University, Haverford College, …]?”

---

#### 6. Alias Dictionary & Feedback Loop

-	Maintain a growing alias → canonical name dictionary from past resolved queries.
-	Allow manual review or feedback to continually improve accuracy.


---

### 🚀 Tools Stack Recommendation:


| Task            | Tool(s)                                         |
|-----------------|-------------------------------------------------|
| Embeddings      | SentenceTransformers, OpenAI Embeddings         |
| Vector Index    | FAISS, Weaviate, Pinecone                       |
| Fuzzy Matching  | rapidfuzz, fuzzywuzzy, thefuzz                  |
| LLM             | GPT-4 (API, for disambiguation)                 |
| Search          | Elasticsearch (optional)                        |


Example Workflow:

Input: "UCBerky"
-	Normalize: "uc berky"
-	Embed and vector search: Top hits might be:
-	UC Berkeley (cosine 0.91)
-	University of California, Berkeley (cosine 0.90)
-	Berkeley College (cosine 0.70)
-	Use fuzzy match + alias dictionary
-	Final result: University of California, Berkeley

---

### ✅ Summary

Best practice combines:

1.	Preprocessing and alias expansion
2.	Embedding-based semantic search
3.	Fuzzy matching for string-level correction
4.	(Optional) LLM for edge cases
5.	Continuous feedback to expand the alias mapping

