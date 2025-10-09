

## Summarization of Academic Researcher's Profile 


---

### Outline of Researcher Profile


1. Personal and Professional Background
- **Education and Qualifications**: Include degrees, institutions, and years of graduation.
- **Current Position**: Title, department, and institution where the researcher is currently working.
- **Previous Roles**: Significant past positions that shaped their career.

1. Research Areas
- **Primary Research Focus**: The main disciplines or topics the researcher specializes in.
- **Secondary Research Interests**: Related areas of interest that complement their primary focus.
- **Interdisciplinary Contributions**: Any work that spans across multiple fields.

2. Key Publications
- **Most Influential Papers**: Highlight key papers that have had a significant impact in their field.
- **Recent Publications**: Include a list of the latest research papers to show current activity.
- **Books and Chapters**: Mention any authored or edited books, book chapters, or major reviews.

3. Research Impact
- **Citation Metrics**: Include metrics like h-index, total citations, or other relevant measures.
- **Grants and Funding**: Information on major grants or funding received for research.
- **Collaborations**: Highlight significant collaborations with other researchers or institutions.

4. Recognition and Awards
- **Honors and Awards**: Any awards, fellowships, or recognitions received.
- **Editorial Roles**: Membership on editorial boards of journals or as a reviewer.
- **Memberships**: Inclusion in professional societies or committees.

5. Trends in Research Interest
- **Emerging Research Areas**: Identify any new or shifting areas of focus in recent years.
- **Influence on the Field**: How their work has shaped current trends in their discipline.
- **Future Directions**: Possible future research directions or emerging topics of interest.

6. Impact Beyond Academia
- **Industry Applications**: Any research that has been applied in industry or policy.
- **Public Engagement**: Participation in public lectures, media contributions, or community outreach.
- **Mentorship and Training**: Contributions to training the next generation of researchers.


---

###  Breakdown of Profile

Here are the definitions and descriptions for the fields in an author’s profile:


1.	Author Identifiers/ID
- Definition: Unique identifiers assigned to an author for distinguishing their work in databases and academic platforms.
- Description: Author identifiers such as ORCID, ResearcherID, or Scopus Author ID are used to ensure accurate attribution of an author’s research work. These identifiers help track publications, citations, and collaborations across different research platforms.

2.	Professional Background
- Definition: An overview of an author’s educational and career history.
- Description: This section includes the author’s academic qualifications, professional positions (such as current and past employment), affiliations, and relevant career milestones. It provides context on the author’s expertise and professional trajectory.

3.	Research Areas
- Definition: The specific fields or disciplines of study the author focuses on in their research.
- Description: Research areas describe the topics, problems, or scientific domains the author is actively engaged in. These areas could be broad (e.g., environmental science) or niche (e.g., quantum computing applications in cryptography), often indicating the author’s expertise and interests.

4.	Key Publications
- Definition: The most significant or impactful research works published by the author.
- Description: Key publications highlight the author’s contributions to the field, typically focusing on influential papers, books, or other research outputs. These works are often cited by other researchers and can include highly rated or innovative studies.

5.	Research Impact
- Definition: The measurable effect of the author’s research on their field, including citations and recognition.
- Description: This metric reflects how widely the author’s work is recognized and referenced by peers. It includes citation counts, h-index, and other indicators of the long-term influence of their publications within the academic and research community.

6.	Trending Research Interests
- Definition: Emerging or evolving topics that the author is currently researching or showing interest in.
- Description: These are areas the author is exploring in recent work, often reflecting shifts in the academic landscape or new technological and scientific challenges. These interests can signal where the author’s research may be heading in the future.

7.	Impact Beyond Academia
- Definition: The influence of the author’s work outside of the academic community, such as in industry, policy, or society.
- Description: This field captures contributions that extend beyond traditional research, such as policy advocacy, public engagement, or industry collaborations. It includes practical applications of research, the development of technologies, or involvement in social or governmental initiatives.

8.	Works Being Cited
- Definition: The works authored by the individual that are frequently cited by other researchers.
- Description: This refers to the research outputs that are referenced in other academic works, indicating their relevance and importance in the field. Highly cited works often reflect significant contributions to their respective disciplines.

9.	Document Attribute
- Definition: Metadata related to specific documents or publications by the author.
- Description: Document attributes can include publication type (e.g., article, book, conference paper), publication date, journal name, and keywords. These details help categorize and identify specific works by the author in databases, making it easier to locate and assess their research.


