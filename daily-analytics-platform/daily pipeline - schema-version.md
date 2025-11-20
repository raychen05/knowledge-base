## TableReader - Delta Table Schema and Version Management


### ✅ Your Requirements (Simplified)

1. You always need to read two schemas in the same job:
   -  One schema depends on col (wos, pprn) → gold_wos_- or gold_pprn_*
   -  One schema is always gold_entity_*
2. Tables under gold_wos and gold_pprn have same table names
3. Tables under gold_entity have different table names
4. You want a simple API to read:
   -  the column-group schema (wos / pprn)
   -  the entity schema
   -  ideally only passing the table name + type ("entity" or "group")


---

### 🎯 Best Overall Solution: Unified TableReader with Two Schema Roots


We build a TableReader that automatically constructs:
   - catalog → ag_ra_search_analytics_data_${env}
   - group schema → gold_${col}_${ver}
   - entity schema → gold_entity_${ver}
You can read from either with a simple function call.


---

### ✅ Final Clean API

**Usage**:

```scala
val dfWosOrPprn = TableReader.group("customer")      // col decides wos or pprn
val dfEntity    = TableReader.entity("customer_dim") // entity schema
```

---

### ⭐ Implementation

```scala
object TableReader {

  private val env = dbutils.widgets.get("env")   // prod, dev, etc
  private val ver = dbutils.widgets.get("ver")   // v1, v2, etc
  private val col = dbutils.widgets.get("col")   // wos, pprn

  private val catalog = s"ag_ra_search_analytics_data_${env}"

  // schema that depends on col (wos / pprn)
  private def groupSchema = s"${catalog}.gold_${col}_${ver}"

  // schema that always uses entity
  private def entitySchema = s"${catalog}.gold_entity_${ver}"

  /*- Read from wos/pprn schema */
  def group(table: String): DataFrame = {
    val full = s"${groupSchema}.${table}"
    spark.read.table(full)
  }

  /*- Read from entity schema */
  def entity(table: String): DataFrame = {
    val full = s"${entitySchema}.${table}"
    spark.read.table(full)
  }
}

```

---

### 🌟 Why This Is the Best Pattern

✔ Matches real-world Lakehouse modeling
   - WOS/PPRN are vertical domain schemas
   - ENTITY is a common reference schema
  
✔ Cleanest API
    - Simple and expressive usage:
```scala
TableReader.group("transactions")
TableReader.entity("entities_dim")
```

✔ No need to pass env/ver/col everywhere
    - They are resolved once from the config.

✔ Extensible
    - You can add more schema families easily:
```scala
def bronze(table: String): DataFrame = ...
def silver(table: String): DataFrame = ...
```

✔ Consistent naming and avoids string mess
    - Modular schema functions ensure maintainability.


---


### ✨ Optional: Convenience Read That Auto-Decides Schema

If table name itself indicates group/entity:

```scala
def read(table: String): DataFrame = {
  if (table.startsWith("ent_"))
    entity(table)
  else
    group(table)
}
```

**Usage**:

```scala
TableReader.read("transactions")   // goes to gold_wos or gold_pprn
TableReader.read("ent_master")     // goes to gold_entity
```

Want me to add?

- ✅ writer functions (write, overwrite, upsert)
- ✅ dynamic table-to-schema mapping table
- ✅ unit tests for the TableReader


---


## TableWriter - Delta Table Schema and Version Management


Below is a clean, production-quality, fully scalable design for a TableWriter (plus companion helpers) that matches your real Lakehouse schema layout, minimizes parameters, and gives you a single simple call:

```scala
TableWriter.output("customers", df)     // writes to dap_entity_wos or dap_entity_pprn
TableWriter.entityEnrich("abc", df)     // writes to dap_entity_enrich
TableWriter.reference("countries", df)  // writes to dap_reference
```

All environment (env), version (ver), and model group (col = wos/pprn) logic is handled automatically.

---


### ✅ Your Schema Groups (Normalized)


#### (1) OUTPUT SCHEMAS (per pipeline)

Depend on col = wos or pprn

```text
dap_entity_wos
dap_metrics_wos

dap_entity_pprn
dap_metrics_pprn
```
Output schemas that do NOT depend on col:

```text
dap_grant
dap_docs
dap_prod_core
dap_entity_enrich
```

#### (2) INPUT SCHEMAS (reference + dimension)

