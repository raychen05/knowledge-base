
## Watermark history and checkpoint history


Here’s the best-practice approach for handling watermark history and checkpoint history in incremental pipelines. The key is when to record for auditability vs. current state.


### 1️⃣ Watermark History


✅ When to record:

1. At the moment you plan the batch, i.e., before the pipeline starts processing
    - Record the planned version ranges into watermark_history (and update the current watermarks table).
    - This ensures you have a history of what was scheduled to be processed.

2. Optionally, you can also record after the batch finishes to log the final processed range and status.


-*Example Flow**

| Step | Watermark | Watermark History | Description |
|------|-----------|-------------------|-------------|
| 1 | Update watermarks table with PLANNED start/end versions | Append PLANNED record | Pipeline picked up this table for processing |
| 2 | Pipeline processes table | None yet | Data is being processed |
| 3 | Processing finishes successfully | Append COMPLETED/SUCCESS record | Final processed version is logged |
| 4 | Update watermarks table status to COMPLETED | Optional | Current table state reflects latest processed version |


✅ Recommendation: Always record at step 1 for traceability and optionally at step 3 to log completion.

---

### 2️⃣ Pipeline Checkpoint History

✅ When to record:

- Create a new checkpoint record at the start of the batch
    - Status = PENDING or IN_PROGRESS
    - This marks that this batch run started for this pipeline

- Update checkpoint at the end of the batch
    - Status = SUCCESS, FAILED, or RETRY
    - Update metrics like rows_read, rows_written, error_message


-*Example Flow**

| Step | Checkpoint | Description |
|------|------------|-------------|
| 1 | Insert checkpoint: batch_id=X, status=PENDING | Marks the start of pipeline run |
| 2 | Pipeline executes | Metrics collected |
| 3 | Update checkpoint: status=SUCCESS/FAILED | Marks completion with results |

---

### 3️⃣ Why This Order is Important

1. Watermark history at start ensures you can audit what version ranges were planned, even if the pipeline fails.
2. Checkpoint at start ensures you have a record of batch execution intent.
3. Updates at finish allow you to record actual outcome and metrics, completing the audit trail.


---

### ✅ Summary Table


| Object | When to insert | When to update | Status example |
|--------|----------------|----------------|----------------|
| Watermark | Before pipeline starts | After pipeline finishes (optional) | PLANNED → COMPLETED |
| Watermark History | Before pipeline starts | After pipeline finishes (optional) | PLANNED / SUCCESS / FAILED |
| Checkpoint | Before pipeline starts | After pipeline finishes | PENDING → SUCCESS / FAILED / RETRY |


---


## Diagram with a full batch run workflow



Perfect! Let’s design a full batch run workflow with Scala code, showing exactly when to update watermarks, record history, and manage checkpoints. I’ll include a simple diagram in text form and the corresponding Scala functions.


### 1️⃣ Workflow Diagram (Text)

```css
 ┌───────────────────────┐
 │ Start Batch Run       │
 └─────────┬─────────────┘
           │
           ▼
 ┌───────────────────────────────┐
 │ Create Checkpoint (PENDING)   │
 │ Record Watermark History (PLANNED) │
 └─────────┬─────────────┘
           │
           ▼
 ┌───────────────────────────────┐
 │ Pipeline Reads Watermark       │
 │ and Computes Version Range     │
 └─────────┬─────────────┘
           │
           ▼
 ┌───────────────────────────────┐
 │ Should Process Table?          │
 │ (Compare start/end versions)   │
 └───────┬─────────────┘
         │ Yes                     │ No
         │                         ▼
         ▼                         └─ Skip Table
 ┌───────────────────────────────┐
 │ Process Table Incrementally    │
 └─────────┬─────────────┘
           │
           ▼
 ┌───────────────────────────────┐
 │ Update Watermark (COMPLETED)  │
 │ Record Watermark History       │
 └─────────┬─────────────┘
           │
           ▼
 ┌───────────────────────────────┐
 │ Update Checkpoint (SUCCESS / FAILED / RETRY) │
 └───────────────────────────────┘
```

---


### 2️⃣ Scala Wrapper: Full Pipeline Driver

```scala
def runPipelineBatch(
    pipelineName: String,
    tables: Seq[String],
    batchId: String,
    runBy: String
): Unit = {

  import spark.implicits._

  // --- 1️⃣ Create new batch checkpoint ---
  val checkpoint = Checkpoint(
    pipelineName = pipelineName,
    batchId = batchId,
    status = CheckpointStatus.Pending.value,
    updatedBy = runBy
  )
  createCheckpoint(checkpoint)

  tables.foreach { tableName =>

    // --- 2️⃣ Compute version range ---
    val (startV, endV) = computeVersionRange(tableName)

    // --- 3️⃣ Load current watermark ---
    val currentWM = loadWatermark(tableName)

    // --- 4️⃣ Check if table needs processing ---
    if (hasVersionChanged(currentWM, startV, endV)) {

      // --- 5️⃣ Record planned watermark history ---
      recordWatermarkHistory(tableName, startV, endV, WatermarkStatus.Planned, runBy, Some(batchId), None, "PLANNED")

      // --- 6️⃣ Update current watermark table (PLANNED) ---
      updateWatermark(tableName, startV, endV, WatermarkStatus.Planned, runBy)

      try {
        // --- 7️⃣ Process the table incrementally ---
        val df = spark.read.format("delta")
          .option("startingVersion", startV)
          .option("endingVersion", endV)
          .table(tableName)

        // Simulate processing logic here...
        val rows = df.count() // example metric

        // --- 8️⃣ Update current watermark (COMPLETED) ---
        updateWatermark(tableName, startV, endV, WatermarkStatus.Completed, runBy)

        // --- 9️⃣ Record watermark history after processing ---
        recordWatermarkHistory(tableName, startV, endV, WatermarkStatus.Completed, runBy, Some(batchId), None, "COMPLETED")

        // --- 🔟 Update checkpoint metrics and SUCCESS ---
        updateCheckpoint(
          pipelineName,
          batchId,
          CheckpointStatus.Success,
          rowsRead = Some(rows),
          rowsWritten = Some(rows),
          metrics = Map("rows_processed" -> rows.toString),
          updatedBy = runBy
        )

      } catch {
        case e: Exception =>
          // --- Handle failures ---
          updateCheckpoint(
            pipelineName,
            batchId,
            CheckpointStatus.Failed,
            errorMessage = Some(e.getMessage),
            updatedBy = runBy
          )
      }

    } else {
      println(s"Skipping $tableName — no new versions to process.")
    }

  } // end foreach table
}
```

---

### 3️⃣ Key Points

1. Checkpoint at start:
    -Status = PENDING → indicates batch started
2. Watermark history at start:
    -Record planned version ranges
3. Watermark table update at start:
    -Status = PLANNED
4. Decision logic:
    -Compare new vs. current start/end version
    -Skip table if unchanged
5. After processing:
    -Update watermark table = COMPLETED
    -Append watermark history = COMPLETED
    -Update checkpoint = SUCCESS or FAILED with metrics

---

### 4️⃣ Benefits of This Approach


- Full audit trail of what was planned and processed
- Skip unnecessary processing for unchanged tables
- Handles failures gracefully and records them in checkpoint history
- Metrics available per table and batch


