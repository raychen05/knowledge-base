

## Golden Dataset for DAP


This is a very good and hard question — and it’s exactly the problem where random sampling completely fails.

Below is a practical, scalable strategy that works for 100+ tables, N-to-N relationships, entity–entity, entity–article, and citation graphs, while minimizing orphan data and keeping the golden dataset small.

I’ll give you:
1.	The core principles
2.	A 3-layer selection strategy (what actually works)
3.	A graph-based algorithm (concrete, implementable)
4.	How to apply it to 100+ tables
5.	What to explicitly avoid

This is battle-tested thinking for complex research / WoS-style data.

---

### 1. Core Principles (Non-Negotiable)


#### Principle 1: Think in GRAPHS, not TABLES

Your system is:
- 	Entities ↔ Entities
- 	Entities ↔ Articles
- 	Articles ↔ Articles (citations)

That is a graph, not relational rows.


✅ Golden data must be graph-connected, not evenly sampled.


---


#### Principle 2: Coverage > Volume

Your goal is relationship coverage, not row count.

A dataset with:
- 	200 rows
- 	Fully connected

Is infinitely more valuable than:
- 	50k rows
- 	70% orphaned


---


#### Principle 3: Start from “Anchor Nodes”

You cannot sample all tables equally.

You must start from high-value anchor entities and expand outward.


---

### 2. The 3-Layer Effective Subset Strategy (Recommended)


#### Layer 1: Anchor Selection (Very Small)

Select a tiny number of anchors that:
- 	Participate in MANY relationships
- 	Touch MANY tables

Examples:

- 	5–10 articles with:
  - 	Multiple authors
  - 	Multiple affiliations
  - 	Multiple citations
- 	5–10 entities with:
  - 	Multiple roles (author + org + funder)

These anchors are your “graph roots”.


---

#### Layer 2: Relationship Closure (Critical Step)

For each anchor:
- 	Include **ALL directly connected records**

This means:
- 	All linking tables
- 	All referenced entities
- 	All reverse relationships

⚠️ This is where most teams fail — they only pull one direction.


---


### Layer 3: Controlled Expansion (Bounded BFS)

From the anchor:
- 	Expand 1–2 hops max
- 	Stop expansion when:
- 	Relationship already covered
- 	Cardinality exceeds threshold

This preserves connectivity without explosion.


---

### 4. Graph-Based Algorithm (Concrete & Implementable)


#### Step 1: Build a Logical Relationship Graph (Metadata Only)

Create a map like:

```yaml
Article
 ├─ article_author → Author
 ├─ article_org → Organization
 ├─ article_citation → Article
 ├─ article_subject → Subject
Author
 ├─ author_org → Organization
Organization
 ├─ org_parent → Organization
```


This can be:
- 	YAML
- 	JSON
- 	Config table

---

#### Step 2: Select Anchor IDs

Criteria:
- 	High degree (many relationships)
- 	Realistic production patterns

Example:

```yaml
anchors:
  articles: 10
  authors: 5
  organizations: 5
```

---

#### Step 3: Relationship Closure Algorithm (Pseudo)

```python
queue = anchor_ids
visited = set()

while queue not empty:
  node = queue.pop()

  if node in visited:
    continue

  visited.add(node)

  for each relationship from node:
    fetch related records
    add to golden dataset

    if depth < MAX_DEPTH:
      queue.add(related_node)
```

**Constraints**
- 	MAX_DEPTH = 2
- 	MAX_ROWS_PER_TABLE = 100–500
- 	Always include both sides of link tables

---

### Step 4: Orphan Elimination Rule (Mandatory)

For every foreign key:
- 	If referenced ID is included → OK
- 	If not → pull the parent row

This rule alone removes 90% of orphan issues.


---

### 4. Table Coverage Strategy for 100+ Tables


Tier Tables (How to Decide What to Include)

Tier 1 – Always Include
- 	Entity master tables
- 	Article master
- 	Citation table
- 	All N-to-N link tables

Tier 2 – Include If Referenced
- 	Metrics
- 	Attributes
- 	Derived indicators
- 	Department / hierarchy tables