Always static:
```text
dap_reference
dap_sort_ref
```

#### (3) OPERATIONAL SCHEMAS

```text
dap_ops
dap_work
```

---

### 🎯 Goal

Create:
```scala
TableWriter.output(table, df)
TableWriter.grant(table, df)
TableWriter.docs(table, df)
TableWriter.ops(table, df)
TableWriter.reference(table, df)
```

Only passing:
  - table name
  - dataframe

No need to pass col/env/version.

---

### ⭐ Final Best Design: SchemaRouter + TableWriter

#### 1. SchemaRouter → resolves full UC schema automatically

```scala
object SchemaRouter {

  private val env = dbutils.widgets.get("env")   // prod, dev, etc
  private val ver = dbutils.widgets.get("ver")   // v1, v2
  private val col = dbutils.widgets.get("col")   // wos or pprn

  private val catalog = s"ag_ra_search_analytics_data_${env}"

  // ---- OUTPUT SCHEMAS ----
  def entityOutput = s"${catalog}.dap_entity_${col}"
  def metricsOutput = s"${catalog}.dap_metrics_${col}"

  def grant = s"${catalog}.dap_grant"
  def docs = s"${catalog}.dap_docs"
  def prodCore = s"${catalog}.dap_prod_core"
  def entityEnrich = s"${catalog}.dap_entity_enrich"

  // ---- INPUT SCHEMAS ----
  def reference = s"${catalog}.dap_reference"
  def sortRef = s"${catalog}.dap_sort_ref"

  // ---- OPERATIONAL ----
  def ops = s"${catalog}.dap_ops"
  def work = s"${catalog}.dap_work"
}
```

---

#### 2. TableWriter → Unified, simple write functions

```scala
object TableWriter {

  private def writeFull(full: String, df: DataFrame): Unit = {
    df.write
      .format("delta")
      .mode("overwrite")  // or pass a mode if needed
      .saveAsTable(full)
  }

  // -------- OUTPUT --------
  def output(table: String, df: DataFrame): Unit =
    writeFull(s"${SchemaRouter.entityOutput}.${table}", df)

  def metrics(table: String, df: DataFrame): Unit =
    writeFull(s"${SchemaRouter.metricsOutput}.${table}", df)

  def grant(table: String, df: DataFrame): Unit =
    writeFull(s"${SchemaRouter.grant}.${table}", df)

  def docs(table: String, df: DataFrame): Unit =
    writeFull(s"${SchemaRouter.docs}.${table}", df)

  def prodCore(table: String, df: DataFrame): Unit =
    writeFull(s"${SchemaRouter.prodCore}.${table}", df)

  def entityEnrich(table: String, df: DataFrame): Unit =
    writeFull(s"${SchemaRouter.entityEnrich}.${table}", df)

  // -------- INPUT --------
  def reference(table: String, df: DataFrame): Unit =
    writeFull(s"${SchemaRouter.reference}.${table}", df)

  def sortRef(table: String, df: DataFrame): Unit =
    writeFull(s"${SchemaRouter.sortRef}.${table}", df)

  // -------- OPERATIONS --------
  def ops(table: String, df: DataFrame): Unit =
    writeFull(s"${SchemaRouter.ops}.${table}", df)

  def work(table: String, df: DataFrame): Unit =
    writeFull(s"${SchemaRouter.work}.${table}", df)
}
```

---


###  🎉 Usage Examples — Super Simple

✔ Write to dap_entity_wos or dap_entity_pprn (based on col)
```scala
TableWriter.output("customer", df)
```

✔ Write to metrics schema
```scala
TableWriter.metrics("daily_stats", df)
```

✔ Write to entity enrich
```scala
TableWriter.entityEnrich("enriched_customers", df)
```

✔ Write to reference tables
```scala
TableWriter.reference("country_mapping", df)
```

✔ Write to operational areas
```scala
TableWriter.ops("job_status", df)
TableWriter.work("temp_stage_data", df)
```

---


### 🌟 Benefits of This Design

✔ Cleanest API
  - You never pass env, col, version, or full schema paths.

✔ Supports your real pipeline structure
  - dual schema output (wos/pprn & entity)
  - unified reference + ops schemas
  - special-purpose schemas (grant, docs, enrich, prod_core)

✔ DRY and maintainable
    - Modify schema rules in one place (SchemaRouter).

