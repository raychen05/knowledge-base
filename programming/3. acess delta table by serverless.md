
### Create service to access datalake table by serverless


1. Install dependencies
   
```bash
    sdk install java  11.0.25-amzn  

    ### Serverless to access datlake table
    pip install databricks-sql-connector
    pip install pyspark
    pip install numpy  

    python -c "import databricks.sql; print('Databricks SQL Connector installed successfully')"

```

####  Starter Warehouse

1. Connection Information
```sql

host: clarivate-databricks-dev-snapshot-us-west-2.cloud.databricks.com
jdbc:databricks://clarivate-databricks-dev-snapshot-us-west-2.cloud.databricks.com:443/default;transportMode=http;ssl=1;AuthMech=3;httpPath=/sql/1.0/warehouses/fa87eb114dffe58e;

```

2. Query data by diasngid

```python

    from databricks import sql

    connection = sql.connect(
        server_hostname= os.getenv("server_hostname"),
        http_path=  os.getenv("http_path"),
        access_token=  os.getenv("access_token")
    )
    query =f"SELECT fuid, cuid, daisngids, reprintauthor, lastauthor, bibissueyear, toppaper, citingsrcslocalcount, title, abstract FROM `wos-family-data`.wos_profile_dev.wos_baseline WHERE  ARRAY_CONTAINS(daisngids, {diasngid}) LIMIT 100 "
    
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    cursor.close()
    connection.close()
```

3. Convert numpy.ndarray is not JSON

```python
    import numpy as np
    from pyspark.sql import Row  # Assuming you are using Spark Row objects


    # Function to convert complex data to JSON-compatible format
    def row_to_dict(row):
        return {
            key: (value.tolist() if isinstance(value, np.ndarray) else value)
            for key, value in row.asDict().items()
        }

    # Convert all rows to dictionaries
    json_compatible_data = [row_to_dict(row) for row in data]

    # Convert to JSON string
    json_result = json.dumps(json_compatible_data, indent=4)

    # Output the JSON
    print(json_result)
```

**Explanation:**
   
- value.tolist(): Converts the numpy.ndarray into a list. This is required because numpy.ndarray is not JSON serializable by default, but lists are.
- json.dumps(): Once the data is converted into a list (from numpy.ndarray), it can be serialized into a valid JSON string.

4. Insert and Update Records:

```python

    from databricks import sql

    # Connection parameters
    server_hostname = "<your-databricks-server-hostname>"
    http_path = "<your-databricks-sql-http-path>"
    access_token = "<your-databricks-personal-access-token>"

    # Establish the connection
    connection = sql.connect(
        server_hostname=server_hostname,
        http_path=http_path,
        access_token=access_token
    )

    try:
        # Create a cursor object
        cursor = connection.cursor()

        # INSERT statement: Add a new row to the Delta table
        insert_query = """
        INSERT INTO your_delta_table (col1, col2, col3)
        VALUES ('value1', 'value2', 123)
        """
        cursor.execute(insert_query)
        print("Insert successful!")

        # UPDATE statement: Modify existing rows in the Delta table
        update_query = """
        UPDATE your_delta_table
        SET col2 = 'updated_value'
        WHERE col1 = 'value1'
        """
        cursor.execute(update_query)
        print("Update successful!")

    except Exception as e:
        print("Error:", e)

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()

```





