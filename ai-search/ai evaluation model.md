
## AI Evaluation Model for Evaluating the Quality of Academic Paper 



To design a systematic approach, scoring model, and an LLM prompt for evaluating the quality of academic paper search results based on a user’s query (keywords, sentence, or Boolean logic), here’s a complete, modular setup:

⸻


### ✅ 1. System Approach

**Goal**: Evaluate how well retrieved academic papers match the user’s search intent and rank them by quality and relevance.

**Input**:
	•	User query (keywords, sentence, or Boolean logic)
	•	Top N academic papers (title, abstract, metadata, possibly full text)
    


**System Architecture**:

```plaintext
+-------------------+           +--------------------------+           +---------------------+
| User Input (Query)| -------> | LLM: Intent Extraction   | --------> | Paper Relevance Eval|
+-------------------+           +--------------------------+           +----------+----------+
                                                                                  |
                                                                                  v
                                                                      +-----------+-----------+
                                                                      | Quality Scoring Model |
                                                                      +-----------+-----------+
                                                                                  |
                                                                                  v
                                                                    +-------------+-------------+
                                                                    | Ranked Results w/ Scores  |
                                                                    +---------------------------+

```


---

### ✅ 2. Scoring Model


Components (Scored 0–1 or 0–5, then weighted):

```plaintext
Total Score = Weighted sum of component scores (normalize to [0, 100])
```

---

### ✅ 3. LLM Prompt (to Evaluate a Paper Given a Query)

You can feed each paper (title, abstract, metadata) and ask the LLM to evaluate it like so:

🔍 Evaluation Prompt Template

```text
You are evaluating the relevance and quality of an academic paper based on a user query.

User Query:
"{user_query}"

Paper Metadata:
- Title: "{title}"
- Abstract: "{abstract}"
- Authors: {authors}
- Journal/Conference: {venue}
- Year: {year}
- Citations: {citation_count}

Evaluate the following and respond with a score from 1 to 5 for each dimension:

1. Relevance to the query (semantic match)
2. Scope alignment with user intent
3. Recency (consider publication year)
4. Impact/prestige (based on venue and citations)
5. Methodological rigor (based on abstract)
6. Clarity of writing (abstract and title)

Then return a final weighted score out of 100.

Use this JSON format:
{
  "relevance": x,
  "scope_match": x,
  "recency": x,
  "impact": x,
  "rigor": x,
  "clarity": x,
  "final_score": x
}
```

--- 

### ✅ Example Output from LLM:

```json
{
  "relevance": 5,
  "scope_match": 4,
  "recency": 4,
  "impact": 3,
  "rigor": 4,
  "clarity": 5,
  "final_score": 87
}
```





