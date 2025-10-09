
## Metric Pipeline Optimization


✅ Refined Requirement Description

We have a dataset of 80 million articles (UTs). Each article is associated with up to 23 schemas (e.g., WoS, ESCI), and each schema contains up to 10,000 categories (typically 10–10 categories per schema, but one schema may go up to 10K due to emerging topics).

Each article (UT) includes:

- ut_number
- pub_year
- citation_count
- article_type
- categories_xxx — where xxx refers to a schema name (e.g., categories_wos), each being an array of category names under that schema.

💡 Goal

1. For each schema, per category, per year, per document type, compute:

- Average citation count
- Normalized Citation Impact (NCI)
- Percentile (e.g., 90th)

2. For each UT, determine the best value of NCI and percentile per schema.

- Since a UT can be assigned to multiple categories per schema, we want the best (i.e., max) NCI and percentile across all its categories in that schema.


---


This is a big-but-common analytics problem. I’ll give a practical, production-ready strategy and a Spark (Scala) pipeline you can implement on Databricks (or any Spark cluster). The plan prioritizes:

- 	one logical pass over the large UT table where feasible,
- 	using percentile_approx (approximate, scalable) for group percentiles,
- 	partitioning & bucketing recommendations to reduce shuffles,
- 	a clear sequence of DataFrame transforms so you can checkpoint / persist intermediate results,
- 	how to compute per-UT metrics and then “best” per-UT per-schema.

---

#### Short summary / high level

1.	Explode: turn each UT row into many rows (ut, pub_year, article_type, schema, category, citation_count).
2.	Persist/write the exploded dataset partitioned by pub_year (and optionally schema) for efficient reuse.
3.	Compute group metrics per (pub_year, schema, category, article_type):
  - 	count, sum, avg, (and optional NCI baseline), percentiles using percentile_approx.
4.	Join exploded rows back to group metrics (co-partition both sides) to compute per-UT-per-(schema,category) derived values: nci = citation / group_avg, pct = percentileFromCutoffs(...) (use a UDF to bucket into deciles or find percentile from cutoffs).
5.	Aggregate per-UT-per-schema to choose the “best” (e.g. maximal) NCI/percentile across categories for that UT and schema.
6.	Persist final outputs (Delta tables) partitioned by pub_year (and possibly bucketed by schema or category) for fast reads.

--- 

#### Important design notes / tradeoffs

- 	Percentiles: exact percentiles at high cardinality are expensive. Use percentile_approx (Spark) with a suitable accuracy parameter. It computes cutoffs per group in one aggregation.
- 	Group cardinality: worst-case groups = years * schemas * categories * article_types. You mentioned up to 10k categories for an emerging schema; multiply that by years (~50?) → potentially millions of groups. Make sure to choose an aggregation strategy that distributes work and does not blow memory.
- 	Partitioning:
  - 	Partition the stored exploded data and metrics by pub_year (highly selective, natural partition).
  - 	Also partition by schema if it helps queries. Avoid partitioning by too many distinct values (like category) — that’s bad.
  - 	Use bucketing (Hive-style) on category if you have many categories and you need join performance and you can control table writes (Delta + Z-order is another option).
- 	Avoiding shuffles:
  - 	Co-partition/co-repartition both DataFrames on the join keys BEFORE the join: df.repartition(n, col("pub_year"), col("schema"), col("category")).
  - 	Tune spark.sql.shuffle.partitions to a sensible number for your cluster (not the default 200).
  - 	Use map-side combine where possible (groupBy on hashed keys with agg uses combineByKey under the hood).
  - 	Scale: use .persist() / write intermediate results to Delta and checkpoint for long pipelines.

---

#### Assumptions / definitions used below

- 	UT table fields: ut_number: String, pub_year: Int, citation_count: Long, article_type: String, and for each schema a column categories_<schema> that is an array of strings (category names). Example categories_wos: Array[String].
- 	We compute group: (pub_year, schema, category, article_type).
- 	NCI (Normalized Citation Impact) = citation_count / avg_citation_of_group — adjust if your NCI definition differs.
- 	We aim to compute decile and percentile per UT per group. For percentile we compute percentile cutoffs via percentile_approx and then map each UT’s citation to the percentile/decile via a UDF.
- 	Use Delta tables as storage.


---

#### End-to-end Scala pipeline (full example)

Below is a complete pipeline skeleton. You should adapt configuration (paths, table names, cluster tuning) to your environment.

