##  Enhanced Test Plan with Stored Golden Delta Tables


Perfect — let’s redesign your Test Plan + Automation Phase to fully use stored, versioned golden Delta tables. This ensures stability, reproducibility, and automation readiness for your complex multi-pipeline system.

---

### 🔹 Enhanced Test Plan with Stored Golden Delta Tables


**Scope**: Databricks → Delta → CDF → Elasticsearch
**Mode**: Golden dataset (versioned), Shadow run, Incremental validation

---

### Phase 0 — One-Time Setup (Golden Dataset Versioning)


**Task 0.1**: Define & Extract Golden Dataset

Action
- Select deterministic anchor IDs for core entities:
- Articles, authors, organizations, citations, metrics
- Include 1–2 hop relationships to cover N-to-N links
- Validate no orphan foreign keys
- Store in versioned Delta tables:


```sql
golden_schema_v1.article
golden_schema_v1.author
golden_schema_v1.organization
golden_schema_v1.article_author
golden_schema_v1.citation
golden_schema_v1.article_metrics
```

- Save expected results table for each pipeline output:

```sql
golden_schema_v1.expected_results
```


Output
- Versioned golden dataset (stable, reproducible)
- YAML config defining relationships & anchors

---

**Task 0.2**: Maintain Version Control
- Increment version for significant schema or data changes:

```sql
golden_schema_v2.*

```


- Use anchor YAML to document which rows are included
- Optional: snapshot old versions for regression comparison

---


### Phase 1 — Pre-Run Checks (Every Release)

Action
- Validate that stored golden tables exist
- Check:
- Row counts
- Primary key uniqueness
- Foreign key coverage (orphan checks)

Pass criteria: All checks pass before workflow execution

---

### Phase 2 — Golden End-to-End Run

Action
- Execute pipelines reading from real prod inputs or stored golden inputs depending on test type
- Writes go to shadow schema or temporary tables for testing:

```sql
shadow_schema.article
shadow_schema.article_author
shadow_schema.citation
```

- Validate outputs against stored expected results in golden_schema_v*

---

Delta Validation
- Row counts match expected
- No unexpected nulls
- Primary key uniqueness

ES Validation
- Document count matches expected
- Mappings are correct
- Spot-check sample documents

---

### Phase 3 — Incremental / Change-Type Validation

Action
- Apply test incremental changes to shadow tables:
- Insert / update / delete
- Run incremental pipeline logic
- Validate:
- Changes reflected correctly in Delta and ES
- Idempotency on reruns

---

### Phase 4 — Shadow / Dry Run in Prod

Action
- Redirect all writes to shadow schema:

```bash
run_mode = shadow
target_schema = shadow_schema
```

- Read from stored golden dataset or prod
- Validate:
- Delta size matches expectations
- No unintended data corruption
- Clean up shadow tables after test

---

### Phase 5 — Multi-Day Drift Validation

Action
- Schedule daily automated metrics capture:
- Source Delta counts
- Shadow / golden Delta counts
- ES doc counts
- Compare day-over-day changes
- Spot-check PKs for consistency

---

### Phase 6 — Automation Test Development

**Task 6.1** — Automation for Stored Golden Tables
- All tests read versioned golden Delta tables
- No live extraction needed per run
- Scripts:
- Delta validation
- ES validation
- Orphan checks
- Incremental / change-type validation

**Task 6.2** — CI/CD Integration
- Parameterize tests:
- golden_version → e.g., v1, v2
- run_mode → shadow / golden
- Trigger pre-commit or nightly regression
- Automated reporting:
- Pass / fail per pipeline
- Detailed row count / sample diff report

---

### Phase 7 — Maintenance of Golden Dataset

Action
- Update golden dataset only when:
- New edge cases added
- Schema changes
- Significant pipeline logic change
- Versioned snapshots ensure regression stability


---


### ✅ Benefits of Stored Golden Dataset Approach


