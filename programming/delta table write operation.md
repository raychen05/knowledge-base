
## Delta Table Write Operation


Short answer: it depends on how you overwrite.
Delta can retain old data or remove it, depending on the overwrite mode and options you use.


### 1️⃣ Overwrite specific partitions (old data in other partitions is retained)

If your Delta table is partitioned and you overwrite only some partitions, then:

- ✅ Only the targeted partitions are replaced
- ✅ Data in other partitions remains untouched
- ❌ Old data within the overwritten partitions is removed (logically)
  

Example: dynamic partition overwrite (Spark / Databricks)

```scala
spark.conf.set("spark.sql.sources.partitionOverwriteMode", "dynamic")

df.write 
  .format("delta") 
  .mode("overwrite") 
  .partitionBy("dt") 
  .saveAsTable("sales")
```

If df contains:

dt = 2024-01-01
dt = 2024-01-02

Then:
- Only partitions dt=2024-01-01 and dt=2024-01-02 are overwritten
- Other partitions (e.g. dt=2024-01-03) are retained

👉 This is the most common and safest behavior for incremental pipelines.

---

### 2️⃣ Overwrite the entire table (all partitions removed)

If you overwrite without dynamic partition mode, Delta treats it as a full table overwrite:

```scala
df.write 
  .format("delta") 
  .mode("overwrite") 
  .saveAsTable("sales")
```

Result:

- ❌ All existing partitions are removed
- ❌ All old data is logically deleted
- ✅ New data replaces the table entirely


---

### 3️⃣ Overwrite using replaceWhere (partition-safe & deterministic)


Delta provides a stronger, safer option using replaceWhere.

```scala
df.write 
  .format("delta") 
  .mode("overwrite") 
  .option("replaceWhere", "dt IN ('2024-01-01','2024-01-02')") 
  .saveAsTable("sales")
```


Behavior:

- ✅ Only the specified partitions are overwritten
- ✅ Delta validates that incoming data matches the condition
- ❌ Prevents accidental full-table overwrite

👉 Best practice for production pipelines.

---

### 4️⃣ What about “old versions” and time travel?

Even when data is overwritten:
- Delta does not physically delete files immediately
- Old data versions are still accessible via time travel

```sql
SELECT - FROM sales VERSION AS OF 42;
or

SELECT - FROM sales TIMESTAMP AS OF '2026-02-01';
```

Physical deletion happens only after:
- VACUUM runs
- And retention period expires (default 7 days)

---

### 5️⃣ Summary table

| Overwrite method | Other partitions kept? | Old data recoverable? |
|---|---|---|
| `overwrite` (default) | ❌ No | ✅ Yes (time travel) |
| Dynamic partition overwrite | ✅ Yes | ✅ Yes |
| `replaceWhere` | ✅ Yes | ✅ Yes |
| `VACUUM` | ❌ No | ❌ No |


✅ Recommendation (best practice)

For partitioned Delta tables:

- ✔ Use replaceWhere for safety
- ✔ Or use dynamic partition overwrite
- ❌ Avoid plain mode("overwrite") unless intentional full refresh


---

##  Recommendation matrix for CDC, backfill, and reprocessing with Delta tables


Below is a battle-tested recommendation matrix for CDC, backfill, and reprocessing with Delta tables, followed by concrete patterns and code you can directly adopt in Databricks / Spark.

---

### ✅ Golden Rules (apply to all cases)

1. Never use plain mode("overwrite") in production
2. Partition by a stable business key
    - Usually: event_date, ingest_date, or bucketed_event_date
3. Prefer idempotent writes
    - Re-running the same job must produce the same result
4. Keep CDC logic explicit (MERGE, not overwrite, when keys exist)

---

### 🔁 1. CDC (Change Data Capture) – BEST PRACTICE

✅ Use MERGE INTO (not overwrite)

CDC implies:
- Updates
- Deletes
- Late-arriving records
  
Pattern

```sql
MERGE INTO target t
USING cdc_source s
ON t.pk = s.pk
WHEN MATCHED AND s.op = 'D' THEN DELETE
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
```

Why this is best

| Benefit | Reason |
|---------|--------|
| Idempotent | Safe re-runs |
| Minimal I/O | Touches only affected rows |
| Handles deletes | Overwrite cannot |
| Late data safe | Yes |


When to partition

Partition target by:
- event_date (derived from business timestamp)
- NOT ingestion time

❌ Avoid
- Overwriting partitions for CDC
- Reprocessing entire days for single-row changes

---

### 🕰 2. Backfill (historical range reprocessing) – BEST PRACTICE


Backfill = replace known partitions deterministically

✅ Use replaceWhere (strongly recommended)

```scala
df_backfill.write 
  .format("delta") 
  .mode("overwrite") 
  .option("replaceWhere", "event_date BETWEEN '2023-01-01' AND '2023-01-31'") 
  .saveAsTable("target")
```

