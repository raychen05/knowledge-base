Pipeline Structure



Below is a clean, production-grade extension of your PipelineRunner that:
	•	Reads once using a single watermark
	•	Runs multiple transform tasks on the same extracted DataFrame
	•	Initializes the checkpoint once
	•	Marks completion once (or failure once)
	•	Allows per-task target tables
	•	Supports dry-run
	•	Is safe for partial failure handling

This pattern fits very well with your existing Delta + watermark + checkpoint architecture.

⸻

1️⃣ Define a Task Abstraction

First, define a small task model so each transform is explicit and traceable.


```scala
case class PipelineTask(
    taskName: String,
    transformFunc: DataFrame => DataFrame,
    targetTable: String
)
```

2️⃣ Extended PipelineRunner (Multi-Task, Single Watermark)


```scala
object PipelineRunner {

  def runMultiple(
      pipelineName: String,
      queryConfigPath: String,
      tasks: Seq[PipelineTask],
      dryRun: Boolean = false
  ): Unit = {

    // 1. Start watermark + checkpoint ONCE
    Checkpoints.markRunStarted(pipelineName)

    try {
      // 2. Extract ONCE (single watermark read)
      val rawDF = DeltaReader.readDeltaWithWatermark(queryConfigPath)

      if (rawDF.isEmpty) {
        println(s"No data found for $pipelineName")
        Checkpoints.markCheckpointSkipped(pipelineName)
        return
      }

      // Optional but recommended to avoid re-reads
      val cachedRawDF = rawDF.persist()

      // 3. Run each task
      tasks.foreach { task =>
        println(s"Running task: ${task.taskName}")

        val transformedDF = task.transformFunc(cachedRawDF)

        if (!dryRun) {
          DeltaWriter.writeDelta(transformedDF, task.targetTable)
        }
      }

      // 4. Mark completion ONCE
      Checkpoints.markRunCompleted(pipelineName)

      cachedRawDF.unpersist()

    } catch {
      case e: Throwable =>
        // 5. Mark failure ONCE
        Checkpoints.markRunFailed(pipelineName, Some(e.getMessage))
        throw e
    }
  }
}
```


3️⃣ Example Usage


```scala
PipelineRunner.runMultiple(
  pipelineName = "article_metrics_pipeline",
  queryConfigPath = "/configs/wos/article_metrics.json",
  tasks = Seq(
    PipelineTask(
      taskName = "citations_metrics",
      transformFunc = ArticleCitationsTransform.run,
      targetTable = "dap_wos.article_citations"
    ),
    PipelineTask(
      taskName = "open_access_metrics",
      transformFunc = ArticleOpenAccessTransform.run,
      targetTable = "dap_wos.article_open_access"
    ),
    PipelineTask(
      taskName = "journal_metrics",
      transformFunc = JournalMetricsTransform.run,
      targetTable = "dap_wos.journal_metrics"
    )
  )
)
```



4️⃣ Why This Design Works Well

✅ Single Watermark Semantics
	•	Watermark read once
	•	All derived tables are logically consistent
	•	No risk of partial watermark advancement

✅ Atomic Pipeline Semantics
	•	Either all tasks succeed → watermark advances
	•	Or any task fails → watermark stays intact

✅ Performance-Friendly
	•	One Delta read
	•	Cached DataFrame reused across tasks

✅ Operationally Clean
	•	One checkpoint record per pipeline run
	•	Easy monitoring and replay

⸻

5️⃣ Optional Enhancements (Recommended for You)

Given your larger DLT / Workflow system, you may want:

🔹 Task-level Metrics


```scala
Checkpoints.markTaskStarted(pipelineName, task.taskName)
Checkpoints.markTaskCompleted(pipelineName, task.taskName)
```

🔹 Parallel Task Execution (Careful)

Only safe if:
	•	No shared temp views
	•	No conflicting writes


```scala
tasks.par.foreach { task => ... }
```


🔹 Partial-Failure Strategy
	•	Allow non-critical tasks to fail
	•	Fail pipeline only for critical ones

⸻

6️⃣ Summary

This extension gives you:

✔ Single watermark read
✔ Multiple transforms
✔ Clean checkpoint lifecycle
✔ Strong consistency guarantees
✔ Scales naturally with your Databricks + Delta architecture

If you want, I can next:
	•	Add task-level checkpoint schema
	•	Show parallel execution with failure isolation
	•	Align this with Databricks Workflows task graph
	•	Integrate CDF-based downstream triggers



This is a very good question, and it goes straight to operational-grade pipeline design — especially aligned with how you’re already thinking about checkpoints, watermarks, and Databricks Workflows.

Below is a clean, recoverable, YAML-driven design that:

✔ Defines tasks in job YAML
✔ Runs them through your existing PipelineRunner framework
✔ Uses task-level state so successful tasks are NOT rerun
✔ Advances the watermark only when all tasks succeed
✔ Supports resume-after-failure

⸻

1️⃣ Job YAML: Define Tasks Declaratively

Example: article_metrics_job.yaml


```scala
pipeline:
  name: article_metrics_pipeline
  queryConfigPath: /configs/wos/article_metrics.json

  tasks:
    - taskName: citations_metrics
      transformClass: com.company.transforms.ArticleCitationsTransform
      targetTable: dap_wos.article_citations
      critical: true

    - taskName: open_access_metrics
      transformClass: com.company.transforms.ArticleOpenAccessTransform
      targetTable: dap_wos.article_open_access
      critical: true

    - taskName: journal_metrics
      transformClass: com.company.transforms.JournalMetricsTransform
      targetTable: dap_wos.journal_metrics
      critical: false
```