✔ Encourages standard naming and governance
    - All writes flow through this controlled gateway.

Want me to generate the TableReader to match this EXACT schema system as well?
I can produce a fully symmetric design:
```scala
TableReader.output("customer")
TableReader.entityEnrich("abc")
TableReader.reference("country")
```

---


## DataFrame  Extension



Yes — you can add an extension method to DataFrame in Scala so you can call something like df.write_dap(...). The normal way is to provide an implicit class that adds a write_dap method which internally calls the standard DataFrameWriter / Delta API (e.g. .format("delta").saveAsTable(...) or a Delta merge for upserts).
Below are several practical variants you can copy into your codebase.


### 1) Simple extension: write to a catalog.schema.table (create/save)

This version writes the DataFrame as a Delta table using saveAsTable and supports mode, partitioning and extra options.

```scala
import org.apache.spark.sql.{DataFrame, SaveMode}
import scala.collection.JavaConverters._

object DataFrameExtensions {
  implicit class RichDataFrame(val df: DataFrame) extends AnyVal {

    /*- 
     - Write DataFrame as a Delta table to a catalog.schema.table
     - Examples:
     -   df.write_dap("my_catalog", "schema", "table")
     -   df.write_dap("my_catalog.schema.table", mode = SaveMode.Overwrite)
     */
    def write_dap(catalog: String,
                  schema: String,
                  table: String,
                  mode: SaveMode = SaveMode.ErrorIfExists,
                  partitionCols: Seq[String] = Seq.empty,
                  options: Map[String, String] = Map.empty): Unit = {

      val fullName = s"$catalog.$schema.$table"
      val writer = df.write
        .format("delta")
        .mode(mode)
        .options(options)

      if (partitionCols.nonEmpty) writer.partitionBy(partitionCols: _*).saveAsTable(fullName)
      else writer.saveAsTable(fullName)
    }

    // Overload to accept full dotted table name in one string
    def write_dap(fullTableName: String,
                  mode: SaveMode = SaveMode.ErrorIfExists,
                  partitionCols: Seq[String] = Seq.empty,
                  options: Map[String, String] = Map.empty): Unit = {

      val writer = df.write
        .format("delta")
        .mode(mode)
        .options(options)

      if (partitionCols.nonEmpty) writer.partitionBy(partitionCols: _*).saveAsTable(fullTableName)
      else writer.saveAsTable(fullTableName)
    }
  }
}
```

**Usage**:

```scala
import DataFrameExtensions._
df.write_dap("my_catalog", "sales", "orders", SaveMode.Overwrite, Seq("country"), Map("path" -> "/mnt/delta/sales/orders"))
// or
df.write_dap("my_catalog.sales.orders", SaveMode.Append)
```

---

### 2) Upsert / Merge variant (merge into existing Delta table)

If you need idempotent writes (upsert), use io.delta.tables.DeltaTable to perform merge. This example assumes the target table already exists.

```scala
import org.apache.spark.sql.{DataFrame, SaveMode}
import io.delta.tables._
import org.apache.spark.sql.functions._
import scala.collection.JavaConverters._

object DataFrameExtensions {
  implicit class RichDataFrame(val df: DataFrame) extends AnyVal {

    /*- Upsert (merge) df into an existing Delta table using join keys */
    def write_dap_upsert(fullTableName: String,
                         keyCols: Seq[String],
                         options: Map[String, String] = Map.empty): Unit = {

      // Build merge condition: target.key1 = source.key1 AND ...
      val cond = keyCols.map(k => s"target.$k = source.$k").mkString(" AND ")

      val spark = df.sparkSession
      val targetExists = try {
        DeltaTable.isDeltaTable(spark, spark.catalog.getTable(fullTableName).location) // not always ideal
      } catch {
        case _: Throwable => false
      }

      // Simpler approach: reference by name (works if catalog resolves)
      val deltaTable = DeltaTable.forName(spark, fullTableName)

      deltaTable.as("target")
        .merge(
          df.as("source"),
          expr(cond)
        )
        .whenMatched()
        .updateAll()
        .whenNotMatched()
        .insertAll()
        .execute()
    }
  }
}
```

**Usage**:

```scala
import DataFrameExtensions._
df.write_dap_upsert("my_catalog.sales.orders", Seq("order_id"))
```