Tier 3 – Exclude by Default
- 	Historical snapshots
- 	Large denormalized aggregates
- 	Raw ingestion audit tables

This keeps the dataset small and meaningful.


---


### 5. Practical Heuristics That Work


#### Heuristic 1: “One of Each Pattern”

Ensure at least one example of:
- 	Many-to-many
- 	Self-join (citations, org hierarchy)
- 	Optional relationship (null FK)
- 	Late-arriving update

---

#### Heuristic 2: Cap Fan-Out Aggressively

If an article has:
- 	500 citations → keep only 5–10
- 	100 authors → keep 5–10

Maintain structure, not scale.

---

### Heuristic 3: Deterministic Selection

Always pick:
- 	Lowest PKs
- 	Earliest dates
- 	Stable hashes

So the dataset does not change across runs.


---


### 6. What to Explicitly Avoid (Common Failures)


- ❌ Random sampling per table
- ❌ Percentage-based sampling
- ❌ Time-window slicing only
- ❌ Isolated table “unit test data”
- ❌ Including metrics without parents

These guarantee orphan data in graph systems.


---


### 7. Outcome You Should Expect

With this approach you get:
- 	< 5 MB golden dataset
- 	90–95% relationship coverage
- 	Minimal orphans
- 	Full workflow execution across 20+ pipelines
- 	Deterministic, repeatable validation


---


### 8. Why This Works for Automated Pipelines

Because:
- 	Automation breaks on relationships, not rows
- 	Workflow bugs appear at join points
- 	Incremental logic fails on graph edges

Golden data must therefore stress edges, not volume.

---

If you want, next I can:
- 	Provide a golden-data extraction SQL template
- 	Design a relationship-config YAML for your system
- 	Show how to validate “no orphan” as a test
- 	Map this into your Databricks Workflow automation

---


### What “< 5 MB total” Actually Means

It is the total physical size of all golden test data used in one end-to-end run, including:
- 	Entity master tables
- 	Article tables
- 	N-to-N link tables
- 	Citation tables
- 	Derived / metric tables (if included)

Think of it as:

```yaml
Golden Dataset = UNION(
  entities
  + articles
  + entity–entity links
  + entity–article links
  + citations
  + small derived tables
)
→ total on disk / in Delta / in memory < ~5 MB
```

Not:
- 	❌ 5 MB per table
- 	❌ 5 MB per entity type
- 	❌ 5 MB per article

---

### Why the Limit Is on the TOTAL Dataset


#### 1. Runtime Guarantee

Keeping everything under ~5 MB ensures:
- 	Spark jobs start instantly
- 	No shuffle stress
- 	Full workflow finishes in < 10 minutes

This is critical for:
- 	CI
- 	Pre-commit checks
- 	UAT gates

---

#### 2. Determinism & Debuggability

Small total size means:
- 	You can diff full outputs
- 	You can inspect raw rows
- 	Failures are obvious and explainable

Once the dataset grows larger, signal-to-noise collapses.


---

#### 3. Relationship Coverage Does NOT Require Volume

For graph systems:
- 	1 article with 5 authors covers N-to-N logic
- 	1 citation loop covers recursive logic
- 	1 org hierarchy covers parent/child logic

You’re testing edges, not scale.

---

### How This Translates to Record Counts (Typical)

A realistic < 5 MB golden dataset might look like:


| Table Type | Approx Rows |
|---|---|
| Articles | 50–100 |
| Authors | 50–150 |
| Organizations | 20–50 |
| Entity–Article links | 200–500 |
| Entity–Entity links | 100–300 |
| Citations | 100–300 |
| Metrics / attributes | 200–500 |
| **Total rows (all tables)** | **~1k–3k** |


Even with 100+ tables, most tables will have:
- 	0–20 rows
- 	Only when referenced

---

### Rule of Thumb (Use This)

If you cannot open the entire golden dataset locally and understand it in 5–10 minutes, it is too big.


---


### When You Might Exceed 5 MB (Rare, Controlled)

