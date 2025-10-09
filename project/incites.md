

---

### Context and Function Mapping


| Context                | Function                           | Unique Column                    | Supported by Champ API |
|------------------------|------------------------------------|----------------------------------|------------------------|
| Researchers            | IncitesExplore.personMain          | DAISNG_AUTHOR_KEY, AUTHOR_ID     | ✓                      |
|                        | IncitesExplore.personPerYear       | DAISNG_AUTHOR_KEY, AUTHOR_ID     | ✓                      |
| Organizations          | IncitesExplore.institutionMain     | INSTITUTION_KEY                  | ✓                      |
|                        | IncitesExplore.institutionPerYear  | INSTITUTION_KEY                  | ✓                      |
| Locations              | IncitesExplore.regionMain          | COUNTRY_KEY                      | ✓                      |
|                        | IncitesExplore.regionPerYear       | COUNTRY_KEY                      | ✓                      |
| Funders                | IncitesExplore.funderMain          | FUNDING_ORGANIZATION_KEY         | ✓                      |
|                        | IncitesExplore.funderPerYear       | FUNDING_ORGANIZATION_KEY         | ✓                      |å
| Research Areas         | IncitesExplore.subjectMain         | CATEGORY_KEY                     | ✓                      |
|                        | IncitesExplore.subjectPerYear      | CATEGORY_KEY                     | ✓                      |
| Publication Sources    | IncitesExplore.journalMain         | JOURNAL_KEY                      | ✓                      |
|                        | IncitesExplore.journalPerYear      | JOURNAL_KEY                      | ✓                      |
| Funder Types           | IncitesExplore.funderTypeMain      | FUNDING_TYPE_KEY                 |                        |
|                        | IncitesExplore.funderTypePerYear   | FUNDING_TYPE_KEY                 |                        |
| Grants                 | IncitesExplore.grantMain           | GRANT_ID                         |                        |
|                        | IncitesExplore.grantPerYear        | GRANT_ID                         |                        |
| Funded Organizations   | IncitesExplore.fundedInstitutionMain | FUNDED_ORGANIZATION_KEY       |                        |
|                        | IncitesExplore.fundedInstitutionPerYear | FUNDED_ORGANIZATION_KEY   |                        |
| Funded Researchers     | IncitesExplore.fundedPersonMain    | FUNDED_ORGANIZATION_KEY          |                        |
|                        | IncitesExplore.fundedPersonPerYear | FUNDED_ORGANIZATION_KEY          |                        |


### Default Parameters

| Parameter            | Default Value | Comment                         |
|----------------------|---------------|---------------------------------|
| sortColumn           | WOS_COUNTS    | Metric name for ranking         |
| sortOrder            | desc          | desc & asc                      |
| queryDataCollection  | WOS           | WOS & ESCI, we use WOS only for RI |
| isLimit              | 1             | To return the metric data       |
| start                | 1             | offset                          |
| end                  | 5             | size                            |


Reference: https://jira.clarivate.io/browse/SES-4201


---


### A Full List Of Filters