**JDON Version**

```json

{
  "summary": "A concise overview of the researcher's professional journey and contributions to their field basedon ranking, academic impact etc.",
  
  "personal_and_professional_background": {
    "name": "researcher's name",
    "pguid": "urn:spm:{diang_id}",
    "affiliation": "The current affiliation of the researcher",
    "education_and_qualifications": "Include degrees, institutions, and years of graduation.",
    "current_position": {
      "title": "Title of the current role",
      "department": "Department name",
      "institution": "Current institution"
    },
    "previous_roles": "List of significant past positions that have shaped the researcher's career."
  },
  
  "research_areas": {
    "primary_focus": "Main disciplines or topics the researcher specializes in.",
    "secondary_interests": "Related areas of interest that complement their primary focus.",
    "interdisciplinary_contributions": "Any work that spans across multiple fields."
  },
  
  "key_publications": {
    "most_influential_papers": "Highlight key papers that have significantly impacted the field.",
    "recent_publications": "List of the latest research papers to demonstrate current activity."
  },
  
  "research_impact": {
    "citation_metrics": "Metrics like h-index, total citations, or other relevant measures.",
    "grants_and_funding": "Details of major grants or funding received for research.",
    "collaborations": {
      "significant_collaborations": "Important collaborations with other researchers or institutions.",
      "top_collaborators": "List of the most frequent collaborators."
    }
  },
  
  "trends_in_research_interest": {
    "emerging_areas": "New or shifting areas of focus in recent years.",
    "influence_on_field": "How their work has shaped current trends in their discipline.",
    "future_directions": "Potential future research directions or emerging topics of interest."
  },
  
  "impact_beyond_academia": {
    "industry_applications": "Any research applied in industry or policy.",
    "public_engagement": "Participation in public lectures, media contributions, or community outreach."
  },

 "cited_works": {
    "top_cited_publications": "Top-cited publications (title, journal/conference, and citation count)",
    "top_cited_categories": "Top-cited categories or research areas where their work is most referenced.",
    "top_cited_organizations": "Top organizations or institutions citing the author's work the most.",
    "top_cited_authors": "Top authors who have frequently cited this author’s research.",
    "top_cited_articles": "Top-cited articles that are highly referenced in specific fields or regions.",
    "citations_trends": "Any notable trends or shifts in the citations over time (e.g., increase in citations in a specific area).",
    "breakdown_topics": "A breakdown of the most popular topics cited from this author's works.",
  }
}

```


---


###  Prompt - Summarization

'''plaintext
As an expert in academic management and research, your task is to summarize an academic researcher's profile based on the background information provided. Ensure the summary is in JSON format, with all tags in lowercase. The profile should cover the following major areas:

{
  "summary": "A concise overview of the researcher's professional journey and contributions to their field.",
  
  "personal_and_professional_background": {
    "pguid": "urn:spm:{diang_id}",
    "researcher_id": "{r_id}",
    "affiliation": "The current affiliation of the researcher",
    "education_and_qualifications": "Include degrees, institutions, and years of graduation.",
    "current_position": {
      "title": "Title of the current role",
      "department": "Department name",
      "institution": "Current institution"
    },
    "previous_roles": "List of significant past positions that have shaped the researcher's career."
  },
  
  "research_areas": {
    "primary_focus": "Main disciplines or topics the researcher specializes in.",
    "secondary_interests": "Related areas of interest that complement their primary focus.",
    "interdisciplinary_contributions": "Any work that spans across multiple fields."
  },
  
  "key_publications": {
    "most_influential_papers": "Highlight key papers that have significantly impacted the field.",
    "recent_publications": "List of the latest research papers to demonstrate current activity."
  },
  
  "research_impact": {
    "citation_metrics": "Metrics like h-index, total citations, or other relevant measures.",
    "grants_and_funding": "Details of major grants or funding received for research.",
    "collaborations": {
      "significant_collaborations": "Important collaborations with other researchers or institutions.",
      "top_collaborators": "List of the most frequent collaborators."
    }
  },
  
  "trends_in_research_interest": {
    "emerging_areas": "New or shifting areas of focus in recent years.",
    "influence_on_field": "How their work has shaped current trends in their discipline.",
    "future_directions": "Potential future research directions or emerging topics of interest."
  },
  
  "impact_beyond_academia": {
    "industry_applications": "Any research applied in industry or policy.",
    "public_engagement": "Participation in public lectures, media contributions, or community outreach."
  },

 "cited_works": {
    "top_cited_publications": "Top-cited publications (title, journal/conference, and citation count)",
    "top_cited_categories": "Top-cited categories or research areas where their work is most referenced.",
    "top_cited_organizations": "Top organizations or institutions citing the author's work the most.",
    "top_cited_authors": "Top authors who have frequently cited this author’s research.",
    "top_cited_articles": "Top-cited articles that are highly referenced in specific fields or regions.",
    "citations_trends": "Any notable trends or shifts in the citations over time (e.g., increase in citations in a specific area).",
    "breakdown_topics": "A breakdown of the most popular topics cited from this author's works.",
  }
}
   

Backrgound information: {{meta_data}}


'''