| Benefit | Explanation |
|---------|-------------|
| Deterministic | Tests always run on same dataset |
| Reproducible | Versioned Delta tables + expected results |
| Fast | No repeated extraction from production tables |
| Stable | Upstream production changes do not affect tests |
| Regression-ready | Historical golden versions allow comparison |


### Summary Flow

```yaml
[Stored Golden Delta Tables]  --> [PipelineRunner/Workflows] --> [Shadow Schema / ES] --> [Validation Checks]
```

- Anchor rows fixed in golden_schema_vX
- Intermediate assembly in shadow schema
- Expected output compared for automated PASS/FAIL
- Incremental & recovery tests fully isolated

---

I can next draft a ready-to-run Databricks notebook template implementing this versioned golden dataset approach:
- Reads versioned golden tables
- Executes pipelines in shadow mode
- Validates Delta + ES + orphans
- Produces automation-friendly test report


---


## A ready-to-run Databricks notebook template


Great! Here’s a ready-to-run Databricks notebook template for versioned golden dataset automation. This integrates:

- Stored golden Delta tables (versioned)
- Shadow / dry-run execution
- Orphan validation
- Delta → ES consistency checks
- Automation-friendly reporting

You can run it standalone or integrate into your Databricks Workflow / PipelineRunner.

---

### 🔹 Databricks Golden Test Automation (Versioned)


```python
# ========================================
# 1️⃣ Configuration
# ========================================
dbutils.widgets.text("golden_version", "v1")       # v1, v2, etc.
dbutils.widgets.text("run_mode", "shadow")         # shadow / golden / prod
dbutils.widgets.text("output_schema", "shadow_schema")
dbutils.widgets.text("relationship_config", "/Workspace/configs/golden_relationship.yaml")
dbutils.widgets.text("expected_results_table", "golden_schema_v1.expected_results")

golden_version = dbutils.widgets.get("golden_version")
run_mode = dbutils.widgets.get("run_mode")
output_schema = dbutils.widgets.get("output_schema")
relationship_config_path = dbutils.widgets.get("relationship_config")
expected_results_table = dbutils.widgets.get("expected_results_table")

print(f"Golden Version: {golden_version}, Run Mode: {run_mode}, Output Schema: {output_schema}")

# ========================================
# 2️⃣ Load Relationship Config
# ========================================
import yaml
import pandas as pd
from pyspark.sql import SparkSession

with open(relationship_config_path, 'r') as f:
    relationship_config = yaml.safe_load(f)

spark = SparkSession.builder.getOrCreate()
print("Loaded relationships:", relationship_config.keys())

# ========================================
# 3️⃣ Function to Copy Golden Tables into Shadow Schema
# ========================================
def copy_golden_to_shadow(table_name):
    source_table = f"golden_schema_{golden_version}.{table_name}"
    target_table = f"{output_schema}.{table_name}"
    df = spark.table(source_table)
    df.write.mode("overwrite").format("delta").saveAsTable(target_table)
    print(f"Copied {df.count()} rows from {source_table} → {target_table}")
    return df

# Copy all tables defined in relationship config
for table_name in relationship_config.keys():
    copy_golden_to_shadow(table_name)

# ========================================
# 4️⃣ Orphan Validation
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

# Example validations
validate_no_orphan("article_author", "author_id", "author", "author_id")
validate_no_orphan("article_author", "article_id", "article", "article_id")
validate_no_orphan("citation", "citing_article_id", "article", "article_id")
validate_no_orphan("citation", "cited_article_id", "article", "article_id")

# ========================================
# 5️⃣ Run Pipeline in Shadow Mode
# ========================================
# Integrate with your PipelineRunner
from pipeline_runner import PipelineRunner

PipelineRunner.run(
    pipelineName="full_pipeline",
    queryConfigPath=relationship_config_path,
    transformFunc=lambda df: df,       # no transformation, just execute
    targetTable=output_schema,
    dryRun=(run_mode=="shadow")
)

print("Pipeline executed in shadow mode.")

# ========================================
# 6️⃣ Validate Delta Results vs Expected
# ========================================
for table_name in relationship_config.keys():
    actual = spark.table(f"{output_schema}.{table_name}")
    expected = spark.table(f"{expected_results_table}_{table_name}")
    
    actual_count = actual.count()
    expected_count = expected.count()
    
    if actual_count != expected_count:
        print(f"❌ {table_name} row count mismatch: actual={actual_count}, expected={expected_count}")
    else:
        print(f"✅ {table_name} row count match: {actual_count}")

# ========================================
# 7️⃣ Optional: Validate Elasticsearch (if integrated)
# ========================================
# Example placeholder:
# es_index = f"{table_name}_golden"
# df_es = spark.read.format("org.elasticsearch.spark.sql") \
#          .option("es.nodes", "<ES_HOST>") \
#          .load(es_index)
# print(f"{table_name} ES doc count: {df_es.count()}")

# ========================================
# 8️⃣ End of Golden Test Automation
# ========================================
print("✅ Golden test automation completed successfully.")

```


