

## Scala Data Types

Below is a clean, practical guide to when you should use object, class, case class, trait, abstract class, enum, sealed trait, etc. This is the version senior Scala/Spark engineers use in real systems.


---

### ✅ 1. object — Singleton, utilities, constants, factories


Use when you need exactly one instance.

Common Use Cases


| Use Case | Example |
|----------|---------|
| Global utilities / helper functions | `object StringUtils { def clean(s: String) = ... }` |
| Constants | `object Config { val Timeout = 30 }` |
| Entry point | `object Main extends App { ... }` |
| Companion for a class | `object User { def apply(...) = ... }` |
| Spark code patterns | `object MyJob { def main(args: Array[String]) }` |


When not to use
- If you expect multiple instances ⇒ use class instead.


---

### ✅ 2. class – Standard object you instantiate

Use when you need multiple independent objects with state.

Common Use Cases

| Use Case | Example |
|----------|---------|
| Business logic with parameters | `class Connection(url: String)` |
| Stateful objects | API clients, caches |
| Dependency injection targets | services, repositories |

When not
- If class only holds data ⇒ use case class.


---

### ✅ 3. case class – Immutable data / DTO / model


Use when you need data structures with:
- auto equals / hashCode
- auto toString
- auto immutability
- easy pattern matching
  
Common Use Cases

| Use Case | Example |
|----------|---------|
| Spark row-level data model | `case class User(id: Long, name: String)` |
| Config structures | `case class JobConfig(...)` |
| API request/response DTOs | JSON case classes (Circe, Spray, etc.) |
| Pattern matching return types | AST, results |

When not
- If mutable or logic-heavy ⇒ use class.


---

### ✅ 4. trait – Behavior/mixin, capability, shared interface


Use when you need an interface or behavior that multiple classes can mix in.

Common Use Cases

| Use Case | Example |
|----------|---------|
| Capability ("has logging") | `trait Logging { def log(msg: String) }` |
| Polymorphic interface | `trait Shape { def area: Double }` |
| Spark job modules | `trait Reader { def read(): DataFrame }` |
| Cross-cutting reusable behavior | retry logic, caching, validation |

When not
- If you need constructor parameters → use abstract class or class.


---

### ✅ 5. abstract class – Base class with constructor parameters

Use when:
- you want inheritance
- need a constructor with parameters
- want partially implemented methods
- but also want constraints

Common Use Cases

| Use Case | Example |
|----------|---------|
| Base class for services | `abstract class Processor(config: Config)` |
| Framework plugin systems | Spark custom rules, connectors |
| Classes providing partial behavior | open/close, setup/teardown |

When to prefer trait instead
- If no constructor parameters → trait is cleaner.


---

### ✅ 6. enum (Scala 3) – Fixed number of values

Use when you need:
- limited choices
- modeling finite states
- safe, type-checked variants

Common Use Cases

| Use Case | Example |
|----------|---------|
| Status codes | `enum Status { case OK, Error }` |
| Workflow states | `enum State { Idle, Running, Failed }` |
| Mode selection | `enum Mode { Dev, Prod }` |


When not
- If variants need fields or behavior and grow complex → use sealed trait + case classes.


---

### ✅ 7. sealed trait / sealed abstract class – ADT / algebraic data types

Use for exhaustive pattern matching and modeling variant types.

This is more powerful than enum.

Common Use Cases

| Use Case | Example |
|----------|---------|
| Domain modeling | `sealed trait Event; case class Click(...); case class View(...)` |
| Compiler AST | expressions, statements |
| API responses with different types | success/failure hierarchy |
| Finite but extensible hierarchies | different message/event types |

---

### 🚦 Quick Decision Table

| You need… | Use |
|-----------|-----|
| Exactly one instance | `object` |
| Many instances with mutable or logical behavior | `class` |
| Data holder, immutability, pattern match | `case class` |
| Multiple inheritance / mix-ins | `trait` |
| Base class with constructor params | `abstract class` |
| Small finite set of values | `enum` |
| Complex finite hierarchy, ADTs | `sealed trait` + `case classes` |


