
Setting up a Docker-based ClickHouse cluster allows you to deploy, scale, and test ClickHouse in both local and cloud environments like AWS. Here’s a detailed step-by-step guide for setting up a configurable ClickHouse cluster on AWS and locally on a MacBook.


https://github.com/ClickHouse/spark-clickhouse-connector


### 1. Prerequisites

#### Local (MacBook) Setup
	•	Install Docker Desktop: Docker Desktop for Mac
	•	Install a terminal tool like iTerm2 or use the default Terminal.

#### AWS Setup
	•	Access to an AWS account.
	•	Install the AWS CLI: AWS CLI Installation.
	•	Install Terraform or use AWS Console for provisioning EC2 instances.
	•	A VPC and subnets set up to launch EC2 instances (optional, can use defaults).


### 2. Architecture

	•	A ClickHouse cluster consists of one or more shards, with replicas per shard (if desired).
	•	Each shard has:
        •	One or more nodes for data storage and query execution.
        •	ZooKeeper for coordination (if replicas are used).
	•	You can configure the number of shards and replicas to scale the cluster.


### 3. Setting Up Locally on MacBook

#### Step 1: Create a docker-compose.yml File

This configuration launches a cluster with multiple shards and optional ZooKeeper.

Example docker-compose.yml:

```yaml
version: '3.8'

services:
  zookeeper:
    image: zookeeper:3.8
    container_name: zookeeper
    ports:
      - "2181:2181"

  clickhouse-node1:
    image: clickhouse/clickhouse-server:22.8
    container_name: clickhouse-node1
    environment:
      CLICKHOUSE_LOG_LEVEL: debug
    volumes:
      - clickhouse-node1-data:/var/lib/clickhouse
      - ./config:/etc/clickhouse-server
    ports:
      - "8123:8123"
      - "9000:9000"
      - "9009:9009"
    depends_on:
      - zookeeper

  clickhouse-node2:
    image: clickhouse/clickhouse-server:22.8
    container_name: clickhouse-node2
    environment:
      CLICKHOUSE_LOG_LEVEL: debug
    volumes:
      - clickhouse-node2-data:/var/lib/clickhouse
      - ./config:/etc/clickhouse-server
    ports:
      - "8124:8123"
      - "9001:9000"
      - "9010:9009"
    depends_on:
      - zookeeper

volumes:
  clickhouse-node1-data:
  clickhouse-node2-data:
```


#### Step 2: Configure ClickHouse

1.	Add Configuration Files:
	•	Create a config.xml in the ./config directory.
	•	Add a cluster configuration with shards and replicas.

Example config.xml:
```xml
<yandex>
  <remote_servers>
    <my_cluster>
      <shard>
        <replica>
          <host>clickhouse-node1</host>
          <port>9000</port>
        </replica>
      </shard>
      <shard>
        <replica>
          <host>clickhouse-node2</host>
          <port>9000</port>
        </replica>
      </shard>
    </my_cluster>
  </remote_servers>
  <zookeeper>
    <node index="1">
      <host>zookeeper</host>
      <port>2181</port>
    </node>
  </zookeeper>
</yandex>
```

2.	Start Docker Containers:

```bash
docker-compose up -d
```

3.	Verify the Cluster:
	•	Access the ClickHouse shell:

```bash
docker exec -it clickhouse-node1 clickhouse-client
```

    •	Run:

```sql
SELECT * FROM system.clusters;
```

### 4. Setting Up on AWS


#### Step 1: Launch EC2 Instances
	•	Use Terraform or AWS Console to launch EC2 instances.
	•	Choose an AMI with Docker pre-installed (or install Docker manually).
	•	Use a security group to allow:
	•	Port 8123 (HTTP interface).
	•	Port 9000 (TCP interface).
	•	Port 2181 (ZooKeeper).

#### Step 2: Install Docker on EC2 Instances

1.	SSH into each instance:

```bash
ssh -i your-key.pem ec2-user@<EC2_IP>
```

2.	Install Docker:
```bash
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user
```
3.	Re-login to apply Docker permissions.

#### Step 3: Transfer Docker Compose Configurations
	•	Copy docker-compose.yml and config files to each EC2 instance using scp:

```bash
scp -i your-key.pem docker-compose.yml ec2-user@<EC2_IP>:/home/ec2-user/
scp -i your-key.pem -r config ec2-user@<EC2_IP>:/home/ec2-user/
```

