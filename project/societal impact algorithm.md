


### 0. Calculate Inidcator Count


#### 0.1 LD1.1 Contribution to facet

Facets: All

```sql
select 
  institution, 
  facet, 
  publication_year, 
  count(distinct ut) 
from 
  data 
group by 
  institution, 
  facet, 
  publication_year
```

#### 0.2 LD2.1 Non-academic collaboration

Facets: All

Note: this is based on the separate work being done to identify which papers are non-academic

```sql
select 
  institution, 
  facet, 
  publication_year, 
  count(distinct ut) 
from 
  data 
where 
  paper is non_academic 
group by 
  institution, 
  facet, 
  publication_year

```


#### 0.3 LG1.1 Papers consistently cited by non-academics

Facets: All

Note: this is based on the separate work being done to identify which papers are non-academic


```sql
create table non_academic_citations asselect cited_ut, 
count(distinct citing_ut) as non_academic_citations 
from 
  citations 
where 
  citing_ut is non_academic 
select 
  institution, 
  facet, 
  publication_year, 
  count(distinct data.ut) 
from 
  data 
  join non_academic_citations on data.ut = non_academic_citations.cited_ut 
where 
  non_academic_citations >= 2 
group by 
  institution, 
  facet, 
  publication_year

```

#### 0.4  LG2.1 Papers cited by patents

Facets: Environmental, Medical, Technological


Note: I’m assuming “patent_citations” provides the number of patent citations (as patent_citation_count) for each ut.

```sql
select 
  institution, 
  facet, 
  publication_year, 
  count(distinct ut) 
from 
  data 
  inner join patent_citations on data.ut = patent_citations.ut 
where 
  patent_citation_count > 0 
group by 
  institution, 
  facet, 
  publication_year

```

#### 0.5 LD3.1 Patent applications

Facets: Environmental, Medical, Technological (to be confirmed)


```sql
select 
  institution, 
  facet, 
  year(priority_date_earliest), 
  count(distinct patent_ut) 
from 
  patent_data 
group by 
  institution, 
  facet, 
  year(priority_date_earliest)


```

#### 0.6  LG2.2 Patents granted

Facets: Environmental, Medical, Technological (to be confirmed)


```sql
select 
  institution, 
  facet, 
  year(priority_date_earliest), 
  count(distinct patent_ut) 
from 
  patent_data 
where 
  patent_granted 
group by 
  institution, 
  facet, 
  year(priority_date_earliest)

```

---

### 1. Calculate Threshold


#### 1.1 institution_count_by_pub_count

```sql
create table institution_count_by_pub_count as
select facet, 
indicator, 
pub_count, 
count(distinct institutions) as institution_count 
from 
  data 
group by 
  facet, 
  indicator, 
  pub_count 
  ```
  

  #### 1.2 percentage_above_threshold_by_pub_count

  ```sql
  create table percentage_above_threshold_by_pub_count as
  select facet, 
  indicator, 
  pub_count, 
  100 * (
    cum_sum(institution_count) over (facet, indicator)
  ) / sum(institution_count) as excess_pc 
from 
  institution_count_by_pub_count 
group by 
  facet, 
  indicator, 
  pub_count 
order by 
  pub_count desc 
  
  ```
  
  #### 1.3  possible_thresholds

  ```sql
  create table possible_thresholds asselect facet, 
  indicator, 
  pub_count, 
  excess_pc 
from 
  percentage_above_threshold_by_pub_count sums 
  inner join SET_OF_POSSIBLE_THRESHOLDS thresholds on sums.pub_count = thresholds.threshold 
  left join MINIMUM_THRESHOLD_FOR_SPECIFIC_INDICATORS exceptions on sums.indicator = exceptions.indicator 
where 
  sums.pub_count > coalesce(exceptions.pub_count, 0)
```


#### 1.4 thresholds

```sql
create table thresholds asselect facet, 
indicator, 
max(pub_count) as threshold 
from 
  possible_thresholds 
  join MINIMUM_INCLUSION_PERCENTAGE 
where 
  excess_pc > MINIMUM_INCLUSION_PERCENTAGE.percentage 
  or rank() over (facet, indicator) 
order by 
  (pub_count) = 1 
group by 
  facet, 
  indicator
```

---

### 2. Calculate Size Dependent Ranking


#### 2.1 percentage_above_threshold_by_pub_count_with_threshold

```sql
create table percentage_above_threshold_by_pub_count_with_threshold as
select facet, 
indicator, 
pub_count, 
100 * (
  cum_sum(institution_count) over (facet, indicator)
) / sum(institution_count) as excess_pc 
from 
  institution_count_by_pub_count counts 
  inner join thresholds on thresholds.facet = counts.facet 
  and thresholds.indicator = counts.indicator 
where 
  pub_count >= threshold 
group by 
  facet, 
  indicator, 
  pub_count 
order by 
  pub_count 
  ```
  
  #### 2.2  min_pub_count_per_quantile
  
  ```sql
  create table min_pub_count_per_quantile
  select facet, 
  indicator, 
  quantile, 
  min(pub_count) as min_pub_count 
from 
  percentage_above_threshold_by_pub_count_with_threshold cross 
  join QUANTILES 
where 
  excess_pc >= quantile 
group by 
  facet, 
  indicator, 
  quantile
```


---

### 3. Calculate Size Normalized Ranking


#### 3.1 size_normalized_indicators

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


#### 3.2 institution_count_by_ratio

```sql
-- Pulling in similar code from slide 18 for code on slide 14 to work with:
create table institution_count_by_ratio as
select facet, numerator, denominator, year_range, ratio,
        count(distinct institutions) as institution_count
    from size_normalized_indicators
  group by facet, numerator, denominator, year_range, ratio;
```

#### 3.3 percentage_above_threshold_by_ratio_with_threshold

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


#### 3.4 min_ratio_per_quantile

```sql
create table min_ratio_per_quantile
select facet, numerator, denominator, year_range, quantile, min(ratio) as min_ratio
    from percentage_above_threshold_by_ratio_with_threshold
        cross join QUANTILES
    where excess_pc >= quantile
    group by facet, numerator, denominator, year_range, quantile
```

#### 3.5 threshold_filtered_data

```sql
-- This assumes data is pre-aggregated by year range and has
--   facet, indicator, year_range, institution and pub_count columns
-- I'm also assuming that's been included in the thresholds table
-- See comment below

create table threshold_filtered_data as
select facet, indicator, year_range, institution, pub_count
    from data
    inner join thresholds
        on data.facet = thresholds.facet
        and data.indicator = thresholds.indicator
        and data.year_range = thresholds.year_range
  where data.pub_count > thresholds.threshold
```


#### 3.6 min_pub_count_per_quantile

```sql
create table min_pub_count_per_quantile
select facet, indicator, quantile, min(pub_count) as min_pub_count
    from percentage_above_threshold_by_pub_count_with_threshold		
        cross join QUANTILES
    where excess_pc >= quantile	
    group by facet, indicator, quantile
```
