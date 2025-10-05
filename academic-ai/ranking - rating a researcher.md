## Ranking A Researcher


Here is a detailed, intuitive, and efficient methodology for a researcher (PhD, postdoc, or professor) to objectively evaluate and rank the research output and impact of other researchers in a specific research topic, using Web of Science (WoS) and InCites.

This is especially useful when:

-	Selecting collaborators, reviewers, or mentors
-	Mapping field leaders
-	Justifying co-PIs for grant proposals
-	Benchmarking your own position in the field

---

### 🎯 Goal:

Objectively evaluate and rank researchers working on a specific research topic using publication volume, citation impact, funding success, and collaborative strength.

---

### 🛠️ Tools Required:

-	✅ Web of Science Core Collection (WoS)
-	✅ InCites Benchmarking & Analytics
-	[Optional] WoS & InCites APIs
-	[Optional] EndNote or LLM assistant (for summarization)

---

### 🔁 Step-by-Step Methodology

---

#### ✅ Step 1: Define the Target Research Topic


In Web of Science:

1.	Use a precise keyword or Boolean search string
- TS=("graph neural networks" AND "drug discovery")

2.	Apply filters:
    -	Years: Last 5 years
    -	Document Type: Articles
    -	Language: English
    -	[Optional] Filter by Funding Agency
3.	Save this search as your topic definition baseline

✅ Output: List of articles that define your target research domain.

---

#### ✅ Step 2: Extract & Rank Authors in Topic Area


1.	In WoS results, click “Analyze Results” → “Authors”
2.	Export:
    -	Top 100–500 authors based on publication count
3.	Optionally analyze:
    -	Organizations
    -	Funding agencies
4.	Sort authors by:
    -	Total Publications
    -	Total Citations
    -	Average Citations per Article
    -	Usage Count (Recent attention)

✅ Output: A raw author ranking for this topic.

---

#### ✅ Step 3: Import Top Authors into InCites for Impact Benchmarking

In InCites:

1.	Go to “People → Author Search”
2.	Paste in author names (ensure full name or ORCID where possible)
3.	Add filters:
    -	Field: Match your topic area
    -	Time window: Last 5 years
4.	Analyze each author:
    -	Category Normalized Citation Impact (CNCI): Field-adjusted impact
    -	% Documents in Top 10% by Citations
    -	% Funded Publications
    -	International Collaboration %
    -	Total Citations, Total Output

✅ Output: Objective, normalized researcher profiles.

Pro Tip: CNCI > 2.0 and >40% Top 10% outputs are strong indicators of global research leadership.

---

#### ✅ Step 4: Rank Researchers by Multi-Metric Composite Score

Create a custom evaluation scorecard, e.g.:

| Metric                        | Weight | Source   |
|-------------------------------|--------|----------|
| CNCI                          | 30%    | InCites  |
| # Publications in Topic       | 25%    | WoS      |
| % in Top 10% Most Cited       | 20%    | InCites  |
| % Funded Publications         | 15%    | InCites  |
| Recent Usage Count (attention)| 10%    | WoS      |


1.	Normalize scores (e.g., scale 0–100)
2.	Compute weighted average for each researcher

✅ Output: Ranked, multi-factor evaluation of researchers on your topic.

---

#### ✅ Step 5: Qualitative Validation

For top 5–10 ranked researchers:

1.	Check recent publications (titles, abstracts) to ensure:
    -	Relevance to your sub-area
    -	Similar methods or datasets
    -	Continuity of work
2.	Use “Times Cited” and “Citing Articles” to understand influence
3.	Review institution, co-author networks, and funding sources

✅ Output: Validated shortlist of leaders, potential collaborators, or evaluators in your field.

---

### 🧠 Bonus: Use WoS + InCites API or LLM Agent to Automate

You can script or build an AI assistant to:

-	Perform search & filter automatically
-	Pull WoS author data and enrich with InCites metrics
-	Generate side-by-side profile cards
-	Score and rank researchers by your weights

Let me know if you want a LangChain agent starter for this.

---

### 📝 Summary Table


| Step                | Tool                | Goal                                |
|---------------------|---------------------|-------------------------------------|
| 1. Define topic     | WoS                 | Set search boundary                 |
| 2. Extract authors  | WoS                 | Gather publication data             |
| 3. Benchmark authors| InCites             | Assess CNCI, Top 10%, Funding       |
| 4. Rank & score     | Spreadsheet/code    | Calculate composite ranking         |
| 5. Validate output  | Manual review       | Finalize shortlist                  |

---


### 📌 Evaluation Indicators Reference


| Indicator                | Description                                         |
|--------------------------|-----------------------------------------------------|
| **CNCI** (≥1.5 good, ≥2 excellent) | Citations normalized by field and year           |
| **% in Top 10%**         | Percentage of papers in the top 10% cited globally  |
| **% Funded Output**      | Proportion of publications with funding             |
| **Total Output & Citations** | Measures overall productivity and recognition    |
| **Usage Count**          | Early signals of interest (e.g., altmetrics)        |


