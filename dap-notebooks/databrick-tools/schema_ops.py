from asyncio import tasks
import email
import sys
import os
from xxlimited import Str
import requests
import json
import re
import csv
import yaml
from datetime import datetime
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Any, Sequence, Optional, Tuple
#from databricks import sql
from databricks import sql as dbsql
from enum import Enum
from dataclasses import dataclass


class WatermarkType(Enum):
    BASELINE = "baseline"
    INCREMENTAL = "incremental"
    DUMPY = "dumpy"


@dataclass
class FeatureContext:
    catalog_name: Optional[str] = None 
    schemas: Optional[list] = None 
    version: Optional[str] = None  
    environment: Optional[str] = None  
    filename: Optional[str] = None 
    ops_table_name: Optional[str] = None             # table - watermark, registry or task   -- pipeline_metadata, insert_watermark
    source_version: Optional[str] = None             # source version for clone schema.      -- clone_dap_schemas
    target_version: Optional[str] = None             # target version for clone schema.      -- clone_dap_schemas
    sql_file_path: Optional[str] = None
    table_name: Optional[str] = None
    file_path: Optional[str] = None
    output_path: Optional[str] = None
    watermark_type: Optional[WatermarkType] = None  # watermark type for insert watermark data
    stmt: Optional [str] = None         # single sql statement to execute
    schema: Optional[str] = None          # single schema name
   # zorder_columns: Optional[dict] = None           # zorder columns for optimize table

class ConfigInfo:

    def __init__(self):

        def load_yaml(path: str) -> dict:

            with open(path, "r") as f:
                return yaml.safe_load(f) or {}

        cfg = load_yaml("./config.yaml")

        self.runtime_env = cfg.get("runtime_env", "prod")

         # Initialize Databricks SQL client
        self.dev_server_hostname = cfg.get(f"dev_server_hostname", "clarivate-ag-dev.cloud.databricks.com")
        self.dev_http_path = cfg.get(f"dev_http_path", "/sql/1.0/warehouses/142758d7a559c589")
        self.dev_access_token = cfg.get(f"dev_access_token", "")

        self.prod_server_hostname = cfg.get("prod_server_hostname", "clarivate-ag-prod.cloud.databricks.com")
        self.prod_http_path = cfg.get("prod_http_path", "/sql/1.0/warehouses/ab9da35c288ba42b")
        self.prod_access_token = cfg.get("prod_access_token", "")


        """ 
        self.conn = DatabricksSQLClient(
                server_hostname = self.prod_server_hostname,
                http_path = self.prod_http_path,
                access_token = self.prod_access_token
            )
        """

        self.src_catalog_name = cfg.get("source_catalog_name", "ag_content_ims_acs")
        self.src_version = cfg.get("source_schema_version", "v_1_0_1")
        self.src_environment = cfg.get("source_environment", "prod")

        self.catalog_name = cfg.get("target_catalog_name", "ag_ra_search_analytics_data")
        self.environment = cfg.get("target_environment", "prod")
        self.version = cfg.get("target_schema_version", "v_1_0_1")  

        self.output_path = cfg.get("output_path",".") 

        self.ops_schema = cfg.get("ops_schema", "dap_ops")
        self.ops_table_name = cfg.get("ops_table_name", "watermarks")
        self.watermark_type = cfg.get("watermark_type", "baseline")
        self.watermark_sql_file =  cfg.get('insert_watermarks_sql_file', 'insert_watermarks.sql')

        self.create_ops_tables_sql_file = cfg.get("create_ops_tables_sql_file", "ddl/create_ops_tables.sql")
        self.optimize_dap_tables_sql_file = cfg.get("optimize_dap_tables_sql_file", "ddl/optimize_dap_tables.sql")
        
        self.clone_schemas = cfg.get("clone_schemas", [
                "dap_reference",
                "dap_sort_ref"
            ])
        
        self.reistry_table_name = cfg.get("registry_table_name", "dap_pipeline_registry")
        self.upstream_table_name = cfg.get("upstream_table_name", "dap_pipeline_task_upstream")

        self.insert_registry_sql_file = cfg.get('insert_registry_sql_file', 'dap_pipeline_registry.sql')
        self.insert_task_sql_file = cfg.get('insert_task_sql_file', 'dap_pipeline_task_upstream.sql')
        self.create_table_schema_sql_file = cfg.get('create_table_schema_sql_file', 'create_dap_table_schema.sql')

        self.acs_tables_version_info_file =cfg.get('acs_tables_version_info_file', 'acs_version_info.json')
        self.dap_schema_info_file = cfg.get('dap_schema_info_file', 'dap_schema_info.json')
        self.dap_pipeline_metadata_file = cfg.get('dap_pipeline_metadata_file', 'pipeline_metadata.json')

        self.acs_schemas = cfg.get("acs_schemas", [
            "gold_entity",
            "gold_wos",
            "gold_pprn"]
            )
        
        self.dap_schemas = cfg.get("dap_schemas", [
            "dap_entity_wos",
            "dap_metrics_wos",
            "dap_entity_pprn",
            "dap_metrics_pprn",
            "dap_docs",
            "dap_grant",
            "dap_prod_core",

            "dap_reference",
            "dap_sort_ref",
            "dap_entity_enrich",
            "dap_ops",
            "dap_work"]
            )


