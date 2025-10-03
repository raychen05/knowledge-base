## Top 20 Prompts for Refactoring Spark Scala Big Data Code

These prompts are designed to help you clean up, optimize, and modularize Spark-Scala data processing pipelines. They focus on performance, maintainability, and best practices in big data workflows.

---

### 🔧 1–10: Core Refactoring Prompts



| **#** | **Prompt**                                                                | **Purpose**                                               |
|-------|--------------------------------------------------------------------------|-----------------------------------------------------------|
| 1     |   Refactor this Spark job to use DataFrame API instead of RDD            | Upgrade legacy RDD code to modern, optimized DataFrame    |
| 2     |   Break this monolithic job into modular transformation steps           | Improves readability and testability                      |
| 3     |   Extract this transformation into a reusable function                  | Promotes reuse and separation of concerns                 |
| 4     |   Simplify this nested transformation using method chaining              | Improves fluency and avoids deeply nested blocks          |
| 5     |   Refactor to use typed Dataset instead of untyped DataFrame             | Adds compile-time safety and better IDE support           |
| 6     |   Move configuration values to external config file or case class       | Decouples logic from config; easier for deployment        |
| 7     |   Add logging for each stage in this ETL pipeline                        | Helps track lineage and debug failures                    |
| 8     |   Add Spark metrics and accumulator tracking for diagnostics            | Improves observability of job internals                   |
| 9     |   Replace UDF with built-in Spark SQL function where possible            | Optimizes performance and avoids serialization costs      |
| 10    |   Add error handling and fallback logic for empty or corrupt inputs     | Makes pipeline more robust to edge cases                  |


### ⚙️ 11–20: Advanced Refactoring & Optimization Prompts



| **#** | **Prompt**                                                                | **Purpose**                                                            |
|-------|--------------------------------------------------------------------------|------------------------------------------------------------------------|
| 11    |   Optimize this wide transformation to reduce shuffle operations        | Performance tuning by avoiding unnecessary data movement               |
| 12    |   Cache intermediate DataFrame to avoid recomputation                    | Improves job performance if reused later                              |
| 13    |   Refactor to support both batch and streaming input sources (e.g., Delta Lake) | Makes pipeline flexible for near-real-time needs                       |
| 14    |   Modularize this job into extract, transform, load phases              | Applies clean ETL architecture                                        |
| 15    |   Use DataFrame.withColumn instead of map when modifying a single field | Efficient column-level transformation                                  |
| 16    |   Annotate this case class with schema metadata and field descriptions  | Improves documentation and downstream use                             |
| 17    |   Refactor this Spark SQL query into a DSL-based transformation pipeline | Converts raw SQL into type-safe API logic                              |
| 18    |   Replace static schema inference with a typed encoder case class       | Boosts performance and safety with Dataset encoders                    |
| 19    |   Replace collect() with take(n) or limit() to avoid driver OOM         | Avoids expensive driver-side memory use                               |
| 20    |   Split this large Spark application into smaller jobs for DAG clarity | Makes job dependencies and retries more manageable                    |


---


### Bonus Prompt Templates (Reusable Formats)


🧩 Modularization

- Extract this block into a named function: [yourFunctionName]

🔁 Rewrite for Performance

- Rewrite this loop-based logic using Spark transformations


📊 Add Observability

- Add logging and metrics to track row counts and transformation timing

🧼 Style and Best Practices

- Refactor this code to follow Scala style conventions and functional best practices


---

### 📌 Summary



| **Category**       | **Example Prompts**                                                   |
|--------------------|----------------------------------------------------------------------|
| 💡 **Core Cleanup** | Replace RDD with DataFrame, extract reusable functions               |
| 🛠️ **Optimization** | Avoid collect(), cache intermediate results                          |
| ⚙️ **Architecture** | Modularize into ETL phases, support streaming                        |
| 🧪 **Robustness**   | Add error handling, schema validation, logging                       |
| 🔬 **Observability**| Add metrics, counters, lineage tracking                              |
