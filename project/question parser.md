## Parse Analytical Question 


--- 

### txt2sql vs. NER

Both Text-to-SQL (txt2sql) and Named Entity Recognition (NER) have distinct purposes, and which one is better for analyzing analytical questions in an LLM depends on the task requirements. Let’s break down both approaches in the context of analytical question processing:

---

### Text-to-SQL (txt2sql)

What it does: Text-to-SQL converts natural language questions into SQL queries. It’s used when the goal is to query databases directly based on natural language inputs.

#### Pros:

- Direct database querying: Allows you to run SQL queries directly on a structured database based on user input, which can be useful if the questions are meant to extract data from a database.
- Highly structured output: Once the SQL query is generated, it's easy to run it against a database to get results.
- Handles complex queries: It can manage questions involving filtering, grouping, or other logical SQL operations, providing direct insights from data.
  
#### Cons:

- Limited flexibility: Works well only for structured data that can be queried via SQL. If your data is unstructured (e.g., documents or text), txt2sql will be less effective.
- Complex question handling: For complex multi-step or ambiguous questions, txt2sql might struggle without further refinement.
- Training complexity: Requires a robust model that has been trained on diverse SQL queries, which can be difficult for highly domain-specific databases.

---

### Named Entity Recognition (NER)

What it does: NER identifies specific entities (e.g., people, organizations, dates, metrics) in text. In the context of analytical questions, NER is used to extract relevant entities (e.g., "MIT" as an organization, "funding" as a metric).

#### Pros:

- Entity extraction: Very effective for recognizing and extracting key entities (e.g., organizations, locations, metrics), which are essential in many analytical questions.
- Flexible: Can be applied to both structured and unstructured data, making it more versatile than txt2sql.
- Preprocessing for other tasks: NER can be used to identify relevant entities that can later be fed into a more structured query (e.g., SQL or a knowledge graph).

#### Cons:

- Not a complete solution: While NER can help identify key parts of a question, it doesn’t generate a full query like txt2sql. Additional steps are needed to convert the entities into a usable format (e.g., SQL or API queries).
- Ambiguity handling: NER might struggle with complex or ambiguous questions where entities are not explicitly mentioned.
- Entity limit: NER models are only as good as the entities they are trained on. It can miss out on domain-specific terms if not properly trained.

---

### Which is better for analyzing analytical questions?


#### For direct database querying and structured outputs:

Text-to-SQL is better if the goal is to translate analytical questions into SQL queries to retrieve data directly from a database. It provides a structured query format and is more suitable if the answers to the questions are in structured relational databases.

#### For flexible, entity-driven analysis:

NER is better if the goal is to extract key information from questions and then use that to drive further logic or queries (not necessarily in SQL). If the analysis involves working with unstructured data or requires further interpretation (e.g., identifying a metric and then running logic based on it), NER will be more flexible.

---

### Conclusion:

- If you need to transform natural language questions into SQL queries, txt2sql is the better approach.
- If you need to extract entities from questions for further analysis, integration, or use in different query formats (e.g., API calls, NoSQL queries), NER will provide more flexibility.
- It’s often useful to combine both: NER can extract entities, and then txt2sql can use those entities to form database queries.


---


### Prompt  for Quation Analysis

