## Naming a catalog or schema 


When naming catalogs or schemas for analytics, focus on:

- **Descriptiveness:** Clearly indicate purpose and contents.
- **Organization:** Group related datasets logically.
- **Scalability:** Use names that support future growth.
- **Consistency:** Apply a standard naming convention.


✅ Recommendation: Use Singular Table Names

Use singular table names consistently to represent each entity, and treat each table as a definition or model of that entity.

Why singular is generally better:

| Reason                                   | Explanation                                                                                                         |
|-------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| 🧱 Represents an entity                   | Singular names reflect that a table models a single type of entity (e.g., `author_profile`), similar to a class.    |
| 📐 Works well with ORM & semantic layers  | Most modeling tools (dbt, SQLAlchemy) expect singular names for entities, improving compatibility and documentation. |
| 🔄 Cleaner joins and column naming        | Singular names make joins and references clearer: `author.id = article.author_id` is more readable than plurals.    |
| 🧠 Semantically intuitive                 | "SELECT * FROM author_profile" reads as retrieving entity data, not just a collection of items.                      |


📍 Examples (Singular):

| Table Purpose                        | Table Name              |
|--------------------------------------|-------------------------|
| Author entity                        | `author_profile`        |
| Article-level metrics for author     | `author_article_metrics`|
| Organization data                    | `organization`          |
| Funding agency                       | `funding_agency`        |
| Article metadata                     | `article_meta`          |
| Research category                    | `category`              |


👎 Why Plural is less preferred (but still used in some teams):

- Plural names like authors or articles emphasize the collection rather than the entity.
- Can lead to awkward or inconsistent plural forms (categories, data, statuses, etc.).
- Doesn't align as cleanly with programming patterns or tools.




---

### 1. ✅ Recommended Schema Name: Product-Ready Data

`research_analytics`

A broad, scalable name that distinguishes analytics-ready research data from operational or raw schemas.

**Example Schema Structure:**

| Schema                      | Tables                                                        |
|-----------------------------|---------------------------------------------------------------|
| research_analytics.core     | incites_data, author_profile, grants_data, patents_data, incites_dict |
| research_analytics.pprn     | pprn_incites, pprn_author_profile, pprn_grants, pprn_patents, pprn_incites_dict |
| research_analytics.ri       | ri_grants, ri_incites                                         |
| research_analytics.impact   | societal_impact                                               |
| research_analytics.fronts   | researchfronts_data, rf_dict                                  |

**Why `research_analytics` Works:**

- Accommodates current and future analytics data.
- Separates analytics-ready data from raw or operational sources.
- Supports a semantic layer for easy navigation.

Use consistent table prefixes (e.g., pprn_, ri_) for further namespace separation.

---

### 2. Recommended Schema Name: Integration-Ready Data

`research_entity_store`

Represents a curated layer of structured entities (authors, orgs, departments, journals, etc.) for assembling final datasets. Not raw, but not fully aggregated — suitable for integration or dimensional modeling.

**Why This Name Works:**

- `research_`: Scope for research-related data.
- `entity_`: Contains normalized, reusable entities.
- `store`: Indicates a persistent, curated layer.

This approach allows:

- Normalized data structures (author_profile, organization, etc.)
- Incremental updates (e.g., daily)
- Use as building blocks for downstream analytics and metrics

**Alternative Name Options:**

| Name              | Use Case                                                                 |
|-------------------|--------------------------------------------------------------------------|
| research_dim      | For dimensional modeling (dimension and fact tables)                     |
| research_model    | Core data model for analytics and metrics                                |
| research_entities | Focuses on entities                                                      |
| analytics_base    | Base layer for analytics views and aggregations                          |
| semantic_layer    | Curated, structured datasets for consumption                             |
| curated_entities  | Cleaned and ready for further use                                        |

**Example Table Layout:**

```sql
research_entity_store.author_profile
research_entity_store.organization
research_entity_store.department
research_entity_store.funding_agency
research_entity_store.journal
research_entity_store.category
research_entity_store.article_metrics
research_entity_store.trend_metrics_5y
research_entity_store.category_metrics
research_entity_store.global_baseline_metrics
```

This layer supports clean joins, fast metric aggregation, and reduces duplication across datasets.

---

### 3. ✅ Recommended Table Name: Meta & Metrics Data

`author_article_metrics`

For article-level metadata and metrics linked to the author_profile entity (e.g., author roles, citation types, identifiers).


**Why This Name Works:**


| Term    | Reason                                                                                       |
|---------|----------------------------------------------------------------------------------------------|
| author  | Focuses on the `author_profile` entity.                                                      |
| article | Data is organized at the article level.                                                      |
| metrics | Represents metrics and metadata for each article in relation to the author.                  |


This name is concise, consistent, and scalable for similar tables (e.g., org-level article metrics).

- Clear and scalable
- Works well with your existing catalog naming
- Easy to document and understand for analysts or engineers



**Alternative Table Name Options:**


| Table Name                   | When to Use                                                                 |
|------------------------------|-----------------------------------------------------------------------------|
| author_profile_article_metrics| To fully qualify the author from the author_profile entity (more verbose).  |
| article_metrics_by_author    | To emphasize aggregation direction.                                         |
| author_article_facts         | For data warehouse star schema style (facts hold metrics).                  |
| author_article_roles_metrics | To highlight tracking of author roles (first, last, reprint, etc.).         |


---

### 4. ✅ Recommended Table Name - Metric Data calculated across the  dataset