You may allow 10–20 MB temporarily if:
- 	You are testing performance regressions
- 	You are validating partitioning logic
- 	You are testing ES bulk indexing behavior

But that is not a golden test — that’s a performance or soak test.


---

### Final Clarification

- ✔ 5 MB = total combined dataset size
- ✔ Covers all entities, articles, links, citations
- ✔ Optimized for correctness, automation, and speed

Anything larger:
- 	Slows releases
- 	Reduces clarity
- 	Adds little correctness value

---

If you want, I can:
- 	Help you estimate size before extraction
- 	Define hard caps per table type
- 	Provide a script to measure golden dataset size
- 	Suggest a two-tier golden + extended test model


---


## Golden-data extraction SQL template


Perfect — let’s create a practical, implementable package for your Databricks + Delta + ES multi-pipeline system, covering golden data extraction, relationship config, orphan validation, and workflow integration. I’ll provide this in a structured, actionable way.



### 1️⃣ Golden-Data Extraction SQL Template


**Goal**: Extract a small, deterministic subset of production data that preserves cross-table relationships and edge cases.


```sql

-- Example: Extract golden data for articles, authors, orgs, citations

-- 1. Anchor articles
CREATE OR REPLACE TABLE golden_articles AS
SELECT *
FROM prod.article
WHERE article_id IN (SELECT article_id FROM prod.article ORDER BY article_id LIMIT 10);

-- 2. Related authors (N-to-N)
CREATE OR REPLACE TABLE golden_article_author AS
SELECT aa.*
FROM prod.article_author aa
JOIN golden_articles ga ON aa.article_id = ga.article_id;

-- 3. Related authors
CREATE OR REPLACE TABLE golden_authors AS
SELECT a.*
FROM prod.author a
JOIN golden_article_author gaa ON a.author_id = gaa.author_id;

-- 4. Related organizations
CREATE OR REPLACE TABLE golden_organizations AS
SELECT o.*
FROM prod.organization o
JOIN golden_authors ga ON o.org_id = ga.org_id;

-- 5. Related citations (article -> article)
CREATE OR REPLACE TABLE golden_citations AS
SELECT c.*
FROM prod.citation c
JOIN golden_articles ga ON c.cited_article_id = ga.article_id
   OR c.citing_article_id = ga.article_id;

-- 6. Optional: related metrics
CREATE OR REPLACE TABLE golden_article_metrics AS
SELECT m.*
FROM prod.article_metrics m
JOIN golden_articles ga ON m.article_id = ga.article_id;
```


**Notes**:
- 	Use LIMIT or deterministic anchor IDs for reproducibility.
- 	Always include 1–2 hop relationships to cover N-to-N edges.


---


### 2️⃣ Relationship-Config YAML Template

**Goal**: Define the pipeline’s entity relationships in a reusable config.


```yaml

entities:
  article:
    primary_key: article_id
    links:
      - table: article_author
        fk: article_id
        target: author
      - table: citation
        fk: citing_article_id
        target: article
      - table: citation
        fk: cited_article_id
        target: article
      - table: article_metrics
        fk: article_id
        target: metrics

  author:
    primary_key: author_id
    links:
      - table: article_author
        fk: author_id
        target: article
      - table: author_org
        fk: author_id
        target: organization

  organization:
    primary_key: org_id
    links:
      - table: author_org
        fk: org_id
        target: author
      - table: org_hierarchy
        fk: parent_org_id
        target: organization
```


**Usage**:
- 	Used by extraction scripts to automatically expand relationships for golden dataset.
- 	Ensures all foreign keys have parent rows included.

---


### 3️⃣ “No Orphan” Validation Test


**Goal**: Ensure every foreign key in the golden dataset has a matching parent row.


