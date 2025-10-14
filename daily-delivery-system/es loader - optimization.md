

## Databrick Scala Spark ES loader - Optimization


Efficiently loading 80 million records from Databricks to a 40-node Elasticsearch cluster requires careful tuning of Spark configurations, Elasticsearch bulk ingestion settings, and Databricks cluster sizing. Below is an optimized Scala Spark solution with performance tuning.


---

### 1. Optimized Scala Spark Code


```scala
import org.apache.spark.sql.SparkSession
import org.elasticsearch.spark.sql._

val spark = SparkSession.builder()
  .appName("DatabricksToElasticsearch")
  .config("spark.sql.shuffle.partitions", "400")  // Increase partitions for parallelism
  .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")  // Efficient serialization
  .config("es.batch.size.entries", "10000")  // Bulk indexing size
  .config("es.batch.size.bytes", "10mb")  // Limit request size per batch
  .config("es.batch.write.refresh", "false")  // Disable auto-refresh for performance
  .config("es.index.auto.create", "false")  // Avoid index auto-creation overhead
  .config("es.nodes.wan.only", "false")  // Use direct node communication
  .config("es.nodes", "es-cluster-endpoint")  // Replace with ES cluster
  .config("es.port", "9200")  // Elasticsearch port
  .getOrCreate()

// Load DataFrame (Example: JSON format in Data Lake)
val df = spark.read.json("s3://your-bucket/path-to-json")

// Optimize partitions for better parallelism
val numPartitions = 400  // Adjust based on ES cluster size and data volume
val partitionedDF = df.repartition(numPartitions)

// Define index and type
val esIndex = "your_index_name/_doc"

// Write data to Elasticsearch
partitionedDF.write
  .format("org.elasticsearch.spark.sql")
  .option("es.resource", esIndex)
  .option("es.nodes", "es-cluster-endpoint")
  .option("es.port", "9200")
  .option("es.batch.write.retry.count", "10")  // Retry failures
  .option("es.batch.write.retry.wait", "10s")  // Wait between retries
  .option("es.mapping.id", "document_id")  // Use a field as ID to avoid duplicates
  .save()

spark.stop()
```

---

### 2.  Optimized Spark Configuration in Databricks

Modify these Spark configs in Databricks Cluster Settings:

```ini
spark.dynamicAllocation.enabled       true
spark.dynamicAllocation.minExecutors  20
spark.dynamicAllocation.maxExecutors  80
spark.executor.memory                 16g
spark.executor.cores                  4
spark.driver.memory                   8g
spark.driver.cores                    4
spark.sql.shuffle.partitions          400
spark.serializer                      org.apache.spark.serializer.KryoSerializer
```

---

### 3. Recommended Databricks Cluster Sizing


| Cluster Type	| Recommended Specs| 
|-----------------------------------|-------------------------------------|
| Workers	| 40-60 nodes (depending on data size & indexing speed)| 
| Instance Type	| i3.4xlarge (16 vCPUs, 122GB RAM) (optimized for IO-heavy tasks)| 
| Executors	| At least 40-80 Executors (to match ES nodes)| 
| Cores/Executor| 	4| 
| Memory/Executor| 	16-32GB| 

---

### 4.  Elasticsearch Index Tuning for High-Speed Ingestion

1.	**Disable Refresh**

```sh
PUT your_index_name/_settings
{
  "index": {
    "refresh_interval": "-1",
    "number_of_replicas": 0
  }
}
```

2.	**Increase Bulk Thread Pool in ES** (elasticsearch.yml)

```ini
    thread_pool.bulk.queue_size: 500
```

3.	**Set Proper Sharding Strategy**

```sh
PUT your_index_name
{
  "settings": {
    "number_of_shards": 40,
    "number_of_replicas": 1
  }
}
```

4.	**Re-enable Refresh & Replicas After Ingestion**

```sh
PUT your_index_name/_settings
{
  "index": {
    "refresh_interval": "1s",
    "number_of_replicas": 1
  }
}
```

**Expected Performance**

- Indexing Speed: 5k-15k records/sec per node
- Estimated Time: 80 million records ≈ 1-2 hours


**Summary:**

- Use Databricks Dynamic Allocation to scale resources.
- Optimize Spark partitions & ES bulk indexing settings.
- Disable refresh & replicas during indexing for speed.
- Ensure Databricks cluster matches Elasticsearch node count for efficiency.


---

### 5. Key Considerations for Optimal Performance


5.1.	**Elasticsearch Bulk Indexing Throughput**
    -	Elasticsearch has limitations on how many documents it can ingest per second per node.
    -	If your ES cluster is already running at max throughput, adding more Databricks nodes won’t help.
    -	Check the ES cluster’s indexing rate (GET /_nodes/stats/indices) to estimate the max indexing speed.

5.2.	**Databricks Spark Cluster Parallelism**
    -	You can efficiently load 80M+ documents with a 5-10 node Databricks cluster if properly tuned.
    -	More nodes ≠ Faster indexing if Elasticsearch is the bottleneck.
    -	You need to balance number of Spark partitions and bulk request size.

5.3.	**Bulk Request Size & Spark Partitioning**
    -	Use bulk.size tuning in elasticsearch-hadoop:
    -	Small bulk size (1MB-5MB) → reduces memory pressure on ES.
    -	Large bulk size (50MB+) → fewer requests but higher ES load.
    -	Adjust Spark partitions dynamically:

```scala
val partitionCount = 5 * spark.conf.get("spark.databricks.clusterUsage.numWorkers").toInt
val df = spark.read.format("delta").load("/mnt/delta/table").repartition(partitionCount)
```

5.4.	**Networking & I/O Constraints**

-	Databricks → Elasticsearch network throughput (check es.nodes bandwidth).
-	Use dedicated ES ingest nodes to avoid overwhelming query nodes.


---

### 6. Recommended Cluster Setup


| **Cluster Type**       | **Databricks Nodes** | **Driver/Worker Type**           | **Parallelism Strategy**                           |
|-----------------------|--------------------|---------------------------------|--------------------------------------------------|
| **High-Performance**  | 8-10              | 16-32 cores, high RAM           | 3-5 partitions per node, 5MB bulk size           |
| **Balanced (Cost vs. Speed)** | 5-6       | 8-16 cores                      | 2-4 partitions per node, 5-10MB bulk size        |
| **Minimal Setup**     | 3-4               | 8 cores                          | 2 partitions per node, 1-5MB bulk size           |


---

**Conclusion**

🚀 Best Approach:

-	Start with 5-10 Databricks nodes (not 40).
-	Monitor ES indexing rate (_nodes/stats/indices).
-	Use 3-5 partitions per worker for optimal parallelism.
-	Optimize bulk.size to match Elasticsearch throughput.


