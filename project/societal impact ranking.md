

## Societal Impact - Quantitle


- Step 1: Creates a table that calculates the percentage of institutions above each pub_count threshold for every (facet, indicator) pair, only including publication counts that meet or exceed a predefined threshold.
- Step 2: Creates a table that calculates the minimum publication count required to be in or above each quantile threshold for each (facet, indicator) pair.


#### Summary of Calculation


Phase-1. Calculate the distinct count for each metric, grouped by institution, facet, and period. (Slide 5 -10)


Phase-2. Calculate Thresholds (Slide 18 - 19)

- step-1: Calculate institution_count_by_pub_count
- step-2: Calculate percentage_above_threshold_by_pub_count
- step-3: Calculate table possible_thresholds
- step-4: Calculate thresholds

Paramters: SET_OF_POSSIBLE_THRESHOLDS, MINIMUM_THRESHOLD_FOR_SPECIFIC_INDICATORS, MINIMUM_INCLUSION_PERCENTAGE

Phase-3. Calculate Size Dependent Ranking (Slide 14)
   
- Step-1: Calculate percentage_above_threshold_by_pub_count_with_threshold
- Step-2: Calculate min_pub_count_per_quantile

Paramters: QUANTILES, thresholds(Phase-2)

Phase-4. Calculate Size Normalized Ranking (Similar to Slide 14)

- step-1: Calculate size_normalized_indicators
- step-2: Calculate institution_count_by_ratio
- step-3: Calculate percentage_above_threshold_by_ratio_with_threshold
- step-4: Calculate min_ratio_per_quantile

Paramters: QUANTILES, thresholds(Phase-2)


Phase-5. Calculate Quantiles
   
- step 1: Calculate the size-dependent quantile  when the numerator is greater than or equal to the specified threshold.
- step 2: Calculate the size-normalized quantile when both the numerator and denominator are greater than or equal to the specified thresholds (Slide 11)

Paramters: min_pub_count_per_quantile (Phase-3), min_ratio_per_quantile(Phase-4)



---


## A.1  Societal Impact - Rankings



###  Size-dependent indicators 

✅ Step 1: percentage_above_threshold_by_pub_count_with_threshold


Purpose:

This query creates a table that calculates the percentage of institutions above each publication count (pub_count) threshold, but only for pub_count values that meet or exceed a pre-defined threshold (per facet and indicator).

```sql
CREATE TABLE percentage_above_threshold_by_pub_count_with_threshold AS
SELECT 
  facet, 
  indicator, 
  pub_count,
  100 * (CUM_SUM(institution_count) OVER (PARTITION BY facet, indicator ORDER BY pub_count DESC)) 
    / SUM(institution_count) OVER (PARTITION BY facet, indicator) AS excess_pc
FROM institution_count_by_pub_count counts
INNER JOIN thresholds
  ON thresholds.facet = counts.facet 
  AND thresholds.indicator = counts.indicator
WHERE pub_count >= threshold
GROUP BY facet, indicator, pub_count
ORDER BY pub_count;
```

🔍 What it does:

-	Inputs:
    -	institution_count_by_pub_count: contains the number of institutions with each publication count per (facet, indicator).
    -	thresholds: defines the minimum publication count required for each (facet, indicator).
-	Filtering:
    -	Only includes rows where pub_count >= threshold (i.e., institutions meeting a defined publication count threshold).
-	Window Functions:
    -	CUM_SUM(...) OVER (...): running total of institution counts from highest pub_count downward.
    -	SUM(...) OVER (...): total institution count across all publication levels for that facet+indicator.
-	excess_pc: Percentage of institutions that have pub_count >= this row's pub_count.

🧾 Output:

Table showing, for each facet, indicator, pub_count, the % of institutions exceeding that publication count, filtered to meet threshold.

| facet | indicator | pub_count | excess_pc |
|-------|-----------|-----------|-----------|
| A     | X         | 20        | 8.0       |
| A     | X         | 10        | 20.0      |


Summary:

-	Filters to only pub_count values above the minimum threshold for that facet+indicator.
-	Calculates for each remaining pub_count the percentage of institutions with at least that count.
-	Useful for scoring or selecting meaningful thresholds that reflect top performers.


---

✅ Step 2: min_pub_count_per_quantile

Creates a table min_pub_count_per_quantile that determines the minimum publication count (pub_count) required to be in or above a given quantile threshold for each (facet, indicator) pair.

```sql
CREATE TABLE min_pub_count_per_quantile AS
SELECT 
  facet, 
  indicator, 
  quantile, 
  MIN(pub_count) AS min_pub_count
FROM percentage_above_threshold_by_pub_count_with_threshold
CROSS JOIN QUANTILES
WHERE excess_pc >= quantile
GROUP BY facet, indicator, quantile;
```

-	QUANTILES: A list of target quantile percentages (e.g., 1, 5, 10, 25, 50, etc.)

🔍 What it does:

-	Goal: For each facet, indicator, quantile, find the minimum pub_count such that at least quantile% of institutions meet or exceed it.
    -	CROSS JOIN with QUANTILES:
    -	QUANTILES contains values like 10, 25, 50, 75, 90 (or whatever quantiles you’re targeting).
    -	This cross joins every row with each quantile — enabling you to check how many institutions exceed that level.
-	Filtering:
    -	WHERE excess_pc >= quantile: Only consider rows where the percentage of institutions with that pub_count is greater than or equal to the quantile.
-	Aggregation:
    -	MIN(pub_count): Among those rows, pick the smallest pub_count — i.e., the minimum publication count required to exceed that quantile.