Why replaceWhere

| Advantage | Why |
|-----------|-----|
| Partition-scoped | Cannot wipe full table |
| Validated | Delta checks data matches condition |
| Deterministic | Re-run safe |
| Auditable | Clear intent |

Backfill checklist

- ✔ Incoming data must fully cover the range
- ✔ No partial partitions
- ✔ Range explicitly defined

---

### 🔄 3. Reprocessing (same logic, same window) – BEST PRACTICE

Reprocessing usually means:
- Bug fix
- Logic change
- Recompute last N days

### ✅ Use dynamic partition overwrite OR replaceWhere

**Option A*- – replaceWhere (preferred)

```scala
.option("replaceWhere", "event_date >= current_date() - 7")
```

**Option B*- – Dynamic overwrite (acceptable)

```scala
spark.conf.set("spark.sql.sources.partitionOverwriteMode", "dynamic")

df.write 
  .mode("overwrite") 
  .partitionBy("event_date") 
  .saveAsTable("target")
```


Decision rule

| Use case | Pattern |
|----------|---------|
| Known window | replaceWhere |
| Data-driven partitions | Dynamic overwrite |
| Strict safety | replaceWhere |


⚠️ 4. What NOT to do (common anti-patterns)

- ❌ Full table overwrite for CDC
- ❌ Overwrite without partition filter
- ❌ Partition by ingestion timestamp
- ❌ Mixed CDC + overwrite in same job
  

---


### 🧠 Recommended Unified Strategy (Production Grade)


**Bronze → Silver → Gold**

| Layer | Pattern |
|-------|---------|
| Bronze (raw) | Append-only |
| Silver (CDC) | `MERGE INTO` |
| Gold (aggregates) | `replaceWhere` |


### 🧪 Example: Combined CDC + Reprocessing Flow

1. CDC MERGE → Silver
2. Identify impacted event_date(s)
3. Recompute aggregates for those dates
4. replaceWhere overwrite in Gold

---

### 🧹 Data Retention

After stability window:

```sql
VACUUM target RETAIN 168 HOURS;
```

(never reduce below 7 days in prod unless fully audited)

---

### 📌 Decision Cheat Sheet

| Scenario | Best Pattern |
|----------|--------------|
| Row-level CDC | `MERGE INTO` |
| Historical backfill | `replaceWhere` |
| Rolling recompute | `replaceWhere` |
| Aggregation rebuild | `replaceWhere` |
| One-off repair | `replaceWhere` |
| Massive rewrite | Full overwrite (rare) |

If you want, I can:
- Map this to Databricks DLT
- Provide a CDC template with schema evolution
- Design a replay / backfill framework
- Review your current pipeline code and recommend fixes


---


## Partition Strategies


With Spark and ~200M+ rows, you want to be very intentional or you’ll drown in shuffle and small files.
Recommended layout for Spark (at this scale)


### ✅ Partition by pub_year

This is the right primary partition.

Why
- Massive partition pruning for time-based queries
- Predictable data volume per partition
- Keeps the number of partitions manageable
- Avoids metadata + small-file explosion

```scala
.write
.partitionBy("pub_year")
```

---

### 🚫 Don’t partition by (pub_year, category)

At 200M rows, this almost always backfires in Spark:

- Too many partitions (years × categories)
- Tons of tiny files
- Slower planning + task scheduling
- Often more shuffle, not less
- 
Even worse if categories are medium/high cardinality.

---

### How to actually reduce shuffle for per-(year, category) metrics

Partitioning alone won’t solve shuffle. You need data locality inside the year.

✅ Bucket or sort by category

This is the key move.

**Option 1**: Bucketing (best if tables are reused/joined)

```scala
.write
.partitionBy("pub_year")
.bucketBy(64, "category")
.sortBy("category")
```

Why
- GroupBy on category within a year needs less shuffle
- Joins on category become cheaper
- Fixed number of files per year (huge win)

Pick bucket count:
- 32 / 64 / 128 depending on cluster size
- Start with 64 for 200M rows

⚠️ Bucketing only helps if:
- You always write with the same bucket spec
- You read the table directly (not via random rewrites)

---

**Option 2**: Sort within partitions (lighter-weight, more flexible)

```scala
.write
.partitionBy("pub_year")
.sortBy("category")
```

Why
- Improves compression
- Faster aggregations
- Less spill during groupBy

This is safer if your data is frequently rewritten.

---

### Spark-side tuning (important)

Even with good layout, Spark defaults can hurt.

GroupBy tuning

```scala
spark.conf.set("spark.sql.shuffle.partitions", 400) // or ~2–3× total cores
```

If aggregations are heavy

```scala
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
```

---

### Summary (what to actually do)

- ✔ Partition: pub_year
- ✔ Within partition: bucket or sort by category
- ❌ Avoid: partitioning by (pub_year, category)
- ✔ Tune shuffle partitions
  
