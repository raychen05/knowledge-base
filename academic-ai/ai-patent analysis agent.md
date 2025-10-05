## Patent Analysis Agent


Designing an AI agent for patent analysis focused on academic researchers or organizations involves combining traditional patent analytics with the unique context of academic output, innovation trajectory, and interdisciplinary research. Below is a list of LLM-powered features categorized by capabilities the AI agent can provide:

---

### 🧠 Top Features of a Patent Analysis AI Agent for Academic Researchers/Organizations (LLM-Powered)

1. Patent Portfolio Summary

- 	What it does: Summarizes the scope, topics, and novelty of an organization’s or researcher’s patent holdings.
- 	LLM Power: Generate plain-language summaries from IPC/CPC codes, claims, and abstract.
- 	Prompt Example:
“Summarize the core technological areas and key innovations represented in this researcher’s patent portfolio.”

---

2. Patent-Publication Linkage

- 	What it does: Matches patents with relevant academic publications by the same researcher or institution.
- 	LLM Power: Match through semantic similarity, citation patterns, and abstract interpretation.
- 	Prompt Example:
“Identify and explain the overlap between this researcher’s publications and their patent filings.”

---

3. Novelty & Innovation Analysis

- 	What it does: Determines how novel or disruptive a patent is compared to prior art and existing academic knowledge.
- 	LLM Power: Compare semantic distance between patent claims and known literature/patents.
- 	Prompt Example:
“Analyze how novel this patent is compared to existing work in the field of nanomedicine.”

---

4. Technology Trend Mapping

- 	What it does: Maps the organization’s or lab’s patent activities onto emerging technology areas.
- 	LLM Power: Cluster and label patents into emerging domains using natural language understanding.
- 	Prompt Example:
“Classify these 20 patents into technology domains and identify any emerging trends.”

---

5. Competitor / Collaborator Patent Overlap

- 	What it does: Finds overlapping or complementary patent areas between the target and other academic or industry players.
- 	LLM Power: Semantic comparison of claim text, keywords, inventors, and citations.
- 	Prompt Example:
“Compare the patent portfolios of Stanford University and MIT in quantum computing. Where do they overlap or diverge?”

---

6. Commercial Potential & Application Mapping

- 	What it does: Maps patents to potential real-world applications, markets, and industries.
- 	LLM Power: Interpret patent claims and associate with downstream applications or products.
- 	Prompt Example:
“Given these 5 biosensor-related patents, identify likely commercial applications and markets.”

---

7. Patent Claim Simplification

- 	What it does: Translates dense legal/technical patent language into layman’s terms.
- 	LLM Power: Simplify claims, compare versions, highlight key points.
- 	Prompt Example:
“Rewrite these patent claims in simple language for a general scientific audience.”

---

8. Inventor Contribution Attribution

- 	What it does: Understand individual researcher contributions in co-invented patents.
- 	LLM Power: Analyze co-patenting behavior, publication roles, and citation context.
- 	Prompt Example:
“Analyze which co-inventor likely contributed to the deep learning method described in this patent.”

---

9. Citation-Based Influence Analysis

- 	What it does: Evaluates the influence and reach of a patent via forward/backward citations and academic references.
- 	LLM Power: Interpret citation patterns and summarize influence narratives.
- 	Prompt Example:
“Explain the impact and influence of this 2015 robotics patent based on its citation network.”

---

10. Funding to Patent Pathway Analysis

- 	What it does: Connects research grants to resulting patents.
- 	LLM Power: Link proposals and funding abstracts to patent claims using topic modeling and semantic analysis.
- 	Prompt Example:
“Trace how this NSF grant led to the development of the following patent. What innovations bridge the two?”

---

11. Time-Series Patent Evolution Analysis

- 	What it does: Analyzes how a researcher’s patent topics evolve over time.
- 	LLM Power: Cluster patents chronologically and summarize technological trajectory.
- 	Prompt Example:
“Analyze the evolution of this lab’s patents from 2010 to 2024 and describe the main technological shifts.”

---

12. Patent Quality and Risk Assessment

- 	What it does: Estimates the strength, defensibility, and litigation risk of a patent.
- 	LLM Power: Evaluate clarity, breadth, uniqueness of claims, and identify potential infringements.
- 	Prompt Example:
“Assess the defensibility of this patent in the area of CRISPR genome editing.”

---

13. Academic-Industry Patent Translation

- 	What it does: Identifies which academic patents are being cited in industry patents (tech transfer pipeline).
- 	LLM Power: Bridge academic and commercial language, identify tech flow pathways.
- 	Prompt Example:
“Which of these university-filed patents have influenced industry players in medical AI?”

---

14. Global Filing Strategy Insights

- 	What it does: Offers analysis of filing behavior across jurisdictions (e.g., PCT, USPTO, EPO, CNIPA).
- 	LLM Power: Infer international commercialization intent from patent family patterns.
- 	Prompt Example:
“Analyze the global strategy of this research group based on their patent filing across jurisdictions.”

