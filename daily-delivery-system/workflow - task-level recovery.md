
## Methodology & Approach for Task-Level Recovery in a Data Pipeline Job


When running multiple data processing tasks sequentially within a single job, where each task’s output serves as input for the next task, it’s essential to implement a robust checkpointing and recovery mechanism. This ensures that when a task fails, it can resume from the last successful task instead of re-executing the entire pipeline.

---

### 1. Architecture & Workflow Approach

The architecture should include:

1.	Task-Level Checkpointing
-	Save intermediate task outputs to a durable storage (e.g., Delta Lake, S3, or a distributed file system).
-	Maintain a metadata log (e.g., in Delta tables, relational databases, or a key-value store) tracking task success/failure.

2.	Retry & Error Handling
-	Implement automatic retries for transient failures.
-	If a task fails after a set retry limit, log it and allow manual or automated re-execution from the failed task.

3.	State Management & Recovery
-	Maintain a task execution log that tracks completed tasks.
-	On failure, read the execution log and resume from the last successful step.

---

### 2.  Databricks Workflow Implementation

Using Databricks Workflows (Task-Oriented Execution)

Databricks supports task dependencies, allowing you to restart from failed tasks without rerunning completed ones.

-	Define each task as a separate Databricks workflow task.
-	Set dependent tasks to trigger only when their required predecessor task has successfully completed.
-	If a task fails, you can retry or manually rerun just that task.

Example Databricks Job Task Graph:

```text
Task 1 → Task 2 → Task 3 → Task 4

If Task 3 fails, you can restart Task 3 and Task 4 without rerunning Task 1 & Task 2.
```

---

### 3. Scala Spark Implementation Using Checkpoints & Metadata Log

The following example demonstrates:

-	Task execution tracking using Delta Lake metadata.
-	Automatic resumption from the last successful task.


#### 1️⃣ Define a Metadata Log Table

Each task writes a checkpoint entry in a tracking table.

```scala
import org.apache.spark.sql.SparkSession

val spark = SparkSession.builder()
  .appName("Pipeline with Task Recovery")
  .getOrCreate()

// Define the metadata checkpoint table
val checkpointTable = "task_execution_log"

spark.sql(s"""
  CREATE TABLE IF NOT EXISTS $checkpointTable (
    task_name STRING,
    status STRING, -- "SUCCESS", "FAILED", "RUNNING"
    timestamp TIMESTAMP
  ) USING DELTA
""")
```
---

#### 2️⃣ Function to Check Task Completion

Before running a task, check if it has already been completed.

```scala
def isTaskCompleted(taskName: String): Boolean = {
  val df = spark.sql(s"SELECT * FROM $checkpointTable WHERE task_name = '$taskName' AND status = 'SUCCESS'")
  df.count() > 0
}
```
---

#### 3️⃣ Process Tasks with Recovery Mechanism

Each task logs its execution status before starting and updates it after success.

```scala
def executeTask(taskName: String, taskLogic: () => Unit): Unit = {
  if (!isTaskCompleted(taskName)) {
    try {
      // Mark task as running
      spark.sql(s"INSERT INTO $checkpointTable VALUES ('$taskName', 'RUNNING', current_timestamp())")

      // Execute the task logic
      taskLogic()

      // Mark task as success
      spark.sql(s"UPDATE $checkpointTable SET status = 'SUCCESS' WHERE task_name = '$taskName'")
      println(s"Task $taskName completed successfully.")
    } catch {
      case e: Exception =>
        // Mark task as failed
        spark.sql(s"UPDATE $checkpointTable SET status = 'FAILED' WHERE task_name = '$taskName'")
        println(s"Task $taskName failed: ${e.getMessage}")
    }
  } else {
    println(s"Skipping $taskName, already completed.")
  }
}
```

---

#### 4️⃣ Define Your Tasks

Each task runs only if it hasn’t already been successfully executed.