This setup:
- Minimizes shuffle
- Avoids small files
- Scales cleanly past 200M rows


---

## Optimal Spark strategy


Perfect — that simplification changes everything, and it lets us go for a much cleaner, faster plan. This is actually the best-case scenario for Spark.


### Key clarification (this unlocks the optimization)

- UT can belong to multiple categories
- Categories can belong to multiple schemas
- You’re allowed to ignore schema during computation
- Treat all categories as one global space
- Schema logic can be applied after metrics are computed

👉 This means you only need to optimize for (year, category, UT), once.

---

### The correct mental model


You are computing:

```css
metrics(year, category, UT)
```

Everything else (schemas, rollups, remapping) is downstream math, not storage or shuffle-critical.


---

### Optimal Spark strategy (storage + shuffle)


#### 1️⃣ Partitioning (non-negotiable)

Partition by pub_year only
```scala
PARTITIONED BY (pub_year)
```

Why:
- 40 partitions = ideal
- Perfect pruning
- No partition explosion
- Stable forever

- 🚫 No multi-column partitions
- 🚫 No category partitions

---

#### 2️⃣ Bucketing (this is the big win)

Since:
- 256 categories
- Joins + aggs always touch category
- Category cardinality is stable

👉 Bucket by category

```scala
BUCKETED BY (category) INTO 256 BUCKETS
SORTED BY (category, ut)
```

Why this works so well

- Hash distribution aligns exactly with category space
- Minimal skew
- Co-locates all rows of (year, category)
- GroupBy on category is almost shuffle-free
- Joins on category avoid rehashing

This is the single most important optimization in your case.

---

#### 3️⃣ Sorting inside buckets (don’t skip this)

```scala
SORT BY (category, ut)
```

Benefits:
- Streaming aggregation on UT
- Less memory pressure
- Fewer spills
- Better compression

---

### Shuffle strategy during computation


#### Pre-aggregation phase

When computing metrics:
```scala
GROUP BY pub_year, category, ut
```

Because of:
- Partition pruning on year
- Bucketing on category
- Sorting on UT

Spark mostly does:
- Map-side partial aggregation
- Minimal shuffle (only final combine)

---

#### Shuffle partitions tuning

Set this once for the job:
```scala
spark.sql.shuffle.partitions = 512
```

Then let AQE coalesce:

```scala
spark.sql.adaptive.enabled = true
spark.sql.adaptive.coalescePartitions.enabled = true
spark.sql.adaptive.skewJoin.enabled = true
```

---

### What you explicitly do NOT need anymore

- ❌ Schema-based partitioning
- ❌ Schema-based bucketing
- ❌ Per-schema aggregation
- ❌ Per-schema shuffles
- ❌ Exploding category space

Schemas become:
- Metadata joins
- Post-processing
- Cheap and fast

---

### Resulting execution characteristics

- One heavy pass over raw data
- Zero redundant scans
- One stable shuffle pattern
- Linear scalability
- Metrics reused everywhere

---

### Final recommended layout (copy/paste friendly)


Storage

```sql
PARTITION BY pub_year
BUCKET BY category INTO 256
SORT BY category, ut
```

Runtime

```scala
spark.sql.shuffle.partitions = 512
```

AQE enabled

If you want, next we can:
- Validate bucket count vs executor cores
- Handle skewed categories (if any are hot)
- Decide whether UT-level aggregation should be materialized or cached
- Design the downstream schema rollup so it’s 100% shuffle-free



---


### New Strategy for Bucketing



With 12,000 categories, 1,000–2,000 buckets strikes the best balance for distribution, shuffle minimization, and parallel execution. This will give you optimal performance for your metrics computation, especially with 40 years of data.



#### Cluster Size and Cores

- If your cluster has a lot of cores (e.g., >100), you can go closer to 2,000 buckets.
- If you're limited on cores, 1,000 buckets will likely be sufficient.
  

#### Final Setup for Spark (adjusted)

- Partition by pub_year — good for pruning and limiting scan size.
- Bucket by category into 1,000 to 2,000 buckets — suitable for your 12,000 categories.
- Sort by category, ut — ensures proper ordering inside buckets.

```scala
.write
.partitionBy("pub_year")
.bucketBy(1000, "category")   // or 2000 if you have many cores
.sortBy("category", "ut")
```

#### This setup ensures:

- Efficient data distribution across categories
- Minimized shuffle during joins and aggregation
- Good parallelism without exploding file sizes or causing bottlenecks


#### Why not 12,000 buckets?

While it seems intuitive to match the bucket count with the number of categories (12,000), it’s generally not optimal because:
- It will result in too many small files which Spark needs to process. Small files lead to metadata overhead, and Spark’s planning can get inefficient.
- It may cause excessive shuffle partitions during joins and aggregations, slowing things down.
- Performance won’t improve much beyond a certain point once you cross around 1,000–2,000 buckets, especially if your cluster has fewer cores.