```scala
import org.apache.spark.sql._
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.spark.storage.StorageLevel

val spark: SparkSession = SparkSession.builder().getOrCreate()
import spark.implicits._

// ========== CONFIG ==========
val rawTable = "catalog.schema.ut_raw"           // existing raw UT Delta table
val explodedPath = "s3://.../tmp/exploded/"     // intermediate storage
val groupMetricsTable = "catalog.schema.group_metrics"
val utMetricsTable = "catalog.schema.ut_metrics"        // per-UT-per-category metrics
val utBestTable = "catalog.schema.ut_best_per_schema"   // final best per UT per schema

val schemas = Seq("wos","esci", "schema3", "...") // list of schema names
val percentilesToCompute = (1 to 99).map(_/100.0).toArray // or use deciles [0.1,0.2,...] if you only want deciles
val percentileAccuracy = 10000 // tune: higher -> more accurate, more memory

// set shuffle partitions reasonably to cluster size
spark.conf.set("spark.sql.shuffle.partitions", "200") // tune to your cluster cores

// ========== 1) Explode UT rows into (ut,year,type,schema,category,citation) ==========
def explodeSchemas(df: DataFrame): DataFrame = {
  // for each schema column categories_<schema> (array<string>), explode into rows
  val basic = df.select($"ut_number", $"pub_year", $"citation_count", $"article_type", 
                        $"some_other_fields") // keep fields you need

  // start with base DF and iteratively union for each schema
  val explodedPerSchema = schemas.map { s =>
    val colName = s"categories_${s}"  // e.g., categories_wos
    // only keep rows where column exists
    df.filter(col(colName).isNotNull)
      // explode the array to get one row per category assignment
      .select(
        $"ut_number",
        $"pub_year",
        $"citation_count".cast("double"),
        $"article_type",
        lit(s).as("schema"),
        explode_outer(col(colName)).as("category")
      )
      .filter($"category".isNotNull)
  }
  // union all schema-specific exploded frames
  explodedPerSchema.reduce(_.unionByName(_))
}

val raw = spark.table(rawTable)
val exploded = explodeSchemas(raw)
  .withColumn("category", trim($"category"))
  .withColumn("source_file", lit(null: String)) // optional
  .persist(StorageLevel.MEMORY_AND_DISK)

// optional: write exploded as Delta partitioned by pub_year (helps repeated runs)
exploded.write.format("delta")
  .mode("overwrite")
  .partitionBy("pub_year")
  .option("overwriteSchema","true")
  .save(explodedPath)

// read back partitioned for downstream processing (ensures good partition pruning)
val explodedDf = spark.read.format("delta").load(explodedPath).repartition(
  col("pub_year"), col("schema")
).persist(StorageLevel.MEMORY_AND_DISK)

// ========== 2) Compute group-level metrics (count, avg, percentiles) ==========
val groupKeyCols = Seq("pub_year","schema","category","article_type")

// compute count & avg & other basic aggregates
val groupAggs = explodedDf
  .groupBy(groupKeyCols.map(col): _*)
  .agg(
    count(lit(1)).as("cnt"),
    sum("citation_count").as("sum_citations"),
    avg("citation_count").as("avg_citations"),
    stddev("citation_count").as("std_citations"),
    expr(s"percentile_approx(citation_count, array(${percentilesToCompute.mkString(",")}), $percentileAccuracy) as percentile_cutoffs")
  )
  .persist(StorageLevel.MEMORY_AND_DISK)

// write group metrics to Delta partitioned by year and schema (avoid partitioning by category)
groupAggs.write.format("delta")
  .mode("overwrite")
  .partitionBy("pub_year","schema")
  .saveAsTable(groupMetricsTable)

// ========== 3) Join exploded UTs to group metrics to compute per-UT derived metrics ==========
val groups = spark.table(groupMetricsTable)

// co-partition both by pub_year & schema for efficient join
val explodedRepart = explodedDf.repartition(col("pub_year"), col("schema"))
val groupsRepart = groups.repartition(col("pub_year"), col("schema"))

// join on group keys
val joined = explodedRepart.join(groupsRepart,
  explodedRepart("pub_year") === groupsRepart("pub_year") &&
  explodedRepart("schema") === groupsRepart("schema") &&
  explodedRepart("category") === groupsRepart("category") &&
  explodedRepart("article_type") === groupsRepart("article_type"),
  "left"
).select(
  explodedRepart("ut_number"),
  explodedRepart("pub_year"),
  explodedRepart("schema"),
  explodedRepart("category"),
  explodedRepart("article_type"),
  explodedRepart("citation_count"),
  groupsRepart("cnt"),
  groupsRepart("avg_citations"),
  groupsRepart("percentile_cutoffs")
)

// helper UDF: compute percentile rank (0..1) from cutoffs array produced by percentile_approx
val computePercentileUDF = udf { (value: Double, cutoffs: Seq[Double]) =>
  if (value == null || cutoffs == null || cutoffs.isEmpty) null
  else {
    // find first cutoff >= value; return index/length as percentile approx
    val idx = java.util.Arrays.binarySearch(cutoffs.toArray.asInstanceOf[Array[Double]], value) match {
      case i if i >= 0 => i
      case i => -i - 1
    }
    val pct = idx.toDouble / cutoffs.size.toDouble
    pct
  }
}

// compute nci and percentile estimate, decile if desired
val perUtCategory = joined.withColumn("nci", $"citation_count" / $"avg_citations")
  .withColumn("pct_est", computePercentileUDF($"citation_count", $"percentile_cutoffs"))
  .withColumn("decile", ceil($"pct_est" * 10).cast("int"))
  .persist()

// write per-UT-per-category metrics
perUtCategory.write.format("delta").mode("overwrite").saveAsTable(utMetricsTable)

// ========== 4) Compute best metric per UT per schema ==========
val bestPerUtSchema = perUtCategory.groupBy("ut_number","schema")
  .agg(
    max("nci").as("best_nci"),
    max("pct_est").as("best_pct"),
    // optionally collect which category produced best_nci
    first(struct($"nci",$"category"), ignoreNulls=true).as("sample") // not perfect; you can use window to pick category
  )

// write final table
bestPerUtSchema.write.format("delta").mode("overwrite").saveAsTable(utBestTable)
```


