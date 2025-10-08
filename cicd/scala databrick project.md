### Hybrid Approach for Scala Databrick project Intef=grated with Unit test


Yes — this is actually the recommended approach for Databricks Scala projects:
keep your core logic in .scala files (version-controlled, testable, reusable),
then call it from a Databricks Scala notebook (.ipynb) for interactive runs or pipeline orchestration.

Here’s how you can do it in the same project:

---

1. Organize Your Project

Example structure:

```text

project-root/
  src/
    main/
      scala/com/example/pipeline/MyPipeline.scala   <-- core logic here
    test/
      scala/com/example/pipeline/MyPipelineTest.scala  <-- unit tests
  notebooks/
    run_pipeline.scala                               <-- Databricks notebook (.ipynb)
  build.sbt

  ```

-	src/main/scala → Core pipeline functions (compiled & tested like normal Scala code).
-	notebooks/ → Databricks notebooks only for execution, visualization, orchestration.


---

2. Define Core Logic in .scala

src/main/scala/com/example/pipeline/MyPipeline.scala:

```scala
package com.example.pipeline

import org.apache.spark.sql.{DataFrame, SparkSession}

object MyPipeline {
  def transformData(df: DataFrame): DataFrame = {
    df.filter("age > 26")
  }
}

```


---


3. Package Logic & Use in Databricks Notebook

Option A: Direct %run approach (Quick, Dev Mode)

-	Export .scala files to Databricks workspace folder:

```bash
databricks workspace import_dir src/main/scala /Workspace/ProjectName/src
```

-	In a Databricks Scala notebook (run_pipeline.ipynb):

```scala
%run /Workspace/ProjectName/src/com/example/pipeline/MyPipeline

val input = Seq(("Alice", 25), ("Bob", 30)).toDF("name", "age")
val result = MyPipeline.transformData(input)
result.show()

```


Option B: Build as JAR (Better for CI/CD & Prod)

1.	Use sbt package:

```bash
sbt package

```

This creates target/scala-2.12/projectname_2.12-0.1.jar.


2.	Upload JAR to Databricks:

```bash
databricks fs cp target/scala-2.12/projectname_2.12-0.1.jar dbfs:/FileStore/jars/
```

3.	Attach JAR to your Databricks cluster in Libraries → Install New → DBFS.
	
4.	Call your function in a notebook:

```scala

import com.example.pipeline.MyPipeline

val input = Seq(("Alice", 25), ("Bob", 30)).toDF("name", "age")
val result = MyPipeline.transformData(input)
result.show()

```

4. CI/CD Workflow
   
- 	Core logic stays in .scala files → tested using sbt test.
- 	Notebook just calls MyPipeline → minimal logic, easier to maintain.
- 	CI/CD exports notebooks and runs tests, but builds pipeline JAR for Databricks deployment.

---

5. Recommended Practice

- 	Dev/Interactive runs → use %run on source files.
- 	Prod pipeline → package as JAR + run as Databricks job for better versioning & reproducibility.
----



### A Complete Sample Databricks Project Template


Got it — I’ll give you a complete sample Databricks project template with:
- 1.	Core logic in .scala
- 2.	Unit tests
- 3.	A Databricks notebook (.ipynb) calling the logic
- 4.	A CI/CD workflow for testing & deployment


This setup works with both local development and Databricks Repos.

---

1. Project Structure

```text

databricks-pipeline/
  build.sbt
  project/
  src/
    main/
      scala/com/example/pipeline/MyPipeline.scala
    test/
      scala/com/example/pipeline/MyPipelineTest.scala
  notebooks/
    RunPipeline.scala
  .github/workflows/ci.yml

```

---

2. build.sbt

```scala

name := "databricks-pipeline"
version := "0.1"
scalaVersion := "2.12.15"

libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-sql" % "3.4.1" % Provided,
  "org.scalatest" %% "scalatest" % "3.2.16" % Test,
  "com.holdenkarau" %% "spark-testing-base" % "3.4.0_1.4.0" % Test
)

Test / fork := true
```

---

3. Core Logic: MyPipeline.scala

```scala
package com.example.pipeline

import org.apache.spark.sql.{DataFrame, SparkSession}

object MyPipeline {
  def transformData(df: DataFrame): DataFrame = {
    df.filter("age > 26")
  }
}

```
---

4. Unit Test: MyPipelineTest.scala

```scala

package com.example.pipeline

import org.scalatest.funsuite.AnyFunSuite
import org.apache.spark.sql.SparkSession

class MyPipelineTest extends AnyFunSuite {
  val spark = SparkSession.builder().master("local[*]").appName("Test").getOrCreate()
  import spark.implicits._

  test("transformData filters age > 26") {
    val input = Seq(("Alice", 25), ("Bob", 30)).toDF("name", "age")
    val result = MyPipeline.transformData(input)
    assert(result.count() == 1)
  }
}
```

Run locally:


```bash
sbt test
```
---

5. Databricks Notebook: RunPipeline.scala

```scala
// Databricks Scala Notebook (.ipynb)
// Either %run the Scala source OR attach JAR built via sbt

import com.example.pipeline.MyPipeline
import org.apache.spark.sql.SparkSession

val spark = SparkSession.builder().getOrCreate()
import spark.implicits._

val input = Seq(("Alice", 25), ("Bob", 30)).toDF("name", "age")
val result = MyPipeline.transformData(input)
result.show()

```
---

6. GitHub Actions CI/CD: .github/workflows/ci.yml

```yaml
name: CI

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Scala
        uses: olafurpg/setup-scala@v12
        with:
          java-version: "temurin:11"
      - name: Run Unit Tests
        run: sbt test
      - name: Package JAR
        run: sbt package
      - name: Upload JAR to Databricks
        run: |
          databricks fs cp target/scala-2.12/databricks-pipeline_2.12-0.1.jar dbfs:/FileStore/jars/ --overwrite

```


---

7. Workflow
   
1.	Local Dev:
- 	Run sbt test for unit tests.
- 	Run notebook with %run or JAR attached.
  
2.	CI/CD:
- 	GitHub Actions runs unit tests & builds JAR.
- 	JAR uploaded to Databricks automatically.

3.	Databricks Job:
- 	Attach JAR to cluster.
- 	Run RunPipeline.scala notebook in a job.


---

I can also make a Databricks Repos version so your .scala files stay in Git, sync automatically, and you don’t need the manual %run or JAR step in dev mode.