Key points:
	•	transformClass → loaded dynamically
	•	critical → controls failure behavior
	•	YAML becomes the source of truth

⸻

2️⃣ Task State Table (Core for Recovery)

You need a task-level checkpoint table in Delta.

Example: dap_meta.pipeline_task_runs


```sql
pipeline_name STRING
run_id STRING
task_name STRING
status STRING        -- PENDING | RUNNING | SUCCESS | FAILED
error_message STRING
started_at TIMESTAMP
completed_at TIMESTAMP
```


This is separate from the watermark table.

⸻

3️⃣ Pipeline Execution Flow (High Level)


```script
mark pipeline RUNNING
read watermark ONCE
for each task:
    if task already SUCCESS → SKIP
    else run task
if all critical tasks SUCCESS:
    advance watermark
    mark pipeline SUCCESS
else:
    mark pipeline FAILED
```


4️⃣ Load YAML → Runtime Task Model

```scala
case class TaskConfig(
    taskName: String,
    transformClass: String,
    targetTable: String,
    critical: Boolean
)

case class PipelineConfig(
    name: String,
    queryConfigPath: String,
    tasks: Seq[TaskConfig]
)

```’


YAML loader → PipelineConfig

⸻

5️⃣ Dynamic Transform Loader

Each transform implements a common trait:

```scala
trait PipelineTransform {
  def run(df: DataFrame): DataFrame
}
```

Example:

```scala
object ArticleCitationsTransform extends PipelineTransform {
  override def run(df: DataFrame): DataFrame = {
    // transform logic
  }
}
```


Loader:


```scala
object TransformLoader {
  def load(className: String): PipelineTransform = {
    Class.forName(className)
      .getField("MODULE$")
      .get(null)
      .asInstanceOf[PipelineTransform]
  }
}

```


6️⃣ Enhanced PipelineRunner (Recovery-Aware)


```scala

object PipelineRunner {

  def runFromYaml(config: PipelineConfig, dryRun: Boolean = false): Unit = {

    val pipelineName = config.name
    val runId = Checkpoints.startPipelineRun(pipelineName)

    try {
      // 1. Read watermark ONCE
      val rawDF = DeltaReader.readDeltaWithWatermark(config.queryConfigPath)

      if (rawDF.isEmpty) {
        Checkpoints.markPipelineSkipped(pipelineName, runId)
        return
      }

      val cachedDF = rawDF.persist()

      // 2. Execute tasks with recovery
      config.tasks.foreach { task =>
        if (Checkpoints.isTaskSuccessful(pipelineName, runId, task.taskName)) {
          println(s"Skipping successful task: ${task.taskName}")
        } else {
          runTask(pipelineName, runId, cachedDF, task, dryRun)
        }
      }

      // 3. Validate critical tasks
      if (Checkpoints.allCriticalTasksSucceeded(pipelineName, runId)) {
        Checkpoints.markPipelineCompleted(pipelineName, runId)
      } else {
        throw new RuntimeException("Critical task failure detected")
      }

      cachedDF.unpersist()

    } catch {
      case e: Throwable =>
        Checkpoints.markPipelineFailed(pipelineName, runId, e.getMessage)
        throw e
    }
  }

  private def runTask(
      pipelineName: String,
      runId: String,
      df: DataFrame,
      task: TaskConfig,
      dryRun: Boolean
  ): Unit = {

    Checkpoints.markTaskStarted(pipelineName, runId, task.taskName)

    try {
      val transform = TransformLoader.load(task.transformClass)
      val resultDF = transform.run(df)

      if (!dryRun) {
        DeltaWriter.writeDelta(resultDF, task.targetTable)
      }

      Checkpoints.markTaskSuccess(pipelineName, runId, task.taskName)

    } catch {
      case e: Throwable =>
        Checkpoints.markTaskFailed(pipelineName, runId, task.taskName, e.getMessage)

        if (task.critical) throw e
    }
  }
}
```


7️⃣ Failure Recovery: What Happens in Practice

Scenario
	•	Task A → SUCCESS
	•	Task B → FAILED
	•	Task C → NOT RUN

Restart Job

✔ Watermark is unchanged
✔ Task A → SKIPPED
✔ Task B → RETRIED
✔ Task C → RUNS

This is exactly what you want.

⸻

8️⃣ Why This Beats Databricks “Retry Job”


Approach	Problem
Databricks retry	Re-runs everything
Framework retry	Resumes at failed task
Watermark-first	Data loss risk
Task-first + watermark-last	Safe


9️⃣ Optional Enhancements (Very Relevant for You)

🔹 Parallel Non-Conflicting Tasks

```scala
config.tasks.par.foreach(...)
```

🔹 Idempotent Write Guard


```scala
DeltaWriter.writeIfNotExists(runId, taskName)
```


🔹 Task Dependency Graph


```scala
dependsOn: [citations_metrics]
```


🔹 Retry Policy per Task


```scala
retries: 3
retryBackoffSeconds: 60
```

🔟 Final Recommendation (Best Practice)

For your DAP / Delta / Workflow system:

✔ YAML defines structure
✔ Framework controls execution
✔ Task-level checkpoints enable recovery
✔ Watermark advances last
✔ Works perfectly with Databricks Workflows

⸻

If you want, next I can:
	•	Design the checkpoint table schemas
	•	Add task DAG dependencies
	•	Align this with Databricks Jobs YAML
	•	Show parallel execution safety rules
	•	Integrate CDF downstream triggers






