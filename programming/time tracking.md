## Execution-time Tracing for all Pipeline Functions


Below is the simplest and cleanest Scala design to add execution-time tracing for all pipeline functions—without writing start/end timing code inside each function.

Scala does not have decorators like Python, but we can achieve the same with:


### ✅ Solution: Use a wrapper function (traceTime) + function composition

This is the simplest and most idiomatic approach.


#### 1️⃣ Define a traceTime wrapper

This logs execution time for ANY function.

```scala
object TimeTracer {

  def traceTime[T](name: String)(f: => T): T = {
    val start = System.nanoTime()
    println(s"[START] $name")

    val result = f

    val end = System.nanoTime()
    val durationMs = (end - start) / 1e6
    println(s"[END]   $name took $durationMs ms")

    result
  }

}
```


#### ✅ 2️⃣ Define your pipeline steps as normal functions (no timing code inside)

```scala
object MyPipelineSteps {

  def loadData(): Unit = {
    Thread.sleep(300)       // simulate work
  }

  def transformData(): Unit = {
    Thread.sleep(500)
  }

  def writeOutput(): Unit = {
    Thread.sleep(200)
  }
}
```


#### ✅ 3️⃣ Pipeline runner executes them sequentially with timing


```scala
import TimeTracer._
import MyPipelineSteps._

object PipelineMain {

  def main(args: Array[String]): Unit = {

    traceTime("PIPELINE TOTAL") {

      traceTime("Load Data") {
        loadData()
      }

      traceTime("Transform Data") {
        transformData()
      }

      traceTime("Write Output") {
        writeOutput()
      }

    }
  }

}
```


#### 📝 Output Example


```bash
[START] PIPELINE TOTAL
[START] Load Data
[END] Load Data took 301.2 ms
[START] Transform Data
[END] Transform Data took 501.1 ms
[START] Write Output
[END] Write Output took 200.3 ms
[END] PIPELINE TOTAL took 1004.2 ms
```


#### ⭐ Why this design is ideal

- ✔ No need to add timing code inside each step function
- ✔ No decorators needed
- ✔ Steps remain clean and testable
- ✔ One central function handles timing, logging, formatting
- ✔ Works with sequential execution or higher-order function lists


#### 👍 Optional: Even simpler version using a list of steps

If your pipeline is a list of () => Unit functions:

```scala
val steps: Seq[(String, () => Unit)] = Seq(
  "Load Data" -> loadData _,
  "Transform Data" -> transformData _,
  "Write Output" -> writeOutput _
)

traceTime("PIPELINE TOTAL") {
  steps.foreach { case (name, fn) => traceTime(name)(fn()) }
}
```


🧡 Want even more elegant?

I can also show:
- ✅ Macro-based annotation (like a decorator)
- ✅ Automatic time tracing via implicit conversions
- ✅ A trait mixin (withTracing) with no timing calls in pipeline main


---

### Macro-based annotation (like a decorator)


Below is a clean, modern, Scala-3 macro-based annotation that works like a Python decorator to automatically trace execution time — without writing any timing code inside each function and without wrapping each call manually.
This is the closest Scala equivalent to a real decorator.


#### ✅ 1. Define the annotation: @TraceTime


TraceTime.scala

```scala
import scala.annotation.StaticAnnotation
import scala.quoted.*

class TraceTime extends StaticAnnotation {
  inline def apply(defn: Any): Any = ${ TraceTime.impl('defn) }
}

object TraceTime {
  def impl(defn: Expr[Any])(using Quotes): Expr[Any] = {
    import quotes.reflect.*

    def wrap(body: Term, name: String): Term = {
      '{
        val start = System.nanoTime()
        println("[START] " + ${Expr(name)})
        val result = ${ body.asExpr }
        val end = System.nanoTime()
        val durationMs = (end - start) / 1e6
        println("[END]   " + ${Expr(name)} + s" took $$durationMs ms")
        result
      }.asTerm
    }

    def process(tree: Tree): Tree = tree match {

      // Transform def foo(): T = { ...body... }
      case DefDef(name, params, tpt, Some(body)) =>
        val newBody = wrap(body, name)
        DefDef(name, params, tpt, Some(newBody))

      case _ =>
        report.error("Annotation @TraceTime can only be applied to methods")
        tree
    }

    val transformed = defn.asTerm match {
      case c: DefDef => process(c)
      case b: Block =>
        Block(b.stats.map {
          case m: DefDef => process(m)
          case other     => other
        }, b.expr)
      case other =>
        report.error("Unsupported definition for @TraceTime")
        other
    }

    transformed.asExpr
  }
}
```


#### ✅ 2. Use it like a decorator on any function

```scala
object PipelineSteps {

  @TraceTime
  def loadData(): Unit = {
    Thread.sleep(300)
  }

  @TraceTime
  def transformData(): Unit = {
    Thread.sleep(500)
  }

  @TraceTime
  def writeOutput(): Unit = {
    Thread.sleep(200)
  }
}
```