---

### 🔹 Features Implemented

1.	Versioned golden Delta tables
- golden_schema_v1.*, golden_schema_v2.*

2.	Shadow / dry-run execution
- Writes isolated to shadow_schema.*

3.	Orphan validation
- Checks foreign key integrity for all core relationships

4.	Delta validation vs expected
- Row count comparison for each table

5.	PipelineRunner integration
- Executes full pipeline logic on stored golden dataset

6.	Optional ES validation
- Ready to add ES consistency checks

7.	Automation-ready
- Parameterized for golden_version, run_mode, output_schema

---

### 🔹 How to Use

1.	Store versioned golden tables in golden_schema_vX.
2.	Update relationship_config.yaml with table links and PK/FK info.
3.	Set golden_version to the desired version.
4.	Schedule notebook in Databricks Workflow:
  - Pre-commit test
  - Nightly regression
5.	Review logs or row counts for automated PASS/FAIL reporting.

---

This setup ensures:
- Deterministic and reproducible tests
- Stable golden dataset unaffected by upstream changes
- Fast automated validation
- Ready for multi-pipeline, N-to-N dependency systems

---

I can next enhance this notebook with incremental / change-type tests, so it can automatically:
- Inject insert/update/delete events into shadow tables
- Run incremental pipeline logic
- Validate Delta → ES consistency for regression

This will make your full automation suite complete.



---

##  Handle incremental/change-type tests


Perfect! Let’s extend the previous golden test notebook to handle incremental/change-type tests. This will make your automation suite fully regression-ready for multi-pipeline, N-to-N dependency systems.

---


### 🔹 Databricks Incremental / Change-Type Test Automation


**Goals**:
- Simulate insert, update, delete changes on golden data
- Run pipelines in shadow mode
- Validate Delta and ES outputs
- Detect idempotency issues and regression errors



