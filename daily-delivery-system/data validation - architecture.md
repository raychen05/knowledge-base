
## Ultimate Design  — Data Validation & Integrity Pipeline for daily incremental loads to Elasticsearch


Nice — you’ve got large-scale, multi-index, denormalized academic documents (WOS, PubPRN, patents, grants, author profiles, etc.) with daily incremental loads of 1M–20M documents. Below is a complete, practical, production-ready plan:

- What to check (concrete checklist of integrity / change items)
- Overall architecture & workflow for the validation pipeline
- Detection & thresholds (statistical + heuristic)
- Reconciliation methods between source (Delta) and sink (Elasticsearch)
- Automated responses & runbook actions
- Schemas & sample queries (SQL / Spark / pseudo-code)
- Scalability notes & performance tuning
- Monitoring / alerting KPIs

---

### 1. Important items to check (integrity & change checklist)

**Group: Global / high-level**

1. Total doc count per index (today vs baseline/day-before/rolling 7/30d).
2. Delta count (new / updated / deleted) - absolute and percent change.
3. Ingestion completeness — did the expected partitions / segments run? (per-source partition presence)
4. Processing failures / write failures (ES bulk error rates, Spark task errors).
5. Latency & timeliness (ingest lag: source timestamp → indexed timestamp).

**Group: Entity-level counts & linkage**

6. Documents per entity (author, organization, funder, journal, region, category, DOI): per-entity doc counts and top-N changes.
7. New / disappeared entities (authors/orgs that appear/disappear suddenly).
8. Cardinality changes (unique counts for author IDs, org IDs, funder IDs, journal IDs).
9. Distribution shifts (geographic distribution by country/state/NUTS, top journals).
10. Citation counts (mean / median / top percentiles); sudden drops/increases.

**Group: Schema, types & content**

11. Schema conformance: required fields present; types match (dates, ints, floats, arrays).
12. Null/NA rates for key fields (e.g., title, authors, DOI, pub_date).
13. Field format validation: DOIs, ORCIDs, ISSNs, patent numbers (regex checks).
14. Text length / truncation: title/abstract length outliers (too short/long).
15. Denormalized links: authorProfile.author_id -> author entity exists (referential integrity).

**Group: Duplicate & identity**

16. Duplicate document detection: same doc-id, same DOI, or hash collision.
17. Document versioning: updates must increase version or carry updated timestamp.

**Group: Quality & content**

18. Anomalous values: negative counts, impossible dates (future publish dates), invalid coordinates.
19. Spam / malformed docs detection (sudden increase in low-quality docs).
20. ES mapping issues: dynamic mapping changes, conflicting field types across indices.

**Group: Operational / performance**

21. ES bulk operation failures and partial writes (non-200 responses).
22. Shard hotspots and bulk latency/queue times.
23. Index size change per shard / index and total cluster storage.
24. Backpressure / queue lag if using Kafka/Event Hubs.


---

### 2. Validation pipeline architecture (end-to-end)


**Logical stages (recommended)**:

1. **Pre-load checks** (before writing to ES)
    - Verify expected input partitions/files present in Delta.
    - Verify schema shape & sample schema drift checks.
    - Sanity counts per source table (expected vs actual).

2. **Write / Load step** (incremental to ES)
    - Write with idempotent semantics (deterministic doc IDs).
    - Record bulk write response metrics (success count, failed items, exceptions).
    - Produce write audit log: write_audit(run_id, index, attempted, success, failed, timestamp).

3. **Post-load validation** (fast, high-signal checks)
    - Compare counts (Delta vs ES) per index and per partition (approx/fast).
    - Compare sample hashes/UIDs to ensure correctness.
    - Capture top anomalies (entities with large ±Δ counts).

4. **Deep validation** (async, heavier)
    - Distributional checks (histogram/reference distribution vs baseline).
    - Referential integrity: verify denormalized links exist in canonical tables.
    - Duplicate detection + content-hash comparisons.
    - Statistical anomaly detection (z-score/MAD/EWMA) on metrics time-series.

5. **Reconciliation & remediation**
    - If issues found, attempt automatic repair (reindex missing docs, retry failed bulks).
    - If auto-repair fails or risk > threshold, create incident and rollback/flag index alias to previous stable alias (if atomic alias swap used).

6. **Reporting & alerts**
    - Store validation results to validation_results Delta table and push key metrics to Prometheus/Datadog + Kibana/Grafana dashboards.
    - Trigger alerts (Slack/PagerDuty) for critical breaches.


---

### 3. Data model & audit tables


Recommended Delta tables (single source of truth for validations):

✅ 1. **write_audit_delta**

