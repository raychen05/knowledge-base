

## Architecture Overview & Configuration

To implement an automated, fault-tolerant data pipeline with multiple jobs that can run sequentially or in parallel, where a job’s input depends on the output of other jobs, and failure recovery is applied only to the failed job without restarting from the beginning, you can leverage Databricks Jobs and a Metadata Log Table to track the job statuses.

---

### 1. Architecture Overview

1.	Databricks Jobs: Define individual jobs in Databricks. Each job can run in parallel or sequentially depending on the dependencies you configure.
2.	Metadata Log Table: A table to track the job statuses (pending, in-progress, success, failed). This log will help in identifying which job failed, and it allows you to resume from the failed job instead of re-running the entire pipeline.
3.	Job Dependencies: Define the execution order based on job dependencies. If Job B depends on Job A’s output, Job B will not start until Job A completes successfully.
4.	Error Recovery: If a job fails, the failure is logged, and the pipeline can be retried from the failed job without affecting the already successful jobs.


---

### 2. Step-by-Step Workflow Configuration in Databricks (No Programming Required)


---

#### step-1. Create a Metadata Log Table

This table will track the execution status of each job in the pipeline. You can create this table using a Databricks notebook or manually, depending on your environment.

Example structure of the table:
```sql
CREATE TABLE job_metadata (
    job_id STRING,
    job_name STRING,
    status STRING,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    error_message STRING
)
```


-	job_id: Unique identifier for each job run.
-	job_name: Name of the job.
-	status: Job status (pending, in-progress, success, failed).
-	start_time and end_time: Time when the job started and ended.
-	error_message: Detailed error message if the job fails.

You can use this table to log the status of each job during its execution.


---

#### step-2. Configure Databricks Jobs

You can configure multiple jobs within the Databricks UI. Here’s how you can configure a simple pipeline with sequential or parallel jobs and a dependency on another job’s output.

*Step 2.1: Define Jobs*

-	Job 1: Task A
-	Job 2: Task B (depends on Task A)
-	Job 3: Task C (can run in parallel with Task B)
-	Job 4: Task D (depends on Task B)

---

**Step 2.2: Configure Sequential Jobs**

In Databricks, you can set up dependencies for jobs. If Job B depends on Job A, follow these steps:

1.	Create Job 1 (Task A) and configure it to run.
2.	Create Job 2 (Task B) and set the dependency to Job 1, so it will only run after Job 1 successfully completes.
3.	Create Job 3 (Task C) and set it to run in parallel with Job 2 (no dependency).

Example: Job 2 (Task B) depends on the output of Job 1 (Task A).
-	In the Databricks Jobs UI, go to Job 2 configuration.
-	Under Job Cluster, set the Dependency to Job 1. This ensures that Job 2 only runs after Job 1 finishes successfully.

---

**Step 2.3: Configure Parallel Jobs**

In Databricks, jobs that are independent can run in parallel. For example, if Job 3 doesn’t depend on Job 2, you can configure them to run in parallel:

1.	Create Job 3 (Task C) and configure it as an independent job with no dependencies on Job 1 or Job 2.
2.	Jobs 3 and 2 will run concurrently.

---

**Step 2.4: Failure Handling and Retry**

1.	Configure Retry Logic: In the Databricks UI, under each job’s settings, you can set the number of retries in case of a job failure.
2.	Failure Recovery: In case a job fails, you can configure the job to retry automatically up to a set number of times. After the retries are exhausted, the job should mark as failed in the metadata table.
3.	Job Dependency: If a job depends on the output of a previous job, it will not run unless the previous job is successful. If Job 1 fails, Job 2 won’t run until Job 1 succeeds.

---

### 3. Update the Metadata Log Table

Each job will log its status in the metadata log table during execution. After each job run, update the status (in-progress, success, or failed) in the metadata table.

-	Start Job: When a job starts, insert a row into the metadata table with status in-progress.
-	End Job: When a job completes, update the table:
-	If successful, set status to success.
-	If failed, set status to failed, and store the error message.


---

### 4. Recovery from Failure

If a job fails:

-	The job can be retried automatically using Databricks’ retry settings.
-	The Metadata Log Table helps you to track where the pipeline failed. You can configure subsequent jobs to either continue based on the metadata log or retry the failed job.
-	If needed, use the RESTORE operation on Delta tables to rollback to a previous stable state (this would be part of the job recovery logic you implement in Databricks).

---

### 5. Monitor and Alerting

-	You can configure Databricks to send email notifications on job failures and retries.
-	Use Databricks Job Notifications to alert stakeholders via email or webhook when jobs fail or succeed.
-	Set up Databricks Dashboards to visually monitor the status of jobs and the overall pipeline health.


---

### 6. Example of Job Configuration in Databricks UI