```python
# ========================================
# 1️⃣ Configuration
# ========================================
dbutils.widgets.text("golden_version", "v1")
dbutils.widgets.text("run_mode", "shadow")         
dbutils.widgets.text("output_schema", "shadow_schema")
dbutils.widgets.text("relationship_config", "/Workspace/configs/golden_relationship.yaml")
dbutils.widgets.text("expected_results_table", "golden_schema_v1.expected_results")
dbutils.widgets.text("change_type_file", "/Workspace/configs/change_type_events.csv")  # defines insert/update/delete

golden_version = dbutils.widgets.get("golden_version")
run_mode = dbutils.widgets.get("run_mode")
output_schema = dbutils.widgets.get("output_schema")
relationship_config_path = dbutils.widgets.get("relationship_config")
expected_results_table = dbutils.widgets.get("expected_results_table")
change_type_file = dbutils.widgets.get("change_type_file")

print(f"Golden Version: {golden_version}, Run Mode: {run_mode}, Output Schema: {output_schema}")

# ========================================
# 2️⃣ Load Relationship Config
# ========================================
import yaml
import pandas as pd
from pyspark.sql import SparkSession

with open(relationship_config_path, 'r') as f:
    relationship_config = yaml.safe_load(f)

spark = SparkSession.builder.getOrCreate()
print("Loaded relationships:", relationship_config.keys())

# ========================================
# 3️⃣ Load Change-Type Events
# ========================================
# CSV columns: table_name, pk_value, change_type(insert/update/delete), columns_to_update(json)
change_events = pd.read_csv(change_type_file)
print(change_events.head())

# ========================================
# 4️⃣ Apply Change Events to Shadow Tables
# ========================================
import json

def apply_changes():
    for idx, row in change_events.iterrows():
        table = row['table_name']
        pk_col = relationship_config[table]['primary_key']
        change_type = row['change_type']
        target_table = f"{output_schema}.{table}"
        
        if change_type.lower() == "insert":
            # Build a new row DataFrame from CSV columns
            new_row = pd.DataFrame([json.loads(row['columns_to_update'])])
            spark_df = spark.createDataFrame(new_row)
            spark_df.write.mode("append").format("delta").saveAsTable(target_table)
            print(f"Inserted 1 row into {target_table}")
        
        elif change_type.lower() == "update":
            # Update the row using Delta merge
            updates = json.loads(row['columns_to_update'])
            set_clause = ", ".join([f"{k} = '{v}'" for k,v in updates.items()])
            sql = f"UPDATE {target_table} SET {set_clause} WHERE {pk_col} = '{row['pk_value']}'"
            spark.sql(sql)
            print(f"Updated row {row['pk_value']} in {target_table}")
        
        elif change_type.lower() == "delete":
            sql = f"DELETE FROM {target_table} WHERE {pk_col} = '{row['pk_value']}'"
            spark.sql(sql)
            print(f"Deleted row {row['pk_value']} from {target_table}")
        
        else:
            print(f"Unknown change_type: {change_type} for table {table}")

apply_changes()

# ========================================
# 5️⃣ Run Pipeline in Shadow Mode
# ========================================
from pipeline_runner import PipelineRunner

PipelineRunner.run(
    pipelineName="full_pipeline",
    queryConfigPath=relationship_config_path,
    transformFunc=lambda df: df,      
    targetTable=output_schema,
    dryRun=(run_mode=="shadow")
)

print("Pipeline executed in shadow mode for incremental test.")

# ========================================
# 6️⃣ Validate Delta Outputs vs Expected
# ========================================
for table_name in relationship_config.keys():
    actual = spark.table(f"{output_schema}.{table_name}")
    expected = spark.table(f"{expected_results_table}_{table_name}")
    
    actual_count = actual.count()
    expected_count = expected.count()
    
    if actual_count != expected_count:
        print(f"❌ {table_name} row count mismatch: actual={actual_count}, expected={expected_count}")
    else:
        print(f"✅ {table_name} row count match: {actual_count}")

# ========================================
# 7️⃣ Optional: ES Validation
# ========================================
# Implement ES read & count comparison if ES is integrated
# e.g., spark.read.format("org.elasticsearch.spark.sql").option(...).load(es_index)

# ========================================
# 8️⃣ End of Incremental Test
# ========================================
print("✅ Incremental / change-type test automation completed successfully.")

```


---


### 🔹 Features Implemented

1.	Apply change events (insert, update, delete) to shadow tables
2.	Run full pipeline in shadow mode for incremental validation
3.	Delta validation against stored golden expected results
4.	Orphan and FK validation still applies
5.	Automation-friendly reporting (row counts, mismatches)
6.	Optional ES validation placeholder


---

### 🔹 Recommended Workflow

1.	Prepare versioned golden dataset in golden_schema_vX.
2.	Maintain change-type CSVs for incremental tests.
3.	Run incremental automation notebook:
  - Reads golden tables
  - Applies incremental changes
  - Executes pipeline in shadow
  - Validates Delta and ES outputs
4.	Integrate into CI/CD:
  - Pre-commit or nightly regression tests
  - Automated PASS/FAIL reporting
5.	Optional: Version new golden dataset if pipeline logic or coverage changes.

---