🧾 Output:

For each quantile, it shows the minimum publication count needed to be included in the top N% of institutions.

| facet | indicator | quantile | min_pub_count |
|-------|-----------|----------|----------------|
| A     | X         | 90       | 10             |
| A     | X         | 75       | 6              |


---

📌 Summary:

These two queries work together to:
1.	Calculate % of institutions that meet or exceed certain pub_count levels (after threshold).
2.	Determine the minimum publication count required to be in the top 90%, 75%, etc., of institutions — per (facet, indicator).


---


##  Societal Impact - Thresholds


Summary

- Step-1:  Creates a table that counts the number of distinct institutions for each (facet, indicator, pub_count) combination 
- Step-2:  Creates a table that calculates, for each (facet, indicator, pub_count), the percentage of institutions that have publication counts greater than or equal to that pub_count (i.e., are above the threshold).
- Step-3: Creates a table of potential threshold values by selecting (facet, indicator, pub_count) pairs from a predefined set of possible thresholds where the publication count exceeds any specified minimum for that indicator.
- Step-4: Creates a table that selects the final threshold pub_count for each (facet, indicator) pair by choosing the highest publication count that either exceeds a minimum inclusion percentage or is the top-ranked value (i.e., has the highest pub_count).

---

###  Lower threshold algorithm parameters

Parameters for the algorithm:

- SET_OF_POSSIBLE_THRESHOLDS
  - Instead of allowing any number from 1 to 200, restrict to a user-friendly set of numbers
  - Suggested: 1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 60, 80, 100, 125, 150, 200
- MINIMUM_THRESHOLD_FOR_SPECIFIC_INDICATORS:
  - Some indicators need a higher minimum threshold than 1 as they’re used as denominators in size-normalized indicators
- Suggested:
  - {“LD1.1”: 50, “LD3.1”: 25}
- MINIMUM_INCLUSION_PERCENTAGE
  - Suggested: 50, however, this may vary by indicator – this is to be decided


---

###  Thresholds  - Lower threshold algorithm 

Here’s a clear step-by-step explanation of your SQL logic — this is a pipeline designed to find appropriate publication count thresholds per (facet, indicator) based on institutional distribution.


✅ Step 1: institution_count_by_pub_count


🔍 Purpose:
Creates a table that counts the number of distinct institutions for each (facet, indicator, pub_count) combination 


```sql
CREATE TABLE institution_count_by_pub_count AS
SELECT 
  facet, 
  indicator, 
  pub_count, 
  COUNT(DISTINCT institutions) AS institution_count
FROM data
GROUP BY facet, indicator, pub_count;
```

🔍 What it does:

-	For each combination of facet, indicator, and pub_count:
-	Counts how many distinct institutions have exactly that pub_count value.
-	Produces a table like:

| facet | indicator | pub_count | institution_count |
|-------|-----------|-----------|--------------------|
| A     | X         | 5         | 12                 |
| A     | X         | 10        | 4                  |
| …     | …         | …         | …                  |


This is the starting distribution of institutions by publication count.

---

✅ Step 2: percentage_above_threshold_by_pub_count


🔍 Purpose:
Creates a table that calculates, for each (facet, indicator, pub_count), the percentage of institutions that have publication counts greater than or equal to that pub_count (i.e., are above the threshold).

This query calculates the percentage of institutions that have a publication count greater than or equal to a given count (pub_count) for each (facet, indicator) combination. It creates a cumulative distribution of institutions from highest pub_count downward.

```sql
CREATE TABLE percentage_above_threshold_by_pub_count AS
SELECT 
  facet, 
  indicator, 
  pub_count,
  100 * (CUM_SUM(institution_count) OVER (PARTITION BY facet, indicator ORDER BY pub_count DESC)) 
      / SUM(institution_count) OVER (PARTITION BY facet, indicator) AS excess_pc
FROM institution_count_by_pub_count
GROUP BY facet, indicator, pub_count
ORDER BY pub_count DESC;
```

🔍 What it does:

-	Calculates a cumulative percentage of institutions that have at least a certain pub_count.
-	The CUM_SUM(...) OVER (...) (cumulative sum) adds up the number of institutions with pub_count >= N.
-	Dividing by the total number of institutions gives the excess percentage (excess_pc).
-	Result: for each (facet, indicator, pub_count), it tells you what percent of institutions meet or exceed that publication count.



🧮 Key Computation:

-	Window Function:
CUM_SUM(institution_count) OVER (...) → running total of institution counts in descending pub_count order, per (facet, indicator).
-	Total Institutions:
SUM(institution_count) OVER (...) → total number of institutions for that (facet, indicator).
-	Percentage Calculation:
excess_pc = cumulative sum ÷ total × 100
→ gives % of institutions having pub_count ≥ current row’s value.


| facet | indicator | pub_count | excess_pc |
|-------|-----------|-----------|-----------|
| A     | X         | 20        | 5.0       |
| A     | X         | 10        | 15.0      |
| A     | X         | 5         | 40.0      |


---

✅ Step 3: possible_thresholds


🔍 Purpose:
Creates a table of potential threshold values by selecting (facet, indicator, pub_count) pairs from a predefined set of possible thresholds where the publication count exceeds any specified minimum for that indicator.