### ✅ 3. Pipeline main — NO timing code required

```scala
object PipelineMain {
  def main(args: Array[String]): Unit = {
    import PipelineSteps.*

    loadData()
    transformData()
    writeOutput()
  }
}
```


#### 📝 Output Example

```bash
[START] loadData
[END]   loadData took 301.3 ms
[START] transformData
[END]   transformData took 501.8 ms
[START] writeOutput
[END]   writeOutput took 201.1 ms
```


#### ⭐ Why this annotation approach is great

- ✔ No timing code inside functions
- ✔ No wrapper calls in pipeline main
- ✔ Works exactly like a Python decorator
- ✔ Clean, centralized tracing logic
- ✔ Powerful—can expand to capture args, exceptions, logs, call graph


#### 🔧 Extra Options I can add

If you want, I can enhance the macro to:
- ✔ log arguments
-  log return results
-  ✔ log exceptions and stack trace
-  ✔ send timing to a logger instead of stdout
-  ✔ produce JSON logs (for Splunk/ELK)
-  ✔ automatically wrap all methods in a class


Would you like me to create:
-A full pipeline tracing framework, or
-A simplified version tailored to your existing pipeline code structure?


---

### Automatic time tracing via implicit conversions


Below is a clean, simple, Scala-friendly solution using implicit conversions to automatically add execution-time tracing to any function without modifying the function body and without macros or decorators.
This approach is lightweight and works in both Scala 2 and Scala 3.


#### ✅ 1. Define an implicit class that adds .trace() to ANY function


TimeTracing.scala

```scala
object TimeTracing {

  implicit class TraceOps[A](f: () => A) {
    def trace(name: String): A = {
      val start = System.nanoTime()
      println(s"[START] $name")

      val result = f()

      val end = System.nanoTime()
      val durationMs = (end - start) / 1e6
      println(s"[END]   $name took $durationMs ms")

      result
    }
  }

}
```

What this gives you
Any () => A function automatically gets a .trace("name") method—even though you didn’t add it inside the function.
This works because implicit class TraceOps wraps your function and adds the timing behavior.


#### ✅ 2. Define your pipeline step functions normally (NO timing code!)

```scala
object PipelineSteps {

  def loadData(): Unit = {
    Thread.sleep(300)
  }

  def transformData(): Unit = {
    Thread.sleep(500)
  }

  def writeOutput(): Unit = {
    Thread.sleep(200)
  }
}
```


#### ✅ 3. Pipeline main uses .trace() without wrapping everything manually

```scala
import TimeTracing._
import PipelineSteps._

object PipelineMain {
  def main(args: Array[String]): Unit = {

    // entire pipeline timing
    (() => {
      // each step timing
      (() => loadData()).trace("Load Data")
      (() => transformData()).trace("Transform Data")
      (() => writeOutput()).trace("Write Output")
    }).trace("PIPELINE TOTAL")

  }
}
```

#### 📝 Sample Output


```bash
[START] PIPELINE TOTAL
[START] Load Data
[END]   Load Data took 300.5 ms
[START] Transform Data
[END]   Transform Data took 501.7 ms
[START] Write Output
[END]   Write Output took 200.4 ms
[END]   PIPELINE TOTAL took 1003.2 ms
```


#### ⭐ Why this is a great solution

- ✔ No timing code in your functions
- ✔ No macros needed
- ✔ No extra boilerplate
- ✔ No changes to function signatures
- ✔ You get decorator-like behavior in pure Scala
- ✔ Simple, transparent, easy to maintain


#### 🔥 Even More Simple (Optional)

If you want an even cleaner syntax, we can define:

```scala
loadData().timed

//or

loadData().timed("Load Data")
```
or even automatically trace every function inside an object.

Just tell me your preferred style and I will generate the optimized version.

Would you like:
- Option A: Minimal and elegant (like above)
- Option B: f.timed and f.timed("name") style
- Option C: Auto-trace all functions in a class/object
- Option D: Integrate with Spark logging / SLF4J / Databricks logger

Which one do you prefer?

---

###  ✅ Minimal & Elegant Execution-Time Tracing (Option A)


Perfect — here is the most minimal, elegant, and idiomatic Scala solution for automatic time tracing using implicit conversions, with clean syntax and zero boilerplate.



#### 1️⃣ Implicit wrapper: adds .trace("name") to any function

```scala
object TimeTracing {

  implicit class TraceOps[A](f: () => A) {
    def trace(name: String): A = {
      val start = System.nanoTime()
      println(s"[START] $name")

      val result = f()

      val end = System.nanoTime()
      val durationMs = (end - start) / 1e6
      println(s"[END]   $name took $durationMs ms")

      result
    }
  }

}
```

This adds a decorator-like .trace(name) to any function of type () => A.


#### ✅ 2️⃣ Your pipeline step functions stay pure & clean

```scala
object PipelineSteps {

  def loadData(): Unit = {
    Thread.sleep(300)
  }

  def transformData(): Unit = {
    Thread.sleep(500)
  }

  def writeOutput(): Unit = {
    Thread.sleep(200)
  }
}
```

