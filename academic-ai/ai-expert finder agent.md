## Expert Finder AI Agent

Designing an Academic Expert Finder AI Agent involves leveraging LLMs and structured academic data (papers, grants, citations, affiliations) to intelligently match users’ needs (e.g., collaborators, reviewers, speakers, mentors) to top experts. Here’s a breakdown of the top LLM-powered features and capabilities that such an agent can support:

---

### 🔍 Top LLM-Powered Features for an Academic Expert Finder AI Agent

1. Expert Matching by Topic or Abstract

- 	Input: Paper title, abstract, or keywords
- 	LLM Role: Semantic parsing of topic, keywords, novelty, and methods
- 	Output: Ranked list of experts based on publication history, impact, and topical relevance

---

2. Contextual Disambiguation of Author Names

- 	Input: Messy author names (e.g., “J Smith”), affiliations, coauthors
- 	LLM Role: Disambiguate author identity using ORCID, institution, coauthors, topics
- 	Output: Canonical author ID or cluster (e.g., “John Smith, Stanford, ORCID: …”)

---

3. Reviewer Recommendation

- 	Input: Manuscript abstract or title
- 	LLM Role: Extract methods, scope, and novelty; filter by expertise and conflict-of-interest
- 	Output: Reviewer candidates with rationale

---

4. Collaboration Partner Suggestion

- 	Input: Target research area or grant idea
- 	LLM Role: Find co-PIs or co-authors with complementary expertise, institutional diversity
- 	Output: Ranked experts and suggested roles (PI, co-PI, method lead)

---

5. Funding-to-Expert Match

- 	Input: Funder call or program announcement
- 	LLM Role: Parse requirements and goals, match with expert portfolios
- 	Output: Experts who fit scope, success history, and innovation goals

---

6. Institutional Expert Landscape

- 	Input: Institution or department name
- 	LLM Role: Summarize research strengths and top researchers
- 	Output: Key experts, focus areas, funding/grant highlights

---

7. Topic Trend and Emerging Expert Analysis

- 	Input: Research area (e.g., “Graph Neural Networks”)
- 	LLM Role: Identify rising stars, new entrants, and early impactful publications
- 	Output: Timeline of expert evolution; senior vs early-career

---

8. Diversity & Inclusion-Aware Expert Search

- 	Input: Topic + inclusion goals (e.g., gender balance, global South)
- 	LLM Role: Reason across metadata and suggest inclusive expert panels
- 	Output: Diverse experts with representation filters

---

9. Explainable Expert Selection

- 	Input: Expert name or selection criteria
- 	LLM Role: Generate rationale for each expert match (e.g., “5 papers on topic, h-index 23”)
- 	Output: Natural language explanation to justify the recommendation

---

10. Expert Cluster Summarization

- 	Input: Cluster of similar experts or co-authors
- 	LLM Role: Summarize shared methods, papers, affiliations, impact
- 	Output: Cluster description, specialization themes

---

11. Graph-Based Reasoning (e.g., Coauthor or Topic Graph)

- 	Input: Graph query (e.g., “shortest coauthor path from A to B”)
- 	LLM Role: Interpret graph relationships, paths, and influence chains
- 	Output: Reasoned paths, network-based recommendations

---

12. Cross-Domain Expert Suggestion

- 	Input: Multidisciplinary topic (e.g., AI + cancer genomics)
- 	LLM Role: Decompose into subdomains, identify experts across fields
- 	Output: Experts per domain and potential interdisciplinary links

---

13. Past Performance-Based Matchmaking

- 	Input: Grant/project description
- 	LLM Role: Match with experts who have led similar successful grants
- 	Output: Experts ranked by fit and past success

---

14. Academic Event Speaker Finder

- 	Input: Event theme, scope, location, diversity criteria
- 	LLM Role: Identify impactful researchers and rising stars
- 	Output: Speaker list with topics, bios, and contact leads

---

15. Expert Availability Estimation (Optional via Profile Analysis)

- 	Input: Target expert name
- 	LLM Role: Estimate availability via publication gaps, job changes, social presence
- 	Output: Engagement likelihood (optional, probabilistic)

---

Would you like:

- 	✅ Example LLM prompts for each feature?
- 	✅ LangChain agent design or tools setup?
- 	✅ Backend data architecture (Elasticsearch, Neo4j, embedding index)?
- 	✅ UI/UX wireframe for the expert search interface?

