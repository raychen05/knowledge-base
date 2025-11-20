
## Refined LLM Prompt - delta data processing


Implement Scala code to create an object or class that performs delta-change detection in a standardized way for multiple pipeline modules. The component should take three inputs:

1. A list of dimension tables (Delta format)
2. A list of link tables (Delta format)
3. A list of citation tables (Delta format)

The output should be the set of affected primary keys (i.e., the delta keys that require downstream processing). These keys may be:
- A single key (e.g., pguid for researcher data), or
- A composite key (e.g., document uid + author pguid).

Processing logic and considerations:
- Dimension table changes occur less frequently but can affect many documents.
- Link table changes are moderate and affect linked documents.
- Citation table changes occur most frequently and can affect multiple related documents.
- The logic should consider this hierarchy and optimize processing by evaluating changes in this order:
    1. Dimension tables
    2. Link tables
    3. Citation tables

Additional requirements:
- All tables are stored in Delta Lake format and CDF enabled.
- The implementation must use the Spark DataFrame API.
- The solution must be modular and easily extensible for future enhancements.
- Upstream Dimension-table deletions/addition,  link-table rows linked to deleted/added dimension records are removed /added automatically.
- Deletions/additions in link tables propagate to citation tables, where related citation entries are removed or added accordingly.
- Upstream tables are processed in streaming mode, so the code must support streaming inputs or/amd patch mode (e.g. processing once daily).
- 
Deliverables:
- Provide complete Scala code using Spark DataFrames.
- Add clear comments throughout the code for better understanding.
- Structure the code into reusable modules/classes.


--









