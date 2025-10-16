
##  Start Databricks pipeline Bundle Multiple Times in Parallel


Excellent question — let’s unpack it carefully, because Databricks pipeline bundles and Workflows (Jobs) have some nuances in how they handle parallel executions with different parameters.

---

✅ Short answer

Yes — a Databricks pipeline bundle (deployed into Workflow space) can be started multiple times in parallel with different parameters and task IDs, as long as you configure each run correctly.

However, each run instance is isolated, so you need to make sure:
-	parameters (job inputs) are unique per run, and
-	concurrent runs don’t conflict in shared resources (e.g., Delta tables, checkpoints, output paths).

---

### 🧱 Key Concepts

1. Bundle deployment → Workflow job

When you deploy a Databricks pipeline bundle (YAML-defined) to the workflow space, it becomes a Databricks job (a workflow).
Each run of this job is an execution instance, tracked under the same job ID but with a unique run ID.

---

2. Parallel job runs

A single job can have multiple active runs — this is supported if you set:

```yaml
concurrent_run: ENABLED
```

in the job configuration (YAML), or enable it via UI under:  “Concurrent runs” → “Allow concurrent runs of this job”

That means:
- Run #1 can start with param = A
- Run #2 can start with param = B
- Both run simultaneously.

---

3. Passing different parameters

You can pass parameters in several ways:

a. From the REST API or CLI

```bash
databricks jobs run-now \
  --job-id 1234 \
  --notebook-params '{"task_id":"t1", "date":"2025-10-15"}'
```

Start another run with:
```bash
databricks jobs run-now \
  --job-id 1234 \
  --notebook-params '{"task_id":"t2", "date":"2025-10-16"}'
```

Both will execute the same pipeline bundle with different parameters.

b. From Workflow task parameters

If the job’s YAML defines:

```yaml
tasks:
  - task_key: process
    notebook_task:
      notebook_path: /Repos/.../pipeline_entry
      base_parameters:
        task_id: "{{bundle.parameters.task_id}}"
```


4. Parallel tasks within a single run

If your workflow has multiple tasks that don’t depend on each other, you can also configure task-level parallelism:

```yaml
tasks:
  - task_key: load_raw
  - task_key: process_data
    depends_on: []
  - task_key: summarize
    depends_on:
      - load_raw
```

---


### ⚙️ Example: Parallel Databricks pipeline runs

Let’s say your bundle defines:
```yaml
bundle:
  name: analytics-pipeline

workflows:
  - name: analytics-pipeline-job
    job_clusters:
      - job_cluster_key: default_cluster
        new_cluster:
          spark_version: 15.3.x-scala2.12
          node_type_id: i3.xlarge
          num_workers: 2

    tasks:
      - task_key: run_pipeline
        notebook_task:
          notebook_path: /Repos/.../main_pipeline
          base_parameters:
            task_id: "{{bundle.parameters.task_id}}"
            date: "{{bundle.parameters.date}}"
```

You can run this bundle multiple times:

```bash
databricks jobs run-now \
  --job-id 7890 \
  --notebook-params '{"task_id": "job_A", "date": "2025-10-15"}'

databricks jobs run-now \
  --job-id 7890 \
  --notebook-params '{"task_id": "job_B", "date": "2025-10-16"}'
```

Both execute in parallel with different task IDs and parameters.

---

⚠️ Watch out for

1.	Shared state conflicts — avoid writing to the same Delta tables, checkpoints, or S3 paths simultaneously.
→ Use parameter-based subpaths (e.g., output/task_id=<value>/).
2.	Cluster capacity — ensure your job cluster pool or compute capacity can handle concurrent runs.
3.	Parameter isolation — always pass parameters explicitly (don’t rely on static global config).

---

### ✅ Summary


| Feature                           | Supported? | Notes                                                         |
|------------------------------------|:----------:|---------------------------------------------------------------|
| Multiple runs of same bundle job   | ✅         | Enable “concurrent runs”                                      |
| Different parameters per run       | ✅         | Pass via `run-now` or Workflow parameters                     |
| Parallel tasks within one run      | ✅         | Use independent `depends_on` configuration                    |
| Safe if sharing Delta tables       | ⚠️         | Only if logic isolates by partition or checkpoint             |




---

##  Multiple Pipeline Bundles  - Reuse the Same Compute Cluster


Excellent — this is an advanced and very common Databricks deployment scenario:

you have multiple pipeline bundles deployed to the Workflow space, and you want them all to reuse the same compute cluster, either in parallel or sequentially, without manually pre-creating a cluster in the UI.


---