---

### 🎯 Practical Spark-Specific Guidance

| Situation | Best Choice |
|-----------|-------------|
| Schema for Dataset / typed DataFrame | `case class` |
| Jobs with parameters | `class` + `object` companion |
| Shared job utilities | `object` |
| Shared behavior (logging, retry, audit) | `trait` |
| State machines (pipeline states) | `enum` |
| Input/output domain events | `sealed trait` + `case classes` |


---


Nice — here are compact, ready-to-use Scala examples for the Spark-specific patterns from the cheat-sheet. Each example includes a short explanation and a small, practical snippet you can drop into a Spark project.


### 1) case class — typed Dataset / schema model

Use for typed Dataset[T], schema definition and pattern matching.

```scala
// file: models.scala
case class User(userId: Long, name: String, email: String, country: String)

// usage in a Spark app
import org.apache.spark.sql.SparkSession
import spark.implicits._   // for toDS / encoders

val spark = SparkSession.builder.appName("CaseClassExample").getOrCreate()
import spark.implicits._

val users = Seq(
  User(1, "Alice", "alice@example.com", "US"),
  User(2, "Bob", "bob@example.com", "CA")
).toDS()

// typed transformations
val usUsers = users.filter(_.country == "US")
usUsers.show()
```

Why: gives compile-time schema, easy toDS()/as[User], safe .filter, works great as schema for writes to Parquet/Delta.


---

### 2) class + object companion — Spark job with params

Use a class to hold configurable behavior and an object with main to bootstrap.


```scala
// file: jobs/UserEnrichmentJob.scala
import org.apache.spark.sql.{DataFrame, SparkSession}

class UserEnrichmentJob(spark: SparkSession, apiEndpoint: String) {
  def enrich(users: DataFrame): DataFrame = {
    // pretend to call external service; here we add a constant column
    users.withColumn("enriched_by", org.apache.spark.sql.functions.lit(apiEndpoint))
  }
}

object UserEnrichmentJob {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder.appName("UserEnrichmentJob").getOrCreate()
    val inputPath = args.lift(0).getOrElse("/tmp/users")
    val apiEndpoint = args.lift(1).getOrElse("https://api.example.com")

    val input = spark.read.parquet(inputPath)
    val job = new UserEnrichmentJob(spark, apiEndpoint)
    val out = job.enrich(input)
    out.write.mode("overwrite").parquet("/tmp/enriched_users")
    spark.stop()
  }
}
```

Why: separates configuration/ dependencies (class) from the launch/CLI (object).


---

### 3) object — utilities / shared helpers

Singleton utilities for reuse across jobs.


```scala
// file: utils/SparkUtils.scala
import org.apache.spark.sql.{DataFrame, SaveMode}

object SparkUtils {
  def writeDelta(df: DataFrame, fullTableName: String, mode: SaveMode = SaveMode.Append): Unit = {
    df.write.format("delta").mode(mode).saveAsTable(fullTableName)
  }

  def readParquet(path: String)(implicit spark: org.apache.spark.sql.SparkSession) =
    spark.read.parquet(path)
}
```

**Usage**:


```scala
import SparkUtils._
implicit val spark = SparkSession.builder.getOrCreate()
val df = readParquet("/tmp/users")
writeDelta(df, "catalog.schema.users")
```

Why: centralizes common I/O, avoids boilerplate, easy to test for behavior.

---

### 4) trait — cross-cutting behavior (logging, retry)

Define reusable behaviors you can mix into jobs/services.


