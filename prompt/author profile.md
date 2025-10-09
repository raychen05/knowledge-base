##  Summarization for Author Profile


### Prompt

```plaintext
Task: Rank a researcher’s topics_micro  an score the stengh based on importance and impact.  Output the top 10 topics_micro with their scores and reasons(including important perofmranc and impact metrics) in yaml format.

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
-	First Author: More documents on a topic = higher score.
-	Last Author: More documents on a topic = higher score.
-	Corresponding Author: More documents on a topic = higher score.
-	99% Percentile: More documents on a topic = higher score.
- Highly Cited: More documents on a topic = higher score.
- Hot Paper: More documents on a topic = higher score.
- Citation from Patent: More documents on a topic = higher score.



3.	fake Output Format (YAML):

- topics_micro: "6.10.63 Corporate Governance"
  score: 9.5
  reason: Many publications, multiple highly-cited papers, and a hot paper.


A list of documents:  

```


