

## Elasticsearch Data Modeling - General Guideline


Nice — this is a classic “lots of derived metrics that change often, but documents are big and reindexing everything would be painful” problem. Below is a pragmatic, production-ready strategy that minimizes reindex operations while keeping queries fast and aggregations correct.

I’ll give: 

- (A) high-level design, 
- (B) concrete index layout choices, 
- (C) query-time techniques that avoid reindexing, 
- (D) when to precompute / reindex, and 
- (E) practical operational tips + small JSON examples you can drop into Elasticsearch.


### A — High level approach (the core idea)

1.** Keep source-of-truth doc index mostly static** — store document metadata and raw base metrics (citation_count, year, article_type, category, funders[], authors[], orgs[], journal, region, etc.). These rarely change per doc.

2. **Never store volatile cohort-derived fields directly on every doc** (percentile, NCI, normalized score) — compute them at query-time using small, separately-updated cohort summaries (thresholds/statistics) or on a small per-article metric index that is much smaller than full doc reindexing.

3. **Store cohort statistics in small indices** (one doc per cohort/year/category/article_type) that are cheap to recompute and update.

4. **Use runtime_mappings / script_fields / search templates** so ES computes derived indicators during search/aggregation using the cohort thresholds passed as parameters (or embedded via runtime mappings). This avoids reindexing all docs when cohort boundaries change.

5. **For heavy UI aggregation needs, maintain incremental entity materialized views** using ES Transforms (or an external job) that aggregate per-entity metrics — these are small and can be updated incrementally or swapped atomically via aliases.

This hybrid keeps the large doc index stable, moves volatility to tiny indices or query-time computations, and provides fast aggregations via pre-aggregated entity indices where needed.


---


### B — Recommended index model (concrete)

1. docs index (primary, large)

- Fields: doc_id (id), title, year, article_type, category, journal_id, authors: [ {author_id, affiliation_id, pos} ] or flattened author_ids: [], org_ids: [], funder_ids: [], region_ids: []
- Raw numeric metrics (doc-level, stable): citation_count, usage_count, downloads, pages, references_count, altmetric_score, publication_date
- Mapping notes: use keyword for IDs & facets, date for dates, long/double for numerics. Enable doc_values on fields used in aggregations (default for keyword/long).
- Avoid storing computed percentiles/NCI here unless you accept reindexing cost.

2. cohort_stats index (small)

- One document per cohort: key = {year, category, article_type} (or other cohort keys you support).
- Fields: cohort_key, n, percentiles (map: p10: val, p25: val, p50: val, p75: val, p90: val, max, min, mean, stddev), version, computed_at
- This is tiny and very cheap to recompute every time your percentile calculation changes.

3. Optional: per_article_metrics index (medium)

- If you want per-article derived values stored (e.g., NCI precomputed), keep them here keyed by doc_id+year+cohort_version. This index is much smaller than docs (only metrics), so updating it is cheaper than reindexing the full doc index.
- Use when you need frequently-used derived values and cannot compute them on the fly.

4. Optional: entity_aggregates index(s) (authors/orgs/funders/journals)

- Use ES Transforms or an offline job to create entity-level documents (e.g., author_id → aggregated counts, sums, top categories, precomputed percentiles by using cohort data).
- These indices are small and can be updated incrementally or rebuilt periodically and swapped with aliases.


---


### C — How to compute derived metrics WITHOUT reindexing


#### 1) Compute cohort thresholds offline, store in cohort_stats.

- Use Spark/MapReduce/ES aggregations to compute percentiles per cohort.
- Store results into cohort_stats (one doc per cohort). This is cheap and fast.

#### 2) At query time, fetch the relevant cohort thresholds and pass them into the search as runtime params

- Two approaches:
  - **Client-side two-step**: first GET cohort_stats for the requested cohort(s), then call ES search on docs with runtime_mappings or script_fields that use these thresholds as constants to compute percentile/NCI per document. This computes derived metrics on-the-fly and supports aggregations over runtime fields.
  - **Search template**: embed cohort numbers in a stored search template and run it.

**Why this works**: runtime_mappings and script_fields compute values per document during query execution; they do not require reindexing documents. They also participate in aggregations (with some performance cost). Because the cohort stats are small and update rarely relative to docs, recomputing them is cheap and avoids massive document updates.



#### 3) Example: compute a percentile rank for an article’s citations with runtime_mappings

(Example painless script: compare doc['citation_count'].value with cohort percentile thresholds passed in as params.)

```json
POST /docs/_search
{
  "runtime_mappings": {
    "citation_percentile": {
      "type": "double",
      "script": {
        "params": {
          "p10": 2,
          "p25": 5,
          "p50": 12,
          "p75": 40,
          "p90": 110
        },
        "source": """
          double c = doc['citation_count'].size() == 0 ? 0 : doc['citation_count'].value;
          if (c <= params.p10) return 10.0;
          if (c <= params.p25) return 25.0;
          if (c <= params.p50) return 50.0;
          if (c <= params.p75) return 75.0;
          if (c <= params.p90) return 90.0;
          return 99.0;
        """
      }
    }
  },
  "query": { "term": { "category.keyword": "immunology" }},
  "aggs": {
    "percentile_hist": {
      "histogram": {
        "field": "citation_percentile",
        "interval": 10
      }
    }
  },
  "_source": ["title", "citation_count"]
}

```

**Notes**:

- The params values should come from cohort_stats returned earlier by your service.
- runtime_mappings can be defined per-search; ES will run the script to compute the runtime field for each doc returned / touched by aggregations.


#### 4) If many derived metrics are needed for aggregations and runtime cost is too high

- Precompute those derived metrics into per_article_metrics (smaller index) and reference them at query-time (join by doc_id). Updating that index is still much cheaper than reindexing entire docs because it holds only metrics.
- Or compute entity-level pre-aggregates (entity_aggregates) for dashboard-level responses.


---

### D — When to precompute / reindex vs when to compute at query-time

**Use query-time (runtime_mappings + cohort_stats) when:**

- Cohort thresholds change frequently OR computation logic changes.
- You want immediate effect of new percentiles without document reindex.
- Your result sets are bounded (e.g., UI pages, filtered subsets) or you can afford the runtime script cost.

**Precompute and store per-article derived metrics when**:

- Derived metric is expensive to compute repeatedly and is used heavily in many aggregations (so runtime cost is too high).
- You can update the metrics index in batches (smaller than full reindex) when cohorts change.
- You need sorting/fast term aggregations on the derived metric (runtime fields can do this but precomputing is faster).

**Reindex full docs only when**:

- You change core mapping types (e.g., converting a field from text to keyword) or add very frequently-used fields that must be stored on the doc.
- Structural mapping change is necessary — otherwise avoid.


---

### E — Operational best practices (shard sizing, refresh, updates)

1. Shard sizing: avoid many small shards. Target ~30–50GB per shard depending on usage. Fewer shards = faster aggregations.
2. Refresh interval: for large bulk ingest/update jobs increase index.refresh_interval to 30s or -1 during bulk and reset after. This reduces refresh overhead.
3. Bulk updates: use bulk API and scripted partial updates for small updates; but avoid update-by-query over millions of docs unless you accept the cost.
4. Alias + swap for rebuilds: when you must rebuild an index, write to new index and atomically swap alias to avoid downtime.
5. Transforms: use ES Transforms for incremental entity-aggregate indexes; they can run continuously and are efficient.
6. Caching & CDN: cache cohort_stats and entity_aggregates in your app layer (Redis) to avoid repeated small ES reads.
7. Version cohort stats: add cohort_version so clients know which cohort a derived metric used.
8. Audit trail: keep computed_at timestamp and version for cohort_stats so you can explain metrics.


---

### F — Example schemas (minimal)


docs mapping (conceptual)

```json
PUT /docs
{
  "mappings": {
    "properties": {
      "doc_id": { "type": "keyword" },
      "title": { "type": "text" },
      "year": { "type": "integer" },
      "category": { "type": "keyword" },
      "article_type": { "type": "keyword" },
      "journal_id": { "type": "keyword" },
      "author_ids": { "type": "keyword" },
      "org_ids": { "type": "keyword" },
      "funder_ids": { "type": "keyword" },
      "region_ids": { "type": "keyword" },
      "citation_count": { "type": "long" },
      "usage_count": { "type": "long" },
      "publication_date": { "type": "date" }
    }
  }
}

```

cohort_stats mapping (tiny)

```json
PUT /cohort_stats
{
  "mappings": {
    "properties": {
      "cohort_key": { "type": "keyword" }, 
      "year": { "type": "integer" },
      "category": { "type": "keyword" },
      "article_type": { "type": "keyword" },
      "percentiles": {
        "properties": {
          "p10": { "type": "double" },
          "p25": { "type": "double" },
          "p50": { "type": "double" },
          "p75": { "type": "double" },
          "p90": { "type": "double" }
        }
      },
      "n": { "type": "long" },
      "computed_at": { "type": "date" },
      "version": { "type": "keyword" }
    }
  }
}

```

---

### G — Example workflow (end-to-end)

1. Nightly/weekly batch job (Spark or ES agg) computes percentiles per {year, category, article_type} → writes to cohort_stats (tiny).
2. User requests a filtered view (e.g., immunology 2024, OA articles). Backend:
   - Gets cohort_stats for that cohort.
   - Calls ES /docs/_search with runtime_mappings that embed the cohort percentiles as params (or uses script_fields). Runtime fields compute percentiles/NCI/scores per document on the fly and appear in aggregations.
   - If dashboard needs fast repeated queries, optionally use a background transform to populate entity_aggregates for that filter set.
3. If cohort logic or percentile definition changes, recompute cohort_stats and client queries immediately reflect new metrics without any doc reindex.


---

### H — Tradeoffs & when this pattern fails

- Runtime fields add CPU cost: If you compute heavy scripts over millions of docs often, runtime cost may be high. Then precompute into per_article_metrics.
- Aggregations over runtime fields are slower than doc_values: acceptable for dashboards with caching or pre-aggregates; if not, use precomputed metrics.
- Cross-index script access is not allowed: scripts cannot query another ES index at query time. That’s why cohort stats must be fetched first by the app and passed in as params (or stored as a small lookup doc per-query).


---

### I — Quick checklist you can follow now

- Move raw metrics into docs as base values (citation_count, etc.)
- Build cohort_stats small index and a job to recompute percentiles per cohort
- Implement client flow: fetch cohort_stats → run ES search with runtime_mappings using cohort params
- For frequently-used derived metrics, create per_article_metrics and update it in small batches
- Build entity-level entity_aggregates via ES Transforms for fast dashboards
- Add aliases, ILM, refresh tuning, and bulk update policies



---

