

### ES Metric  Aggregations 


#### 1. Percentage Aggregation 
 
 ```json
"THE_90_PERCENTILE_DOCS": { 
  "percentage": { 
    "field": "wos.percentile_esi", 
    "thresholds": [ 
      10, 90 
    ], 
    "comparator": "lte" 
  } 
} 
``` 
 
```java
new ElasticPercentageAggregation() 
.field("wos.percentile_esi") 
 .name("THE_90_PERCENTILE_DOCS") 
.missing(2.2).comparator("gt") 
.thresholds(Arrays.asList(1.0, 2.0)); 
```


 
#### 2. Quartile Aggregation 
 
 ```json 
"JOURNAL_QUARTILE": { 
  "ca_quartile": { 
    "field": "docs_key_latest", 
    "indicator": "quartile", 
    "metrics": "quartile", 
    "includes": [], 
    "default_quartile": 0 
  } 
}   
``` 

```java
new ElasticQuartileAggregation() 
        .name("JOURNAL_QUARTILE") 
        .field("docs_key_latest") 
        .metrics("sum") 
        .indicator("q1") 
        .includes(Arrays.asList(1L, 2L, 3L)); 
``` 

 
#### 4. Ratio Aggregation 
 
 ```json 
"PERCENTILE_QA1": { 
  "ca_ratio": { 
    "missing_num": 0, 
    "missing_denom": 0, 
    "field_num": "docs_q1", 
    "field_denom": "docs_jif", 
    "metrics_num": "Sum", 
    "metrics_denom": "Sum" 
  } 
} 
``` 
  
```java
new ElasticRatioAggregation() 
        .name("PERCENTILE_QA1") 
        .fieldNum("docs_q1") 
        .fieldDenom("docs_jif") 
        .metricsNum("sum") 
        .metricsDenom("sum"); 

``` 


 
#### 4. Encoded Metric Aggregation 
 
```json
"JCI_RANK": { 
    "ca_encoded_metric": { 
        "field": "jci_rank_latest", 
        "scale": 1.0, 
        "metrics": "min", 
        "includes": [ 687, 1711 ], 
        "best_value": "min" 
    } 
}   

```  
  
```java
new ElasticEncodedMetricAggregation() 
        .name("JCI_RANK") 
        .field("jci_rank_latest") 
        .metrics("value") 
        .bestValue("max") 
        .scale(0.01) 
        .includes(Arrays.asList(1L, 2L, 3L)); 
``` 



#### 5. Range Aggregation – Impact Profile  

 ```json
  "impact_profile": { 
    "range": { 
      "field": "wos.nci_wos", 
      "ranges": [ 
        { 
          "to": 0.125 
        }, 
        { 
          "from": 0.125, 
          "to": 0.25 
        }, 
        { 
          "from": 0.25, 
          "to": 0.5 
        }, 
        { 
          "from": 0.5, 
          "to": 1 
        }, 
        { 
          "from": 1 
        } 
      ] 
    } 
  } 
```   



####  6. Meta Aggregation 
 
 ```json 
"INSTITUTION_FULL_NAME": { 
  "scripted_metric": { 
    "init_script": { 
      "source": "state.data='';", 
      "lang": "painless" 
    }, 
    "map_script": { 
      "source": "if(state.data=='' && doc['organizations.institution_full_name'].size()>0 && doc['organizations.institution_full_name'].value!=null) state.data=doc['organizations.institution_full_name'].value;", 
      "lang": "painless" 
    }, 
    "combine_script": { 
      "source": "return state.data;", 
      "lang": "painless" 
    }, 
    "reduce_script": { 
      "source": "for(s in states){if(s!='') return s;} return ''", 
      "lang": "painless" 
    } 
  } 
} 
``` 
  
```java
new ElasticMetaAggregation() 
      .name("INSTITUTION_FULL_NAME") 
    .field("organizations.institution_full_name") 
    .metrics("term"))); 
 ``` 


#### 7. Filters Aggregation 
 
```json
"group_items": { 
    "filters": { 
      "filters": { 
        "grp_1": { 
          "terms": { 
            "journal_key": [ "2665947031265781604", 
              "-7862999993925918391" ] 
          } 
        }, 
        "grp_2": { 
          "terms": { 
        "journal_key:[ "967606376204084614",               "-4393215734432443598" ] 
          } 
        } 
      } 
    }, 
    "aggs": { 
      "tot_cites": { 
        "sum": { 
          "field": "wos.tot_cites" 
        } 
      } 
    } 
  } 
```  
 
#### 8. SearchEngine<?> engine = new HttpElasticSearchEngine(); 
 
 
```java
new ElasticFiltersAggregation() 
        .name("filters_aggs") 
        .filter("errors", engine.termQuery().term("error") 
                .fields(SearchField.fields("message") )) 
        .filter("warnings", engine.termQuery().term("warning") 
                .fields(SearchField.fields("message") )) 
        .aggregation( engine.distinctAggregation().field("message").name("count")) ); 
 ``` 


 
