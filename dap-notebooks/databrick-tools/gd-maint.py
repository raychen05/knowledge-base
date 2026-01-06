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
import pandas as pd
from enum import Enum
from dataclasses import dataclass, field
from textwrap import dedent

# -------------------------------------------------------------------
# General Config and Feature class
# -------------------------------------------------------------------

@dataclass
class FeatureContext:
    params: Dict[str, Any] = field(default_factory=dict)

    def __init__(self, **kwargs):
        object.__setattr__(self, "params", kwargs)

    def __getattr__(self, item):
        return self.params.get(item)
 

class ConfigInfo:

    def __init__(self):

        def load_yaml(path: str) -> dict:

            with open(path, "r") as f:
                return yaml.safe_load(f) or {}

        cfg = load_yaml("./config.yaml")

        self.output_path = cfg.get("output_path", ".") 

        # env = cfg.get("runtime_env", "prod")
        self.prod_workspace_url = cfg.get(f"prod_url", "https://clarivate-ag-prod.cloud.databricks.com")
        self.prod_token =  cfg.get(f"prod_token", "")
        self.dev_workspace_url = cfg.get(f"dev_url", "https://clarivate-ag-dev.cloud.databricks.com")
        self.dev_token =  cfg.get(f"dev_token", "")

        self.src_catalog_name = cfg.get("source_catalog_name", "ag_content_ims_acs")
        self.src_environment =  cfg.get("source_environment", "prod")
        self.src_schema_version = cfg.get("source_schema_version", "v_1_0_1")

        self.tgt_catalog_name = cfg.get("target_catalog_name", "ag_ra_search_analytics_data")
        self.tgt_environment =  cfg.get("target_environment", "dev")
        self.tgt_schema_version = cfg.get("target_schema_version", "v1_0")

        self.src_udm_catalog = cfg.get("source_udm_catalog_name", "ag_content_ims_udm")

        self.left_schema_version = cfg.get("cp_left_schema_version", "_")  
        self.right_schema_version = cfg.get("cp_right_schema_version", "v_1_0_1")
        self.release_version = cfg.get("bundle_release_version", "1.3")
        
        self.reistry_table_name = cfg.get("registry_table_name", "dap_pipeline_registry")
        self.upstream_table_name = cfg.get("upstream_table_name", "dap_pipeline_task_upstream")

        self.insert_task_sql_file = cfg.get("insert_task_sql_file", "ddl/insert_da_task_upstream.sql")
        self.insert_registry_sql_file = cfg.get("insert_registry_sql_file", "ddl/insert_dap_pipeline_registry.sql")
        self.pipeline_metadata_file = cfg.get("pipeline_metadata_file", "pipeline_metadata")
        self.dap_lineage_file = cfg.get("dap_lineage_file", "dap_lineage.csv")
        self.acs_schema_info_file = cfg.get("acs_schema_info_file", "acs_schema_info.json")
        self.dap_schema_info_file = cfg.get('dap_schema_info_file', 'dap_schema_info.json')
        self.acs_table_relation_file = cfg.get("acs_table_relation_file", "acs_table_relation.json") 
        self.dap_job_list_file = cfg.get("dap_job_list_file", "dap_job_list.csv")
        self.dap_table_lineage_file = cfg.get("dap_table_lineage_file", "dap_ftable_lineage.json")
        self.anchor_config_file = cfg.get("anchor_config_file", "anchor_tables.yaml")
        self.golden_data_path = cfg.get("golden_data_path", "golden")
        self.anchor_sql_file = cfg.get("anchor_sql_file", "anchor_query.sql")

        self.acs_schemas = cfg.get("acs_schemas", [
            "gold_entity",
            "gold_wos",
            "gold_pprn"]
            )
        
        self.udm_schemas = cfg.get("udm_schemas", [
            "patent_org_relationship", 
            "researcher_grants_relationship", 
            "topic_model"]
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
            "dap_work" ]
            )

# -------------------------------------------------------------------
# General Helper Function
# -------------------------------------------------------------------
class Utils:

      # extract name from email address
    def name_from_email(
            self, email: str) -> str:
        local_part = email.split("@")[0]
        name_parts = (
            local_part
            .replace("_", " ")
            .replace(".", " ")
            .replace("-", " ")
            .split()
        )
        return " ".join(part.capitalize() for part in name_parts)

    # check if two lists have at least one common element
    def has_common_id(
            self, a, b):
        """
        Return True if at least one element in list a exists in list b.
        """
        b_set = set(b)  # convert to set for O(1) lookups
        return any(x in b_set for x in a)

    # drop schema version suffix from schema names
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

    # safely get nested dictionary values
    def nested_get(
            self, d, *keys, default=None):
        for key in keys:
            d = d.get(key, {})
        return d or default

    # append a raw CSV line to a file
    def append_csv_line(
            self,
            row: str, 
            filename: str
        ) -> None:
        """
        Append a raw CSV line to a file.
        Assumes `line` is already CSV-formatted.
        """
        with open(filename, "a", encoding="utf-8") as f:
            if not row.endswith("\n"):
                row += "\n"
            f.write(row)


    # dump JSON data to a file
    def dump_json_to_file(
            self,
            data, 
            filename: str
        ) -> None:

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # read JSON lines from a file
    def read_json_lines(
            self,
            filename: str
        ) -> List[Dict[str, Any]]:

        rows = []

        with open(filename, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue  # skip empty lines
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON on line {line_no}: {e}")

        return rows

    def ensure_path_exists(
            self,
            filename: str
        ) -> None:
        """
        Ensure the directory for the given file path exists.
        Creates directories if they do not exist.
        """
        if not os.path.exists(filename):
            os.makedirs(filename)
            print(f"Folder created at {filename}")
        else:
            print(f"Folder already exists at {filename}")

    # save SQL statements to a file
    def save_to_file(
            self,
            rows: list[str], 
            filename: str
        ) -> None:

        with open(filename, "w", encoding="utf-8") as f:
            for row in rows:
                f.write(row)
                f.write("\n\n")  # separate statements by a blank line

    def load_yaml(path: str) -> dict:

        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    
    def delete_file(self, file_path: str) -> None:
        if os.path.exists(file_path):
            os.remove(file_path)

    def load_json_file(self, file_path: str) -> Any:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)