```scala
// file: traits/LoggingRetry.scala
import org.slf4j.LoggerFactory
import scala.util.{Try, Failure, Success}
import scala.concurrent.duration._

trait Logging {
  protected val logger = LoggerFactory.getLogger(this.getClass)
}

trait Retry { self: Logging =>
  def withRetry[T](retries: Int = 3, delay: FiniteDuration = 1.second)(fn: => T): T = {
    var lastEx: Throwable = null
    var i = 0
    while (i < retries) {
      try return fn
      catch {
        case e: Throwable =>
          lastEx = e
          logger.warn(s"Attempt ${i+1} failed: ${e.getMessage}")
          Thread.sleep(delay.toMillis)
      }
      i += 1
    }
    throw lastEx
  }
}
```

**Mix-in example**:


```scala
class ExternalCaller extends Logging with Retry {
  def callApi(): String = withRetry(3) {
    // call a flaky external service
    if (scala.util.Random.nextDouble() < 0.7) throw new RuntimeException("fail")
    "ok"
  }
}
```

Why: keeps cross-cutting concerns separate and reusable across classes.

---

### 5) enum (Scala 3) — state machine / fixed modes

If you’re on Scala 3, use enum. If on Scala 2, prefer sealed trait (next example).


```scala
// Scala 3
enum JobState {
  case Pending, Running, Success, Failed
}

def handleState(s: JobState): String = s match {
  case JobState.Pending => "scheduled"
  case JobState.Running => "in-progress"
  case JobState.Success => "done"
  case JobState.Failed  => "retry"
}
```

If using Scala 2.x, implement the same with sealed trait + case objects.

Why: clear, type-safe state enumeration; exhaustive pattern matching helps avoid bugs.

---

### 6) sealed trait + case class — ADT for domain events / responses

Model a family of related events or responses; excellent for pattern matching and serialization.


```scala
// file: events.scala
sealed trait JobEvent
case class JobStarted(jobId: String, at: Long) extends JobEvent
case class JobProgress(jobId: String, percent: Int) extends JobEvent
case class JobCompleted(jobId: String, at: Long) extends JobEvent
case class JobFailed(jobId: String, reason: String, at: Long) extends JobEvent

// usage: pattern match on events
def handleEvent(e: JobEvent): Unit = e match {
  case JobStarted(id, at) => println(s"Started $id at $at")
  case JobProgress(_, pct) => println(s"Progress $pct%")
  case JobCompleted(id, at) => println(s"Completed $id at $at")
  case JobFailed(id, reason, at) => println(s"Failed $id: $reason")
}
```

Why: ADTs are perfect for domain modeling (events, API results, ASTs). They make handling every variant explicit.

---

### Extra: small end-to-end Spark pattern combining several pieces


```scala
// file: app.scala
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._

object MainApp extends App {
  implicit val spark = SparkSession.builder.appName("CombinedExample").getOrCreate()
  import spark.implicits._

  // model (case class)
  case class Order(id: Long, total: Double, country: String)

  // utility object
  object IO {
    def readOrders(path: String) = spark.read.json(path).as[Order]
    def writeOrders(df: org.apache.spark.sql.Dataset[Order], table: String) =
      df.write.format("delta").mode("append").saveAsTable(table)
  }

  // trait example
  trait Audit {
    def audit(msg: String): Unit = println(s"[AUDIT] $msg")
  }

  // job class
  class OrderProcessor(targetTable: String) extends Audit {
    def run(inputPath: String): Unit = {
      val orders = IO.readOrders(inputPath)
      val enriched = orders.map(o => o.copy(total = o.total - 1.0)) // trivial transform
      IO.writeOrders(enriched, targetTable)
      audit(s"Wrote orders to $targetTable")
    }
  }

  val input = args.lift(0).getOrElse("/tmp/orders.json")
  new OrderProcessor("catalog.sales.orders").run(input)
  spark.stop()
}
```

---

### Quick tips & gotchas

- Use case class for schemas and small immutable DTOs. Use class for stateful objects or where you need constructor DI.
- Prefer trait for mix-ins and cross-cutting behaviors; use abstract class only when you need constructor params that traits cannot (or when you want to limit linearization).
- Use sealed trait/ADTs for complex variants needing payloads — better than enums when variants carry data.
- Keep object for singletons, job entry points, and shared stateless utilities.
