

##  Sorting Organizations - Maintain stable, incremental sort order without reassigning sort values 


Got it! For organizations and departments, you want:

- 	One sort field (sort_value) instead of two
- 	Stable values for existing rows
- 	Ability to insert new organizations/departments without touching existing values
- 	Efficient for ~20K rows

We can adapt the same “gap insertion” principle but simplified.

⸻

### 1️⃣ Strategy Overview

1.	Assign initial sort_value to existing organizations with a gap between consecutive rows.
2.	When inserting a new org between two existing orgs, assign a midpoint value rather than +1.
3.	If multiple new orgs are inserted between the same two existing orgs, distribute them evenly within the gap.
4.	Avoid touching existing sort_value → stable ordering.


Step 1: Initial Assignment

- 	Suppose 20,000 orgs
- 	Maximum Long value is huge (~9e18), so safe to leave large gaps
- 	Choose STEP = 10,000 (or larger if desired)

Step 2: Inserting New Organization

- 	Find prev_org and next_org alphabetically surrounding the new org
- 	Compute gap:
```text
  gap = sort_value_next - sort_value_prev
```
- 	Assign midpoint:
```text
  sort_value_new = sort_value_prev + gap / 2
```
- 	Guarantees:
```text
  sort_value_prev < sort_value_new < sort_value_next
```
- 	Leaves room for future inserts:
```text
    sort_value_future = sort_value_prev + gap / 4
    sort_value_future2 = sort_value_prev + 3*gap /4
```

Step 3: Bulk Insert of Multiple Orgs

1.	Sort new orgs alphabetically
2.	For each new org:
- 	Identify prev_org and next_org
- 	Assign sort_value proportional to its position in the gap
```scala
val totalGap = sort_value_next - sort_value_prev
val positionIndex = index of new org in this gap
val numNewOrgs = total number of new orgs in this gap

sort_value_new = sort_value_prev + totalGap * (positionIndex + 1) / (numNewOrgs + 1)
```
- 	Ensures even spacing and preserves order
- 	No existing sort_value changes
  
✅ Alphabetical order preserved, existing values unchanged, room for future inserts

⸻

Step 5: Advantages

1.	Single field → simpler than author two-field approach
2.	Stable existing values → no reassignments
3.	Efficient for bulk inserts using proportional distribution
4.	Scales to tens of thousands of orgs easily
5.	Can increase initial STEP to support decades of incremental growth


⸻

Step 6: Spark Implementation (Delta)

```scala
import org.apache.spark.sql.functions._
import org.apache.spark.sql.expressions.Window

// Existing orgs
val orgsDF = spark.table("orgs").orderBy("org_name")

// New orgs
val newOrgsDF = spark.table("new_orgs").orderBy("org_name")

// For each new org, find prev and next existing org
val windowSpec = Window.orderBy("org_name")
val joinedDF = newOrgsDF
  .withColumn("prev_sort", last("sort_value", ignoreNulls=true).over(windowSpec.rowsBetween(Window.unboundedPreceding, -1)))
  .withColumn("next_sort", first("sort_value", ignoreNulls=true).over(windowSpec.rowsBetween(1, Window.unboundedFollowing)))

// Calculate proportional sort_value
val withSortValueDF = joinedDF
  .withColumn("position_index", row_number().over(windowSpec)-1)
  .withColumn("num_new_in_gap", count("*").over(windowSpec))
  .withColumn("sort_value_new",
    col("prev_sort") + (col("next_sort") - col("prev_sort")) * (col("position_index")+1) / (col("num_new_in_gap")+1)
  )

// Insert into Delta
withSortValueDF
  .select(
    monotonically_increasing_id().as("pguid"),
    col("org_name"),
    col("sort_value_new").as("sort_value")
  )
  .write.format("delta").mode("append").saveAsTable("orgs")
```


### ✅ Summary

- 	Single sort field, stable for existing rows
- 	New orgs inserted proportionally within gap
- 	Alphabetical order preserved
- 	Efficient bulk insert algorithm
- 	Scales well for 20K organizations/departments


*This approach can be applied other entity names: funding organiztions, journal, regions etc.*
