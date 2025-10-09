### Scalastyle integrated with Scalal Databrick Project


Checkstyle itself is designed for Java code, but in the Scala ecosystem you typically use Scalastyle or Scapegoat for style checks, since they integrate well with SBT or Maven.

Because your code is in Databricks notebooks (.ipynb), you need a workflow that can:
1.	Extract the Scala source code from the notebooks.
2.	Run style checks on the extracted code.
3.	Optionally fail CI/CD builds if style rules are violated.

Here’s a practical approach:


---

1. Export Scala Code from Databricks Notebooks

Databricks notebooks can be exported as .dbc, .ipynb, or .scala files. For style checks:
- 	Use the Databricks CLI or Repos API to export notebooks as .scala files:

```bash
databricks workspace export_dir /Workspace/ProjectName ./local_project --format SOURCE
```

This gives you plain Scala files that tools like Scalastyle can analyze.


---

2. Use Scalastyle for Scala Style Checks

Install Scalastyle in your project (SBT example):

```scala
addSbtPlugin("org.scalastyle" %% "scalastyle-sbt-plugin" % "1.0.0")
```


Create a scalastyle-config.xml file in your project root with rules (similar to Checkstyle).

Run style checks:

``bash
sbt scalastyle
```

For Maven:

```xml
<plugin>
  <groupId>org.scalastyle</groupId>
  <artifactId>scalastyle-maven-plugin</artifactId>
  <version>1.0.0</version>
  <configuration>
    <configLocation>scalastyle-config.xml</configLocation>
    <failOnViolation>true</failOnViolation>
  </configuration>
</plugin>
```

Then run:

```bash
mvn scalastyle:check
```


---

3. Automate in CI/CD

- 	Add the notebook export step as a job in your pipeline.
- 	Run sbt scalastyle or mvn scalastyle:check.
- 	Fail the build if style violations occur.

For Databricks Repos + GitHub Actions example:

```yaml
jobs:
  checkstyle:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Export Notebooks
        run: databricks workspace export_dir /Workspace/ProjectName ./local_project --format SOURCE
      - name: Run Scalastyle
        run: sbt scalastyle
```

---

4. Alternative: Convert .ipynb to Scala Script

If you must stay with .ipynb, use a Python tool like nbconvert:

```bash
jupyter nbconvert --to script mynotebook.ipynb
```

Then run Scalastyle on the generated .scala files.


---


### Script to Export notebook to Scala file


**export_notebooks.sh file**

Feature

-  export notebook .ipynb to  .scala file

```python
#!/bin/bash
set -e

#!/bin/bash

SRC_DIR="src"
OUT_DIR="scala_out"

# Create output directory
# mkdir -p "$OUT_DIR"

# Find all .ipynb files and convert to .scala
find "$SRC_DIR" -type f -name "*.ipynb" | while read notebook; do
    # Get relative path without extension
    rel_path="${notebook#$SRC_DIR/}"
    rel_dir="$(dirname "$rel_path")"
    base_name="$(basename "$notebook" .ipynb)"
    
    # Create same directory structure inside OUT_DIR
    # mkdir -p "$OUT_DIR/$rel_dir"

    # Convert to .scala using nbconvert with script format
    #  jupyter nbconvert --to script "$notebook" --output "./$base_name"

    # Move the .txt file and rename to .scala
    # mv "$OUT_DIR/$rel_dir/$base_name.txt" "$OUT_DIR/$rel_dir/$base_name.scala"

    # Convert directly into OUT_DIR with same structure
    jupyter nbconvert --to script "$notebook" \
        --output "$base_name" \
        --output-dir "$SRC_DIR/$rel_dir"

    # Rename .py or .txt to .scala if needed
    if [ -f "$SRC_DIR/$rel_dir/$base_name.py" ]; then
        mv "$SRC_DIR/$rel_dir/$base_name.py" "$SRC_DIR/$rel_dir/$base_name.scala"
    elif [ -f "$SRC_DIR/$rel_dir/$base_name.txt" ]; then
        mv "$SRC_DIR/$rel_dir/$base_name.txt" "$SRC_DIR/$rel_dir/$base_name.scala"
    fi


done
```

**buid.sbt file**

Features
-  manage the dependencies
-  run unit test
-  export notebook .ipynb to  .scala file
-  run checkstyle
-  run veracode
  



```sbt

import sys.process._

lazy val scalastyleSettings = Seq(
  scalastyleConfig := baseDirectory.value / "scalastyle-config.xml"
)

libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-core" % "3.5.6" % Provided,
  "org.apache.spark" %% "spark-sql" % "3.5.6" % Provided,
  "org.scalatest" %% "scalatest" % "3.3.0-SNAP4" % Test,
  "com.holdenkarau" %% "spark-testing-base" % "3.2.0_1.1.1" % Test
)

lazy val root = (project in file("."))
  .settings(
    name := "databricks-pipeline",
    version := "0.1.0",
    scalaVersion := "2.12.20", 
    scalafmtOnCompile := true  ,

    scalastyleSettings,

  // Add JVM option for tests 
// Export internal JDK package for Spark (apply to both run + test)
    Compile / run / javaOptions ++= Seq(
      "--add-exports=java.base/sun.nio.ch=ALL-UNNAMED"
    ),
    Test / javaOptions ++= Seq(
      "--add-exports=java.base/sun.nio.ch=ALL-UNNAMED"
    ),

    // Fix IllegalAccessError in tests due to classloader isolation
    Test / classLoaderLayeringStrategy := ClassLoaderLayeringStrategy.Flat,

    // Run style/format checks before compiling
    Compile / compile := {
      // Run export script before compiling
      sys.process.Process("./export_notebooks.sh").!

      // Run scalafmtAll
      (Compile / scalafmtAll).value

 
      // Run scalastyle check
      (Compile / scalastyleFailOnError).value

      // Run scalafmt check
      // (Compile / scalafmtCheck).value

     // Finally, run the actual compile
      (Compile / compile).value

     // Compile / packageBin / artifactPath := target.value / "databricks-pipeline.jar"
    },

    // Finally, run test compile
     Test / fork := true

  )
  
```