---

15. LLM-Powered Patent Search Assistant

- 	What it does: Interactive assistant that answers natural language queries about patents.
- 	LLM Power: Semantic retrieval, reasoning over large patent databases.
- 	Prompt Example:
“Show me patents by this university in photonic quantum computing filed since 2018 with high citation counts.”


---


### LLM prompt Templates for Patent Analysis 


Here is a list of LLM prompt templates—one for each of the 15 key features of a Patent Analysis AI Agent focused on academic researchers or organizations. Each template is designed to work in LLM tools like ChatGPT, LangChain prompt nodes, or RAG chains.

---

🔍 1. Patent Portfolio Summary



```plaintext
You are a patent analyst. Summarize the main technological domains, innovation focus, and key strengths of the following researcher’s or organization’s patent portfolio. Highlight unique contributions and innovation areas.

PATENTS:
{{list_of_patents}}  (Include titles, abstracts, claims, CPC codes if available)
```


---

🔗 2. Patent-Publication Linkage



```plaintext
Match each patent below with related academic publications by the same researcher. Highlight overlapping methods, technologies, or concepts.

PATENTS:
{{patent_abstracts}}

PUBLICATIONS:
{{publication_titles_and_abstracts}}
```


---

🧪 3. Novelty & Innovation Analysis



```plaintext
Analyze the novelty and uniqueness of the following patent. Compare it against existing academic literature or known technologies. What makes this invention different?

PATENT:
{{title}}, {{abstract}}, {{claims}}, {{prior_art_refs (optional)}}
```

---

📈 4. Technology Trend Mapping



```plaintext
Categorize these patents into technology areas and identify any emerging trends or shifts in innovation focus. Group similar patents together.

PATENTS:
{{patent_list}}
```

---

🤝 5. Competitor / Collaborator Patent Overlap



```plaintext
Compare the patent portfolios of the following two academic institutions or research groups. Where do they overlap in research focus or technology? Where are they differentiated?

ENTITY A PATENTS:
{{patents_entity_a}}

ENTITY B PATENTS:
{{patents_entity_b}}
```


---

💰 6. Commercial Potential & Application Mapping



```plaintext
Identify real-world commercial applications and potential industries for each of the following patents. Suggest possible use cases and product categories.

PATENTS:
{{patent_titles_and_abstracts}}

```

---

📝 7. Patent Claim Simplification



```plaintext
Simplify the following patent claims for a non-technical audience. Retain the core technical idea while removing legal jargon.

CLAIMS:
{{claim_text}}
```


---

👥 8. Inventor Contribution Attribution



```plaintext
Given this multi-inventor patent, estimate the likely contributions of each co-inventor. Use the content of the patent, related publications, and inventor background.

PATENT:
{{title}}, {{abstract}}, {{claims}}

INVENTORS:
{{inventor_list}}, with optional bios or publication record
```

---

🔗 9. Citation-Based Influence Analysis. 



```plaintext
Analyze the influence and impact of the following patent based on forward citations, backward citations, and referenced literature. Explain the technological reach.

PATENT:
{{title}}, {{citation_data}}, {{cited_by_patents}}
```

---

🎯 10. Funding to Patent Pathway Analysis



```plaintext
Trace the connection between this research grant and the resulting patents. Identify shared themes, methodologies, or outcomes that link them.

GRANT ABSTRACT:
{{grant_text}}

RELATED PATENTS:
{{patent_titles_and_abstracts}
```

---

⏳ 11. Time-Series Patent Evolution Analysis



```plaintext
Analyze how the researcher’s or lab’s patent portfolio has evolved over time. Describe key shifts in research topics or technological focus from {{start_year}} to {{end_year}}.

PATENTS:
{{list_of_patents_with_filing_dates}}
```


---

⚖️ 12. Patent Quality and Risk Assessment



```plaintext
Assess the legal and technical strength of this patent. Consider scope, clarity, novelty, and potential litigation risk.

PATENT:
{{title}}, {{abstract}}, {{claims}}, {{citations}}, {{jurisdiction}}
```

---

🏭 13. Academic-Industry Patent Translation




```plaintext
Identify which patents filed by this university have been cited in industry patents. Describe the academic-to-industry knowledge flow.

UNIVERSITY PATENTS:
{{academic_patents}}

CITED BY (optional):
{{industry_patents}}
```

---

🌍 14. Global Filing Strategy Insights



```plaintext
Analyze the patent filing strategy of this researcher or organization across different jurisdictions. What can you infer about their commercialization or global strategy?

PATENT FAMILY DATA:
{{patents_with_filing_countries_and_dates}}
```

---

🧾 15. LLM-Powered Patent Search Assistant



```plaintext
You are an expert patent search assistant. Return a list of patents that match the following query. Include title, filing date, assignee, and a brief description.

QUERY:
{{natural_language_query}}

FILTERS:
{{optional_filters_like_date_range, keywords, assignee, inventor}}
```