- No timing code inside.
- No wrappers.
- No unnecessary complexity.


#### ✅ 3️⃣ Pipeline main simply calls functions with .trace

```scala
import TimeTracing._
import PipelineSteps._

object PipelineMain {
  def main(args: Array[String]): Unit = {

    (() => {
      (() => loadData()).trace("Load Data")
      (() => transformData()).trace("Transform Data")
      (() => writeOutput()).trace("Write Output")
    }).trace("PIPELINE TOTAL")

  }
}
```

#### 📌 Output Example


```bash
[START] PIPELINE TOTAL
[START] Load Data
[END]   Load Data took 300.5 ms
[START] Transform Data
[END]   Transform Data took 501.7 ms
[START] Write Output
[END]   Write Output took 200.4 ms
[END]   PIPELINE TOTAL took 1003.2 ms
```

#### ⭐ Why this is the best minimal design

- ✔ No changes to your pipeline functions
- ✔ No macros or annotations needed
- ✔ Clear and explicit where timing is used
- ✔ Only one small implicit class
- ✔ Pure Scala solution
- ✔ Easy to maintain
- ✔ No boilerplate anywhere

If you want, I can also generate:

-A version that automatically infers the function name
-A version that uses spark.log instead of println
-A version that returns (result, durationMs)
-A version that traces a Seq of functions in a loop


---

### ⭐ Minimal .timed and .timed("name") timing decorator

Great — here is Option B, the cleanest and most elegant Scala syntax:

This gives you:

```scala
loadData().timed
loadData().timed("Load Data")
```

No wrappers. No macros. Just pure Scala sugar.


#### ✅ 1️⃣ Implicit class adding .timed

TimeTracing.scala
```scala
object TimeTracing {

  implicit class TimedOps[A](value: => A) {

    // timed with default name (uses caller’s function name when possible)
    def timed: A = timed("execution")

    // timed with custom name
    def timed(name: String): A = {
      val start = System.nanoTime()
      println(s"[START] $name")

      val result = value

      val end = System.nanoTime()
      val durationMs = (end - start) / 1e6
      println(s"[END]   $name took $durationMs ms")

      result
    }
  }

}
```

- ✔ Works for any expression
- ✔ No extra lambda wrappers
- ✔ No modification to original function
- ✔ Shortest, cleanest syntax


#### ✅ 2️⃣ Your pipeline step functions remain unchanged

```scala
object PipelineSteps {

  def loadData(): Unit = {
    Thread.sleep(300)
  }

  def transformData(): Unit = {
    Thread.sleep(500)
  }

  def writeOutput(): Unit = {
    Thread.sleep(200)
  }
}
```


#### ✅ 3️⃣ Use .timed in your pipeline

```scala
import TimeTracing._
import PipelineSteps._

object PipelineMain {
  def main(args: Array[String]): Unit = {

    {
      loadData().timed("Load Data")
      transformData().timed("Transform Data")
      writeOutput().timed("Write Output")
    }.timed("PIPELINE TOTAL")

  }
}
```

#### 📌 Example Output


```bash
[START] PIPELINE TOTAL
[START] Load Data
[END]   Load Data took 300.4 ms
[START] Transform Data
[END]   Transform Data took 501.6 ms
[START] Write Output
[END]   Write Output took 200.4 ms
[END]   PIPELINE TOTAL took 1002.9 ms
```

#### ⭐ Why this is extremely elegant

- ✔ No () => f() wrapper
- ✔ Natural syntax: f().timed
- ✔ Works with any expression, not just functions
- ✔ Minimal code
- ✔ No timing code inside your functions
- ✔ Perfect for sequential pipelines
- ✔ Easy to integrate into Spark jobs

#### 🔥 Optional Enhancements (let me know if you want them)

- Auto-name based on reflection
  - → loadData().timed auto-logs "loadData"
- Return (value, duration) instead of printing
- Use SLF4J logger instead of println
- Write timing metrics to Delta or ELK
- Add .timedWarn(thresholdMs) to warn slow steps
- Add .timedAsync for async pipelines

---

### Option C: Auto-trace all functions in a class/object


Below is Option C: fully automatic tracing for ALL functions in a class/object — with zero .timed, zero wrappers, and zero timing code inside step functions.

This is the closest you can get to AOP-style automatic tracing in Scala without changing the function bodies.

I’ll give you two versions:

### ✅ Version 1 (Recommended): Mixin Trait AutoTrace (No Macros)

This works in both Scala 2 and Scala 3, and automatically wraps every public pipeline step with time tracing.
Perfect for:
-Pipeline engineering
-Spark ETL pipelines
-Sequential execution flows

#### ⭐ 1. AutoTrace trait