### 🧭 Goal

You want to:
1.	Deploy multiple Databricks bundles (pipelines) as Workflows (jobs).
2.	Share the same cluster configuration — not a manually created cluster.
3.	Allow parallel or sequential execution.
4.	Configure everything in the YAML bundle config, not the UI.

---

### 🧩 Background: Cluster options in bundle workflows

In Databricks Workflow (Job) YAML (used by bundles), you have two ways to specify compute:

**Option 1 — new_cluster**

Creates an ephemeral cluster per job run, managed automatically by Databricks.
✅ Easiest and fully automated
❌ Each job run spins up its own cluster (no sharing)

```yaml
job_clusters:
  - job_cluster_key: default_cluster
    new_cluster:
      spark_version: 15.3.x-scala2.12
      node_type_id: i3.xlarge
      num_workers: 2
```


**Option 2 — existing_cluster_id**

Reuses an existing cluster (interactive or persistent).
✅ Enables sharing across multiple pipelines
✅ Can run in parallel or sequentially
❌ You must know the cluster ID — but you can inject it via variables or parameters

```yaml
tasks:
  - task_key: run_pipeline
    existing_cluster_id: "{{bundle.parameters.shared_cluster_id}}"
    notebook_task:
      notebook_path: /Repos/.../main_pipeline
```

You can then pass the cluster ID from your environment or a common config file.

---

### 🧠 How to Configure Shared Cluster Without Manual Creation

If you want a shared cluster automatically managed by bundles, you can:

✅ **Approach 1**: Define a shared cluster job in one bundle

Define a “shared-cluster” bundle that creates and keeps a persistent cluster running, then reference its cluster ID dynamically in other bundles.

Example shared-cluster-bundle/databricks.yml:

```yaml
bundle:
  name: shared-cluster

resources:
  clusters:
    shared_compute:
      spark_version: 15.3.x-scala2.12
      node_type_id: i3.xlarge
      autoscale:
        min_workers: 1
        max_workers: 8
```

When deployed, Databricks creates a named cluster (shared_compute) visible in the workspace.
You can then reference its ID or name from other pipeline bundles.

---

✅ **Approach 2**: Parameterize existing_cluster_id in each pipeline bundle

Each pipeline’s YAML can include:

```yaml
bundle:
  name: metrics-pipeline

parameters:
  shared_cluster_id:
    default: "1111-222222-abc123"  # or injected at deploy time

workflows:
  - name: metrics-pipeline-job
    tasks:
      - task_key: main
        existing_cluster_id: "{{bundle.parameters.shared_cluster_id}}"
        notebook_task:
          notebook_path: /Repos/.../run_metrics

```


You can override that parameter per environment (dev/staging/prod):

```bash
databricks bundle deploy --environment prod \
  --var shared_cluster_id=1111-222222-abc123
```


All bundles that use that same parameter value will bind to the same cluster.

---

✅ **Approach 3**: Use job_clusters + Reusable Cluster Definition YAML Include

You can centralize cluster configuration in a shared YAML include file, e.g. includes/cluster.yml:

```yaml
job_clusters:
  - job_cluster_key: shared_cluster
    new_cluster:
      spark_version: 15.3.x-scala2.12
      node_type_id: i3.xlarge
      autoscale:
        min_workers: 2
        max_workers: 8
```

Then, in each pipeline’s databricks.yml:

```yaml
includes:
  - ../includes/cluster.yml

workflows:
  - name: pipeline-A
    job_clusters:
      - ${job_clusters.shared_cluster}
    tasks:
      - task_key: taskA
        job_cluster_key: shared_cluster
```

This ensures all bundles use identical cluster definitions.
Each workflow run creates its own ephemeral cluster — but with identical config, ensuring consistency (not the same instance though).


---


### ⚙️ Parallel vs Sequential Control


🔹 **Run in Parallel**

Enable concurrent runs:
```yaml
concurrent_run: ENABLED
```
Now multiple bundles referencing the same cluster can execute simultaneously.

If using existing_cluster_id, multiple tasks can share that cluster concurrently (depending on cluster capacity).


---

🔹 **Run Sequentially**

If you want sequential execution (to avoid contention), you can:
- 	Disable concurrent runs:
```yaml
concurrent_run: DISABLED

```
- 	Or chain jobs using depends_on or job triggers (Workflow chaining).


---


### 💡 Recommended Practical Setup

Here’s a clean, automated multi-bundle setup pattern:

```text
/shared/cluster_bundle/databricks.yml
/pipelineA/databricks.yml
/pipelineB/databricks.yml
```