| Frontend Name          | Type                           | XRPC Name                  |
|------------------------|--------------------------------|----------------------------|
| personIdTypeGroup      |                                | personIdTypeGroup          |
| singlePrsnIdTypeGroup  |                                | personIdTypeGroup          |
| association            |                                | association                |
| openaccess             |                                | openaccess                 |
| authorposition         |                                | authorposition             |
| esimostcited           |                                | esimostcited               |
| clbrprsnId             |                                | clbrprsnnamefull           |
| clbrprsnId             | personIdType=fullName          | clbrprsnnamefull           |
| clbrprsnId             | personIdType=shortName         | clbrprsnnameshort          |
| clbrprsnId             | personIdType=researcherId      | clbrprsnnamerid            |
| clbrprsnId             | personIdType=orcId             | clbrorcrid                 |
| clbrprsnId             | personIdType=allUniqueId       | clbrUniqueId               |
| clbrprsnId             | personIdType=authorRecord      | clbrauthorrecord           |
| clbrprsnId             | personIdType=claimed           | clbrauthorrecord           |
| clbrprsnId             | personIdType=unclaimed         | clbrauthorrecord           |
| clbrorgname            |                                | clbrorgname                |
| clbrlocname            |                                | clbrlocname                |
| rgnsearch              |                                | rgnsearch                  |
| sbjsearch              |                                | sbjsearch                  |
| orgtype                |                                | orgtype                    |
| orgsearch              |                                | orgsearch                  |
| sbjname                |                                | sbjname                    |
| jrnname                |                                | jrnname                    |
| period                 |                                | period                     |
| personId               |                                | prsnname                   |
| personId               | personIdType=fullName          | prsnname                   |
| personId               | personIdType=shortName         | prsnnameshort              |
| personId               | personIdType=researcherId      | prsnrschid                 |
| personId               | personIdType=orcId             | prsnorcid                  |
| personId               | personIdType=allUniqueId       | prsnUniqueId               |
| personId               | personIdType=authorRecord      | authorRecord               |
| personId               | personIdType=claimed           | authorRecord               |
| personId               | personIdType=unclaimed         | authorRecord               |
| prssearch              | personIdType=fullName          | prssearch                  |
| prssearch              | personIdType=shortName         | prssearch                  |
| prssearch              | personIdType=authorRecord      | prssearch                  |
| prssearch              | personIdType=claimed           | prssearch                  |
| prssearch              | personIdType=unclaimed         | prssearch                  |
| prssearch              | personIdType=researcherId      | prssearch                  |
| prssearch              | personIdType=orcId             | prssearch                  |
| prssearch              | personIdType=allUniqueId       | prssearch                  |
| #NAME?                 | personIdType=claimed           | authorRecord               |
| #NAME?                 | personIdType=unclaimed         | authorRecord               |
| issn                   |                                | issn                       |
| schema                 |                                | schema                     |
| jrnsearch              |                                | jrnsearch                  |
| orgname                |                                | orgname                    |
| location               |                                | location                   |
| esisbjname             |                                | esisbjname                 |
| articletype            |                                | articletype                |
| woscountsOrg           |                                | woscounts                  |
| timescitedOrg          |                                | timescited                 |
| woscountsPrsn          |                                | woscounts                  |
| timescitedPrsn         |                                | timescited                 |
| woscountsRgn           |                                | woscounts                  |
| timescitedRgn          |                                | timescited                 |
| woscountsSbj           |                                | woscounts                  |
| timescitedSbj          |                                | timescited                 |
| woscountsJrn           |                                | woscounts                  |
| timescitedJrn          |                                | timescited                 |
| woscountsFnd           |                                | woscounts                  |
| timescitedFnd          |                                | timescited                 |
| publisher              |                                | publisher                  |
| funder                 |                                | funder                     |
| funderType             |                                | v_f.FUNDER_TYPE            |
| funderOrPublisher      | funder                         | v_f.FUNDING_ORGANIZATION   |
| fndsearch              |                                | v_f.FUNDING_ORGANIZATION   |
| clbrfunder             |                                | clbrfunder                 |
| singlePrsnId           |                                | prsnname                   |
| singlePrsnId           | singlePrsnIdType=fullName      | prsnname                   |
| singlePrsnId           | singlePrsnIdType=shortName     | prsnnameshort              |
| singlePrsnId           | singlePrsnIdType=researcherId  | prsnrschid                 |
| singlePrsnId           | singlePrsnIdType=orcId         | prsnorcid                  |
| singlePrsnId           | singlePrsnIdType=allUniqueId   | prsnUniqueId               |
| singlePrsnId           | singlePrsnIdType=authorRecord  | authorRecord               |
| singlePrsnId           | singlePrsnIdType=claimed       | authorRecord               |
| singlePrsnId           | singlePrsnIdType=unclaimed     | authorRecord               |
| wppersonId             |                                | wpauthor                   |
| wporgname              |                                | wporg                      |
| wpwid                  |                                | wpwid                      |
| wpclbrprsnId           |                                | wpclbrprsnid               |
| wpclbrorgname          |                                | wpclbrorgname              |
| wpclbrarea             |                                | wpclbrarea                 |
| wpprssearch            |                                | wpprssearch                |
| wporgsearch            |                                | wporgsearch                |
| deptlevels             |                                | deptlevels                 |
| wpdepts                |                                | wpdepts                    |
| locationType           |                                | countrytype                |
| jrncountry             |                                | jrncountry                 |
| authorcount            |                                | authorcount                |
| jrnQuartile            |                                | jrnQuartile                |
| averagejifpercentile   |                                | averagejifpercentile       |
| jrnSourceType          |                                | jrnSourceType              |
| alcNoTopicAssigned     |                                | alcNoTopicAssigned         |
| funderLocation         |                                | funderLocation             |
| fundingDataSource      |                                | fundingDataSource          |
| geographicCollabType   |                                | geographicCollabType       |
| topPercentileDocs      |                                | topPercentileDocs          |
| grantStartFnd          |                                | grantStartFnd              |
| grantEndFnd            |                                | grantEndFnd                |
| grantNumber            |                                | grantNumber                |
| jciQuartile            |                                | jciQuartile                |
| earlyAccess            |                                | earlyAccess                |
| jrnkey                 |                                | jrnkey                     |
| almaperiod             |                                | almaperiod                 |
| citedDocs              |                                | citedDocs                  |
| departments            |                                | departments                |


