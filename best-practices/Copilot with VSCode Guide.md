## GitHub Copilot in VS Code


Below is a practical, opinionated guide to using GitHub Copilot in VS Code efficiently, focused on real developer workflows (refactoring, simplification, logic checks, performance tuning, etc.). This is written for experienced engineers and works especially well for large Scala / Spark / Python / data-pipeline codebases like the ones you usually work on.

Project-specific: /Users/r.chen/workspace/es-notebook-25/prompts
Global: /Users/r.chen/Library/Application Support/Code/User/prompts

### 🚀 GitHub Copilot in VS Code — Efficient Usage Guide


### 0️⃣ Prerequisites (Do This Once)

Enable the right Copilot modes

In VS Code:
- Install GitHub Copilot
- Install GitHub Copilot Chat
- Sign in with GitHub
- 
Recommended settings:

```json
{
  "github.copilot.enable": {
    "*": true
  },
  "github.copilot.inlineSuggest.enable": true,
  "editor.inlineSuggest.enabled": true,
  "github.copilot.chat.codeGeneration.useInstructionFiles": true
}
```

💡 Use Copilot Chat for reasoning & reviews, inline Copilot for writing.

---

### 1️⃣ Core Mental Model (Very Important)


Copilot is best when you:
1. Select code
2. State intent clearly
3. Constrain output

- Bad prompt ❌:
“Refactor this”

- Good prompt ✅:
“Refactor to reduce duplication and make it immutable. Do not change behavior.”

---

### 2️⃣ Refactoring Code (Safely)


#### A. Refactor a method / class

Steps
1. Select the code
2. Press Cmd + Shift + I (Copilot Chat)
3. Use a structured instruction

Prompt template
```text
Refactor this code to:
- Improve readability
- Reduce duplication
- Keep behavior identical
- Prefer pure functions
- No new dependencies
```


Example (Scala / Spark)
```text
Refactor this Spark transformation to:
- Extract reusable functions
- Avoid repeated column expressions
- Keep the same output schema
```

💡 Tip: Add “show before/after diff” if the change is large.

---

#### B. Extract functions automatically

Select a long block → Chat:

```text
Extract logical sub-functions with clear names.
Each function should do one thing.
```

This works extremely well for:
- Spark pipelines
- ETL transformations
- Valid logic

---

### 3️⃣ Simplification & Readability


#### A. Simplify complex logic

Prompt
```text
Simplify this logic while preserving semantics.
Prefer early returns and smaller expressions.
```

Even better
```text
Rewrite this using:
- Fewer nested conditionals
- Clear variable names
- Early exit where possible
```

Copilot excels at:
- Nested if/else
- Long match / case
- Deep loops

---

#### B. Make code more idiomatic

Examples
```text
Make this code more idiomatic Scala

Rewrite using functional style (map/filter/fold)

Rewrite using PySpark best practices
```

This is excellent for:
- Scala collections
- Spark DataFrame transformations
- Python list/dict logic

---

### 4️⃣ Logic & Correctness Checks (Very Powerful)


### A. Ask Copilot to review logic

Select code → Chat:

```text
Review this code for:
- Logical bugs
- Edge cases
- Incorrect assumptions
```

or more targeted:
```text
Check correctness when input is empty or null.
```

💡 Copilot often catches:
- Null handling bugs
- Off-by-one errors
- Incorrect joins / filters
- Wrong aggregation semantics

---

#### B. Validate business logic

```text
Explain what this code does step by step.
Then list cases where it may fail.
```


This is extremely effective for:
- Incremental processing logic
- CDC / watermark logic
- Joins with optional relationships

---

### 5️⃣ Performance Improvement

#### A. General performance review

Select code → Chat:

```text
Analyze performance issues in this code.
Focus on:
- Time complexity
- Memory usage
- Unnecessary recomputation
```

---

#### B. Spark / Data Engineering specific

```text
Optimize this Spark job:
- Reduce shuffles
- Avoid wide transformations where possible
- Cache only when beneficial

Identify expensive Spark operations and suggest alternatives.
```

Copilot is very good at spotting:
- Repeated .withColumn
- Unnecessary .count()
- Bad joins (broadcast needed)
- Missing partition pruning

---

### 6️⃣ Generate Tests (Highly Recommended)


#### A. Unit tests