```scala
executeTask("Task1", () => {
  // Task 1 logic (e.g., reading data, transformation)
  println("Executing Task 1")
})

executeTask("Task2", () => {
  // Task 2 logic
  println("Executing Task 2")
})

executeTask("Task3", () => {
  // Task 3 logic
  println("Executing Task 3")
})

executeTask("Task4", () => {
  // Task 4 logic
  println("Executing Task 4")
})
```

---

### Summary

Task-Level Recovery in Databricks Workflow

| Feature                 | Approach |
|-------------------------|----------|
| **Task Execution Tracking** | Store task execution state in a metadata table (Delta Lake or relational DB). |
| **Failure Recovery** | Resume execution from the last failed task, avoiding re-running previous tasks. |
| **Parallel Processing** | Tasks can be independent or have dependencies managed in Databricks workflows. |
| **Resilient Processing** | Automatic retries, error handling, and logging. |
| **Storage for Intermediate Outputs** | Use Delta Lake, Parquet, or S3 for storing outputs between tasks. |
| **Best Approach** | Use Databricks workflows for structured task dependencies and recovery mechanisms. |


---

### Final Recommendation

-	Use Databricks Workflows for a managed approach with task dependencies.
-	Use Scala Spark Checkpointing for finer control over failures and retries.
-	Store metadata logs to track completed and failed tasks, ensuring efficient recovery without redundant processing.


---



## Workflow for Task-Level Recovery in a Data Pipeline Job - No programming


Yes, it’s possible to implement a workflow with failure point recovery in Databricks using only Delta Lake, Databricks Workflows, and Task Configuration—without additional programming. Here’s how:


### 1. Use Databricks Workflows for Task Orchestration

-	Define multiple tasks in a Databricks Workflow Job.
-	Set dependencies between tasks (output of one task as input for another).
-	Configure retry policies for automatic recovery.

---

### 2. Store Task Execution Status in Delta Lake

-	Each task updates a metadata table (stored in Delta Lake) that tracks:
    -	Task Name
    -	Status (Success, Failed, In Progress)
    -	Timestamp
    -	Error Logs (if any)
-	This allows workflows to resume from the last failed task instead of restarting.

---

### 3. Configure Failure Recovery in Databricks Workflow

-	Enable “Run on Failure” Options:
    -	Retry Failed Tasks Automatically (Set Max Retries in Task Settings).
    -	On Failure, Resume from Last Successful Task.
-	Use Conditional Execution:
    -	Check if a task has already been completed using the metadata table.
    -	Skip execution if the task is marked as Success.

---

### 4. Use Delta Tables for Intermediate Data Storage

-	Save task outputs to Delta Lake (e.g., bronze, silver, gold layers).
-	Tasks read only required partitions, reducing redundant processing.

---

### 5. No Programming Required – Configuration Only
   
-	Workflow Job: Configured in UI with task dependencies.
-	Failure Handling: Set retry policies.
-	Delta Lake: Stores status & data checkpoints.
-	Cluster Autoscaling: Optimizes cost & performance.


---

### Example Workflow Execution Flow

|Task	|Status Check|	Action|
|-------------------------|----------|----------|
|Task 1: Extract Data	|Check if output exists|	Skip if success, else run|
|Task 2: Transform Data	|Check status in Delta Table|	Skip or rerun only if failed|
|Task 3: Load Data to Target|	Read processed data from Delta	|Resume from failure if needed|

---

### Conclusion

✅ Yes, it’s possible to build a fully recoverable pipeline using Databricks Workflows & Delta Lake—without programming.
🚀 Best for ETL pipelines, batch processing, and fault-tolerant workflows.



---



## Example: Workflow for Task-Level Recovery in a Data Pipeline Job


### Step-by-Step Guide: Configuring Databricks Workflow for Failure Recovery

This guide shows how to configure a Databricks Workflow Job using Delta Lake for failure recovery in job.yml. The setup ensures that:

-	Multiple tasks run sequentially.
-	Each task checks its previous execution status in a Delta Table before running.
-	Only failed tasks are retried instead of restarting from scratch.
-	Databricks retry settings are configured for automatic recovery.

