
### Databricks Lakehouse and Data Mesh

https://www.databricks.com/blog/databricks-lakehouse-and-data-mesh-part-1
https://www.databricks.com/blog/building-data-mesh-based-databricks-lakehouse-part-2


Data mesh is a paradigm that describes a set of principles and logical architecture for scaling data analytics platforms. The purpose is to derive more value from data as an asset at scale. The phrase 'data mesh' was introduced by Zhamak Dehghani in 2019 and expanded on in her 2020 article Data Mesh Principles and Logical Architecture.

At the core of the data mesh logical architecture are four principles:
- Domain ownership: adopting a distributed architecture where domain teams - data producers - retain full responsibility for their data throughout its lifecycle, from capture through curation to analysis and reuse
- Data as a product: applying product management principles to the data analytics lifecycle, ensuring quality data is provided to data consumers who may be within and beyond the producer's domain
- Self-service infrastructure platform: taking a domain-agnostic approach to the data analytics lifecycle, using common tools and methods to build, run, and maintain interoperable data products
- Federated governance: ensuring a data ecosystem that adheres to organizational rules and industry regulations through standardization







### Building a Data Mesh Based on the Databricks Lakehouse

The basic building block of a data mesh

- Source data (owned by the domain)
- Self-serve compute resources and orchestration (within Databricks Workspaces)
- Domain-oriented Data Products served to other teams and domains
- Insights ready for consumption by business users
- Adherence to federated computational governance policies-

To enable capabilities
- cross-domain collaboration
- self-service analytics 
- common services  
- access control mechanisms 
- data cataloging
  

Databricks Unity Catalog 
- informational cataloging capabilities
- enforcement of fine-grained access controls and auditing


### Approach for a harmonized Data Mesh
A harmonized data mesh emphasizes autonomy within domains:

- Data domains create and publish domain-specific data products
- Data discovery is automatically enabled by Unity Catalog
- Data products are consumed in a peer-to-peer way
- Domain infrastructure is harmonized via
- platform blueprints, ensuring security and compliance
- self-serve platform services (domain provisioning automation, data cataloging, metadata publishing, policies on data and compute resources)

* The implications of a harmonized approach may include:

- Data Domains each needing to adhere to standards and best practices for interoperability and infrastructure management
- Data Domains each independently spending more time and effort on topics such as access controls, underlying storage accounts, or even infrastructure (e.g. event brokers for streaming data products)


### Approach for a Hub & Spoke Data Mesh
A Hub & Spoke Data Mesh incorporates a centralized location for managing shareable data assets and data that does not sit logically within any single domain:

- Data domains (spokes) create domain specific data products
- Data products are published to the data hub, which owns and manages a majority of assets registered in Unity Catalog
- The data hub provides generic services platform operations for data domains such as:
- self-service data publishing to managed locations
- data cataloging, lineage, audit, and access control via Unity Catalog
- data management services such as time travel and GDPR processes across domains (e.g. right to be forgotten requests)
- The data hub can also act as a data domain. For example, pipelines or tools for generic or externally acquired datasets such as weather, market research, or standard macroeconomic data.

* The implications for a Hub and Spoke Data Mesh include:
- Data domains can benefit from centrally developed and deployed data services, allowing them to focus more on business and - data transformation logic
- Infrastructure automation and self-service compute can help prevent the data hub team from becoming a bottleneck for data product publishing

In both of these approaches, domains may also have common and repeatable needs such as:
- Data ingestion tools and connectors
- MLOps frameworks, templates, or best practices
- Pipelines for CI/CD, data quality, and monitoring


### Scaling and evolving the Data Mesh





