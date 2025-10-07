
## 📄 Naming Convention Guide for Data Platform



### 🔖 Document Purpose

To ensure consistency, clarity, and scalability in naming data assets (schemas, tables, columns) across all data domains: InCites, PPRN, RI, Entity Store, and more.

---

### 🔧 1. Schema Naming Conventions


| Type                   | Pattern                              | Example(s)                                 | Description                                                        |
|------------------------|--------------------------------------|--------------------------------------------|--------------------------------------------------------------------|
| Core analytics data    | `research_analytics.core`            | `research_analytics.core`                  | Index-ready data used for analytics (e.g., InCites, grants)        |
| Project-specific data  | `research_analytics.<project>`       | `research_analytics.pprn`, `research_analytics.ri` | Schemas for specific projects such as PPRN, RI                     |
| Entity layer           | `research_entity_store.<domain>`     | `research_entity_store.entity_wos`, `research_entity_store.metrics_wos` | Stores normalized, reusable entities and metrics                   |
| Staging/raw            | `staging.<source>`                   | `staging.wos`                             | (Optional) Raw or ingested data prior to transformation            |


---

### 📁 2. Table Naming Conventions


**General Rules:**

- Use lowercase with underscores to separate words
- Use singular nouns (e.g., author_profile, not author_profiles)
- Prefix with subject or context only if needed for clarity (e.g., author_article_metrics)
- Avoid abbreviations unless standard (e.g., nci, uid)



**Patterns:**

| Pattern                      | Description                                 | Example(s)                                 |
|------------------------------|---------------------------------------------|--------------------------------------------|
| `<entity>`                   | Core entity table                           | `author_profile`, `organization`, `journal`|
| `<entity>_article_metrics`   | Metrics at the article level for the entity | `author_article_metrics`, `department_article_metrics` |
| `article_<type>_metrics`     | Article-level metrics by type               | `article_normalized_metrics`, `article_metrics` |
| `<entity>_metrics`           | Entity-level metrics                        | `trend_metrics_5y`, `category_metrics`     |
| `pprn_<entity>`              | PPRN project-specific entity                | `pprn_author_profile`, `pprn_grants`       |
| `ri_<entity>`                | RI-specific table                           | `ri_incites`, `ri_grants`                  |

---


### 📊 3. Column Naming Conventions

**General Rules:**

- Use snake_case
- Use clear, descriptive names
- Include units or time context if applicable (citation_count_5y, percentile_rank)
- Foreign keys should reference table (author_id, article_id)

**Common Column Examples:**

| Column Name        | Description                                 |
|--------------------|---------------------------------------------|
| uid                | Unique ID for an article                    |
| author_id          | Foreign key to author profile               |
| grant_number       | Original grant identifier                   |
| nci                | Normalized Citation Impact                  |
| percentile         | Article’s citation percentile               |
| publication_year   | Year of publication                         |
| category           | Subject area or research category           |
| organization_id    | Foreign key to organization                 |


---


✅ 4. Best Practices

- Be consistent – apply the same rules across teams and projects
- Avoid reserved keywords – especially in SQL engines
- Document exceptions – some legacy names may differ
- Version your logic in code, not names – avoid metrics_v2, instead track changes in version-controlled transformation logic
- Don’t encode logic into table names – e.g., avoid high_impact_articles_2022


---

### 🧰 5. Optional Extensions


| Asset Type         | Convention                                                      |
|--------------------|-----------------------------------------------------------------|
| Views              | Prefix with `vw_` (e.g., `vw_author_summary`)                   |
| Materialized Views | Prefix with `mv_` (e.g., `mv_author_metrics`)                   |
| Temporary Tables   | Prefix with `tmp_` (use only in processing layers, e.g., `tmp_stage_data`) |
| dbt Models         | Match table naming conventions exactly where possible            |
