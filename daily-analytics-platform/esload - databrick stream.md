 ## ES-Hadoop connector 


This is a classic ES-Hadoop connector pain point 😅By default, one bad row can fail the whole Spark → Elasticsearch write, because ES rejects the bulk request.
Below is a battle-tested, Databricks-friendly approach to skip bad rows, keep loading good data, and still keep observability.

Root Cause (why it stops)
When Spark writes to ES via elasticsearch-hadoop:
- Rows are sent in bulk batches
- If any document in the bulk fails (mapping conflict, bad JSON, oversized field, etc.)
- ES returns a bulk error → Spark task fails → job stops
So the fix is:👉 tolerate document-level failures instead of task-level failure

---

✅ Recommended Solution (Best Practice)


### 1️⃣ Enable ES write error tolerance (MOST IMPORTANT)

Set these ES connector options:

```scala
.option("es.write.operation", "index")
.option("es.batch.write.retry.count", "3")
.option("es.batch.write.retry.wait", "10s")

// 🔑 critical flags
.option("es.write.rest.error.handlers", "log")
.option("es.write.rest.error.handler.log.level", "WARN")
```

---

### ✅ What this does:

- ES logs failed documents
- Spark continues writing remaining docs
- Job does NOT fail

⚠️ Without this, Spark fails hard.

---

### 2️⃣ Capture Failed Rows Separately (Highly Recommended)

Logging alone isn’t enough in production. You want bad rows saved.
Use multiple error handlers

```scala
.option(
  "es.write.rest.error.handlers",
  "log,store"
)
.option(
  "es.write.rest.error.handler.store.path",
  "dbfs:/mnt/es_errors/my_index/"
)
```


Result:
- ✅ Successful docs → ES
- ❌ Failed docs → DBFS (JSON)
- 🧠 You can reprocess them later

---

### 3️⃣ Pre-Validate Rows Before Writing (Avoid ES Failures)

Most ES failures fall into 4 buckets:
1. Null / invalid ID
2. Field type mismatch
3. Oversized strings / arrays
4. Unkown schema chnage

Example: filter obvious bad rows

```scala
val (goodDF, badDF) = df
  .withColumn("is_valid",
    col("id").isNotNull &&
    length(col("title")) < 32766
  )
  .cache()
  .randomSplit(Array(0.999, 0.001)) // optional sampling

goodDF
  .write
  .format("org.elasticsearch.spark.sql")
  .options(esOptions)
  .save("index/_doc")

badDF.write.mode("append").saveAsTable("es_rejects_raw")
```

👉 This dramatically reduces ES bulk errors

---

### 4️⃣ Reduce Blast Radius with Smaller Batches

Large ES batches = one bad doc kills many good ones.
Tune batch size:

```scala
.option("es.batch.size.entries", "500")  // default is 1000+
.option("es.batch.size.bytes", "5mb")
```

This limits damage and speeds retries.

---

### 5️⃣ Use Deterministic Document IDs (Avoid Silent Dupes)

Always set:

```scala
.option("es.mapping.id", "id")
```

Why:
- Avoids re-indexing duplicates
- Failed docs can be replayed safely

---

### 6️⃣ Production-Grade Pattern (Recommended Architecture)

🔹 Step 1: Normalize → Bronze
  - Clean schema
  - Enforce max lengths
  - Cast types
🔹 Step 2: Validate → Silver
  - Add is_valid flag
  - Split good vs bad
🔹 Step 3: Write → ES
  - Enable error handlers
  - Small batch size
🔹 Step 4: Observe
  - Store ES failures
  - Dashboard failure rate
  - Alert if > threshold

---

### 7️⃣ Minimal Working Example (Scala / Databricks)


```scala
df.write
  .format("org.elasticsearch.spark.sql")
  .option("es.nodes", "es-host")
  .option("es.port", "9200")
  .option("es.mapping.id", "id")
  .option("es.batch.size.entries", "500")
  .option("es.write.rest.error.handlers", "log,store")
  .option("es.write.rest.error.handler.store.path", "dbfs:/mnt/es_errors/")
  .mode("append")
  .save("my_index/_doc")
```

---

### Summary 