```sql
CREATE TABLE write_audit_delta (
  run_id           STRING,
  index            STRING,
  attempted_long   BIGINT,
  success_long     BIGINT,
  failed_long      BIGINT,
  start_ts         TIMESTAMP,
  end_ts           TIMESTAMP,
  error_sample     ARRAY<STRING>,
  es_response_stats MAP<STRING, STRING>
) USING DELTA;
```

✅ 2. **validation_results_delta**

```sql
CREATE TABLE validation_results_delta (
  run_id          STRING,
  index           STRING,
  check_category  STRING,
  check_name      STRING,
  status          STRING,
  severity        STRING,
  observed_value  STRING,
  expected_value  STRING,
  delta           STRING,
  details_json    STRING,
  ts              TIMESTAMP
) USING DELTA;
```

✅ 3. **reconciliation_actions_delta**

```sql
CREATE TABLE reconciliation_actions_delta (
  run_id        STRING,
  index         STRING,
  action_type   STRING,
  action_status STRING,
  effected_docs BIGINT,
  notes         STRING,
  ts            TIMESTAMP
) USING DELTA;
```

✅ 4. **entity_counts_daily**

```sql
CREATE TABLE entity_counts_daily (
  date         DATE,
  index        STRING,
  entity_type  STRING,
  entity_id    STRING,
  doc_count    BIGINT
) USING DELTA;
```

🧾 **Notes**:

- You can customize storage locations by adding LOCATION 'path/to/table' at the end.
- If you're working with structured JSON in **details_json**, consider using STRUCT or MAP<STRING, STRING> instead of raw STRING, if applicable.
  
- write_audit_delta: (run_id, index, attempted_long, success_long, failed_long, start_ts, end_ts, error_sample ARRAY<STRING>, es_response_stats MAP)
- validation_results_delta: (run_id, index, check_category, check_name, status, severity, observed_value, expected_value, delta, details_json, ts)
- reconciliation_actions_delta: (run_id, index, action_type, action_status, effected_docs, notes, ts)
- entity_counts_daily: (date, index, entity_type, entity_id, doc_count)

These allow dashboards, audit trails, and automated remediation.


---

### 4. Detection methods & thresholds

Use a multi-tier detection set:

**4.1 Heuristic checks (fast)**

- Absolute delta: |today_count - yesterday_count| > ABS_THRESHOLD (e.g., > 100k), trigger medium alert.
- Percent delta: percent_change = (today - baseline)/baseline *100. Trigger if > PCT_THRESHOLD (e.g., 30% for big corp; or 10% for stable indices).
- Minimum workload volume: don't over-alert on small baselines (use min count requirement e.g., baseline > 1k).

**4.2 Statistical checks (robust)**

- Z-score on rolling window (7 or 30 days): z = (x - mean)/std. Trigger when |z| > 3.
- Median Absolute Deviation (MAD) for heavy-tailed distributions: flag if deviation > 3*MAD.
- EWMA (Exponential Weighted Moving Average) to detect sudden shifts with time sensitivity.

**4.3 Entity-level anomaly (sensitive)**

- Relative change for top entities: if a top-100 author suddenly gets 10x docs, flag. Use rank-based thresholds.
- New entity rate: new entities today / baseline new entities > threshold.

**4.4 Schema & format checks**

- Any required field missing in > X% of docs (suggest X = 5%) → high severity.
- Any format validation failure (DOI regex fails) > small limit (0.1%) → medium.

**4.5 ES-specific checks**

- Bulk error rate: failed_docs / attempted_docs > 0.5% → medium; > 2% → critical.
- Non-200 counts: any 5xx from ES should escalate immediately.

---

### 5. Reconciliation strategies (Delta ⇄ Elasticsearch)

Because ES is eventually consistent and Delta is authoritative, reconcile with a layered approach:

**A. Fast count reconciliation (cheap)**

- Query Delta partition counts grouped by primary key or partition (e.g., date, source_table) and compare to ES _count API per index + query filter (date or id range). This is fast and done per index/partition.

Example (Spark SQL):
```sql
-- Delta side
SELECT partition_id, count(*) AS delta_count
FROM delta_source
WHERE ingest_date = '2025-10-13'
GROUP BY partition_id;

-- ES side (use _count with same filter per partition)
# curl -XGET 'http://es/_count' -d '{"query": {"term":{"ingest_date":"2025-10-13"}}}'
```


**B. Fingerprint reconciliation (sampled)**

- Compute a hash fingerprint (e.g., SHA256 of canonicalized JSON fields) per document in Delta; write a bloom filter or a sampled list. Query ES for presence of sampled IDs or hash. If mismatch rate > threshold, escalate.

**C. Full key reconciliation (when needed)**