**1. /shared/cluster_bundle/databricks.yml**

```yaml
bundle:
  name: shared-cluster

resources:
  clusters:
    shared_compute:
      spark_version: 15.3.x-scala2.12
      node_type_id: i3.xlarge
      autoscale:
        min_workers: 2
        max_workers: 10

```

Deploy once:
```bash
databricks bundle deploy --bundle shared-cluster
```

Obtain cluster ID:
```bash
databricks clusters list | grep shared_compute
```


**2. /pipelineA/databricks.yml**

```yaml
bundle:
  name: pipelineA

parameters:
  shared_cluster_id:
    default: "1111-222222-abc123"

workflows:
  - name: pipelineA-job
    tasks:
      - task_key: pipelineA_main
        existing_cluster_id: "{{bundle.parameters.shared_cluster_id}}"
        notebook_task:
          notebook_path: /Repos/.../pipelineA_entry
```

Same for /pipelineB/databricks.yml.

Then both can be started:
```bash
databricks jobs run-now --job-id <pipelineA-job-id>
databricks jobs run-now --job-id <pipelineB-job-id>

```
Both run in parallel on the shared cluster.

---

### ✅ Summary

### Practical Goals & Configuration Summary

| Goal                                   | Configuration Approach                                                                                  |
|---------------------------------------- |--------------------------------------------------------------------------------------------------------|
| Run multiple bundles on same cluster    | Use `existing_cluster_id` parameter shared across bundles                                               |
| Avoid manual cluster creation           | Define cluster in a shared bundle (`resources.clusters`) or via YAML includes                          |
| Run in parallel                        | Set `concurrent_run: ENABLED` in workflow/job configuration                                            |
| Run sequentially                       | Set `concurrent_run: DISABLED` or use `depends_on` for workflow chaining                               |
| Centralize cluster config               | Use YAML includes for cluster definition or maintain a dedicated shared cluster bundle                  |


---

##  Controller-Orchestrator Workflow


Perfect — you’re describing a controller-orchestrator workflow pattern in Databricks Workflows (Jobs) that:

1.	Defines a main workflow that orchestrates several external pipeline jobs (bundles).
2.	Runs those external jobs in parallel or sequentially, controlled via configuration.
3.	Uses a shared compute cluster, whose cluster_id is passed as a parameter to all downstream pipelines.

Let’s design this properly and show you a complete implementation example.

---

### 🧠 Architecture Overview


```text
Main Orchestrator Job (in workflow space)
│
├── Task 1 → runs external pipeline A (bundle A)
├── Task 2 → runs external pipeline B (bundle B)
├── Task 3 → runs external pipeline C (bundle C)
│
└── Shared cluster across all
    (created by orchestrator, cluster_id passed as param)
```



---

### 🧩 High-Level Flow

1.	Main workflow starts
  - Creates or identifies a shared job cluster.
  - Stores its cluster_id.
2.	Each task in the main workflow calls the Databricks API (or databricks bundle run)
  - Triggers an external pipeline job.
  - Passes shared_cluster_id and any other parameters.
3.	Tasks can be parallel or sequential using depends_on.
4.	External jobs (pipeline bundles) use existing_cluster_id: "{{bundle.parameters.shared_cluster_id}}" to attach to the shared cluster.

---


### ✅ Example Implementation


**1. Shared Cluster Definition**

```yaml
# includes/shared_cluster.yml
resources:
  clusters:
    shared_cluster:
      spark_version: 15.3.x-scala2.12
      node_type_id: i3.xlarge
      autoscale:
        min_workers: 2
        max_workers: 8
```


**2. External Pipeline Bundles (A, B, C)**

Each external pipeline (pipelineA, pipelineB, etc.) uses the shared cluster ID parameter.

Example: pipelineA/databricks.yml


```yaml
bundle:
  name: pipelineA

parameters:
  shared_cluster_id:
    default: ""

workflows:
  - name: pipelineA-job
    tasks:
      - task_key: pipelineA_main
        existing_cluster_id: "{{bundle.parameters.shared_cluster_id}}"
        notebook_task:
          notebook_path: /Repos/pipelines/pipelineA/main_notebook
          base_parameters:
            run_date: "{{bundle.parameters.run_date}}"
```

Same pattern for pipelineB and pipelineC.


**3. Main Orchestrator Bundle**

File: /orchestrator/databricks.yml

