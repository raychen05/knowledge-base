

##  Incremental Assembly Pipeline Design for Building a Unified incites Delta Table from Entity and Article-Level Metrics



### Optimal Delta + Spark design to build incites (assembly) from intermediate entity tables

Nice — you have multiple independent pipelines writing normalized entity tables + entity_metrics and two article-level metric tables, and you want a robust, efficient way to assemble a denormalized incites materialized view. My recommendation and plan below balances correctness, performance, and operational simplicity.

**Short answer / recommended approach (tl;dr):**

Use a single assembly pipeline (Option 2) that incrementally updates incites using Change Data Feed (CDF) or a small change-log from each intermediate pipeline to compute the union of affected uids, then MERGE only those rows into incites. Only do large overwrites when the affected set is large (heuristic threshold). This central assembly avoids write contention & repeated partial writes and ensures consistent, atomic updates.


---

### Why Option 2 (incremental assembly) is better than per-entity partial updates


Pros:
- 	Single point of truth / single transaction: the assembly pipeline can build a consistent row combining all entities and article-level metrics before updating incites.
- 	Lower contention: fewer small writes into a single hot table; one well-optimized merge is better than many competing partial updates.
- 	Easier to reason & test: assembly logic is centralized; bugs or schema changes are addressed in one place.
- 	Efficient incremental updates: only update uids that actually changed.

Cons addressed:
- 	If multiple pipelines update the same uid simultaneously, assembly will pick the latest snapshot (use timestamps / versioning / watermarks to choose ordering).
- 	Slightly more orchestration is needed (trigger assembly after entity pipelines finish). But orchestration can be event or schedule-based; not expensive.

---

### High-level architecture / dataflow

1.	Entity pipelines (authorprofile, organization, funder, category) update:
- 	<entity> and <entity>_metric delta tables.
- 	Each pipeline also emits a change-log (small table) containing uids (and update_ts) it touched in this run. If CDF enabled, you can read CDF instead of explicit change-log.
  
2.	Article-level pipelines update article_metric and article_metrics and emit their change-logs.

3.	Assembly pipeline:
- 	Collects changed uids from each change-log (or CDF) → affected_uids (de-duplicated).
- 	Reads only required columns from entity tables and article metric tables for those uids.
- 	Joins/aggregates to produce the denormalized incites rows for those uids.
- 	MERGE (UPSERT) into incites Delta table.
- 	Optionally compacts / optimizes incites afterwards.

4.	Monitoring: track counts, latency, rows updated, and merge durations.


---

### Key implementation details & best practices


1) Finding affected rows

Preferred: Delta CDF (Change Data Feed) on each intermediate delta table to get the keys changed since the last assembly run:

- 	Enable CDF: ALTER TABLE db.table SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
- 	Query: table_changes('db.table', <last_version_or_timestamp>) → filter to keys of interest.

Fallback: each pipeline writes a small staging/<table>_changes delta with columns (uid, key, op, ts) for the pipeline run. The assembly collects these change tables.

Compute:

```sql
affected_uids = select distinct uid from (
  changes_authorprofile
  union changes_organization
  union changes_authorprofile_metric
  union changes_article_metric
  ...
)
```

2) Read minimal columns

When building the assembled row, read only the required columns + join keys from each table for the affected uids. This minimizes shuffle and I/O.

3) Join strategy

- 	Use hash/broadcast joins when one side is small (e.g., entity list objects per uid are small).
- 	For large joins by uid, partition/read by uid (filter pushdown) so Spark only scans relevant files.
- 	Use spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1) only to control broadcasting; instead explicitly broadcast() where necessary.

4) Use MERGE INTO (atomic)

Delta MERGE gives ACID semantics. Merge assembled rows into incites using MERGE on primary key uid.


5) Overwrite vs Merge decision — heuristic