```sql
CREATE TABLE possible_thresholds AS
SELECT 
  facet, 
  indicator, 
  pub_count, 
  excess_pc
FROM percentage_above_threshold_by_pub_count AS sums
INNER JOIN SET_OF_POSSIBLE_THRESHOLDS AS thresholds
  ON sums.pub_count = thresholds.threshold
LEFT JOIN MINIMUM_THRESHOLD_FOR_SPECIFIC_INDICATORS AS exceptions
  ON sums.indicator = exceptions.indicator
WHERE sums.pub_count > COALESCE(exceptions.pub_count, 0);
```

🔍 What it does:

-	Filters the rows from step 2 to find allowed threshold candidates:
	1.	The pub_count must exist in SET_OF_POSSIBLE_THRESHOLDS.
	2.	It must be above a minimum threshold (if specified) in MINIMUM_THRESHOLD_FOR_SPECIFIC_INDICATORS.

The final table gives you possible publication thresholds per (facet, indicator) that satisfy policy constraints and ensure a manageable number of institutions (based on excess_pc).

| facet | indicator | pub_count | excess_pc |
|-------|-----------|-----------|-----------|
| A     | X         | 10        | 15.0      |


Summary:

-	Filters down a pre-defined list of candidate thresholds to only those:
-	Actually observed in the data (pub_count in sums)
-	Included in the official list of allowed thresholds (thresholds)
-	Exceed the minimum requirement for the indicator (exceptions)


✅ Why it’s useful here:

This ensures the WHERE clause always has a value to compare against, avoiding errors or accidental exclusion of rows where no exception was defined.

🧠 Example:

| sums.pub_count | exceptions.pub_count | COALESCE(exceptions.pub_count, 0) | Result of Condition         |
|----------------|----------------------|-----------------------------------|-----------------------------|
| 50             | 40                   | 40                                | 50 > 40 = ✅                |
| 50             | NULL                 | 0                                 | 50 > 0 = ✅                 |
| 10             | 20                   | 20                                | 10 > 20 = ❌                |
| 10             | NULL                 | 0                                 | 10 > 0 = ✅                 |


---


✅ Step 4: thresholds


```sql
CREATE TABLE thresholds AS
SELECT
  facet,
  indicator,
  MAX(pub_count) AS threshold
FROM possible_thresholds
JOIN MINIMUM_INCLUSION_PERCENTAGE
WHERE
  excess_pc > MINIMUM_INCLUSION_PERCENTAGE.percentage
  OR RANK() OVER (PARTITION BY facet, indicator ORDER BY pub_count DESC) = 1
GROUP BY facet, indicator;
```

🔍 What it does:

-	Inputs:
  -	possible_thresholds: contains publication counts and excess percentage values for each (facet, indicator) combination.
  -	MINIMUM_INCLUSION_PERCENTAGE: defines the minimum percentage threshold for including data.
-	Filtering:
  -	Includes rows where excess_pc > percentage (i.e., the proportion of data above this publication count is significant).
  -	Also includes the row with the lowest publication count (rank() = 1) for each (facet, indicator) to guarantee baseline coverage.
-	Window Functions:
  -	RANK() OVER (PARTITION BY facet, indicator ORDER BY pub_count): assigns rank to rows based on ascending pub_count within each (facet, indicator) group.
-	Aggregation:
  -	For each (facet, indicator), selects the maximum pub_count among the filtered rows as the final threshold.
-	Output:
  -	A new table thresholds with the highest relevant pub_count per (facet, indicator) that meets inclusion criteria or serves as a fallback baseline.


📦 Example Input & Output

Input: possible_thresholds

| Facet   | Indicator | Pub Count | Excess PC |
|---------|-----------|-----------|-----------|
| Country | Citations | 200       | 0.07      |
| Country | Citations | 150       | 0.03      |
| Country | Papers    | 100       | 0.06      |
| Country | Papers    | 80        | 0.01      |


Input: MINIMUM_INCLUSION_PERCENTAGE

|percentage|
|---------|
|0.05     |


Step-by-step:

-	Threshold = 0.05
-	excess_pc > 0.05: Only rows with 200 and 100 pass.
-	For papers, the lowest pub_count = 80, so we also keep that row due to rank() = 1.

Filtered rows:

| Facet   | Indicator | Pub Count |
|---------|-----------|-----------|
| Country | Citations | 200       |
| Country | Papers    | 100       |
| Country | Papers    | 80        |


Grouped by facet, indicator → take max(pub_count)

| Facet   | Indicator | Threshold |
|---------|-----------|-----------|
| Country | Citations | 200       |


✅ Final Output Table: thresholds

| Facet   | Indicator | Threshold |
|---------|-----------|-----------|
| Country | Citations | 200       |
| Country | Papers    | 100       |


✅ Summary

This query:
-	Ensures only meaningful data (based on excess_pc) is kept,
-	But always keeps the row with the lowest pub_count (even if it doesn’t meet the excess_pc threshold),
-	Then sets a threshold value per (facet, indicator) as the maximum of the remaining pub_count.


---

📌 Summary:

This entire query sequence is used to:
-	Analyze institutional contribution levels by publication count.
-	Determine what threshold to use (e.g., only include institutions with ≥ X publications) for fair and manageable inclusion.
-	Apply minimum and allowed thresholds to ensure consistency and quality.



Size normalization


| Indicator                                      | Numerator | Denominator                   |
|------------------------------------------------|-----------|-------------------------------|
| LD 1.1 Contribution to facet                   | LD1.1     | Total output by institution   |
| LD 2.1 Non-academic collaboration             | LD2.1     | LD1.1                         |
| LG1.1 Papers consistently cited by non-academics | LG1.1     | LD1.1                         |
| LG2.1 Papers cited by patents                 | LG2.1     | LD1.1                         |
| LD3.1 Patent applications                     | LD3.1     | LD1.1                         |
| LG2.2 Patents granted                         | LG2.2     | LD3.1                         |



