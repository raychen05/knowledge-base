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

