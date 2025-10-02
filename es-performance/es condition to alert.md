# Factor | Condition to Alert

### Identify Conditions for Cluster Abnormalities: Major Factors to Alert

---

### High Resource Utilization
- CPU usage > 80% for extended periods
- Memory usage > 75%
- Disk usage > 85%

---

### Node Failures or Unreachable Nodes
- Nodes frequently going down or unreachable
- Cluster status shows "red" or "yellow"
- Missing nodes in cluster

---

### Slow Query Performance
- Significant increase in query response times (e.g., > 5 seconds)
- High query queue lengths or timeouts

---

### Replication or Shard Allocation Issues
- Unassigned shards
- Replication lag or failures
- Uneven shard distribution across nodes

---

### Increased Error Rate
- High number of failed requests (e.g., 500 errors)
- Unusual spikes in error logs
- Frequent timeouts

---

### Data Consistency Issues
- Mismatched data across replicas
- Unexpected changes in indexed data
- Failed indexing

---

### Cluster Recovery Failures
- Failures during recovery or rebalancing
- Delay in recovering nodes/shards
- Failures during shard reassignment

---

### High Garbage Collection Activity
- Frequent or long garbage collection pauses
- JVM heap usage near maximum

---

### Network Latency or Partitioning
- High network latency between nodes
- Connectivity issues between cluster nodes
