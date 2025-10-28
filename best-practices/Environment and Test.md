

## UAT vs. Proprod Testing


### ✅ What UAT Environment Is For

UAT = User Acceptance Testing

**Purpose**:
- Validate the system meets business requirements
- Real users confirm functionality, usability, and workflows are correct
- Data is representative but not too large
- Focus on end-to-end business scenarios, not engineering internals

**Who tests**: Business users / product owners
- Goal: “Are we ready to GO LIVE?”


---

### ✅ What Pre-Prod Environment Is For

Pre-prod = Production simulation

**Purpose**:
- Validate infrastructure + deployment process
- Integration with all external dependencies (auth, APIs, messaging, ES, etc.)
- Performance, scalability, reliability testing
- Full data volume and identical security setup as prod
- Final dress rehearsal before real deployment

**Who tests:** Engineering + DevOps
- Goal: “Will this deployment run smoothly in production?”


--- 

### ✅ What Testing Should Be Done in Each?


| Test Type                        | UAT | Pre-Prod |
|-----------------------------------|:---:|:--------:|
| Business Requirement Validation   | ✅  |    ➖    |
| User Workflow / Usability         | ✅  |    ➖    |
| Regression Functional Tests       | ✅  |    ✅    |
| Data Quality & Business Rules     | ✅  |    ✅    |
| Integration Validation            | ✅  |    ✅    |
| Load / Performance / Failover     | ➖  |    ✅    |
| Security & Access Control         | ➖  |    ✅    |
| Infrastructure & Deployment       | ➖  |    ✅    |
| Production-like Data Validation   | ➖  |    ✅    |

---

### ✅ Do We Need Both for Backend Pipeline + Data Systems?

**Yes — especially for large data pipelines**

Here’s why:
- UAT checks outputs make sense to business users → “Are grant matches correct? Are author profiles right?”
- Pre-prod checks data volume + operational readiness → “Can we process 20M docs daily without breaking ES?”

For ETL / Data pipelines / Search indexing, pre-prod prevents:
- Broken schema changes
- Performance collapses under full-load
- Bad data flowing into prod and corrupting downstream systems

Skipping pre-prod is how data disasters happen.


---

### ✅ Can UAT → Prod Directly?


Only in **small, low-risk apps** with:
- Low data volume
- Simple functionality
- Few integrations
- Zero infra complexity


**But not for your system** — you have:
- Daily incremental loads
- Schema evolution
- Multiple data sources (WOS, patents, grants, clinical trials, authors…)
- Multi-index Elasticsearch deployment
You definitely need pre-prod.

---

### 🧩 Bottom Line Recommendation

- Keep both UAT and Pre-Prod
- UAT validates business correctness.
- Pre-prod validates operational readiness.
- Both are required before go-live.

If you want, I can give you a strong deployment workflow that fits your daily ES pipeline updates:
- Feature → Dev → Automated Tests
- Promotion to UAT → Business validation
- Promotion to Pre-Prod → Full data + load test + smoke test + deployment rehearsal
- ✅ Prod

---


### ✅ UAT Sign-Off Checklist

Great — here’s a clear, actionable UAT + Pre-Prod sign-off checklist specifically designed for your academic data + Elasticsearch pipeline environment.


Focus: Business correctness + end-to-end workflows

#### ✅ Data Quality & Business Logic
- Author matching accuracy validated (random sampling + business verification)
- Institution / funder disambiguation makes sense to domain experts
- Paper topics / metrics align with user expectations
- No major regressions in search experience

#### ✅ Functionality / User Workflows
- Expert Finder produces relevant authors
- Grant Matching suggestions acceptable
- Novelty Analysis feedback matches research domain
- Citation maps and impact metrics render correctly

#### ✅ Schema-Level Expectations
- Expected fields present with correct data types
- No unexpected fields removed / renamed without communication

#### ✅ Validation Reports
- Compare reference dataset vs new version
- Edge-case users test approval (power users)

#### ✅ Approval
- Product lead + business owner sign-off
- Release notes reviewed with end-users

**Exit Rule** → “Users confirm the data and features are correct and useful.”

---

### ✅ Pre-Prod Sign-Off Checklist


Focus: Operational reliability + performance at scale