---


### Output Example


1. Summary of obert Vishny's Performance:

```md

### Summary:

Robert Vishny, a prominent researcher affiliated with the University of Chicago and the National Bureau of Economic Research (NBER), has made significant contributions to the academic community. His work, mostly cited within academic circles, has garnered 43,374 citations, with 43,255 of those coming from external sources, indicating minimal self-citation. He holds an h-index of 48, a strong indicator of the consistent impact of his research across multiple papers.

### Key metrics highlight his significant citation impact:

- His work has a Category Normalized Citation Impact of 21.75, which means his research is cited over 21 times more than the average in his field.
- His Citation Impact of 747.83 suggests a high average citation per paper.
- Vishny’s influence extends far beyond the national level, with 41.98% impact relative to the world average, emphasizing his global scholarly influence.
- 92.33% average percentile indicates that his papers are ranked in the top 10% of their respective categories.

Regarding quality, 44.83% of his publications are in the top 1%, and 79.31% are in the top 10%, further demonstrating the high relevance and value of his research. Additionally, 33 of his publications are available through open access, contributing to his research’s broad accessibility.

Vishny's collaborations are primarily domestic (56.9%), with some international partnerships (18.97%), but no industry collaborations are recorded. His work has also been referenced in patents, albeit minimally (2 citations).

### Conclusion:
Robert Vishny is a highly influential researcher whose work has received substantial recognition globally, particularly in high-impact academic circles. His h-index of 48 and Category Normalized Citation Impact of 21.75 are testaments to the exceptional quality and reach of his research. Although his focus has been on academic rather than industry collaborations, the depth and breadth of his work position him as a leading figure in his field. The absence of highly cited or hot papers suggests that his influence is steady across a broad body of work rather than concentrated in a few blockbuster publications.

```

---

2. Summary of Robert Vishny's Cited Work:

```md
Based on the citation metrics for Robert Vishny’s research, his work has garnered significant attention across multiple high-impact topics, organizations, and researchers, highlighting his profound influence in several areas of economics and finance.

#### Key Cited Research Topics:
1. **Corporate Governance**: Vishny’s most-cited work revolves around corporate governance, with **18,782 citations** in this area, contributing to a total of **609,588 citations** globally. This underscores his foundational contributions to corporate governance theory and practices, making it his most influential domain.
2. **Economic Growth**: His research on economic growth is the second most cited, with **5,561 citations** contributing to **207,802 total citations**. His work has significantly impacted macroeconomic growth theories.
3. **Option Pricing**: With **5,244 citations** and **176,484 total citations**, Vishny's work on option pricing highlights his influence on financial economics, particularly in asset pricing.
4. **Corporate Social Responsibility (CSR)**: Vishny’s work in CSR, although less cited than his corporate governance work, still has notable influence with **1,314 citations** and **56,153 total citations**.
5. **Internationalization, Knowledge Management, and International Trade**: His work on topics such as internationalization (741 citations), knowledge management (422 citations), and international trade (613 citations) shows broad but comparatively more specialized influence in global business and economics.

#### Key Cited Researchers:
1. **Andrei Shleifer**: The most frequent collaborator and one of the top-cited researchers in this network, with **120 citations** from Vishny’s work and a total of **71,309 citations** globally. This reflects their joint contributions to corporate governance.
2. **Robert Vishny**: His own work has been cited **39 times** by others, leading to **37,930 total citations**, emphasizing his reputation as a foundational thinker in his field.
3. **Collaborators like Lopez-de-Silanes, Florencio and La Porta, Rafael**: These scholars, with **34 and 26 citations**, respectively, also demonstrate key partnerships in Vishny’s research network.

#### Key Cited Organizations:
1. **Harvard University**: The leading institution citing Vishny’s work with **822 documents** and **174,286 total citations**, reflecting the strong academic connection and intellectual influence between Vishny’s work and Harvard.
2. **National Bureau of Economic Research (NBER)**: Vishny’s research is widely cited within NBER, with **956 documents** contributing to **143,699 total citations**, reflecting his central role within this economic research organization.
3. **University of Chicago**: Vishny’s own institution has contributed **481 documents** and **110,792 citations** to his work, underscoring his significant role within the academic community at Chicago.
4. Other major institutions like the **University of California System** (766 citations) and **MIT** (330 citations) also prominently reference his work.

### Conclusion:

Robert Vishny's research has had a far-reaching and transformative impact, particularly in the fields of **corporate governance**, **economic growth**, and **option pricing**. His collaborative work with high-profile economists such as Andrei Shleifer has defined key areas of economic theory, and his influence extends globally across top academic institutions such as **Harvard**, **NBER**, and the **University of Chicago**. Vishny’s work is foundational in corporate governance, widely cited across multiple institutions, and continues to shape scholarly discourse in economics, business, and finance.

Despite his broad influence, Vishny's work has fewer citations in more specialized areas like **corporate social responsibility** and **internationalization**, indicating a concentration of his impact in core financial and economic theories. The strong academic collaborations and lack of industrial citations highlight his role as a leading academic rather than an industry-focused researcher.

```

---

### Prompt - Summary of Profile

```pliantext
Task:
 As an expert in academic research, Summarize the academic profile of a researcher in 250-300 words based on the provided background data. Your summary should be factual, concise, and well-structured, avoiding subjective evaluations or assumptions. remove double quotes from result and output  as valid JSON format with tag 'diasngid' and 'summary' 

Instructions:
	•	Focus exclusively on the provided background information. Do not add extra details or references.
	•	Highlight notable achievements, such as highly cited works, “HOT PAPERS,” or “HIGHLY CITED PAPERS.” Avoid mentioning low citation counts or details that imply negative evaluation.
	•	Objectively summarize key metrics, including the number of publications, citation counts, and publication timeline (e.g., spanning decades or recent).
	•	Cover key areas such as education, qualifications, positions held, research focus areas (primary, secondary, interdisciplinary), and significant publications.
	•	Include any impact beyond academia, such as public engagement, industry contributions, or policy influence, if mentioned.
	•	Maintain a natural flow without using headings, and ensure the summary reflects all relevant aspects of the researcher’s contributions.

Background Information:
```

---

### Prompt - Profile Evaluation

```plaintext
As an expert in academic management and research, your task is to evaluate the quality, accuracy, and objectivity of the LLM-generated summaries based solely on the background information provided. Objectively compare the content and structure of the two summary versions by:

Quantifying Similarities and Differences: Identify and measure the degree of similarity and divergence between the two versions.
Highlighting Missing Information: Pinpoint any critical points or information omitted in each version compared to the background data.
Assessing Completeness and Accuracy: Determine which version is more comprehensive and precise in representing the provided background information.
Evaluating Strengths and Weaknesses: Outline the strengths and weaknesses (pros and cons) of each version.
Conclude your analysis by summarizing the relative merits of the two versions and identifying which one is superior in terms of completeness, accuracy, and objectivity.


Background information:

```

### Prompt - Summay of Summary from Breakdown


```plaintext

As an expert in academic research, your task is to summarize an academic researcher's profile based on the background information provided. Focus specifically on the researcher's research areas, interests, achievements, impact, collaborations, reputation, and the evolution of their research focus over time. The summary should be presented in JSON format with all lowercase tags, covering the following key areas:

```


---


## Ranking - Author Profile


### 1. Researcher Ranking Criteria


Here’s a ranking system with 20 levels that evaluates researchers' reputations and impacts based on their academic achievements. Each level includes an appropriate adjective and short description to reflect the academic standing.


*Levels 1–5: Early-Career or Limited Impact*

