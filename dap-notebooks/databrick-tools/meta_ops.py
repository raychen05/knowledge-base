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
from dataclasses import dataclass


# -------------------------------------------------------------------
# General Config and Feature class
# -------------------------------------------------------------------
@dataclass
class FeatureContext:
    catalog_name: Optional[str] = None 
    schemas: Optional[list] = None 
    version: Optional[str] = None  
    environment: Optional[str] = None  
    filename: Optional[str] = None 
    output_path: Optional[str] = None
    trait_name: Optional[str] = None                 # trait name - ACS, DAP, UDM.           -- acs_trait
    ops_table_name: Optional[str] = None             # table - watermark, registry or task   -- pipeline_metadata, insert_watermark
    left_schema: Optional[dict] = None               # left schema info for diff             -- diff_acs_schema
    right_schema: Optional[dict] = None              # right schema info for diff            -- diff_acs_schema
    source_version: Optional[str] = None             # source version for clone schema.      -- clone_dap_schemas
    target_version: Optional[str] = None             # target version for clone schema.      -- clone_dap_schemas
    src_environment: Optional[str] = None         # source environment for lineage        -- generate_pipeline_lineages

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
            "dap_work"]
            )

# -------------------------------------------------------------------
# General Helper Function
# -------------------------------------------------------------------
class Utils:

    # extract  job meta data from job settings tags
    def parse_tags(
            self,
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

    # get first macthed ID from two lists
    def first_matched_id(
            self, a, b):
        """
        Return the first ID from list `a` that is also in list `b`.
        Returns None if no match is found.
        """
        b_set = set(b)  # fast lookups
        for x in a:
            if x in b_set:
                return x
        return None

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

    # sort tables and columns
    def sort_tables_and_columns(
            self,
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

    # filter table fields based on specified columns
    def filter_table_fields(
            self,
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

        job_list = []
        next_page_token = None

        while True:
            params = {"page_token": next_page_token} if next_page_token else {}
            data = self.call_api( 
                    url = "/api/2.1/jobs/list", 
                    params = params,
                    environment= environment
                )
            jobs = self.utils.parse_tags(data, release_version)
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
                self.utils.filter_table_fields(table_dict, filter_columns)
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
        
        all_tables = self.utils.sort_tables_and_columns(all_tables)

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

    # get table lineage info (upstream )for specified table and write to csv
    def fetch_table_upstream_lineage_csv(
            self,
            schema: str, 
            table_name: str, 
            environment: str,
            filename: str 
        ) -> None:
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
        def extract_tables(schema: str, tables_list, filename: str ):

            for t in tables_list:
                # Extract job_id correctly
                catalog_name = t.get("catalog_name")
                schema_name = t.get("schema_name")
                name = t.get("name")
                full_table_name = f"{catalog_name}.{schema_name}.{name}"
                csv_line = f"{schema},{table_name},{full_table_name}"

                self.utils.append_csv_line(csv_line, filename )

        extract_tables(schema, upstreams, filename=filename)

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

    # generate table lineage info (upstream )for specified downstream table and pipeline
    def fetch_pipeline_lineages(
            self,
            table_name: str, 
            environment: str,
            job_list: list = None
        ) -> list:

        print(
                f"generatePipelineLineages: table_name={table_name}"
            )
        
        upstreams, downstreams = self.fetch_table_lineage(
                    table_name=table_name,
                    environment=environment
                )

        task_list = []

        job_ids = [job["job_id"] for job in job_list]

        for t in upstreams:
            print(f"Processing upstream table: {t}")

            job_id = self.utils.first_matched_id( t['job_ids'], job_ids ) if job_ids else True
            if job_id:

                tasks = self.fetch_tasks(
                            job_id=job_id, 
                            environment=environment
                        )
                # print(f"  Found matching job_id: {job_id} with tasks: {tasks}")

                job_info = next((j for j in job_list if j["job_id"] == job_id), None)

                emails = job_info.get("email_on_failure") or []
                emails = emails if isinstance(emails, list) else [emails]

                owner = self.utils.name_from_email(emails[0]) if emails else ""
                email = ",".join(emails)

                # print(f"  Job info: {job_info}")
                if job_info:
                    task_list.append({
                        "pipeline": job_info['name'], #job_info['tag_Component'],
                        "owner": owner, # job_info['tag_Owner'],
                        "product": job_info['tag_Product'],
                        "email": email, # job_info['email_on_failure'],
                        # "job_id": str(job_info['job_id']),
                        "tasks": tasks,
                        # "name": t['name'],
                        "downstream_table": table_name,
                        "upstream_table": t['name'],
                        "upstream_catalog_name": t['catalog_name'],
                        "upstream_schema_name": t['schema_name'],
                        "upstream_table_type": t['table_type'],
                    })

        task_list.sort(key=lambda x: (x['pipeline'], x['downstream_table']))
        return task_list


# -------------------------------------------------------------------
# Feature Function 
# -------------------------------------------------------------------

class DapFeatures:

    def __init__(self):

        self.cfg = ConfigInfo()
        self.api = DatabricksAPIClient(self)
        self.utils = Utils()

        self.CONTEXT_FACTORIES = {
            "acs_trait": lambda kwargs:FeatureContext(
                            catalog_name=self.src_catalog_name,
                            schemas=self.acs_schemas,
                            trait_name="ACS",
                            version=kwargs.get("version", self.src_schema_version),
                            environment=kwargs.get("environment", self.src_environment),
                            output_path=kwargs.get("output_path", self.output_path)
                        ),
            "dap_trait": lambda kwargs:FeatureContext(
                            catalog_name= self.tgt_catalog_name,
                            schemas=self.dap_schemas,
                            trait_name="DAP",
                            version=kwargs.get("version", self.tgt_schema_version),
                            environment=kwargs.get("environment", self.tgt_environment),
                            output_path=kwargs.get("output_path", self.output_path) 
                        ), 
            "udm_trait": lambda kwargs:FeatureContext(
                            catalog_name= self.src_udm_catalog,
                            schemas=self.udm_schemas,
                            trait_name="UDM",
                            version=kwargs.get("version", ""),
                            environment=kwargs.get("environment", self.src_environment),
                            output_path=kwargs.get("output_path", self.output_path) 
                        ),
            "dap_lineage": lambda kwargs:FeatureContext(
                    catalog_name=   self.tgt_catalog_name,
                    schemas=self.dap_schemas,
                    version=kwargs.get("version", self.tgt_schema_version),
                    environment=kwargs.get("environment", self.tgt_environment),
                    filename = kwargs.get("filename", self.dap_lineage_file), 
                    output_path=kwargs.get("output_path", self.output_path)  
                ),
            "pipeline_metadata": lambda kwargs:FeatureContext(
                    catalog_name=self.tgt_catalog_name,
                    schemas=self.dap_schemas,
                    environment=kwargs.get("environment", self.tgt_environment),
                    version=kwargs.get("version", self.tgt_schema_version),
                    filename=kwargs.get("filename", self.pipeline_metadata_file),
                    output_path=kwargs.get("output_path", self.output_path) 
                ),
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
            "diff_schema": lambda kwargs:FeatureContext(
                    left_schema ={
                        "catalog_name": self.src_catalog_name,
                        "schemas": self.acs_schemas,
                        "environment": kwargs.get("environment", self.src_environment),
                        "version": kwargs.get("left_version", self.left_schema_version),
                        "filename":   f"acs_schema_{kwargs.get('left_version', self.left_schema_version)}.json",
                        "output_path": kwargs.get("output_path", self.output_path) 
                    },
                    right_schema = {
                        "catalog_name": self.src_catalog_name,
                        "schemas": self.acs_schemas,
                        "environment": kwargs.get("environment", self.src_environment),
                        "version": kwargs.get("right_version", self.right_schema_version),
                        "filename": f"acs_schema_{kwargs.get('right_version', self.right_schema_version)}.json",
                        "output_path": kwargs.get("output_path",self.output_path) 
                    },
                    filename = self.acs_schema_info_file,
                    output_path=kwargs.get("output_path", self.output_path) 
                ),
            "list_jobs": lambda kwargs:FeatureContext(
                    environment=kwargs.get("environment", self.tgt_environment),
                    output_path=kwargs.get("output_path", self.output_path) 
                )
        }

        self.FEATURE_HANDLERS = {
            # schema trait generation features
            "acs_trait": self.generate_schema_trait,
            "dap_trait": self.generate_schema_trait,
            "udm_trait": self.generate_schema_trait,
            # lineage and pipeline metadata features
            "dap_lineage": self.generate_lineages,
            "pipeline_metadata": self.generate_pipeline_metadata,
            # schema management features
            "acs_schema": self.fetch_table_schema_info,
            "dap_schema": self.fetch_table_schema_info,
            "diff_schema": self.diff_tables_schema,
            "list_jobs": self.fetch_dap_jobs_list
        }

    def __getattr__(self, name):
            return getattr(self.cfg, name)
        
    # -------------------------------------------------------------------
    # Feature Helper Function 
    # -------------------------------------------------------------------
    
    def fetch_dap_jobs_list(self, ctx: FeatureContext):
        """
        Fetch and return the list of DAP-related jobs in the specified environment.
        """
        job_list = self.api.fetch_jobs_list(
                release_version= self.release_version, 
                environment=ctx.environment
            )

        for row in job_list:
            d = json.dumps(row)
            self.utils.append_csv_line(d,  f"{ctx.output_path}/dap_job_list.csv")

        return job_list
    
    # compare table schema between two versions
    def compare_table_schemas(
        self,
        left_tables: List[Dict],
        right_tables: List[Dict]
    ) -> List[Dict]:
        """
        Compare two lists of table schemas and return discrepancies at table & column level.
        """

        def table_key(t):
            return (self.utils.drop_schema_version(t["schema_name"]), self.utils.drop_schema_version(t["table_name"]))

        
        # Index tables by (schema_name, table_name)
        left_index = {table_key(t): t for t in left_tables}
        right_index = {table_key(t): t for t in right_tables}

        all_tables = set(left_index.keys()) | set(right_index.keys())
        report = []

        for key in sorted(all_tables):
            schema_name, table_name = key
            left_table = left_index.get(key)
            right_table = right_index.get(key)

            table_diff = {
                "schema_name": schema_name,
                "table_name": table_name,
                "table_status": None,
                "column_differences": []
            }

            # Table missing cases
            if not left_table:
                table_diff["table_status"] = "missing_in_left"
                report.append(table_diff)
                continue

            if not right_table:
                table_diff["table_status"] = "missing_in_right"
                report.append(table_diff)
                continue

            table_diff["table_status"] = "present_in_both"

            # Index columns by name
            left_cols = {c["name"]: c for c in left_table.get("columns", [])}
            right_cols = {c["name"]: c for c in right_table.get("columns", [])}

            all_columns = set(left_cols.keys()) | set(right_cols.keys())

            for col_name in sorted(all_columns):
                left_col = left_cols.get(col_name)
                right_col = right_cols.get(col_name)

                # Column missing cases
                if not left_col:
                    table_diff["column_differences"].append({
                        "column_name": col_name,
                        "status": "missing_in_left",
                        "left": None,
                        "right": right_col
                    })
                    continue

                if not right_col:
                    table_diff["column_differences"].append({
                        "column_name": col_name,
                        "status": "missing_in_right",
                        "left": left_col,
                        "right": None
                    })
                    continue

                # Compare column attributes
                diffs = {}
                for attr in ["type_name", "type_text", "nullable"]:
                    if left_col.get(attr) != right_col.get(attr):
                        diffs[attr] = {
                            "left": left_col.get(attr),
                            "right": right_col.get(attr)
                        }

                if diffs:
                    table_diff["column_differences"].append({
                        "column_name": col_name,
                        "status": "attribute_mismatch",
                        "differences": diffs
                    })

            # Only include table if differences exist
            if table_diff["column_differences"]:
                report.append(table_diff)

        return report

    # export schema comparison discrepancies to CSV
    def export_schema_diff_to_csv(
        self,
        diff_report: list,
        output_file: str
    ) -> None:
        """
        Export schema comparison discrepancies to a CSV file.
        """
        headers = [
            "schema_name",
            "table_name",
            "table_status",
            "column_name",
            "issue_type",
            "attribute",
            "left_value",
            "right_value"
        ]

        with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()

            for table in diff_report:
                schema_name = table["schema_name"]
                table_name = table["table_name"]
                table_status = table["table_status"]

                # Table-level missing
                if table_status in ("missing_in_left", "missing_in_right"):
                    writer.writerow({
                        "schema_name": schema_name,
                        "table_name": table_name,
                        "table_status": table_status,
                        "column_name": None,
                        "issue_type": "table_missing",
                        "attribute": None,
                        "left_value": None,
                        "right_value": None
                    })
                    continue

                # Column-level differences
                for col_diff in table.get("column_differences", []):
                    column_name = col_diff["column_name"]
                    status = col_diff["status"]

                    # Column missing
                    if status in ("missing_in_left", "missing_in_right"):
                        writer.writerow({
                            "schema_name": schema_name,
                            "table_name": table_name,
                            "table_status": table_status,
                            "column_name": column_name,
                            "issue_type": status,
                            "attribute": None,
                            "left_value": col_diff.get("left"),
                            "right_value": col_diff.get("right")
                        })

                    # Attribute mismatch
                    elif status == "attribute_mismatch":
                        for attr, values in col_diff["differences"].items():
                            writer.writerow({
                                "schema_name": schema_name,
                                "table_name": table_name,
                                "table_status": table_status,
                                "column_name": column_name,
                                "issue_type": "attribute_mismatch",
                                "attribute": attr,
                                "left_value": values["left"],
                                "right_value": values["right"]
                            })

        #Convert list of dicts to DataFrame
       # df = pd.DataFrame(rows)

        # Write to Excel
       # df.to_excel(output_file, index=False)

    # build  structured data for pipelines from flat rows (pipeline meta, downstream_table, upstream_table)
    def build_pipeline_structured_data(
            self,
            rows: List[Dict[str, Any]]
        ) -> Dict[str, Dict[str, Any]]:

        pipelines: Dict[str, Dict[str, Any]] = {}

        for row in rows:
            print(f"Processing row: {row}")
            pipeline_name = row.get("pipeline", "")

            # Initialize pipeline entry once
            if pipeline_name not in pipelines:
                pipelines[pipeline_name] = {
                    "pipeline": pipeline_name,
                    "owner":  row.get("owner", ""),
                    "product": row.get("product", ""),
                    "email": row.get("email", ""),
                    "tasks": row.get("tasks", []),
                    "upstreams_tables": set(),       # temp set for dedupe
                    "downstream_tables": defaultdict(list)
                }

            u_table_name = f"{row['upstream_catalog_name']}.{row['upstream_schema_name']}.{row['upstream_table']}"
            # Track upstream tables
            pipelines[pipeline_name]["upstreams_tables"].add(u_table_name)

            # Track downstream → upstream mapping
            d_table_name = row["downstream_table"].split('.')[-1]
            pipelines[pipeline_name]["downstream_tables"][d_table_name].append(u_table_name )

        # Finalize structure (convert sets/defaultdicts to lists)
        for pipeline_data in pipelines.values():
            pipeline_data["upstreams_tables"] = sorted(pipeline_data["upstreams_tables"])

            pipeline_data["downstream_tables"] = [
                {
                    "downstream_table": dt,
                    "upstream_tables": uts
                }
                for dt, uts in pipeline_data["downstream_tables"].items()
            ]

        return pipelines

    # build SQL INSERT statements for pipeline metadata 
    def build_pipelines_insert_sql(
        self,
        rows: List[Dict[str, Any]],
        table_name: str
    ) -> List[str]:
        pipelines: Dict[str, Dict[str, Any]] = {}

        # Aggregate by pipeline
        for row in rows:
            pipeline = row.get("pipeline", "")

            if pipeline not in pipelines:
                pipelines[pipeline] = {
                    "pipeline_name": pipeline,
                    "owner": self.utils.name_from_email(row.get("email", "")[0]) if row.get("email") else "",
                    "email": ",".join(row.get("email", [])) if isinstance(row.get("email"), list) else row.get("email", ""),
                    "upstream_tables": set(),
                }

            if row.get("upstream_table"):
                if row["upstream_table"] == "<JOB_ONLY_UPSTREAM>": continue
                tableFullName = f"{row['upstream_catalog_name']}.{row['upstream_schema_name']}.{row['upstream_table']}"
                pipelines[pipeline]["upstream_tables"].add(tableFullName) 

        # Generate SQL per pipeline
        sql_statements = []
        for p in pipelines.values():
            upstream_array = ", ".join(f"'{t}'" for t in sorted(p["upstream_tables"]))

            sql = f"""
    INSERT INTO {table_name} (
    pipeline_name,
    type,
    owner,
    prodcut,
    email,
    description,
    upstream_tables,
    update_ts,
    updated_by
    )
    VALUES (
    '{p["pipeline_name"]}',
    'Data',
    '{p["owner"]}',
    'WOSRI',
    '{p["email"]}',
    '',
    array({upstream_array}),
    current_timestamp(),
    'system'
    );
    """.strip()

            sql_statements.append(sql)

        return sql_statements


    # build structured data for pipeline tasks (task - upstreams) from flat rows (pipeline, task, upstream_table)
    def build_pipeline_task_rows(
            self,
            rows: List[Dict[str, Any]]
        ) -> List[Dict[str, Any]]:

        tasks: Dict[tuple, Dict[str, Any]] = {}

        for row in rows:
            pipeline = row.get("pipeline", "")
            task_name = row.get("downstream_table", "").split(".")[-1]

            key = (pipeline, task_name)

            if key not in tasks:
                tasks[key] = {
                    "pipeline_name": pipeline,
                    "task_name": task_name,
                    "upstream_tables": set(),
                }

            upstream = row.get("upstream_table")
        # if upstream and upstream != "<JOB_ONLY_UPSTREAM>":
        #     tasks[key]["upstream_tables"].add(upstream)

            if upstream:
                if upstream == "<JOB_ONLY_UPSTREAM>": continue
                tableFullName = f"{row['upstream_catalog_name']}.{row['upstream_schema_name']}.{row['upstream_table']}"
                tasks[key]["upstream_tables"].add(tableFullName) 

        # Convert sets to lists for export
        result = []
        for task in tasks.values():
            result.append({
                "pipeline_name": task["pipeline_name"],
                "task_name": task["task_name"],
                "upstream_tables": sorted(task["upstream_tables"]),
            })

        return result


    # build SQL INSERT statements for pipeline task metadata 
    def build_pipelines_task_insert_sql(
        self,
        rows: List[Dict[str, Any]],
        table_name: str
    ) -> List[str]:
        tasks: Dict[str, Dict[str, Any]] = {}

        # Aggregate by pipeline
        tasks = self.build_pipeline_task_rows(rows)
        # Generate SQL per pipeline
        sql_statements = []
        for p in tasks:
            upstream_array = ", ".join(f"'{t}'" for t in sorted(p["upstream_tables"]))

            sql = f"""
    INSERT INTO {table_name} (
    pipeline_name,
    task_name,
    upstream_tables,
    updated_by,
    updated_at
    )
    VALUES (
    '{p["pipeline_name"]}',
    '{p["task_name"]}',
    array({upstream_array}),
    'system',
    current_timestamp()
    );
    """.strip()

            sql_statements.append(sql)

        return sql_statements


    # generate scala case objects (scala file) from table schema (Active version)
    def generate_case_objects(
        self,
        catalog_name: str,
        table_schema: list,
        output_path: str,
        trait_name: str
    ) -> None:
        """
        Generate Scala sealed trait and case objects from Unity Catalog table metadata.

        Features:
        - Alphabetical sorting
        - Sealed trait generation
        - Duplicate validation
        - Writes output to .scala file
        """

        # ---------- Helpers ----------

        def to_camel_case(s: str) -> str:
            return "".join(word.capitalize() for word in s.split("_"))

        def normalize_table_name(name: str) -> str:
            return name.removesuffix("_woscore")

        def normalize_schema(schema: str) -> str:
            schema = self.utils.drop_schema_version(schema)
            return "" if schema in ("gold_wos", "gold_pprn") else schema

        # ---------- Extract rows ----------

        rows = []
        for t in table_schema:
            rows.append((
                normalize_schema(t["schema_name"]),
                t["table_name"]
            ))

        # ---------- Group by normalized table ----------

        grouped = defaultdict(list)
        for schema, table in rows:
            grouped[normalize_table_name(table)].append((schema, table))

        # ---------- Duplicate validation ----------

        object_names = {}
        for table_name in grouped:
            obj_name = to_camel_case(table_name)
            if obj_name in object_names:
                raise ValueError(
                    f"Duplicate case object name detected: '{obj_name}' "
                    f"for tables '{table_name}' and '{object_names[obj_name]}'"
                )
            object_names[obj_name] = table_name

        # ---------- Generate case objects ----------

        case_objects = []

        for table_name, entries in grouped.items():
            has_woscore = any(t.endswith("_woscore") for _, t in entries)
            # final_schema = "dataset" if has_woscore else entries[0][0]
            final_schema = entries[0][0]
            obj_name = to_camel_case(table_name)

            #needsSuffix = "override val needsSuffix = true" if has_woscore else ""
            #final_schema = "override val schema = \"" + drop_schema_version( entries[0][0]) + "\"" if  entries[0][0] else ""
            
            if "incremental" in table_name or any(ch.isdigit() for ch in table_name): continue

            case_objects.append((
                obj_name,
                "\tcase object " + obj_name + " extends " + trait_name + " {\n" +
                "\t\tval tableName = \"" + table_name + "\"\n" +
                (f"\t\toverride val schema = \"{self.utils.drop_schema_version(final_schema)}\"\n" if final_schema else "") +
                (f"\t\toverride val needsSuffix = true\n" if has_woscore else "") +
                "\t}"
            ))

    # \t\tdef schema: String = "{drop_schema_version(final_schema)}"
    # \t\tval catalog = "{catalog_name}"

        # ---------- Sort alphabetically ----------

        case_objects.sort(key=lambda x: x[0])

        # ---------- Generate sealed trait ----------


        objects_def = "\n\n".join(obj for _, obj in case_objects)

        scala_code = f"""// AUTO-GENERATED FILE — DO NOT EDIT
    // Generated by Python

    object {trait_name} {{

    {objects_def}

    }}
    """

        # ---------- Write to file ----------

        output_file = Path(output_path)

        output_file.write_text(scala_code, encoding="utf-8")

        print(f"Scala file generated: {output_file.resolve()}")


    # -------------------------------------------------------------------
    # Feature Function 
    # -------------------------------------------------------------------
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
    
        self.utils.dump_json_to_file(all_tables, f"{ctx.output_path}/{ctx.filename}")

        return all_tables

    # generate scala trait and case object from unity catalog schemas
    def generate_schema_trait(
        self,
        ctx: FeatureContext
    ) -> None:
        
        print(
                f"generateSchemaTrait: catalog={ctx.catalog_name}, "
                f"schemas={ctx.schemas}, trait={ctx.trait_name}, "
                f"version={ctx.version}, output={ctx.output_path}, environment={ctx.environment}"
            )
        
        all_tables = []

        catalog = f"{ctx.catalog_name}_{ctx.environment}" if ctx.environment else ctx.catalog_name
        for schema_name in ctx.schemas:
            tables = self.api.fetch_tables_info(
                    catalog_name=catalog, 
                    schema_name=f"{schema_name}_{ctx.version}".removesuffix("_"),
                    environment=ctx.environment
                )

            if not tables:
                print(f"No tables found for schema: {schema_name}")
                continue

            all_tables.extend(tables)

        # One object, deduped across schemas
        self.generate_case_objects(
            catalog_name=ctx.catalog_name,
            table_schema=all_tables,
            output_path=f"{ctx.output_path}/{ctx.trait_name}.scala",
            trait_name=ctx.trait_name
        )

    # generate table lineage info (upstream )for specified schemas and write to csv
    def generate_lineages(
            self,
            ctx: FeatureContext
        ):  

        print(
                f"generateDapLineageCsv: catalog={ctx.catalog_name}, "
                f"version={ctx.version}, output={ctx.filename}"
            )
        
        catalog = f"{ctx.catalog_name}_{ctx.environment}" if ctx.environment else ctx.catalog_name
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
                self.api.fetch_table_upstream_lineage_csv(
                        schema=schemaName, 
                        table_name=tableName,
                        environment=ctx.environment,
                        filename=f"{ctx.output_path}/{ctx.filename}"
                    )

  # compare table schemas between two versions and export the diff report to json and csv
    def diff_tables_schema(
            self,
            ctx: FeatureContext
        ):

        left_infos = self.fetch_table_schema_info(
                FeatureContext(
                    catalog_name=ctx.left_schema["catalog_name"],
                    schemas=ctx.left_schema["schemas"],
                    environment=ctx.left_schema["environment"],
                    version=ctx.left_schema["version"],
                    filename=ctx.left_schema["filename"],
                    output_path=ctx.left_schema["output_path"]
                )
            )
        
        right_infos = self.fetch_table_schema_info(
                FeatureContext(
                    catalog_name=ctx.right_schema["catalog_name"],
                    schemas=ctx.right_schema["schemas"],
                    environment=ctx.right_schema["environment"],
                    version=ctx.right_schema["version"],
                    filename=ctx.right_schema["filename"],
                    output_path=ctx.right_schema["output_path"]
                )
            )

        report = self.compare_table_schemas(
                left_tables = left_infos,
                right_tables = right_infos
            ) 

        self.utils.dump_json_to_file(report, f"{ctx.output_path}/{ctx.filename}.json")
        self.export_schema_diff_to_csv(report, f"{ctx.output_path}/{ctx.filename}.csv")

        return report

    # generate pipeline metadata (upstream , downstream, pipeline, task) for specified schemas and write to csv
    def generate_pipeline_metadata(
            self,
            ctx: FeatureContext
        ):

        print(
            f"generatePipelineMetadata: catalog={ctx.catalog_name}, "
            f"schemas={ctx.schemas}, version={ctx.version}, "
            f" output={ctx.output_path}, environment={ctx.environment}, src_environment={ctx.src_environment}"
        )

        all_tables = []

        jobList = self.api.fetch_jobs_list(
                    release_version= self.release_version, 
                    environment=ctx.environment
                )
            
        catalog = f"{ctx.catalog_name}_{ctx.environment}" if ctx.environment else ctx.catalog_name
        for schema_name in ctx.schemas:
            tables = self.api.fetch_tables_info(
                        catalog_name=catalog, 
                        schema_name=f"{schema_name}_{ctx.version}".removesuffix("_"),
                        environment=ctx.environment
                    )
            if not tables:
                print(f"No tables found for schema: {schema_name}")
                continue

            for table in tables:
                task_list = self.api.fetch_pipeline_lineages(
                                table_name=table["full_name"], 
                                environment=ctx.environment,
                                job_list=jobList
                            )
                for row in task_list:
                    d = json.dumps(row)
                    all_tables.append(row)
                    self.utils.append_csv_line(d, f"{ctx.output_path}/{self.self.acs_schema_info_file}.csv")
    
        # build structured data for pipelines
        data = self.build_pipeline_structured_data(all_tables)
        self.utils.dump_json_to_file(data, f"{ctx.output_path}/{self.self.acs_schema_info_file}.json")   
        # read flat rows from csv
        metadata = self.utils.read_json_lines(f"{ctx.output_path}/{self.self.acs_schema_info_file}.csv") 
        # generate sql insert statements for pipeline registry and task upstream tables
        stmt = self.build_pipelines_insert_sql(metadata, f"{ctx.schema}.{self.reistry_table_name}")
        self.utils.save_to_file(stmt, f"{ctx.output_path}/{self.insert_registry_sql_file}")
        # generate sql insert statements for pipeline task upstream tables
        stmt = self.build_pipelines_task_insert_sql(metadata, f"{ctx.schema}.{self.upstream_table_name}") 
        self.utils.save_to_file(stmt, f"{ctx.output_path}/{self.insert_task_sql_file}")

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
        print("Usage:  python meta_ops.py <feature_name> [param=value ...]\n")
        print(
            f"Feature: list_jobs | acs_trait | udm_trait | dap_trait | dap_lineage |\n"
            f"         pipeline_metadata | acs_schema | dap_schema |diff_schema | all\n"
        )

        sys.exit(1)

    feature_name = sys.argv[1]

    feature_list = (
            [ "list_jobs", "acs_trait", "udm_trait", "dap_trait", "dap_lineage", "acs_schema", "diff_schema",  "pipeline_metadata" ]
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

    ft = DapFeatures()
    ft.ensure_path_exists(**kwargs)

    for feature in feature_list:
        print(f"Executing feature {feature} with parameters: {kwargs}")
        ft.run_feature(feature, **kwargs)
