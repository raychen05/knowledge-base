### A ready-to-use Pipeline Script


Got it — I can give you a ready-to-use pipeline script that:
	1.	Exports Databricks notebooks from your workspace.
	2.	Runs Scalastyle checks automatically in your CI/CD pipeline.
	3.	Fails the build if style violations are found.

This approach works for GitHub Actions or can be adapted for Azure DevOps / GitLab CI.


---


1. Prerequisites
   
- 	Databricks CLI installed & configured with DATABRICKS_HOST and DATABRICKS_TOKEN.
- 	Scalastyle plugin in build.sbt:

```scala
addSbtPlugin("org.scalastyle" %% "scalastyle-sbt-plugin" % "1.0.0")
```

- 	scalastyle-config.xml in project root defining rules.


---

```yaml
name: Databricks Notebook Scalastyle Check

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  scalastyle-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      # Install Databricks CLI
      - name: Install Databricks CLI
        run: pip install databricks-cli

      # Export Databricks notebooks as .scala files
      - name: Export Notebooks from Databricks
        run: |
          mkdir -p notebooks
          databricks workspace export_dir /Workspace/MyProject notebooks --format SOURCE

      # Setup Scala + SBT
      - name: Setup Scala and SBT
        uses: olafurpg/setup-scala@v12
        with:
          java-version: "temurin:11"

      # Run Scalastyle on exported .scala files
      - name: Run Scalastyle Checks
        run: |
          sbt scalastyle

```

---


3. Local Scalastyle Run

You can also run Scalastyle locally:

```bash
databricks workspace export_dir /Workspace/MyProject notebooks --format SOURCE
sbt scalastyle
```

Violations will appear in the console; you can make the build fail if any are found.



---

4. Optional: Fail Build on Violation

In build.sbt, add:

``scala
scalastyleFailOnError := true
```

Now sbt scalastyle exits with an error if style violations occur → CI pipeline fails automatically.



---

5. Output

- 	All notebooks exported to notebooks/ as .scala files.
- 	Scalastyle checks code quality.
- 	Pipeline fails if style violations exist.