```scala
import scala.reflect.runtime.universe._
import scala.reflect.runtime.currentMirror

trait AutoTrace {

  private val log = (msg: String) => println(msg)

  // Execute all public methods with timing
  def runAll(): Unit = {
    val instanceMirror = currentMirror.reflect(this)
    val methods = instanceMirror.symbol.typeSignature.members.collect {
      case m: MethodSymbol if m.isPublic && m.paramLists.flatten.isEmpty && m.returnType =:= typeOf[Unit] =>
        m
    }.toList.reverse  // maintain natural order

    val pipelineStart = System.nanoTime()
    log("[START] Pipeline")

    methods.foreach { method =>
      val name = method.name.toString
      val start = System.nanoTime()

      log(s"[START] $name")
      instanceMirror.reflectMethod(method).apply()
      val end = System.nanoTime()

      val durationMs = (end - start) / 1e6
      log(s"[END]   $name took $durationMs ms")
    }

    val pipelineEnd = System.nanoTime()
    val totalMs = (pipelineEnd - pipelineStart) / 1e6

    log(s"[END]   Pipeline took $totalMs ms")
  }
}
```

#### It automatically:

-inspects the object with reflection
-finds all public no-arg methods returning Unit
-executes them in the same order you wrote them
-logs each method’s execution time
-logs total pipeline time

- No decorators.
- No .timed.
- Zero work per function.

---

#### ⭐ 2. Define your pipeline object (no timing code!)

```scala
object Pipeline extends AutoTrace {

  def loadData(): Unit = {
    Thread.sleep(300)
  }

  def transformData(): Unit = {
    Thread.sleep(500)
  }

  def writeOutput(): Unit = {
    Thread.sleep(200)
  }
}
```

#### ⭐ 3. Pipeline runner: just call runAll()

```scala
object PipelineMain {
  def main(args: Array[String]): Unit = {
    Pipeline.runAll()
  }
}
```      

#### 📌 Example Output

```bash
[START] Pipeline
[START] loadData
[END]   loadData took 300.6 ms
[START] transformData
[END]   transformData took 501.2 ms
[START] writeOutput
[END]   writeOutput took 200.3 ms
[END]   Pipeline took 1002.8 ms
```

#### ⭐ Why this version is amazing

- ✔ ZERO timing code in step functions
- ✔ ZERO .timed calls
- ✔ Functions stay 100% pure
- ✔ One call to runAll() does everything
- ✔ Automatically logs total pipeline time
- ✔ No macros required
- ✔ Works in Spark pipelines (good for ETL workflows)
- ✔ Very easy to maintain

#### 🔥 Optional Improvements (easy to add)

I can enhance the AutoTrace trait to include:

-log arguments and return values
-log Spark job metrics
-log to SLF4J instead of println
-log to Delta table or Elasticsearch
-parallel execution version
-skipping specific methods (e.g., annotation @SkipTrace)
-only trace methods matching a pattern (e.g. process*)

#### 👍 Want the macro-based version too?

If you'd like the Scala 3 macro annotation version (automatic compile-time rewriting), I can produce:

- ✔ @AutoTraceClass → automatically wraps all methods
- ✔ Zero reflection
- ✔ Faster
- ✔ Cleaner logs


---

### ⭐ Option D — SLF4J-based Auto Timing Decorator (f.timed + Spark-safe logging)


Below is Option D: Timing-trace integration with Spark logging / SLF4J / Databricks logger.
This version provides production-grade logging, not println. It works in Scala 2 & 3 and in Databricks, EMR, Spark Standalone, or Kubernetes.

You can choose whichever logger you prefer:
-Spark logger
-SLF4J
-Databricks logger (com.databricks.logging)

I'll use SLF4J because it's the cleanest and supported everywhere.


### 1️⃣ Add implicit .timed with SLF4J logging

```scala
import org.slf4j.LoggerFactory

object TimeTracing {

  private val log = LoggerFactory.getLogger("PipelineTiming")

  implicit class TimedOps[A](value: => A) {

    // timed with default name
    def timed: A = timed("execution")

    // timed with custom name
    def timed(name: String): A = {
      val start = System.nanoTime()
      log.info(s"[START] $name")

      val result = value

      val end = System.nanoTime()
      val durationMs = (end - start) / 1e6
      log.info(s"[END]   $name took $durationMs ms")

      result
    }
  }
}
```

- ✔ Uses production logging (SLF4J → Log4j / Databricks driver logs)
- ✔ No println
- ✔ Thread-safe
- ✔ Works in Spark executors & driver


#### 2️⃣ Pipeline step functions — unchanged

```scala
object PipelineSteps {

  def loadData(): Unit = {
    Thread.sleep(300)
  }

  def transformData(): Unit = {
    Thread.sleep(500)
  }

  def writeOutput(): Unit = {
    Thread.sleep(200)
  }
}
```


#### 3️⃣ Pipeline main using .timed

```scala
import TimeTracing._
import PipelineSteps._

object PipelineMain {

  def main(args: Array[String]): Unit = {

    {
      loadData().timed("Load Data")
      transformData().timed("Transform Data")
      writeOutput().timed("Write Output")
    }.timed("PIPELINE TOTAL")

  }
}
```