Notes: DeltaTable.forName requires the table to be registered in the metastore/catalog. If the table path is used instead, use DeltaTable.forPath(spark, "/mnt/..").

---

### 3) More advanced: configurable registry, create-if-not-exists, and atomic swap


You can combine the simple writer and merge logic to:
- create table if not exists (df.write.format("delta").saveAsTable(...) with mode=SaveMode.Overwrite but careful with schema),
- perform schema merge: set spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", "true") (or the Delta equivalent),
- write to staging path then CREATE OR REPLACE TABLE ... USING DELTA LOCATION, or use MERGE for upserts.

**Important practical notes / gotchas**

1. Catalog config — saveAsTable("catalog.schema.table") will only work if that catalog is configured in Spark (e.g. Unity Catalog or an external Hive metastore). Make sure spark.sql.catalog.my_catalog is set and the user has permission to create/alter the table.
2. Delta dependency — add the Delta Lake dependency (e.g., io.delta:delta-core_2.12:...) and imports io.delta.tables._ for merge operations.
3. Schema evolution — to allow automatic schema evolution during writes, configure:
```scala
spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", "true")
```
and use .option("mergeSchema", "true") when writing.

4. Transactions & concurrent writes — Delta provides ACID guarantees, but be careful about concurrent saveAsTable + merge patterns and use merge for upserts.
5. Method naming — Scala style often uses writeDap, but you can name the method write_dap (Scala allows underscores). Make sure colleagues are aware of the API style.
6. Testing — unit-test your extension in a local test Spark session and test both creation and overwrite/append/upsert paths.

If you want, I can:
- give a complete single-file example (including SBT dependency snippet for Delta),
- add an overload that accepts a Map[String,String] of metadata (catalog/hive props),
- or provide a write_dap that automatically chooses between saveAsTable and merge (create-if-not-exists then upsert) — I can include one of these full implementations right away. Which of those would you like me to include now?



----
 

## DataFrame Extension - v2



Below is the cleanest and most idiomatic Scala approach to make your DataFrame writable like:
```scala
df.output("customers")
df.metrics("daily_stats")
df.docs("raw_doc")
df.entityEnrich("customer_enriched")
df.ops("job_run")
```

This is done by adding extension methods to DataFrame via implicit class.


### ✅ 1. Reuse your existing SchemaRouter + TableWriter

We keep your SchemaRouter as-is and reuse the core write logic:

```scala
private def writeFull(full: String, df: DataFrame): Unit = {
  df.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable(full)
}
```

---

### ⭐ 2. Add DataFrame extension methods (implicit class)

This allows you to call:
```scala
df.metrics("table")
```
just like a native Spark method.

```scala
import org.apache.spark.sql.DataFrame

object DataFrameWriters {

  implicit class DataFrameWriterOps(df: DataFrame) {

    // ---- OUTPUT ----
    def output(table: String): Unit =
      df.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable(s"${SchemaRouter.entityOutput}.${table}")

    def metrics(table: String): Unit =
      df.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable(s"${SchemaRouter.metricsOutput}.${table}")

    def docs(table: String): Unit =
      df.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable(s"${SchemaRouter.docs}.${table}")

    def grant(table: String): Unit =
      df.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable(s"${SchemaRouter.grant}.${table}")

    def entityEnrich(table: String): Unit =
      df.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable(s"${SchemaRouter.entityEnrich}.${table}")


    // ---- INPUT / REF ----
    def reference(table: String): Unit =
      df.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable(s"${SchemaRouter.reference}.${table}")

    def sortRef(table: String): Unit =
      df.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable(s"${SchemaRouter.sortRef}.${table}")


    // ---- OPERATIONS ----
    def ops(table: String): Unit =
      df.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable(s"${SchemaRouter.ops}.${table}")

    def work(table: String): Unit =
      df.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable(s"${SchemaRouter.work}.${table}")
  }
}
```

---

### 🎉 3. Usage — as simple as calling a DataFrame method


```scala
//Import it:

import DataFrameWriters._
//Then:

df.output("customers")
df.metrics("daily_stats")
df.docs("document_payload")
df.entityEnrich("entity_enriched")
df.reference("country_mapping")
df.ops("job_status")
df.work("temp_stage")
```

No need to reference schemas anywhere in your code.
Everything is handled by SchemaRouter.

---

### ⭐ Why This Approach Is Ideal

