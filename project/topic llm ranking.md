
##  Aggregation Algorithm Summary - Researchers


#### Objective

The goal is to aggregate research topics across various content types and assign a strength indicator to researchers, departments, and organizations. This will enable ranking and sorting for applications like Expert Finder, while also identifying a researcher’s strongest topics.

Key Aggregation Principles

1.	Content-Based Topic Aggregation
    -	Different types of research outputs (publications, clinical trials, patents, etc.) contribute to a researcher’s expertise in a topic.
    -	Each content type is assigned a weight (e.g., clinical trials may weigh more than regular publications).
    -	Multiple topics can be associated with a single document.
      
2.	Strength Indicators & Ranking
    -	Frequency Count: Tracks how often a researcher works on a given topic.
    -	Impact (Times Cited): Measures how influential the work is, ensuring it reflects what the researcher is known for.
    -	Recency Factor: Optional—users can filter to focus on recent work.
    -	Composite Strength Score: A behind-the-scenes ranking combining frequency, impact, and content weight to sort researchers by expertise.
    -	First Author: More documents on a topic = higher score.
    -	Last Author: More documents on a topic = higher score.
    -	Corresponding Author: More documents on a topic = higher score.
    -	99% Percentile: More documents on a topic = higher score.
    - Highly Cited: More documents on a topic = higher score.
    - Hot Paper: More documents on a topic = higher score.
    - Citation from Patent: More documents on a topic = higher score.
  
3.	Sorting & Ranking of Topics and Researchers
    -	Per Researcher: Topics are ranked by strength, displaying primary and secondary expertise.
    -	Across Researchers:
        -	Single Topic Search: Researchers are sorted by strength in that topic.
        -	Multiple Topic Search: Researchers matching all topics are ranked higher than partial matches.

4.	User-Driven Adjustments
    -	Future enhancements may allow users to assign weights to content types.
    -	Topic impact normalization can be applied to adjust for discipline differences.

---

#### Implementation & Deliverable

-	Aggregate research topics across sample content sets.
-	Apply topic weighting to compute strength scores.
-	Demonstrate ranking of researchers and their strongest topics.
-	Ensure flexible search ranking without enforcing a definitive hierarchy.

---

## LLM Prompt for Aggregating and Ranking Research Topics by Strength


Prompt:

You are an expert in analyzing and ranking research topics based on their significance and impact for a given researcher. Your task is to process a list of research-related documents (publications, patents, clinical trials) and generate a ranked list of research topics for the researcher, with scores on a scale from 1 to 10.

Instructions:

1.	Aggregation of Research Topics:
    -	Each document is associated with one or more research topics.
    -	Consider all provided documents to determine the major research topics for the researcher.

2.	Scoring and Ranking Principles:

- Assign a topic strength score (1 to 10) based on: 
    -	Frequency of topic occurrences: More documents on a topic indicate stronger expertise.
    -	Times Cited: Higher citation counts increase the importance of a topic.
    -	Document Type Weighting:
        -	Patents and clinical trials may carry higher weight than standard publications.
        -	Highly-cited papers and hot papers indicate high impact.
    -	Recency Factor (optional): More recent impactful publications may slightly increase the score.

3.	Output Format:
    -	A sorted list of research topics from highest to lowest strength score.
    -	Each topic should have a score from 1 to 10 representing its strength.
    -	Provide a brief justification for the score of each topic.



Input Example:

A list of documents with the following fields:

-	Research Topic
-	Document Type (Publication, Patent, Clinical Trial)
-	Times Cited
-	Is Highly-Cited? (Yes/No)
-	Is Hot Paper? (Yes/No)
-	Publication Year


Output Example:

```json
[
  {"research_topic": "Artificial Intelligence in Healthcare", "score": 9.5, "justification": "High frequency of publications, multiple highly-cited papers, and a hot paper."},
  {"research_topic": "Machine Learning for Drug Discovery", "score": 8.7, "justification": "Several publications and a clinical trial, moderate citation impact."},
  {"research_topic": "Computational Biology", "score": 7.2, "justification": "A patent and some publications, but fewer citations."}
]
```

Key Considerations:

-	The score should reflect both breadth (frequency) and depth (impact) of work in a topic.
-	Topics with high impact papers or patents should rank higher even if frequency is lower.
-	Topics with low impact but many documents should receive a moderate score.
-	Use a balanced approach to avoid overweighing any single factor.

Task: Generate a ranked list of research topics for the given researcher, following the above principles.

---

## Simplified LLM Prompt

Task: Rank a researcher’s topics_micro  an score the stengh based on importance and impact.  Output the top 10 topics_micro with their scores and reasons(including important perofmrance and impact metrics) in yaml format.



Instructions:

1.	Aggregate Topics:
    -	Each document (publication, patent, clinical trial) is linked to one or more research topics.
    -	Consider all documents to determine the researcher’s key topics.

2.	Score & Rank Topics (1-10) Based on:
    -	Frequency: More documents on a topic = higher score.
    -	Impact: Higher citations, hot papers, and highly-cited papers boost score.
    -	Document Type Weighting:
    -	Patents and clinical trials weigh more than regular publications.
    -	Recency (Optional): Recent impactful work may slightly increase score.

3.	fake Output Format (YAML):

```yaml
- topics_micro: "6.10.63 Corporate Governance"
  score: 9.5
  reason: Many publications, multiple highly-cited papers, and a hot paper.
```

Alternatively, JSON format

3.	Output Format (JSON):

```json
[
  {"research_topic": "AI in Healthcare", "score": 9.5, "reason": "Many publications, multiple highly-cited papers, and a hot paper."},
  {"research_topic": "ML for Drug Discovery", "score": 8.7, "reason": "Several papers, a clinical trial, moderate citations."},
  {"research_topic": "Computational Biology", "score": 7.2, "reason": "A patent and some papers, but fewer citations."}
]
```

A list of documents:  


---