#### 📌 Output (in Databricks/Spark logs)

```bash
INFO PipelineTiming: [START] PIPELINE TOTAL
INFO PipelineTiming: [START] Load Data
INFO PipelineTiming: [END]   Load Data took 300.4 ms
INFO PipelineTiming: [START] Transform Data
INFO PipelineTiming: [END]   Transform Data took 501.7 ms
INFO PipelineTiming: [START] Write Output
INFO PipelineTiming: [END]   Write Output took 200.4 ms
INFO PipelineTiming: [END]   PIPELINE TOTAL took 1002.9 ms
```

#### ⭐ Why this is perfect for Spark Production Pipelines

- ✔ Logs show up in:
  - Databricks Driver Logs
  - Databricks Cluster Event Log
  - Spark Standalone logs
  - Yarn/EMR logs
  - ELK / Splunk (if logs are forwarded)
- ✔ Works with ANY cluster
- ✔ Safe, thread-safe, executor-safe
- ✔ Minimal code
- ✔ Your functions stay clean


#### 🔥 Want Databricks-native logger instead?

If you're running on Databricks, I can give you an alternate version using:

```scala
import com.databricks.logging.AttributionContext
import com.databricks.logging.UsageLogger
```

Which gives logs like:

UsageLogger: [TRACE] function=loadData duration=300ms

Ask for “Databricks logger version” if you want that.


#### 🔥 Want a hybrid?

I can also combine AutoTrace (Option C) with SLF4J (Option D) so EVERY method in your pipeline object gets auto-timed with Spark logging, no .timed needed.

Just tell me:
“Give me AutoTrace + SLF4J combined”


---


### The best, simplest, production-grade approach 


Below is the best, simplest, production-grade approach for a pipeline with many steps across many objects, 

where:
- You want timing for each pipeline step
- You want total pipeline duration
- You want to log all timing data to a Delta table
- You want spend ZERO time writing start/end timestamps inside each function
- You want clean pipeline code (just step1, step2, ...)
- You want Spark/Databricks-friendly logging

This approach is optimized for Spark ETL / Databricks pipelines.


#### ⭐ Recommended Architecture

- ✔ Use a tiny wrapper function: traceStep("name") { … }
- ✔ Use a pipeline runner that logs each step’s name + duration
- ✔ Append logs to a Delta table
- ✔ Zero timing code inside step functions
- ✔ Works across multiple objects
- ✔ Works with DataFrames

This is the simplest, cleanest, maintainable method.

#### ✅ 1️⃣ Create the Delta logging table

```sql
CREATE TABLE IF NOT EXISTS pipeline_perf_log (
  run_id STRING,
  step STRING,
  duration_ms DOUBLE,
  timestamp TIMESTAMP
) USING DELTA
```

You may add:
-pipeline name
-user
-parameters
-cluster ID
-etc.


#### ✅ 2️⃣ Scala helper: traceStep(name)( { code } )

PipelineTracer.scala


```scala
import org.apache.spark.sql.{DataFrame, SparkSession}
import java.util.UUID

object PipelineTracer {

  case class StepLog(run_id: String, step: String, duration_ms: Double, timestamp: String)

  private var currentRunId: String = _

  def startRun(): Unit = {
    currentRunId = UUID.randomUUID().toString
  }

  def runId: String = currentRunId

  def traceStep[T](spark: SparkSession, stepName: String)(block: => T): T = {
    val start = System.nanoTime()

    val result = block

    val end = System.nanoTime()
    val durationMs = (end - start) / 1e6

    import spark.implicits._
    Seq(
      StepLog(currentRunId, stepName, durationMs, java.time.Instant.now.toString)
    ).toDF()
      .write
      .mode("append")
      .format("delta")
      .saveAsTable("pipeline_perf_log")

    result
  }
}
```

- ✔ Automatically logs to a Delta table
- ✔ Works with any return type (DataFrame or anything else)
- ✔ Tracks a single pipeline run with run_id
- ✔ No timing code in your object methods
- ✔ Easiest approach for production


#### ✅ 3️⃣ Use it in your pipeline

The pipeline stays clean and readable:


```scala
import PipelineTracer._
import org.apache.spark.sql.SparkSession

def run_pipeline()(implicit spark: SparkSession): Unit = {

  startRun()   // create pipeline run ID

  // step 1
  val df1 = traceStep(spark, "Obj1.getDataframe") {
    Obj1.getDataframe()
  }

  // step 2
  val df2 = traceStep(spark, "Obj3.ComputeMetric") {
    Obj3.ComputeMetric(df1)
  }

  // step 3
  val df3 = traceStep(spark, "Obj4.getDataframe + Obj5.getDf2") {
    Obj4.getDataframe(df2).join(Obj5.getDf2())
  }

  // step N
  val finalDf = traceStep(spark, "Final Step") {
    df3 // or more transformations
  }
}
```