```text
Generate unit tests covering:
- Normal case
- Edge cases
- Failure scenarios
```

For Spark:
```
Generate Spark unit tests using local mode and sample data.
```

---

#### B. Property / invariant tests

```text
Generate tests that validate invariants of this function.
```

This is excellent for:
- Dedup logic
- Aggregations
- ID mapping / normalization

---

### 7️⃣ Documentation & Explanation


#### A. Explain for future maintainers

```text
Add concise comments explaining:
- Why this logic exists
- Key assumptions
- Non-obvious decisions
```

---

#### B. Generate design docs from code

```text
Summarize this module as a design doc:
- Purpose
- Inputs/Outputs
- Key algorithms
- Failure modes
```

Very useful for onboarding and handoffs.

---

### 8️⃣ Interactive Inline Usage (Fastest)


#### A. Comment-driven coding

Write a comment:
```text
// Build incremental dataset using watermark and deduplicate by id
```
Then press Enter — Copilot fills it.

---

#### B. Partial code → completion

Start typing:
```text
def normalize_author_name(name: str):
```

Pause. Let Copilot infer intent.


💡 Works best when:
- Function name is descriptive
- Types are present
- Surrounding code exists

---

### 9️⃣ Power Patterns (Advanced)


#### A. Constraint-driven prompts

```text
Rewrite this code but:
- Do not change public APIs
- Do not add new dependencies
- Keep time complexity O(n)
```

---

#### B. Compare approaches

```text
Provide two alternative implementations:
1) Readability-first
2) Performance-first
Explain tradeoffs.
```
---

#### C. Incremental refactor

```text
Refactor this in small safe steps.
Show step 1 only.
```

---

### 🔟 When Copilot Works Poorly (Know This)


Avoid Copilot when:
- You need exact business correctness
- APIs are very domain-specific
- Code relies on tribal knowledge

In those cases: 👉 Use Copilot to explain, not generate.

---

### ✅ Recommended Workflow (Daily Use)

1. Write rough code
2. Select → Ask Copilot to simplify
3. Ask for logic review
4. Ask for performance review
5. Generate tests
6. Final manual review

This aligns perfectly with your pipeline-heavy, correctness-sensitive systems.

If you want, I can:

- Create ready-to-copy prompt templates for Spark / Scala / Python
- Show a before/after refactor example
- Provide a Copilot usage playbook for data pipelines
- Compare Copilot vs ChatGPT vs Cursor for your workflow



---


### Refactor hard-coded and variable-based table names to table definition objects


```prompt
---
description: Refactor hard-coded and variable-based table names to table definition objects
---

Refactor the selected Scala pipeline code to eliminate hard-coded table name strings
and dynamically constructed table name variables.

Replace them with canonical table definition references using case objects.


Schema-to-object mapping rules:
- If the schema name starts with `gold_`, use object prefix `ACS`
- If the schema name starts with `dap_`, use object prefix `DAP`


Table name derivation rules:
For any table name in snake_case (literal or derived):

1. Extract the final table identifier
   (e.g. `address_publication_link`, `wos_docs_processed`).
2. Convert snake_case to PascalCase:
   - address_publication_link → AddressPublicationLink
   - wos_docs_processed → WosDocsProcessed
3. Use the derived name as the case object under the schema object.
4. Replace the table reference with:
   <SchemaObject>.<DerivedCaseObjectName>.fullName


Variable handling rules:
- If a `val` is used only to define or compose a table name
  (e.g. `val tb_wos_src = s"${schema}.wos_docs_processed"`):
  - Replace all usages of that variable with the derived
    `<SchemaObject>.<CaseObject>.fullName`
  - Remove the variable definition if it is no longer used.
- Do NOT inline or reconstruct schema strings.
- Assume the case object already exists and exposes `fullName`.


Literal string handling:
- Replace any literal table name string used in:
  read, write, merge, insert, delete
- Apply the same derivation and schema rules as above.

Examples:
- "address_publication_link"
    → ACS.AddressPublicationLink.fullName
- "author_publication_link"
    → ACS.AuthorPublicationLink.fullName

Variable example:
Input:
  val schema_src = s"${catalog}.{dap_work}_${ver}"
  val tb_wos_src = s"${schema_src}.wos_docs_processed"

  spark.read.table(tb_wos_src)

Output:
  spark.read.table(DAP.WosDocsProcessed.fullName)


Constraints:
- Only refactor table name references.
- Do NOT change business logic or data transformations.
- Preserve formatting and method chaining style.
- If the schema prefix cannot be confidently determined,
  leave the code unchanged.

Output:
- Return only the refactored code.
- Do not add explanations or commentary.
```


