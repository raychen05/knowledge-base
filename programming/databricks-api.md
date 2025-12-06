

## Databricks API: Table Lineage and Constraints

Databricks exposes table lineage and table constraints through two different APIs.

Below is the full explanation and the correct API calls.


### 1. Lineage API (Upstream/Downstream Only)

**Endpoint:**
```bash
/api/2.0/lineage-tracking/table-lineage
```

Usage Example
```bash
curl -X GET "https://xxx.cloud.databricks.com/api/2.0/lineage-tracking/table-lineage" \
-H "Authorization: Bearer xxx" \
-H 'Content-Type: application/json' \
-d '{"table_name": "analytics_data_dev.entity.article", "include_entity_lineage": true}'


```

**Provides:**
- Upstream tables
- Downstream tables
- Job and notebook lineage
- Table metadata used in lineage

**Does NOT include:**
- ❌ Primary keys
- ❌ Foreign keys
- ❌ Column-level constraints

---

### 2. How to Get Table Primary Keys / Foreign Keys

Databricks stores relational constraints in Unity Catalog, not in the lineage API.

**Unity Catalog Constraints API:**

```bash
GET /api/2.1/unity-catalog/constraints
```

Or retrieve constraints for a single table:

```bash
GET /api/2.1/unity-catalog/tables/{full_table_name}
```

**Returns:**
- Primary keys (PRIMARY KEY)
- Foreign keys (FOREIGN KEY)
- Unique constraints
- Check constraints
- Column definitions

---

### 3. Python Example: Get PK/FK + Lineage Together

```python
import requests
import json

token = "<DATABRICKS_TOKEN>"
workspace = "https://<your-workspace-url>"

table = "content_dev.docs.publication"

headers = {"Authorization": f"Bearer {token}"}

# ---- Lineage ----
lineage_url = f"{workspace}/api/2.0/lineage-tracking/table-lineage"
lineage_payload = {
    "table_name": table,
    "include_entity_lineage": True
}
lineage = requests.get(lineage_url, headers=headers, json=lineage_payload).json()

# ---- Constraints (PK, FK) ----
constraints_url = f"{workspace}/api/2.1/unity-catalog/tables/{table}"
constraints = requests.get(constraints_url, headers=headers).json()

print("Lineage:", json.dumps(lineage, indent=2))
print("PK/FK:", json.dumps(constraints.get("constraints", []), indent=2))
```

---

### 4. Summary

| Information Needed | API | Includes PK/FK? |
|-------------------|-----|-----------------|
| Table lineage (upstream/downstream) | `/api/2.0/lineage-tracking/table-lineage` | ❌ No |
| Table metadata + constraints | `/api/2.1/unity-catalog/tables/{name}` | ✅ Yes |
| List of all constraints | `/api/2.1/unity-catalog/constraints` | ✅ Yes |


---

### ✅ Key Takeaway

Databricks does not provide PK or FK info via API, so your “lineage + PK/FK” Delta table pipeline must rely on manual or external metadata sources for PK/FK.


---

In Databricks Unity Catalog, you can get all tables and their columns under a specific catalog and schema by combining two APIs:


###  5. List tables in a schema:


```bash
GET /api/2.1/unity-catalog/tables?catalog_name=<catalog>&schema_name=<schema>

```

```bash
curl -X GET "https://xxx.databricks.com/api/2.1/unity-catalog/tables?catalog_name=analytics_data_dev&schema_name=entity" \
-H "Authorization: Bearer xxx" 

```


- Returns a list of tables under the specified catalog and schema.
- Each table object includes name, catalog_name, schema_name, table_type, created_at, etc.
- Does not include column details.


---

### 6. Get table details (including columns) for each table:


```bash
GET /api/2.1/unity-catalog/tables/{full_table_name}
```

Usage:

```bash
curl -X GET "https://xxx.databricks.com/api/2.1/unity-catalog/tables/analytics_data_dev.entity.organizations" \
-H "Authorization: Bearer xxx" 

```



- full_table_name format: <catalog>.<schema>.<table>
- Returns columns array with all column metadata (name, type_text, nullable, etc.).


---

### Python Example

```python
import requests

workspace_url = "https://<your-workspace-url>"
token = "<your-token>"

catalog = "ag_content_ims_dev"
schema = "acs_wos"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 1️⃣ List tables
list_tables_url = f"{workspace_url}/api/2.1/unity-catalog/tables?catalog_name={catalog}&schema_name={schema}"
resp = requests.get(list_tables_url, headers=headers)
tables = resp.json().get("tables", [])

all_table_columns = []

# 2️⃣ Get columns for each table
for t in tables:
    table_name = t["name"]
    full_name = f"{catalog}.{schema}.{table_name}"
    table_url = f"{workspace_url}/api/2.1/unity-catalog/tables/{full_name}"
    r = requests.get(table_url, headers=headers)
    if r.status_code != 200:
        print(f"Failed for {full_name}: {r.text}")
        continue
    table_info = r.json()
    columns = table_info.get("columns", [])
    for col in columns:
        all_table_columns.append({
            "table": full_name,
            "col_name": col["name"],
            "col_type": col["type_text"],
            "nullable": col["nullable"]
        })

# Print results
for row in all_table_columns:
    print(row)

```
