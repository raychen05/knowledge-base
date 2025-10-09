
## Expert Finder - Research Topics (Nested Field )


--- 
### 1. Match Query 


To search multiple terms in the name field of a nested field (research_topics) and rank researchers by cumulative score of matching topics, you need to:


✅ 1. Example Mapping 

```json
{
  "mappings": {
    "properties": {
      "research_topics": {
        "type": "nested",
        "properties": {
          "id": { "type": "keyword" },
          "parent_id": { "type": "keyword" },
          "score": { "type": "integer" }
        }
      }
    }
  }
}
```


✅ 2. Query: Match on Nested name, Use score for Relevance

You want to:
-	Search for user terms in research_topics.name
-	For each matching topic, sum up score
-	Rank researchers by that sum

✅ Sample Query (multi-term input like ["Nanofluid", "Ferrites"]):


```json
{
  "query": {
    "nested": {
      "path": "research_topics",
      "query": {
        "bool": {
          "should": [
            { "match": { "research_topics.name": "Nanofluid" } },
            { "match": { "research_topics.name": "Ferrites" } }
          ]
        }
      },
      "score_mode": "sum"
    }
  }
}
```
✅ 3. Sorting by Relevance (Score)

The score_mode: sum inside the nested query sums the topic scores for matched nested objects, and Elasticsearch automatically uses that as the main _score for sorting researchers.

To explicitly sort:

```json
"sort": [
  { "_score": { "order": "desc" } }
]
```

✅ 4. Optional: Fine-tune with function_score

If you want to customize score calculations (e.g., boost certain topics or apply weights), use function_score:

```json
{
  "query": {
    "nested": {
      "path": "research_topics",
      "score_mode": "sum",
      "query": {
        "function_score": {
          "query": {
            "bool": {
              "should": [
                { "match": { "research_topics.name": "Nanofluid" } },
                { "match": { "research_topics.name": "Ferrites" } }
              ]
            }
          },
          "script_score": {
            "script": {
              "source": "doc['research_topics.score'].value"
            }
          }
        }
      }
    }
  }
}
```

---

###  2.  Prefix or Term Query 

Great question. When you search using prefix or term on fields like id or parent_id (typically treated as keywords), Elasticsearch does not compute a relevance _score in the traditional way like with full-text fields (e.g., match on text). These queries are filtering by default, not scoring.

But — you can still assign relevance manually using a custom scoring approach like script_score, and then sort by that.

---

✅ GOAL

You want to:
-	Search research_topics.id or research_topics.parent_id using term or prefix
-	Sum their associated score fields
-	Rank the parent document (e.g., a researcher) by that summed score

---

✅ 1. Example Mapping 

```json
{
  "mappings": {
    "properties": {
      "research_topics": {
        "type": "nested",
        "properties": {
          "id": { "type": "keyword" },
          "parent_id": { "type": "keyword" },
          "score": { "type": "integer" }
        }
      }
    }
  }
}
```

✅ 2. Query with term or prefix, and Custom Score

Use a nested + function_score + script_score to emulate relevance.

🎯 Match id or parent_id with term or prefix:

```json
{
  "size": 100,
  "from": 0,
  "query": {
    "nested": {
      "path": "research_topics",
      "score_mode": "sum", 
      "query": {
        "function_score": {
          "query": {
            "bool": {
              "should": [
                { "term": { "research_topics.id": "7.70.219" } },
                {
                  "prefix": {
                    "research_topics.id": "7.70"
                  }
                }
              ]
            }
          },
          "script_score": {
            "script": {
              "source": "doc['research_topics.score'].value"
            }
          }
        }
      }
    }
  },
  "sort": [
    { "_score": "desc" }
  ],
  "_source": {
    "includes": [
      "pguid"
    ]
  }
}

```

✅ 3. What Happens Here