Size-dependent indicators


| Bucket    | Quantile | Description         | Lower Limit (%) | Upper Limit (%) |
|-----------|----------|---------------------|-----------------|-----------------|
| Bucket 1  | N/A      | Below threshold     | N/A             | *threshold*     |
| Bucket 2  | 20%      | < 20%               | *threshold*     | 20              |
| Bucket 3  | 30%      | ≥ 20% and < 30%     | 20              | 30              |
| Bucket 4  | 40%      | ≥ 30% and < 40%     | 30              | 40              |
| Bucket 5  | 50%      | ≥ 40% and < 50%     | 40              | 50              |
| Bucket 6  | 60%      | ≥ 50% and < 60%     | 50              | 60              |
| Bucket 7  | 70%      | ≥ 60% and < 70%     | 60              | 70              |
| Bucket 8  | 80%      | ≥ 70% and < 80%     | 70              | 80              |
| Bucket 9  | 90%      | ≥ 80% and < 90%     | 80              | 90              |
| Bucket 10 | 95%      | ≥ 90% and < 95%     | 90              | 95              |
| Bucket 11 | 99%      | ≥ 95% and < 99%     | 95              | 99              |
| Bucket 12 | N/A      | ≥ 99%               | 99              | N/A             |


---

### Calculate Normalized Quantile 



✅  Step-1: size_normalized_indicators

```sql
-- Start by calculating the ratios
-- This just provides the data we're working with below
-- I'm assuming required_ratios includes which ratios we
--   actually need to calculate, such as LD2.1/LD1.1 etc.
-- I'm also assuming threshold_filtered_data only includes
--   data where an institution's value is at or above the
--   threshold for that indicator/facet/year_range, so we're
--   not calculating ratios we're not actually going to use



create table size_normalized_indicators as
select facet, institution, year_range,
        left_data.indicator as numerator,
    right_data.indicator as denominator,
    left_data.value / right_data.value as ratio
    from threshold_filtered_data numerator_data
    inner join threshold_filtered_data denominator_data
        on numerator_data.facet = denominator_data.facet
        and numerator_data.institution = denominator_data.institution
        and numerator_data.year_range = denominator_data.year_range
    inner join required_ratios
        on required_ratios.numerator = numerator_data.indicator
        and required_ratios.denominator = denominator_data.indicator;

  ```

---

✅  Step-2: institution_count_by_ratio


```sql
-- Pulling in similar code from slide 18 for code on slide 14 to work with:
create table institution_count_by_ratio as
select facet, numerator, denominator, year_range, ratio,
        count(distinct institutions) as institution_count
    from size_normalized_indicators
  group by facet, numerator, denominator, year_range, ratio;
```


✅  Step-3: percentage_above_threshold_by_ratio_with_threshold


```sql
-- The rest of this is as per slide 14
-- No need to bring in the threshold code again, though, as the 
--   above code ensures we only include institutions above the necessary
--   thresholds
create table percentage_above_threshold_by_ratio_with_threshold as
select facet, numerator, denominator, year_range, ratio,
    100 * (cum_sum(institution_count) over (facet, indicator)) / sum(institution_count) as excess_pc
    from institution_count_by_ratio
    group by facet, numerator, denominator, year_range, ratio
    order by ratio
  ```

---


✅  Step-4: min_ratio_per_quantile


```
create table min_ratio_per_quantile
select facet, numerator, denominator, year_range, quantile, min(ratio) as min_ratio
    from percentage_above_threshold_by_ratio_with_threshold
        cross join QUANTILES
    where excess_pc >= quantile
    group by facet, numerator, denominator, year_range, quantile
```



---


## A.3 ES Implementation  ( complciated & Impractible)


Let’s now walk through how to implement each step from your SQL logic in Elasticsearch using the structure of your document. Your SQL workflow breaks into these logical parts:

Example ES Documents

```json

{
    "facet": ["Health", "Medical"],
    "indicator": ["non-acadmeia", "citation fromnon-academia"],
    "institutions" {"Harvard University", "MIT", "Standford"},
    "pubyear": 2021
}
```

Lower threshold algorithm parameters

- SET_OF_POSSIBLE_THRESHOLDS
  - Instead of allowing any number from 1 to 200, restrict to a user-friendly set of numbers
  - Suggested: 1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 60, 80, 100, 125, 150, 200
- MINIMUM_THRESHOLD_FOR_SPECIFIC_INDICATORS:
  - Some indicators need a higher minimum threshold than 1 as they’re used as denominators in size-normalized indicators
- Suggested:
  - {“LD1.1”: 50, “LD3.1”: 25}
- MINIMUM_INCLUSION_PERCENTAGE
  - Suggested: 50, however, this may vary by indicator – this is to be decided


---

🔹 1. institution_count_by_pub_count

Elasticsearch equivalent (aggregation):

```json
{
  "size": 0,
  "aggs": {
    "by_facet": {
      "terms": { "field": "facet.keyword" },
      "aggs": {
        "by_indicator": {
          "terms": { "field": "indicator.keyword" },
          "aggs": {
            "by_pubyear": {
              "terms": { "field": "pubyear" },
              "aggs": {
                "institution_count": {
                  "cardinality": { "field": "institutions" }
                }
              }
            }
          }
        }
      }
    }
  }
}

```

---

🔹 2. percentage_above_threshold_by_pub_count


✅ Use Case: Cumulative Counts with histogram