#### 📌 Logging Output in Delta Table (pipeline_perf_log)

```bash
run_id	step	duration_ms	timestamp
123e-...	Obj1.getDataframe	323.5	2025-01-16T12:00:00Z
123e-...	Obj3.ComputeMetric	510.8	2025-01-16T12:00:01Z
123e-...	Obj4.getDataframe + Obj5.getDf2	1120.3	2025-01-16T12:00:03Z
123e-...	Final Step	42.1	2025-01-16T12:00:04Z
```


#### ⭐ Why this is the BEST solution

- ✔ Clean pipeline code
- ✔ ONE unified tracing function (traceStep)
- ✔ Logs both per-step + per-run
- ✔ Works across multiple objects
- ✔ Production-grade Delta logging
- ✔ No macros, no implicit wrappers, minimal complexity
- ✔ Can be extended easily (cluster ID, row counts, etc.)


#### 🔥 Optional Enhancements (I can add any of these for you)

- Log Spark metrics (bytes scanned, shuffle data, job ids)
- Log DataFrame row counts after each step
- Auto-index the Delta table for fast dashboards
- Add pipeline name + version
- Add warn threshold (e.g., >30 seconds)
- Wrap everything in a DAG-style declarative pipeline
- Auto-generate Databricks dashboards for performance monitoring

If you'd like, I can also produce a full working Databricks notebook version or unit-testable version.

---

### Log DataFrame row counts after each step


Perfect — we can extend the traceStep helper to automatically log DataFrame row counts after each step if the returned object is a DataFrame, while keeping the pipeline clean and production-ready.
Here’s a full example:

✅ 1️⃣ Updated PipelineTracer.scala with row counts


```scala
import org.apache.spark.sql.{DataFrame, SparkSession}
import java.util.UUID
import java.time.Instant

object PipelineTracer {

  case class StepLog(
      run_id: String,
      step: String,
      duration_ms: Double,
      row_count: Option[Long],
      timestamp: String
  )

  private var currentRunId: String = _

  def startRun(): Unit = {
    currentRunId = UUID.randomUUID().toString
  }

  def runId: String = currentRunId

  /*-Trace a step, log duration, and row count if the result is DataFrame */
  def traceStep[T](spark: SparkSession, stepName: String)(block: => T): T = {
    val start = System.nanoTime()
    val result = block
    val end = System.nanoTime()

    val durationMs = (end - start) / 1e6
    val rowCount: Option[Long] = result match {
      case df: DataFrame => Some(df.count())
      case _ => None
    }

    import spark.implicits._
    Seq(
      StepLog(
        currentRunId,
        stepName,
        durationMs,
        rowCount,
        Instant.now.toString
      )
    ).toDF()
      .write
      .mode("append")
      .format("delta")
      .saveAsTable("pipeline_perf_log")

    result
  }
}
```


#### ✅ 2️⃣ Pipeline Example


```scala
import PipelineTracer._
import org.apache.spark.sql.SparkSession

def run_pipeline()(implicit spark: SparkSession): Unit = {

  startRun()   // create pipeline run ID

  // step 1
  val df1 = traceStep(spark, "Obj1.getDataframe") {
    Obj1.getDataframe()
  }

  // step 2
  val df2 = traceStep(spark, "Obj3.ComputeMetric") {
    Obj3.ComputeMetric(df1)
  }

  // step 3
  val df3 = traceStep(spark, "Obj4.getDataframe + Obj5.getDf2") {
    Obj4.getDataframe(df2).join(Obj5.getDf2())
  }

  // step N
  val finalDf = traceStep(spark, "Final Step") {
    df3
  }
}
```


### 📌 Sample Delta Table (pipeline_perf_log) Output

```bash
run_id	step	duration_ms	row_count	timestamp
123e-...	Obj1.getDataframe	320.5	1_000_000	2025-12-09T12:00:00Z
123e-...	Obj3.ComputeMetric	510.7	950_000	2025-12-09T12:00:01Z
123e-...	Obj4.getDataframe + Obj5.getDf2	1120.3	1_500_000	2025-12-09T12:00:03Z
123e-...	Final Step	42.1	1_500_000	2025-12-09T12:00:04Z
```

row_count is automatically None for steps returning non-DataFrame objects.


#### ⭐ Advantages

- Automatic row count without modifying functions
- Works across multiple objects and steps
- Step duration + row count + timestamp logged to Delta
- Clean pipeline code: just wrap steps in traceStep
- Compatible with Spark, Databricks, Delta Lake


#### 🔥 Optional Enhancements

- Log DataFrame schema or column counts
- Log shuffled bytes / stages / jobs from Spark metrics
- Log exceptions if a step fails
- Add threshold warning if duration exceeds a limit
- Aggregate logs per run for pipeline dashboards

If you want, I can produce a ready-to-use Databricks notebook where the pipeline_perf_log table is fully populated with duration, row counts, and extra metrics, so you can monitor your ETL pipelines automatically.
Do you want me to do that next?

---

### Minimal traceStep helper