```plaintext

Perform named entity recognition on the question and identify groupby, period, metric and take, and label the following fields and output JSON object with question directly.
  
  groupby: people, organization, location, subject, journal, funder. subject when  topics, categories or researches etc. are mentioned as main focus.
  
  Filter fields:
  clbrorgname: An organization that collaborates with or partner for the primary entity. 
  clbrlocname: A location  that collaborates with the primary entity.
  clbauthorprofile: A people that collaborates with the primary entity.
  clbrfunder: a list of funders or funding agencies collaborate with.
  orgname: A specific organization or entity primarily focused on conducting research, employing researchers, publishing papers, and may also receive external funding.
  orgtype: organization type refers to the classification of an organization, MUST be value from the list: 'Academic', 'Academic System', 'Global Corporate', 'Corporate', 'Government', 'Health', 'Healthcare System', 'National Academy', 'Nonprofit', 'Partnership', 'Research Council' or 'Research Institute'.  Extract 'Academic' when 'universities' or 'colleges' is  mentioned. Drop values which are not in the list.
  personId: A specific people or entity.
  location: A specific geographic region where organizations or research entities are based. such as a country, state, province, NUTS code. 
  sbjname: the field of research or topics covered in the journal.
  jrnname: specific journals, or a scholarly periodical, where research articles, papers, or reviews are published, which could includes the words 'journal', 'magazine', or 'proceedings' etc. .  Extract the value in capital letters.
  jrncountry: country of the journal.
  funder: A specific organization or entity primarily dedicated to distributing grants or funding research projects.
  funderLocation: A special country or region where funders or funding agencies are based. Prioritize this field over `location` if the question refers to funders, funding agencies, or research funding.
  funderType: Funded, Published, Funded or Published, when groupby is 'funder' and funder type is explicitly requested.
  publisher: specific publishers of publications, Journals  and books.
  highly_cited: 1 if the term 'highly cited' is mentioned. '"highly cited paper"' is not jornal name.
  schema: WOS, GIPP, SDG, Citation Topic-Macro, Citation Topic-Meso, Citation Topic-Micro,  (default is WOS if not specified).
  authorposition: First, Last  or Corresponding;  if first author, last author or corresponding author is mentioned.
  citedOrCiting: citing if 'citing' is mentioned, cited if 'cited' is mentioned.
  
  period: Extract the start and end year pair from the input. For phrases similar to 'last X years,' use full years only, excluding the current year 2024. If a single year is provided, assign the same year to both start and end. Notice that start and end are included so the difference between the two edges of X year period should be X-1. If no period or year is specified, do not extract period.

  take: number of entities when it's explicitly requested, for example, extract 20  from 'list top 20 researchers', extract null from  'list top researchers'.
  trend: 1 if a period of time is mentioned, e.g. the trend-related terms like 'yearly', 'over',  'increasing' or 'trend', "last 3 years" is mentioned.
  pinned: 1 if the term 'compare' is mentioned and take is specified and greater than {default_take}.
  
  articletype: a list of article type, e.g. Article, Book Series, etc.
  association: a list of association names, e.g. AUSTRALIA: ATN, CHINA MAINLAND: 211 UNIV, SOUTH KOREA: PUBLIC UNIV, CHINA MAINLAND: C9, etc.
  authorcount: number of authors in a single article.
  geographicCollabType: All, Domestic, International  when collabnoration type is explicitly requested.
  clbrprsnId: a list of people collaborated with.
  earlyAccess: 1 if early access is present or 0 if not.
  grantEndFnd: grant end date.
  grantNumber: a list of grant number.
  grantStartFnd: grant start date.
  issn: a list of ISSN, eISSN, or ISBN.
  jciQuartile: a list of Quartile value: Q1, Q2, Q3, Q4.
  jrnQuartile: a list of Quartile value: Q1, Q2, Q3, Q4.
  jrn_source_type: a list of journal types: Journal, Books, Book Series, Conference Proceedings.
  countrytype: location type, mandatory for 'location',  select one option from the following array: {location_types}. output 'Country/Region' if 'countries' is mentioned

  openaccess: open access type, required only when open acces type is explicitly requested, MUST select from the following array: ['All Open Access', 'Non-Open Access', 'Gold', 'Gold - Hybrid', 'Free to Read', 'Green Submitted', 'Green Published', 'Green Accepted', 'Green Only'].
  
  topPercentileDocs: If the query is asking for data explicitly restricted to a percentile of the documents. Then if the query restricts the answer to a percentile, please extract that percentile. For example if it states "please return me the 99th percentile", extract 99. Then if the query restricts the answer the top 10%, please extract 90. For example if it states the "top 10%", extract 90. Then if the query restricts the answer the top 5%, please extract 95. For example if it states the "top 5%", extract 95. Then if the query restricts the answer the top 1%, please extract 99. For example if it states the "top 1%", extract 99. Otherwise extract null.
  
  
Metrics: Perform named entity recognition (NER) on the question to identify metric indicators related to academic performance, research impact, collaboration, funding, or open access. Tag these indicators using appropriate labels and output the JSON object with the question and corresponding metric tag.  Ensure that variations, abbreviations, and synonymous terms are correctly recognized and mapped to their respective metric tag.

    Funding: grantAward, numberOfGrants, currency. Tag grantAward when terms like "funding", "funds", or "research funds" is recognized, numberOfGrants for "grants" is recoginized,.
    Impact:  hindex, timesCited, avrgCitations, norm, jNCI, nonselftimescited, percentCited, impactRelToWorld, avrgPrcnt, nonselftimescited, yearCiting, docsCited, citationsFromPatents. Recognize metrics like "times cited", "citation impact", "H-index", etc.
    Production: highlyCitedPapers, esi, wosDocuments, prcntDocsIn99, docsIn99, prcntDocsIn90, docsIn90, hotPapers, prcntHotPapers, jifdocs, jifdocsq1, percjifdocsq1, jifdocsq2, percjifdocsq2, jifdocsq3, percjifdocsq3, jifdocsq4, percjifdocsq4, prcntHighlyCitedPapers. Recognize metrics like  WoS count, documents in JIF journals, etc.
    Author Position: firstauthor, lastauthor, correspauthor,percfirstauthor, perclastauthor, perccorrespauthor. Recognize First, last, or corresponding author.
    Collaboration: intCollaborations, prcntIntCollab, indCollaborations, prcntIndCollab, countryCollab, prcntCountryCollab, organizationOnly, prcntOrganizationOnly. Recognize metrics like  International, domestic, or industry collaboration.
    Open Access: allopenaccessdocs, percallopenaccess, doajgolddocuments, percdoajgolddocuments, greenpublisheddocuments, percgreenpublisheddocuments, greenaccepteddocuments, percgreenaccepteddocuments, greensubmitteddocs, percgreensubmitteddocs, othergolddocuments, percothergolddocuments, bronzedocuments, percbronzedocuments, greenOnly, prcntGreenOnly, nonOaDocs, prcntNonOaDocs. Recognize metrics like "green OA", "gold OA", etc.
    Baseline share: prcntGlobalBaseDocs, prcntGlobalBaseCites, prcntBaselineAllDocs, prcntBaselineAllCites, prcntBaselineForPinnedDocs, prcntBaselineForPinnedCites.  Recognize metrics like  % Global Baseline (Cites), % Baseline for All Items (Docs), etc.
    JCR:  impactFactor, impactFactor5yr, journalImpFactWoSelfCites, eigenFactor, articleInfluence, jNCI, averagejifpercentile, quartile, jcirank, jcipercentile, jciquartile, jci, jifrank, immediacyIndex, citedHalfLife. Recognize metrics like Impact factor, eigenfactor, article influence, etc.

     If the metric category name (e.g. funding, JCR, impact, etc.) is recognized, output the top 5 metric indicators for that category instead.
     If the metric scope  (e.g.  top 5, top, most important, etc.) is recognized and special category is not specified, output the top 5 impact  indicators  instead.



  Example: What topics are covered in the journal Nature?
  Output:  "groupby": "subject",  "jrnname": { "is": ["Nature"] }
  Example: Which Australian universities work in AI research with Harvard?",
  Output:  "groupby": "organization", "clbrorgname" : { "is"; ["Harvard"] }, "location" : { "not"; ["Australia"] }, "sbjname": { "is": ["AI"] }, orgtype: {'is', ['Academic'] }
  Example: How many partners does Rutgers have in last 5 years?
  Output:  "groupby": "organization", "clbrorgname" : { "is"; ["Rutgers"] }, "period": { "start": 2019, "end": 2023 }, "trend": 1
  Example: How many grants has CGIAR offered ?
  Output:  "groupby": "funder",  "funder": { "is": ["CGIAR"] }
  
  Rules:
  If the logic is NOT, label the field data under the child tag 'not'; otherwise, label the field data under the child tag 'is'. Apply this logic to all fields except to period.
  Example: Which researchers not in Belgium are well-known in the field of AI?
  Output: "groupby": "people", "location" : { "not"; ["Belgium"] }, "sbjname" : { "is"; ["AI"] }

  If 'countrytype' is missing for the 'location', output: "countrytype": "Country/Region".
  If the question mentions funders, funding agencies, or grants, use `funderLocation`.  Otherwise, use `location` for general institutions or geographic references. If `groupby` is set to 'funder', always use `funderLocation`.
  If 'clbrorgname' is extracted for 'funder', it should be classified as 'clbrfunder' instead.
  
  question: {{line}}


```


