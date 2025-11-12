

##  Monitoring Elasticsearch Ingestion in Databricks Workflow

To ensure optimal performance, we need to monitor the indexing rate, errors, and cluster resource usage in Elasticsearch while loading data from Databricks. This can help identify bottlenecks and dynamically adjust Spark partitioning or bulk settings.


---

### 1. Key Metrics to Monitor in Elasticsearch

You can monitor these using Elasticsearch APIs:

1.1. **Indexing Throughput** (documents per second):

```bash
GET _nodes/stats/indices
```

Look for:
-	indexing.index_total (Total docs indexed)
-	indexing.index_current (Docs currently being indexed)
-	indexing.index_time_in_millis (Time taken)


1.2. **Bulk Request Rejections** (if ES is overloaded):

```bash
GET _nodes/stats/thread_pool
```

Look for:
-	bulk.rejected (Too many bulk requests)
-	bulk.queue (Queue size)


1.3. **Cluster Resource Usage** (CPU, Memory, Disk I/O):

```bash
GET _cluster/stats
```

-	jvm.mem.heap_used_percent (Memory pressure)
-	fs.total.available_in_bytes (Disk space)
-	indices.store.size_in_bytes (Total index size)


---

### 2. Collect and Analyze ES Metrics in Databricks


You can use Databricks to query ES stats and log indexing progress.

Python Code to Monitor ES Indexing from Databricks

```python
import requests
import time

ES_HOST = "http://es-host:9200"

def get_es_indexing_stats():
    """Fetch Elasticsearch indexing statistics."""
    stats_url = f"{ES_HOST}/_nodes/stats/indices"
    response = requests.get(stats_url).json()
    
    total_docs = 0
    index_time = 0
    for node_id, data in response['nodes'].items():
        total_docs += data['indices']['indexing']['index_total']
        index_time += data['indices']['indexing']['index_time_in_millis']

    return total_docs, index_time / 1000  # Convert to seconds

def monitor_es_indexing(target_docs, sleep_interval=10):
    """Monitor ES indexing progress in real-time."""
    start_docs, _ = get_es_indexing_stats()
    
    while True:
        time.sleep(sleep_interval)
        current_docs, index_time = get_es_indexing_stats()
        indexed_docs = current_docs - start_docs
        
        print(f"Indexed {indexed_docs}/{target_docs} docs in {index_time} sec")
        
        if indexed_docs >= target_docs:
            print("Indexing complete!")
            break

# Monitor progress (e.g., 80M docs)
monitor_es_indexing(target_docs=80000000)
```

📌 This script will:
-	Poll ES every 10 seconds.
-	Print the number of indexed docs vs. the target (80M).
-	Stop when indexing is complete.


---

### 3. Dynamic Tuning of Bulk Size & Parallelism in Databricks

Based on ES indexing rate, we can adjust the bulk size dynamically.

Scala Spark Code for Adaptive Bulk Size

```scala
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.elasticsearch.spark.sql._
import scala.io.Source

def getESBulkRejections(esHost: String): Int = {
  val url = s"$esHost/_nodes/stats/thread_pool"
  val json = Source.fromURL(url).mkString
  val regex = """"bulk"\s*:\s*{\s*"rejected"\s*:\s*(\d+)""".r
  regex.findFirstMatchIn(json).map(_.group(1).toInt).getOrElse(0)
}

def adaptiveBulkSize(esHost: String): Int = {
  val rejections = getESBulkRejections(esHost)
  if (rejections > 0) {
    println(s"High bulk rejections detected ($rejections), reducing batch size...")
    2000 // Reduce batch size if ES is rejecting requests
  } else {
    5000 // Use higher batch size for optimal performance
  }
}

// Function to load data to Elasticsearch with adaptive tuning
def loadToES(df: DataFrame, esHost: String): Unit = {
  val batchSize = adaptiveBulkSize(esHost)

  val esConfig = Map(
    "es.nodes" -> esHost,
    "es.port" -> "9200",
    "es.resource" -> "my_index/_doc",
    "es.batch.size.entries" -> batchSize.toString, // Adjust dynamically
    "es.nodes.wan.only" -> "true",
    "es.mapping.id" -> "id"
  )

  df.write
    .format("org.elasticsearch.spark.sql")
    .options(esConfig)
    .mode("append")
    .save()
}

// Usage
val spark = SparkSession.builder().appName("ES Bulk Load with Monitoring").getOrCreate()
val df = spark.read.format("delta").load("/mnt/delta/table")
loadToES(df, "es-host")
```

----

### 4. Visualizing Metrics in Databricks

- Use Databricks SQL to log indexing speed into a table:

```sql
CREATE TABLE es_indexing_log (
    timestamp STRING,
    indexed_docs BIGINT,
    total_docs BIGINT
);

INSERT INTO es_indexing_log VALUES (current_timestamp(), 500000, 80000000);
```

-	Use Databricks Dashboards to visualize:
    -	Documents Indexed over Time
    -	ES Bulk Rejections
    -	ES Cluster Load (CPU, Memory)

---

### Final Strategy

🚀 Key Steps for Optimized ES Ingestion in Databricks
1.	Monitor ES indexing rate & bulk rejections via _nodes/stats.
2.	Dynamically adjust bulk size to prevent overload.
3.	Parallelize Spark writes based on ES indexing throughput.
4.	Log indexing progress in Databricks for real-time monitoring.
5.	Visualize ingestion trends using SQL Dashboards.


---