---

### Notes on key pieces above


#### Percentile computation and mapping

- 	We compute percentile_cutoffs per group using percentile_approx(citation_count, array(...), accuracy) — this returns an array of cutoff values for requested percentiles.
- 	The computePercentileUDF binary-searches the cutoffs to estimate percentile. This is an approximation driven by percentile_approx accuracy.
- 	If you only need deciles, compute percentiles at [0.1,0.2,...,1.0] which is much cheaper (smaller arrays to store & process).

---

#### NCI

- 	In the example nci = citation_count / avg_citations. If your NCI formula differs (e.g., normalized by world average or by expected counts), adjust the expression.

---

#### Memory & shuffle tuning

- 	Set spark.sql.shuffle.partitions to the number of reduce slots your cluster can handle (cores). For example, on a cluster with 100 cores, use ~200 partitions as a starting point.
- 	Use repartition on the exact join keys (pub_year, schema) so join happens with minimal shuffle; ensuring both sides are partitioned the same reduces data movement.
- 	Persist large intermediate DataFrames to disk-backed memory to avoid recomputation.

--- 
#### Storage / Table layout

- 	Exploded data: write to Delta, partitioned by pub_year (and optionally schema), do NOT partition by category if category cardinality is high.
- 	Group metrics: write partitioned by pub_year and schema. Each partition will contain many categories but queries that restrict year & schema will read only necessary partitions.
- 	Ut metrics & best table: also partition by pub_year or store partition-less if you query by UT.

---
####  Handling very large group cardinality (10k categories * many years)

- 	If groups are too many to process in one job, process by shards: run pipeline in parallel by year or by schema slices (submit one job per year or per schema). This limits peak memory needs and enables parallel cluster usage.
- 	Use composite/paged aggregations if you try to do aggregations purely in Elasticsearch; in Spark you can handle large group counts but tune resources.

---
####  Avoiding full-table shuffles

- 	Use map-side combine (Spark groupBy with aggregate will do this by default).
- 	Co-partition before joins to avoid unnecessary shuffles.
- 	Where possible, do per-year processing so that data movement is limited.

---
#### Extra production touches


- 	Checkpointing and streaming: if you ingest new UTs incrementally, run this pipeline per-day or per-batch; append new UTs and recompute group metrics only for affected (pub_year, schema, category, type) values.
- 	Incremental recompute: if only a subset of UTs changed, recompute groups for those (year,schema,category) only, then update joins.
- 	Broadcast small lookups: if some dimension (like article_type mapping or small category metadata) is small, broadcast it to avoid join shuffles.
- 	Testing: test pipeline on a sample partition (one year / one schema) first; validate percentile UDF mapping.


---

##  How how to incrementally update group metrics and only re-join on affected groups.

This is exactly the pain point when you scale up to tens of millions of documents with lots of grouping dimensions (year, category, schema, article_type). If you recompute all group metrics every time, the shuffle cost will kill you. Instead, you want an incremental strategy where only affected groups are recomputed. Here’s how you can design it in Spark (Scala) efficiently:



#### 🔑 Key Idea

- 	Partition by stable dimensions → pub_year, schema, article_type, category.
- 	Precompute group aggregates (avg citation, NCI, percentiles) and store them in a Delta table.
- 	On new/changed UTs (from daily/weekly loads), extract only the set of affected groups (grouping keys that those UTs belong to).
- 	Recompute metrics only for those groups, then overwrite/update just those partitions in the metrics table.

---

### ⚙️ Step-by-Step Approach

#### 1. Define Group Keys

For each schema category assignment, explode categories into rows:

```scala
val exploded = utDF
  .withColumn("schema", lit("wos")) // repeat for each schema field
  .withColumn("category", explode($"categories_wos"))
  .select($"ut_number", $"pub_year", $"citation_count", $"article_type", $"schema", $"category")
```

Now your grouping key is:

```text
(pub_year, schema, category, article_type)
```
---

#### 2. Maintain Precomputed Metrics Table

Create a Delta table like:

```scala
CREATE TABLE metrics_per_group (
  pub_year INT,
  schema STRING,
  category STRING,
  article_type STRING,
  avg_citation DOUBLE,
  nci DOUBLE,
  percentile DOUBLE,
  updated_at TIMESTAMP
)
USING DELTA
PARTITIONED BY (pub_year, schema)
```


Partitioning on (pub_year, schema) keeps updates local and avoids giant shuffles.

---

#### 3. Incremental Update Strategy
   
	1.	Identify changed UTs (inserts/updates/deletes).
- 	If a UT changed → explode its schema categories → collect the set of affected (pub_year, schema, category, article_type) group keys.

```scala
val affectedGroups = changedUTs
  .withColumn("schema", lit("wos"))
  .withColumn("category", explode($"categories_wos"))
  .select("pub_year", "schema", "category", "article_type")
  .distinct()
```

	2.	Recompute metrics only for those groups:


```scala
val recomputed = exploded
  .join(affectedGroups, Seq("pub_year","schema","category","article_type"))
  .groupBy("pub_year","schema","category","article_type")
  .agg(
    avg($"citation_count").as("avg_citation"),
    expr("avg(citation_count) / avg(citation_count) OVER()").as("nci"), // example NCI calc
    callUDF("percentile_approx", $"citation_count", lit(100)).as("percentile")
  )
  .withColumn("updated_at", current_timestamp())
```

	3.	Merge back into the metrics Delta table:

```scala
recomputed.createOrReplaceTempView("updates")

spark.sql("""
MERGE INTO metrics_per_group m
USING updates u
ON m.pub_year = u.pub_year
AND m.schema = u.schema
AND m.category = u.category
AND m.article_type = u.article_type
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
""")
```

---

#### 4. Compute Best Metric Per UT

After metrics per group are updated, compute UT-level “best values”:


```scala
val bestPerUT = exploded
  .join(metricsPerGroup, Seq("pub_year","schema","category","article_type"))
  .groupBy("ut_number","schema")
  .agg(
    max($"nci").as("best_nci"),
    max($"percentile").as("best_percentile")
  )
```

This can also be done incrementally for only UTs that belong to affected groups.

---

#### 🚀 Optimizations

- 	Broadcast small lookup tables (like affectedGroups) to avoid shuffles.
- 	Partition pruning works well since metrics_per_group is partitioned by (pub_year, schema).
- 	Z-ORDER by category/article_type if you need frequent selective queries.
- 	For percentiles, precompute with percentile_approx to avoid expensive exact ranks.

✅ This way, you only re-aggregate the groups touched by updated UTs, instead of the full 80M dataset. Shuffle is limited to the subset of affected partitions.


---
## Spark Config Tuning


Spark config tuning is critical here, because you’re dealing with 80M docs × thousands of groups. I’ll show you baseline tuning values that you can adapt depending on your Databricks cluster size (say, 8–16 worker nodes with 32–64 GB RAM each).


---


#### ⚙️ Spark Config Tuning Example

Here’s a Scala snippet you can drop into your pipeline notebook:

```scala
// ==============================
// Cluster / Execution tuning
// ==============================

// Parallelism → generally 2–3 × total cores in cluster
spark.conf.set("spark.sql.shuffle.partitions", "2000")  // tune by cluster size (see below)

// Adaptive execution (auto-adjust shuffle partitions)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.shuffle.targetPostShuffleInputSize", "256MB")

// Joins → broadcast when small
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)  // disable if memory issues
spark.conf.set("spark.sql.broadcastTimeout", "1200")        // 20 min for large lookups

// Shuffle + spill
spark.conf.set("spark.sql.shuffle.compress", "true")
spark.conf.set("spark.sql.shuffle.spill.compress", "true")
spark.conf.set("spark.memory.fraction", "0.6")    // fraction for execution/storage
spark.conf.set("spark.memory.storageFraction", "0.4")

// Caching (if reusing UT → category exploded DF multiple times)
spark.conf.set("spark.databricks.io.cache.enabled", "true")

// Skew + skew handling
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
```

---

#### 📊 How to Size spark.sql.shuffle.partitions

Rule of thumb:

- 	#partitions ≈ 2–3 × total CPU cores in cluster
- 	Partition size target ≈ 200–300 MB each post-shuffle.

Examples:

#### Cluster Configuration

| Cluster Size             | Total Cores | Shuffle Partitions (spark.sql.shuffle.partitions) |
|--------------------------|-------------|----------------------------------------------------|
| 8 nodes × 16 cores = 128 | 128         | 300–400                                            |
| 16 nodes × 16 cores = 256| 256         | 600–800                                            |
| 32 nodes × 32 cores = 1024| 1024        | 2000–2500                                          |