✔ Feels natural and readable
- df.metrics("table") is extremely expressive.

✔ Avoids code repetition
- No more boilerplate:
- df.write.format("delta").mode("overwrite")...

✔ Central governance
- All schema routing remains in one place (SchemaRouter).
  
✔ Fully extensible
- Want df.bronze("t")? Add another method.

---

### 🔧 Optional Enhancements (I can add if needed)

- Support mode = append / overwrite
- Unified writer method: df.writeTo("schemaGroup", "table")
- Writing options (ZORDER, optimize, checkpointing)
- Adding logging & metrics
- Async writes / retries


---


## Unified, Extensible I/O Framework 



Below is a production-grade, unified, extensible I/O framework that cleanly combines:
- ✅ TableReader
- ✅ TableWriter
- ✅ DataFrame extension write methods
- ✅ Flexible write modes (overwrite/append)
- ✅ Schema routing
- ✅ Optional enhancements (logging, ZORDER, optimize, mode override)
  
All in a single, compact, maintainable design.
This is the kind of framework used in well-structured Databricks Lakehouse platforms.

---

### 🔥 Final Unified Framework: **LakeIO**

You will get:
```scala
val df = LakeIO.read.output("transactions")
df.output("customers")
df.metrics("daily_stats")
```
Everything centralized.

---

### 1️⃣ SchemaRouter — All schema routing rules in ONE place

```scala
object SchemaRouter {

  private val env = dbutils.widgets.get("env")   // dev/prod/nonprod
  private val ver = dbutils.widgets.get("ver")   // v1/v2
  private val col = dbutils.widgets.get("col")   // wos/pprn

  private val catalog = s"ag_ra_search_analytics_data_${env}"

  // ---- OUTPUT SCHEMAS (depend on col) ----
  def entityOutput  = s"${catalog}.dap_entity_${col}"
  def metricsOutput = s"${catalog}.dap_metrics_${col}"

  // ---- OTHER OUTPUT SCHEMAS ----
  def grant        = s"${catalog}.dap_grant"
  def docs         = s"${catalog}.dap_docs"
  def prodCore     = s"${catalog}.dap_prod_core"
  def entityEnrich = s"${catalog}.dap_entity_enrich"

  // ---- INPUT / REF ----
  def reference = s"${catalog}.dap_reference"
  def sortRef   = s"${catalog}.dap_sort_ref"

  // ---- OPERATIONS ----
  def ops  = s"${catalog}.dap_ops"
  def work = s"${catalog}.dap_work"
}
```


---

### 2️⃣ Base Write Utility (mode + ZORDER + logging)

```scala
object WriterUtils {

  def write(
      df: DataFrame,
      fullName: String,
      mode: String = "overwrite",
      zorderBy: Seq[String] = Seq.empty,
      optimizeAfter: Boolean = false
  ): Unit = {

    println(s"[LakeIO] Writing to table: $fullName (mode = $mode)")

    df.write
      .format("delta")
      .mode(mode)
      .saveAsTable(fullName)

    // OPTIONAL: Auto ZORDER + OPTIMIZE
    if (zorderBy.nonEmpty) {
      println(s"[LakeIO] OPTIMIZE + ZORDER BY: ${zorderBy.mkString(",")}")
      spark.sql(s"OPTIMIZE $fullName ZORDER BY (${zorderBy.mkString(",")})")
    }
    else if (optimizeAfter) {
      println(s"[LakeIO] OPTIMIZE (no ZORDER)")
      spark.sql(s"OPTIMIZE $fullName")
    }
  }
}
```

---

### 3️⃣ Unified TableWriter (API)