- 	If affected_count / total_rows < threshold (e.g. threshold 0.05 or 5%) → use incremental MERGE for only affected uids.
- 	If the affected set is very large (e.g. > 20–30% or > a configured absolute number like 10M rows), do a partition-based overwrite (overwrite partitions / or rewrite entire table). Choose threshold according to your cluster and table size.

6) Partitioning & clustering on incites

- 	Partition incites on a meaningful dimension if available (e.g., pubyear) only if queries use it.
- 	Z-ORDER BY uid or cluster keys to speed up point lookups by uid.
- 	Keep file sizes ~ 256MB for good performance.

7) Compaction & Optimizations

- 	After many small merges, run OPTIMIZE incites ZORDER BY (uid) periodically for compaction.
- 	Run VACUUM with proper retention to clean up old files.

8) Idempotency & retries

- 	Make assembly idempotent. Use update_ts or update_run_id fields and MERGE keyed by uid.
- 	Use pipeline run ids and checkpoints.

9) Deletes

Handle deletes explicitly: if upstream deletes are allowed, CDF will present delete operations — assembly should DELETE from incites or mark as deleted.


---

### Example PySpark assembly pipeline (incremental MERGE using CDF / change-logs)


This is a complete skeleton you can adapt. I keep it concise and practical.


**🧱 Python Assembly Pipeline (Incremental MERGE)**

```python
from delta.tables import DeltaTable
from pyspark.sql import functions as F
from pyspark.sql import SparkSession
from pyspark.sql.functions import broadcast

spark = SparkSession.builder.getOrCreate()

# Config / thresholds
DB = "analytics"
INCITES_TABLE = f"{DB}.incites"
THRESHOLD_FRACTION = 0.05  # if affected > 5% => consider partition overwrite
ABS_OVERWRITE_THRESHOLD = 5_000_000  # or a count threshold

# 1) Get changed uids from change-log tables created by each pipeline OR from CDF
# Example: if pipelines wrote small change tables like analytics.changes_authorprofile (columns: uid)
change_tables = [
    f"{DB}.changes_authorprofile",
    f"{DB}.changes_authorprofile_metric",
    f"{DB}.changes_organization",
    f"{DB}.changes_organization_metric",
    f"{DB}.changes_funder",
    f"{DB}.changes_funder_metric",
    f"{DB}.changes_category",
    f"{DB}.changes_category_metric",
    f"{DB}.changes_article_metric",
    f"{DB}.changes_article_metrics"
]

# Read and union distinct uids
changes_dfs = []
for t in change_tables:
    try:
        df = spark.table(t).select("uid").filter(F.col("uid").isNotNull())
        changes_dfs.append(df)
    except Exception as e:
        # table might not exist for this run - log and continue
        print(f"warning: cannot read {t}: {e}")

if not changes_dfs:
    print("No changes found. Exiting.")
    exit(0)

affected_uids_df = changes_dfs[0]
for df in changes_dfs[1:]:
    affected_uids_df = affected_uids_df.union(df)
affected_uids_df = affected_uids_df.distinct().cache()
affected_count = affected_uids_df.count()

# Quick check vs total
incites_dt = DeltaTable.forName(spark, INCITES_TABLE)
total_count = spark.table(INCITES_TABLE).count()

print(f"affected_count={affected_count} total_count={total_count}")

# Heuristic: if very large, do partition or full rewrite
if (affected_count > ABS_OVERWRITE_THRESHOLD) or (affected_count / max(1, total_count) > THRESHOLD_FRACTION):
    # Option: full partition rewrite or full rebuild
    print("Large affected set - consider rewrite/partition-overwrite instead of many merges.")
    # Example: full overwrite of partitions containing affected uids:
    # 1) Read incites rows NOT in affected_uids
    keep_df = spark.table(INCITES_TABLE).join(affected_uids_df, on="uid", how="left_anti")
    # 2) Recompute new rows for affected_uids below and union + overwrite table
    recompute_df = ... # compute assembled rows for affected_uids (see below)
    new_incites = keep_df.unionByName(recompute_df)
    new_incites.write.format("delta").mode("overwrite").option("replaceWhere", None).saveAsTable(INCITES_TABLE)
    # You might prefer partition-level overwrite if partitioning available.
else:
    # Incremental MERGE path (preferred)
    # 2) Build assembled rows for affected uids
    # read only necessary columns from source tables and join on uid
    uids = affected_uids_df.select("uid")
    # example entity reads: authorprofile, authorprofile_metric, organization, article_metric
    ap = spark.table(f"{DB}.authorprofile").select("uid", "author_key", "authorprofile_list")\
          .join(uids, on="uid", how="right")
    apm = spark.table(f"{DB}.authorprofile_metric").select("uid", "author_key", "ap_metric_cols...")\
          .join(uids, "uid", "right")
    org = spark.table(f"{DB}.organization").select("uid", "organization_key", "organization_list")\
          .join(uids, "uid", "right")
    article_m = spark.table(f"{DB}.article_metric").select("uid", "metric1", "metric2")\
          .join(uids, "uid", "right")
    article_ms = spark.table(f"{DB}.article_metrics").select("uid", "metrics_array")\
          .join(uids, "uid", "right")

    # join them. use broadcast hints if a table is small
    assembled = (
        uids
        .join(ap, on="uid", how="left")
        .join(apm, on="uid", how="left")
        .join(org, on="uid", how="left")
        .join(article_m, on="uid", how="left")
        .join(article_ms, on="uid", how="left")
        # compute or flatten fields into final schema
        .withColumn("assembled_ts", F.current_timestamp())
        .select("uid", "authorprofile_list", "ap_metric_cols...", "organization_list",
                "metric1", "metric2", "metrics_array", "assembled_ts")
    )

    # 3) MERGE into incites
    target = DeltaTable.forName(spark, INCITES_TABLE)
    # Build a temp view or temp table for merge source
    assembled.createOrReplaceTempView("stg_assembled_incites")

    merge_sql = f"""
    MERGE INTO {INCITES_TABLE} t
    USING stg_assembled_incites s
      ON t.uid = s.uid
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
    """
    spark.sql(merge_sql)

    # Optionally optimize / compact small files for affected partitions
    # spark.sql(f"OPTIMIZE {INCITES_TABLE} ZORDER BY (uid) WHERE uid IN (select uid from stg_assembled_incites)")
```

