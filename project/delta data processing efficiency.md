## Processing a Small Subset on Large Delta Tables 


This is a common scenario in incremental ETL pipelines on large Delta tables (80M+ rows) when processing a small subset of keys (~100K).


**Key principles:**
- Avoid scanning all 80M rows.
- Use Spark’s broadcast join and data skipping/Z-Ordering to reduce shuffle and I/O.

**Efficient strategy:**

---

**Scenario**

- Main Delta table: `fact_table` (~80M rows)
- Incremental subset: `update_table` (~100K rows), e.g., changed entity keys
- Goal: Efficiently join/filter `fact_table` with `update_table` to process only relevant records

---

### Step 1: Cache and broadcast `update_table`

Since `update_table` is small (<100K rows), Spark can broadcast it to all worker nodes, preventing shuffling of the large `fact_table`.

```python
from pyspark.sql.functions import broadcast

update_df = spark.read.format("delta").load("/path/to/update_table")
update_df = update_df.cache()    # optional but helps if reused
```


---

### ✅ Step 2: Push filters down to Delta read

If fact_table is partitioned, always push filters on the partition column first to prune files before the join.

For example, if the table is partitioned by year or country:

```python
fact_df = (
    spark.read.format("delta")
    .load("/path/to/fact_table")
    .where("year >= 2020")   # partition pruning
)
```

---

### ✅ Step 3: Join using broadcast(update_df) on the key

Suppose the join key is id:

```python
joined_df = (
    fact_df.join(
        broadcast(update_df),  # 🚀 small table broadcasted
        on="id",
        how="inner"
    )
)
```

This ensures:
-	update_df is sent to each worker once.
-	No shuffle on the large fact_df.
-	Only relevant rows from fact_df are processed.

👉 With 100K keys, this is much faster than shuffling 80M rows.

---

### ✅ Step 4: Optional — Pre-filter fact_df using update_df keys

If the join key has good selectivity and is indexed / sorted, you can pre-filter using IN or semi join. Example:

```python
# Extract keys as a Python list (if very small) or keep as DF if ~100K
update_keys = update_df.select("id")

filtered_fact_df = fact_df.join(
    broadcast(update_keys),
    on="id",
    how="inner"
)
```


Or using a semi-join (less overhead):

```python
filtered_fact_df = fact_df.join(
    broadcast(update_df),
    on="id",
    how="left_semi"  # keeps only fact rows with matching keys
)
```

This is especially efficient if the id column is indexed through Z-ORDER or clustering (next step).

--

### ✅ Step 5: Z-ORDER the Delta table by join key (optional but powerful)

If this join happens frequently, Z-ORDERing your Delta table on the join key (id) will greatly improve data skipping, meaning Spark will read fewer data files for matching keys:

```sql
OPTIMIZE fact_table
ZORDER BY (id)
```

This clusters related rows together in fewer data files, so Spark can skip non-relevant files during the read.

💡 Best for repeated incremental jobs, not for one-time.


---


### ✅ Step 6: Tune Shuffle Partitions

Since your incremental set is small, avoid creating thousands of shuffle partitions unnecessarily:

```python
spark.conf.set("spark.sql.shuffle.partitions", "200")
```

You can adjust 200 to a lower number if the incremental workload is tiny. This prevents Spark from over-partitioning small outputs.

---

### ✅ Step 7: Optionally, Use Bloom Filters (Delta feature)

If you have a large Delta table and the join key is highly selective, you can create a Bloom filter index on the join key column. Spark will then skip files that definitely don’t contain relevant keys:


```sql
CREATE BLOOMFILTER INDEX bf_idx ON TABLE fact_table FOR COLUMNS(id) OPTIONS ('fpp' = '0.1', 'numItems'='100000000');
```
Then Spark will use this index during joins/filter to avoid reading unnecessary files.

---

📊 Summary Table

| Technique               | Purpose                           | Benefit                                 |
|-------------------------|-----------------------------------|-----------------------------------------|
| Broadcast join          | Avoid shuffling 80M rows          | Huge performance boost                  |
| Partition pruning       | Skip irrelevant partitions early  | Reduces I/O                             |
| Left semi-join or IN    | Narrow large dataset early        | Smaller data read                       |
| Z-ORDER on key          | Cluster data for skipping         | File-level skipping on repeated jobs    |
| Shuffle partitions tuning| Match parallelism to data size   | Avoid overhead                          |
| Bloom filter index      | File skipping for selective filters| Efficient for point lookups             |


---

### 🧪 Example end-to-end code

```python
from pyspark.sql.functions import broadcast

# Load incremental keys
update_df = spark.read.format("delta").load("/path/to/update_table").cache()

# Load large table with partition pruning
fact_df = (
    spark.read.format("delta")
    .load("/path/to/fact_table")
    .where("year >= 2020")
)

# Efficient join
result_df = fact_df.join(
    broadcast(update_df),
    on="id",
    how="inner"
)

# Process result
result_df.write.format("delta").mode("overwrite").save("/path/to/output")

```

⚡ Performance Tips

- 	Broadcast joins work best when the smaller table < ~100MB compressed.
- 	Use explain() to confirm Spark plans show BroadcastHashJoin.
- 	Use OPTIMIZE + ZORDER periodically, not in every run.
- 	Avoid collect() on 100K keys if it can fit as broadcast DF.


