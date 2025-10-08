#### Unit text with Databricks notebooks 

Got it — you have Scala code inside Databricks notebooks (.ipynb) and want unit tests that run in your CI/CD pipeline, just like a normal Scala/Spark project.

Here’s a complete way to set it up:

---


1. Organize Code & Tests Outside Notebooks

Notebooks aren’t ideal for unit testing directly. The best practice is:
- 	Move core logic into .scala files (in a Git repo) using Databricks Repos or regular SBT project structure:
    
```text
project-root/
  src/
    main/
      scala/   <-- your actual pipeline code
    test/
      scala/   <-- your unit tests
```

- 	Notebooks just call the tested functions, not contain the logic.


---

2. Pick a Testing Framework

Common Scala testing frameworks:

- 	ScalaTest (most popular)
- 	MUnit (lightweight)
- 	Specs2

For Spark code, ScalaTest + spark-testing-base is common.

In build.sbt:

```scala
libraryDependencies ++= Seq(
  "org.scalatest" %% "scalatest" % "3.2.16" % Test,
  "com.holdenkarau" %% "spark-testing-base" % "3.4.0_1.4.0" % Test
)
```

---

3. Write a Simple Unit Test

Example using ScalaTest for a pipeline function:

```scala
import org.scalatest.funsuite.AnyFunSuite
import org.apache.spark.sql.SparkSession

class SamplePipelineTest extends AnyFunSuite {
  val spark = SparkSession.builder().master("local[*]").appName("Test").getOrCreate()
  import spark.implicits._

  test("Check pipeline transforms data correctly") {
    val input = Seq(("Alice", 25), ("Bob", 30)).toDF("name", "age")
    val output = input.filter($"age" > 26)
    assert(output.count() == 1)
  }
}
```

Run locally with:

```bash
sbt test
```

---

4. Run in Databricks Notebooks (Optional)

If you must run inside Databricks for interactive debugging:
- 	Use %run to import .scala files into a Databricks notebook.
- 	Run tests using Databricks Connect or a test runner library like databricks-ijava-test-runner (for Scala/Java).

But for CI/CD, keep tests in Git + SBT, not notebooks.

---

5. Automate in CI/CD

Typical pipeline steps:

1.	Export code from Databricks if needed:

```bash
databricks workspace export_dir /Workspace/ProjectName ./src/main/scala --format SOURCE
```


2.	Run sbt test in your CI/CD runner:
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Export Notebooks
        run: databricks workspace export_dir /Workspace/ProjectName ./src/main/scala --format SOURCE
      - name: Run Unit Tests
        run: sbt test
```

6. Extra for Spark Pipelines
7. 
- 	Use spark-testing-base for helper methods like assertDataFrameEquals.
- 	Optionally use a mock SparkSession for faster tests.