-	term / prefix: Matches id or parent_id
-	script_score: Uses each matching nested object’s score field
-	score_mode: sum: Adds up the scores for all matching research_topics
-	sort by _score: Ranks researchers by total matched topic scores

⸻

✅ Notes

| Feature                        | Term                  | Prefix                | Match                |
|---------------------------------|-----------------------|-----------------------|----------------------|
| Uses analyzer                  | ✔                     | ✔                     | ✖                    |
| Good for ID-style fields       | ✔                     | ✔                     | ✖                    |
| Computes text relevance        | ✔                     | ✔                     | ✖                    |
| Can customize score            | ✔ (with script)       | ✔ (with script)       | ✔                    |



✅ Summary

To search id or parent_id fields (using term or prefix) and rank by relevance:

-	Use nested + function_score + script_score
-	Manually compute relevance using the score field
-	Aggregate using score_mode: sum
-	Sort by _score


---

### 3. Aggregaion

Great follow-up. Yes — using aggregations to sum score for matched id or parent_id values is a very valid alternative and in many use cases, it can be more efficient and scalable than using nested + function_score + script_score, especially when:

-	You don’t need full document ranking in the same query response
-	You are preparing a ranked list, e.g., top N researchers by topic relevance
-	You’re okay doing two steps: aggregation first → fetch full docs later (optional)


🔁 Comparison Summary

| Feature                               | nested + function_score + script_score | nested aggregation + sum(score) |
|---------------------------------------|---------------------------------------|---------------------------------|
| Good for full document ranking in one step | ✔                                     | ✖ (aggregation only)            |
| Relevance _score returned            | ✔                                     | ✖                               |
| Simpler post-processing              | ✔                                     | ✖                               |
| Needs doc lookup or join             | ✖                                     | ✔                               |
| Efficient for large-scale queries    | ✖ (costly scoring)                   | ✔ (more scalable)               |
| Query complexity                     | Higher                                | Lower                           |
| Supports real-time scoring           | ✔                                     | ✖ (aggregated summaries only)   |



✅ Example: Aggregate Score for Matching IDs

```json
{
  "query": {
    "nested": {
      "path": "research_topics",
      "query": {
        "bool": {
          "should": [
            { "term": { "research_topics.id": "7.70.219" } },
            {
              "prefix": {
                "research_topics.parent_id": "7.70"
              }
            }
          ]
        }
      }
    }
  },
  "aggs": {
    "top_researchers": {
      "terms": {
        "field": "_id",
        "size": 10,
        "order": { "total_score": "desc" }
      },
      "aggs": {
        "matched_topics": {
          "nested": {
            "path": "research_topics"
          },
          "aggs": {
            "matched_score": {
              "filter": {
                "bool": {
                  "should": [
                    { "term": { "research_topics.id": "7.70.219" } },
                    { "prefix": { "research_topics.parent_id": "7.70" } }
                  ]
                }
              },
              "aggs": {
                "total_score": {
                  "sum": { "field": "research_topics.score" }
                }
              }
            }
          }
        },
        "total_score": {
          "bucket_script": {
            "buckets_path": {
              "score": "matched_topics>matched_score>total_score"
            },
            "script": "params.score"
          }
        }
      }
    }
  }
}
```

🧠 Recommendation for 20M+ docs and 1000+ fields:

| Use case                            | Recommended                |
|-------------------------------------|---------------------------|
| Search + rank in one-shot (interactive UI) | nested + function_score (only if needed) |
| Batch processing, precompute ranking | ✔ Use aggregation         |
| High-frequency or massive-scale queries | ✔ Use aggregation         |
| Need rich scoring logic (e.g. multiple weights) | script_score (if unavoidable) |



✅ Best Practice

For large-scale and performance-critical pipelines:

-	Use aggregations to precompute relevance scores
-	Store scores in a cache index or materialized field
-	Use a simple term query + sort on that field later


---

###  3.  Comparison - function_score + script_score vs aggregation