- For smaller partitions (or when anomaly detected), fetch IDs from Delta and ES and compute set differences. For millions, do partitioned set-diff in Spark using join with ES scroll/point-in-time snapshot or by exporting ES doc IDs via _search with scroll or point-in-time then joining in Spark.

**D. Versioning & tombstones**

- Maintain doc_version / last_updated_ts in Delta and write to ES as metadata. Use this to reconcile and decide if ES needs a reindex for outdated docs.

**E. Reindex/Mend actions**

- Auto reindex: for missing docs list under threshold (e.g., <500k docs), push reindex job that reads delta and writes to ES via bulk.
- Alias swap rollback: if you used staging index + alias swap, you can revert alias to previous stable index quickly.

---


### 6. Example validation checks & sample queries


#### 6.1 Total count delta (Delta vs ES) — SQL + pseudo-ES call


```sql
-- Delta counts per index
SELECT index_name, count(*) AS delta_count
FROM delta_index_table
WHERE ingest_date = current_date()
GROUP BY index_name;
```

ES side (via API):

```bash
GET /{index_name}/_count
{ "query": { "term": { "ingest_date": "2025-10-13" } } }
```

Compute percent diff:

```ini
pct_diff = (es_count - delta_count) / delta_count - 100
```

Alert if abs(pct_diff) > 5% AND delta_count > 10000.


#### 6.2 Top-entity sudden change (authors)

Spark SQL:
```sql
WITH today AS (
  SELECT author_id, COUNT(*) AS today_cnt
  FROM delta_docs WHERE ingest_date = current_date() GROUP BY author_id
),
hist AS (
  SELECT author_id, AVG(cnt) AS avg_cnt
  FROM (SELECT author_id, COUNT(*) AS cnt, CAST(ingest_date AS DATE) d
        FROM delta_docs WHERE ingest_date >= date_sub(current_date(), 30)
        GROUP BY author_id, CAST(ingest_date AS DATE))
  GROUP BY author_id
)
SELECT t.author_id, today_cnt, avg_cnt, (today_cnt/NULLIF(avg_cnt,0)) AS ratio
FROM today t JOIN hist h ON t.author_id = h.author_id
WHERE today_cnt > 10 AND (today_cnt/NULLIF(avg_cnt,0)) > 3
ORDER BY ratio DESC LIMIT 100;
```

Flag these for manual review or automated sampling (fetch sample docs for human check).


#### 6.3 Schema conformance example

Spark:
```scala
val df = spark.table("delta_docs").filter($"ingest_date" === lit(today))
val badDois = df.filter(not($"doi".rlike("^10.\\d{4,9}/[-._;()/:A-Z0-9]+$")))
val badRatio = badDois.count().toDouble / df.count()
```

Alert if badRatio > 0.001 (0.1%).

#### 6.4 Duplicate detection

Use content hash or (index, unique_key) grouping:
```sql
SELECT unique_key, COUNT(*) as dup_count
FROM delta_docs
WHERE ingest_date = current_date()
GROUP BY unique_key
HAVING COUNT(*) > 1;
```

If duplicates > threshold, inspect ingestion dedupe logic.

---

### 7. Implementation pattern (Spark + Delta + ES) — scalable

**Workflow per daily run (automated)**

1. **Pre-check job** (Spark)
    - Confirm expected source partitions exist
    - Run schema conformance quick checks (field presence)
    - Emit pre_check results to validation_results_delta

2. **Load job** (bulk incremental to ES)
    - Use deterministic doc IDs and idempotent upserts
    - Batch size tuned (500–5k bulk) and parallelism throttled to ES capacity
    - Record write_audit_delta entries (attempted, success, failed, errors)

3. **Fast post-check job** (Spark & ES)
    - Count reconciliation per index (fast)
    - Compute pct_diff, push validation_results_delta
    - If fails severity = critical -> trigger alert & depending on policy either auto-reindex or stop pipeline

4. **Deep checks** (async)
    - Entity-level counts, distribution drift (stat methods), duplicate detection, referential integrity, mapping checks
    - Store findings to validation_results_delta with severity and suggested actions

5. **Remediation job(s)**
    - For missing docs: queue a reindex task (partitioned)
    - For mapping issues: freeze writes to index and escalate
    - For major distribution shifts: open incident for data team

6. **Report job** (Databricks SQL dashboard)
    - Populate dashboards, send nightly reports, keep audit logs

--


### 8. Automation & remediation strategies

- **Auto-reindex for small failures**: if missing docs < configurable threshold (e.g., 0.5% AND < 1M docs) → run targeted reindex.

- **Staging + alias swap:** always write to staging index and switch alias only after all post-checks pass. If checks fail, keep alias on old index.

- **Back-off & retry:** implement exponential backoff for ES bulk failures; write failed docs to failed_docs table for manual inspection.