🧠 Why this combined prompt is strong

- Handles both literals and variables
- Deterministic name derivation (low hallucination risk)
- Enforces direct usage of table definitions
- Scales cleanly across large pipelines
- Safe: leaves ambiguous cases untouched

📌 Suggested filename

refactor-table-names-to-definitions.prompt.md

If you want next steps, I can:

- Create a validation-only prompt to find missed tables
- Add ODS / SILVER / DIM schema rules
- Make a dry-run version that reports changes instead of applying them
- Optimize for Spark SQL strings vs DataFrame API



---



Below is a curated, battle-tested prompt library that senior engineers, architects, and staff-level ICs commonly use with Claude / Copilot / ChatGPT for large-scale data pipeline projects (Scala + Spark + Databricks–style environments).
These prompts are opinionated, professional, and production-oriented. They are designed to make the model behave like a principal data engineer / software architect, not a tutorial bot.
You can paste these verbatim into Claude, Copilot Chat, or ChatGPT and then append your code or context.


### 0️⃣ Universal “Senior Engineer Mode” System Prompt (Use First)

Use this once per session to set behavior.

```diff
You are a Staff/Principal Software Engineer and Data Platform Architect.

You:
- Design for large-scale, production Spark pipelines (Scala, Databricks, Delta Lake).
- Optimize for correctness, performance, cost, and operability.
- Prefer explicit, testable, deterministic logic.
- Avoid magic, hidden state, or notebook-only patterns.
- Think in terms of data contracts, idempotency, incremental processing, and failure modes.
- Call out risks, trade-offs, and anti-patterns.
- Assume multi-team ownership and long-term maintenance.

When reviewing or generating code:

- Be precise, pragmatic, and opinionated.
- Propose clean abstractions.
- Include edge cases, validation, and observability.
- Prefer clarity over cleverness.
```

---

### 1️⃣ Software Design & Architecture (Pipeline / Platform)


High-Level Pipeline Design

```diff
Act as a Principal Data Architect.

Given the following requirements and constraints, design a production-grade
Spark/Databricks data pipeline.

Include:
- Logical architecture
- Data flow (bronze/silver/gold if applicable)
- Incremental strategy (CDC / watermark / versioning)
- Idempotency and replay strategy
- Failure handling and recovery
- Schema evolution strategy
- Cost and performance considerations

Requirements:
<PASTE REQUIREMENTS>
```


Registry / Metadata / Control Table Design

```diff
Design a minimal but production-ready metadata schema
to manage pipelines, tasks, upstream dependencies, and checkpoints.

Goals:
- Simple operations and maintenance
- Support partial re-runs
- Support multi-task pipelines
- Support upstream dependency tracking

Provide:
- Table schemas
- Primary keys and indexes
- Example records
- Rationale and trade-offs
```

---


### 2️⃣ Scala / Spark Coding (Production-Quality)

Implement Logic Like a Senior Engineer
```diff
Rewrite the following Spark/Scala logic as production-quality code.

Requirements:
- No notebook-only assumptions
- Pure functions where possible
- Explicit inputs and outputs
- Clear naming and separation of concerns
- Defensive handling of nulls and empty inputs
- Scalable for large datasets

Code:
<PASTE CODE>
```

Refactor Notebook → Modular Pipeline

```diff
Scan the entire notebook logic and refactor it into
a modular, testable Scala pipeline.

Goals:
- Group logic into cohesive functions or classes
- Introduce a clear main orchestration function
- Remove duplicated logic
- Make configuration explicit
- Prepare code for CI/CD execution

Notebook cells:
<PASTE NOTEBOOK OR SUMMARY>
```

---

### 3️⃣ Performance Optimization (Spark / Databricks)

Spark Performance Review
```diff
Review the following Spark job as a performance engineer.

Focus on:
- Shuffles and joins
- Partition strategy
- Broadcast usage
- Caching / persistence correctness
- UDF vs built-in functions
- Skew handling
- Delta Lake optimizations

Code:
<PASTE CODE>

Explain:
- What will be slow at scale
- Why
- How to fix it
```

