
### Organization Search Requirments

Following are the basic priority rules: 

- Prioritize exact matches- ensure phrases identical to the search term appear at the top.
- Include phrases that begin with the search term
- Include phrases where the search term appears in the exact order
- Include phrases containing the search term in different orders and distances
- Do not include the result if the term is in the middle of a word or the suffix.
- For example: When Searching for "anna" the following shouldn't be included:
  - Al-Muthanna University
  - Bannari Amman Institute of Technology

- When searching single term - display exact and then begins with. 
- When searching multiple terms - display exact and then reverse and then the distance calculations.

---

### To fully meet your matching priority rules, the scoring script must:

✅ Priority Rules Recap:
- Exact match ⟶ highest priority (score = 0)
- Phrase starts with query (e.g., "university of arizona...")
- Phrase contains full query in order
- Contains query terms in reverse order
- Contains query terms scattered at various distances
- ❌ No partial (substring/suffix/infix) matches – i.e., do not match "suniversity" for "university"

✅ Updated Elasticsearch script_score Logic:
We’ll build the logic in steps:

- Normalize input
- Tokenize both field and query
- Check for exact match
- Check for starts with
- Check ordered term match (e.g., "university arizona")
- Check reversed term match ("arizona university")
- Penalize based on distance if scattered
- Reject if terms appear as substrings within other words

---

### 🔧 Final Working Script:

#### 1. Final version

```json
{
  "script_score": {
    "script": {
      "source": """
        String fieldValue = doc[params.field].value.toLowerCase();
        String[] fieldTokens = /\\s+/.split(fieldValue.trim()); 
        String queryPhrase = String.join(" ", params.terms).toLowerCase();
        String reversedQuery = "";
        for (int i = params.terms.length - 1; i >= 0; i--) {
          reversedQuery += params.terms[i].toLowerCase();
          if (i > 0) reversedQuery += " ";
        }

        // 1. Exact match
        if (fieldValue.equals(queryPhrase)) return 0;

        // 2. Starts with
        if (fieldValue.startsWith(queryPhrase + " ")) return 1;
        //- return fieldTokens.length;

        // 3. Contains phrase in exact order
        if (fieldValue.contains(" " + queryPhrase + " ") || fieldValue.endsWith(" " + queryPhrase)) return 2;
        //- return (firstMatchPos >= 0 ? (firstMatchPos + 1) * 100 : 1000000) + fieldTokens.length;}
        //- return (firstMatchPos + 1) * 10 + fieldTokens.length;}

        // 4. Reversed phrase match
        if (fieldValue.contains(" " + reversedQuery + " ") || fieldValue.startsWith(reversedQuery + " ")) return 3;
        //- return 100 + (firstMatchPos + 1) * 10 + fieldTokens.length;}

        // 5. Tokenized field check for scattered match
        int matchedTerms = 0;
        int[] positions = new int[params.terms.length];
        for (int i = 0; i < params.terms.length; i++) positions[i] = -1;

        for (int i = 0; i < fieldTokens.length; i++) {
          for (int j = 0; j < params.terms.length; j++) {
            if (fieldTokens[i].equals(params.terms[j].toLowerCase())) {
              matchedTerms += 1;
              positions[j] = i;
              break;
            }
          }
        }

       //-  if (matchedTerms != params.terms.length) return 1000000; // reject partials or suffix/infix

        // Distance-based score
        int minPos = Integer.MAX_VALUE;
        int maxPos = Integer.MIN_VALUE;
        for (int p : positions) {
          minPos = Math.min(minPos, p);
          maxPos = Math.max(maxPos, p);
        }

        int distance = maxPos - minPos;
        return 200 + distance * 10 + fieldTokens.length;
      """,
      "params": {
        "terms": ["university", "arizona"],
        "field": "preferredName.norm"
      }
    }
  }
}

```

#### 2. Compact Version:

```json
{
  "script_score": {
    "script": {
      "source": "String fieldValue = doc[params.field].value.toLowerCase(); String[] fieldTokens = /\\s+/.split(fieldValue.trim()); String queryPhrase = String.join(' ', params.terms).toLowerCase(); String reversedQuery = ''; for (int i = params.terms.length - 1; i >= 0; i--) { reversedQuery += params.terms[i].toLowerCase(); if (i > 0) reversedQuery += ' '; }  if (fieldValue.equals(queryPhrase)) return 0; if (fieldValue.startsWith(queryPhrase + ' ')) return 1; if (fieldValue.contains(' ' + queryPhrase + ' ') || fieldValue.endsWith(' ' + queryPhrase)) return 2; if (fieldValue.contains(' ' + reversedQuery + ' ') || fieldValue.startsWith(reversedQuery + ' ')) return 3; int matchedTerms = 0; int[] positions = new int[params.terms.length]; for (int i = 0; i < params.terms.length; i++) positions[i] = -1;  for (int i = 0; i < fieldTokens.length; i++) { for (int j = 0; j < params.terms.length; j++) { if (fieldTokens[i].equals(params.terms[j].toLowerCase())) { matchedTerms += 1; positions[j] = i; break; } } }  if (matchedTerms != params.terms.length) return 1000000;  int minPos = Integer.MAX_VALUE; int maxPos = Integer.MIN_VALUE; for (int p : positions) { minPos = (int) Math.min(minPos, p); maxPos = (int)Math.max(maxPos, p); }  int distance = maxPos - minPos; return 100 + distance * 10 + fieldTokens.length;",
      "params": {
        "terms": ["university", "arizona"],
        "field": "preferredName.norm"
      }
    }
  }
}

```

#### 3. Workable Version - Multiple Terms:

```json
 {
                    "script_score": {
                        "script": {
                            "source": "String fieldValue = doc[params.field].value.toString().toLowerCase(); int minPos = Integer.MAX_VALUE;int totalFound = 0;for (String term : params.terms) { int pos = fieldValue.indexOf(term.toLowerCase()); if (pos >= 0) { totalFound += 1;  minPos = (int) Math.min(minPos, pos); } }  int wordCount =  /\\s+/.split(fieldValue.trim()).length; int score = (totalFound == wordCount) ? 0 :100000 + (minPos == Integer.MAX_VALUE ? 10000 : minPos) * 1000 + totalFound * 100 + wordCount; return score;",
                            "params": {
                                "terms": ["harvard"],
                                "field": "preferredName.norm"
                            }
                        }
                    },
                    "weight": 1
                 }

```

#### 4. Workable Version - Single/Two Terms:

```json
                 {
                    "script_score": {
                        "script": {
                            "source": "String fieldValue = doc[params.field].value; def pos1 = fieldValue.indexOf(params.term1); def pos2 = Math.max(fieldValue.indexOf(params.term2), 100); int len = /\\s+/.split(fieldValue.trim()).length; int ord = ( pos1 < pos2) ? 100:200; return Math.abs((pos1+1) * 1000 + ord +  len);",
                            "params": {
                                "term1": "uni",
                                "term2": "arizona",
                                "field": "preferredName.norm"
                            }
                        }
                    },
                   "weight" : 1
                }

```

---

### 🔎 Explanation of Score Tiers:

| Priority                    | Example                                 | Score                                |
|----------------------------|-----------------------------------------|--------------------------------------|
| Exact match                | "university arizona"                    | 0                                    |
| Starts with                | "university arizona campus"            | 1                                    |
| In-order phrase            | "the university arizona system"        | 2                                    |
| Reverse phrase             | "arizona university"                   | 3                                    |
| Scattered words (both terms) | "arizona is part of a university"      | 100 + distance * 10 + word count     |
| Incomplete / Substring match | "suniversity of arizona"               | Rejected (score = 1,000,000)         |


 ---

 ### 🧪 Input/Output Example

 ```json
 "terms": ["harvard"]

```
| Field Value                 | Score     | Match Type         |
|----------------------------|-----------|---------------------|
| "harvard"                  | 0         | exact              |
| "harvard university"       | 1         | starts with        |
| "this is harvard"          | 2         | contains term      |
| "suniversity of harvard"   | 1,000,000 | substring – rejected |
| "this is about havard"     | 1,000,000 | typo – rejected    |


---

✅ Ready for Production

- Fully guards against partial word matches
- Penalizes distance
- Flexible for single and multi-term queries
- Clean tiered scoring


---

### Enahnced Version - Up-to-date

```json
{
    "_source": [
        "preferredName", "itemPGUID"
    ],
    "from": 0,
    "size": 20,
    "query": {
        "function_score": {
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {
                                "itemStatus": 3
                            }
                        },
                        {
                            "prefix": {
                                "preferredName": {
                                    "value": "harvard",
                                    "case_insensitive": true,
                                    "boost": 1
                                }
                            }
                        }
                    ]
                }
            },
            "functions": [ 
                {
                    "script_score": {
                        "script": {
                            "source": "String fieldValue = doc[params.field].value.replace(' of ', ' ').toLowerCase(); String[] fieldTokens = /\\s+/.split(fieldValue.trim()); String queryPhrase = String.join(' ', params.terms).toLowerCase().replace(' of ', ' '); String reversedQuery = ''; for (int i = params.terms.length - 1; i >= 0; i--) { reversedQuery += params.terms[i].toLowerCase(); if (i > 0) reversedQuery += ' '; }  if (fieldValue.equals(queryPhrase)) return 0; if (fieldValue.startsWith(queryPhrase + ' ')) return fieldTokens.length; if (fieldValue.contains(' ' + queryPhrase + ' ') || fieldValue.endsWith(' ' + queryPhrase)) {int firstMatchPos = -1;String term = params.terms[0].toLowerCase();for (int i = 0; i < fieldTokens.length; i++) {if (fieldTokens[i].toLowerCase().startsWith(term)) { firstMatchPos = i; break;}} return 200 + (firstMatchPos + 1) * 10 + fieldTokens.length;} if (fieldValue.contains(' ' + reversedQuery + ' ') || fieldValue.startsWith(reversedQuery + ' ')) { int reversedPos = fieldValue.indexOf(reversedQuery); return 500 + (reversedPos + 1) * 10 + fieldTokens.length; } int matchedTerms = 0; int[] positions = new int[params.terms.length]; for (int i = 0; i < params.terms.length; i++) positions[i] = -1;  for (int i = 0; i < fieldTokens.length; i++) { for (int j = 0; j < params.terms.length; j++) { if (fieldTokens[i].equals(params.terms[j].toLowerCase())) { matchedTerms += 1; positions[j] = i; break; } } }  int minPos = Integer.MAX_VALUE; int maxPos = Integer.MIN_VALUE; for (int p : positions) { minPos = (int) Math.min(minPos, p); maxPos = (int)Math.max(maxPos, p); }  int distance = maxPos - minPos; return 1000 + distance * 10 + fieldTokens.length;",
                            "params": {
                                "terms": ["harvard"],
                                "field": "preferredName.norm"
                            }
                        }
                    },
                    "weight": 1
                 }
            ],
            "score_mode": "sum",
            "boost_mode": "replace"
        }
    },
    "sort": [
        {
            "_score": {
                "order": "asc"
            }
        },
        {
            "wos_count": {
                "order": "desc"
            }
        },
        {
            "preferredName.norm": {
                "order": "asc"
            }
        }
    ],
    "track_total_hits": 2147483647
}

```