Suppose you want to calculate how many institutions exceed a given pub_count threshold. Using histogram, you can:

1.	Group documents by pub_count (or any numeric field).
2.	Count institutions per bucket.
3.	Calculate cumulative counts manually or via a visualization tool like Kibana (or in client code).

excess_pc = 100 * cumulative_institution_count / total_institution_count



```json

{
  "size": 0,
  "aggs": {
    "pub_count_hist": {
      "histogram": {
        "field": "pub_count",
        "interval": 5,
        "order": "key",
        "min_doc_count": 1
      },
      "aggs": {
        "institution_count": {
          "cardinality": {
            "field": "institutions.keyword"
          }
        }
      }
    }
  }
}
```


✅ Alternatives:

```json
{
  "aggs": {
    "histogram": {
      "histogram": {
        "field": "pub_count",
        "interval": 5
      },
      "aggs": {
        "institution_count": {
          "cardinality": {
            "field": "institutions.keyword"
          }
        },
        "cum_count": {
          "cumulative_sum": {
            "buckets_path": "institution_count"
          }
        }
      }
    }
  }
}
```


---

🔹 3. possible_thresholds


ES equivalent:
1.	Use a terms filter on pubyear (representing pub_count) to only keep values from SET_OF_POSSIBLE_THRESHOLDS.
2.	Filter out pubyear below indicator-specific minimum thresholds (can do in the client after pulling results or use a script filter if hardcoded).

Example filter:

```json
"query": {
  "bool": {
    "filter": [
      { "terms": { "pubyear": [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 60, 80, 100, 125, 150, 200] }},
      { "range": { "pubyear": { "gt": 25 }} }  // for LD3.1, e.g.
    ]
  }
}
```

---

🔹 4. percentage_above_threshold_by_pub_count_with_threshold


```json
"query": {
  "bool": {
    "filter": [
      { "range": { "pubyear": { "gte": <threshold> } } }
    ]
  }
}
```


---

🔹 5. min_pub_count_per_quantile

Elasticsearch equivalent:

You’ll calculate excess_pc for each bucket (as before), and for a predefined list of quantiles ([10, 25, 50, 75, 90], etc.), find the minimum pubyear where excess_pc >= quantile. This step has to be computed client-side unless using Elasticsearch transforms.


---


Summary of Required ES Capabilities:

-	Aggregation pipeline: yes ✅
-	Cumulative aggregations: not supported natively; implement via client or transform jobs
-	Threshold filtering: doable via query filters ✅
-	Cross join logic: emulate via loop on quantiles on the client ✅
-	Institution deduplication: supported using cardinality agg ✅
    


---


## A.4 Requirement Analysis for Societal Impact Metric - Quantitle



Phase-1: Precalulcate Threshholds

- Step-1:  Counts the number of distinct institutions  per facet, indicator, pub_count 
- Step-2:  Calculates the percentage of institutions that have publication counts greater than or equal to that pub_count 
- Step-3: Selecting  thresholds from a predefined set of possible thresholds where the publication count exceeds any specified minimum for that indicator
- Step-4: Creates a table that selects the final threshold pub_count for each (facet, indicator) pair by choosing the highest publication count that either exceeds a minimum inclusion percentage or is the top-ranked value (i.e., has the highest pub_count).


Phase-2: Precalulcate Ratings

- Step 1:  Calculates the percentage of institutions above each pub_count threshold per facet, indicator, only including publication counts that meet or exceed a predefined threshold.
- Step-2: Calculates the minimum publication count required to be in or above each  quantile threshold  per facet, indicator, predefined quantile.



Phase 3: Calculate Quartile Value Dynamically

- Step 1: Evaluate indicator qualification for the Quartiles metric using the dynamic document count and predefined threshold values.
- Step 2: Assign the appropriate quartile bucket based on the document count and the minimum document count defined in the predefined quartile table.


---

## A.5 Spark Implementation


### 1.  Thresholds  - Lower threshold algorithm 



✅  Step-1: table institution_count_by_pub_count 

Objective

From a source DF with columns:
-	doc_id: String
-	facet: Array[String]
-	indicator: Array[String]
-	organization: Array[String]

We want to produce a DataFrame with:
-	facet
-	indicator
-	pub_count = number of documents per (facet, indicator, organization)
-	institution_count = number of distinct organizations for each (facet, indicator, pub_count)


```scala
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

// Step 1: Explode arrays to get one row per (doc_id, facet, indicator, organization)
val exploded = documents
  .withColumn("facet", explode(col("facet")))
  .withColumn("indicator", explode(col("indicator")))
  .withColumn("organization", explode(col("organization")))

// Step 2: Count number of documents (pub_count) per (facet, indicator, organization)
val pubCountByOrg = exploded
  .groupBy("facet", "indicator", "organization")
  .agg(countDistinct("doc_id").alias("pub_count"))

// Step 3: Count number of distinct organizations (institution_count) per (facet, indicator, pub_count)
val institutionCountByPubCount = pubCountByOrg
  .groupBy("facet", "indicator", "pub_count")
  .agg(countDistinct("organization").alias("institution_count"))

// Show the final result
institutionCountByPubCount.show()

institutionCountByPubCount.write
  .format("delta")
  .mode("overwrite") // use "append" if you want to add to existing
  .saveAsTable("institution_count_by_pub_count")

```

---

✅  Step-2: table percentage_above_threshold_by_pub_count 