---

#### 1️⃣ Configure Delta Table for Tracking Task Status

Before setting up the workflow, create a Delta Table (pipeline_task_status) to track task execution.

Run the following once in a Databricks notebook:

```sql
CREATE TABLE IF NOT EXISTS pipeline_task_status (
    task_name STRING,
    status STRING,      -- 'Success', 'Failed', 'In Progress'
    timestamp TIMESTAMP,
    error_message STRING
) USING DELTA;

```

--- 

##### ️⃣ Define Workflow in job.yml

Below is an example job.yml file that defines a multi-step workflow with failure recovery:

```yaml
job:
  name: "data_pipeline_workflow"

  tasks:
    - task_key: extract_data
      description: "Extract data from source"
      existing_cluster_id: <CLUSTER_ID>
      notebook_task:
        notebook_path: "/Repos/MyRepo/ExtractData"
      libraries: []
      max_retries: 3
      retry_on_timeout: true
      depends_on: []
      
    - task_key: transform_data
      description: "Transform extracted data"
      existing_cluster_id: <CLUSTER_ID>
      notebook_task:
        notebook_path: "/Repos/MyRepo/TransformData"
      libraries: []
      max_retries: 3
      retry_on_timeout: true
      depends_on:
        - task_key: extract_data
      
    - task_key: load_data
      description: "Load data into target system"
      existing_cluster_id: <CLUSTER_ID>
      notebook_task:
        notebook_path: "/Repos/MyRepo/LoadData"
      libraries: []
      max_retries: 3
      retry_on_timeout: true
      depends_on:
        - task_key: transform_data
```

---

#### 3️⃣ Task Execution Logic

Each task notebook should:

1.	Check the pipeline_task_status table.
2.	Skip execution if the task is already successful.
3.	Update status upon failure for recovery.

Example pseudocode for each task notebook:


```python
from pyspark.sql.functions import col
from datetime import datetime

# Define Task Name (should match `task_key` in job.yml)
TASK_NAME = "extract_data"

# Read task status from Delta Table
task_status_df = spark.read.table("pipeline_task_status").filter(col("task_name") == TASK_NAME)

# If task is already successful, exit early
if not task_status_df.filter(col("status") == "Success").isEmpty():
    dbutils.notebook.exit("Task already completed successfully.")

# Log task as in-progress
spark.sql(f"""
    MERGE INTO pipeline_task_status AS target
    USING (SELECT '{TASK_NAME}' AS task_name, 'In Progress' AS status, current_timestamp() AS timestamp, NULL AS error_message) AS source
    ON target.task_name = source.task_name
    WHEN MATCHED THEN UPDATE SET target.status = 'In Progress', target.timestamp = source.timestamp
    WHEN NOT MATCHED THEN INSERT (task_name, status, timestamp) VALUES (source.task_name, source.status, source.timestamp)
""")

try:
    # ---- Your Data Processing Logic Here ----
    print("Running extraction process...")

    # Simulating processing
    import time
    time.sleep(10)

    # Mark task as successful
    spark.sql(f"""
        UPDATE pipeline_task_status 
        SET status = 'Success', timestamp = current_timestamp()
        WHERE task_name = '{TASK_NAME}'
    """)

except Exception as e:
    # Log error & mark failure
    spark.sql(f"""
        UPDATE pipeline_task_status 
        SET status = 'Failed', timestamp = current_timestamp(), error_message = '{str(e)}'
        WHERE task_name = '{TASK_NAME}'
    """)
    raise e  # Ensure Databricks workflow catches the failure for retry
```