```scala
object TableWriter {

  import WriterUtils._

  // ------------ OUTPUT ---------------

  def output(table: String, df: DataFrame, mode: String = "overwrite") =
    write(df, s"${SchemaRouter.entityOutput}.${table}", mode)

  def metrics(table: String, df: DataFrame, mode: String = "overwrite") =
    write(df, s"${SchemaRouter.metricsOutput}.${table}", mode)

  def docs(table: String, df: DataFrame, mode: String = "overwrite") =
    write(df, s"${SchemaRouter.docs}.${table}", mode)

  def grant(table: String, df: DataFrame, mode: String = "overwrite") =
    write(df, s"${SchemaRouter.grant}.${table}", mode)

  def prodCore(table: String, df: DataFrame, mode: String = "overwrite") =
    write(df, s"${SchemaRouter.prodCore}.${table}", mode)

  def entityEnrich(table: String, df: DataFrame, mode: String = "overwrite") =
    write(df, s"${SchemaRouter.entityEnrich}.${table}", mode)


  // ------------ INPUT / REF ----------

  def reference(table: String, df: DataFrame, mode: String = "overwrite") =
    write(df, s"${SchemaRouter.reference}.${table}", mode)

  def sortRef(table: String, df: DataFrame, mode: String = "overwrite") =
    write(df, s"${SchemaRouter.sortRef}.${table}", mode)


  // ------------ OPERATIONS -----------

  def ops(table: String, df: DataFrame, mode: String = "overwrite") =
    write(df, s"${SchemaRouter.ops}.${table}", mode)

  def work(table: String, df: DataFrame, mode: String = "overwrite") =
    write(df, s"${SchemaRouter.work}.${table}", mode)
}
```

---

### 4️⃣ Unified TableReader

```scala
object TableReader {

  def read(schema: String, table: String): DataFrame =
    spark.read.table(s"$schema.$table")

  // High-level helpers:
  def output(table: String): DataFrame =
    read(SchemaRouter.entityOutput, table)

  def metrics(table: String): DataFrame =
    read(SchemaRouter.metricsOutput, table)

  def docs(table: String): DataFrame =
    read(SchemaRouter.docs, table)

  def reference(table: String): DataFrame =
    read(SchemaRouter.reference, table)

  def entityEnrich(table: String): DataFrame =
    read(SchemaRouter.entityEnrich, table)

  def ops(table: String): DataFrame =
    read(SchemaRouter.ops, table)

  def work(table: String): DataFrame =
    read(SchemaRouter.work, table)
}
```

---

### 5️⃣ Extension Methods: DataFrame.write API

```scala
object DataFrameExtensions {

  import TableWriter._

  implicit class LakeDataFrameWriter(df: DataFrame) {

    def output(table: String, mode: String = "overwrite"): Unit =
      TableWriter.output(table, df, mode)

    def metrics(table: String, mode: String = "overwrite"): Unit =
      TableWriter.metrics(table, df, mode)

    def docs(table: String, mode: String = "overwrite"): Unit =
      TableWriter.docs(table, df, mode)

    def grant(table: String, mode: String = "overwrite"): Unit =
      TableWriter.grant(table, df, mode)

    def entityEnrich(table: String, mode: String = "overwrite"): Unit =
      TableWriter.entityEnrich(table, df, mode)

    def reference(table: String, mode: String = "overwrite"): Unit =
      TableWriter.reference(table, df, mode)

    def sortRef(table: String, mode: String = "overwrite"): Unit =
      TableWriter.sortRef(table, df, mode)

    def ops(table: String, mode: String = "overwrite"): Unit =
      TableWriter.ops(table, df, mode)

    def work(table: String, mode: String = "overwrite"): Unit =
      TableWriter.work(table, df, mode)
  }
}
```


---

### 6️⃣ Unified Facade Object: LakeIO

This gives you a single entry point:

```scala
object LakeIO {
  val read = TableReader
  val write = TableWriter
}
```

---

### 🎉 7️⃣ Usage — beautiful, clean, simple

```scala
import DataFrameExtensions._

// Read from entity output
val df = LakeIO.read.output("transactions")

// Write to output schema
df.output("transactions_clean")

// Write to metrics
df.metrics("daily_metrics")

// Write to docs schema
df.docs("docs_payload")

// Write to operations schema
df.ops("job_status")

// Write as append
df.output("incremental_data", mode = "append")
```

---


### 🌟 Advantages of This Framework

- ✔ 100% consistent read/write patterns
- ✔ Only one place controls schema routing
- ✔ Cleanest possible API for pipelines
- ✔ Flexible write modes + optional OPTIMIZE/ZORDER
- ✔ Easy to unit test
- ✔ Easy to extend for new schemas (bronze/silver/gold, raw/curated, etc.)
- ✔ Works with Unity Catalog seamlessly

---

🚀 Want advanced features?

I can add:
- automatic incremental merge (MERGE INTO)
- SCD2 writer
- CDC ingestion pattern
- Auto-logging lineage to a log table
- Automatic table existence + schema validation
- Retry wrapper for operational tables
- Deleting partitions
- Iceberg support