🆚 Comparison: nested + function_score + script_score vs nested + aggregation


| Criteria                                  | nested + function_score + script_score | nested + aggregation (sum)             |
|-------------------------------------------|----------------------------------------|----------------------------------------|
| 🔧 Use case                               | Real-time search & relevance scoring   | Pre-ranking or batch scoring           |
| 🔩 Supports dynamic score sum per topic   | ✅ Yes                                  | ✅ Yes                                  |
| ⚡ Performance on large datasets (20M+)   | ❌ Slower (complex scoring)            | ✅ Better (scalable aggregation)        |
| 🎯 Granular control over scoring          | ✅ (via script)                         | ✅ (via aggregation filters)            |
| 🧠 Relevance _score supported             | ✅ Yes (directly affects doc ranking)  | ❌ No (you get bucketed sums, need separate fetch) |
| 🔁 Updates with new user queries          | Real-time                              | Real-time (just update filters)        |
| 🧑‍💻 Query structure                       | Complex (nested + script)              | Complex (nested + aggregation pipeline)|
| 📦 Output type                            | Documents sorted by _score             | Buckets sorted by sum(score)           |

---

✅ Option 1: nested + function_score + script_score

Best for: real-time user search & ranking in UIs.

Sample Query:
```json
{
  "query": {
    "function_score": {
      "query": {
        "nested": {
          "path": "research_topics",
          "query": {
            "bool": {
              "should": [
                { "term": { "research_topics.id": "7.70.219" } },
                { "prefix": { "research_topics.parent_id": "7.70" } }
              ]
            }
          },
          "score_mode": "sum"
        }
      },
      "script_score": {
        "script": {
          "source": """
            double sum = 0;
            for (topic in params['_source']['research_topics']) {
              if (params.ids.contains(topic.id) || topic.parent_id.startsWith('7.70')) {
                sum += topic.score;
              }
            }
            return sum;
          """,
          "params": {
            "ids": ["7.70.219"]
          }
        }
      },
      "boost_mode": "replace"
    }
  }
}
```

⚠️ This approach is CPU-intensive because it runs per-doc scripts and works on full nested arrays.

---

✅ Option 2: nested + aggregation (sum)

Best for: scalable, fast batch-style or backend search processing.

Sample Query:
```json

{
  "size": 0,
  "query": {
    "nested": {
      "path": "research_topics",
      "query": {
        "bool": {
          "should": [
            { "term": { "research_topics.id": "7.70.219" } },
            {
              "prefix": {
                "research_topics.parent_id": "7.70"
              }
            }
          ]
        }
      }
    }
  },
  "aggs": {
    "pguid_aggregation": {
      "ca_filter_terms": {
          "field": "pguid",
          "size": 200,
          "shard_size": 2000,
          "min_doc_count": 1,
          "shard_min_doc_count": 0,
          "show_term_doc_count_error": false,
          "filter_shard_level_bucket": false,
          "order": [
              {
                  "nested_research_topics>total_score": "desc"
              },
              {
                  "_key": "asc"
              }
          ],
          "collect_mode": "breadth_first",
          "pinned_items_keys": [ ]
      },
      "aggs": {
        "nested_research_topics": {
          "nested": {
            "path": "research_topics"  
          },
          "aggs": {
            "total_score": {
              "sum": {
                "field": "research_topics.score" 
              }
            }
          }
        }
      }
    }
  },
  "_source": false,
  "track_total_hits": 2147483647
}

```

🧠 Recommendation

| Goal                                                | Recommended Approach                          |
|-----------------------------------------------------|-----------------------------------------------|
| ✅ UI Search with relevance ranking per doc         | nested + function_score + script_score        |
| ✅ Precompute relevance or sort backend/batch ranking | nested aggregation + score sum              |
| ✅ Large scale: 20M+ docs with 1000+ fields         | ✅ Aggregation (faster, scalable)             |