- **Novice**: Just starting their research career with minimal publications and citations.
- **Aspiring**: A few publications with limited citations; potential for growth evident.
- **Emerging**: Modest publication record and citations, showing early signs of productivity.
- **Developing**: Growing research portfolio with increasing citations; making initial contributions.
- **Budding**: Consistent publishing efforts with a small but noticeable citation base.


*Levels 6–10: Establishing Reputation*

- **Proficient**: A steady stream of publications; citations indicate recognition in the field.
- **Competent**: Building a respectable h-index; contributions gaining moderate attention.
- **Promising**: Work is gaining traction with steady citations; regional or niche recognition.
- **Productive**: Significant output with good citation rates; emerging as a reliable scholar.
- **Accomplished**: Well-rounded research portfolio with evidence of growing impact.


*Levels 11–15: Recognized and Influential*

- **Distinguished**: A strong h-index and citations; recognized for contributions to specific areas.
- **Esteemed**: Well-respected researcher with impactful work and consistent citations.
- **Prominent**: Regularly cited across various publications; influential in subfields.
- **Notable**: Work is recognized as essential reading in the domain; high citations.
- **Influential**: Shaping the direction of research within their area; widely acknowledged.


*Levels 16–20: Renowned and Elite*

- **Renowned**: Widely known across the field; high citation rates and a significant h-index.
- **Pioneering**: Groundbreaking research that redefines paradigms; exceptional impact.
- **Preeminent**: Among the top researchers globally; work is foundational in the field.
- **Trailblazing**: Leading research that sets benchmarks for excellence and innovation.
- **Legendary**: Universally recognized as a luminary; unparalleled achievements in academia.


*Ranking by 20 levels*


| **Level** | **Title**        | **Description**                                                                                     |
|-----------|------------------|-----------------------------------------------------------------------------------------------------|
| 1         | Novice           | Just starting their research career with minimal publications and citations.                       |
| 2         | Aspiring         | A few publications with limited citations; potential for growth evident.                          |
| 3         | Emerging         | Modest publication record and citations, showing early signs of productivity.                     |
| 4         | Developing       | Growing research portfolio with increasing citations; making initial contributions.                |
| 5         | Budding          | Consistent publishing efforts with a small but noticeable citation base.                          |
| 6         | Proficient       | A steady stream of publications; citations indicate recognition in the field.                     |
| 7         | Competent        | Building a respectable h-index; contributions gaining moderate attention.                         |
| 8         | Promising        | Work is gaining traction with steady citations; regional or niche recognition.                    |
| 9         | Productive       | Significant output with good citation rates; emerging as a reliable scholar.                     |
| 10        | Accomplished     | Well-rounded research portfolio with evidence of growing impact.                                  |
| 11        | Distinguished    | A strong h-index and citations; recognized for contributions to specific areas.                   |
| 12        | Esteemed         | Well-respected researcher with impactful work and consistent citations.                           |
| 13        | Prominent        | Regularly cited across various publications; influential in subfields.                           |
| 14        | Notable          | Work is recognized as essential reading in the domain; high citations.                           |
| 15        | Influential      | Shaping the direction of research within their area; widely acknowledged.                        |
| 16        | Renowned         | Widely known across the field; high citation rates and a significant h-index.                    |
| 17        | Pioneering       | Groundbreaking research that redefines paradigms; exceptional impact.                            |
| 18        | Preeminent       | Among the top researchers globally; work is foundational in the field.                           |
| 19        | Trailblazing     | Leading research that sets benchmarks for excellence and innovation.                             |
| 20        | Legendary        | Universally recognized as a luminary; unparalleled achievements in academia.                     |



*Ranking by 10 levels*

| Level | Title         | Description                                                        |
|-------|---------------|--------------------------------------------------------------------|
| 1     | Novice        | Just beginning their research journey with minimal publications and impact. |
| 2     | Emerging      | Starting to publish with some initial recognition.                |
| 3     | Developing    | Steady publication record with growing citations.                 |
| 4     | Proficient    | A consistent researcher with moderate recognition in the field.   |
| 5     | Accomplished  | Well-established in the field with significant contributions and citations. |
| 6     | Distinguished | Recognized for impactful work with a strong citation record.      |
| 7     | Prominent     | Highly respected for influential research in their domain.        |
| 8     | Renowned      | A leading figure in the field with exceptional achievements.       |
| 9     | Trailblazing  | Redefining the field through innovative and groundbreaking work.  |
| 10    | Legendary     | Universally celebrated for unparalleled contributions to academia.|