Cost & Scale Optimization

```diff
Analyze this Spark pipeline from a cost and scalability perspective.

Assume:
- Billions of rows
- Daily incremental loads
- Databricks autoscaling

Recommend:
- Partitioning strategy
- File size optimization
- Job decomposition
- Cluster sizing guidance
- Query pattern improvements
```

---

### 4️⃣ Business Logic Review & Correctness

Logic Validation
```diff
Act as a senior engineer reviewing business logic.

Given the following requirements and implementation:
- Validate correctness
- Identify hidden assumptions
- Identify edge cases
- Identify data quality risks

Requirements:
<PASTE REQUIREMENTS>

Implementation:
<PASTE CODE>
```

Edge Case Discovery

```diff
Enumerate all realistic edge cases for this data transformation.

Include:
- Empty inputs
- Partial upstream updates
- Late-arriving data
- Duplicates
- Schema drift
- Null / malformed records

Code:
<PASTE CODE>
```

---

### 5️⃣ Data Validation & Integrity Checks

Incremental Validation Strategy

```diff
Design an incremental-only data validation strategy
between source Delta tables and downstream targets.

Constraints:
- Avoid full table scans
- Support large datasets
- Detect missing, duplicated, or corrupted records

Include:
- Validation rules
- Sampling strategy
- Metrics to compute
- Failure thresholds
```

Data Contract Enforcement

```diff
Define a data contract for this dataset.

Include:
- Required columns
- Nullable vs non-nullable
- Uniqueness constraints
- Allowed value ranges
- Backward compatibility rules

Dataset schema:
<PASTE SCHEMA>
```

---

### 6️⃣ Unit Testing & Comparison Testing

Spark Unit Tests

```diff
Write production-grade unit tests for this Spark transformation.

Requirements:
- Use small in-memory DataFrames
- Cover happy path and edge cases
- Validate schema and data correctness
- Deterministic and fast

Transformation:
<PASTE FUNCTION>
```

Comparison Test (Before vs After Refactor)

```diff
Generate comparison tests that validate
the refactored implementation produces identical results
to the original logic.

Include:
- Schema comparison
- Row-level comparison
- Aggregation checks
- Handling of nulls and ordering
```

---

### 7️⃣ SQL → Spark / Scala Migration

SQL to Spark Translation

```diff
Translate the following SQL logic into idiomatic Spark Scala code.

Requirements:
- Preserve semantics exactly
- Avoid unnecessary shuffles
- Use DataFrame APIs (not SQL strings)
- Be readable and testable

SQL:
<PASTE SQL>
```


Validate SQL vs Spark Equivalence

```diff
Explain how to validate that this Spark implementation
is semantically equivalent to the original SQL.

Include:
- Test strategy
- Known pitfalls
- Differences in NULL semantics
- Aggregation edge cases
```

---

### 8️⃣ Code Review (Senior / Staff Level)


Formal Code Review Prompt

```diff
Perform a senior-level code review of the following code.

Focus on:
- Correctness
- Readability
- Scalability
- Maintainability
- Production readiness

Call out:
- Bugs
- Design smells
- Missing tests
- Operational risks

Code:
<PASTE CODE>
```


Simplification & Cleanup

```diff
Simplify this code without changing behavior.

Goals:
- Reduce cognitive load
- Remove redundancy
- Improve naming
- Make intent obvious

Code:
<PASTE CODE>
```

---

### 9️⃣ Observability, Reliability & Ops

Production Hardening

```diff
Review this pipeline for production readiness.

Evaluate:
- Logging quality
- Metrics to emit
- Alerting signals
- Failure modes
- Retry and idempotency

Code:
<PASTE CODE>
```

---

### 🔟 “Architect Judgment” Prompt (Very Powerful)

Use this when you want opinionated decisions.

Act as a Principal Engineer making a design decision.

Given the context below:
- Recommend the best approach
- Explain why alternatives are worse
- Call out long-term risks
- Consider scale, team size, and maintenance

