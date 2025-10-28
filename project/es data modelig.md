
## ES Data Modeling

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


## Design and Data Modeling of Incites Search Engine


### 1. Background

We have migrated Incites Application backend from Oracle Exadata to Elasticsearch (ES) engine. ES is the innovated search and analytic engine and it's  the technology stack different from Oracle and new to most people, this document describes the design and data modeling of Incite backend data structure, as well as various strategies to implement 100% accuracy and the high performance for Incites on ES.


#### 1.1. Incites Data


- 40 years’ WoS Core documents from 1980 to now
- Two datasets: the WoS core dataset (64.5+ million) and the WoS core dataset with ESCI (67.9+ million)
- Six contexts: People, Organizations, Regions, Journal, Category, and Funder
- Max number of entity corresponding to the context shown in Table-1


**Context Total Count of Entity**

| Context        | Total Count of Entity |
|---------------|----------------------|
| People        | 49.5+ million        |
| WoS Author    | 24.6+ million        |
| Organizations | 14.5k               |
| Regions       | 2,083               |
| Category      | 255                 |
| Journal       | 220k+               |
| Funder        | 1,244               |


Table-1: max number of entity for various contexts

**Notes**: all data are from the r111 UDM data (Sept, 2020)


#### 1.2. Incites on Oracle


- Context based v table data model on Oracle
- About 150 context based v tables in total
- 20+ individual v tables on average for each context 


---


### 2. Data Modeling on ES


#### 2.1.  Incites on ES


The context based v table data model on Oracle is transformed and modeled to the document based data structure on ES

- One Json document for each article (UT) 
- All context data (entity) related to one article are stored to the same document
- The document is indexed to the search engine
- UT based index for all contexts
- Author based index for people context


**IndexTypeContextIndex size**

| Index Name   | Index Type / Key      | Contexts Covered                        | Index Size   |
|--------------|-----------------------|-----------------------------------------|--------------|
| incites      | UT-based, static      | Organizations, Regions, Categories, Journal, Funder | 2.6 TB       |
| people       | Author-based, static  | Researchers                             | 478 GB       |
| WoS author   | Author-based, static  | Researchers                             | 318 GB       |
| myorg        | UT-based, dynamic     | All contexts for MyOrg dataset          | > 20 GB      |


ES is the distributed search and analytics engine, and there are a lot of benefits: horizontal scalability and modular growth, fault tolerance and redundancy, low latency, and so on. But ES also has the known feature, the document counts (and the results of any sub aggregations) in the terms aggregation are not always accurate. This is because each shard provides its own view of what the ordered list of terms should be and these are combined to give a final view.


#### 2.2.  Strategies for accuracy and performance


We apply the following strategies to meet  the Incites requirements of 100%  accuracy and the high performance (< 2 sec) simultaneously.

- **Denormalization** - De-normalize documents for context having massive number of entities to index by routing
- **Routing** - Routing and index all related documents to the same shard to ensure the aggregation accuracy with the small shard size 
- **Shard Size** (shard_size query parameter) - Select the appropriate shard size to meet the requirement of both accuracy and performance
- **Two Step Queries** - Use two-step queries to improve the performance further



**Denormalization**

In general, an article could be co-authored by multiple authors, and one author could publish multiple articles. Similar to the Incites data model on Oracle,   documents are denormalized by the unique author key on ES.

- Denormalize only when context contains massive number of entities
- Denormalize in order to index by routing
- Combine the article number and the entity key to the primary key 


**Routing**


The routing technology on ES is used to route and index a document to the specific shard. A custom routing value could be used to ensure that all related documents—for instance, all the documents belonging to the same author—are stored on the same shard. 


- Ensure the accuracy with the small shard size
- Applied routing when context has massive number of entities
- Capable of accessing all documents for each entity on shard
- Accurately computing all indicator values on shard
- Return the accurate top N in short time from shard
- Routing documents by author key in people index for People context
- Routing documents by journal key in incites index for Journal context 

For example, we are able to use the requested size value (the top N) for the shard size to get the accurate result for the top N entities (N = 25, 50, 500, etc.) from 44.5 million people entities in less than 1 sec.


**Shard Size** (shard_size query parameter)


The higher the requested size is, the more accurate the results will be, but also, the more expensive it will be to compute the final results (both due to bigger priority queues that are managed on a shard level and due to bigger data transfers between the nodes and the client).


So, it is important for us to choose the appropriate shard size to meet the requirements of  both accuracy and performance. We use the following strategies to choose the size for the different contexts

- **Context without routing**:  we select the max number of entity for the shard size and ES return all entities to ensure the accuracy without the performance issue because the shard size for these contexts is not big. For example, we choose 2500 as the shard size for Regions context because the total number of Regions entity is 2083.
- **Context with routing**: we are able to choose the small value for the shard size to ensure the accuracy because entities data are routed and approximately evenly distributed on shard. For example, regarding to the edge case top 50K entities,  we  are able to choose 2000  for the shard size for People context to return 160K entities with accurate data from shards to get the top 50K people.
- **Context-specific shard size** is configurable and the value can be updated when the number of entities increases significantly
- **Dynamic shard size** corresponding to  the request size can be implemented for further optimization. For example, when customer is asking the top 25 or top 500 people,  we are able to choose 25 or 500 as the shard size and it's enough to ensure the accuracy.


**Two Step Queries**


Because Incites application provides up to 20+ indicators for each context and customer may request most or even all indicators, if we send one query with all indicators, it will consume a lot of ES resources (memory and CPU etc.) for unnecessary computing and it’s inefficient and very slow.

In order to improve the performance and efficiency further, as a general rule, we split the query into two steps for all contexts as following

  - **Step-1**: Send the 1st query with the sort indicator  to get the top N key values
  - **Step-2**: Pass the top N key values as the filter in the 2nd query to reduce the dataset to retrieve all requested indicators for top N entities

Two-step queries help to avoid the unnecessary computing,  minimize the resource usage and reduce the whole response time,  reduce the old gc in JVM, as well as improve the cluster stability greatly.

---

### 3. Scalability

The horizontal scalability on ES provides the capability for us to quickly develop and meet the potential data related requirement changes 

- Expand documents from the existing 40 years to all years
- Add the new collection other than WoS core
- Add the new dataset


The plugin technology on ES provides the capability for us to quickly develop and meet the potential aggregation functionality related requirement changes 

- The standard metrics aggregation supported by ES: Min, Max, Avg, Sum, Percentile, Stat, Cardinality etc.
- The special metrics  aggregation are supported by developing plugins: H-index, Ratio, Quartile, Percent, etc.

The 1pca framework technology provides the capability for us to quickly develop and meet the potential business related requirement changes 