Let me know and I can deliver the next step.

---


### LLM Prompt Examples 

Here are LLM prompt examples for each of the 15 features in the Academic Expert Finder AI Agent, designed to be used with GPT-style LLMs (e.g., via LangChain, OpenAI function calls, or prompt templates).

---

🔍 1. Expert Matching by Topic or Abstract

Prompt:
```yaml
Given the research abstract below, identify the top 5 academic experts worldwide working on this topic. Justify each selection based on their publications, methods used, and relevance.

Abstract: "{{abstract_text}}"
```

---

👤 2. Contextual Disambiguation of Author Names

Prompt:
```yaml
Disambiguate the author name "{{author_name}}" using the following clues:

Affiliation: {{affiliation}}
Co-authors: {{coauthors}}
Publication title: {{title}}

Return the most likely canonical full name, institution, and ORCID if known.
```


---

🧪 3. Reviewer Recommendation

Prompt:
```yaml
Act as a journal editor. Based on the following manuscript abstract, suggest 3 expert reviewers with relevant expertise and no clear conflict of interest.

Abstract: "{{abstract}}"
Field: "{{field}}"
Exclude: ["{{author_name}}", "{{institution}}"]
```

---

🤝 4. Collaboration Partner Suggestion

Prompt:
```yaml
I'm preparing a research proposal on the following topic:

"{{proposal_title}}"

Based on this, recommend 3 potential collaborators (with complementary expertise) from different institutions. Include a short description of each expert’s relevant background and how they would contribute to the proposal.

```


---

💰 5. Funding-to-Expert Match

Prompt:
```yaml
Analyze this grant call description:

"{{funder_call_description}}"

Suggest 5 academic experts who are well-positioned to apply, based on their past work, funding history, and relevant expertise.
```

---

🏛️ 6. Institutional Expert Landscape

Prompt:
```yaml
Summarize the top research areas and lead researchers from the institution "{{institution_name}}". Focus on their most active or high-impact fields in the past 5 years.
```


---

📈 7. Topic Trend and Emerging Expert Analysis

Prompt:
```yaml
Identify emerging academic experts in the area of "{{research_topic}}" over the past 3 years. List rising researchers with early impactful work, and briefly describe their contributions.
```

---

🌐 8. Diversity & Inclusion-Aware Expert Search

Prompt:
```yaml
Provide a list of diverse experts (gender, geography, and career stage) working in the field of "{{topic}}". Include underrepresented regions or groups where possible.
```

---

🔍 9. Explainable Expert Selection

Prompt:
```yaml
Explain why "{{expert_name}}" is a strong candidate for collaboration on the following research topic: "{{topic}}". Include details like publications, methods, impact, and recent work.

```

---

🔗 10. Expert Cluster Summarization

Prompt:
```yaml
Given the following list of expert names, summarize the shared research themes, methods, and institutions that link them:

["{{expert_1}}", "{{expert_2}}", "{{expert_3}}"]
```

---

🧠 11. Graph-Based Reasoning (Coauthor or Topic Network)

Prompt:
```yaml
Describe the shortest academic coauthor path between "{{Author A}}" and "{{Author B}}". Summarize their research overlap or bridges if any.
```


---

🧬 12. Cross-Domain Expert Suggestion

Prompt:
```yaml
Suggest academic experts from two domains who could collaborate on the following interdisciplinary project:

Project: "{{project_description}}"
Domains: "{{domain_1}}", "{{domain_2}}"
```

---

📊 13. Past Performance-Based Matchmaking

Prompt:
```yaml
Given the following grant proposal description, recommend academic experts who have led similar successful grants before:

Proposal: "{{proposal_abstract}}"
Funder: "{{funder_name}}"
```


---

🎤 14. Academic Event Speaker Finder

Prompt:
```yaml
Find 5 potential keynote speakers for an academic conference on "{{event_topic}}". Ensure diversity in institution and geography. Include one rising star and one industry-affiliated expert if available.
```

---

🕒 15. Expert Availability Estimation

Prompt:
```yaml
Estimate the likelihood that "{{expert_name}}" is currently available or interested in new collaborations. Consider their recent activity, job changes, or sabbaticals.
```