| Problem | Solution |
|---------|----------|
| Job stops on bad rows | `es.write.rest.error.handlers=log,store` |
| Need bad row visibility | Store failed docs to DBFS |
| Reduce failures | Pre-validate schema & length |
| Limit damage | Smaller ES batch size |
| Safe replay | Deterministic document ID |


If you want, I can:
- 🔍 Build a replay pipeline for failed docs
- 📊 Add metrics & alerting (failure ratio, bad fields)
- 🧪 Provide unit tests using golden data (ties nicely to your CDC testing work)
Just say the word 👌


---


## Build a replay pipeline for failed docs



Nice choice 👍 — a replay pipeline is exactly how teams make ES ingestion self-healing instead of fragile.
Below is a production-grade replay design that fits Databricks + ES connector, works incrementally, and won’t create duplicates.


---

### 🎯 Goal

When ES rejects some documents during Spark write:
- ❌ Failed docs are captured
- 📦 Stored durably (DBFS / Delta)
- 🔁 Replayed automatically after fixes
- 🔐 Idempotent (safe to retry many times)
- 📊 Observable

---

### 🧱 Overall Architecture

```css
Source DF
   │
   ├──► ES (good docs)
   │
   └──► ES Error Store (bad docs)
                │
                ▼
        Normalize / Fix
                │
                ▼
          Replay to ES
                │
                ├── success → archive
                └── failure → retry / DLQ
```

---

### 1️⃣ Capture Failed Docs in a Structured Way


ES Connector Configuration

```scala
.option("es.write.rest.error.handlers", "log,store")
.option("es.write.rest.error.handler.store.path",
        "dbfs:/mnt/es_errors/my_index/")
```

This generates files like:

```json
{
  "timestamp": "2026-01-29T10:22:31Z",
  "index": "my_index",
  "type": "_doc",
  "id": "123",
  "error": {
    "type": "mapper_parsing_exception",
    "reason": "failed to parse field [age]"
  },
  "document": {
    "id": "123",
    "age": "abc"
  }
}
```

---


### 2️⃣ Normalize Failed Docs into a Delta Table


Create a replay staging table (silver-quality).

```scala
val rawErrors = spark.read.json("dbfs:/mnt/es_errors/my_index/*")

val failedDocs = rawErrors.select(
  col("document.*"),
  col("id").as("es_id"),
  col("error.type").as("error_type"),
  col("error.reason").as("error_reason"),
  current_timestamp().as("failed_at"),
  lit(0).as("retry_count"),
  lit("PENDING").as("status")
)

failedDocs.write
  .format("delta")
  .mode("append")
  .saveAsTable("es_failed_docs")
```

---


### 3️⃣ Fix / Normalize Before Replay


Apply targeted transformations based on known ES failures.


```scala
val candidates = spark.table("es_failed_docs")
  .filter("status = 'PENDING' AND retry_count < 5")

val fixed = candidates
  .withColumn("age",
    when(col("age").cast("int").isNotNull, col("age").cast("int"))
      .otherwise(lit(null))
  )
  .withColumn("title", substring(col("title"), 1, 32766))
```

👉 Keep this logic versioned so you know what fix was applied.


---

### 4️⃣ Replay to Elasticsearch (Idempotent)


```scala
fixed.write
  .format("org.elasticsearch.spark.sql")
  .option("es.nodes", "es-host")
  .option("es.port", "9200")
  .option("es.mapping.id", "es_id")
  .option("es.write.rest.error.handlers", "log")
  .mode("append")
  .save("my_index/_doc")
```

Because es.mapping.id is set:
- Replay is safe
- Overwrites existing doc if needed
- No duplicates

---

### 5️⃣ Update Replay Status (MERGE)


```scala
import io.delta.tables._

val deltaTable = DeltaTable.forName("es_failed_docs")

deltaTable.as("t")
  .merge(
    fixed.select("es_id").as("s"),
    "t.es_id = s.es_id AND t.status = 'PENDING'"
  )
  .whenMatched
  .updateExpr(Map(
    "status" -> "'SUCCESS'",
    "replayed_at" -> "current_timestamp()"
  ))
  .execute()
```

---

### 6️⃣ Handle Second-Level Failures (DLQ)

If replay fails again:

```scala
val failedAgain = spark.read.json("dbfs:/mnt/es_errors/my_index/*")

deltaTable.as("t")
  .merge(
    failedAgain.select(col("id").as("es_id")).as("s"),
    "t.es_id = s.es_id"
  )
  .whenMatched
  .updateExpr(Map(
    "retry_count" -> "retry_count + 1",
    "status" -> "CASE WHEN retry_count >= 5 THEN 'DLQ' ELSE 'PENDING' END"
  ))
  .execute()
```

Final states:
- SUCCESS → archived
- PENDING → retried later
- DLQ → manual review

---

### 7️⃣ Automate with Databricks Jobs

Suggested Schedule

| Job | Frequency |
|-----|-----------|
| Primary ES load | Continuous / batch |
| Replay job | Every 15–30 min |
| DLQ audit | Daily |

---

### 8️⃣ Metrics & Alerts (Highly Recommended)


Track:
- % failed docs
- Retry count distribution
- DLQ volume
- Top error types

Example:

```sql
SELECT error_type, count(*) 
FROM es_failed_docs
WHERE status = 'PENDING'
GROUP BY error_type
```

Alert if:
- Failure rate > 0.5%
- DLQ > threshold

---

### 9️⃣ Folder / Table Layout

```css
dbfs:/mnt/es_errors/
  └── my_index/
        ├── raw/
        ├── replay/
        └── archive/
```

Delta Tables:
- es_failed_docs
- es_replay_history
- es_dlq

---

### ✅ Why This Works Well

- ✔ No data loss
- ✔ Fully idempotent
- ✔ Replayable forever
- ✔ Clear audit trail
- ✔ Scales with volume

If you want next:
- 🔁 Generic replay framework (config-driven per index)
- 🧪 Golden-data tests for replay logic
- 📊 ES ingest SLO dashboard
- 🔧 Auto-classification of ES errors → fix strategy

Tell me which one you want to tackle next 🚀


---


## Save Log to s3

Short answer: yes — you can use S3, but not directly as s3://… in that option. There’s an important Databricks + ES-connector nuance here.
Let’s break it down cleanly 👇

### ✅ What does work

✔ Use DBFS that is backed by S3
This is the recommended + supported approach.

```scala
.option(
  "es.write.rest.error.handler.store.path",
  "dbfs:/mnt/es_errors/"
)
```

If /mnt/es_errors is an S3 mount:

dbfs:/mnt/es_errors  →  s3://my-bucket/es_errors/

- 👉 Physically stored in S3, logically accessed as DBFS
- 👉 ES connector is happy
- 👉 Spark permissions + retries work correctly

❌ What does NOT work

```scala
.option(
  "es.write.rest.error.handler.store.path",
  "s3://my-bucket/es_errors/"
)
```

Why this fails:
- ES-Hadoop does not use Spark’s FileSystem abstraction
- It expects a Hadoop-compatible FS path
- Direct s3:// paths often fail with:
    - No FileSystem for scheme s3
    - Silent write failures
    - Executor-side permission errors
This is a known limitation of ES-Hadoop.

---

### ✅ Correct Ways to Use S3 (Ranked)

#### 🥇 Option 1 — DBFS Mount to S3 (BEST)


```scala
dbutils.fs.mount(
  source = "s3a://my-bucket",
  mountPoint = "/mnt/es_errors",
  extraConfigs = Map(
    "fs.s3a.access.key" -> "...",
    "fs.s3a.secret.key" -> "..."
  )
)
```

Then:

```scala
.option(
  "es.write.rest.error.handler.store.path",
  "dbfs:/mnt/es_errors/"
)
```

- ✔ Fully supported
- ✔ Secure
- ✔ Easy replay pipeline
- ✔ Works with Delta

---

#### 🥈 Option 2 — Unity Catalog External Location (Modern)

If you’re on UC:

External Location:
  s3://my-bucket/es_errors/

Access via:

dbfs:/Volumes/catalog/schema/es_errors/
Then:

```scala
.option(
  "es.write.rest.error.handler.store.path",
  "dbfs:/Volumes/catalog/schema/es_errors/"
)
```

- ✔ IAM-based access
- ✔ Cleaner governance
- ✔ Works great with Delta

---