Since you’re working with 80M docs, if you’re on 16 × 32-core = 512 cores, start with 1000–1500.


#### 🏎️ Additional Delta Lake Tuning


```scala
// Z-order by category for pruning
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")
spark.conf.set("spark.databricks.delta.autoCompact.enabled", "true")
```

Run periodically:

```sql
OPTIMIZE metrics_per_group ZORDER BY (category, article_type);
```

🚀 Rule of Thumb

	1.	Start with 200 MB shuffle partition target.
	2.	Enable adaptive query execution (AQE).
	3.	Monitor spill (shuffle spill bytes) in Spark UI. If high → increase partitions or scale nodes.
	4.	For percentile-heavy queries → use approximate UDFs to avoid O(N log N).


---

## Avoiding full-table shuffles

 let’s break this down into detailed explanation + Spark Scala implementation examples for your UT + schema + categories pipeline. The focus is on avoiding full-table shuffles while computing metrics (avg citation, NCI, percentiles, etc.) for each schema, category, year, and article type.

---

#### 🔹 Why Full-Table Shuffles Kill Performance

- 	A shuffle happens when Spark redistributes data across executors by key (e.g., groupBy, join).
- 	On 80M rows × 10k categories, a full shuffle = network + disk I/O bottleneck.
- 	Avoiding full-table shuffles means:
  - 	Keep as much aggregation local (map-side combine).
  - 	Partition data before joins so Spark doesn’t reshuffle.
  - 	Process smaller subsets (per year / schema) independently.


---

#### 🔹 Strategy to Avoid Shuffles

1. Map-Side Combine (default in groupBy)

When you do df.groupBy(...).agg(...), Spark performs map-side aggregation before shuffling partial results, so only reduced values move across the network.

- ➡️ Good: groupBy on small key cardinality fields (year, article_type).
- ➡️ Bad: groupBy on high-cardinality keys (UT number, schema categories).

---

2. Co-Partition Before Joins

If you must join, ensure both sides are partitioned by the same key.

- 	Store large dimension/reference tables as Delta partitioned by join keys.
- 	Repartition fact DF by the same key before join.
- 
This avoids shuffle → Spark can just scan aligned partitions.

---

3. Per-Year Processing

Since metrics are per-year:

- 	Partition data by pub_year.
- 	Run separate aggregations per year.
- 	Reduces shuffle domain from entire 80M → smaller year slices.
- 	Can be implemented via repartition(pub_year) or Delta Z-ORDER pub_year for pruning.



---

#### 🔹 Implementation (Scala + Spark)

Example Dataset

```scala
case class Article(
  ut: String,
  pub_year: Int,
  citation_count: Long,
  article_type: String,
  categories_wos: Seq[String],
  categories_esci: Seq[String]
)

val df = spark.read.format("delta").load("/mnt/delta/articles")
```

---

Step 1. Explode Categories Per Schema

Each schema has its own categories array; we normalize into (schema, category).

```scala
import org.apache.spark.sql.functions._

val exploded = df
  .withColumn("schema", lit("wos"))
  .withColumn("category", explode($"categories_wos"))
  .select($"ut", $"pub_year", $"citation_count", $"article_type", $"schema", $"category")
  .union(
    df.withColumn("schema", lit("esci"))
      .withColumn("category", explode($"categories_esci"))
      .select($"ut", $"pub_year", $"citation_count", $"article_type", $"schema", $"category")
  )
```

This keeps things narrow: only columns we need.

---

Step 2. Partition Data by Year (limit shuffle scope)

```scala
val partitioned = exploded.repartition($"pub_year")
```

Now aggregations will run per year slice → less data per shuffle stage.


---

Step 3. Compute Metrics Per Group (Map-Side Combine)

```scala
val grouped = partitioned
  .groupBy($"schema", $"category", $"pub_year", $"article_type")
  .agg(
    avg($"citation_count").as("avg_citations"),
    expr("percentile_approx(citation_count, 0.5)").as("median_citations"),
    expr("percentile_approx(citation_count, array(0.9,0.95,0.99))").as("percentiles"),
    (sum($"citation_count") / count($"ut")).as("nci")
  )
```

👉 Here Spark will do map-side combine before shuffle → reduces traffic.

---

Step 4. Best Metrics Per UT (Avoid Full Join Shuffle)

Instead of joining metrics back to UT (which would shuffle 80M rows), we:

	1.	Compute per-UT metrics per schema separately.
	2.	Use window function per UT to pick “best” value.

```scala
import org.apache.spark.sql.expressions.Window

val w = Window.partitionBy($"ut", $"schema").orderBy($"nci".desc)

val bestPerUT = exploded
  .join(grouped, Seq("schema", "category", "pub_year", "article_type"))
  .withColumn("rn", row_number().over(w))
  .where($"rn" === 1)   // keep only best row per UT+schema
  .drop("rn")
```