```sql
-- Example: Check article_author -> authors
SELECT aa.author_id
FROM golden_article_author aa
LEFT JOIN golden_authors a ON aa.author_id = a.author_id
WHERE a.author_id IS NULL;

-- Example: article_author -> article
SELECT aa.article_id
FROM golden_article_author aa
LEFT JOIN golden_articles a ON aa.article_id = a.article_id
WHERE a.article_id IS NULL;

-- Example: article -> citation (citing)
SELECT c.citing_article_id
FROM golden_citations c
LEFT JOIN golden_articles a ON c.citing_article_id = a.article_id
WHERE a.article_id IS NULL;

-- Example: article -> citation (cited)
SELECT c.cited_article_id
FROM golden_citations c
LEFT JOIN golden_articles a ON c.cited_article_id = a.article_id
WHERE a.article_id IS NULL;
```

**Pass criteria**: Query returns 0 rows for all foreign key checks.

---


### 4️⃣ Mapping into Databricks Workflow Automation


#### Step 1: Create a dedicated Golden-Data Job

- 	Job parameters:

```yaml
job_name: golden_data_extraction
run_mode: golden
output_schema: golden_schema

```

- 	Tasks:
1.	Load anchor IDs from config or YAML
2.	Run extraction SQLs for all entities and link tables
3.	Run orphan validation checks (above SQL)
4.	Write expected outputs to golden_expected_results table

---


#### Step 2: Integration with PipelineRunner


```scala
PipelineRunner.run(
    pipelineName = "golden_data_extraction",
    queryConfigPath = "configs/golden_relationship.yaml",
    transformFunc = df => df,       // minimal transform
    targetTable = "golden_schema",
    dryRun = false
)

```


-	Uses relationship YAML to determine which tables to extract.
- 	Keeps everything isolated in shadow/golden schema.
- 	Produces ready-to-use golden tables for automated tests.


---

#### Step 3: Schedule / Trigger

- 	Trigger manually for UAT or pre-commit test.
- 	Optional: nightly rebuild for regression validation.
- 	Keep versions of golden datasets (v1.0, v1.1, etc.).

---

### ✅ Benefits

- 	Reproducible, deterministic golden dataset
- 	Full relationship coverage (N-to-N, citations, org hierarchy)
- 	No orphan data
- 	Ready for automated Delta + ES validation
- 	Easily integrated into Databricks Workflows and CI/CD

---


## golden test automation template


I can next draft a full “golden test automation template” notebook, with SQL + YAML + validation checks all in one that you can run directly in Databricks.



Perfect! Here’s a full Golden Test Automation Template for your Databricks environment, integrating SQL extraction, YAML-based relationship config, orphan validation, and workflow automation. You can run it directly as a Databricks notebook or integrate into a Databricks Workflow job.

---

### 🔹 Databricks Golden Test Automation Notebook Template