```scala
import org.apache.spark.sql.functions._
import org.apache.spark.sql.SparkSession
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

val spark = SparkSession.builder().appName("TaskExample").getOrCreate()

// Define Task Name (should match `task_key` in job.yml)
val taskName = "extract_data"

// Read task status from Delta Table
val taskStatusDF = spark.read.table("pipeline_task_status").filter(col("task_name") === taskName)

// If task is already successful, exit early
if (taskStatusDF.filter(col("status") === "Success").isEmpty) {
  dbutils.notebook.exit("Task already completed successfully.")
}

// Log task as in-progress
spark.sql(s"""
    MERGE INTO pipeline_task_status AS target
    USING (SELECT '$taskName' AS task_name, 'In Progress' AS status, current_timestamp() AS timestamp, NULL AS error_message) AS source
    ON target.task_name = source.task_name
    WHEN MATCHED THEN UPDATE SET target.status = 'In Progress', target.timestamp = source.timestamp
    WHEN NOT MATCHED THEN INSERT (task_name, status, timestamp) VALUES (source.task_name, source.status, source.timestamp)
""")

try {
  // ---- Your Data Processing Logic Here ----
  println("Running extraction process...")

  // Simulating processing (sleep)
  Thread.sleep(10000)

  // Mark task as successful
  spark.sql(s"""
    UPDATE pipeline_task_status 
    SET status = 'Success', timestamp = current_timestamp()
    WHERE task_name = '$taskName'
  """)

} catch {
  case e: Exception =>
    // Log error & mark failure
    spark.sql(s"""
      UPDATE pipeline_task_status 
      SET status = 'Failed', timestamp = current_timestamp(), error_message = '${e.getMessage}'
      WHERE task_name = '$taskName'
    """)
    throw e  // Ensure Databricks workflow catches the failure for retry
}


```


---

#### 4️⃣ How This Ensures Failure Recovery

-	Each task first checks its status in pipeline_task_status.
-	If successful, it skips execution to save compute time.
-	If failed, it retries based on max_retries in job.yml.
-	If a task fails after all retries, it will stay in the “Failed” state in Delta Lake.
-	Manual recovery: Only failed tasks need to be re-run.


---

### ✅ Benefits of This Approach

-	No manual intervention required for retries.
-	Efficient failure recovery – no need to start from scratch.
-	Delta Lake ensures consistency – task statuses are stored persistently.
-	Works with Databricks Workflows – no external workflow manager required.


---

### 🔔 Failure Alerting

1.	Email Notifications: Configure job failure alerts to notify team members.
2.	Webhook Integration: Send failure alerts to Slack, Teams, or monitoring systems.
3.	Datadog or PagerDuty Integration: Trigger alerts in observability tools.

---

### 🔄 Automated Rollback on Failure

1.	Delta Lake Time Travel: If a processing step fails, revert to the last checkpoint using RESTORE.
2.	Job Restart with Checkpoints: Restart from the last successful step instead of reprocessing everything.
3.	Retries with Backoff: Automatically retry failed steps with exponential backoff.


```python
from delta.tables import DeltaTable
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("RollbackExample").getOrCreate()
delta_table = DeltaTable.forPath(spark, "dbfs:/mnt/delta/staging_table")

# Rollback to the previous version on failure
try:
    df = spark.read.format("delta").load("dbfs:/mnt/delta/staging_table")
    df.write.format("delta").mode("overwrite").save("dbfs:/mnt/delta/staging_table")
except Exception:
    print("Rolling back due to failure...")
    spark.sql("RESTORE TABLE staging_table TO VERSION AS OF 1")  # Rollback
```


```scala
import org.apache.spark.sql.SparkSession
import io.delta.tables._

val spark = SparkSession.builder().appName("RollbackExample").getOrCreate()
val deltaTable = DeltaTable.forPath(spark, "dbfs:/mnt/delta/staging_table")

// Rollback to the previous version on failure
try {
  val df = spark.read.format("delta").load("dbfs:/mnt/delta/staging_table")
  df.write.format("delta").mode("overwrite").save("dbfs:/mnt/delta/staging_table")
} catch {
  case e: Exception =>
    println("Rolling back due to failure...")
    spark.sql("RESTORE TABLE staging_table TO VERSION AS OF 1")  // Rollback
}
```


---

### 🔥 Recommended Approach