---

###  A Full List Of Indicators


| No  | Champ(XRPC)                   | UI Services               | UI                                      | Champ(XRPC)                   |
|-----|-------------------------------|---------------------------|-----------------------------------------|-------------------------------|
| 1   | INSTITUTION_FULL_NAME         | orgName                   | Organization                            | INSTITUTION_FULL_NAME         |
| 2   | WOS_COUNTS                    | wosDocuments              | Web of Science Documents                | WOS_COUNTS                    |
| 3   | TOT_CITES                     | timesCited                | Time Cited                              | TOT_CITES                     |
| 4   | INT_COLLAB                    | intCollaborations         | International Collaboration             | INT_COLLAB                    |
| 5   | ALL_OA_DOCS                   | allopenaccessdocs         | All Open Access Documents               | ALL_OA_DOCS                   |
| 6   | PCT_FIRST_AUTHOR              | percfirstauthor           | % First Author                          | PCT_FIRST_AUTHOR              |
| 7   | PCT_GLOBAL_BASELINE_DOCS      | prcntGlobalBaseDocs       | % Global Baseline (Docs)                | PCT_GLOBAL_BASELINE_DOCS      |
| 8   | COUNTRY                       | location                  | Country or Region                       | COUNTRY                       |
| 9   | ESI_MOST_CITED_INS            | esi                       | ESI Most Cited                          | ESI_MOST_CITED_INS            |
| 10  | PERC_INT_COLLAB               | prcntIntCollab            | % International Collaborations          | PERC_INT_COLLAB               |
| 11  | GOLD_DOCS                     | doajgolddocuments         | Gold Documents                          | GOLD_DOCS                     |
| 12  | PCT_LAST_AUTHOR               | perclastauthor            | % Last Author (2008-2023)               | PCT_LAST_AUTHOR               |
| 13  | PCT_GLOBAL_BASELINE_CITES     | prcntGlobalBaseCites      | % Global Baseline (Cites)               | PCT_GLOBAL_BASELINE_CITES     |
| 14  | NON_SELF_TOT_CITES            | nonselftimescited         | Time Cited without Self-Citations       | NON_SELF_TOT_CITES            |
| 15  | PROC_CITED                    | percentCited              | % Documents Cited                       | PROC_CITED                    |
| 16  | RANK                          | rank                      | Rank                                    | RANK                          |
| 17  | THE_99_PERCENTILE             | prcntDocsIn99             | % Documents in Top 1%                   | THE_99_PERCENTILE             |
| 18  | PERC_INDUS_COLLAB             | prcntIndCollab            | % Industry Collaborations               | PERC_INDUS_COLLAB             |
| 19  | GOLD_HYBRID_DOCS              | othergolddocuments        | Gold-Hybrid Documents                   | GOLD_HYBRID_DOCS              |
| 20  | PCT_CORRESP_AUTHOR            | perccorrespauthor         | % Corresponding Author (2008-2023)      | PCT_CORRESP_AUTHOR            |
| 21  | PCT_ALL_BASELINE_DOCS         | prcntBaselineAllDocs      | % Baseline for All Items (Docs)         | PCT_ALL_BASELINE_DOCS         |
| 22  | NORM                          | norm                      | Category Normalized Citation Impact     | NORM                          |
| 23  | LIST_INSTITUTION_TYPES        | type                      | Organization Type                       | LIST_INSTITUTION_TYPES        |
| 24  | THE_90_PERCENTILE             | prcntDocsIn90             | % Documents in Top 10%                  | THE_90_PERCENTILE             |
| 25  | FREE_TO_READ_DOCS             | bronzedocuments           | Free to Read Documents                  | FREE_TO_READ_DOCS             |
| 26  | FIRST_AUTHOR                  | firstauthor               | First Author (2008-2023)                | FIRST_AUTHOR                  |
| 27  | INDUS_COLLAB_DOCS             | indCollaborations         | Industry Collaboration                  | INDUS_COLLAB_DOCS             |
| 28  | PCT_ALL_BASELINE_CITES        | prcntBaselineAllCites     | % Baseline for All Items (Cites)        | PCT_ALL_BASELINE_CITES        |
| 29  | AVG_CITES                     | avrgCitations             |                                         | AVG_CITES                     |
| 30  | P_ESI_MOST_CITED_ARTICLE      | prcntHighlyCitedPapers    | % Highly Cited Papers                   | P_ESI_MOST_CITED_ARTICLE      |
| 31  | LAST_AUTHOR                   | lastauthor                | Last Author (2008-2023)                 | LAST_AUTHOR                   |
| 32  | COUNTRY_COLLAB                | countryCollab             | Domestic Collaborations                 | COUNTRY_COLLAB                |
| 33  | PCT_PINNED_BASELINE_DOCS      | prcntBaselineForPinnedDocs| % Baseline for Pinned Items (Docs)      | PCT_PINNED_BASELINE_DOCS      |
| 34  | GREEN_SUBMITTED_DOCS          | greensubmitteddocs        | Green Submitted Documents               | GREEN_SUBMITTED_DOCS          |
| 35  | AVG_PERCENTILE                | avrgPrcnt                 | Average Percentile                      | AVG_PERCENTILE                |
| 36  | ESI_MOST_CITED_ARTICLE        | highlyCitedPapers         | Highly Cited Papers                     | ESI_MOST_CITED_ARTICLE        |
| 37  | STATE                         | stateProvice              | State or Province                       | STATE                         |
| 38  | GREEN_ACCEPTED_DOCS           | greenaccepteddocuments    | Green Accepted Documents                | GREEN_ACCEPTED_DOCS           |
| 39  | CORRESP_AUTHOR                | correspauthor             | Corresponding Author (2008-2023)        | CORRESP_AUTHOR                |
| 40  | PERC_COUNTRY_COLLAB           | prcntCountryCollab        | % Domestic Collaborations               | PERC_COUNTRY_COLLAB           |
| 41  | PCT_PINNED_BASELINE_DOCS      | prcntBaselineForPinnedCites| % Baseline for Pinned Items (Cites)    | PCT_PINNED_BASELINE_DOCS      |
| 42  | JXC                           | jNCI                      | Journal Normalized Citation Impact      | JXC                           |
| 43  | P_HOT_PAPER                   | prcntHotPapers            | % Hot Papers                            | P_HOT_PAPER                   |
| 44  | GREEN_PUB_DOCS                | greenpublisheddocuments   | Green Published Documents               | GREEN_PUB_DOCS                |
| 45  | ORGANIZATION_ONLY_COLLAB      | organizationOnly          | Organization only Collaborations        | ORGANIZATION_ONLY_COLLAB      |
| 46  | IMPACT_TO_WORLD               | impactRelToWorld          | Impact Relative to World                | IMPACT_TO_WORLD               |
| 47  | DOCS_JIF                      | jifdocs                   | Documents in JIF Journals               | DOCS_JIF                      |
| 48  | GREEN_ONLY                    | greenOnly                 | Green only Documents                    | GREEN_ONLY                    |
| 49  | PERC_ORGANIZATION_ONLY_COLLAB | prcntOrganizationOnly     | % Organization only Collaborations      | PERC_ORGANIZATION_ONLY_COLLAB |
| 50  | H_INDEX                       | hindex                    | H-index                                 | H_INDEX                       |
| 51  | DOCS_Q1                       | jifdocsq1                 | Documents in Q1 Journals                | DOCS_Q1                       |
| 52  | NON_OA_DOCS                   | nonOaDocs                 | Non-Open Access Documents               | NON_OA_DOCS                   |
| 53  | DOCS_Q2                       | jifdocsq2                 | Documents in Q2 Journals                | DOCS_Q2                       |
| 54  | PCT_ALL_OA_DOCS               | percallopenaccess         | % All Open Access Documents             | PCT_ALL_OA_DOCS               |
| 55  | NON_SELF_H_INDEX              | nonselfhindex             | H-index without Self-Citations          | NON_SELF_H_INDEX              |
| 56  | CNT_CITED                     | docsCited                 | Document Cited                          | CNT_CITED                     |
| 57  | DOCS_Q3                       | jifdocsq3                 | Documents in Q3 Journals                | DOCS_Q3                       |
| 58  | PCT_GOLD_DOCS                 | percdoajgolddocuments     | % Gold Documents                        | PCT_GOLD_DOCS                 |
| 59  | DOCS_Q4                       | jifdocsq4                 | Documents in Q4 Journals                | DOCS_Q4                       |
| 60  | CITED_YEAR_COUNT              | yearCiting                | Cumulative Citations Per Year           | CITED_YEAR_COUNT              |
| 61  | PCT_GOLD_HYBRID_DOCS          | percothergolddocuments    | % Gold-Hybrid Documents                 | PCT_GOLD_HYBRID_DOCS          |
| 62  | PERCENTILE_QA1                | percjifdocsq1             | % Documents in Q1 Journals              | PERCENTILE_QA1                |
| 63  | PCT_FREE_TO_READ_DOCS         | percbronzedocuments       | % Free to Read Documents                | PCT_FREE_TO_READ_DOCS         |
| 64  | CITATIONS_FROM_PATENTS        | citationsFromPatents      | Citations From Patents                  | CITATIONS_FROM_PATENTS        |
| 65  | PERCENTILE_QA2                | percjifdocsq2             | % Documents in Q2 Journals              | PERCENTILE_QA2                |
| 66  | PCT_GREEN_SUBMITTED_DOCS      | percgreensubmitteddocs    | % Green Submitted Documents             | PCT_GREEN_SUBMITTED_DOCS      |
| 67  | PERCENTILE_QA3                | percjifdocsq3             | % Documents in Q3 Journals              | PERCENTILE_QA3                |
| 68  | PCT_GREEN_ACCEPTED_DOCS       | percgreenaccepteddocuments| % Green Accepted Documents              | PCT_GREEN_ACCEPTED_DOCS       |
| 69  | PERCENTILE_QA4                | percjifdocsq4             | % Documents in Q4 Journals              | PERCENTILE_QA4                |
| 70  | PCT_GREEN_PUB_DOCS            | percgreenpublisheddocuments| % Green Published Documents            | PCT_GREEN_PUB_DOCS            |
| 71  | THE_99_PERCENTILE_DOCS        | docsIn99                  | Documents in Top 1%                     | THE_99_PERCENTILE_DOCS        |
| 72  | PCT_GREEN_ONLY_DOCS           | prcntGreenOnly            | % Green Only Documents                  | PCT_GREEN_ONLY_DOCS           |
| 73  | THE_90_PERCENTILE_DOCS        | docsIn90                  | Documents in Top 10%                    | THE_90_PERCENTILE_DOCS        |
| 74  | PCT_NON_OA_DOCS               | prcntNonOaDocs            | % Non-Open Access Documents             | PCT_NON_OA_DOCS               |
| 75  | HOT_PAPER_DOCS                | hotPapers                 | Hot Papers                              | HOT_PAPER_DOCS                |