#### 🥉 Option 3 — Local FS (NOT recommended)

file:/tmp/es_errors/

- ❌ Executor-local
- ❌ Lost on restart
- ❌ No replay durability


#### 🧠 Why ES Error Store Needs DBFS

The ES error handler:
- Writes from executors
- Uses Hadoop FS APIs
- Needs atomic file creation
- Needs retry-safe storage

DBFS solves all of this; raw S3 does not.

---

### 🔁 Replay Pipeline Compatibility

Once errors are stored in DBFS-backed S3:

```scala
spark.read.json("dbfs:/mnt/es_errors/*")
```

- ✔ Parallel reads
- ✔ Schema evolution
- ✔ Delta-friendly
- ✔ Cheap storage

---

### ✅ Final Recommendation

YES, you can absolutely use S3 BUT always go through DBFS (mount or UC Volume)
✔ Do this

"dbfs:/mnt/es_errors/"

❌ Not this

"s3://my-bucket/es_errors/"

If you want, I can:
- 🔐 Design an IAM + UC external location setup
- 📁 Give a partitioned S3 layout for multi-index replay
- 🧪 Add replay tests that read from mounted S3
- 🛡 Add encryption & retention policies


---

## Design an IAM + UC external location setup

Perfect — this is the cleanest, future-proof setup for what you’re building 
👍 Below is a production-grade IAM + Unity Catalog External Location design tailored for:
- ES error capture
- Replay pipelines
- Least-privilege security
- Auditing & governance
- 
I’ll keep it concrete and Databricks-ready.

---

### 🎯 Target Architecture

```css
Elasticsearch
   │
   ├── good docs → ES index
   │
   └── failed docs
          │
          ▼
DBFS path (UC Volume)
dbfs:/Volumes/main/ops/es_errors/
          │
          ▼
S3 bucket (External Location)
```

s3://company-data-prod/es/es_errors/

**Key idea**:
ES connector writes to DBFS → DBFS maps to UC Volume → UC Volume maps to S3 via IAM role

---

### 1️⃣ S3 Bucket Design (Foundation)

Bucket

s3://company-data-prod/
Folder layout (important for replay & governance)

```css
es/
 └── es_errors/
      ├── index=my_index/
      │    ├── dt=2026-01-29/
      │    └── dt=2026-01-30/
      ├── index=another_index/
      └── _archive/
```

- ✔ Partitionable
- ✔ Cheap replay scans
- ✔ Easy lifecycle rules

---

### 2️⃣ IAM Role (Least Privilege)

IAM Role

databricks-uc-es-errors-role
Trust Policy (Databricks AWS account)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<DATABRICKS_AWS_ACCOUNT_ID>:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "<DATABRICKS_EXTERNAL_ID>"
        }
      }
    }
  ]
}
```

Permissions Policy (Minimal)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EsErrorStoreAccess",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::company-data-prod",
        "arn:aws:s3:::company-data-prod/es/es_errors/*"
      ]
    }
  ]
}
```

- 🚫 No access to other datasets
- 🚫 No wildcard buckets

---

### 3️⃣ Create UC Storage Credential

Run once as UC admin:

```sql
CREATE STORAGE CREDENTIAL es_error_cred
WITH IAM_ROLE 'arn:aws:iam::<ACCOUNT_ID>:role/databricks-uc-es-errors-role';
```

Verify:
```sql
DESCRIBE STORAGE CREDENTIAL es_error_cred;
```

---

### 4️⃣ Create External Location

```sql
CREATE EXTERNAL LOCATION es_error_location
URL 's3://company-data-prod/es/es_errors/'
WITH (STORAGE CREDENTIAL es_error_cred);
```

Validation:
```sql
DESCRIBE EXTERNAL LOCATION es_error_location;
```

---

### 5️⃣ Create UC Volume (This is the Key Step)

Volumes give you a DBFS-style path, which ES connector requires.
```sql
CREATE VOLUME main.ops.es_errors
LOCATION 's3://company-data-prod/es/es_errors/';
```

Resulting path:

dbfs:/Volumes/main/ops/es_errors/

✔ ES-Hadoop compatible
✔ IAM governed
✔ Audited by UC

---

### 6️⃣ Grant Access (Fine-Grained)