Step 5. Optimize Storage for Incremental Updates
- 	Store results in Delta, partitioned by year + schema.
- 	When new data comes in, only recompute affected partitions (per-year incremental).

```scala
bestPerUT.write
  .format("delta")
  .mode("overwrite")
  .partitionBy("pub_year", "schema")
  .save("/mnt/delta/metrics_best_ut")
```

----
#### 🔹 How This Avoids Shuffles

	1.	Per-year repartition → metrics computed per slice.
	2.	Map-side combine → shuffle carries only reduced aggregates.
	3.	Explode early, project narrow → small, efficient shuffle payload.
	4.	Window function avoids big joins → Spark does sort per partition.
	5.	Delta partitioning keeps incremental updates scoped.



---


## Incremental Update Plan 


Excellent — let’s extend the pipeline with an incremental update plan using Delta Lake Change Data Feed (CDF) so we don’t have to recompute metrics for all 80M UTs every time. Instead, we only reprocess affected UTs, categories, and years.

---

#### 🔹 Key Idea
	1.	Articles table (80M UTs) is stored in Delta with CDF enabled.
	2.	On every update (new / modified / deleted articles), we read only changed rows.
	3.	Identify the groups impacted (year + schema + category + article_type).
	4.	Recompute metrics only for those groups.
	5.	Merge back into the metrics Delta table.

---

#### 🔹 Enabling CDF on the Articles Table

When you first create the articles table, enable CDF:

```sql
ALTER TABLE articles SET TBLPROPERTIES (delta.enableChangeDataFeed = true);
```

Now all appends/updates/deletes will track changes.

---

#### 🔹 Step 1. Read Changed Articles

In Spark Scala:

```scala
val changed = spark.read.format("delta")
  .option("readChangeFeed", "true")
  .option("startingVersion", 123)   // or use timestamp
  .table("articles")
  .filter("_change_type != 'delete'")  // keep inserts + updates
```

---

#### 🔹 Step 2. Identify Impacted Groups

Since metrics are grouped by (schema, category, pub_year, article_type), we derive impacted groups:

```scala
val impactedGroups = changed
  .withColumn("schema", lit("wos"))
  .withColumn("category", explode($"categories_wos"))
  .select($"schema", $"category", $"pub_year", $"article_type")
  .distinct()
```

This is usually small (just the categories touched by the changed UTs).

---

#### 🔹 Step 3. Recompute Metrics Only for Impacted Groups

Filter the full articles table by the impacted groups → scoped recompute:

```scala
val articles = spark.table("articles")

val impactedArticles = articles.join(
  broadcast(impactedGroups),
  Seq("schema", "category", "pub_year", "article_type")
)

val updatedMetrics = impactedArticles
  .groupBy($"schema", $"category", $"pub_year", $"article_type")
  .agg(
    avg($"citation_count").as("avg_citations"),
    expr("percentile_approx(citation_count, 0.5)").as("median_citations"),
    expr("percentile_approx(citation_count, array(0.9,0.95,0.99))").as("percentiles"),
    (sum($"citation_count") / count($"ut")).as("nci")
  )
```

---

#### 🔹 Step 4. Merge Into Metrics Table

Use Delta MERGE to overwrite only the affected groups:

```scala
import io.delta.tables._

val metricsTable = DeltaTable.forPath(spark, "/mnt/delta/metrics")

metricsTable.as("t")
  .merge(
    updatedMetrics.as("s"),
    "t.schema = s.schema AND t.category = s.category AND t.pub_year = s.pub_year AND t.article_type = s.article_type"
  )
  .whenMatched.updateAll()
  .whenNotMatched.insertAll()
  .execute()
```

---

#### 🔹 Step 5. Best Per UT (Incremental)

For per-UT best metrics:
- 	Collect impacted UTs from changed.
- 	Recompute only for those UTs by joining with metrics for their categories.

```scala
val impactedUTs = changed.select($"ut").distinct()

val bestPerUT = impactedArticles
  .join(updatedMetrics, Seq("schema", "category", "pub_year", "article_type"))
  .withColumn("rn", row_number().over(Window.partitionBy($"ut", $"schema").orderBy($"nci".desc)))
  .filter($"rn" === 1)
```

Then MERGE this into your best_metrics_per_ut Delta table.

---

#### 🔹 Advantages of This Plan

- 	No full shuffle across all 80M rows → recompute only impacted slices.
- 	Per-year, per-schema partitions keep I/O localized.
- 	MERGE on Delta makes metrics table always up-to-date.
- 	Incremental recomputation ensures fast CI/CD runs and nightly updates.

⸻

✅ With this design, even if a customer updates 100k UTs in a batch, you only touch the categories and years those UTs belong to — not the entire dataset.


---

##  Decile-only Version

let’s build a decile-only version (10 groups instead of full percentiles) and show how to tune the cluster for incremental runs. This will give you much faster performance and lower memory usage.

---

