## Top 40 Prompts for Building Data Delivery Systems 


Here’s a comprehensive GitHub Copilot Prompt Cookbook of the Top 40 Prompts for helping with architecture, modeling, and programming in a daily data delivery system built on Delta Lake, Spark (batch/streaming), with ES (Elasticsearch) assembly/injection, multiple sources (e.g. WoS, patents, grants), and a reliable pipeline ecosystem.

Everything is formatted in inline markdown for direct use in documentation, dev notebooks, or prompts to Copilot or ChatGPT.

---

### 🚀 Copilot Prompt Cookbook: Top 40 Prompts for Building Data Delivery Systems (Delta Lake + Spark + ES)

✅ System Context:

- 	🗃 Sources: WoS, PPRN, Patents, Grants, etc.
- 	🏗 Layers: Bronze → Silver → Gold (Delta Lake)
- 	⚙️ Orchestration: Triggerless or triggered workflows
- 	⏱ Modes: Batch, Micro-batch, Streaming, NRT
- 	💡 Features: High parallelism, metric recalculation, ES data injection

---

### ⚒️ 1–10: Core Architecture & Design Prompts



| **#** | **Prompt**                                                                 | **Description**                        |
|-------|---------------------------------------------------------------------------|----------------------------------------|
| 1     |   Design a modular data pipeline architecture using Delta Lake for ingest, clean, enrich, and publish stages | High-level modular design             |
| 2     |   Create a layered data lake architecture (bronze/silver/gold) using Delta tables for versioned storage | Layered Delta Lake modeling            |
| 3     |   Design a batch + micro-batch + stream hybrid pipeline using Spark Structured Streaming | For multi-mode ingestion               |
| 4     |   Model a parallel daily data pipeline that processes wos, patent, and grant data in isolation | For content separation                 |
| 5     |   Propose a scalable file layout and partitioning strategy for Delta Lake tables | Optimizes scan/filter                  |
| 6     |   Define schema evolution strategy for structured and semi-structured data in Delta | Handling source drift                  |
| 7     |   Design pipeline run DAG with minimum interdependencies (no downstream trigger) | Triggerless reliability                |
| 8     |   Add audit logging and checkpointing mechanism to all streaming and batch pipelines | Resilience and observability           |
| 9     |   Design the system so metric recalculation can be triggered by updates to source tables | Dynamic recalculation logic            |
| 10    |   Create a reusable library to handle data ingestion, deduplication, and Delta merge logic | Improves consistency                   |


---

### 🛠️ 11–20: Programming and Engineering Prompts


| **#** | **Prompt**                                                                 | **Description**                        |
|-------|---------------------------------------------------------------------------|----------------------------------------|
| 11    |   Write a Spark job to ingest new WOS records, deduplicate, and write to bronze Delta table | ETL pattern                           |
| 12    |   Refactor this Spark job to run in parallel by content type (wos, grant, patent) | Parallelism                           |
| 13    |   Write a function that merges incoming stream into an existing Delta table using MERGE INTO | CDC logic                              |
| 14    |   Create a Delta MERGE script with change capture logic for updated vs inserted rows | UPSERT logic                           |
| 15    |   Build a reusable schema enforcement + normalization function for JSON ingestion | Schema guard                           |
| 16    |   Write code to build metrics table (e.g. paper counts, top authors) from gold layer | Aggregation logic                      |
| 17    |   Add watermarks and event-time windows to Spark Structured Streaming job for late data | Handles lag                           |
| 18    |   Refactor Spark SQL with multiple joins into optimized CTEs and broadcast joins | Performance boost                      |
| 19    |   Use Delta time travel to compare today’s data snapshot with yesterday’s | Auditing support                       |
| 20    |   Design a metric recalculation trigger based on new rows in source Delta table | Conditional updates                     |


---

### 📦 21–30: Elasticsearch Assembly + Injection Prompts



| **#** | **Prompt**                                                                 | **Description**                        |
|-------|---------------------------------------------------------------------------|----------------------------------------|
| 21    |   Build a Spark job that assembles structured paper data into a nested JSON document for ES | ES-ready struct                        |
| 22    |   Create ES index mappings for documents containing nested author, institution, and funding fields | ES schema design                       |
| 23    |   Write Scala function to convert Spark Row to JSON for Elasticsearch bulk API | Serialization                          |
| 24    |   Create bulk writer logic with retry + backoff for injecting data into Elasticsearch | Reliable injection                     |
| 25    |   Generate document-level versioning logic based on last_updated timestamp | ES conflict prevention                 |
| 26    |   Assemble per-paper object with author names, institutions, keywords, and metrics in nested struct | Document enrichment                    |
| 27    |   Build a job to delete stale documents from ES that no longer exist in Delta | Data sync cleanup                      |
| 28    |   Add logic to split large ES bulk batches and retry on partial failure | Robust bulk loader                     |
| 29    |   Add Spark metrics and logging to monitor number of documents pushed to ES | Observability                          |
| 30    |   Create data quality check to ensure required fields exist before indexing to ES | Validity guardrail                     |


---

### 🧠 31–40: Operational Reliability, Monitoring, NRT


| **#** | **Prompt**                                                                 | **Description**                        |
|-------|---------------------------------------------------------------------------|----------------------------------------|
| 31    |   Build logic to detect missing daily runs and auto-trigger backfill for missed partitions | Ops reliability                       |
| 32    |   Write Scala code to compare record counts between Delta and ES for validation | Output verification                    |
| 33    |   Create job orchestration template for running content-specific jobs in parallel with retries | Workflow resilience                    |
| 34    |   Add checkpointing, resume logic, and streaming status logging to structured streaming job | Streaming robustness                   |
| 35    |   Add histograms of data lag and volume to Spark metrics dashboard | Monitoring                              |
| 36    |   Refactor to isolate schema, transform, and write logic into reusable functions | Code modularity                        |
| 37    |   Define alert conditions and thresholds for unusual volume drops or surges in daily data | Anomaly detection                      |
| 38    |   Implement a validation stage to compare WOS and PPRN record counts across layers | Consistency check                      |
| 39    |   Write a delta-to-delta change extractor that publishes only updated papers to downstream | Efficient NRT                          |
| 40    |   Model the full DAG of the daily system using task metadata, status tracking, and lineage graph | Observability + lineage                |


---

### 🧩 Bonus Prompt Templates

🎯 For Any Job

- Write a Spark job to ingest {source_type} data, normalize schema, deduplicate, and merge to Delta

🔁 Parallelism

- Refactor this pipeline to use parallel tasks by partition or content_type


📦 For ES Struct Assembly

- Build nested JSON object for Elasticsearch from Spark DataFrame with author, inst, metrics fields



---

### 🧰 Tech Stack Alignment



| **Component**              | **Relevant Prompts**                                                   |
|----------------------------|------------------------------------------------------------------------|
| **Delta Lake**              | 1–10, 13, 14, 19, 20, 31, 39                                           |
| **Spark Structured Streaming** | 3, 7, 17, 34                                                           |
| **Elasticsearch**           | 21–30                                                                  |
| **Data Modeling**           | 1, 2, 5, 6, 10, 40                                                     |
| **Monitoring + Reliability**| 31–38                                                                  |