```sql
GRANT READ, WRITE
ON VOLUME main.ops.es_errors
TO `data-platform-es-writer`;
```

Optional read-only for analysts:
```sql
GRANT READ
ON VOLUME main.ops.es_errors
TO `data-observability`;
```

---

### 7️⃣ ES Connector Configuration (Final)

Use only DBFS path:

```scala
.option(
  "es.write.rest.error.handlers",
  "log,store"
)
.option(
  "es.write.rest.error.handler.store.path",
  "dbfs:/Volumes/main/ops/es_errors/index=my_index/dt=2026-01-30/"
)
```

💡 You can dynamically inject:
- index
- date
- env (dev/prod)

---

### 8️⃣ Replay Pipeline Reads (Spark / Delta)

```scala
val errors = spark.read.json(
  "dbfs:/Volumes/main/ops/es_errors/index=my_index/*"
)
```

Or materialize to Delta:
```scala
errors.write
  .format("delta")
  .mode("append")
  .saveAsTable("ops.es_failed_docs")
```

---

### 9️⃣ Lifecycle & Cost Control (Highly Recommended)

**S3 Lifecycle Rule**

| Data | Action |
|------|--------|
| Raw ES errors | 30 days |
| Replayed success | Glacier after 60 days |
| DLQ | Retain 180 days |

---

### 10️⃣ Why This Setup Is “Correct”

- ✔ ES-Hadoop compatible
- ✔ Cloud-native IAM
- ✔ Unity Catalog governance
- ✔ Auditable access
- ✔ No hardcoded secrets
- ✔ Replay-safe
- ✔ Future-proof (DBFS mounts are legacy)

---

### 🔐 Security Model Summary

| Layer | Responsibility |
|-------|----------------|
| IAM Role | S3 access |
| UC Storage Credential | Identity binding |
| External Location | Path scoping |
| Volume | Runtime access |
| Grants | Who can write/read |


Want to go further?
I can next:
- 🔁 Make this multi-index / multi-env config-driven
- 📊 Add replay SLA dashboards
- 🧪 Add golden-data tests for replay
- 🚨 Add auto-quarantine for mapping errors
- 🧩 Package this as a reusable ES ingestion framework

---


### 1️⃣ Volume paths in Unity Catalog

If you have a catalog volume like:
```sh
/Volumes/catalog_name/schema_name/folder_name
```

- This is a Databricks-managed volume in Unity Catalog.
- Spark can access files directly using the /Volumes/... path.
- You do NOT need dbfs: prefix in this case.
  
So this works:

```scala
val path = "/Volumes/my_catalog/my_schema/my_folder/errors.json"

val df = spark.read
  .format("json")
  .load(path)

df.show()
```

✅ Works fine because Databricks automatically resolves the /Volumes/... path through the Unity Catalog volume.


---

### 2️⃣ When dbfs: prefix is needed

- dbfs:/ is used for DBFS storage paths (like /FileStore/...)
- Also required for some connectors (like the ES connector), when they don’t automatically resolve /Volumes/....
So for Unity Catalog volumes, dbfs: is not required, but for external DBFS paths, you usually need dbfs:/.

---

### 3️⃣ Using a Unity Catalog volume path as ES error log path


You can use the /Volumes/... path directly:

```scala
.option("es.write.rest.error.handlers", "log,store")
.option("es.write.rest.error.handler.store.path", "/Volumes/my_catalog/my_schema/my_folder/es_errors/")
.option("es.write.rest.error.handler.log.level", "WARN")
```

- This will store failed documents in the catalog volume.
- ES connector will write successfully, Spark can read from the same path.

---

### ✅ Key Takeaways

| Storage Type | Path Format | Notes |
|-------------|-------------|-------|
| DBFS FileStore / mounts | `dbfs:/FileStore/...` or `dbfs:/mnt/...` | Use `dbfs:` prefix |
| Unity Catalog volume | `/Volumes/catalog/schema/folder` | `dbfs:` prefix NOT needed |
| ES connector log path | Works with either | Just ensure path is accessible to Spark |


💡 Recommendation: 

- For Unity Catalog volumes, just stick with /Volumes/.... 
- Use dbfs: only if you’re using DBFS-managed paths.