```scala
import org.apache.spark.sql.expressions.Window
import org.apache.spark.sql.functions._

// Step 1: Define window specs
val windowSpec = Window.partitionBy("facet", "indicator").orderBy(col("pub_count").desc)
val totalWindow = Window.partitionBy("facet", "indicator")

// Step 2: Compute excess_pc
val percentageAboveThreshold = institutionCountByPubCount
  .withColumn("cum_sum", sum("institution_count").over(windowSpec))
  .withColumn("total", sum("institution_count").over(totalWindow))
  .withColumn("excess_pc", col("cum_sum") * 100 / col("total"))
  .select("facet", "indicator", "pub_count", "excess_pc")
  .orderBy(col("pub_count").desc)

// Step 3: Save as a Delta table
percentageAboveThreshold.write
  .format("delta")
  .mode("overwrite") // use "append" if you want to add to existing
  .saveAsTable("percentage_above_threshold_by_pub_count")
```

---

✅  Step-3: table institution_count_by_pub_count 


```scala

val percentageDf = spark.table("percentage_above_threshold_by_pub_count")
val thresholdsDf = spark.table("SET_OF_POSSIBLE_THRESHOLDS")
val exceptionsDf = spark.table("MINIMUM_THRESHOLD_FOR_SPECIFIC_INDICATORS")

import org.apache.spark.sql.functions._

// Join percentage data with threshold values
val joined = percentageDf
  .join(thresholdsDf, percentageDf("pub_count") === thresholdsDf("threshold"), "inner")
  .join(exceptionsDf, Seq("indicator"), "left") // join on 'indicator'

// Filter with COALESCE condition
val possibleThresholds = joined
  .filter(col("pub_count") > coalesce(col("exceptions.pub_count"), lit(0)))
  .select("facet", "indicator", "pub_count", "excess_pc")

possibleThresholds.write
  .format("delta")
  .mode("overwrite")
  .saveAsTable("possible_thresholds")

```


---

✅  Step-4: table thresholds 


```scala
val possibleThresholdsDf = spark.table("possible_thresholds")
val minInclusionDf = spark.table("MINIMUM_INCLUSION_PERCENTAGE")

import org.apache.spark.sql.expressions.Window
import org.apache.spark.sql.functions._

// Join possible_thresholds with MINIMUM_INCLUSION_PERCENTAGE
val joinedDf = possibleThresholdsDf
  .join(minInclusionDf, Seq("facet", "indicator"))

// Add rank per (facet, indicator) by descending pub_count
val windowSpec = Window.partitionBy("facet", "indicator").orderBy(col("pub_count").desc)

val withRankDf = joinedDf
  .withColumn("rank", rank().over(windowSpec))

// Filter: excess_pc > percentage OR rank = 1
val filteredDf = withRankDf
  .filter(col("excess_pc") > col("percentage") || col("rank") === 1)

// Group and take max pub_count as threshold
val thresholdsDf = filteredDf
  .groupBy("facet", "indicator")
  .agg(max("pub_count").alias("threshold"))

thresholdsDf.write
  .format("delta")
  .mode("overwrite")
  .saveAsTable("thresholds")

```


---


### 2.    Societal Impact - Rankings  - Size-dependent indicators 



✅  Step-1: table percentage_above_threshold_by_pub_count_with_threshold  


```scala
val institutionCountDf = spark.table("institution_count_by_pub_count")
val thresholdsDf = spark.table("thresholds")

import org.apache.spark.sql.expressions.Window
import org.apache.spark.sql.functions._

// Join with threshold
val joinedDf = institutionCountDf
  .join(thresholdsDf, Seq("facet", "indicator")) // join on facet + indicator
  .filter(col("pub_count") >= col("threshold"))

// Define windows
val cumSumWindow = Window.partitionBy("facet", "indicator").orderBy(col("pub_count").desc)
val totalSumWindow = Window.partitionBy("facet", "indicator")

// Compute excess_pc
val resultDf = joinedDf
  .withColumn("cum_sum", sum("institution_count").over(cumSumWindow))
  .withColumn("total_sum", sum("institution_count").over(totalSumWindow))
  .withColumn("excess_pc", (col("cum_sum") * 100) / col("total_sum"))
  .select("facet", "indicator", "pub_count", "excess_pc")

resultDf.write
  .format("delta")
  .mode("overwrite")
  .saveAsTable("percentage_above_threshold_by_pub_count_with_threshold")


```


---



✅  Step-2: table min_pub_count_per_quantile 


```scala

val pctAboveThresholdDf = spark.table("percentage_above_threshold_by_pub_count_with_threshold")
val quantilesDf = spark.table("QUANTILES") // assuming it has a column named "quantile"

import org.apache.spark.sql.functions._

// CROSS JOIN: select all combinations
val crossJoinedDf = pctAboveThresholdDf.crossJoin(quantilesDf)

// Filter: excess_pc >= quantile
val filteredDf = crossJoinedDf.filter(col("excess_pc") >= col("quantile"))

// Group by facet, indicator, quantile and get min(pub_count)
val resultDf = filteredDf
  .groupBy("facet", "indicator", "quantile")
  .agg(min("pub_count").alias("min_pub_count"))

resultDf.write
  .format("delta")
  .mode("overwrite")
  .saveAsTable("min_pub_count_per_quantile")

```

---



### 3.  Quantiles 


✅ Assumptions:

You have the following tables:
- 	df: main dataset
- 	thresholds: with columns facet, indicator, threshold
- 	min_pub_count_per_quantile: with columns facet, indicator, quantile, min_pub_count


✅ Step-by-step Spark Scala Code