```python

# ========================================
# 1️⃣ Configuration: Define Run Parameters
# ========================================
dbutils.widgets.text("run_mode", "golden")      # golden / shadow / prod
dbutils.widgets.text("output_schema", "golden_schema")
dbutils.widgets.text("relationship_config", "/Workspace/configs/golden_relationship.yaml")
dbutils.widgets.text("anchor_file", "/Workspace/configs/golden_anchors.csv")

run_mode = dbutils.widgets.get("run_mode")
output_schema = dbutils.widgets.get("output_schema")
relationship_config_path = dbutils.widgets.get("relationship_config")
anchor_file = dbutils.widgets.get("anchor_file")

print(f"Run Mode: {run_mode}, Output Schema: {output_schema}")

# ========================================
# 2️⃣ Load Relationship Config YAML
# ========================================
import yaml
import pandas as pd

with open(relationship_config_path, 'r') as f:
    relationship_config = yaml.safe_load(f)

# Example: {'article': {...}, 'author': {...}, 'organization': {...}}
print("Loaded Relationship Config:")
print(relationship_config.keys())

# ========================================
# 3️⃣ Load Anchor IDs (Deterministic)
# ========================================
anchors = pd.read_csv(anchor_file)  # CSV contains table_name, id_column, id_value
print(anchors.head())

# Convert to dictionary: {table_name: [id1, id2, ...]}
anchor_dict = anchors.groupby('table_name')['id_value'].apply(list).to_dict()

# ========================================
# 4️⃣ Golden Data Extraction Function
# ========================================
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

def extract_golden_table(table_name, id_column, id_list, fk_relations=[]):
    """
    Extracts golden table rows based on anchor IDs and relationship closure.
    fk_relations: list of dicts [{'fk': 'author_id', 'target_table': 'author'}]
    """
    # Base filter
    ids_str = ",".join([str(x) for x in id_list])
    df = spark.sql(f"SELECT * FROM prod.{table_name} WHERE {id_column} IN ({ids_str})")
    
    # Save to golden schema
    df.write.mode("overwrite").format("delta").saveAsTable(f"{output_schema}.{table_name}")
    
    print(f"Extracted {df.count()} rows into {output_schema}.{table_name}")
    
    # Process relationships recursively
    for rel in fk_relations:
        fk = rel['fk']
        target_table = rel['target_table']
        fk_ids = [row[fk] for row in df.select(fk).distinct().collect()]
        if fk_ids:
            extract_golden_table(target_table, rel.get('target_pk', fk), fk_ids, relationship_config.get(target_table, {}).get('links', []))

# ========================================
# 5️⃣ Execute Extraction for Anchors
# ========================================
for table_name, id_list in anchor_dict.items():
    primary_key = relationship_config[table_name]['primary_key']
    links = relationship_config[table_name].get('links', [])
    extract_golden_table(table_name, primary_key, id_list, links)

# ========================================
# 6️⃣ Orphan Validation
# ========================================
def validate_no_orphan(child_table, fk_column, parent_table, parent_pk):
    query = f"""
    SELECT c.{fk_column} 
    FROM {output_schema}.{child_table} c
    LEFT JOIN {output_schema}.{parent_table} p
    ON c.{fk_column} = p.{parent_pk}
    WHERE p.{parent_pk} IS NULL
    """
    df = spark.sql(query)
    count = df.count()
    if count == 0:
        print(f"No orphans detected for {child_table}.{fk_column} → {parent_table}.{parent_pk}")
    else:
        print(f"❌ {count} orphan(s) found for {child_table}.{fk_column} → {parent_table}.{parent_pk}")
        df.show(truncate=False)
        raise Exception("Orphan validation failed!")

# Example: Validate some core relationships
validate_no_orphan("golden_article_author", "author_id", "golden_authors", "author_id")
validate_no_orphan("golden_article_author", "article_id", "golden_articles", "article_id")
validate_no_orphan("golden_citations", "citing_article_id", "golden_articles", "article_id")
validate_no_orphan("golden_citations", "cited_article_id", "golden_articles", "article_id")

# ========================================
# 7️⃣ Optional: Delta → ES Verification (Shadow Run)
# ========================================
# Example: count ES documents for each golden table
# (Requires elasticsearch-hadoop connector or REST API)
# es_index = "articles_golden"
# df_es = spark.read.format("org.elasticsearch.spark.sql").option("es.nodes","<ES_HOST>").load(es_index)
# print("ES doc count:", df_es.count())

# ========================================
# 8️⃣ End of Golden Extraction / Validation
# ========================================
print("✅ Golden dataset extraction and orphan validation complete.")

```

---


### ✅ How This Maps to Your Databricks Workflow



#### 1.	PipelineRunner Integration


```scala
PipelineRunner.run(
    pipelineName = "golden_data_extraction",
    queryConfigPath = "/Workspace/configs/golden_relationship.yaml",
    transformFunc = df => df,       // no transformation
    targetTable = "golden_schema",
    dryRun = False
)
```


#### 2.	Workflow Task Design


| Task Name | Type | Notes |
|-----------|------|-------|
| Load anchor IDs | Notebook task | Reads CSV/DB table |
| Extract golden tables | Notebook task | Recursive using relationship-config YAML |
| Orphan validation | Notebook task | Fails workflow if orphan detected |
| ES validation (optional) | Notebook task | Verify ES doc count / mapping |
| Cleanup (optional) | Notebook task | Drop golden tables or truncate |



#### 3.	Automation Strategy