**🧱 Scala Assembly Pipeline (Incremental MERGE)**

```scala
// Databricks notebook or Scala job
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import io.delta.tables._

val spark = SparkSession.builder().getOrCreate()

// -----------------------------------------
// Configurations
// -----------------------------------------
val db = "analytics"
val incitesTable = s"$db.incites"

// Heuristic thresholds for large updates
val thresholdFraction = 0.05
val absOverwriteThreshold = 5000000L

// -----------------------------------------
// 1) Collect affected UIDs from change tables
// -----------------------------------------
val changeTables = Seq(
  s"$db.changes_authorprofile",
  s"$db.changes_authorprofile_metric",
  s"$db.changes_organization",
  s"$db.changes_organization_metric",
  s"$db.changes_funder",
  s"$db.changes_funder_metric",
  s"$db.changes_category",
  s"$db.changes_category_metric",
  s"$db.changes_article_metric",
  s"$db.changes_article_metrics"
)

val changesDFs = changeTables.flatMap { t =>
  try {
    Some(spark.table(t).select("uid").filter(col("uid").isNotNull))
  } catch {
    case e: Exception =>
      println(s"Warning: Cannot read $t - ${e.getMessage}")
      None
  }
}

if (changesDFs.isEmpty) {
  println("No changes detected. Exiting assembly.")
  dbutils.notebook.exit("No changes")
}

val affectedUidsDF = changesDFs.reduce(_ union _).distinct().cache()
val affectedCount = affectedUidsDF.count()

println(s"Number of affected UIDs: $affectedCount")

// -----------------------------------------
// 2) Check whether to MERGE incrementally or do large rewrite
// -----------------------------------------
val totalCount = spark.table(incitesTable).count()
val affectedFraction = affectedCount.toDouble / math.max(1, totalCount.toDouble)

println(s"Total incites count: $totalCount")
println(s"Affected fraction: $affectedFraction")

val largeUpdate = affectedCount > absOverwriteThreshold || affectedFraction > thresholdFraction

// -----------------------------------------
// 3) Read source tables for affected UIDs
// -----------------------------------------
val uids = affectedUidsDF

val authorProfile = spark.table(s"$db.authorprofile")
  .join(uids, Seq("uid"), "right")
  .select("uid", "author_key", "authorprofile_list")

val authorProfileMetric = spark.table(s"$db.authorprofile_metric")
  .join(uids, Seq("uid"), "right")
  .select("uid", "author_key", "metric_field1", "metric_field2")  // Replace with real metric fields

val organization = spark.table(s"$db.organization")
  .join(uids, Seq("uid"), "right")
  .select("uid", "organization_key", "organization_list")

val articleMetric = spark.table(s"$db.article_metric")
  .join(uids, Seq("uid"), "right")
  .select("uid", "metric1", "metric2")

val articleMetrics = spark.table(s"$db.article_metrics")
  .join(uids, Seq("uid"), "right")
  .select("uid", "metrics_array")

// -----------------------------------------
// 4) Assemble the final incites rows
// -----------------------------------------
val assembledDF = uids
  .join(authorProfile, Seq("uid"), "left")
  .join(authorProfileMetric, Seq("uid"), "left")
  .join(organization, Seq("uid"), "left")
  .join(articleMetric, Seq("uid"), "left")
  .join(articleMetrics, Seq("uid"), "left")
  .withColumn("assembled_ts", current_timestamp())
  .select(
    col("uid"),
    col("authorprofile_list"),
    col("metric_field1"),
    col("metric_field2"),
    col("organization_list"),
    col("metric1"),
    col("metric2"),
    col("metrics_array"),
    col("assembled_ts")
  )

assembledDF.createOrReplaceTempView("stg_assembled_incites")

// -----------------------------------------
// 5) MERGE or Overwrite into incites
// -----------------------------------------
if (largeUpdate) {
  println("Large affected set detected — performing overwrite strategy.")
  
  val existingDF = spark.table(incitesTable)
    .join(uids, Seq("uid"), "left_anti")
  
  val finalDF = existingDF.unionByName(assembledDF)

  finalDF.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(incitesTable)

} else {
  println("Performing incremental MERGE.")
  val deltaTarget = DeltaTable.forName(spark, incitesTable)

  deltaTarget.as("t")
    .merge(
      assembledDF.as("s"),
      "t.uid = s.uid"
    )
    .whenMatched()
    .updateAll()
    .whenNotMatched()
    .insertAll()
    .execute()
}

// -----------------------------------------
// 6) Optional: Optimize & Vacuum
// -----------------------------------------
// You can run this less frequently, e.g. daily
spark.sql(s"OPTIMIZE $incitesTable ZORDER BY (uid)")
// spark.sql(s"VACUUM $incitesTable RETAIN 168 HOURS")
```