Context:
<PASTE CONTEXT>
```

---

### ✅ How Senior Engineers Actually Use These

Typical flow in real projects:
1. Architecture prompt
2. Refactor prompt
3. Logic validation
4. Edge case discovery
5. Performance review
6. Comparison tests
7. Production hardening


If you want, next I can:
- 🔧 Convert this into a Copilot prompt pack (one-liners optimized for inline chat)
- 📦 Generate a prompt YAML library you can version-control
- 🧠 Create a “Databricks Principal Engineer” super-prompt
- 🧪 Provide real Scala + Spark examples for each category



---



Perfect use-case for Copilot 👍 Below is a Copilot-optimized prompt pack: short, directive, one-liners designed for inline chat (VS Code / JetBrains / Databricks notebooks).
These are written the way senior/staff engineers actually talk to Copilot: imperative, scoped, no fluff, assumes production context.
You can copy-paste these as-is.

### 🧠 Copilot Prompt Pack — Senior Engineer / Data Architect Mode

(Scala · Spark · Databricks · Large-Scale Pipelines)

0️⃣ Session Primer (Run Once)

```diff
Act as a Staff/Principal Data Engineer. Assume production Spark/Scala pipelines, large datasets, incremental processing, strict correctness, and long-term maintainability. Be opinionated.
```

1️⃣ Architecture & Pipeline Design

```diff
Design a production-grade Spark/Databricks pipeline architecture for this use case. Focus on incremental processing, idempotency, failure recovery, and schema evolution.

Propose a minimal metadata/control-table design to manage pipelines, tasks, upstream dependencies, and checkpoints. Optimize for ops simplicity.

Given these requirements, recommend bronze/silver/gold layering and justify trade-offs.
```

2️⃣ Notebook → Modular Pipeline Refactor

```diff
Refactor this notebook logic into a clean, testable Scala pipeline with explicit inputs, outputs, and orchestration.

Group this logic into cohesive functions or classes and remove notebook-only assumptions.

Extract the main orchestration flow and make configuration explicit.
```

3️⃣ Scala / Spark Code Quality

```diff
Rewrite this Spark/Scala code to be production-quality: clear naming, pure functions where possible, defensive handling, no hidden state.

Simplify this code without changing behavior; reduce cognitive load and duplication.

Refactor this logic to be more readable and maintainable at scale.
```

4️⃣ Business Logic & Correctness

```diff
Review this implementation against the business requirements and identify logic bugs, hidden assumptions, or mismatches.

Validate whether this transformation is correct under partial updates and incremental loads.

Identify all edge cases this logic must handle in real production data.
```

5️⃣ Edge Case & Failure Mode Analysis

```diff
List all realistic edge cases for this transformation: empty inputs, late data, duplicates, nulls, schema drift.

Explain how this job behaves if upstream data is partially updated or missing.

Identify failure modes and how to make this logic idempotent and retry-safe.
```

6️⃣ Spark Performance & Scalability

```diff
Review this Spark job for performance issues at scale (joins, shuffles, partitions, skew).

Identify where this code will be slow or expensive on billions of rows and how to fix it.

Recommend partitioning, caching, and broadcast strategies for this pipeline.

Rewrite this logic to minimize shuffles and improve scalability.
```

7️⃣ Cost Optimization (Databricks-Aware)

```diff
Analyze this pipeline for Databricks cost efficiency and scaling risks.

Recommend cluster sizing, job decomposition, and file-size optimizations.

Suggest Delta Lake optimizations (OPTIMIZE, ZORDER, partitioning) for this workload.
```

8️⃣ Data Validation & Integrity

```diff
Design incremental-only data validation checks between source and target without full table scans.

Add data quality checks for uniqueness, nulls, and referential integrity.

Propose a lightweight sampling-based validation strategy for large datasets.
```

9️⃣ Unit Tests & Comparison Tests

```diff
Write Spark unit tests for this transformation using small in-memory DataFrames.

Add tests covering edge cases, null handling, and empty inputs.

Create comparison tests to verify this refactored code matches the original output exactly.

Validate schema and row-level equivalence between these two implementations.
```

🔟 SQL → Spark / Scala Migration

```diff
Translate this SQL query into idiomatic Spark Scala DataFrame code with identical semantics.

Review this SQL-to-Spark conversion for correctness and performance pitfalls.

Explain how to prove this Spark logic is semantically equivalent to the original SQL.
```

1️⃣1️⃣ Code Review (Senior Level)

```diff
Perform a senior-level code review: correctness, scalability, maintainability, and production readiness.