#### 1. Decile Computation (Instead of Full Percentiles)

Instead of computing all percentiles (0–100), you compute only decile cutoffs (10, 20, …, 90).
That way:
- 	Fewer values to calculate.
- 	Smaller shuffle & aggregation footprint.
- 	Works well for dashboards/summary metrics.

Example Spark Code (Incremental + Deciles)

```scala
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Assume df has schema: group_id, year, value, updated_flag

# 1. Filter only updated partitions/groups
changed_groups = df.filter("updated_flag = true").select("group_id").distinct()

# 2. Restrict source data to only those groups
affected_df = df.join(changed_groups, "group_id", "inner")

# 3. Compute decile cutoffs
# Instead of approx_percentile(..., array of 0..1), use just 10 deciles
deciles = affected_df.groupBy("group_id", "year").agg(
    F.expr("approx_percentile(value, array(0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9), 100) as deciles")
)

# 4. Flatten deciles into columns
deciles = deciles.select(
    "group_id", "year",
    *[F.col("deciles")[i].alias(f"decile_{(i+1)*10}") for i in range(9)]
)

# 5. Upsert back into Delta table
(
    deciles.write.format("delta")
    .mode("overwrite")
    .option("replaceWhere", "group_id IN (SELECT group_id FROM changed_groups)") 
    .save("/mnt/metrics/deciles")
)
```

---

#### 2. Why This Avoids Full Shuffles

- 	groupBy("group_id", "year") → Spark does map-side combine before shuffle.
- 	Only affected groups are re-joined and re-aggregated, not the entire table.
- 	approx_percentile runs per-group in memory, so it avoids exploding intermediate rows.

---

#### 3. Cluster Tuning for Incremental Jobs

Since incremental jobs process smaller partitions, your Spark conf can be lighter than for full baselines.

Recommended Configs (example: 32-core cluster, 256 GB RAM)

```scala
spark.conf.set("spark.sql.shuffle.partitions", "64")
# Fewer partitions than baseline (default 200), since less data is moved.

spark.conf.set("spark.sql.adaptive.enabled", "true")
# Adaptive query execution helps shrink shuffles at runtime.

spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
# Skew handling for hot groups.

spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
# Prevents over-partitioning when only a few groups are updated.

spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")
spark.conf.set("spark.databricks.delta.autoCompact.enabled", "true")
# Keeps Delta files small + avoids too many tiny files during incremental upserts.
```
---

#### 4. Scaling Rules of Thumb

- 	Baseline runs (full recompute): higher spark.sql.shuffle.partitions (e.g., 200–400), big executors.
- 	Incremental runs (10–100 groups at a time): reduce shuffle partitions (e.g., 32–64), let AQE handle skew.
- 	Per-year processing: partition Delta tables by year → when updating only 2025 data, Spark skips older files.

---

#### ✅ This setup gives you:

- 	Decile summaries (fast, memory-light).
- 	Incremental-only processing (skip full shuffle).
- 	Cluster tuned for lighter loads.



---



Great question 👍 — this is the core design decision in your 80M-article, multi-schema, multi-category metric pipeline.

Let’s think it through carefully:

---

#### Option 1: Compute Metrics Across All Schemas Together

Approach: Explode all schema → category arrays into a single long table
ut_number, pub_year, article_type, schema_name, category, citation_count

- 	Then run one grouped aggregation:
  
```scala
df.groupBy("schema_name", "category", "pub_year", "article_type")
  .agg(avg("citation_count"), ...)
```

Pros:
- 	Single pipeline, less code duplication.
- 	Only one shuffle stage for all schemas at once (Spark will handle grouping on schema_name as just another column).
- 	Easier incremental updates (just replace partitions for affected schema+year+category).

Cons:
- 	Exploding all schema/category arrays into one table can multiply row counts (10–20x expansion).
- 	Wide shuffle key (schema_name, category, pub_year, article_type) → more shuffle partitions.


---


#### Option 2: Compute Schema by Schema (Separate Jobs or Loops)

Approach: For each schema (e.g., wos, esci…), explode categories only for that schema and calculate metrics. Write results to schema-specific output tables, then union later if needed.

Pros:
- 	Narrower shuffle keys → less shuffle skew per job.
- 	Per-schema jobs can run in parallel (on Databricks Workflows or separate clusters).
- 	Easier debugging and resource tuning (emerging schema with 10K categories can get a bigger cluster).

Cons:
- 	More orchestration complexity (N jobs instead of 1).
- 	Duplicate logic across schemas (though can be parameterized).
- 	Harder to optimize globally across schemas.

---

#### Trade-off

- 	If categories per schema are small (<1000 each):
→ Option 1 (all together) is usually better. Less orchestration, Spark can handle it fine.