---

### 2. Steps to Divide Total Times Cited into Groups


Dividing the range of total times cited into groups that represent authors of similar impact and productivity requires a thoughtful approach. A reasonable method is to use percentile-based binning, logarithmic scales, or domain-specific thresholds. Here's how you can do this:


1. Understand the Distribution:

- Examine the distribution of citation counts across all authors.
- Determine if the data is skewed (e.g., many authors with few citations and a few with very high citations).

2. Choose Grouping Method:

- Percentile-Based: Group authors based on citation percentiles, which ensures an even distribution of authors in each group.
- Logarithmic Binning: If citation counts are skewed, use logarithmic bins to better reflect the distribution of influence.
- Custom Thresholds: Set thresholds manually based on domain expertise or notable ranges, such as "0–10," "11–100," etc.

3. Define Groups: For simplicity, here’s a 10-group structure for "Total Times Cited":

| Author    | TotalCitations | CitationGroup                     |
|-----------|----------------|------------------------------------|
| Author A  | 0              | Group 1: No citations            |
| Author B  | 45             | Group 3: Modest impact           |
| Author C  | 150            | Group 5: Moderate impact         |
| Author D  | 1200           | Group 7: Highly productive       |
| Author E  | 52000          | Group 10: Exceptional impact     |


---

### 3. Steps to Divide Total Publication Count into Groups

To divide the range of the total number of publications into reasonable groups representing similar impactful and productive authors, you can consider several approaches based on the distribution of publication counts and the characteristics of your dataset. Here’s a general methodology:


1. Analyze the Distribution
- Histogram Analysis: Plot the histogram of publication counts to identify natural groupings (e.g., clusters, outliers).
- Percentiles: Calculate percentiles (e.g., 25th, 50th, 75th) to group authors into quartiles or other meaningful segments.

2. Define Categories
You can divide authors into categories based on their productivity and likely impact. Here is a reasonable example:

**Example Grouping:**

2.1. Emerging Authors:
  - Range: 1–10 publications.
  - Description: Early-career researchers or those with niche contributions.

3.2.Moderately Productive Authors:
  - Range: 11–50 publications.
  - Description: Researchers with consistent output in their field, likely mid-career or active in interdisciplinary work.

2.3. Highly Productive Authors:
  - Range: 51–100 publications.
  - Description: Established researchers with significant contributions, often leaders in their domain.

2.4. Prolific Authors:
  - Range: 101–200 publications.
  - Description: Senior researchers with a long career of sustained productivity or working in collaborative, high-output fields.

2.5. Elite Authors:
  - Range: 200+ publications.
  - Description: Exceptional output, often collaborative, with a significant global impact.


3. Adjust for Field-Specific Variations
   
Certain fields like physics or genomics may have high publication counts due to the nature of collaboration, while others like history or philosophy may have lower counts due to longer publication cycles. Adjust the ranges accordingly to reflect discipline-specific norms.


4. Use Clustering Algorithms

For large datasets, statistical methods like clustering can help define groups:

- K-means Clustering: Group authors by their total publications.
- Hierarchical Clustering: Allows visualization of how groups are formed, especially if there are natural breaks in publication counts.

5. Example Python Implementation

Here’s an example using Python to divide authors into groups:

```python
import pandas as pd
import numpy as np

# Sample data
data = {'author': ['Author A', 'Author B', 'Author C', 'Author D'],
        'total_publications': [5, 45, 120, 300]}
df = pd.DataFrame(data)

# Define bins and labels
bins = [0, 10, 50, 100, 200, np.inf]
labels = ['Emerging', 'Moderately Productive', 'Highly Productive', 'Prolific', 'Elite']

# Categorize authors
df['category'] = pd.cut(df['total_publications'], bins=bins, labels=labels)

print(df)

```


| Author     | Total Publications | Category              |
|------------|--------------------|-----------------------|
| Author A   | 5                  | Emerging              |
| Author B   | 45                 | Moderately Productive |
| Author C   | 120                | Highly Productive     |
| Author D   | 300                | Elite                 |



6. Validation
   
Validate these ranges by cross-referencing:

- Average h-index or citation count for each group.
- Subjective expert opinion or domain-specific insights.

By defining groups in this structured way, you can better analyze and rank researchers based on their productivity and impact.