- **Quarantine**: flag suspicious docs into a quarantine index for investigation (avoid contaminating main index).

- **Human-in-the-loop**: for high-severity anomalies, create a ticket with samples and suspend alias swap.

---


### 9. Threshold recommendations (starter values — tune for your data)

- **Pct diff on counts**: 5–10% (looser for very volatile sources; stricter for stable ones).
- **Absolute delta:** escalate if change > 100k docs for a mid-sized index.
- **Schema missing fields:** fail if required field missing > 5% of documents.
- **DOI/ORCID format errors**: warn if > 0.1%; fail if > 1%.
- **Bulk error rate**: > 0.5% warn; > 2% critical.
- **Duplicate rate**: > 0.1% warn; > 1% critical.
- **Entity count spike** (top entity): ratio > 3–5x against 30d average → flag.

Tune these thresholds after 1–2 months of historical analysis.

---


### 10. Monitoring / Alerts & KPIs


Push summary metrics to Prometheus / Datadog:

- ingest_docs_total{index}
- ingest_docs_failed{index}
- ingest_latency_seconds
- validation_count_failures{check}
- validation_alert_severity{level}

**Alert rules** (examples):

- ingest_docs_failed / ingest_docs_total > 0.005 → Alert (critical)
- validation_count_failures{check="count_delta"} > 0 → Alert
- pct_diff_count{index="wos"} > 0.05 AND delta_count > 10000 → Alert

---


### 11. Performance & scalability notes

- **Avoid full ID scans** of ES for millions of docs — use partitioned ID ranges or hashed partitions to do set diffs in parallel.
- **Use ES Point-in-Time (PIT)** or scroll APIs for stable snapshots when doing large comparisons. Beware of memory/time limits.
- **Parallelize reconciliation**: split by ingestion partition (date, shard) and reconcile in parallel Spark tasks.
- **Use CDF / change feeds** in Delta to only validate changed docs (more efficient).
- **Bloom filters**: to quickly test membership for large sets — keep a daily bloom per partition for quick existence checks.
- **Sampling**: for expensive content checks, do probabilistic sampling for each anomaly candidate.

---

### 12. Example: sample validation_results schema + insertion (Spark SQL)

DDL:
```sql
CREATE TABLE IF NOT EXISTS validation_results_delta (
  run_id STRING,
  index_name STRING,
  check_name STRING,
  status STRING,           -- PASSED, WARN, FAILED
  severity STRING,         -- INFO, MEDIUM, HIGH, CRITICAL
  expected DOUBLE,
  observed DOUBLE,
  delta_pct DOUBLE,
  details STRING,
  ts TIMESTAMP DEFAULT current_timestamp()
) USING DELTA;
```

Insert example (Scala):
```scala
val result = Seq(("run123","wos","count_reconcile","FAILED","CRITICAL", 1000000.0, 900000.0, -10.0, "ES count 10% lower")).toDF(
  "run_id","index_name","check_name","status","severity","expected","observed","delta_pct","details")
result.write.format("delta").mode("append").saveAsTable("validation_results_delta")
```

---

### 13. Runbook & operator actions (examples)


If count_reconcile fails with delta_pct < -5% and failed_docs < 1M:
- Auto: schedule reindex job for missing partitions and verify results.
- Notify: Slack channel + on-call.
- Log: append reconciliation_actions_delta entry.

If bulk_error_rate > 2% or ES 5xx:
- Immediately pause writes to index.
- Roll back alias if staging used.
- Alert on-call, attach write_audit and sample errors.

If top-author spike ratio > 10x:
- Sample 100 docs from this author and send to data QA.
- If content valid and expected (e.g., special harvest), mark as known and whitelist.

---

### 14. Recommended next steps to implement


1. **Create the audit & validation Delta tables** (write_audit_delta, validation_results_delta, entity_counts_daily).
2. **Instrument your load job** to record write_audit entries with granular stats. Include sample of failed doc IDs.
3. **Implement fast post-check job** that runs counts and schema checks; push results to validation_results_delta and alert if failing.
4. **Implement deep validation as async Spark jobs**: entity counts, distribution drift, referential checks.
5. **Add automated remediation** for small reindex jobs; implement staging + alias swap.
6. **Add dashboards & alerts** for the KPIs described above.
7.** Run calibration period** (30–60 days) to set thresholds, using historical baselines.

If you want I can immediately:

- produce the Spark/Scala skeleton for the post-load validation job (fast checks + insertion into validation_results_delta), or
- produce SQL queries for all checks above ready to run as Databricks SQL queries, or
- produce a detailed reindex micro-job that takes a list of missing doc IDs and re-bulks them to ES with backoff and audit.


---