📝 Notes:

- 	Replace placeholder columns (ap_metric_cols...) with your actual fields.
- 	You can construct the MERGE with explicit UPDATE SET clause to control which columns are replaced/preserved, and treat NULL carefully.
- 	Consider staging assembled results in a temp Delta table for auditability before merging.



📝 Key Notes for Scala Version

-	✅ Uses DeltaTable.forName(...).merge(...) for atomic upserts.
-	✅ Switches between incremental MERGE and overwrite when affected rows are large.
-	✅ Joins only affected UIDs to minimize read and shuffle.
-	✅ Uses unionByName to preserve schema alignment during overwrite.
-	✅ Easily extendable to include funder and category similarly to author/organization.
-	🧠 All select(...) column lists should be adjusted to your actual schema fields.

---

### Handling concurrency and ordering

- 	If pipelines run concurrently, use update_ts or run_id from each pipeline in change-log to determine last update and avoid reordering problems.
- 	Assembly should use the newest data (max update_ts) per source for the uid. If you get multiple updates per uid within the same assembly window, pick latest. Alternatively, run assembly after all pipelines for a time window finish.

---

### Failure handling and retries

- 	Assembly must be idempotent. Use MERGE semantics and an assembly checkpoint that records the last processed watermark (timestamp/version).
- 	If assembly fails mid-merge, Delta rollback + transaction semantics will prevent partial corruption. On retry, it can read change logs again.