---


### Context and Endpoints

| Context             | Endpoint                                                                 |
|---------------------|--------------------------------------------------------------------------|
| Researchers         | [https://incites.clarivate.com/incites-app/explore/0/person](https://incites.clarivate.com/incites-app/explore/0/person)          |
| Organizations       | [https://incites.clarivate.com/incites-app/explore/0/organizaion](https://incites.clarivate.com/incites-app/explore/0/organizaion)  |
| Departments         | [https://incites.clarivate.com/incites-app/explore/0/department](https://incites.clarivate.com/incites-app/explore/0/department)   |
| Locations           | [https://incites.clarivate.com/incites-app/explore/0/region](https://incites.clarivate.com/incites-app/explore/0/region)           |
| Research Areas      | [https://incites.clarivate.com/incites-app/explore/0/subject](https://incites.clarivate.com/incites-app/explore/0/subject)         |
| Publication Sources | [https://incites.clarivate.com/incites-app/explore/0/journal](https://incites.clarivate.com/incites-app/explore/0/journal)         |
| Funding Agencies    | [https://incites.clarivate.com/incites-app/explore/0/funder](https://incites.clarivate.com/incites-app/explore/0/funder)           |


#### API Paths

| API       | Path                                                            |
|-----------|-----------------------------------------------------------------|
| main      | /data/table/page?queryDataCollection=ESCI                       |
| peryear   | /data/trend/page?queryDataCollection=ESCI                       |
| benchmark | /data/table/benchmarks?queryDataCollection=ESCI                 |
| isTotal   | /data/table/total?queryDataCollection=ESCI                      |


#### Codes


- UI Service Restful Endpoint

| Context             | Endpoint                                                                 |
|---------------------|--------------------------------------------------------------------------|
| Researchers         | [https://incites.clarivate.com/incites-app/explore/0/person](https://incites.clarivate.com/incites-app/explore/0/person)          |
| Organizations       | [https://incites.clarivate.com/incites-app/explore/0/organizaion](https://incites.clarivate.com/incites-app/explore/0/organizaion)  |
| Departments         | [https://incites.clarivate.com/incites-app/explore/0/department](https://incites.clarivate.com/incites-app/explore/0/department)   |
| Locations           | [https://incites.clarivate.com/incites-app/explore/0/region](https://incites.clarivate.com/incites-app/explore/0/region)           |
| Research Areas      | [https://incites.clarivate.com/incites-app/explore/0/subject](https://incites.clarivate.com/incites-app/explore/0/subject)         |
| Publication Sources | [https://incites.clarivate.com/incites-app/explore/0/journal](https://incites.clarivate.com/incites-app/explore/0/journal)         |
| Funding Agencies    | [https://incites.clarivate.com/incites-app/explore/0/funder](https://incites.clarivate.com/incites-app/explore/0/funder)           |


- API Paths

| API       | Path                                                            |
|-----------|-----------------------------------------------------------------|
| main      | /data/table/page?queryDataCollection=ESCI                       |
| peryear   | /data/trend/page?queryDataCollection=ESCI                       |
| benchmark | /data/table/benchmarks?queryDataCollection=ESCI                 |
| isTotal   | /data/table/total?queryDataCollection=ESCI                      |



** Reference: https://jira.clarivate.io/browse/SES-4255**