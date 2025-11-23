

##  Architecture of ES Loader in Databrick Workflows


 Implementing the Elasticsearch (ES) loader as a separate common job in Databricks is a great design choice. This allows multiple data processing jobs to trigger the loader asynchronously with parameters, ensuring scalability, reusability, and parallel execution.

---

### 1. Recommended Architecture


#### 1.1. Common ES Loader Job

-	A standalone Databricks job that loads data into ES.
-	Accepts parameters such as:
    -	source_table (processed data location)
    -	data_source (to determine the ES index)
    -	es_nodes
    -	batch_id (optional for tracking)
    -	Can be triggered by different pipelines.

---

#### 1.2. Data Processing Jobs

-	Each data pipeline processes and writes transformed data to a staging location (Delta/S3).
-	It triggers the ES loader job asynchronously with required parameters.

---

#### 1.3. Parallel Execution

-	If a single processing job produces multiple datasets for different indices, it can trigger multiple asynchronous ES loader jobs.
-	Jobs can run in parallel for different data sources.


---


### 2. Implementation


#### 2.1. Create a Common ES Loader Job in Databricks

Scala Spark Code for ES Loader Job
```scala
    import org.apache.spark.sql.{DataFrame, SparkSession}
    import org.elasticsearch.spark.sql._

    object ESLoaderJob {

    def loadToES(spark: SparkSession, sourceTable: String, dataSource: String, esNodes: String): Unit = {
        // Read processed data
        val df = spark.read.format("delta").load(sourceTable)

        // Define mapping of data sources to indices
        val indexMapping = Map(
        "sourceA" -> "index_a",
        "sourceB" -> "index_b",
        "sourceC" -> "index_c"
        )

        val esIndex = indexMapping.getOrElse(dataSource, "default_index")

        // ES Config
        val esConfig = Map(
        "es.nodes" -> esNodes,
        "es.port" -> "9200",
        "es.resource" -> s"$esIndex/_doc",
        "es.nodes.wan.only" -> "true",
        "es.mapping.id" -> "id"
        )

        // Write DataFrame to ES
        df.write
        .format("org.elasticsearch.spark.sql")
        .options(esConfig)
        .mode("append")
        .save()
    }

    def main(args: Array[String]): Unit = {
        val spark = SparkSession.builder()
        .appName("Common ES Loader Job")
        .getOrCreate()

        // Read parameters passed to the job
        val sourceTable = sys.env.getOrElse("SOURCE_TABLE", "")
        val dataSource = sys.env.getOrElse("DATA_SOURCE", "")
        val esNodes = sys.env.getOrElse("ES_NODES", "es-host")

        require(sourceTable.nonEmpty, "SOURCE_TABLE is required")
        require(dataSource.nonEmpty, "DATA_SOURCE is required")

        // Load data to Elasticsearch
        loadToES(spark, sourceTable, dataSource, esNodes)
    }
    }
```

---

#### 2.2. Trigger ES Loader from Another Job
   
Python Example to Trigger Parallel Jobs in Databricks

```python
    from databricks_api import DatabricksAPI
    import concurrent.futures

    # Initialize Databricks API client
    db = DatabricksAPI(host="https://<your-databricks-instance>", token="<your-token>")

    # List of ES Loader job invocations
    jobs = [
        {"source_table": "/mnt/datalake/sourceA", "data_source": "sourceA"},
        {"source_table": "/mnt/datalake/sourceB", "data_source": "sourceB"},
        {"source_table": "/mnt/datalake/sourceC", "data_source": "sourceC"}
    ]

    def trigger_es_loader(job_params):
        """Trigger ES Loader Databricks job with parameters."""
        response = db.jobs.run_now(
            job_id=<ES_LOADER_JOB_ID>,
            notebook_params={
                "SOURCE_TABLE": job_params["source_table"],
                "DATA_SOURCE": job_params["data_source"],
                "ES_NODES": "es-host"
            }
        )
        return response

    # Run multiple jobs in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(trigger_es_loader, jobs))

    # Print Job Run IDs
    for res in results:
        print(f"Triggered ES Loader Job Run ID: {res['run_id']}")
```

---

## Key Benefits of This Approach


- ✅ Reusability: The ES loader is a single, reusable component for all pipelines.
- ✅ Scalability: Multiple jobs can trigger it independently.
- ✅ Parallel Execution: Each data source loads its data into ES simultaneously.
- ✅ Decoupled Architecture: Processing jobs focus on transformations, while the ES loader handles indexing.


---