Call out bugs, design smells, missing validations, and operational risks.

Recommend refactors that would improve long-term maintainability.
```

1️⃣2️⃣ Observability & Production Hardening

```diff
Add production-grade logging, metrics, and failure signals to this pipeline.

Identify what should be logged, measured, and alerted on in this job.

Review this pipeline for operational risks and recovery behavior.
```

1️⃣3️⃣ Architectural Judgment / Trade-off Decisions

```diff
Recommend the best architectural approach here and explain why alternatives are worse at scale.

Make a principal-engineer-level design decision considering long-term maintenance and team ownership.

Call out hidden risks in this design that may not be obvious initially.
```

1️⃣4️⃣ Copilot “Inline Diff” Prompts (Very Effective)

```diff

Use when highlighting code:

Improve this block for readability and scalability.

Fix correctness issues and edge cases in this logic.

Optimize this join logic for large-scale data.

Make this function deterministic and testable.
```

⭐ Pro Tips (How Seniors Use Copilot)

- Keep prompts short + directive
- Assume production context by default
- Chain prompts:
    1. Refactor
    2. Logic review
    3. Edge cases
    4. Performance
    5. Tests

If you want next, I can:

- 📄 Package this as a .md / README prompt library
- 🧩 Generate a VS Code snippet file (.code-snippets)
- 🧠 Create a single ultra-dense “Principal Engineer” Copilot prompt
- 🧪 Provide real Scala Spark examples paired with these prompts



---


Below is a single, ultra-dense “Databricks Principal Engineer” super-prompt you can paste once per session into Copilot / Claude / ChatGPT.

This is designed to lock the model into Staff / Principal behavior for Scala + Spark + Databricks + Delta Lake pipeline work.


🧠 Databricks Principal Engineer — Super Prompt

```diff
You are acting as a Principal Data Engineer and Platform Architect specializing in
Databricks, Spark (Scala), and Delta Lake at enterprise scale.

Assumptions:
- Datasets range from millions to billions of rows
- Pipelines are incremental (CDC, watermark, version-based)
- Jobs must be idempotent, replayable, and production-safe
- Multiple teams own and extend this code over years
- Cost, performance, and operability matter as much as correctness

Your responsibilities:
- Design clean, scalable architectures (not notebook hacks)
- Enforce correctness of business logic under partial updates
- Identify edge cases, failure modes, and hidden assumptions
- Optimize Spark performance (joins, shuffles, skew, partitioning)
- Minimize Databricks cost without sacrificing reliability
- Prefer explicit, deterministic, testable logic
- Avoid magic configs, implicit state, or brittle assumptions

When reviewing or generating code:
- Be opinionated and pragmatic
- Call out bugs, design smells, and long-term risks
- Propose better abstractions and refactors
- Consider schema evolution and backward compatibility
- Assume Delta Lake semantics (MERGE, OPTIMIZE, ZORDER, ACID)
- Favor DataFrame APIs over SQL strings unless justified

Always include, when relevant:
- Incremental processing strategy
- Idempotency and replay behavior
- Edge case handling
- Data validation approach
- Unit or comparison testing guidance
- Observability (logs, metrics, alerts)
- Trade-offs and alternatives with justification

Do NOT:
- Give tutorial-style explanations
- Assume small data or one-off jobs
- Ignore operational or maintenance concerns

Operate as if you are reviewing or designing a production pipeline
that will run daily, cost real money, and be paged on if it fails.

```


How to Use It (Senior Pattern)

1. Paste the super-prompt once
2. Then issue short Copilot prompts like:
    - “Refactor this notebook into a pipeline”
    - “Review this Spark job for correctness and skew”
    - “Design incremental validation”
    - “Compare SQL vs Spark semantics”
3. Let the model stay anchored in Principal mode

When This Prompt Is Most Effective

- Large Spark refactors
- SQL → Spark migrations
- Incremental / CDC pipelines
- Delta MERGE logic
- Performance & cost reviews
- Production hardening
- Code reviews before release

If you want next, I can:
- 📦 Embed this into your README prompt library
- 🧩 Turn it into a VS Code snippet (one keystroke)
- 🔒 Create variants (Reviewer mode / Performance-only mode)
- 🏗️ Add a Delta Live Tables–specific super-prompt


---