#### ✅ Data Volume & Load Testing
- Full reindex test on all index types (papers, patents, grants, authors…)
- Daily incremental pipeline succeeds under 20M doc load
- Query latency/throughput meet prod SLAs

#### ✅ Schema + API Compatibility
- ES index templates identical to prod
- Data contract validated with all consuming services
- Downstream analytics dashboards still work

#### ✅ Error Handling & Monitoring
- Airflow/Spark logs clean
- Alerting verified for failures (Slack/Teams)
- Retry + rollback works

#### ✅ Deployment + Infra Validation
- Blue/Green or Feature Flag tested
- Secrets + access control identical to prod
- Automated promotion scripts validated

#### ✅ Security & Compliance
- Audit logs active
- PII handling checks (if applicable)

#### ✅ Approval
- DevOps + Data Engineering sign-off
- Automated test results attached
- Runbook updated

**Exit Rule** → “The system can handle real traffic + real data safely.”

---

### 🔐 Final Promotion Gate: Go-Live Decision


**What Must Be Green?**

| Quality Area           | UAT | Pre-Prod |
|------------------------|:---:|:--------:|
| Business Validation    | ✅  |    ✅    |
| Data Quality           | ✅  |    ✅    |
| Operational Stability  | ✅  |    ✅    |
| Security & Deployment  | ✅  |    ✅    |

All areas must pass in both UAT and Pre-Prod before promoting to production.


When in doubt: fail fast → roll back → fix → re-promote.

---

### ⭐ Recommendation for Your System


Because your system:
- Daily incremental indexing
- Schema evolution with ongoing R&D features
- High throughput + latency sensitivity
- Critical downstream users (funding decisions)

You should **never** go UAT → Prod directly.
```text
Standard path: Dev → UAT → Pre-Prod → Prod
```

If you'd like, I can also provide one of these next:
- A) ✅ Template: UAT → Pre-Prod → Prod automated promotion workflow (Git branching + CI/CD)
- B) ✅ Data validation automation script (Spark + ES diffing + metrics reports)
- C) ✅ Dashboard designs for pipeline health + data trust score
- D) ✅ An Airflow DAG structure including rollbacks and reprocessing


---

### ✅ Deployment Workflow: Dev → UAT → Pre-Prod → Prod


#### 🔹 1️⃣ Branching Model (Avoid Chaos)

| Branch      | Purpose                                 | Who Pushes                |
|-------------|-----------------------------------------|---------------------------|
| `main`      | ✅ Production state only                | CI/CD, Release Manager    |
| `release/*` | ✅ Deployment candidates                | Dev lead                  |
| `develop`   | ✅ Latest tested code, passes unit/integration | Developers           |
| `feature/*` | Individual changes                      | Developers                |
| `hotfix/*`  | Critical prod fixes                     | DevOps, Senior Engineers  |