- 	If you have outliers (e.g., emerging schema with 10K categories, while others have ~10–100):
→ Hybrid strategy:
  - 	Run small schemas together in one job.
  - 	Isolate big schemas (like “emerging topic schema”) into their own pipeline to avoid blowing up shuffle.

---

#### Recommended Efficient Strategy (for your case)

Since you said:
- 	23 schemas total
- 	Some schemas have small category sets
- 	One has 10K categories

👉 Best approach:
1.	Build a common pipeline function (input: schema_name, categories_column).
2.	Run it:
- 	One big job for all normal schemas (say 22 of them).
- 	One separate job for the emerging-topic schema (10K categories).

This way:
- 	Shuffle pressure stays balanced.
- 	Incremental updates are still partitioned by (schema, year, category).
- 	Maintenance is easy (same logic applied everywhere).

---

## Spark Scala Pipeline Skeleton


Let’s design a Spark Scala pipeline skeleton that can run either all schemas together or schema-by-schema depending on configuration.



#### 🔹 Data Assumptions

- 	Input table: articles
- 	Schema:
```text
ut_number: String
pub_year: Int
citation_count: Long
article_type: String
categories_wos: Array[String]
categories_esci: Array[String]
categories_emerging: Array[String]
...
```
- 	Up to 23 category arrays, one per schema.


---

#### 🔹 Core Idea

- 	Write one generic function that:
	1.	Explodes the category array for a given schema.
	2.	Adds a schema_name column.
	3.	Aggregates metrics per (schema, category, pub_year, article_type).
- 	Run:
  - 	All schemas in one job: union exploded views before aggregation.
  - 	Schema-by-schema mode: loop through schemas, process independently.


---

#### 🔹 Pipeline Skeleton (Scala)

```scala
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._

object SchemaMetricsPipeline {

  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder.getOrCreate()

    val inputPath = "s3://bucket/articles_delta"
    val mode = args.headOption.getOrElse("all")  // "all" or "perSchema"

    val articles = spark.read.format("delta").load(inputPath)

    // Define schemas and their category column names
    val schemas = Seq(
      "wos" -> "categories_wos",
      "esci" -> "categories_esci",
      "emerging" -> "categories_emerging"
      // add all 23 schemas here
    )

    mode match {
      case "all" =>
        // Explode all schemas into one long DataFrame
        val explodedDFs = schemas.map { case (schemaName, colName) =>
          explodeSchema(articles, schemaName, colName)
        }
        val unionDF = explodedDFs.reduce(_ union _)
        val metrics = computeMetrics(unionDF)
        metrics.write.format("delta").mode("overwrite").save("s3://bucket/schema_metrics_all")

      case "perSchema" =>
        schemas.foreach { case (schemaName, colName) =>
          val exploded = explodeSchema(articles, schemaName, colName)
          val metrics = computeMetrics(exploded)
          metrics.write.format("delta").mode("overwrite").save(s"s3://bucket/schema_metrics_$schemaName")
        }
    }
  }

  /** Explode categories for one schema into (schema_name, category, ...) */
  def explodeSchema(df: DataFrame, schemaName: String, colName: String): DataFrame = {
    df.withColumn("category", explode(col(colName)))
      .withColumn("schema_name", lit(schemaName))
      .select("ut_number", "pub_year", "citation_count", "article_type", "schema_name", "category")
  }

  /** Compute decile-based metrics per schema/category/year/article_type */
  def computeMetrics(df: DataFrame): DataFrame = {
    val baseAgg = df.groupBy("schema_name", "category", "pub_year", "article_type")
      .agg(
        avg("citation_count").alias("avg_citations"),
        count("*").alias("n_articles"),
        expr("percentile_approx(citation_count, array(0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9))")
          .alias("deciles")
      )

    // Example: compute NCI (normalized citation impact) as citations / avg for that group
    val withNci = baseAgg.withColumn("nci", col("avg_citations") / avg("avg_citations").over())
    withNci
  }
}
```

#### 🔹 Notes on Performance

- 	All-schemas mode: fewer jobs, one shuffle → efficient if schemas have balanced category counts.
- 	Per-schema mode: avoids skew from big schemas (like emerging with 10K categories).
- 	Use partitioning:
```scala
df.repartition($"schema_name", $"pub_year")
```

before aggregation to co-locate categories by year and schema.

- 	Incremental updates: partition by (schema_name, pub_year) in output Delta tables.
- 	Replace only updated partitions during refresh.


---

#### 🔹 Example Cluster Tuning

For your scale (80M rows, ~23 schemas):
```scala
spark.conf.set("spark.sql.shuffle.partitions", "800")     // tune based on cluster cores
spark.conf.set("spark.sql.adaptive.enabled", "true")      // AQE on
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.files.maxPartitionBytes", "128m")
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1") // avoid unwanted broadcast
```

✅ This skeleton lets you toggle between “all schemas” and “per schema” with a config flag.
You can benchmark runtime & shuffle size on your cluster to decide which strategy is most efficient.