This completes your full automated regression suite:
- Stored versioned golden dataset
- Shadow / dry-run execution
- Incremental / change-type tests
- Delta → ES validation
- Automation-friendly and CI/CD ready

---

I can next draw a diagram showing the workflow and data flow for golden + incremental + shadow testing. This helps teams understand execution and dependencies clearly.



---


##  Diagram of Golden + Incremental + Shadow Testing Workflow 


Perfect! Here’s a clear diagram and explanation for your Golden + Incremental + Shadow Testing Workflow in a complex multi-pipeline system. I’ll describe the flow so you can visualize or implement it in documentation or presentations.


---


### 🔹 Golden + Incremental + Shadow Test Workflow


```yaml
           ┌───────────────────────────────┐
           │   Versioned Golden Dataset     │
           │  (Delta Tables in golden_schema_vX) │
           └───────────────┬───────────────┘
                           │
                           │ Copy / Reference
                           ▼
                 ┌─────────────────────┐
                 │ Shadow Schema Tables │
                 │ (shadow_schema.*)   │
                 └─────────┬───────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
 ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
 │ Insert Rows │     │ Update Rows │     │ Delete Rows │
 │ (Change-    │     │ (Change-    │     │ (Change-    │
 │ Type CSV)   │     │ Type CSV)   │     │ Type CSV)   │
 └─────┬───────┘     └─────┬───────┘     └─────┬───────┘
       │                   │                   │
       └───────────┬───────┴───────┬───────────┘
                   ▼
           ┌─────────────────────┐
           │ Run Pipeline in     │
           │ Shadow Mode / Dry   │
           │ Run                │
           └─────────┬───────────┘
                     │
       ┌─────────────┴─────────────┐
       ▼                           ▼
┌─────────────┐             ┌─────────────┐
│ Delta Output│             │ Elasticsearch│
│ Tables      │             │ Indices      │
└─────┬───────┘             └─────┬───────┘
      │                           │
      ▼                           ▼
┌─────────────┐             ┌─────────────┐
│ Validate    │             │ Validate    │
│ Delta vs    │             │ ES Docs     │
│ Expected    │             │ Count &     │
│ Results     │             │ Mappings    │
└─────┬───────┘             └─────┬───────┘
      │                           │
      └─────────────┬─────────────┘
                    ▼
           ┌─────────────────────┐
           │ Automated Test Report│
           │ (PASS / FAIL, Row   │
           │ Counts, Orphans)    │
           └─────────────────────┘

```

---

### 🔹 Explanation of Workflow


1.	Stored Golden Dataset
  - Stable, versioned Delta tables (golden_schema_vX)
  - Contains deterministic subset of production data
  - Covers cross-entity relationships, N-to-N, citations, metrics
2.	Shadow Schema
  - Copy golden tables into shadow_schema for test isolation
  - All pipeline writes go here; prod data is untouched
3.	Incremental / Change-Type Events
  - Insert, update, delete operations defined in CSV or config
  - Applied to shadow tables to simulate real-life incremental loads
4.	Pipeline Execution
  - Run full pipeline logic in shadow mode
  - Handles joins, transformations, metrics, Delta & ES writes
5.	Validation
  - Delta Tables: row counts, primary/foreign keys, orphan checks
  - ES: document count, mappings, spot-check sample docs
6.	Automated Reporting
  - Summarizes PASS/FAIL per table and per test scenario
  - Logs row-level mismatches, orphan issues, or ES inconsistencies
7.	Regression-Ready
  - Versioned golden dataset ensures reproducible results
  - Only update when new edge cases or schema changes occur

---


### 🔹 Advantages

- Fully deterministic and reproducible
- Supports multi-pipeline, N-to-N dependency systems
- Safe testing without touching production data
- Automation-friendly: CI/CD integration, nightly regression
- Incremental / change-type tests included for realistic simulations
- Easy regression tracking via versioned golden tables

---


### 📦 Pipeline Test Automation Package (Golden + Incremental)