```scala
import org.apache.spark.sql.functions._
import org.apache.spark.sql.expressions.Window

// Step 1: Aggregate counts per (facet, indicator, organization)
val aggregated = df
  .groupBy("facet", "indicator", "organization")
  .agg(
    sum(when(col("indicator") === "LG1.1", col("cited_nonacad"))).alias("LG1.1_count"),
    sum(when(col("indicator") === "LG2.1", col("cited_pat"))).alias("LG2.1_count"),
    sum(when(col("indicator") === "LD 1.1", col("cnt_isi_loc"))).alias("LD1.1_count"),
    sum(when(col("indicator") === "LD 2.1", col("nonacad"))).alias("LD2.1_count")
  )

// Step 2: Define dependency mapping
val dependencyMap = Map(
  "LD 1.1" -> Seq("LD 1.1"),
  "LD 2.1" -> Seq("LD 2.1", "LD 1.1"),
  "LG1.1"  -> Seq("LG1.1", "LD 1.1"),
  "LG2.1"  -> Seq("LG2.1", "LD 1.1")
)

// Explode dependencyMap to get a long format dependency DataFrame
val dependencyDF = dependencyMap.toSeq
  .flatMap { case (indicator, dependencies) => dependencies.map(dep => (indicator, dep)) }
  .toDF("current_indicator", "required_indicator")

// Step 2: Join with thresholds to check required thresholds
val thresholdsWithDeps = dependencyDF
  .join(thresholds, dependencyDF("required_indicator") === thresholds("indicator"))
  .select("current_indicator", "facet", "required_indicator", "threshold")

// Melt the aggregated counts to long format
val countsLong = aggregated
  .selectExpr("facet", "indicator as current_indicator", "organization",
    "stack(4, 'LG1.1', LG1.1_count, 'LG2.1', LG2.1_count, 'LD1.1', LD1.1_count, 'LD2.1', LD2.1_count) as (required_indicator, count_value)"
  )

// Join thresholds with counts to validate thresholds
val validated = countsLong
  .join(thresholdsWithDeps,
    countsLong("facet") === thresholdsWithDeps("facet") &&
    countsLong("current_indicator") === thresholdsWithDeps("current_indicator") &&
    countsLong("required_indicator") === thresholdsWithDeps("required_indicator")
  )
  .withColumn("is_valid", col("count_value") > col("threshold"))

// Count how many required indicators passed per (facet, indicator, org)
val passedCounts = validated
  .groupBy("facet", "current_indicator", "organization")
  .agg(
    count(when(col("is_valid"), true)).alias("valid_count"),
    count("*").alias("total_required")
  )
  .filter(col("valid_count") === col("total_required"))

// Step 3: Join with min_pub_count_per_quantile and assign quantile
val quantileJoin = aggregated
  .withColumnRenamed("indicator", "current_indicator")
  .join(passedCounts, Seq("facet", "current_indicator", "organization"))
  .join(min_pub_count_per_quantile, 
    aggregated("facet") === min_pub_count_per_quantile("facet") &&
    aggregated("indicator") === min_pub_count_per_quantile("indicator"),
    "inner"
  )
  .withColumn("relevant_count",
    when(col("current_indicator") === "LG1.1", col("LG1.1_count"))
      .when(col("current_indicator") === "LG2.1", col("LG2.1_count"))
      .when(col("current_indicator") === "LD 1.1", col("LD1.1_count"))
      .when(col("current_indicator") === "LD 2.1", col("LD2.1_count"))
  )
  .filter(col("relevant_count") >= col("min_pub_count"))

// Use window to get highest quantile
val w = Window.partitionBy("facet", "current_indicator", "organization").orderBy(col("min_pub_count").desc)

val finalWithQuantile = quantileJoin
  .withColumn("rank", row_number().over(w))
  .filter(col("rank") === 1)
  .select("facet", "current_indicator", "organization", "quantile")

finalWithQuantile.show(false)

```


✅ Output

You will get a DataFrame of qualified (facet, indicator, organization) rows with the highest quantile that the relevant count meets the minimum threshold for, based on dependencies and indicator-specific logic.


---

Optimized Version