---

### Schema evolution & object lists

You mentioned authorprofile, organization, funder, category are lists of objects. Recommendations:

- 	Keep these as array<struct<...>> columns in Delta.
- 	When merging, you can replace the entire list or merge elements depending on your downstream needs. Usually replace entire list for simplicity.
- 	If you need to roll up aggregated fields (counts, top-N), compute them in assembly and store as separate scalar columns for faster read.

---

### Metrics & monitoring

- 	Record metrics each run: affected_count, merged_count, duration, merge_time, bytes_read, bytes_written.
- 	Emit metrics to your monitoring system.
- 	Keep history table for assembly runs for debugging.

---

### When would per-entity partial updates (Option 1) be reasonable?

- 	If incites is extremely small and updates are extremely infrequent, or if each entity only touches disjoint keys and you really must minimize latency per entity. But in practice, Option 2 gives better consistency & maintainability.

---

### Summary checklist for implementing

1.	Enable CDF or make each pipeline write a change-log with (uid, op, ts, run_id).
2.	Central assembly pipeline:
  - 	compute affected_uids (union of change sources)
  - 	read minimal columns for uids
  - 	join + compute assembled rows
  - 	choose MERGE vs partition/full overwrite based on affected size heuristic
  - 	MERGE into incites
  - 	Optimize (periodically) and vacuum
3.	Make assembly idempotent and record watermark/checkpoint.
4.	Monitor and alert for long-running merges or high affected counts.
5.	Test end-to-end with deletes and concurrent updates.




---



##  Full Re-assembly per Affected record vs  Partial Field-level Updates


Good question — this is a core design choice for incremental materialized view assembly in Delta/Spark pipelines.

Let’s compare Option 1 (full re-assembly per affected record) vs Option 2 (partial field-level updates) in detail for your use case:

---

### 🧭 Option 1 – Full Re-Assembly for Affected uids

For every affected uid, re-read all relevant intermediate tables (entity + article-level) and rebuild the entire incites row, then MERGE it back.

✅ Pros
-	✔️ Simpler logic & maintenance: The assembly step has one clear responsibility — produce the entire “canonical” incites row per uid.
-	✔️ Schema evolution–friendly: Adding or changing fields in intermediate tables doesn’t require complex partial update logic.
-	✔️ Consistent data: Every update re-materializes the entire row → guarantees no stale fields are left behind from older updates.
-	✔️ Easier to debug: If something looks wrong in incites, you can rerun assembly for that uid and fix it.

⚠️ Cons
-	Might read more intermediate data than strictly necessary (e.g., authorprofile, funder, category even if only funder changed).
-	Slightly larger Spark job per run.

🚀 Performance notes
-	Spark joins by uid are efficient if you filter intermediate tables by the affected_uids first.
-	If your intermediate tables are partitioned or indexed by uid, reading all relevant data is typically fast, even for millions of rows.
-	The MERGE cost is the same whether you update a few columns or all columns for those rows.

👉 Real-world experience (including Databricks best practices):