---

### Example Parser Implementation 


```python

import requests
import os
from colorama import Fore, Style, init


init()
# Define the API endpoint gpt_35_turbo 
url="https://openai/api"

# Define the headers
headers = {
    "Content-Type": "application/json",
    "x-auth-token": ""
}

questions = [
  "Which universities in France have the highest number of documents in top 10% in collaboration with KU Leuven, Belgium?",
  "What are funding amount the funding agency name provide?",
]

# Define the prompt
def read_file_to_string(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content


prompt = read_file_to_string(os.path.join(os.getcwd() , 'prompt.cfg'))

os.system('clear')

# param: "top_p": 0.9, "top_k": 1
for line in questions:
  # print(line)
  data =  {
        "prompt": prompt + line,
        "max_tokens": 4000,
        "temperature": 0,
        "num_results": 1,
        "streaming": 0
      }
  
  # Make the POST request
  response = requests.post(url, headers=headers, json=data)
  json_object = response.json()
  # Process the response and write to the output file
  if 'results' in json_object:
      result = json_object['results'][0]['completion']
  else:
      result = response.text

  print(result)

```


---

### Use Case of Breakdown (Distribution)

| # | Use Case Description | Example 1 | Example 2 |
|---|----------------------|-----------|-----------|
| 1 | User specifies one entity and asks for a breakdown of top N other entities | Show the top 10 research areas associated with MIT. | Provide a breakdown of the top 5 organizations collaborating with Harvard University. |
| 2 | User specifies one entity and asks for a breakdown of the same N entities that the user specified | Show the performance of MIT in the research areas: Artificial Intelligence, Machine Learning, and Data Science. | Provide the funding breakdown for Harvard in the categories: Education, Healthcare, and Technology. |
| 3 | User specifies N entities and asks for a breakdown of top M other entities | Compare MIT and Stanford and show the top 5 research areas each university specializes in. | For Google and Apple, show the top 3 countries where they have the highest number of collaborations. |
| 4 | User specifies N entities and asks for a breakdown of the same N entities that the user specified | Compare the research output of MIT, Stanford, and Harvard in the areas of Artificial Intelligence, Machine Learning, and Data Science. | Provide a funding breakdown for Google, Apple, and Microsoft across the categories: Technology, Healthcare, and Education. |
| 5 | User simply asks for top N entities and a breakdown of M other entities | Show the top 10 organizations and provide a breakdown of their collaborations with the top 5 research areas. | Provide the top 5 research areas and show the top 3 organizations working in those areas. |
| 6 | User simply asks for top N entities and a breakdown of the same M other entities | Show the top 10 organizations and provide a breakdown of their work in those same organizations' top 5 research areas. | Provide the top 5 organizations and show the performance of each in the same 5 categories: Technology, Education, Healthcare, Environment, and Energy. |
| 7 | N research areas by M organizations | Show the top 5 research areas by the organizations MIT, Stanford, and Harvard. | Compare 10 research areas across 5 leading organizations. |
| 8 | N organizations by multiple funders | Show the top 5 organizations funded by the NIH, Wellcome Trust, and Gates Foundation. | Compare 10 organizations and their funding from Wellcome Trust and Horizon 2020. |
| 9 | N funded organizations by multiple funders and country | Show the top 10 organizations funded by the NIH and the EU across the US and the UK. | Compare the top 5 funded organizations from the Gates Foundation across the US, Germany, and Canada. |