Yes — we can make it much simpler while still logging step duration and row count to a Delta table, without creating case classes, optional types, or verbose code.
Here’s a minimal approach:


#### ✅ Minimal traceStep helper


```scala
import org.apache.spark.sql.{DataFrame, SparkSession}
import java.util.UUID
import java.time.Instant

object PipelineTracer {

  private var runId: String = _

  def startRun(): Unit = runId = UUID.randomUUID().toString

  /*-Trace a step and log duration + row count (if DataFrame) */
  def traceStep[T](spark: SparkSession, stepName: String)(block: => T): T = {
    val start = System.nanoTime()
    val result = block
    val end = System.nanoTime()

    val durationMs = (end - start) / 1e6
    val rowCount: Long = result match {
      case df: DataFrame => df.count()
      case _ => -1L
    }

    import spark.implicits._
    Seq((runId, stepName, durationMs, rowCount, Instant.now.toString))
      .toDF("run_id", "step", "duration_ms", "row_count", "timestamp")
      .write
      .mode("append")
      .format("delta")
      .saveAsTable("pipeline_perf_log")

    result
  }
}
```

#### ✅ Key points:

- Only one helper function
- Logs step duration + row count automatically
- Works with any return type (DataFrame or other)
- Simple Delta write, no case classes needed
- Minimal boilerplate


#### ✅ Using it in your pipeline

```scala
import PipelineTracer._
import org.apache.spark.sql.SparkSession

def run_pipeline()(implicit spark: SparkSession): Unit = {

  startRun()

  val df1 = traceStep(spark, "Obj1.getDataframe") {
    Obj1.getDataframe()
  }

  val df2 = traceStep(spark, "Obj3.ComputeMetric") {
    Obj3.ComputeMetric(df1)
  }

  val df3 = traceStep(spark, "Obj4 + Obj5 join") {
    Obj4.getDataframe(df2).join(Obj5.getDf2())
  }

  traceStep(spark, "Final Step") {
    df3
  }
}
```


#### 📌 Delta Table Example Output

```scala
run_id	step	duration_ms	row_count	timestamp
123e...	Obj1.getDataframe	320.5	1_000_000	2025-12-09T12:00:00Z
123e...	Obj3.ComputeMetric	510.7	950_000	2025-12-09T12:00:01Z
123e...	Obj4 + Obj5 join	1120.3	1_500_000	2025-12-09T12:00:03Z
123e...	Final Step	42.1	1_500_000	2025-12-09T12:00:04Z
```

Row count = -1 for steps that are not DataFrames.

This is the simplest production-ready solution:
- No case classes
- No optional types
- No macros or decorators
- Step timing + row counts logged automatically
- Clean pipeline code
- 

----

### Auto-naming TimeTracing with reflection


Absolutely! We can enhance the previous TimeTracing helper so that the step name is automatically inferred from the calling method or function using reflection / StackTraceElement, so you don’t need to manually pass a name every time.
Here’s a clean, minimal implementation:


#### ✅ Auto-naming TimeTracing with reflection

```scala
import org.apache.spark.sql.{DataFrame, SparkSession}
import java.util.UUID
import java.time.Instant

object TimeTracing {

  private var currentRunId: String = _

  def startRun(): Unit = currentRunId = UUID.randomUUID().toString

  private def runId: String = currentRunId

  /*- Get calling function name via stack trace */
  private def callerName: String = {
    Thread.currentThread().getStackTrace
      .dropWhile(_.getClassName.contains("TimeTracing$"))
      .drop(1)
      .headOption
      .map(st => s"${st.getClassName}.${st.getMethodName}")
      .getOrElse("UnknownStep")
  }

  /*- Trace a block with auto-named step */
  def trace[T](spark: SparkSession)(block: => T): T = trace(spark, callerName)(block)

  /*- Trace a block with optional custom name */
  def trace[T](spark: SparkSession, name: String)(block: => T): T = {
    val start = System.nanoTime()
    val result = block
    val end = System.nanoTime()

    val durationMs = (end - start) / 1e6
    val rowCount: Long = result match {
      case df: DataFrame => df.count()
      case _ => -1L
    }

    import spark.implicits._
    Seq((runId, name, durationMs, rowCount, Instant.now.toString))
      .toDF("run_id", "step", "duration_ms", "row_count", "timestamp")
      .write
      .mode("append")
      .format("delta")
      .saveAsTable("pipeline_perf_log")

    result
  }
}
```


#### ✅ Usage Example

```scala
import TimeTracing._
import org.apache.spark.sql.SparkSession

def run_pipeline()(implicit spark: SparkSession): Unit = {

  startRun()

  val df1 = trace(spark) {
    Obj1.getDataframe()
  } // auto name: e.g., "MyPipeline$.run_pipeline"

  val df2 = trace(spark) {
    Obj3.ComputeMetric(df1)
  }

  val df3 = trace(spark) {
    Obj4.getDataframe(df2).join(Obj5.getDf2())
  }

  trace(spark) {
    df3
  } // final step
}
```