- 	Schedule as nightly regression test or pre-commit check
- 	Parameterize:
- 	run_mode → golden / shadow / prod
- 	output_schema → e.g., golden_schema or shadow_schema
- 	Store expected results for automated delta comparisons


---

This notebook covers:
- 	Golden data extraction (SQL / Delta)
- 	Relationship expansion (recursive, N-to-N)
- 	Orphan validation (blocking check)
- 	Workflow-ready automation (Databricks & PipelineRunner compatible)

---

If you want, I can also create the companion “Automated Golden Test Validation Notebook”, which:
- 	Runs incremental changes (insert/update/delete)
- 	Checks Delta → ES consistency
- 	Produces PASS/FAIL report
- 	Can be fully scheduled in your Databricks workflow


---


## To extract on-demand  vs.  keep a stable copy


Exactly — you’ve identified a key consideration for golden datasets: whether to extract on-demand from production sources or keep a stable copy. Let me clarify the reasoning and best practice.

---


### 1️⃣ Why people sometimes schedule extraction nightly / pre-commit

Some teams extract golden data repeatedly because:

1.	Automation convenience
- 	Pull the latest anchors or relationships automatically without maintaining separate tables.

2.	Dynamic upstream coverage
- 	Ensures golden data reflects new edge cases if production adds new relationships (e.g., new citation types or org hierarchies).

3.	Avoid extra storage
- 	No need to maintain separate golden Delta tables across environments.


✅ But this approach has major drawbacks for your system:
- 	Data is non-deterministic: every extraction could pick slightly different anchors or relationships.
- 	Test results can flap if upstream production changes.
- 	Hard to guarantee reproducibility or track regressions.

---

### 2️⃣ Why you should keep extracted golden data in Delta tables

Best practice for complex systems like yours (20+ pipelines, N-to-N, citations):

1.	Deterministic, repeatable tests
- 	The same golden dataset always produces the same results.

2.	Isolation from upstream changes
- 	Upstream production may evolve; your test dataset remains stable.

3.	Faster test execution
- 	No need to join 100+ tables each time.
- 	Smaller subset is already materialized in a shadow schema or golden_schema.

4.	Easier debugging & regression analysis
- 	You can compare current workflow output with expected results reliably.

Implementation approach:
- 	Extract once, store in golden_schema.* Delta tables.
- 	Version the dataset: golden_v1, golden_v2, etc.
- 	Only update intentionally when new edge cases need coverage.

---


### 3️⃣ When you might re-extract

Re-extraction is only needed if:

- 	New relationships or entities are added that need to be tested.
- 	Golden data becomes outdated for new pipeline features.
- 	You intentionally want a larger coverage set for regression.

Even in this case:

- 	Keep versioned snapshots: golden_v1, golden_v2
- 	Update the YAML anchor/config to control which rows are included.

---


### 4️⃣ Recommended Workflow for Your System

1.	Initial extraction
- 	Extract anchor IDs → expand relationships → store in golden_schema.*
- 	Validate no orphans, row counts, etc.

2.	Automation tests
- 	Run against stored golden Delta tables
- 	Compare output vs expected results

3.	Optional shadow run
- 	Only extract new anchors if testing new upstream logic
- 	Keep old version intact for regression

---

### ✅ Key Takeaways


| Aspect | Extract Every Run | Keep Stored Golden Data |
|--------|-------------------|-------------------------|
| Reproducibility | Low, may change | High, deterministic |
| Test speed | Slower | Faster |
| Upstream changes | Automatically included | Must version & update manually |
| Regression tracking | Hard | Easy |
| Complexity | Lower upfront | Higher upfront (versioning, schema) |


### Conclusion:

For a complex, multi-pipeline system like yours, you should extract once, store in versioned Delta tables, and run automated tests against this stable golden dataset. Only update when new relationships or edge cases require it.

---

If you want, I can redesign your previous Test Plan + Automation Phase to fully incorporate versioned stored golden Delta tables, including:
- 	Shadow / dry runs
- 	Incremental / CDF tests
- 	ES validation

So the workflow is fully stable, reproducible, and automation-ready.


---