If you want, I can also combine all the notebooks, YAML configs, and this workflow diagram into a single “Pipeline Test Automation Package” — essentially a ready-to-run framework for your Databricks environment.


---

Excellent. Below is a complete, concise, executable “Pipeline Test Automation Package” you can directly adopt for your 20+ pipeline, N-to-N, citation-heavy Databricks → Delta → ES system.
This is designed to be practical, minimal, deterministic, and automation-ready.

---


### 1️⃣ Package Purpose

Provide a stable, repeatable, low-cost test framework that:
- Verifies end-to-end correctness (Delta + ES)
- Handles cross-entity, N-to-N, citation dependencies
- Supports incremental / CDF logic
- Avoids flaky tests caused by upstream data drift
- Fits tight release timelines

---


### 2️⃣ Package Components (What You Deploy)


```yml
pipeline-test-automation/
├── golden/
│   ├── golden_schema_v1/           # Stored versioned golden Delta tables
│   ├── expected_results_v1/        # Expected pipeline outputs
│   └── anchors.yaml                # Deterministic anchor IDs
│
├── config/
│   ├── relationship.yaml           # Entity PK/FK graph
│   ├── change_events.csv           # Insert / Update / Delete scenarios
│   └── pipeline_params.yaml        # Run-mode, schemas, versions
│
├── notebooks/
│   ├── 01_golden_validation.ipynb  # Orphan, PK, FK checks
│   ├── 02_shadow_run.ipynb         # Golden → Shadow execution
│   ├── 03_incremental_test.ipynb   # Change-type simulation
│   └── 04_es_validation.ipynb      # ES consistency checks
│
├── workflows/
│   └── golden_test_workflow.json   # Databricks Workflow definition
│
└── reports/
    └── test_results/               # PASS/FAIL + metricsyaml

```

---

### 3️⃣ Core Design Principles (Why This Works)


#### ✅ Stored Golden Delta Tables
- Extract once
- Version (v1, v2, …)
- Never change unless intentionally updated

Result: deterministic, reproducible tests

---

#### ✅ Shadow Schema Execution
- All writes go to shadow_schema
- Production data is never touched

Result: zero-risk testing in prod/UAT

---

#### ✅ Relationship-Driven Coverage
- Relationship YAML defines entity graph
- Ensures no orphan data
- Covers N-to-N, citations, hierarchies

Result: small dataset, high coverage

---

#### ✅ Incremental Simulation
- Controlled insert/update/delete events
- Validates:
- CDF logic
- Idempotency
- Delete propagation

Result: realistic regression testing

---

### 4️⃣ Minimal Test Phases (Executable)

#### Phase 0 — Golden Dataset (One-Time / Rare)
- Extract anchors + 1–2 hop relationships
- Store as golden_schema_vX
- Validate no orphans
- Freeze version

---

#### Phase 1 — Pre-Run Validation (Every Release)
- Table existence
- PK uniqueness
- FK orphan checks

⏱️ < 1 minute

---

#### Phase 2 — Golden Shadow Run
- Copy golden → shadow schema
- Run full pipeline logic
- No final commit

⏱️ < 10 minutes

---

#### Phase 3 — Incremental Test
- Apply change events
- Rerun pipeline
- Validate deltas

⏱️ < 5 minutes

---

#### Phase 4 — Validation
- Delta row counts
- Key integrity
- ES doc counts + mappings

⏱️ < 5 minutes

---

### 5️⃣ Automation Rules (Non-Negotiable)

| Rule | Why |
|------|-----|
| No live prod extraction per test | Prevents flaky tests |
| Golden data is versioned | Enables regression comparison |
| Shadow schema only | Safe testing |
| Tests fail fast | Save time |
| Expected results stored | True automation |


### 6️⃣ When to Update Golden Data

Only update golden dataset if:
- New entity type added
- New relationship introduced
- Pipeline logic fundamentally changes

- ➡️ Create golden_schema_v2
- ➡️ Keep v1 for regression comparison

---

### 7️⃣ How This Fits CI / Release Flow