#### 9. Custom** Filter Term Aggregation 
 
```json
 "ca_filter_terms": { 
    "field": "organizations.institution_key", 
    "size": 5, 
    "shard_size": 500, 
    "min_doc_count": 1, 
    "shard_min_doc_count": 0, 
    "show_term_doc_count_error": false, 
    "filter_shard_level_bucket": false, 
    "pinned_items_keys": [ 
      "40270007288854", 
      "40270007290261" 
    ], 
    "group_items": [ 
      { 
        "key": "123", 
        "sort_value": 35002, 
        "doc_count": 12, 
        "threshold_field": "TOT_CITES", 
        "threshold": 33, 
        "pinned": false 
      }    ], 
    "order": [ 
      { "TOT_CITES": "desc" }, 
      { "_key": "asc" } 
    ], 
    "thresholds": [ 
      { 
        "_count": [ 0, 4327 ] 
      }, 
      { 
        "TOT_CITES": [  0, 100761 ] 
      } 
    ], 
    "exclude": [] 
  } 
 ``` 
 
  
```java
new ElasticFilterTermsAggregation() 
      .name("filterAgg_name") 
      .field("filterTermsField") 
      .groupItem("123", 2.0, 3, "TOT_CITES", 4, false) 
      .threshold("_count", 0, 10) 
      .threshold("max_value", 1, 100) 
      .pinnedItemsKeys(pinnedItemsKeys)) ); 
``` 


####  10. H-index Aggregation 
 
  
```json
"H_INDEX": { 
  "h-index": { 
    "field": "wos.tot_cites" 
  } 
}      

``` 

```java

new ElasticHIndexAggregation() 
        .field("wos.tot_cites") 
        .name("H_INDEX") 
        .missing(2.2))); 

``` 

####  11. H-index Aggregation 
 
  
```json
"H_INDEX": { 
  "h-index": { 
    "field": "wos.tot_cites" 
  } 
}      
 
``` 

  
```java
new ElasticHIndexAggregation() 
        .field("wos.tot_cites") 
        .name("H_INDEX") 
        .missing(2.2))); 

``` 
   
 
####  12. Bucket Selector Aggregation   
  
```json
"post_filter": { 
  "bucket_selector": { 
    "buckets_path": { 
      "timesCited": "TOT_CITES_sum", 
      "wosCount": "_count" 
    }, 
    "script": { 
      "inline": "params.timesCited > 0 && params.timesCited <= 709517076 &&  params.wosCount < 54588455", 
      "lang": "painless" 
    } 
  } 
} 
``` 

     
```java 
new ElasticBucketSelectorAggregation() 
 .name("bucketSelectorAgg_name") 
.lang("painless") 
.script("script") 
.bucketsPath(Collections.singletonMap("bucket", "path")); 
``` 

#### 13. Filter Metric Aggregation – Author Position  
 
  
```json
"aggregations": { 
    "AUTHOR_POS": { 
      "nested": { 
        "path": "people" 
      }, 
      "aggregations": { 
        "filter": { 
          "filter": { 
            "bool": { 
              "must": [ 
                { 
                  "terms": { 
                    "people.author_full_name": [ 
                      "Wang, Wei" 
                    ] 
                  } 
                } 
              ] 
            } 
          }, 
          "aggregations": { 
            "FIRST_ATHOR": { 
              "sum": { 
                "field": "people.is_first" 
              } 
            } 
          } 
        } 
      } 
    } 
  } 
``` 


 
#### 14. Regular Aggregation Structure 
 
    
```json
"aggregations": { 
    "topn_terms": { 
      "ca_filter_terms": { 
        "field": "daisng_author_key", 
        "size": 10, 
        "shard_size": 10000 
      }, 
      "aggregations": { 
        "TOT_CITES": { 
          "sum": { 
            "field": "wos.tot_cites" 
          } 
        } 
      } 
    } 
  } 
 ``` 



 #### 15. Filter Term Aggregation – Entity filter    
 
  
```json
{ 
  "aggregations": { 
    "organizations": { 
      "nested": { 
        "path": "organizations" 
      }, 
      "aggregations": { 
        "filter": { 
          "filter": { 
            "exists": { 
              "field": "organizations.institution_association" 
            } 
          }, 
          "aggregations": { 
            "row": { 
              "ca_filter_terms": { 
                "field": "organizations.institution_full_name", 
                "size": 2000, 
                "shard_size": 2000, 
                "order": [ 
                  { 
                    "_count": "desc" 
                  } 
                ], 
                "thresholds": [ 
                { 
                "_count": [0, 4327 ] 
                }, 
                { 
                "TOT_CITES": [0,100761 ] 
                } 
                ], 
 
                "collect_mode": "breadth_first" 
              }, 
              "aggregations": { 
                "reverse_nested": {}, 
                "aggregations": { 
                  "TOT_CITES": { 
                    "sum": { 
                      "field": "wos.tot_cites" 
                    } 
                  } 
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