For complex wide materialized views like incites, Option 1 is almost always preferred because Spark/Delta is optimized for reading & joining filtered data, and full row replacement avoids correctness issues.


---


### 🧭 Option 2 – Partial Field-Level Updates

Only pick the updated fields from the changed intermediate tables and MERGE those into existing incites rows.

✅ Pros
-	Potentially less data read and processed if only a small subset of fields change.
-	Might reduce computation if intermediate tables are extremely large and many fields are unrelated.

⚠️ Cons
-	⚠️ Much more complex logic: You need to track exactly which fields changed per pipeline and build per-field UPDATE SET clauses dynamically.
-	⚠️ Risk of stale data: If multiple entity pipelines update the same uid concurrently or out of order, partial updates can overwrite each other incorrectly.
-	⚠️ Harder to maintain: Any schema change or additional field requires code changes in partial update logic.
-	⚠️ MERGE still has to rewrite the full row physically (Delta stores row-level files, not columnar patches). So no real storage or write savings.

🚀 Performance notes
-	Delta MERGE does not do partial physical updates — it rewrites the entire row or file block anyway.
-	Partial updates may read less intermediate data, but savings are often marginal compared to complexity.

👉 In practice, Option 2 only makes sense if:
-	Each entity’s data lives in a separate physical table or column family.
-	You have ultra-wide tables (hundreds of columns) and want to isolate hot columns.
-	You are willing to invest in complex field-tracking logic and accept risk of stale joins.

⸻

📊 Summary Table


| Criteria                | Option 1: Full Re-Assembly                | Option 2: Partial Field Update                |
|-------------------------|-------------------------------------------|-----------------------------------------------|
| **Simplicity**          | ✅ Simple joins, one merge                 | ❌ Complex per-field logic                    |
| **Data Consistency**    | ✅ Always fresh & consistent               | ⚠️ Risk of stale fields / ordering issues     |
| **Schema Evolution**    | ✅ Easy to handle                          | ❌ Every new field needs logic                |
| **MERGE Performance**   | ⚡ Similar to partial (row-level rewrite)  | ⚡ No real physical benefit                   |
| **Spark Compute**       | Reads more intermediate data but scalable  | Slightly less read but marginal              |
| **Operational Robustness** | ✅ Easy retries & idempotency           | ⚠️ Complex to retry                           |


---


### ✅ Recommendation for Your Case

Given:
-	You already have separate pipelines for authorprofile, organization, funder, category, article metrics.
-	incites is a denormalized materialized view combining multiple entity & metric tables.
-	You’re using Delta + Spark (no column-family updates).

👉 Use Option 1: Rebuild entire incites records for affected uids.

This is more efficient overall, more reliable, and much easier to evolve and maintain long-term. The Spark join/filter model makes this practical even for millions of affected records.

If performance becomes a concern at massive scale, you can optimize Option 1 by:

-	Using Change Data Feed to only pick affected uids.
-	Caching or broadcasting small dimension tables.
-	Partition pruning and column pruning in reads.
-	Using merge vs partition overwrite heuristics (as shown in Scala/Python examples earlier).

⸻

📝 TL;DR

- 🔸 Option 1 (full reassembly) is the better, more efficient, and more maintainable solution in Delta/Spark.
- 🔸 Option 2 (partial updates) adds complexity with minimal performance gain — usually not worth it unless you have very unusual data shapes.



---


## Hybrid Strategy


✅ Great — a hybrid strategy is often the best in large-scale incremental pipelines like your incites table scenario.
Here’s a structured reasoning of why and how this hybrid approach works best:


---


### 🧠 Recap of Your Two Options


