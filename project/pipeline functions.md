
### Description of QueryProcessor


#### Features

- Dynamic table_changes for tables with version_param.
- Optional per-table filter applied automatically.
- Multi-column joins handled correctly.
- Union across multiple tables.
- Dynamic catalog replacements like ${entity} supported.
- Runtime version map allows flexible filtering of selected tables.

---

#### 1. Function: renderSqlTemplate,  renderSqlTemplateExtended

This function can be used to check the the generated SQL query before actual test, we can copy the query to SQL editor to run to validate first 

```scala


// Basic function: read master table by start/end version and read appendix tables as end version
def renderSqlTemplate(
  sqlTemplateConfig: String, 
  tableVersionMap: Map[String, (Long, Long)] = Map.empty
): Unit = { ... }



// Extended function(experimental): extend the logic to return the row of the latest version if multiple rows exist
def renderSqlTemplateExtended(
  sqlTemplateConfig: String, 
  tableVersionMap: Map[String, (Long, Long)] = Map.empty
): Unit = { ... }


```

**Paramters**:
- sqlTemplateConfig: The SQL-query configuration that defines the SQL query. It contains placeholders(catalog) that need to be replaced.
- tableVersionMap: A map for rom upstream tables: tableName → (startVersion, endVersion), where `startVersion` and `endVersion` define the inclusive version range to process for each upstream table.  the map data can be created using WatermarkManager 


---

#### 2. Function: runSqlAndSave

This function is used to actually create the delta Paffected K table speficied in SQL config and save data to the table

```scala


def runSqlAndSave(
  sqlTemplateConfig: String,
  targetTableName: String,
  tableVersionMap: Map[String, (Long, Long)] = Map.empty
): Unit = { ... }

```

**Paramters**:
- sqlTemplateConfig: The SQL-query configuration that defines the SQL query. It contains placeholders(catalog) that need to be replaced.
- targetTableName: The taget delta tbale to save the output Dataframe
- tableVersionMap: A map for upstream tables: tableName → (startVersion, endVersion), where `startVersion` and `endVersion` define the inclusive version range to process for each upstream table.  the map data can be created using Watermarks 


---

#### 3. SQL Ccongiuration

SQL Config Example

```yaml
  output_table:
    name: "${dap}.pk_affected_sp"
  union_tables:
    - select_columns: "sp_id AS sp_id, sp._change_type as _change_type, sp.__end_at"
      joins:
        - table_name: ${entity}.d_spmaster
          alias: "sp"
          pk: "sp_id"
          version_param: ${entity}.d_spmaster   # optional: will use dynamic version
          filter: "sp._change_type IN ('insert',  'update_postimage') AND sp.__end_at IS NULL"  # optional
          
    - select_columns: "spl.sp_id AS sp_id,  org.update_postimage AS _change_type, org.__end_at"
      joins:
        # Base table: updated orgmaster
        - table_name: ${entity}.d_orgmaster
          alias: org
          pk: "org.org_pguid"
          version_param: ${entity}.d_orgmaster 
          filter: "org._change_type IN ('update_postimage') AND org.__end_at IS NULL"

        # Join to orgmaster_publication_link (by org_pguid)
        - table_name: ${entity}.orgmaster_publication_link
          alias: oml
          pk: "oml.org_pguid"
          fk: "org.org_pguid"
          filter: "oml.__end_at IS NULL"

```


- select_columns: Comma-separated SQL expression list defining which columns will be selected in the generated query.
- joins: A list of join definitions specifying how tables are connected, including table name, alias, key relationships, and filters applied to each join.
  - 2.1 table_name: The fully qualified table name (may contain placeholders like ${entity}) used as the source for each join.
  - 2.2 alias: Alias assigned to the table for use in SQL expressions and join conditions.
  - 2.3 pk: Primary key or join key from the current table used to drive the join relationship.
  - 2.4 fk (optional): Foreign key in the joining table that references the primary key of the previous table.
  - 2.5 version_param (optional): A version or partition parameter used for versioned/historized tables, inserted into the query when needed.
  - 2.6 filter: A SQL filter expression applied to the table in the join, typically used for change-type filtering or active-record constraints (e.g., __end_at IS NULL).


#### 4. Scheam Map Definition: SchemaResolver.SCHEMA_MAP

This object warp the information on catalog, schema, environment and  version varibable management, which is used to render the SQl query with the dynamic varibale for catalog.


```scala
val catalogMap = SchemaResolver.SCHEMA_MAP
```


**SCHEMA_MAP Example**

```scala

 Map(
  pprn -> ag_content_ims_acs_prod.gold_pprn
  dap_metrics_pprn -> ag_ra_search_analytics_data_dev.dap_metrics_pprn_v1_0
  dap_entity_wos -> ag_ra_search_analytics_data_dev.dap_entity_wos_v1_0
  dap_metrics_wos -> ag_ra_search_analytics_data_dev.dap_metrics_wos_v1_0
  dap_entity_enrich -> ag_ra_search_analytics_data_dev.dap_entity_enrich_v1_0
  dap_reference -> ag_ra_search_analytics_data_dev.dap_reference_v1_0
)

```

---





