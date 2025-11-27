
## Production-ready Databricks SQL Dashboard 


Below is a complete, production-ready Databricks SQL Dashboard to monitor:

- ✔  CDF ingestion progress for all upstream tables
- ✔  Last processed version vs current Delta version
- ✔  Lag (number of versions behind)
- ✔  Time since last successful ingestion
- ✔  CDF table status (OK, BEHIND, STALE, ERROR)
- ✔  Alerts for tables not updated in 24 hours

You can paste these queries directly into a Databricks SQL dashboard, with widgets or filters.

---

### 📊 1. MASTER MONITORING QUERY (CDF Pipeline Overview)

This single query powers a table tile showing ingestion status per table.

```sql
WITH state AS (
    SELECT 
        table_name,
        last_processed_version,
        updated_at
    FROM pipeline_state.cdf_progress
),

current AS (
    SELECT 
        table_name,
        MAX(version) AS current_version
    FROM (
        SELECT DISTINCT 
            table_name,
            version
        FROM (
            SELECT 
                table_name,
                version
            FROM delta.`/dbfs/path/to/your/tables`  -- Optional if using external tables
        )
    )
    GROUP BY table_name
),

merged AS (
    SELECT
        s.table_name,
        s.last_processed_version,
        c.current_version,
        c.current_version - s.last_processed_version AS version_lag,
        CAST(s.updated_at AS TIMESTAMP) AS updated_at,
        NOW() AS now
    FROM state s
    LEFT JOIN current c ON s.table_name = c.table_name
)

SELECT
    table_name,
    last_processed_version,
    current_version,
    version_lag,
    updated_at,

    CASE 
        WHEN version_lag = 0 THEN 'OK'
        WHEN version_lag BETWEEN 1 AND 10 THEN 'BEHIND'
        WHEN version_lag > 10 THEN 'CRITICAL'
        WHEN updated_at < now() - INTERVAL 1 DAY THEN 'STALE'
        ELSE 'UNKNOWN'
    END AS status

FROM merged
ORDER BY status, version_lag DESC;
```

---

### 📉 2. LAG TREND OVER TIME (Line Chart)

Tracks ingestion lag daily.

```sql
SELECT
    table_name,
    DATE(updated_at) AS day,
    MAX(current_version - last_processed_version) AS lag
FROM pipeline_state.cdf_progress
GROUP BY table_name, DATE(updated_at)
ORDER BY day DESC;
Use in a line chart with filters for table_name.
```

---

### 💡 3. INGESTION HEAT MAP (Tables × Date)

Shows activity per table.

```sql
SELECT
    table_name,
    DATE(updated_at) AS day,
    COUNT(- 👉 ) AS updates
FROM pipeline_state.cdf_progress
GROUP BY table_name, DATE(updated_at)
ORDER BY day DESC, table_name;

```
Display as a heatmap.

---

### 🆘 4. Identify Tables Behind by More Than N Versions

```sql
SELECT
    table_name,
    last_processed_version,
    current_version,
    (current_version - last_processed_version) AS lag
FROM pipeline_state.cdf_progress s
JOIN (
    SELECT table_name, MAX(version) AS current_version
    FROM delta.`/your/tables/root`
    GROUP BY table_name
) c USING (table_name)
WHERE (current_version - last_processed_version) > 5
ORDER BY lag DESC;
```

---

### ⏳ 5. Tables Not Updated in Last 24 Hours

```sql
SELECT 
    table_name,
    last_processed_version,
    updated_at,
    NOW() - updated_at AS time_since_update
FROM pipeline_state.cdf_progress
WHERE updated_at < NOW() - INTERVAL 1 DAY
ORDER BY updated_at;
```

---

### 🟥 6. Critical Lag Alerts (Version lag > 50)

```sql
SELECT 
    table_name,
    last_processed_version,
    current_version,
    (current_version - last_processed_version) AS lag
FROM (
    SELECT 
        s.table_name,
        s.last_processed_version,
        c.current_version
    FROM pipeline_state.cdf_progress s
    JOIN (
        SELECT 
            table_name,
            MAX(version) AS current_version
        FROM delta.`/your/tables/root`
        GROUP BY table_name
    ) c USING (table_name)
) x
WHERE lag > 50
ORDER BY lag DESC;
```

---

### 🟢 7. Tablets That Have Never Been Processed (first run not completed)

```sql
SELECT 
    table_name
FROM (
    SELECT DISTINCT table_name FROM upstream_table_list  -- Your metadata table
) upstream
LEFT JOIN pipeline_state.cdf_progress state
    USING (table_name)
WHERE state.table_name IS NULL;
```

---

### 🎛️ 8. Summary KPI Tiles

KPI 1 – Total Tables

```sql
SELECT COUNT(- 👉 ) FROM upstream_table_list;
```

KPI 2 – Tables Behind (> 0 versions)

```sql
SELECT COUNT(- 👉 ) 
FROM (
    SELECT 
        s.table_name,
        c.current_version - s.last_processed_version AS lag
    FROM pipeline_state.cdf_progress s
    JOIN (
        SELECT table_name, MAX(version) AS current_version
        FROM delta.`/your/tables/root`
        GROUP BY table_name
    ) c USING (table_name)
) 
WHERE lag > 0;
```

KPI 3 – Critical (> 10 versions)

```sql
SELECT COUNT(- 👉 ) FROM (
    SELECT 
        c.current_version - s.last_processed_version AS lag
    FROM pipeline_state.cdf_progress s
    JOIN (
        SELECT table_name, MAX(version) AS current_version
        FROM delta.`/your/tables/root`
        GROUP BY table_name
    ) c USING (table_name)
) 
WHERE lag > 10;
```

KPI 4 – Stale (> 24 hours without update)

```sql
SELECT COUNT(- 👉 ) 
FROM pipeline_state.cdf_progress
WHERE updated_at < NOW() - INTERVAL 1 DAY;
```

---

### 🎨 DASHBOARD SETUP (recommended layouts)

Row 1 — KPIs

| Tile | Function |
|------|----------|
| Total tables | quick snapshot |
| Behind | # tables lagging |
| Critical | # tables seriously behind |
| Stale | not updated in 24 hours |

Row 2 — Main Table

- 👉  Use the Master Monitoring Query
- 👉  Set conditional formatting for status field

Row 3 — Visuals

- 👉  Line chart: lag over time
- 👉  Heat map: ingestion activity
- 👉  Alert table: tables behind > 10 versions

---

### 🚀 Optional: I can also generate

- ✔  Alerts using Databricks Jobs
- ✔  Email notifications from lag > threshold
- ✔  A CLI tool to check ingestion health
- ✔  A dashboard for downstream tables consistency
- ✔  A custom DLT expectation that raises alerts