| Strategy                        | Description                                                                                                 | Pros                                                                 | Cons                                                                                   |
|----------------------------------|-------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| **Option 1: Full Record Reassembly** | For each affected UID/doc, rejoin and reassemble the entire record from all intermediate tables, then overwrite the full record in incites. | ✅ Simple logic<br>✅ Ensures consistency across all fields            | ❌ Expensive when intermediate data is large<br>❌ Repeated heavy joins for unchanged fields |
| **Option 2: Partial Incremental Update** | For each intermediate source, detect what changed, then patch only the affected fields in incites.         | ✅ Reduces computation<br>✅ Less data shuffled<br>✅ Efficient if only a few fields change | ❌ More complex merge logic<br>❌ Risk of inconsistent state if partial updates overlap incorrectly |


--- 


### 🧪 Option 3: Hybrid Strategy (Recommended)


🧱 Core Idea
-	For minor field-level updates (e.g., metrics in 1–2 intermediate tables), only patch those fields in the incites table.
-	For major updates or when multiple dependent metrics changed for a UID, fully reassemble that record from all intermediate sources to avoid inconsistency.

⸻

⚙️ Implementation Pattern

1.	Track Change Types per UID
-	Each intermediate table generates a change manifest or change log indicating:
    -	UID
    -	Field(s) affected
    -	Update type: partial or full (based on logic, e.g. number of sources changed or complexity)
-	Example manifest:

```json
[
  {"uid": "U123", "fields": ["funding_metrics"], "update_type": "partial"},
  {"uid": "U456", "fields": ["articles", "collaborations", "metrics"], "update_type": "full"}
]
```

2.	Branch Processing
-	Partial updates → Only read the minimal intermediate tables, and do a Delta MERGE updating the affected fields.
-	Full updates → Re-run the full reassembly logic for that UID (e.g., joins with all intermediate datasets) and replace the entire row.

3.	Batch Partial Updates Together
-	Group partial updates by intermediate source type for efficient joins.
-	Apply partial merges in one or few batches rather than per-record.

4.	Run Full Reassembly in Smaller Batches
-	For UIDs needing full reassembly, join across intermediate tables only for those UIDs (usually 5–10% of total) — this dramatically reduces the heavy join cost.

⸻


📈 Efficiency Gains


| Aspect           | Option 1 (Full)           | Option 2 (Partial)      | Hybrid                   |
|------------------|---------------------------|-------------------------|--------------------------|
| **CPU & Shuffle**    | 🔴 High (rejoins for all)   | 🟢 Low                  | 🟡 Moderate–Low           |
| **Complexity**       | 🟢 Simple                  | 🔴 High                 | 🟡 Moderate               |
| **Data Consistency** | 🟢 Strong                  | 🟡 Risky if not careful | 🟢 Strong                 |
| **Scalability**      | 🔴 Slows as data grows     | 🟢 Good for sparse changes | 🟢 Best of both        |


⸻

📝 When to Trigger Full Reassembly

Typical triggers for full updates:
-	Structural schema changes or metric recalculation across multiple datasets.
-	High number of intermediate tables changed for the same UID (e.g., >2).
-	Missing or corrupted records detected in the final incites table.

⸻

🧠 Pro Tip

Maintain a lightweight “UID change registry” Delta table that aggregates all changes detected from intermediate tables for each batch. This acts as a routing table to decide per-UID whether to run partial or full logic.


⸻

🧠 Key Considerations



| **Factor**                | **Partial Update**                                                                                                                                         | **Full Reassembly**                                                                                                   |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| **Number of fields**      | ❌ Updating hundreds of columns partially is complex and inefficient; large MERGE clauses are hard to maintain.                                             | ✅ Reassembling the full row for each UID is simpler and often faster than managing many individual field updates.     |
| **Schema Evolution**      | ❌ Risk of brittleness—adding or removing metric columns requires frequent changes to partial update logic.                                                 | ✅ Full reassembly automatically adapts to schema changes, regenerating the row structure from the latest schema.      |
| **Data Dependencies**     | ❌ Interdependent metrics (e.g., totals, derived indicators) can become inconsistent with partial updates.                                                  | ✅ Full reassembly guarantees all metrics are computed together, ensuring internal consistency.                        |
| **Volume of UIDs updated**| ✅ Efficient when only a few UIDs and a small number of metric columns are affected.                                                                       | ✅ Still efficient, as reassembling metrics for N UIDs is usually much cheaper than rebuilding the entire dataset.     |