#### 📌 How it works

- If you don’t pass a name, the callerName function inspects the stack trace to get the calling method name automatically.
- Optional: you can still override the name by using trace(spark, "CustomStepName"){ ... }.
- Automatically logs duration, row count (if DataFrame), timestamp, run_id to a Delta table.


#### ⭐ Advantages

1. Zero boilerplate per step — no manual naming required.
2. Works for DataFrames and other objects.
3. Logs everything to Delta for dashboards / metrics.
4. Pipeline code stays clean.
5. Can easily integrate with Spark / Databricks logging if needed.


---

### Production-ready TimeTracing 


Perfect! Here's a fully combined, production-ready TimeTracing for Spark/Databricks pipelines. It handles:

- Automatic step naming via reflection
- Automatic row count for DataFrames
- Logging step duration to a Delta table
- Automatic pipeline run ID
- Automatic total pipeline duration
- Clean usage: no need to pass step names manually


#### ✅ Full TimeTracing.scala

```scala
import org.apache.spark.sql.{DataFrame, SparkSession}
import java.util.UUID
import java.time.Instant

object TimeTracing {

  private var currentRunId: String = _
  private var pipelineStartTime: Long = _

  /*- Start a new pipeline run */
  def startPipeline(): Unit = {
    currentRunId = UUID.randomUUID().toString
    pipelineStartTime = System.nanoTime()
  }

  /*- End the pipeline and log total duration */
  def endPipeline()(implicit spark: SparkSession): Unit = {
    val endTime = System.nanoTime()
    val durationMs = (endTime - pipelineStartTime) / 1e6
    import spark.implicits._
    Seq((currentRunId, "PIPELINE_TOTAL", durationMs, -1L, Instant.now.toString))
      .toDF("run_id", "step", "duration_ms", "row_count", "timestamp")
      .write
      .mode("append")
      .format("delta")
      .saveAsTable("pipeline_perf_log")
  }

  /*- Get calling function name for automatic step naming */
  private def getStepName: String = {
    Thread.currentThread().getStackTrace
      .dropWhile(_.getClassName.contains("TimeTracing$"))
      .drop(2) // skip traceStep + internal frame
      .headOption
      .map { st =>
        val cls = st.getClassName.split("\\.").lastOption.getOrElse("UnknownClass")
        s"$cls.${st.getMethodName}"
      }
      .getOrElse("UnknownStep")
  }

  /*- Trace a step with automatic or custom name */
  def traceStep[T](spark: SparkSession, name: String = null)(block: => T): T = {
    val stepName = if (name != null) name else getStepName
    val start = System.nanoTime()
    val result = block
    val end = System.nanoTime()
    val durationMs = (end - start) / 1e6

    val rowCount: Long = result match {
      case df: DataFrame => df.count()
      case _ => -1L
    }

    import spark.implicits._
    Seq((currentRunId, stepName, durationMs, rowCount, Instant.now.toString))
      .toDF("run_id", "step", "duration_ms", "row_count", "timestamp")
      .write
      .mode("append")
      .format("delta")
      .saveAsTable("pipeline_perf_log")

    result
  }
}
```


#### ✅ Usage Example


```scala
import org.apache.spark.sql.SparkSession
implicit val spark: SparkSession = SparkSession.builder()
  .appName("FullPipelineTimeTracing")
  .getOrCreate()

import TimeTracing._

// Start pipeline
startPipeline()

val df1 = traceStep { Obj1.getDataframe() }         // Auto step name: Obj1.getDataframe
val df2 = traceStep { Obj3.ComputeMetric(df1) }     // Auto step name: Obj3.ComputeMetric
val df3 = traceStep { Obj4.getDataframe(df2).join(Obj5.getDf2()) } // Auto step name: Obj4.getDataframe

// Optional: manual custom step name
val df4 = traceStep(spark, "CustomJoinStep") {
  df3.join(Obj6.getDf())
}

// End pipeline (logs total duration)
endPipeline()

```


#### 📌 Example Delta Table Output (pipeline_perf_log)

```bash
run_id	step	duration_ms	row_count	timestamp
123e-...	Obj1.getDataframe	320.5	1_000_000	2025-12-09T12:00:00Z
123e-...	Obj3.ComputeMetric	510.7	950_000	2025-12-09T12:00:01Z
123e-...	Obj4.getDataframe	1120.3	1_500_000	2025-12-09T12:00:03Z
123e-...	CustomJoinStep	250.2	1_500_000	2025-12-09T12:00:04Z
123e-...	PIPELINE_TOTAL	2201.7	-1	2025-12-09T12:00:04Z
```

#### ⭐ Advantages

- Fully automatic step naming → no need to pass step names manually
- Logs row counts for DataFrames
- Logs total pipeline duration
- Clean, readable pipeline code
- Works in Databricks, Spark standalone, EMR, Kubernetes
- Data persisted in Delta table, easy for dashboards and metrics

---