class DatabricksSQLClient:
    def __init__(self, server_hostname: str, http_path: str, access_token: str):
        self.server_hostname = server_hostname
        self.http_path = http_path
        self.access_token = access_token

    def execute_sql(
        self,
        statement: str
    ):
        """
        Execute a SQL statement with automatic connection & cursor management.
        """

        with dbsql.connect(
            server_hostname=self.server_hostname,
            http_path=self.http_path,
            access_token=self.access_token
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(statement)
                try:
                    return cursor.fetchall()  # SELECT
                except Exception:
                    return None  # INSERT / UPDATE / DDL


class DapDbManager:

    def __init__(self, **kwargs):

         # Load configuration
        self.cfg = ConfigInfo()
 
        env = kwargs.get("runtime_env",  self.runtime_env)


        self.conn = DatabricksSQLClient(
                server_hostname = self.dev_server_hostname if env == "dev" else self.prod_server_hostname,
                http_path =  self.dev_http_path if env == "dev" else self.prod_http_path,
                access_token = self.dev_access_token if env == "dev" else self.prod_access_token
            )
 
        self.CONTEXT_FACTORIES = {
            "create_schemas": lambda kwargs:FeatureContext(
                    catalog_name=self.catalog_name,
                    schemas=self.dap_schemas,
                    environment=kwargs.get("environment", self.environment), 
                    version=kwargs.get("version", self.version)
                ),
            "purge_schemas": lambda kwargs:FeatureContext(
                    catalog_name=self.catalog_name,
                    schemas=self.dap_schemas,
                    environment=kwargs.get("environment", self.environment), 
                    version=kwargs.get("version", self.version)
                ),
            "clone_schemas": lambda kwargs:FeatureContext(
                    catalog_name=self.catalog_name,
                    schemas=kwargs.get("schemas",self.clone_schemas),
                    environment=kwargs.get("environment", self.environment),
                    source_version=kwargs.get("source_version", self.version),
                    target_version=kwargs.get("target_version", self.version)
                ),
            "create_ops_tables": lambda kwargs:FeatureContext(
                    catalog_name=self.catalog_name,
                    environment=kwargs.get("environment", self.environment),
                    version=kwargs.get("version", self.version),
                    sql_file_path= kwargs.get("sql_file_path", self.create_ops_tables_sql_file),
                    output_path= kwargs.get("output_path", self.output_path)
                ),
            "drop_ops_tables": lambda kwargs:FeatureContext(
                    catalog_name=self.catalog_name,
                    schemas= [self.ops_schema],
                    environment=kwargs.get("environment", self.environment), 
                    version=kwargs.get("version", self.version)
                ),
            "enable_cdc": lambda kwargs:FeatureContext(
                    catalog_name=self.catalog_name,
                    schemas=self.dap_schemas,
                    environment=kwargs.get("environment", self.environment), 
                    version=kwargs.get("version", self.version)
                ),
            "optimize_tables": lambda kwargs:FeatureContext(
                    catalog_name=self.catalog_name,
                    schemas=self.dap_schemas,
                    environment=kwargs.get("environment", self.environment),
                    version=kwargs.get("version", self.version)
                    # zorder_columns=kwargs.get("zorder_columns", None)
                ),
            "insert_dap_tasks": lambda kwargs:FeatureContext(
                    catalog_name= kwargs.get("catalog_name", self.catalog_name),
                    version=kwargs.get("version", self.version),
                    environment=kwargs.get("environment", self.environment),
                    table_name=kwargs.get("table_name", self.upstream_table_name),
                    file_path=kwargs.get("file_path", self.insert_task_sql_file),
                    output_path= kwargs.get("output_path", self.output_path)
                ),
            "insert_dap_registry": lambda kwargs:FeatureContext (
                    catalog_name= kwargs.get("catalog_name", self.catalog_name),
                    version=kwargs.get("version", self.version),
                    environment=kwargs.get("environment", self.environment),
                    table_name=kwargs.get("table_name",self.registry_table_name),
                    file_path=kwargs.get("file_path", self.insert_registry_sql_file),
                    output_path= kwargs.get("output_path", self.output_path)
                ),
            "fetch_acs_versions": lambda kwargs:FeatureContext(
                    catalog_name = kwargs.get("catalog_name", self.src_catalog_name),
                    schemas=kwargs.get("schemas", self.acs_schemas),
                    version=kwargs.get("version", self.src_version),
                    environment=kwargs.get("environment", self.src_environment),
                    file_path=kwargs.get("file_path",  self.acs_tables_version_info_file),
                    output_path= kwargs.get("output_path", self.output_path)
                ),
            "create_watermark_sql": lambda kwargs:FeatureContext(
                    catalog_name = kwargs.get("catalog_name", self.src_catalog_name),
                    schemas= self.acs_schemas,
                    version=kwargs.get("version", self.src_version),
                    environment=kwargs.get("environment", self.src_environment),
                    ops_table_name=kwargs.get("ops_table_name", "dap_watermarks"),
                    watermark_type=kwargs.get("watermark_type", self.watermark_type),
                    file_path=kwargs.get("file_path",  self.acs_tables_version_info_file ),
                    sql_file_path=kwargs.get("sql_file_path", self.watermark_sql_file ),
                    output_path= kwargs.get("output_path", self.output_path)
                ),
             "create_checkpoint_sql": lambda kwargs:FeatureContext(
                    catalog_name = kwargs.get("catalog_name", self.catalog_name),
                    ops_table_name=kwargs.get("ops_table_name", "dap_checkpoints"),
                    version=kwargs.get("version", self.version),
                    environment=kwargs.get("environment", self.environment),
                    file_path=kwargs.get("file_path",  self.dap_pipeline_metadata_file ),
                    sql_file_path=kwargs.get("sql_file_path", "insert_dap_checkpoints.sql" ),
                    output_path= kwargs.get("output_path", self.output_path) 
                ),
            "create_table_schema_sql": lambda kwargs:FeatureContext(
                    catalog_name = kwargs.get("catalog_name", self.catalog_name),
                    schemas=kwargs.get("schemas", self.dap_schemas),
                    version=kwargs.get("version", self.version),
                    environment=kwargs.get("environment", self.environment),
                    file_path=kwargs.get("file_path",  self.dap_schema_info_file),
                    sql_file_path=kwargs.get("sql_file_path", self.create_table_schema_sql_file ),
                    output_path= kwargs.get("output_path", self.output_path) 
                ),
            "run_sql_file":lambda kwargs:FeatureContext(
                    catalog_name = kwargs.get("catalog_name", self.catalog_name),
                    schema=kwargs.get("schema", ""),
                    version=kwargs.get("version", self.version),
                    environment=kwargs.get("environment", self.environment),
                    sql_file_path=kwargs.get("sql_file_path", "")
                ),
            "run_sql": lambda kwargs:FeatureContext(
                    stmt=kwargs.get("stmt", "")
                )   
        }

        self.FEATURE_HANDLERS = {
            "create_schemas": self.create_dap_schemas,
            "purge_schemas": self.purge_dap_schemas,
            "clone_schemas":self.clone_dap_schemas,
            "create_ops_tables": self.create_dap_ops_tables,
            "drop_ops_tables": self.drop_dap_tables,
            "enable_cdc": self.enable_cdc_on_tables,
            "optimize_tables": self.optimize_dap_tables,
            "insert_dap_registry": self.insert_dap_metadata,
            "insert_dap_tasks": self.insert_dap_metadata,
            "fetch_acs_versions": self.fetch_version_for_tables,
            "create_watermark_sql": self.create_watermarks_insert_sql,
            "create_checkpoint_sql": self.create_checkpoint_insert_sql,
            "create_table_schema_sql": self.create_dap_table_schema_sql_file,
            "run_sql_file": self.run_sql_file,
            "run_sql": self.execute_sql_statement
        }

    def __getattr__(self, name):
            return getattr(self.cfg, name)

    # -------------------------------------------------------------------
    # Helper Functions
    # -------------------------------------------------------------------
    
    # save SQL statements to file
    def save_to_file(
            self,
            rows: list[str], 
            file_path: str
        ) -> None:


        with open(file_path, "w", encoding="utf-8") as f:
            for row in rows:
                f.write(row)
                f.write("\n\n")  # separate statements by a blank line

    # dump JSON data to file
    def dump_json_to_file(
            self,
            data, 
            filename: str
        ) -> None:

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
   
   # load JSON data from file
    def load_json_from_file(
            self,
            filename: str
        ) -> Any:

        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)

    # drop version suffix from schema name
    def drop_schema_version(
            self,
            schema: str
        ) -> str:
        """
        Drop trailing version suffix from schema names.

        Handles:
        _v_1_0_1
        _v_1_0
        _v_1_0_1_1
        _v_1_0_1
        """
        if not schema:
            return schema

        return re.sub(r"_v_?\d+(?:_\d+)*$", "", schema)
   
    # sort columns based on predefined rules
    def sort_columns(
            self,
            columns: list[dict]
        ) -> list[dict]:
        def sort_key(col):
            name = col["name"].lower()
            col_type = col["type_name"].lower()

            if col_type in ("array", "map", "struct"):
                return (9, name)  # complex types at the end
            if name == "_id" or name == "id":
                return (0, name)
            if  name == "pipeline_name" or name == "task_name"  or name == "table_name":
                return (0, name)
            if name == "uid":
                return (1, name)
            if name == "pguid" or name == "sp_id" or name == "isi_loc":
                return (2, name)
            if name == "collection_id" or name == "dataset_id" :
               return (7, name)
            if re.fullmatch(r".+_id", name):
                return (3, name)
            if name.endswith("id"):
                return (4, name)
            if name == "key":
                return (5, name)
            if re.fullmatch(r".+_key", name):
                return (6, name)
            if re.fullmatch(r".+_ts", name):
                return (10, name)
            if re.fullmatch(r".+_by", name):
                return (11, name)
            return (8, name)  # remaining columns

        return sorted(columns, key=sort_key)

    # print SQL execution result
    def print_sql_execution_result(self, data):

        if all(isinstance(item, list) for item in data):
            for index, rows in enumerate(data):
                print(f"\nResult set-{index}:\n")
                for row in rows:
                    print(row)  
        else:
            print(f"Result set:\n")
            for row in data:
                print(row)
            
    # create watermark row data structure
    def create_watermark_row(
            self,
            table_name: str,
            lastest_version: int,
            latest_timestamp: str,
            wm_type: WatermarkType
        ) -> Dict[str, Any]:

        def parse_watermark_type(wm_type: WatermarkType):

            match WatermarkType(wm_type):
                case WatermarkType.INCREMENTAL:
                    return lastest_version - 1, "Ready"
                case WatermarkType.DUMPY:
                    return -1, "Success"
                case WatermarkType.BASELINE:
                    return lastest_version, "Ready"
                case _:
                    raise ValueError(f"Unsupported watermark type: {wm_type}")
  
        update_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        start_version, status = parse_watermark_type(wm_type)

        return {
                "batch_id": 1,
                "table_name": table_name,
                "start_version": start_version,
                "end_version": lastest_version,
                "last_processed_version": lastest_version,
                "latest_available_version": lastest_version,
                "start_ts": latest_timestamp,
                "end_ts": latest_timestamp,
                "cdf_enabled": True,
                "status": status,
                "error_message": "",
                "update_ts": update_ts,
                "updated_by": "system"
            }

   # build SQL INSERT statement for watermark metadata
    def build_watermark_insert_sql(
            self,
            table_name: str,
            data: Dict[str, Any]
        ):
        # List of columns in the database
        columns = [
            "batch_id", "table_name", "start_version", "end_version", 
            "last_processed_version", "latest_available_version", 
            "start_ts", "end_ts", "cdf_enabled", "status", 
            "error_message", "update_ts", "updated_by"
        ]
        
        # Ensure that all the keys are in the dictionary
        if not all(key in data for key in columns):
            raise ValueError("Missing one or more required keys in the input data.")

        # Prepare the SQL INSERT statement
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ("

        # Add the values from the dictionary, ensuring proper formatting for each field type
        values = []
        for column in columns:
            value = data[column]
            if isinstance(value, str):  # String values should be wrapped in quotes
                value = f"'{value}'"
            elif isinstance(value, bool):  # Boolean values should be converted to 1/0
                value = '1' if value else '0'
            elif isinstance(value, (int, float)):  # Numbers don't need quotes
                value = str(value)
            elif isinstance(value, (type(None))):  # Null values for missing/empty fields
                value = 'NULL'
            values.append(value)
        
        # Finalize the SQL statement
        sql += f"{', '.join(values)});"

        return sql

       # Read a SQL file, replace placeholders, split statements, and execute them one by one.
    
    # build INSERT SQL for dap_checkpoints table
    def build_checkpoint_insert_sql(
            self,
            table_name: str,
            pipeline_name: str, 
            batch_id: int, 
            status: str, 
            updated_by: str
        ):
        # Get the current timestamp for 'update_ts'
        update_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Define default values for fields that are not passed
        default_values = {
            "start_ts": "NULL",  # Use NULL for start_ts
            "end_ts": "NULL",    # Use NULL for end_ts
            "processed_ts": 0,   # Use 0 for processed_ts
            "rows_read": 0,      # Use 0 for rows_read
            "rows_written": 0,   # Use 0 for rows_written
            "retry": 0,          # Use 0 for retry
            "error_message": "NULL",  # Use NULL for error_message
        }
        
        # Build the column names and the corresponding values
        columns = [
            "pipeline_name", "batch_id", "start_ts", "end_ts", "processed_ts",
            "status", "rows_read", "rows_written", "retry", "error_message", 
            "update_ts", "updated_by"
        ]
        
        values = [
            f"'{pipeline_name}'", batch_id, default_values["start_ts"], default_values["end_ts"], default_values["processed_ts"],
            f"'{status}'", default_values["rows_read"], default_values["rows_written"], default_values["retry"], default_values["error_message"], 
            f"'{update_ts}'", f"'{updated_by}'"
        ]

        # Create the SQL statement
        sql_statement = f"""
INSERT INTO {table_name} (
    {', '.join(columns)}
) VALUES (
    {', '.join(map(str, values))}
);
"""

        return sql_statement
    
    # generate CREATE TABLE SQL from table definition
    def generate_create_dap_table_sql(
            self,
            table_def: dict
        ) -> str:

        schema = self.drop_schema_version(table_def["schema_name"])
        table = table_def["table_name"]

        columns_sql = []
 
        for col in self.sort_columns(table_def["columns"]):
            col_def = f'{col["name"]} {col["type_text"].upper()}'
            if not col["nullable"]:
                col_def += " NOT NULL"
            columns_sql.append(col_def)

        columns_block = ",\n    ".join(columns_sql)

        return f"""CREATE TABLE  IF NOT EXISTS {schema}_{{version}}.{table} (
    {columns_block}
    );"""

    # execute SQL file with schema replacement
    def execute_sql_file(
        self,
        sql_file_path: str,
        replacement: str,
    ):
        """
        Read a SQL file, replace placeholders, split statements,
        and execute them one by one.
        """

        sql_text = Path(sql_file_path).read_text()

        # Replace placeholders like ${schemaName}
        #for key, value in replacements.items():
        #    sql_text = sql_text.replace(f"${{{key}}}", value)

        # Split on semicolon, remove empty statements
        statements = [
            stmt.strip()
            for stmt in sql_text.split(";")
            if stmt.strip()
        ]
        data = []
        for stmt in statements:
            stmt = stmt.format(schema=replacement)  if replacement else stmt  # add semicolon back
            print(f"Executing SQL statement:\n{stmt}\n")
            d = self.conn.execute_sql(stmt)
            data.append(d)

        return data
   
   
    # -------------------------------------------------------------------
    # Feature Functions
    # -------------------------------------------------------------------

    # Create specified DAP schemas.
    def create_dap_schemas(
            self,
            ctx: FeatureContext
        ):
        
        for schema in ctx.schemas:
            print(f"Creating schema: {ctx.catalog_name}_{ctx.environment}.{schema}_{ctx.version}")
            stmt = f"CREATE SCHEMA IF NOT EXISTS {ctx.catalog_name}_{ctx.environment}.{schema}_{ctx.version}"
            self.conn.execute_sql(stmt)

    # Drop specified DAP schemas.
    def purge_dap_schemas(
            self,
            ctx: FeatureContext
        ):
        
        for schema in ctx.schemas:
            print(f"Dropping schema: {ctx.catalog_name}_{ctx.environment}.{schema}_{ctx.version}") 
            stmt = f"DROP SCHEMA IF EXISTS {ctx.catalog_name}_{ctx.environment}.{schema}_{ctx.version} CASCADE"
            self.conn.execute_sql(stmt)
    
    # Clone DAP schemas from source version to target version.
    def clone_dap_schemas(
            self,
            ctx: FeatureContext
        ):
        
        for schema in ctx.schemas:
            print(f"Cloning schema: {ctx.catalog_name}_{ctx.environment}.{schema} from version {ctx.source_version} to {ctx.target_version}")
            source_schema = f"{ctx.catalog_name}_{ctx.environment}.{schema}_{ctx.source_version}"
            target_schema = f"{ctx.catalog_name}_{ctx.environment}.{schema}_{ctx.target_version}"

            stmt = f"SHOW TABLES IN {source_schema}"
            tableList = self.conn.execute_sql(stmt) 
            tables = [row.tableName for row in tableList]
            for tbl in tables:
                stmt = f"CREATE TABLE {target_schema}.{tbl} DEEP CLONE {source_schema}.{tbl}"
                print(stmt)
                self.conn.execute_sql(stmt)
    
    # Create DAP ops tables in specified schema.
    def create_dap_ops_tables(
            self,
            ctx: FeatureContext
        ):
          
        schema_name = f"{ctx.catalog_name}_{ctx.environment}.{self.ops_schema}_{ctx.version}"
        print(f"Creating tables in schema: {schema_name}")

        self.execute_sql_file(
            sql_file_path=ctx.file_path,
            replacement=schema_name
        )
   
    # Drop all DAP tables in specified schemas.
    def drop_dap_tables(
            self,
            catalog_name: str,
            schemas: list,
            environment: str,
            version: str
        ):
        
        for schema in schemas:
            schema_name = f"{catalog_name}_{environment}.{schema}_{version}"
            print(f"Dropping tables in schema: {schema_name}")

            stmt = f"SHOW TABLES IN {schema_name}"  
            tableList = self.conn.execute_sql(stmt) 
            tables = [row.tableName for row in tableList]
            for tbl in tables:
                stmt = f"DROP TABLE IF EXISTS {schema_name}.{tbl} "
                self.conn.execute_sql(stmt)
    
    # Enable CDC on all DAP tables.
    def enable_cdc_on_tables(
            self,
            ctx: FeatureContext
        ):
        
        for schema in ctx.schemas:
            schema_name = f"{ctx.catalog_name}_{ctx.environment}.{schema}_{ctx.version}"
            print(f"Enabling CDC on tables in schema: {schema_name}")

            stmt = f"SHOW TABLES IN {schema_name}"  
            tableList = self.conn.execute_sql(stmt) 
            tables = [row.tableName for row in tableList]
            for tbl in tables:
                stmt = f"ALTER TABLE {schema_name}.{tbl} SET TBLPROPERTIES (delta.enableChangeDataFeed = true)      "
                self.conn.execute_sql(stmt)
    
    # Optimize all DAP tables with optional ZORDER columns.
    def optimize_dap_tables(
            self,
            ctx: FeatureContext
        ): 

        for schema in ctx.schemas:
            schema_name = f"{ctx.catalog_name}_{ctx.environment}.{schema}_{ctx.version}"
            print(f"Optimizing tables in schema: {schema_name}")

            stmt = f"SHOW TABLES IN {schema_name}"  
            tableList = self.conn.execute_sql(stmt) 
            tables = [row.tableName for row in tableList]
            for tbl in tables:
               # if ctx.zorder_columns and tbl in ctx.zorder_columns:
               #     cols = ", ".join(ctx.zorder_columns[tbl])
               #     stmt = f"OPTIMIZE {schema_name}.{tbl} ZORDER BY ({cols})"
               # else:
                stmt = f"OPTIMIZE {schema_name}.{tbl}"
                self.conn.execute_sql(stmt)
   
    # Optimize a single DAP table with optional ZORDER columns.
    def optimize_dap_table(
            self,
            table_name: str,
            zorder_columns: Optional[List[str]] = None
        ): 

        print(f"Optimizing tables in schema: {table_name}")
        cols = ", ".join(zorder_columns)
        stmt = f"OPTIMIZE {table_name} ZORDER BY ({cols})"
        self.conn.execute_sql(stmt) 
     # Fetch tables from Unity Catalog and return structured metadata.
    
    # fetch version info for tables
    def fetch_version_for_tables(
            self,
            ctx: FeatureContext
        ) -> list:
        """
        Fetch tables from Unity Catalog and return structured metadata.
        Returns:
            list of dict: Each dict represents a table with requested metadata
        """

        all_tables = []
  
        for schema in ctx.schemas:
            schema_name = f"{ctx.catalog_name}_{ctx.environment}.{schema}_{ctx.version}"
            print(f"Fetching data for schema: {schema_name} ")

            stmt = f"SHOW TABLES IN {schema_name}"
            tableList = self.conn.execute_sql(stmt) 
            tables = [row.tableName for row in tableList]
            for tbl in tables:
                table_name = f"{schema_name}.{tbl}"
                stmt = f"""
                    SELECT MAX(version) AS latest_version, MAX(timestamp) AS latest_timestamp 
                    FROM ( 
                        DESCRIBE HISTORY {table_name} 
                    )"""
                # print(stmt)
                data = self.conn.execute_sql(stmt)[0].asDict()
                row = {
                    "table_name": table_name,
                    "latest_version": data["latest_version"],
                    "latest_timestamp": data["latest_timestamp"].isoformat()
                }

                all_tables.append(row)

        self.dump_json_to_file(all_tables, f"{ctx.output_path}/{ctx.file_path}")

        return all_tables

    # insert pipeline task metadata into delta table
    def insert_dap_metadata(
            self,
            ctx: FeatureContext
        ):

        schema = f"{ctx.catalog_name}_{ctx.environment}.{self.ops_schema}_{ctx.version.replace('.', '_')}"
        
        self.conn.execute_sql(f"DELETE FROM {schema}.{ctx.table_name}")
        self.execute_sql_file(
            sql_file_path = f"{ctx.output_path}/{ctx.file_path}",
            replacement =  schema
        )

    # insert watermark data into delta table
    def create_watermarks_insert_sql(
            self,
            ctx: FeatureContext
        ): 
        sql_statements = []

        filename = f"{ctx.output_path}/{ctx.file_path}"

        print(f"Process acs version data file: {filename} , {ctx.watermark_type}")
        if Path(filename).exists():
            print(f"Loading version info from file: {filename}")
            version_infos = self.load_json_from_file( f"./{filename}")
        else:
            print(f"Fetching version info for tables in schemas: {ctx.schemas}")
            version_infos = self.fetch_version_for_tables( FeatureContext(
                            catalog_name = ctx.catalog_name, 
                            schemas = ctx.schemas,
                            environment = ctx.environment,
                            version = ctx.version,
                            file_path = ctx.file_path 
                        )
                )
        
        ops_table_name = f"{{schema}}.{ctx.ops_table_name}"
   
        for table_version in version_infos:
            data = self.create_watermark_row(
                table_name = table_version['table_name'],
                lastest_version = table_version['latest_version'],
                latest_timestamp = table_version['latest_timestamp'],
                wm_type = ctx.watermark_type
            )
            stmt = self.build_watermark_insert_sql(ops_table_name, data)
            # self.conn.execute_sql(sql_statement)
            sql_statements.append(stmt)

        self.save_to_file(sql_statements,  f"{ctx.output_path}/{ctx.sql_file_path}")
        print(f"Saved watermark INSERT statements to {ctx.output_path}/{ctx.sql_file_path}")
        #ops_table_name = f"{ctx.catalog_name}_{ctx.environment}.{self.ops_schema}_{ctx.version.replace('.', '_')}"
        #self.execute_sql_file(
        #    sql_file_path = self.watermark_sql_file,
        #    replacement =  ops_table_name  # no replacement needed here
        #)

    # insert checkpoint data into delta table
    def create_checkpoint_insert_sql(
            self,
            ctx: FeatureContext
        ): 
    
        sql_statements = []
        pipeline_names = []

        filename = f"{ctx.output_path}/{ctx.file_path}"
        print(f"Process acs pipeline data file: {filename}" )
              
        if Path(filename).exists():
            print(f"Loading pipeline info from file: {filename}")
            data = self.load_json_from_file( f"./{filename}")
            pipeline_names =  list(data.keys())
        else:
            print(f"Fetching pipeline info for tables in schemas: {ctx.schemas}")
              
        ops_table_name = f"{{schema}}.{ctx.ops_table_name}"
   
        for pipeline in pipeline_names:
            stmt = self.build_checkpoint_insert_sql(
                table_name = ops_table_name,
                pipeline_name=pipeline, 
                batch_id= 1, 
                status="Ready", 
                updated_by="system"
            )
            # self.conn.execute_sql(sql_statement)
            sql_statements.append(stmt)

        self.save_to_file(sql_statements,  f"{ctx.output_path}/{ctx.sql_file_path}")
        print(f"Saved checkpoint INSERT statements to {ctx.output_path}/{ctx.sql_file_path}")
        #ops_table_name = f"{ctx.catalog_name}_{ctx.environment}.{self.ops_schema}_{ctx.version.replace('.', '_')}"
        #self.execute_sql_file(
        #    sql_file_path = self.watermark_sql_file,
        #    replacement =  ops_table_name  # no replacement needed here
        #)


    # generate CREATE TABLE SQL file from table definitions
    def create_dap_table_schema_sql_file(
            self,
            ctx: FeatureContext
        ) -> None:

        table_defs = self.load_json_from_file(f"{ctx.output_path}/{ctx.file_path}")
        sql_statements = []

        for table_def in table_defs:
            sql = self.generate_create_dap_table_sql(table_def)
            sql_statements.append(sql)

        # output_file = f"create_tables_schema.sql"
        self.save_to_file(sql_statements, f"{ctx.output_path}/{ctx.sql_file_path}")
        print(f"Saved CREATE TABLE statements to {ctx.output_path}/{ctx.sql_file_path}")

    # execute a single SQL statement
    def execute_sql_statement(
        self,
        ctx: FeatureContext
    ):
        """
        Execute a single SQL statement.
        """

        print(f"Executing SQL statement:\n{ctx.stmt}\n")
        #stmt = ctx.stmt[0] if isinstance(ctx.stmt, tuple) else ctx.stmt
        rows = self.conn.execute_sql(ctx.stmt)

        print("SQL execution result:\n")
        self.print_sql_execution_result(rows)
    
    # Run SQL file with schema context.
    def run_sql_file(
            self,
            ctx: FeatureContext
        ):

        schema_name = f"{ctx.catalog_name}_{ctx.environment}.{ctx.schema}_{ctx.version}" if ctx.schema else ""
        print(f"Executing SQL file: {ctx.sql_file_path} with schema: {schema_name}")

        data = self.execute_sql_file(
            sql_file_path = ctx.sql_file_path,
            replacement =  schema_name
        )
        print("SQL execution result:\n")
        self.print_sql_execution_result(data)
            

    # run feature based on feature name with  context handling
    def run_feature(
            self,
            feature: str, **kwargs):
        try:
            ctx = self.CONTEXT_FACTORIES[feature](kwargs)
            self.FEATURE_HANDLERS[feature](ctx)
        except KeyError:
            raise ValueError(f"Unsupported feature: {feature}")


if __name__ == "__main__":

    os.system('clear')

    if len(sys.argv) < 2:
        print( 
            f"Please provide a feature name as the first argument ...\n\n"
            f"- Usage:  python schema_ops.py <feature_name> [param=value ...]\n"
            f"- Feature:  create_schemas | purge_schemas | clone_schemas | create_ops_tables | drop_ops_tables | \n"
            f"            enable_cdc | optimize_tables | fetch_acs_versions | create_watermark_sql | run_sql | run_sql_file\n"
            f"- Parameters: environment (default: prod), version (default: v_1_0_1), source_version, target_version \n\n"
            f"- Examples: \n"
            f"   python schema_ops.py create_schemas environment=prod version=v_1_0_1\n"
            f"   python schema_ops.py run_sql_file sql_file_path=path/to/file.sql environment=prod\n"
            f"   python schema_ops.py create_watermark_sql  environement=dev  version=v_1_0_1  watermark_type=baseline\n"
           # f"Example: python schema_ops.py optimize_tables environment=prod version=v_1_0_1 zorder_columns='{\"dap_entity_wos\": [\"publication_year\", \"document_type\"]}'"
        )  
        sys.exit(1)    

    feature_name = sys.argv[1]

    print(f"Running feature: {feature_name}")
    
    # Parse additional optional parameters from CLI
    kwargs = {}
    for arg in sys.argv[2:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            # Convert comma-separated values into list for 'schemas'
            if k == "schemas":
                v = v.split(",")
            kwargs[k] = v

    # env = kwargs.get("environment", "prod")

    try:
        db_mgr = DapDbManager(**kwargs) 
        db_mgr.run_feature( feature=feature_name, **kwargs)

    except Exception as e:
        print(f"Error running feature '{feature_name}': {e}")

# python schema_ops.py run_sql stmt="show tables in ag_ra_search_analytics_data_uat.dap_ops_v_1_0_1" 
# python schema_ops.py run_sql_file sql_file_path=test.sql
# python schema_ops.py run_sql_file sql_file_path=v_1_0_1/insert_watermarks.sql schema=dap_ops 