```scala

import org.apache.spark.sql.functions._
import org.apache.spark.sql.expressions.Window

// Load base table with relevant years
val df = spark.table("arga_analytics_data_dev.sandbox.wos_5y_exploded")
  .filter($"publication_year".between(2020, 2024))

// Step 1: Aggregate counts per (facet, indicator, organization)
val indicatorsCountDf = df
  .groupBy("facet", "indicator", "organization")
  .agg(
    sum(
      when($"indicator" === "LG1_1", $"cited_nonacad")
        .when($"indicator" === "LG2_1", $"cited_pat")
        .when($"indicator" === "LD1_1", $"cnt_isi_loc")
        .when($"indicator" === "LD2_1", $"nonacad")
        .otherwise(lit(0))
    ).alias("metric_count")
  )

// Step 2: Join with thresholds and compute valid flag
val dfWithValidFlags = indicatorsCountDf
  .join(
    spark.table("arga_analytics_data_dev.sandbox.thresholds"),
    Seq("facet", "indicator"),
    "left"
  )
  .withColumn("valid", $"metric_count" >= $"threshold")

// Step 3: Pivot valid flags for dependency logic
val validFlagsPivotDf = dfWithValidFlags
  .select("facet", "indicator", "organization", "valid")
  .groupBy("facet", "organization")
  .pivot("indicator")
  .agg(first("valid"))

// Step 4: Join back and apply dependency rules
val enrichedDf = dfWithValidFlags
  .join(validFlagsPivotDf, Seq("facet", "organization"), "left")
  .withColumn(
    "quantile_valid",
    when($"indicator" === "LD1_1", $"LD1_1")
      .when($"indicator" === "LD2_1", $"LD1_1" && $"LD2_1")
      .when($"indicator" === "LG1_1", $"LD1_1" && $"LG1_1")
      .when($"indicator" === "LG2_1", $"LD1_1" && $"LG2_1")
      .otherwise(lit(null))
  )
  .withColumn("quantile_valid", col("quantile_valid").cast("int"))

// Step 5: Join with quantile thresholds
val minPubCountPerQuantileDf = spark.table("arga_analytics_data_dev.sandbox.min_pub_count_per_quantile")

val joinedDf = enrichedDf
  .join(minPubCountPerQuantileDf, Seq("facet", "indicator"), "left")
  .filter($"metric_count" >= $"min_pub_count")

// Step 6: Use window function to find best quantile
val quantileWindow = Window.partitionBy("facet", "indicator", "organization")
  .orderBy(col("min_pub_count").desc)

val finalQuantileDf = joinedDf
  .withColumn("rn", row_number().over(quantileWindow))
  .filter($"rn" === 1)
  .select(
    $"facet",
    $"indicator",
    $"organization",
    $"metric_count",
    $"threshold",
    $"min_pub_count",
    $"valid",
    $"quantile_valid",
    when($"quantile_valid" === 1, $"quantile").otherwise(lit(null)).alias("quantile")
  )

````






---

## A.6 SQL Implementation




### 1.  Thresholds  - Lower threshold algorithm 



✅  Step-1: table institution_count_by_pub_count 

```sql
CREATE TABLE institution_count_by_pub_count AS
SELECT
  facet,
  indicator,
  pub_count,
  COUNT(DISTINCT institutions) AS institution_count
FROM
  data
GROUP BY
  facet,
  indicator,
  pub_count;
```

---

✅  Step-2: table percentage_above_threshold_by_pub_count 

```sql
CREATE TABLE percentage_above_threshold_by_pub_count AS
SELECT
  facet,
  indicator,
  pub_count,
  100 * SUM(institution_count) OVER (
    PARTITION BY facet, indicator
    ORDER BY pub_count DESC
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) / SUM(institution_count) OVER (PARTITION BY facet, indicator) AS excess_pc
FROM
  institution_count_by_pub_count;
```



---

✅  Step-3: table institution_count_by_pub_count 

```sql
CREATE TABLE possible_thresholds AS
SELECT 
  sums.facet,
  sums.indicator,
  sums.pub_count,
  sums.excess_pc
FROM 
  percentage_above_threshold_by_pub_count AS sums
  INNER JOIN SET_OF_POSSIBLE_THRESHOLDS AS thresholds
    ON sums.pub_count = thresholds.threshold
  LEFT JOIN MINIMUM_THRESHOLD_FOR_SPECIFIC_INDICATORS AS exceptions
    ON sums.indicator = exceptions.indicator
WHERE 
  sums.pub_count > COALESCE(exceptions.pub_count, 0);
```





---

✅  Step-4: table thresholds 

```sql
CREATE TABLE thresholds AS
SELECT 
  facet,
  indicator,
  MAX(pub_count) AS threshold
FROM (
  SELECT 
    pt.facet,
    pt.indicator,
    pt.pub_count,
    pt.excess_pc,
    mip.percentage,
    RANK() OVER (PARTITION BY pt.facet, pt.indicator ORDER BY pt.pub_count) AS rnk
  FROM 
    possible_thresholds pt
    JOIN MINIMUM_INCLUSION_PERCENTAGE mip
      ON pt.indicator = mip.indicator
) sub
WHERE 
  excess_pc > percentage OR rnk = 1
GROUP BY 
  facet, indicator;
```




---


### 2.    Societal Impact - Rankings  - Size-dependent indicators 


✅  Step-1: table percentage_above_threshold_by_pub_count_with_threshold  

```sql
CREATE TABLE percentage_above_threshold_by_pub_count_with_threshold AS
SELECT
  counts.facet,
  counts.indicator,
  counts.pub_count,
  SUM(counts.institution_count) OVER (PARTITION BY counts.facet, counts.indicator ORDER BY counts.pub_count) AS cum_sum,
  SUM(counts.institution_count) OVER (PARTITION BY counts.facet, counts.indicator) AS total_sum,
  100.0 * SUM(counts.institution_count) OVER (PARTITION BY counts.facet, counts.indicator ORDER BY counts.pub_count) /
  SUM(counts.institution_count) OVER (PARTITION BY counts.facet, counts.indicator) AS excess_pc
FROM
   arga_analytics_data_dev.sandbox.institution_count_by_pub_count counts
INNER JOIN
   arga_analytics_data_dev.sandbox.thresholds
  ON thresholds.facet = counts.facet
  AND thresholds.indicator = counts.indicator
WHERE
  counts.pub_count >= thresholds.threshold
ORDER BY
  counts.facet,
  counts.indicator,
  counts.pub_count;
```



----



✅  Step-2: table min_pub_count_per_quantile 

```sql
CREATE TABLE min_pub_count_per_quantile AS
SELECT
  facet,
  indicator,
  quantile,
  MIN(pub_count) AS min_pub_count
FROM
  percentage_above_threshold_by_pub_count_with_threshold
CROSS JOIN
  QUANTILES
WHERE
  excess_pc >= quantile
GROUP BY
  facet,
  indicator,
  quantile;
```


---



### 3.  Quantiles 