--- 

### 🧪 Option 4:  Partial Updates at Object Level 


If your article_metric table has hundreds of fields, but they are grouped under structured objects like:

```json
{
  "uid": "...",
  "wos": { ... hundreds of metrics ... },
  "esci": { ... hundreds of metrics ... }
}
```

…then the decision between full reassembly vs. partial update becomes more nuanced — and this grouping actually helps a lot.
Let’s break it down carefully 👇



🧠 Scenario Recap

-	article_metric contains two nested objects, e.g.:
-	wos: metrics for Web of Science dataset
-	esci: metrics for Emerging Sources Citation Index dataset
-	Each object can contain dozens to hundreds of metrics (e.g., citation counts, normalized scores, etc.).
-	Incremental updates might affect either:
-	Only the wos section
-	Only the esci section
-	Or both

    

This is a hybrid in itself:
-	If any wos metric changes → rebuild the entire wos struct and overwrite only that column.
-	If any esci metric changes → rebuild the esci struct and overwrite only that column.

✅ Pros:
-	Efficient: you don’t touch unaffected metric groups.
-	Clean MERGE — you just set wos or esci to the new struct.
-	Schema evolution friendly — new metrics inside wos/esci don’t break the merge.
-	Much smaller execution plan than hundreds of per-field updates.


    
🧭 Real-World Best Practice

👉 Treat each logical metric block (wos, esci) as a unit, and fully reassemble that struct when any field inside it changes.
👉 Do not update individual metric fields inside these blocks.

This gives you:
-	✅ Better performance than reassembling both blocks every time.
-	✅ Cleaner code than per-field updates.
-	✅ Incremental efficiency if only wos or esci changed.
-	✅ Flexibility as the schema evolves.
    
```scala
import io.delta.tables._
import org.apache.spark.sql.functions._

val incitesDelta = DeltaTable.forName("incites")
val updatedWosDf = spark.table("article_metric_updates_wos")  // contains uid, wos struct
val updatedEsciDf = spark.table("article_metric_updates_esci") // contains uid, esci struct

// Update WOS block
incitesDelta.as("t")
  .merge(updatedWosDf.as("s"), "t.uid = s.uid")
  .whenMatched()
  .updateExpr(Map(
    "wos" -> "s.wos"
  ))
  .execute()

// Update ESCI block
incitesDelta.as("t")
  .merge(updatedEsciDf.as("s"), "t.uid = s.uid")
  .whenMatched()
  .updateExpr(Map(
    "esci" -> "s.esci"
  ))
  .execute()
```



🟡 Summary Table

| Approach                   | Granularity            | Performance           | Maintenance         | Best For                                 |
|----------------------------|------------------------|-----------------------|---------------------|------------------------------------------|
| Full record reassembly     | Whole record           | ❌ Can be overkill    | ✅ Simple           | Small metric blocks                      |
| Per-field partial update   | Individual fields      | ❌ Slow, complex      | ❌ Brittle          | Very small schema                        |
| Struct-level partial update| Logical metric blocks  | ✅ Efficient          | ✅ Robust           | ✅ Best for hundreds of metrics grouped logically |



✅ Final Recommendation

For a structure like:

```json
{ "wos": { ...hundreds metrics... }, "esci": { ...hundreds metrics... } }
```

👉 Use struct-level partial updates — i.e., fully reassemble only the affected object (wos or esci), not the entire record or individual fields.

This is both more efficient and more maintainable than full reassembly or per-field updates.

It fits perfectly with a hybrid assembly pipeline strategy.