```yaml
bundle:
  name: orchestrator-pipeline

includes:
  - ../includes/shared_cluster.yml

parameters:
  run_mode:
    default: "parallel"   # or "sequential"
  run_date:
    default: "2025-10-15"

workflows:
  - name: orchestrator-job
    job_clusters:
      - job_cluster_key: shared_cluster
        new_cluster:
          spark_version: 15.3.x-scala2.12
          node_type_id: i3.xlarge
          autoscale:
            min_workers: 2
            max_workers: 8

    tasks:
      - task_key: prepare
        job_cluster_key: shared_cluster
        notebook_task:
          notebook_path: /Repos/orchestrator/prepare_cluster
          base_parameters:
            action: "init"
        # This task can collect cluster_id dynamically if needed

      - task_key: run_pipelineA
        job_cluster_key: shared_cluster
        notebook_task:
          notebook_path: /Repos/orchestrator/trigger_external_job
          base_parameters:
            target_job: "pipelineA-job"
            run_date: "{{bundle.parameters.run_date}}"

      - task_key: run_pipelineB
        job_cluster_key: shared_cluster
        notebook_task:
          notebook_path: /Repos/orchestrator/trigger_external_job
          base_parameters:
            target_job: "pipelineB-job"
            run_date: "{{bundle.parameters.run_date}}"

      - task_key: run_pipelineC
        job_cluster_key: shared_cluster
        notebook_task:
          notebook_path: /Repos/orchestrator/trigger_external_job
          base_parameters:
            target_job: "pipelineC-job"
            run_date: "{{bundle.parameters.run_date}}"

      - task_key: finalize
        job_cluster_key: shared_cluster
        depends_on:
          - run_pipelineA
          - run_pipelineB
          - run_pipelineC
        notebook_task:
          notebook_path: /Repos/orchestrator/finalize
```

**4. Trigger External Jobs Notebook**

File: /Repos/orchestrator/trigger_external_job
Python code to call other workflow jobs via REST API:

```python
# Databricks notebook source
import requests
import json
import os

dbutils.widgets.text("target_job", "")
dbutils.widgets.text("run_date", "")
target_job = dbutils.widgets.get("target_job")
run_date = dbutils.widgets.get("run_date")

# You can inject your shared cluster id from Databricks context if known
shared_cluster_id = dbutils.notebook.entry_point.getDbutils().notebook().getContext().tags().apply("jobClusterId")

workspace_url = os.environ["DATABRICKS_HOST"]
token = os.environ["DATABRICKS_TOKEN"]

run_url = f"{workspace_url}/api/2.1/jobs/run-now"
payload = {
    "job_id": target_job,
    "notebook_params": {
        "shared_cluster_id": shared_cluster_id,
        "run_date": run_date
    }
}

headers = {"Authorization": f"Bearer {token}"}
response = requests.post(run_url, headers=headers, json=payload)
print(response.json())

```

Each orchestrator task runs this notebook to trigger an external pipeline job.

---

**5. Control Parallel vs Sequential Execution**

You can make this dynamic in the orchestrator YAML:
```yaml
      - task_key: run_pipelineB
        job_cluster_key: shared_cluster
        depends_on: 
          {{ "['run_pipelineA']" if bundle.parameters.run_mode == "sequential" else "[]" }}
```

or programmatically in Python (if generating jobs via API).

---

**6. Execution Flow**

**Sequential mode**

```text
prepare → pipelineA → pipelineB → pipelineC → finalize
```

**Parallel mode**

```text
prepare → [pipelineA, pipelineB, pipelineC run together] → finalize
```

---

### 🚀 End-to-End Flow Summary



| Step | Action                                         | Runs On             |
|------|------------------------------------------------|---------------------|
| 1    | Main orchestrator starts shared cluster         | Workflow cluster    |
| 2    | Orchestrator triggers external pipeline jobs (A, B, C) | Each uses `existing_cluster_id` |
| 3    | Pipelines execute in parallel or sequentially  | Same shared cluster |
| 4    | Finalization task collects results             | Same shared cluster |


---

### ⚡ Best Practices

1.	Use environment parameters (--var shared_cluster_id) to inject shared cluster dynamically.
2.	Store cluster ID in orchestrator’s context or Databricks Secrets if needed for retries.
3.	Handle job result polling in orchestrator if you need to ensure downstream steps wait.
4.	Enable concurrent_run: ENABLED in external jobs.
5.	Avoid writing to the same Delta paths unless partitioned by pipeline or date.

---

### ✅ Result

You now have:
- 	A single orchestrator workflow that can launch multiple Databricks pipeline bundles (external jobs).
- 	Shared compute cluster managed automatically.
- 	Configurable parallel or sequential execution.
- 	Fully declarative YAML configuration — no manual cluster setup required.

---

