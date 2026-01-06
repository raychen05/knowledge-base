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