#### Step 4: Start the Cluster

1.	Run the cluster on each EC2 instance:

```bash
docker-compose up -d
```

2.	Connect to any node:

```bash
docker exec -it clickhouse-node1 clickhouse-client
```

### 5. Configuration Variables
	•	Number of shards: Modify the remote_servers section in config.xml.
	•	Number of replicas per shard: Add or remove <replica> tags.
	•	Add more nodes: Add more services in docker-compose.yml.

### 6. Testing the Setup
	•	Create tables using the cluster:

```sql
CREATE TABLE test_table ON CLUSTER my_cluster (
    id UInt32,
    name String
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/test_table', '{replica}')
ORDER BY id;
```

	•	Insert and query data to test the cluster behavior:


```sql
INSERT INTO test_table VALUES (1, 'ClusterTest');
SELECT * FROM test_table;
```

This setup works both locally and on AWS by following the same principles. For AWS, ensure proper networking and security settings.



### 6.Use Clickhouse


#### 1. Use the ClickHouse Client Inside the Container

1.	Access the container:

docker exec -it loving_goldwasser  clickhouse-client


2.	Run SQL queries:

```sql
CREATE TABLE example_table (
    id UInt32,
    name String,
    value Float32
) ENGINE = MergeTree()
ORDER BY id;

INSERT INTO example_table VALUES (1, 'John Doe', 123.45), (2, 'Jane Smith', 678.90);

SELECT * FROM example_table;

```

#### 2. Use HTTP Interface

Send a query using curl:

```bash
curl -X POST 'http://localhost:8123/' --data 'CREATE TABLE example_table (id UInt32, name String) ENGINE = Memory'
curl -X POST 'http://localhost:8123/' --data 'INSERT INTO example_table VALUES (1, "Alice"), (2, "Bob")'
curl -X POST 'http://localhost:8123/' --data 'SELECT * FROM example_table FORMAT JSON'
```


#### 3. Use ClickHouse JDBC/ODBC Drivers

If you want to connect programmatically (e.g., using Python, Java, or BI tools like Tableau), you can use ClickHouse’s JDBC/ODBC drivers.


pip install clickhouse-connect

```python
import clickhouse_connect

# Connect to the server
client = clickhouse_connect.get_client(host='localhost', port=8123, username='default', password='')

# Create a table
client.command('CREATE TABLE example_table (id UInt32, name String) ENGINE = Memory')

# Insert data
client.command("INSERT INTO example_table VALUES (1, 'Alice'), (2, 'Bob')")

# Query data
result = client.query('SELECT * FROM example_table')
print(result.result_rows)

```

#### 4. Hands on

- Install Docker
  Pull the ClickHouse Docker Image
  Run the ClickHouse Container

```bash 
docker pull clickhouse/clickhouse-server
docker run -d --name clickhouse-server -p 8123:8123 -p 9000:9000 -p 9009:9009 clickhouse/clickhouse-server
```

- Mounting Volumes for Persistent Data

```bash
docker run -d \
  --name clickhouse-server \
  -p 8123:8123 -p 9000:9000 -p 9009:9009 \
  -v //Users/r.chen/workspace/clickhouse:/var/lib/clickhouse \
  clickhouse/clickhouse-server
```

- Configure ClickHouse (Optional)

```bash
docker run -d \
  --name clickhouse-server \
  -p 8123:8123 -p 9000:9000 -p 9009:9009 \
  -v /path/to/local/config:/etc/clickhouse-server \
  clickhouse/clickhouse-server
```

- Stop or Remove the Container
  
```bash
docker stop clickhouse-server
docker rm clickhouse-server
```

- Access the ClickHouse Server

a. HTTP Interface:
```bash
  curl http://localhost:8123/
```

b. ClickHouse Client:
```bash
  clickhouse-client --host=127.0.0.1 --port=9000
```

c. Docker Exec:
```bash
  docker exec -it clickhouse-server clickhouse-client
```

- Path

configuration file: /etc/clickhouse-server/config.xml
Logging file:       /var/log/clickhouse-server/clickhouse-server.log
Logging errors:     /var/log/clickhouse-server/clickhouse-server.err.log

Start Option: 

binding:      local path --->  /var/lib/clickhouse
/var/log/


clickhouse-jdbc-0.8.0.jar