# -------------------------------------------------------------------
# Databricks API Client Functions
# -------------------------------------------------------------------
class DatabricksAPIClient:

    def __init__(self, cfg: ConfigInfo):

        self.prod_workspace_url = cfg.prod_workspace_url
        self.prod_token =  cfg.prod_token
        self.dev_workspace_url = cfg.dev_workspace_url
        self.dev_token =  cfg.dev_token

        self.utils = Utils()

    # -------------------------------------------------------------------
    #   Databrick API call functions 
    # -------------------------------------------------------------------

    def call_api(
            self,
            url: str,
            params: dict = {},
            environment: str = "prod" 
            ):
        
        print(f"Calling API: {url} with params: {params}")

        workspace_url = self.prod_workspace_url if environment == "prod" else self.dev_workspace_url
        token = self.prod_token if environment == "prod" else self.dev_token

        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{workspace_url}{url}", headers=headers, params=params)
        resp.raise_for_status()
        
        return resp.json()
    
    def fetch_schemas(
            self,
            catalog_name: str,
            environment: str = "prod"
        ) -> list:
        """
        Fetches schema list from Unity Catalog API for a given catalog.
        Returns:
            list of schema names
        """

        return  self.call_api( 
                    url = "/api/2.1/unity-catalog/schemas", 
                    params =  {"catalog_name": catalog_name},
                    enviroenment= environment
                )
        
    def fetch_tables(
            self,
            catalog_name: str, 
            schema_name: str,
            environment: str = "prod"
        ) -> list:
        """
        Fetch tables from Unity Catalog and return structured metadata.

        Returns:
            list of dict: Each dict represents a table with requested metadata
        """

        return  self.call_api( 
                    url = "/api/2.1/unity-catalog/tables", 
                    params =  {"catalog_name": catalog_name, "schema_name": schema_name} ,
                    environment= environment
                )

    def fetch_jobs(
            self,
            release_version: str,
            environment: str = "prod"
        ) -> list:
        """
        Fetches job list from Databricks Jobs API.
        Returns:
            list of jobs
        """
        # extract  job meta data from job settings tags
        def parse_tags(
                data: dict,
                release_version: str = "1.3"
            ) -> dict:

            jobs = []
            for job in data.get("jobs", []):
                job_id = job.get("job_id")
                # Safe extraction of on_failure email
                email_on_failure = (
                    job.get("settings", {})
                        .get("email_notifications", {})
                        .get("on_failure")
                )
                # Flatten tags if present
                name = job.get('settings', {}).get('name').split("_")[0]
                version = job.get('settings', {}).get('name').split("_")[-1]
                tags = job.get("settings", {}).get("tags", {})
                flat_tags = {f"tag_{k}": v for k, v in tags.items()}

                # Combine all info
                if(flat_tags and flat_tags['tag_Product'] == "wosri" and version == release_version):
                    job_info = {
                        "job_id": job_id,
                        "name": name,
                        "email_on_failure": email_on_failure,
                        **flat_tags
                    }

                    jobs.append(job_info)

            return jobs



        job_list = []
        next_page_token = None

        while True:
            params = {"page_token": next_page_token} if next_page_token else {}
            data = self.call_api( 
                    url = "/api/2.1/jobs/list", 
                    params = params,
                    environment= environment
                )
            jobs = parse_tags(data, release_version)
            job_list.extend(jobs or [])
            
            if data.get("has_more"):
                next_page_token = data.get("next_page_token")
            else:
                break
           
        return job_list
     
    def fetch_job_details(
            self,
            job_id: str,
            environment: str = "prod"
        ) -> dict:
        """
        Fetches job details from Databricks Jobs API.
        Returns:
            job details dict
        """

        return  self.call_api( 
                url = "/api/2.1/jobs/get", 
                params =  {"job_id": job_id},
                environment= environment
            )
    
    def fetch_lineage(
            self,
            table_name: str,
            environment: str = "prod"
            ) -> dict:
        """
        Fetches table lineage info from Databricks API.
        Returns:
            lineage dict
        """

        return  self.call_api( 
                    url = "/api/2.0/lineage-tracking/table-lineage", 
                    params =  {"table_name": table_name,  "include_entity_lineage": "true"},
                    environment= environment
                )
    
    
    # -------------------------------------------------------------------
    #  Schema, Table, Lineage Information Extract functions 
    # -------------------------------------------------------------------

    # get a list of schemas for specified catalog
    def fetch_schema_list(
            self,
            catalog_name: str,
            environment: str
        ) -> list:
        """
        Fetches schema list from Unity Catalog API for a given catalog.
        Returns:
            list of schema names
        """

        data = self.fetch_schemas(
                    catalog_name=catalog_name, 
                    environment=environment
                )

        # exclude information_schema
        schema_names = [s["name"] for s in data.get("schemas", []) if s["name"] != "information_schema"]

        return schema_names

    # get job meta data for specified job id
    def fetch_job_info(
            self,
            job_id: str,
            environment: str
        ) -> dict:
        """
        Fetches job details from Databricks Jobs API and returns selected metadata.

        Returns:
            dict: {
                'Component': ...,
                'Owner': ...,
                'Product': ...,
                'tasks': [(task_key, job_cluster_key), ...]
            }
        """

        data =self.fetch_job_details(
                job_id=job_id, 
                environment=environment
            )
        # print(json.dumps(data, indent=2))  # For debugging

        # Extract tags safely
        name = data.get('settings', {}).get('name').split("_")[0]
        tags = data.get('settings', {}).get('tags', {})
        component = name # tags.get('Component')
        owner = tags.get('Owner')
        product = tags.get('Product')

        email = self.utils.nested_get(data, 'settings', 'email_notifications', 'on_failure')

        # Extract tasks
        tasks = data.get('settings', {}).get('tasks', [])
        task_list = []
        for t in tasks:
            task_key = t.get('task_key')
            job_cluster_key = t.get('job_cluster_key')
            task_list.append((task_key, job_cluster_key))

        return {
            "pipeline": component,
            "owner": owner,
            "email": email,
            "product": product,
            "tasks": task_list
        }

    # get table meta data and columns
    def fetch_tables_info(
            self,
            catalog_name: str, 
            schema_name: str,
            environment: str,
            filter_columns: List[str] = None,
        ) -> list:
        """
        Fetch tables from Unity Catalog and return structured metadata.

        Returns:
            list of dict: Each dict represents a table with requested metadata
        """

        # filter table fields based on specified columns
        def filter_table_fields(
                table_dict: dict, 
                filter_columns: list | None
            ) -> dict:

            """
            Reduce table_dict to only keys in filter_columns.
            If filter_columns is None, return all fields.
            """
            if not filter_columns:
                return table_dict

            return {
                k: v
                for k, v in table_dict.items()
                if k in filter_columns
            }


        data = self.fetch_tables(
                catalog_name=catalog_name,
                schema_name=schema_name,
                environment=environment
            )
    
        # parse tables info 
        tables_info = []

        for tbl in data.get("tables", []):
            full_name = tbl.get("full_name") or f'{tbl.get("catalog_name")}.{tbl.get("schema_name")}.{tbl.get("name")}'
            catalog = tbl.get("catalog_name")
            schema = tbl.get("schema_name")
            name = tbl.get("name")
            
            # Columns info
            columns_info = []
            for col in tbl.get("columns", []):
                columns_info.append({
                    "name": col.get("name"),
                    "type_text": col.get("type_text"),
                    "type_name": col.get("type_name"),
                    "nullable": col.get("nullable")
                })
            
            # Delta CDF property
            properties = tbl.get("properties", {})
            delta_props = properties.get("delta", {})
            cdf = delta_props.get("enableChangeDataFeed", False)

            table_dict = {
                "full_name": full_name,
                "catalog_name": catalog,
                "schema_name": schema,
                "table_name": name,
                "cdf": cdf,
                "columns": columns_info
            }
            
            tables_info.append(
                filter_table_fields(table_dict, filter_columns)
            )

        return tables_info

    # get table schema info for specified catalog and schemas
    def fetch_table_schemas(
            self,
            catalog_name: str, 
            schemas: List,
            environment: str,
            version: str
        ) -> list:
        """
        Fetch tables from Unity Catalog and return structured metadata.

        Returns:
            list of dict: Each dict represents a table with requested metadata
        """
        
        # sort tables and columns
        def sort_tables_and_columns(
                tables: list[dict]
            ) -> list[dict]:

            """
            Sort tables by full_name (ASC),
            and sort columns by column name (ASC) inside each table.
            """

            # Sort columns inside each table
            for table in tables:
                columns = table.get("columns", [])
                if isinstance(columns, list):
                    columns.sort(key=lambda c: c.get("name", ""))

            # Sort tables by full_name
            return sorted(tables, key=lambda t: t.get("full_name", ""))


        all_tables = []
        catalog_name = f"{catalog_name}_{environment}"

        for schema in schemas:
            schema_name =  f"{schema}_{version}".removesuffix("_")
            tables = self.fetch_tables_info(
                    catalog_name = catalog_name, 
                    schema_name = schema_name, 
                    environment= environment,
                    filter_columns=["schema_name", "table_name", "columns"]
                )
            all_tables.extend(tables)
        
        all_tables = sort_tables_and_columns(all_tables)

        return all_tables

    # get table lineage info (upstream & downstream)for specified table
    def fetch_table_lineage(
            self,
            table_name: str,
            environment: str
            ) -> tuple:
        """
        Fetches table lineage info from Databricks API and returns upstreams and downstreams.
        Returns:
            tuple: (upstreams, downstreams), each is a list of dicts with requested fields
        """

        data = self.fetch_lineage(
                    table_name=table_name, 
                    environment=environment
                )
        #data= json.loads(res)
        
        # parse upstreams and downstreams
        def extract_tables(tables_list, direction: str = "upstream"):
            result = []
            for t in tables_list:
                # Extract job_id correctly
                table_info = t.get("tableInfo", {})
                job_infos = t.get("jobInfos", [])

                # Handle jobInfos: could be missing, None, or empty
                job_infos = t.get("jobInfos") or []
                job_ids = [j.get("job_id") for j in job_infos if j.get("job_id") is not None]
                # Optional: deduplicate while preserving order
                job_ids = list(dict.fromkeys(job_ids))

                # Detect JOB-only lineage (no tableInfo but has jobs)
                is_job_only = (
                    not table_info.get("name")
                    and not table_info.get("catalog_name")
                    and job_ids
                )
                if is_job_only:
                    continue
                    result.append({
                        "type": "JOB_ONLY",
                        "name": "<JOB_ONLY_DOWNSTREAM>" if direction == "downstream" else "<JOB_ONLY_UPSTREAM>",
                        "catalog_name": None,
                        "schema_name": None,
                        "table_type": "JOB",
                        "job_ids": job_ids
                    })
                else:
                    result.append({
                        "type": "TABLE",
                        "name": table_info.get("name"),
                        "catalog_name": table_info.get("catalog_name"),
                        "schema_name": table_info.get("schema_name"),
                        "table_type": table_info.get("table_type"),
                        "job_ids": job_ids
                    })

            return result
   
        upstreams = extract_tables(data.get("upstreams", []), direction="upstream")
        downstreams = extract_tables(data.get("downstreams", []), direction="downstream")

        return upstreams, downstreams

    # get job's tasks for specified job id
    def fetch_tasks(
            self,
            job_id: str,
            environment: str
        ) -> list:
        """
        Fetches job details from Databricks Jobs API and returns selected metadata.

        Returns:
            dict: {
                'Component': ...,
                'Owner': ...,
                'Product': ...,
                'tasks': [(task_key, job_cluster_key), ...]
            }
        """

        data = self.fetch_job_details(
                    job_id=job_id, 
                    environment=environment
                )

        # Extract tasks
        tasks = data.get('settings', {}).get('tasks', [])
        task_list = []
        for t in tasks:
            task_key = t.get('task_key')
            job_cluster_key = t.get('job_cluster_key')
            task_list.append((task_key, job_cluster_key))

        return task_list

    # get list of jobs for all jobs in workspace
    def fetch_jobs_list(
            self, 
            environment: str, 
            release_version: str):
        """
        Analyze Databricks jobs/list API output.
        Returns:
            List[dict]: Flattened job info with job_id, email notifications, and tags
        """
        # API endpoint
        data = self.fetch_jobs(
                    release_version=release_version, 
                    environment=environment
                )

        # Parse and flatten job info
        deduped = list({item["name"]: item for item in data}.values())

        return deduped