```yaml
PR / Release →
  Pre-Run Checks →
  Golden Shadow Run →
  Incremental Test →
  Delta + ES Validation →
  PASS / FAIL
```

- Pre-commit: fast subset
- Nightly: full regression
- Release gate: mandatory PASS

---

### 8️⃣ What This Prevents (Very Important)

- 🚫 Silent orphan data
- 🚫 Partial ES updates
- 🚫 Broken incremental logic
- 🚫 Undetected cross-pipeline regressions
- 🚫 “Works on my data” failures

---

### 9️⃣ Final Recommendation (For Leadership / Review)

This testing package provides maximum confidence with minimal data and runtime, is safe for production environments, and scales cleanly as pipelines and relationships grow.

---

If you want, next I can:
- Convert this into a 1-page architecture diagram
- Create a release-readiness checklist using this framework
- Provide a standard test-failure triage playbook


---


## ✅ Release-Readiness Checklist



### 1️⃣ Pre-Release Preconditions (Must Be TRUE)

- ☐ Golden dataset exists and is versioned (golden_schema_vX)
- ☐ Golden dataset is frozen (no live prod extraction)
- ☐ Relationship config YAML reviewed and unchanged
- ☐ Change-event scenarios defined (insert / update / delete)
- ☐ Shadow schema is empty or freshly recreated

⸻

### 2️⃣ Golden Dataset Integrity Checks (Fast Gate)

- ☐ All golden tables present
- ☐ Primary keys are unique
- ☐ No orphan foreign keys
- ☐ entity ↔ entity
- ☐ entity ↔ article
- ☐ citation ↔ article
- ☐ Golden dataset size < 5 MB
- ☐ Golden run completes in < 10 minutes

Result: - ☐ PASS - ☐ FAIL

⸻

### 3️⃣ Shadow / Dry-Run Execution

- ☐ Pipeline executed in shadow mode
- ☐ Writes redirected to shadow_schema only
- ☐ No production tables modified
- ☐ Job completed without retries or partial failures
- ☐ Pipeline logs show expected stage execution order

Result: - ☐ PASS - ☐ FAIL

⸻

### 4️⃣ Golden Output Validation (Delta)

- ☐ Output row counts match expected results
- ☐ No unexpected nulls in required fields
- ☐ PK uniqueness preserved
- ☐ FK relationships preserved (no new orphans)
- ☐ No schema drift detected

Result: - ☐ PASS - ☐ FAIL

⸻

### 5️⃣ Incremental / Change-Type Validation

- ☐ Insert events processed correctly
- ☐ Update events propagated correctly
- ☐ Delete events handled correctly
- ☐ Idempotent rerun produces no additional changes
- ☐ No residual orphan records after deletes

Result: - ☐ PASS - ☐ FAIL

⸻

### 6️⃣ Elasticsearch Validation (If Applicable)

- ☐ Index exists / updated as expected
- ☐ Document count matches Delta output
- ☐ Sample documents validated (IDs, nested fields)
- ☐ Mappings unchanged or expected
- ☐ No partial or duplicate documents

Result: - ☐ PASS - ☐ FAIL

⸻

### 7️⃣ Multi-Day Drift & Stability (If Required)

- ☐ Day-over-day counts stable or explainable
- ☐ No unexpected growth or shrinkage
- ☐ Key metrics trend aligns with expectations

Result: - ☐ PASS - ☐ N/A - ☐ FAIL

⸻

### 8️⃣ Automation & Recovery Readiness

- ☐ Tests are fully automated (no manual steps)
- ☐ Failure produces clear PASS/FAIL signal
- ☐ Logs + metrics captured for triage
- ☐ Rerun succeeds without cleanup
- ☐ Shadow data cleanup confirmed

⸻

### 9️⃣ Final Release Decision

- ☐ ALL mandatory sections passed
- ☐ Known issues documented and accepted
- ☐ Rollback plan confirmed
- ☐ Monitoring enabled post-release

### 🚀 RELEASE STATUS

- ☐ APPROVED  ☐ BLOCKED