-	Use Databricks Workflow Task Dependencies for automatic retries & failure recovery.
-	Store intermediate data in Delta Lake and use versioning for rollback.
-	Enable alerting via email, Slack, or monitoring tools.


---

### A complete YAML example for configuring failure recovery in Databricks Workflows

Here’s a complete Databricks Workflow YAML configuration for failure recovery, automated rollback, and alerting  in Databricks Workflows.:

#### 📌 Key Features in This job.yml

1.	Failure Recovery with Retry:
-	If a task fails, it retries 3 times with exponential backoff.
-	If it still fails, it skips to the rollback task instead of failing the whole workflow.

2.	Automated Rollback on Failure:
-	Uses Delta Lake Time Travel to restore the last successful version.

3.	Alerting on Failure:
-	Sends email notifications.
-	Can be extended to Slack, Teams, or PagerDuty via Webhooks.

---

#### 📌 Databricks Job Configuration (job.yml)

```yaml
name: "Data Pipeline Workflow with Failure Recovery"
email_notifications:
  on_failure:
    - "your_team_email@example.com"  # Alerting on job failure

tasks:
  - task_key: extract_data
    job_cluster_key: main_cluster
    notebook_task:
      notebook_path: "/Repos/my_repo/extract_data"
    retry_policy:
      max_retries: 3
      min_retry_interval_millis: 30000  # 30 seconds
      retry_on_timeout: true

  - task_key: transform_data
    depends_on:
      - task_key: extract_data
    job_cluster_key: main_cluster
    notebook_task:
      notebook_path: "/Repos/my_repo/transform_data"
    retry_policy:
      max_retries: 2
      min_retry_interval_millis: 30000
      retry_on_timeout: true

  - task_key: load_data
    depends_on:
      - task_key: transform_data
    job_cluster_key: main_cluster
    notebook_task:
      notebook_path: "/Repos/my_repo/load_data"
    retry_policy:
      max_retries: 3
      min_retry_interval_millis: 45000
      retry_on_timeout: true

  - task_key: rollback_on_failure
    depends_on:
      - task_key: load_data
    job_cluster_key: main_cluster
    notebook_task:
      notebook_path: "/Repos/my_repo/rollback"
    condition_task:
      condition: "FAILED"
      task_key: load_data  # Run rollback only if "load_data" fails

  - task_key: retry_failed_records
    depends_on:
      - task_key: rollback_on_failure
    job_cluster_key: main_cluster
    notebook_task:
      notebook_path: "/Repos/my_repo/retry_failed_records"
    retry_policy:
      max_retries: 2
      min_retry_interval_millis: 30000
      retry_on_timeout: true

```

---

#### 📌 Supporting Notebooks

1️⃣ Rollback Notebook (rollback_data)

```python
from delta.tables import DeltaTable
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("RollbackExample").getOrCreate()
table_path = "dbfs:/mnt/delta/staging_table"

# Rollback to the last successful version
print("Rolling back to previous version due to failure...")
spark.sql(f"RESTORE TABLE staging_table TO VERSION AS OF (SELECT MAX(version) FROM (DESCRIBE HISTORY staging_table) WHERE operation = 'WRITE')")
```

```scala
from delta.tables import DeltaTable
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("RollbackExample").getOrCreate()
table_path = "dbfs:/mnt/delta/staging_table"

# Rollback to the last successful version
print("Rolling back to previous version due to failure...")
spark.sql(f"RESTORE TABLE staging_table TO VERSION AS OF (SELECT MAX(version) FROM (DESCRIBE HISTORY staging_table) WHERE operation = 'WRITE')")
```


---

### 🔥 Summary


| Feature                 | Description |
|-------------------------|-------------|
| **Retries**              | Each task retries **3 times** before failing. |
| **Failure Recovery**     | If a task fails, it **automatically moves to rollback** instead of stopping the workflow. |
| **Automated Rollback**   | Uses **Delta Lake Time Travel** to restore the last successful version. |
| **Alerts**               | Sends **email notifications on failure**. |