# -------------------------------------------------------------------
# Feature Function 
# -------------------------------------------------------------------

class DapGoldenDatasetManager:

    def __init__(self):

        self.cfg = ConfigInfo()
        self.api = DatabricksAPIClient(self)
        self.utils = Utils()

        self.CONTEXT_FACTORIES = {
            "acs_schema": lambda kwargs:FeatureContext(
                    catalog_name = self.src_catalog_name, 
                    schemas = self.acs_schemas,
                    environment = kwargs.get("environment", self.src_environment),
                    version = kwargs.get("version", self.src_schema_version),
                    filename =self.acs_schema_info_file,
                    output_path=kwargs.get("output_path", self.output_path) 
                ),
            "dap_schema": lambda kwargs:FeatureContext(
                    catalog_name = self.tgt_catalog_name, 
                    schemas = self.dap_schemas,
                    environment = kwargs.get("environment", self.tgt_environment),
                    version = kwargs.get("version", self.tgt_schema_version),
                    filename =self.dap_schema_info_file,
                    output_path=kwargs.get("output_path", self.output_path) 
            ),
            "dap_table_lineage": lambda kwargs:FeatureContext(
                    catalog_name=   self.tgt_catalog_name,
                    schemas=self.dap_schemas,
                    version=kwargs.get("version", self.tgt_schema_version),
                    environment=kwargs.get("environment", self.tgt_environment),
                    filename = kwargs.get("filename", self.dap_table_lineage_file), 
                    output_path=kwargs.get("output_path", self.output_path)  
                ),
            "acs_relations":  lambda kwargs:FeatureContext(
                    catalog_name = self.src_catalog_name, 
                    schemas = self.acs_schemas,
                    environment = kwargs.get("environment", self.src_environment),
                    version = kwargs.get("version", self.src_schema_version),
                    filename =self.acs_table_relation_file,
                    output_path=kwargs.get("output_path", self.output_path) 
                ),
            "build_gd_map": lambda kwargs:FeatureContext(
                    catalog_name=   self.tgt_catalog_name,
                    schemas=self.dap_schemas,
                    version=kwargs.get("version", self.tgt_schema_version),
                    environment=kwargs.get("environment", self.tgt_environment),
                    output_path=kwargs.get("output_path", self.output_path)  
                ),
            "create_anchor_sql": lambda kwargs:FeatureContext(
                    years=kwargs.get("years", [2000, 2001]),
                    cte_name=kwargs.get("cte_name", "article_stats"),
                    anchor_config_file=kwargs.get("anchor_config_file", self.anchor_config_file),
                    anchor_sql_file=kwargs.get("anchor_sql_file", self.anchor_sql_file),
                    output_path=kwargs.get("output_path", self.golden_data_path)  
                )
        }


        self.FEATURE_HANDLERS = {
            "acs_schema": self.fetch_table_schema_info,
            "dap_schema": self.fetch_table_schema_info,
            "dap_table_lineage": self.generate_lineages,
            "acs_relations": self.generate_acs_tables_relationships,
            "build_gd_map": self.build_relationships_with_lineage,
            "create_anchor_sql": self.create_anchor_table_sql
        }

    def __getattr__(self, name):
            return getattr(self.cfg, name)
      
    # -------------------------------------------------------------------
    # Feature Function 
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

 
    def save_feature_result(
            self,
            data: List[Dict],
            filename: str
        ) -> Any:
        """
        Save feature data to files (csv, json, excel).
        """

        filename = filename.rstrip(".json").rstrip(".csv").rstrip(".xlsx")
        self.utils.delete_file( f"{filename}.csv")

        self.utils.dump_json_to_file(data, f"{filename}.json")
        # self.utils.save_to_file(data, f"{filename}.csv")

        df = pd.read_json( f"{filename}.json")
        df.to_csv(f"{filename}.csv", index=False)
        df.to_excel(f"{filename}.xlsx", index=False)

    # get table lineage info (upstream & downstream)for specified table
    def fetch_table_lineage(
            self,
            table_name: str,
            environment: str
            ) -> tuple:
        """
        Fetches table lineage info from Databricks API and returns upstreams and downstreams.
        Returns:
            tuple: (upstreams, downstreams), each is a list of dicts with requested fields
        """

        data = self.api.fetch_lineage(
                    table_name=table_name, 
                    environment=environment
                )
        #data= json.loads(res)
        
        # parse upstreams and downstreams
        def extract_tables(tables_list, direction: str = "upstream"):
            result = []
            for t in tables_list:
                # Extract job_id correctly
                table_info = t.get("tableInfo", {})
                job_infos = t.get("jobInfos", [])

                # Handle jobInfos: could be missing, None, or empty
                job_infos = t.get("jobInfos") or []
                job_ids = [j.get("job_id") for j in job_infos if j.get("job_id") is not None]
                # Optional: deduplicate while preserving order
                job_ids = list(dict.fromkeys(job_ids))

                # Detect JOB-only lineage (no tableInfo but has jobs)
                is_job_only = (
                    not table_info.get("name")
                    and not table_info.get("catalog_name")
                    and job_ids
                )
                if is_job_only:
                    continue
                    result.append({
                        "type": "JOB_ONLY",
                        "name": "<JOB_ONLY_DOWNSTREAM>" if direction == "downstream" else "<JOB_ONLY_UPSTREAM>",
                        "catalog_name": None,
                        "schema_name": None,
                        "table_type": "JOB",
                        "job_ids": job_ids
                    })
                else:
                    result.append({
                        "type": "TABLE",
                        "name": table_info.get("name"),
                        "catalog_name": table_info.get("catalog_name"),
                        "schema_name": table_info.get("schema_name"),
                        "table_type": table_info.get("table_type"),
                        "job_ids": job_ids
                    })

            return result
   
        upstreams = extract_tables(data.get("upstreams", []), direction="upstream")
        downstreams = extract_tables(data.get("downstreams", []), direction="downstream")

        return upstreams, downstreams

    # get table schema info for specified catalog and schemas and write to json
    def fetch_table_schema_info(
            self,
            ctx: FeatureContext
        ) -> List[Dict]:

        print( f"fetch_table_schema_info: catalog={ctx.catalog_name},  "
                f"schemas={ctx.schemas}, version={ctx.version}, filename={ctx.filename}, "
                f"output={ctx.output_path}, environment={ctx.environment}"
            )
        
        all_tables = self.api.fetch_table_schemas(
                    catalog_name = ctx.catalog_name, 
                    schemas = ctx.schemas,
                    environment = ctx.environment,
                    version = ctx.version.removesuffix("_")
                )
    
        filename = f"{ctx.output_path}/{ctx.filename}"
        self.save_feature_result(all_tables, filename)

        return all_tables

    # generate table lineage info (upstream )for specified schemas and write to csv
    def generate_lineages(
            self,
            ctx: FeatureContext
        ):  

        print(
                f"generateDapLineageCsv: catalog={ctx.catalog_name}, "
                f"version={ctx.version}, output={ctx.filename}"
            )
        
        # get table lineage info (upstream )for specified table and write to csv
        def fetch_table_upstream_lineage(
                table_name: str, 
                environment: str
            ) -> List[dict]:
            """
            Fetches table lineage info from Databricks API and returns upstreams and downstreams.
            Returns:
                tuple: (upstreams, downstreams), each is a list of dicts with requested fields
            """

            upstreams, downstreams = self.fetch_table_lineage(
                        table_name=table_name, 
                        environment=environment
                    )

            # parse upstreams
            def extract_tables( tables_list ) -> List[dict]:

                lineages=[]
                for t in tables_list:
                    # Extract job_id correctly
                    source_table_catalog_name = t.get("catalog_name")
                    source_table_schema_name = t.get("schema_name")
                    source_table_name = t.get("name")
                    target_catalog_name, target_schema_name, target_table = table_name.split(".")
                    lineages.append(
                        {   
                            "source_table_catalog": source_table_catalog_name,
                            "source_table_schema":  self.utils.drop_schema_version(source_table_schema_name),
                            "source_table_name": source_table_name,
                            "target_table_catalog":  target_catalog_name,
                            "target_table_schema": self.utils.drop_schema_version(target_schema_name),
                            "target_table_name": target_table
                        }
                    )

                return lineages
            
            return extract_tables( upstreams)


        catalog = f"{ctx.catalog_name}_{ctx.environment}" if ctx.environment else ctx.catalog_name
        filename = f"{ctx.output_path}/{ctx.filename}"

        dap_lineages = []
        for schema in ctx.schemas:
            schemaName = f"{schema}_{ctx.version}"

            tablesList =  self.api.fetch_tables_info(
                        catalog_name=catalog, 
                        schema_name=schemaName,
                        environment=ctx.environment
                    )
            full_names = [t["full_name"] for t in tablesList]

            for tableName in full_names:
                print(f"Processing table: {schemaName}.{tableName}")
                dap_lineages.extend(
                        fetch_table_upstream_lineage(
                            table_name=tableName,
                            environment=ctx.environment
                        )
                )
        
        self.save_feature_result(dap_lineages, filename)
    
    # generate ACS table relationships metadata from table definitions
    def generate_acs_tables_relationships(
            self,
            ctx: FeatureContext,
        ) :
        """
        Create ACS table relationships metadata from table definitions.
        Returns:
            list of dict: Each dict represents a table with primary and foreign keys
        """

        # build CREATE TABLE SQL from table definition
        def build_acs_table_relationships(
                table_def: dict
            ) -> dict:

            # sort columns based on predefined rules
            def select_pk_columns(
                    schema_name: str,
                    table_name: str,
                    columns: list[dict]
                ) -> list[dict]:
                    
                def sort_key(col):
                    name = col["name"].lower()

                    if name == "uid":
                        return (1, name)
                    if name == "pguid" or name == "sp_id" :
                        return (2, name)
                    if name == "org_pguid":
                        return (3, name)
                    if re.fullmatch(r".+_pguid", name):
                        return (4, name)
                    if re.fullmatch(r".+_key", name):
                        return (5, name)
                    if re.fullmatch(r".+_uid", name):
                        return (6, name) 
                    if name == "dataset_id" or name == "variable_id":
                        return (9, name)
                    if re.fullmatch(r"fk_.+_id", name):
                        return (7, name) 
                    if re.fullmatch(r".+_id", name):
                        return (6, name) 
                    if re.fullmatch(r".+_code", name):
                        return (8, name)
                    return (9, name)  # remaining columns
                
                def sort_if_both_end_with_key(values: list[str]) -> list[str]:
                    if len(values) == 2 and all(v.endswith("_key") for v in values):
                        # Ensure category_key is always second
                        if "category_key" in values:
                            first = values[0] if values[1] == "category_key" else values[1]
                            return [first, "category_key"]
                        return sorted(values, reverse=True)
                    return values
                
                def valid_column(col: str) -> bool:
                    return col not in {"doc_id", "__END_AT", "__START_AT","orcid_id", "diasng_id"} and not col.startswith("is")

                def to_pk_fk(schema_name, table_name, rows):
                    if len(rows) < 2:
                        return{
                                "schema": schema_name, 
                                "table_name": table_name, 
                                "pk": rows[0], 
                                "fk": ""
                            }
                    else:
                        rows = sort_if_both_end_with_key(rows)
                        row = rows[1] if len(rows) > 1 and valid_column(rows[1]) else ""
                        return {
                                "schema": schema_name, 
                                "table_name": table_name, 
                                "pk": rows[0], 
                                "fk": row 
                        } 

                pk_columns = sorted(columns, key=sort_key)
                relations = [row["name"] for row in pk_columns[:2] ]

                return to_pk_fk(schema_name, table_name, relations)

            # schema = self.drop_schema_version(table_def["schema_name"])
            schema_name = self.utils.drop_schema_version(table_def["schema_name"])
            table_name = table_def["table_name"]
            pk_columns = select_pk_columns(schema_name, table_name, table_def["columns"])           
            #csv_string = ",".join(pk_columns)     
            #                 
            return pk_columns

        relationships = []

        table_defs = self.api.fetch_table_schemas(
                    catalog_name = ctx.catalog_name, 
                    schemas = ctx.schemas,
                    environment = ctx.environment,
                    version = ctx.version.removesuffix("_")
                )
        
        filename = f"{ctx.output_path}/{ctx.filename}"

        for table_def in table_defs:
            relation = build_acs_table_relationships(table_def)
            relationships.append(relation)
            
        self.save_feature_result(data=relationships, filename=filename)

        return relationships
    
    def build_relationships_with_lineage(
            self,
            ctx: FeatureContext
        ):
        
        print(
                f"build_relationships_with_lineage: catalog={ctx.catalog_name}, "
                f"version={ctx.version}, output={ctx.filename}"
            )
        
        def resolve_entity_name(table_name: str, entity_map: dict) -> str:
            """
            Resolve business entity name from table name using keyword matching.
            """

            table = table_name.lower()

            # Priority: exact domain entities first
            for entity, keywords in entity_map.items():
                for kw in keywords:
                    if kw in table:
                        return entity

            # Fallback: use table name itself
            return table_name
        
        lineage =  self.utils.load_json_file(f"{ctx.output_path}/{self.dap_table_lineage_file}")
        metadata = self.utils.load_json_file(f"{ctx.output_path}/{self.acs_table_relation_file}")
    
        print(f"Total lineages: {len(lineage)}, relationships: {len(metadata)}")

        def build_relationships_with_lineage_for_schema(
                schema: str,
                metadata: list[dict],
                lineage: list[dict],
                entity_map: dict
            ) -> dict:
       # metadata,  lineage,  schema,   entity_map

            tables = {m["table_name"]: m for m in metadata if m["schema"] == schema}

            pk_index = {m["pk"]: m["table_name"] for m in tables.values() if m["pk"]}

            relationships = defaultdict(lambda: {
                "entity": None,
                "primary_key": None,
                "links": [],
                "derived_from": []
            })

            # 1.  PK/FK relationships (authoritative)
            for table, meta in tables.items():
                relationships[table]["entity"] = resolve_entity_name(table, entity_map)
                relationships[table]["primary_key"] = meta["pk"]

                fk = meta.get("fk")
                if fk and fk in pk_index:
                    relationships[table]["links"].append({
                        "fk": fk,
                        "target_table": pk_index[fk],
                        "relation_type": "fk"
                    })

            # 2. Lineage-based relationships (supporting signal)
            for row in lineage:
                src = row["source_table_name"]
                tgt = row["target_table_name"]

                if src in tables and tgt in tables:
                    relationships[tgt]["derived_from"].append({
                        "source_table": src,
                        "relation_type": "lineage"
                    })

            return dict(relationships)

        for schema in ctx.schemas:
            print(f"Processing schema: {schema}")
            relationships = build_relationships_with_lineage_for_schema(
                    schema=schema,
                    metadata=metadata,
                    lineage=lineage,
                    entity_map=self.entity_keyword_map
                )
            
            # Save relationships per schema
            filename = f"{ctx.output_path}/gd_relationships_{schema}.json"
            self.utils.dump_json_to_file(
                    relationships, 
                    filename
                )
            
            df = pd.read_json(filename)
            df.to_csv(filename.replace(".json", ".csv"), index=False)

    def generate_document_stats_sql(
            self,
            anchor_tables: List[dict],
            years: list[int],
            cte_name: str 
        ) -> tuple[str, str]:
            
            def build_alias(table_name: str) -> str:
                remove_terms = {"citation"}

                parts = table_name.split("_")

                # Case 1: starts with "d_"
                if table_name.startswith("d_"):
                    # remove "d_"
                    parts = parts[1:]

                    normalized = []
                    for p in parts:
                        if p in remove_terms:
                            continue
                        if p == "count":
                            normalized.append("cite")
                        else:
                            normalized.append(p)

                    if not normalized:
                        raise ValueError(f"No valid terms left for alias: {table_name}")

                    return f"{normalized[0]}_ct"

                # Case 2: default
                return parts[0]

            # Anchor table (first one)
            anchor = anchor_tables[0]

            alias_suffix = anchor.get("alias_suffix", "")
            
            anchor_table = f"""capped_{anchor["table"]}{alias_suffix}"""
            anchor_pk = anchor["pk"]

            uid_col = anchor_pk[0]
            year_col = anchor_pk[1]

            # schema = anchor.get("schema", "schema")

            select_cols = [
                f"pub.{uid_col}",
                f"pub.{year_col}"
            ]

            joins = []
            count_exprs = []
            aliases = []

            for t in anchor_tables[1:]:
                table = t["table"]
                pk = t["pk"]
                is_select = t.get("select_count", False)
                alias_suffix = t.get("alias_suffix", "")

                fk = pk[0]          # uid
                count_col = pk[1]   # second pk

                # alias = table.split("_")[0]
                alias = build_alias(table) + alias_suffix
                aliases.append(f"{alias}_cnt")

                joins.append(
                    f"LEFT JOIN capped_{table}{alias_suffix} {alias} ON pub.{uid_col} = {alias}.{fk}"
                )

                if is_select:
                    select_cols.append(
                        f"MAX({alias}.{count_col}) AS {alias}_cnt"
                    )
                else:  
                    count_exprs.append(
                        f"COUNT(DISTINCT {alias}.{count_col}) AS {alias}_cnt"
                    )

            year_filter = ", ".join(map(str, years))
            separator = ",\n\t\t"
            separator_2= "\n\t"
            sql = dedent(f"""
{cte_name} AS (
SELECT
\t\t{separator.join(select_cols)},
\t\t{separator.join(count_exprs)}
FROM {anchor_table} pub
\t{separator_2.join(joins)}
WHERE pub.{year_col} IN ({year_filter})
GROUP BY pub.{uid_col}, pub.{year_col}
LIMIT 100
),
""").strip()
            order_by = " + ".join(aliases)
            return sql, order_by

    def generate_anchor_ctes(
            self,
            anchor_tables: List[dict],
            years: list[int]
        ) -> str:

        ctes = []
        year_filter = ", ".join(map(str, years)) 

        for cfg in anchor_tables:
            table = cfg["table"]
            pk = cfg["pk"]
            start, end = cfg["cnt_range"]
            schema = cfg.get("schema", "schema")
            alias_suffix = cfg.get("alias_suffix", "")

            partition_col = pk[0]
            order_col = pk[1]

            cte_name = f"capped_{table}{alias_suffix}"

            if table == "f_publication":
                filter =  f" {pk[1]} IN ({year_filter})"
            else:
                filter = f" rn >= {start} AND rn <= {end}"
               

            cte_sql = dedent(f"""
                 {cte_name} AS (
                    SELECT {", ".join(pk)}
                    FROM (
                        SELECT
                            {", ".join(pk)},
                            ROW_NUMBER() OVER (
                                PARTITION BY {partition_col}
                                ORDER BY {order_col}
                            ) AS rn
                        FROM  {{{schema}}}.{table}
                    )
                    WHERE{filter}  
                )
            """).strip()
            # rn >= {start} AND rn <= {end} 
            ctes.append(f" {cte_sql}")

        return ",\n\n".join(ctes)

    def generate_anchor_ranked(
            self,
            order_by: str,
        ) -> str:

  
        return dedent(f"""
ranked_articles AS (
    SELECT
        *,
        ({order_by}) AS total_score,
        ROW_NUMBER() OVER (
            PARTITION BY pub_year
            ORDER BY ({order_by}) DESC
        ) AS rn
    FROM article_stats
)

SELECT *
FROM ranked_articles
WHERE rn <= 10
ORDER BY pub_year, total_score DESC;
        """).strip()


    def generate_publication_uid_cte(
        self,
        anchor_tables: List[dict]
    ):
        def normalize(col_name: str) -> str:
            name = col_name.removeprefix("d_")
            parts = name.split("_")
            return f"{parts[0]}_{''.join(p[0] for p in parts[1:] if p)}"

        pub_year_list = ", ".join(map(str,  anchor_tables[0]["year_range"]))

        pub_uids_cte = dedent(f"""
            WITH
            pub_uids AS (
                SELECT DISTINCT uid
                FROM {{schema}}.f_publication
                WHERE pub_year IN ({pub_year_list})
            )
        """).strip()

        union_blocks = []

        for et in anchor_tables[1:]:
            table = et["table"]
            uid_col = et["pk"][0]
            cnt_col = et["pk"][1]
            min_cnt, max_cnt = et["cnt_range"]
            select_count = et.get("select_count", False)

            schema = et.get("schema", "schema")
            alias_suffix = et.get("alias_suffix", "")

            src = f"{table}{alias_suffix}"
            alias = normalize(table) + alias_suffix
            # Type A: pre-aggregated count table
            if select_count:
                block = dedent(f"""
                    SELECT '{src}' AS src, l.{uid_col} AS uid
                    FROM {{{schema}}}.{table} l
                    JOIN pub_uids p
                        ON l.{uid_col} = p.uid
                    WHERE l.{cnt_col} BETWEEN {min_cnt} AND {max_cnt}
                """).strip()

            # Type B: link / fact table
            else:
                block = dedent(f"""
                    SELECT '{src}' AS src, l.{uid_col} AS uid
                    FROM {{{schema}}}.{table} l
                    JOIN pub_uids p
                        ON l.{uid_col} = p.uid
                    GROUP BY l.{uid_col}
                    HAVING COUNT(l.{cnt_col}) BETWEEN {min_cnt} AND {max_cnt}
                """).strip()

            union_blocks.append(block)
        
        union_sql = "\n\nUNION ALL\n\n".join(union_blocks)
        qualified_uids_cte = dedent(f"""
            qualified_uids AS (
                {union_sql}
            )
        """).strip()

        final_select = dedent(f"""
            SELECT uid
            FROM qualified_uids
            GROUP BY uid
            HAVING COUNT(DISTINCT src) = {len(anchor_tables)-1}
        """).strip()

        return  [",\n\n".join([pub_uids_cte, qualified_uids_cte]), final_select]

    def create_anchor_table_sql(
            self,
            ctx: FeatureContext
        ):
        print(
                f"create_anchor_table_sql: "
            )
        
        conf_file = f"{ctx.output_path}/{ctx.anchor_config_file}"

        with open(conf_file, "r") as f:
             config = yaml.safe_load(f)

        anchor_tables = config["anchor_tables"]

        capped_ctes = self.generate_publication_uid_cte( anchor_tables=anchor_tables)

        """ 
        capped_ctes = self.generate_anchor_ctes(
                anchor_tables=anchor_tables, 
                years=ctx.years
            )
    
        stmt, orderby = self.generate_document_stats_sql(
                anchor_tables= anchor_tables,
                years= ctx.years,
                cte_name= ctx.cte_name
            )
        
        ranked_stmt = self.generate_anchor_ranked(order_by=orderby)
        """

        sql_filename = f"{ctx.output_path}/{ctx.anchor_sql_file}"
        #self.save_to_file([f"WITH {capped_ctes},", stmt, ranked_stmt], sql_filename)
        self.save_to_file(capped_ctes, sql_filename)
        print(f"Saved CREATE TABLE statements to {sql_filename}")

    # run feature based on feature name with  context handling
    def run_feature(
            self,
            feature: str, **kwargs):
        try:
            ctx = self.CONTEXT_FACTORIES[feature](kwargs)
            self.FEATURE_HANDLERS[feature](ctx)
        except KeyError:
            raise ValueError(f"Unsupported feature: {feature}")


    def ensure_path_exists(
            self,
            **kwargs
        ):
        
        version = kwargs.get("version", self.src_schema_version)
        output_path = kwargs.get("output_path", version)

        self.utils.ensure_path_exists(output_path)