- UAT deploys from release/*
- Pre-Prod & Prod deploy from main


#### 🔹 2️⃣ Automated Promotion Rules

| Stage             | Trigger                      | Validation Steps                                | Output / Next Step                      |
|-------------------|-----------------------------|-------------------------------------------------|-----------------------------------------|
| Dev → UAT         | Merge to `release/*` branch  | CI: Unit tests, API contract checks             | Deploy to UAT environment               |
| UAT → Pre-Prod    | Business sign-off            | Regression, E2E, and Data Quality checks        | Merge `release/-` → `main`, auto-deploy to Pre-Prod |
| Pre-Prod → Prod   | DevOps & Performance sign-off| Load test, infra validation, rollback test      | Manual approval required for Prod deploy |


Automation everywhere. Human approval only at leaps in risk.

--- 

### 🔹 3️⃣ Promotion Flow Diagram


```text
(feature/*)  →  develop  →  release/-  →  main
                   │          │           │
                 Dev        UAT       Pre-Prod → Prod
```

--- 


### ✅ Deployment Tasks For Data Pipelines


| Step                     | Dev | UAT | Pre-Prod | Prod |
|--------------------------|:---:|:---:|:--------:|:----:|
| Spark Code Deploy        | ✅  | ✅  |    ✅    |  ✅  |
| ETL Schema Change Validation | ✅  | ✅  |    ✅    |  ✅  |
| Unit Tests               | ✅  | ➖  |    ➖    |  ➖  |
| Data Quality Tests       | ✅  | ✅  |    ✅    |  ✅  |
| Full Volume Load         | ➖  | ➖  |    ✅    |  ✅  |
| Monitoring + Alerts      | ➖  | ✅  |    ✅    |  ✅  |
| Rollback Strategy Test   | ➖  | ➖  |    ✅    |  ✅  |


--- 

### ✅ Elasticsearch Index Promotion Strategy


| Phase    | Index Strategy                                                                 |
|----------|-------------------------------------------------------------------------------|
| UAT      | Use alias-based switching with sandbox/test data for safe user validation      |
| Pre-Prod | Reindex all indices using full production data volumes to simulate real load   |
| Prod     | Blue-Green deployment: build new indices, then atomically switch aliases to cut over with zero downtime |

- In all phases, use Elasticsearch aliases to enable instant rollback if needed.
- Always validate data and mappings before switching aliases in Pre-Prod and Prod.
- For Prod, ensure monitoring and alerting are active during and after alias switch.

- Rollback = Just point alias back to previous index 💡
- No downtime. No damaged data.


--- 

### ✅ Sign-Off Gates (What must be green?)

**Business Gate (UAT → Pre-Prod)**
- Data correctness approved ✅
- Integration scenarios pass ✅
- Major dashboards functional ✅

**Engineering Gate (Pre-Prod → Prod)**
- Airflow/Spark jobs stable ✅
- Query latency meets SLA ✅
- Alerts + rollbacks validated ✅
- Deploy automation validated ✅

✅ Only when both gates pass → Promote to PROD

--- 


### ✅ CI/CD Tooling (Example Tech Stack)

| Feature                      | Recommended Tool(s)                          |
|------------------------------|----------------------------------------------|
| Pipeline Orchestrator        | GitHub Actions, Azure DevOps, GitLab CI      |
| Build & Test Pipeline        | GitHub Actions, Jenkins                      |
| Infrastructure Deployment    | Terraform, ArgoCD                            |
| Data Quality & Schema Tests  | Great Expectations, DataHub                  |
| Canary / Blue-Green Routing  | Elasticsearch Aliases, Feature Flags         |


--- 


### 🔐 Final Reality Check

-Skipping Pre-Prod is a gamble.
-Your system handles:
  - Millions of daily updates
  - Critical research metrics
  - Production-scale ES writes + search
- Pre-Prod is your safety net.


Would you like me to generate B next?

B) ✅ Data validation automation script (Spark + ES diffing + metrics reports)
Or would you rather go straight to:
C) Dashboard designs for pipeline health + data trust score
D) Airflow DAG structure with rollback & reprocessing
Which one do you want next?


---


### Data validation automation script 


Nice — below is a complete, practical data-validation automation package you can drop into your CI/CD or run as scheduled jobs. It covers:
- Spark-side validation for ETL outputs (schema, counts, nulls, distribution, checksums)
- Elasticsearch index validation/diff (counts, mappings, top-term diffs, sampled doc diffs)
- Report generation (JSON + HTML) with pass/fail gates and exit codes for automation
- Airflow DAG snippet to wire it into your pipeline
I kept code portable and well-commented. Copy/paste, adapt paths/hosts, and wire it into your CI.


---

#### 1) Project layout (suggested)

```text
validator/
├─ conf/
│  ├─ expected_schema.json
│  └─ validator_config.yml
├─ spark_data_validation.py
├─ es_index_diff.py
├─ report_generator.py
├─ templates/
│  └─ report_template.html
└─ dags/
   └─ validate_and_promote_dag.py   # Airflow snippet
```

---

#### 2) conf/validator_config.yml (example)

```yaml
env: preprod
run_id: "{{ timestamp }}"
spark:
  app_name: "data-validation"
  master: "yarn"   # or local[*] for testing
source:
  format: parquet
  path: "s3a://my-bucket/indexed/papers/{{run_date}}/"
  primary_key: "paper_id"
elasticsearch:
  host: "https://es-preprod.internal:9200"
  index: "papers_v2"
  baseline_index: "papers_v1"
report:
  output_dir: "/tmp/validation_reports"
thresholds:
  max_null_rate: 0.25
  max_schema_diff_fields: 0
  max_row_drop_pct: 0.5
  max_doc_mismatch_pct: 2.0
  sample_size: 1000
```

Edit thresholds to fit your tolerance.

---


#### 3) spark_data_validation.py (PySpark job)

Save this as spark_data_validation.py. It returns non-zero exit code on critical failures, writes JSON metrics to report.output_dir/<run_id>/spark_metrics.json.

```python
"""
spark_data_validation.py
PySpark job to run data quality checks on an ETL output dataset.

Usage:
  spark-submit --conf ... spark_data_validation.py --config conf/validator_config.yml --run-date 2025-10-28
"""

import argparse
import json
import os
import sys
import uuid
import yaml
from datetime import datetime
from pyspark.sql import SparkSession, functions as F, types as T

def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def start_spark(app_name, master):
    return SparkSession.builder.appName(app_name).master(master).getOrCreate()

def compute_basic_metrics(df, pk):
    metrics = {}
    metrics['row_count'] = df.count()
    metrics['distinct_pk_count'] = df.select(pk).distinct().count()
    metrics['dup_pk_count'] = metrics['row_count'] - metrics['distinct_pk_count']
    metrics['sample_checksum'] = df.select(F.md5(F.concat_ws("||", *df.columns)).alias("chk")).agg(F.md5(F.collect_list("chk")).alias("global_chk")).collect()[0]["global_chk"]
    return metrics

def compute_null_rates(df):
    # returns dict col -> null_pct
    total = df.count()
    nulls = {}
    for c in df.columns:
        nulls[c] = df.filter(F.col(c).isNull() | (F.col(c) == "")).count() / max(total, 1)
    return nulls

def top_value_counts(df, cols, k=10):
    out = {}
    for c in cols:
        rows = df.groupby(c).count().orderBy(F.desc("count")).limit(k).toPandas()
        out[c] = rows.to_dict(orient="records")
    return out

def schema_diff(expected_schema, actual_schema):
    # expected_schema, actual_schema: lists of {"name":..., "type":...}
    expected_map = {c['name']: c['type'] for c in expected_schema}
    actual_map = {c['name']: c['type'] for c in actual_schema}
    added = [c for c in actual_map.keys() if c not in expected_map]
    removed = [c for c in expected_map.keys() if c not in actual_map]
    type_mismatches = []
    for k in expected_map.keys() & actual_map.keys():
        if expected_map[k].lower() != actual_map[k].lower():
            type_mismatches.append({"col": k, "expected": expected_map[k], "actual": actual_map[k]})
    return {"added": added, "removed": removed, "type_mismatches": type_mismatches}

def load_expected_schema(path):
    with open(path, "r") as f:
        return json.load(f)  # expect [{"name":"col","type":"string"}...]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--run-date", required=False)
    args = parser.parse_args()

    cfg = load_config(args.config)
    run_id = f"{cfg.get('run_id','')}_{uuid.uuid4().hex[:6]}_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}"
    output_base = os.path.join(cfg['report']['output_dir'], run_id)
    os.makedirs(output_base, exist_ok=True)

    spark = start_spark(cfg['spark']['app_name'], cfg['spark'].get('master', 'local[*]'))

    # read dataset
    src_path = cfg['source']['path'].replace("{{run_date}}", args.run_date or "")
    print(f"[INFO] reading source from {src_path}")
    df = spark.read.format(cfg['source']['format']).load(src_path)

    # expected schema
    expected_schema = load_expected_schema(os.path.join("conf", "expected_schema.json"))
    actual_schema = [{"name": f.name, "type": f.dataType.simpleString()} for f in df.schema.fields]

    # metrics
    basic = compute_basic_metrics(df, cfg['source']['primary_key'])
    nulls = compute_null_rates(df)
    top_values = top_value_counts(df, cols=[cfg['source']['primary_key']], k=20)

    schema_check = schema_diff(expected_schema, actual_schema)

    # compute row-level sampling diff vs previous snapshot if available (optional)
    # For large tables it's expensive; this demo computes hashed sample
    sample_size = cfg.get('thresholds', {}).get('sample_size', 1000)
    sampled = df.select(cfg['source']['primary_key'], *df.columns).limit(sample_size).toPandas().to_dict(orient="records")

    metrics = {
        "run_id": run_id,
        "env": cfg.get("env"),
        "timestamp": datetime.utcnow().isoformat(),
        "basic": basic,
        "null_rates": nulls,
        "top_values": top_values,
        "schema_check": schema_check,
        "sample_row_count": len(sampled),
    }

    # Evaluate against thresholds to determine pass/fail
    thresholds = cfg.get("thresholds", {})
    failures = []
    # null rate checks (only check high risk columns)
    for col, pct in nulls.items():
        if pct > thresholds.get("max_null_rate", 0.25):
            failures.append({"type":"null_rate", "col":col, "pct":pct})
    # schema break
    if len(schema_check['removed']) > thresholds.get("max_schema_diff_fields", 0):
        failures.append({"type":"schema_removed", "removed": schema_check['removed']})
    # row drop check: compare expected vs actual if baseline row count known (omitted here)
    metrics['failures'] = failures
    metrics['status'] = "FAIL" if failures else "PASS"

    # write metrics
    out_path = os.path.join(output_base, "spark_metrics.json")
    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2, default=str)
    print(f"[INFO] written metrics to {out_path}")

    spark.stop()

    # exit non-zero for CI if critical failures
    if failures:
        print(f"[ERROR] validation failed with {len(failures)} failures.")
        sys.exit(2)
    else:
        print("[INFO] validation passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

**Notes**:
- Replace source.path with your S3/HDFS/DB path.
- This is intentionally simple — you should extend top_value_counts() to include domain-specific fields (e.g., author_name, affiliation_id).

--- 

#### 4) es_index_diff.py (Elasticsearch comparison)

Compare mappings, doc counts, top terms, and sample doc-level diffs between index and baseline_index. Writes es_metrics.json to the same report folder.

```python
"""
es_index_diff.py
Run index-level and sample-level comparisons between two ES indices.
Requires: elasticsearch python client (pip install elasticsearch)
"""

import argparse
import json
import os
import sys
from datetime import datetime
from elasticsearch import Elasticsearch, helpers
from collections import Counter

def load_config(path):
    import yaml
    with open(path) as f:
        return yaml.safe_load(f)

def es_client(host):
    # host can include auth in the URL if needed, or you can pass http_auth param
    return Elasticsearch(hosts=[host], verify_certs=False)

def get_index_stats(es, index):
    si = es.indices.get(index=index)
    stats = es.indices.stats(index=index, metric="docs,store")
    mapping = si[index]['mappings']
    doc_count = int(stats['_all']['primaries']['docs']['count'])
    return {"mapping": mapping, "doc_count": doc_count}

def top_terms(es, index, field, size=20):
    # terms agg
    body = {
        "size": 0,
        "aggs": {
            "top_terms": {
                "terms": {"field": field, "size": size}
            }
        }
    }
    res = es.search(index=index, body=body)
    buckets = res['aggregations']['top_terms']['buckets']
    return [{ "term": b['key'], "count": b['doc_count']} for b in buckets]

def sample_docs(es, index, pk_field, sample_size):
    # use simple query with random_score if docs small; otherwise use scroll and sample locally
    # for portability, we use a deterministic scan and take every Nth doc
    docs = []
    resp = es.search(index=index, body={"query": {"match_all": {}}, "_source": [pk_field], "size": min(1000, sample_size)}, scroll='1m')
    sid = resp['_scroll_id']
    total = resp['hits']['total']['value'] if isinstance(resp['hits']['total'], dict) else resp['hits']['total']
    hits = resp['hits']['hits']
    docs.extend(h['_source'] for h in hits)
    while len(docs) < sample_size and hits:
        resp = es.scroll(scroll_id=sid, scroll='1m')
        sid = resp['_scroll_id']
        hits = resp['hits']['hits']
        docs.extend(h['_source'] for h in hits)
        if len(docs) >= sample_size:
            break
    return docs[:sample_size]

def compare_samples(sample_a, sample_b, pk_field):
    # sample_a/b are lists of dicts (source)
    map_a = {d[pk_field]: d for d in sample_a if pk_field in d}
    map_b = {d[pk_field]: d for d in sample_b if pk_field in d}
    common = set(map_a.keys()) & set(map_b.keys())
    only_a = set(map_a.keys()) - set(map_b.keys())
    only_b = set(map_b.keys()) - set(map_a.keys())
    diffs = []
    for k in list(common)[:100]:  # limit diff detail
        a = map_a[k]
        b = map_b[k]
        if a != b:
            diffs.append({"pk": k, "a": a, "b": b})
    return {"common_count": len(common), "only_a": len(only_a), "only_b": len(only_b), "diffs_sample": diffs[:50]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    cfg = load_config(args.config)
    es = es_client(cfg['elasticsearch']['host'])
    index = cfg['elasticsearch']['index']
    baseline = cfg['elasticsearch']['baseline_index']
    pk = cfg['source'].get('primary_key', 'id')
    sample_size = cfg.get('thresholds', {}).get('sample_size', 1000)

    out_dir = os.path.join(cfg['report']['output_dir'], args.run_id)
    os.makedirs(out_dir, exist_ok=True)

    stats1 = get_index_stats(es, index)
    stats2 = get_index_stats(es, baseline)
    mapping_changes = {"present_in_index": list(stats1['mapping'].keys()), "present_in_baseline": list(stats2['mapping'].keys())}
    # doc count diff
    doc_count_diff = stats1['doc_count'] - stats2['doc_count']
    doc_count_pct = 100.0 - doc_count_diff / max(stats2['doc_count'], 1)

    # top term diffs for fields of interest (e.g., 'subject.keyword')
    fields_to_check = ["subject.keyword", "venue.keyword", pk]
    top_terms_cmp = {}
    for f in fields_to_check:
        try:
            top_terms_cmp[f] = {
                index: top_terms(es, index, f, size=20),
                baseline: top_terms(es, baseline, f, size=20)
            }
        except Exception as e:
            top_terms_cmp[f] = {"error": str(e)}

    sample_a = sample_docs(es, index, pk, sample_size)
    sample_b = sample_docs(es, baseline, pk, sample_size)
    sample_cmp = compare_samples(sample_a, sample_b, pk)

    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "index": index,
        "baseline_index": baseline,
        "doc_count_index": stats1['doc_count'],
        "doc_count_baseline": stats2['doc_count'],
        "doc_count_diff": doc_count_diff,
        "doc_count_pct": doc_count_pct,
        "mapping_changes": mapping_changes,
        "top_terms_cmp": top_terms_cmp,
        "sample_cmp_summary": sample_cmp
    }

    out_path = os.path.join(out_dir, "es_metrics.json")
    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2, default=str)
    print(f"[INFO] ES metrics written to {out_path}")

    # Evaluate thresholds
    thresholds = cfg.get('thresholds', {})
    failures = []
    if abs(doc_count_pct) > thresholds.get("max_doc_mismatch_pct", 2.0):
        failures.append({"type":"doc_count_mismatch", "pct": doc_count_pct})
    if sample_cmp['only_a'] + sample_cmp['only_b'] > thresholds.get("max_doc_mismatch_pct", 2.0) / 100.0 - sample_size:
        failures.append({"type":"sample_mismatch", "only_a": sample_cmp['only_a'], "only_b": sample_cmp['only_b']})

    metrics['failures'] = failures
    metrics['status'] = "FAIL" if failures else "PASS"

    if failures:
        print(f"[ERROR] ES validation failed: {failures}")
        sys.exit(3)
    else:
        print("[INFO] ES validation passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

**Notes**:
- verify_certs=False used for private certs; use proper TLS settings in prod.
- For very large indices, sampling strategy must be more robust — consider reservoir sampling via scroll + hashing.

---

#### 5) report_generator.py (JSON → HTML + summary)

Aggregates spark_metrics.json and es_metrics.json into a single HTML report and a small CSV summary for dashboards.

```python
"""
report_generator.py
Takes run_id folder and produces an HTML report (report.html) and a summary CSV for dashboards.
"""

import argparse
import json
import os
from jinja2 import Environment, FileSystemLoader
import pandas as pd

def load_json(path):
    with open(path) as f:
        return json.load(f)

def generate_html(run_dir, template_dir="templates"):
    spark = load_json(os.path.join(run_dir, "spark_metrics.json"))
    es = load_json(os.path.join(run_dir, "es_metrics.json"))

    env = Environment(loader=FileSystemLoader(template_dir))
    tmpl = env.get_template("report_template.html")
    html = tmpl.render(spark=spark, es=es)
    out = os.path.join(run_dir, "report.html")
    with open(out, "w") as f:
        f.write(html)
    print(f"[INFO] HTML report generated at {out}")
    return out

def generate_summary_csv(run_dir):
    spark = load_json(os.path.join(run_dir, "spark_metrics.json"))
    es = load_json(os.path.join(run_dir, "es_metrics.json"))
    df = pd.DataFrame([{
        "run_id": spark["run_id"],
        "timestamp": spark["timestamp"],
        "spark_status": spark.get("status"),
        "es_status": es.get("status"),
        "spark_rows": spark["basic"]["row_count"],
        "es_doc_count": es["doc_count_index"]
    }])
    out = os.path.join(run_dir, "summary.csv")
    df.to_csv(out, index=False)
    print(f"[INFO] summary csv at {out}")
    return out

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--template-dir", default="templates")
    args = parser.parse_args()

    html = generate_html(args.run_dir, args.template_dir)
    csv_path = generate_summary_csv(args.run_dir)
    print(f"[INFO] done. report={html} summary={csv_path}")

if __name__ == "__main__":
    main()
```

And a minimal templates/report_template.html (simple, extendable):

```html
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Validation Report - {{ spark.run_id }}</title></head>
<body>
  <h1>Validation Report - {{ spark.run_id }}</h1>
  <h2>Overview</h2>
  <ul>
    <li>Run: {{ spark.run_id }}</li>
    <li>Timestamp: {{ spark.timestamp }}</li>
    <li>Spark status: {{ spark.status }}</li>
    <li>ES status: {{ es.status }}</li>
  </ul>
  <h2>Spark Metrics</h2>
  <pre>{{ spark | tojson(indent=2) }}</pre>

  <h2>Elasticsearch Metrics</h2>
  <pre>{{ es | tojson(indent=2) }}</pre>
</body>
</html>
```

---

#### 6) Airflow DAG snippet (dags/validate_and_promote_dag.py)

Run tasks in sequence: run Spark validation, run ES diff, generate report, and fail gate blocks deployment on failure.

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "retries": 0,
    "email_on_failure": True,
    "email": ["oncall@example.com"]
}

with DAG(
    dag_id="validate_and_promote",
    default_args=default_args,
    schedule_interval=None,
    start_date=datetime(2025,1,1),
    catchup=False,
) as dag:

    run_spark_validation = BashOperator(
        task_id="spark_data_validation",
        bash_command="spark-submit --master yarn /opt/validator/spark_data_validation.py --config /opt/validator/conf/validator_config.yml --run-date {{ ds }} || exit 2"
    )

    run_es_diff = BashOperator(
        task_id="es_index_diff",
        bash_command="python3 /opt/validator/es_index_diff.py --config /opt/validator/conf/validator_config.yml --run-id {{ ts_nodash }} || exit 3"
    )

    generate_report = BashOperator(
        task_id="generate_report",
        bash_command="python3 /opt/validator/report_generator.py --run-dir /tmp/validation_reports/{{ ts_nodash }} || exit 4"
    )

    # Manual human approval before promotion
    wait_for_approval = BashOperator(
        task_id="wait_for_approval",
        bash_command="echo 'Manual approval required. Use Airflow UI to continue.'; exit 0"
    )

    run_spark_validation >> run_es_diff >> generate_report >> wait_for_approval
```

Replace bash_command paths with where you deploy the validator code.

---

### 7) How to wire this into CI/CD and promotion rules

- CI runs unit tests on code. On merge to release/*, trigger UAT deploy and run validations with spark_data_validation.py (smaller sample).
- On release/- → main merge, trigger Pre-Prod job that runs Spark + ES validation with full dataset (set sample_size large or perform full reindex check).
- If validation tasks exit non-zero, block the promotion and send alerts (Slack + email).
- If all pass and manual signoff is given, run Prod deployment and optionally run the same validator in a light mode after deploy to confirm success.

Use the exit codes to fail the pipeline and require human attention:
- 2 — Spark validation failed (data quality)
- 3 — ES validation failed (index mismatch)
- 4 — Report generation or downstream failure

---

#### 8) Suggested checks & thresholds (practical)

Tune thresholds in validator_config.yml.
- Document / row count mismatch: fail if > 2% difference (unless you expect deletion).
- Null rate for required keys (e.g., paper_id, title): fail if > 5%. For soft fields (abstract), warn at 25%.
- Schema column removal: fail immediately. Column type change: warn (manual review).
- Unique PK duplicates: fail if any duplicates.
- Query latency estimate (from Pre-Prod): warn if 95th percentile exceeds SLA. You can add these as additional metrics by running sample queries and measuring response times.

---

#### 9) Alerting & Runbook

- Push failures to Slack with link to report.html. Include a runbook link and rollback steps.
- Rollback approach for ES: use aliases to point to previous index (index_v1 → index_v0). For DB: restore from snapshot or fail upstream consumers.
- Reprocessing: add Airflow DAG to re-run ETL for the affected time slice.

---

#### 10) Next steps I can provide immediately

Pick one and I’ll generate it now (no waiting):

1. A) Great Expectations integration templates to run these checks declaratively (expectation suites).
2. B) A fully fleshed Airflow DAG with retries/SLAs/Slack notifications and automatic alias swap on success.
3. C) A ready-to-run Terraform / ArgoCD snippet to install this validator into a Kubernetes environment.
4. D) Tailored thresholds + a sample expected_schema.json generated from one of your indices (if you paste a small sample schema or mapping).
Which one do you want next?


---

### SLAs = Service Level Agreements


SLAs = Service Level Agreements — the performance, reliability, and quality targets your system must meet in production.
For your backend data pipelines + Elasticsearch search system, the SLAs should cover:


#### ✅ 1️⃣ Data Pipeline SLAs


| Category         | Example Targets                                         |
|------------------|--------------------------------------------------------|
| Freshness        | Daily ingestion complete by 6 AM UTC                    |
| Latency          | Incremental pipeline completes within 2 hours           |
| Success Rate     | ≥ 99.5% successful jobs per month                       |
| Data Accuracy    | ≥ 99% expected field population rate                    |
| Schema Stability | Any breaking changes must be announced 7 days in advance|
| Rollback Time    | < 30 mins under failure scenario                        |



#### ✅ 2️⃣ Search / Query SLAs (Elasticsearch layer)


| Category         | Example Targets                                                                 |
|------------------|--------------------------------------------------------------------------------|
| Query Latency    | < 200 ms P95 for filter + keyword queries; < 500 ms P95 for semantic/embedding searches |
| Throughput       | ≥ 200 requests/sec at steady state                                              |
| Availability     | ≥ 99.9% uptime per quarter                                                      |
| Indexing Latency | New updates visible in ES < 5 min after pipeline finish                         |
| Consistency      | No schema mismatch or index mapping conflict allowed                            |


#### ✅ 3️⃣ Data Quality SLAs


| Category                          | Example Targets                                 |
|------------------------------------|------------------------------------------------|
| Deduplication Quality              | False duplicates < 2%                          |
| Entity Linking (author/institution)| ≥ 95% correct top-1 match                      |
| Topic Classification               | ≥ 90% accuracy on validation set               |
| Citation / Metric Completeness     | ≥ 98% expected values populated                |


#### ✅ 4️⃣ Security / Compliance SLAs

| Category         | Example Targets                                                    |
|------------------|-------------------------------------------------------------------|
| Access Control   | Permissions sync within 10 minutes                                |
| Audit Logging    | 100% of actions logged and retained for at least 90 days          |
| Data Retention   | Production snapshots every 24 hours; recovery RTO < 4 hours       |


#### ✅ SLA Summary Cheat Sheet



| Layer         | Purpose                   | Minimum SLA              |
|---------------|---------------------------|--------------------------|
| Pipelines     | Deliver data reliably     | ≥ 99.5% success rate     |
| Search        | User-facing performance   | P95 latency < 500 ms     |
| Data Quality  | Trust & analytics         | > 95% accuracy           |
| Availability  | Business continuity       | ≥ 99.9% uptime           |


#### Why SLAs matter especially for your system

You’re powering:

- Expert finding
- Research funding decision support
- Novelty assessment metrics

- ❌ Slow or inaccurate data → wrong judgments → business/user trust failure
- ✅ SLAs create clear expectations + objective promotion gates

If you'd like, I can help you define:

- ✅ SLOs (service level objectives)
- ✅ SLIs (service level indicators)
- ✅ Dashboards to measure them
- ✅ Alert thresholds + auto-rollback policy

Which one do you want next:
- A) Dashboards + Alert thresholds
- B) SLO vs SLA documentation template
- C) CI/CD promotion gates based on SLIs










ChatGPT can make mistakes. Check important info.