---


## Optimizations when working with large Delta Tables


Great question 👌 — this is one of the most important optimizations when working with large Delta tables.

Short answer:

- ❌ No, you don’t need to load all data from the Delta table to update a small subset.
- ✅ You should target and update only the impacted subset using MERGE, partition pruning, or semi-joins — without reading the entire table into a DataFrame first.
- 

Let’s break this down carefully 👇


---

### 🧠 Scenario

- 	Large Delta table: main_table (80+ million rows)
- 	Incremental dataset: updates_df (e.g., 100K rows to insert/update/delete)
- 	You want to update only those 100K impacted rows.

---

### ❌ Inefficient Pattern — Full Table Load + Update Subset

```python
# ❌ This loads ALL 80M rows into memory unnecessarily
main_df = spark.read.format("delta").load("/path/to/main_table")

# Then tries to update subset by join / filter
updated_df = (
    main_df.alias("m")
    .join(updates_df.alias("u"), "id", "left_outer")
    # ... update logic ...
)
```

🔸 Why this is bad:

- 	Full table scan every run → heavy I/O.
- 	Shuffles & joins on massive dataset even if only 0.1% of rows change.
- 	Memory pressure and slow jobs.

---

### ✅ Efficient Pattern — Use Delta MERGE INTO with Incremental DF

Delta Lake supports ACID upserts directly on the Delta table. You don’t need to load the main table into a DataFrame. Instead, push your incremental changes to Delta’s storage engine to do the update efficiently:

```python
from delta.tables import DeltaTable

# Load your incremental dataset
updates_df = spark.read.format("delta").load("/path/to/updates")

# Point to the existing Delta table (without reading it fully)
delta_table = DeltaTable.forPath(spark, "/path/to/main_table")

# Perform MERGE (UPSERT)
(
    delta_table.alias("t")
    .merge(
        updates_df.alias("s"),
        "t.id = s.id"   # join key
    )
    .whenMatchedUpdateAll()       # or .whenMatchedUpdate(...) for selective columns
    .whenNotMatchedInsertAll()    # handle new rows if needed
    .execute()
)
```

✅ What happens under the hood:

- 	Delta scans only files that contain matching keys (using partition pruning, Z-order, or bloom filters if present).
- 	It rewrites only affected data files.
- 	No need to materialize the full table as a Spark DataFrame.

⚡ This is the most scalable way to update a small subset in a large Delta table.


---


### ✅ Optional — Target Subset with Pre-Filter (for extra efficiency)

If your table is partitioned, add filters on partition columns to minimize file scanning:

```python
(
    delta_table.alias("t")
    .merge(
        updates_df.alias("s"),
        "t.id = s.id AND t.year = s.year"   # partition column helps pruning
    )
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll()
    .execute()
)
```

If you have Z-ORDER or bloom filters on id, Delta will also skip irrelevant files efficiently.

---


### ✅ For Deletes or Partial Updates

Delta supports whenMatchedDelete() or column-level update logic:

```python
(
    delta_table.alias("t")
    .merge(updates_df.alias("s"), "t.id = s.id")
    .whenMatchedUpdate(set = {
        "col1": "s.col1",
        "col2": "s.col2"
    })
    .whenNotMatchedInsert(values = {
        "id": "s.id",
        "col1": "s.col1",
        "col2": "s.col2"
    })
    .execute()
)
```

---

### ✅ If Only Deletes (e.g., tombstones)

```python
(
    delta_table.alias("t")
    .merge(deletes_df.alias("s"), "t.id = s.id")
    .whenMatchedDelete()
    .execute()
)
```


---

### 📊 Summary


| Approach                          | Reads full table? | Efficient for large tables? | Best use case                |
|------------------------------------|-------------------|-----------------------------|------------------------------|
| Full load → join → overwrite       | ✅ Yes            | ❌ No                       | Rare (only for small tables) |
| MERGE INTO with incremental DF     | ❌ No             | ✅ Yes                      | Incremental upserts          |
| DELETE / UPDATE SQL                | ❌ No             | ✅ Yes                      | Targeted deletes/updates     |
| Partition + ZORDER / Bloom filters | ❌ No             | ✅ Very                     | Repeated merges, file skipping|


---

### 🔥 Pro Tip:

If you’re running frequent incremental updates:

- 	Partition by high-cardinality column that aligns with query filters.
- 	Periodically OPTIMIZE ZORDER on your join key to make merges even faster.
- 	Keep incremental batches reasonably sized (e.g., < few million) for fast commit cycles.


---

🧪 Example End-to-End Incremental Update Job

```python
from delta.tables import DeltaTable

# Incremental source (e.g., new/changed rows)
incremental_df = spark.read.format("parquet").load("/incoming/updates")

# Target delta table
target = DeltaTable.forPath(spark, "/delta/main_table")

# Merge
(
    target.alias("t")
    .merge(incremental_df.alias("s"), "t.id = s.id")
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll()
    .execute()
)
```

👉 This will update only the relevant subset without reading the entire 80M dataset.


✅ TL;DR

No, you don’t need to load the full Delta table to update a subset.

Use MERGE INTO or targeted deletes/updates — they are designed exactly for this incremental use case.