if __name__ == "__main__":

    """
    Usage:  python dap-utils.py <feature_name> [param=value ...]

    FEAUETURES TO RUN: 
       acs_trait - generate ACS trait scala file
       udm_trait - generate UDM trait scala file
       dap_trait - generate DAP trait scala file
       pipeline_metadata - generate pipeline_metadata.csv file
       dap_lineage - generate dap_lineage.csv file 
       diff_schema - compare table schemas between two versions and export the diff report to json and csv
    
    Example:
        python dap-utils.py acs_trait catalog_name=my_catalog   version=v2_0
        python dap-utils.py dap_lineage version=v_1_0_1 
    """

    # example_usage()

    if len(sys.argv) < 2:
        print("Please provide a feature name as the first argument ...\n\n")
        print("Usage:  python golden-data-maint.py <feature_name> [param=value ...]\n")
        print(
            f"Feature: list_jobs | acs_trait | udm_trait | dap_trait | dap_lineage | acs_relations |\n"
            f"         pipeline_metadata | acs_schema | dap_schema |diff_schema | all\n"
        )

        sys.exit(1)

    feature_name = sys.argv[1]

    feature_list = (
            [ "list_jobs", "acs_trait", "udm_trait", "dap_trait", "dap_lineage", "acs_schema", "acs_relations", "diff_schema",  "pipeline_metadata" ]
            if feature_name == "all"
            else [feature_name]
        )
     #
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

    # Run only the requested feature once
    # Set up connection and API info for PROD environment

    gd_manager = DapGoldenDatasetManager()
    gd_manager.ensure_path_exists(**kwargs)

    for feature in feature_list:
        print(f"Executing feature {feature} with parameters: {kwargs}")
        gd_manager.run_feature(feature, **kwargs)