1.	Job 1 (Task A):
-	Type: Notebook/Run command
-	Dependencies: None (first job in the pipeline)
-	Retry Settings: Set retry count (e.g., 3 retries)

2.	Job 2 (Task B):
-	Type: Notebook/Run command
-	Dependencies: Job 1 (runs only after Job 1 completes successfully)
-	Retry Settings: Set retry count (e.g., 3 retries)

3.	Job 3 (Task C):
-	Type: Notebook/Run command
-	Dependencies: None (runs in parallel with Job 2)
-	Retry Settings: Set retry count (e.g., 3 retries)

4.	Job 4 (Task D):
-	Type: Notebook/Run command
-	Dependencies: Job 2 (depends on Task B’s completion)
-	Retry Settings: Set retry count (e.g., 3 retries)

---

### Summary:

-	Job Dependencies: Set jobs to run sequentially or in parallel by defining dependencies in Databricks Jobs UI.
-	Retry Logic: Configure automatic retries for job failures.
-	Metadata Log Table: Track job statuses and recovery from failures.
-	Failure Recovery: Retry failed jobs, and continue the pipeline from the last successful job.
-	Alerting: Set up email or webhook alerts for failure notifications.

This approach allows you to manage and automate complex workflows in Databricks without programming, and ensures that jobs only retry in case of failure, using the metadata table to track progress and prevent unnecessary reruns.



---


##  Configuration Example of Multiple Jobs

Here are individual job.yml configuration files for each Databricks Workflow Job in the pipeline. These jobs are separate individual jobs, not tasks within a single job.


### 📌 Overview of the Workflow:

1.	data_extract_job.yml → Extracts data from the source.
2.	data_load_job.yml → Loads extracted data into a Delta table.
3.	es_load_job.yml → Indexes loaded data into Elasticsearch.

**Dependencies**:

-	data_extract_job runs first.
-	data_load_job runs after data_extract_job completes.
-	es_load_job runs after data_load_job completes.
-	Jobs automatically retry on failure and send alerts.

---

### 1️⃣ Data Extract Job (data_extract_job.yml)

```yaml
jobs:
  - name: Data_Extract_Job
    job_clusters:
      - job_cluster_key: extract_cluster
        new_cluster:
          spark_version: "11.3.x-scala2.12"
          num_workers: 4
    tasks:
      - task_key: ExtractTask
        description: "Extract data from the source system"
        notebook_task:
          notebook_path: "/Workspace/Pipeline/Extract"
        max_retries: 3
        retry_on_timeout: true
        timeout_seconds: 3600
    email_notifications:
      on_failure:
        - data_pipeline_admin@example.com
    # This job triggers the next job after success
    on_success:
      trigger_job:
        job_name: Data_Load_Job
```

---

### 2️⃣ Data Load Job (data_load_job.yml)

```yaml
jobs:
  - name: Data_Load_Job
    job_clusters:
      - job_cluster_key: load_cluster
        new_cluster:
          spark_version: "11.3.x-scala2.12"
          num_workers: 4
    tasks:
      - task_key: LoadTask
        description: "Load extracted data into Delta table"
        notebook_task:
          notebook_path: "/Workspace/Pipeline/Load"
        max_retries: 3
        retry_on_timeout: true
        timeout_seconds: 3600
    email_notifications:
      on_failure:
        - data_pipeline_admin@example.com
    # This job triggers the next job after success
    on_success:
      trigger_job:
        job_name: ES_Load_Job
```

---

### 3️⃣ Elasticsearch Load Job (es_load_job.yml)

```yaml
jobs:
  - name: ES_Load_Job
    job_clusters:
      - job_cluster_key: es_cluster
        new_cluster:
          spark_version: "11.3.x-scala2.12"
          num_workers: 4
    tasks:
      - task_key: ESLoadTask
        description: "Index loaded data into Elasticsearch"
        notebook_task:
          notebook_path: "/Workspace/Pipeline/ES_Load"
        max_retries: 3
        retry_on_timeout: true
        timeout_seconds: 3600
    email_notifications:
      on_failure:
        - data_pipeline_admin@example.com
```

---

### 📌 How It Works

1.	Data_Extract_Job runs first.
2.	When Data_Extract_Job completes successfully, it automatically triggers Data_Load_Job.
3.	When Data_Load_Job completes successfully, it automatically triggers ES_Load_Job.
4.	If any job fails, it retries up to 3 times.
5.	Email alerts are sent on failures.


### 🌟 Why This Approach?

- ✅ Jobs are independent but still linked using triggers.
- ✅ Failure Recovery → Failed jobs retry without restarting the whole pipeline.
- ✅ Scalable → Each job runs on its own cluster, improving performance.
- ✅ Automated Execution Flow → No manual intervention needed.

This setup automates your Databricks Workflow Pipeline in a structured, failure-resilient way! 🚀