`article_normalized_metrics`


The context — you're describing a fact-style table that stores article-level metric scores, calculated across the entire dataset, segmented by:
- Time (per year)
- Category (e.g., research area)
- Article type
- And mapped to each article

Metrics include: percentile, nci, collab_nci, expected_rate, word_ratio, etc.


**🔹 Why this name works**

| Part               | Meaning                                                                                                 |
|--------------------|---------------------------------------------------------------------------------------------------------|
| article            | Indicates that each row corresponds to a specific article, segmented by year, category, and type.       |
| normalized_metrics | Specifies that the metrics are calculated or derived from global baselines, such as percentiles and NCI. |


This name is clear, scalable, and semantically correct — it's not just "raw" article metrics, but derived/normalized ones.

- Fits well under your research_entity_store schema
- Reflects that metrics are normalized/evaluated, not raw counts
- Leaves room for other article metric tables (like raw counts, source-based metrics, etc.)


**🔄 Alternative Naming Options (if you want variations):**


| Table Name                | When to Use                                                                                  |
|---------------------------|---------------------------------------------------------------------------------------------|
| article_metric_dta        | Use when focusing on the output of metric calculations (data); generic and straightforward |
| article_impact_metrics    | Use if most metrics relate to citation or impact (e.g., NCI, percentile)                    |
| article_level_metrics     | Use to emphasize article-level granularity; may be too broad if multiple article-level tables|
| article_category_metrics  | Use to highlight per-category segmentation                                                   |
| article_evaluated_metrics | Use to indicate metrics are derived via evaluation logic, not raw values                    |


---

### 5. ✅  Scheam &  Table Name - Product-ready Data


| Schema                      | Delta Table Name         | Index Name           | Incites only | WOSRI Only | Description      |
|-----------------------------|-------------------------|----------------------|--------------|------------|------------------|
| research_analytics.core     | incites_data            | incites              |              |            |                  |
|                             | author_profile          | authorprofile        |              |            |                  |
|                             | grants_data             | grants               |              |            |                  |
|                             | patents_data            | patents              |              |            |                  |
|                             | incites_dict            | incites-dict         |              |            |                  |
| research_analytics.pprn     | pprn_incites            | pprn-incites         |              |            |                  |
|                             | pprn_author_profile     | pprn-authorprofile   |              |            |                  |
|                             | pprn_grants             | pprn-grants          |              |            |                  |
|                             | pprn_patents            | pprn-patents         |              |            |                  |
|                             | pprn_incites_dict       | pprn-incites-dict    |              |            |                  |
| research_analytics.ri       | ri_grants               | ri-grants            |              | ✓          |                  |
|                             | ri_incites              | ri-incites           |              | ✓          |                  |
|                             | societal_impact         | societal-impact      |              | ✓          |                  |
|                             | researchfronts_data     | researchfronts       |              |            | Out of scope     |
|                             | rf_dict                 | rf-dict              |              |            | Out of scope     |
|                             | custom_data             | custom               | ✓            |            | Out of scope     |
|                             | people_data             | people               | ✓            |            | Out of scope     |
|                             | myorg_data              | myorg                | ✓            |            | Out of scope     |
|                             | pprn_people             | pprn-people          | ✓            |            | Out of scope     |
|                             | pprn_myorg              | pprn-myorg           | ✓            |            | Out of scope     |


---


### 6. ✅  Scheam &  Table Name - Integration-ready Data



| Schema                              | Delta Table Name                | Description                                   |
|--------------------------------------|---------------------------------|-----------------------------------------------|
| research_entity_store.entity_wos     | author_profile                  | Author entity (Web of Science)                |
| research_entity_store.entity_wos     | author_article_metrics          | Article-level metrics for authors (WOS)       |
| research_entity_store.entity_wos     | organization                    | Organization entity (WOS)                     |
| research_entity_store.entity_wos     | organization_article_metrics    | Article-level metrics for organizations (WOS) |
| research_entity_store.entity_wos     | department                      | Department entity (WOS)                       |
| research_entity_store.entity_wos     | department_article_metrics      | Article-level metrics for departments (WOS)   |
| research_entity_store.entity_wos     | region                          | Region entity (WOS)                           |
| research_entity_store.entity_wos     | region_article_metrics          | Article-level metrics for regions (WOS)       |
| research_entity_store.entity_wos     | funding_agency                  | Funding agency entity (WOS)                   |
| research_entity_store.entity_wos     | funding_agency_article_metrics  | Article-level metrics for funding agencies    |
| research_entity_store.entity_wos     | category                        | Research category entity (WOS)                |
| research_entity_store.entity_wos     | category_article_metrics        | Article-level metrics for categories (WOS)    |
| research_entity_store.entity_wos     | journal                         | Journal entity (WOS)                          |
| research_entity_store.entity_wos     | jcr_metrics                     | Journal Citation Reports metrics (WOS)        |
| research_entity_store.metrics_wos    | article_metrics                 | Article-level metrics (WOS)                   |
| research_entity_store.metrics_wos    | trend_metrics_5y                | 5-year trend metrics (WOS)                    |
| research_entity_store.metrics_wos    | category_metrics                | Category-level metrics (WOS)                  |
| research_entity_store.metrics_wos    | article_normalized_metrics      | Normalized article metrics (WOS)              |
| research_entity_store.entity_pprn    | author_profile                  | Author entity (PPRN)                          |
| research_entity_store.metrics_pprn   | article_metrics                 | Article-level metrics (PPRN)                  |

