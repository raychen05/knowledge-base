
## System Design - 2

Great image! It’s a list of system design practice problems (常见面试题目) with different difficulty levels (“容易的” = easy, “中等的” = medium, “困难的” = hard). I’ll go through each visible question from the image and provide details on what interviewers expect you to cover for each one.

---

### 🔹 Easy Level

1.	设计一个自动售货机系统 (Design a Vending Machine System)
- 	Handle item selection, inventory, pricing.
- 	Support cash & card payments.
- 	Manage refunds & change.
- 	Concurrency if multiple users.

2.	设计一个标签服务 (Design a Tagging Service)
- 	Allow users to create, assign, search tags.
- 	Support tagging for different object types (posts, files, users).
- 	Store relationships (tag-object mapping).
- 	Query optimization.

3.	设计Craigslist (Design Craigslist)
- 	Classified ads system: categories, listings, search, filtering.
- 	User authentication.
- 	Messaging between buyers/sellers.
- 	Scalability for search + spam prevention.

4.	设计一个多设备图片采集系统 (Design Multi-device Image Collection System)
- 	Sync images from multiple devices.
- 	Deduplication & conflict resolution.
- 	Storage optimization (cloud, CDN).
- 	Privacy/security handling.

---

### 🔹 Medium Level

5.	设计Instagram (Design Instagram)
- 	Upload & store images/videos.
- 	Feed generation (ranking, caching).
- 	User profiles, followers/following.
- 	Scalability (sharding, CDN for media).
- 	Search & hashtags.
	
6.	设计一个在线国际象棋服务 (Design Online Chess Service)
- 	Matchmaking (random, ranked).
- 	Game state synchronization in real-time.
- 	Persistence for move history.
- 	Anti-cheat & fairness.
	
7.	设计一个Web缓存 (Design a Web Cache)
- 	Cache strategies (LRU, LFU, TTL).
- 	Consistency (cache invalidation).
- 	Distributed cache (Redis, Memcached).
- 	Scaling read-heavy systems.
	
8.	设计一个任务计划表 (Design a Task Scheduler)
- 	Support recurring & one-time jobs.
- 	Handle failures, retries, priorities.
- 	Distributed job coordination.
- 	Scalability (many workers, message queues).
	
9.	设计电子商务服务 (Design an E-commerce Service)
- 	Product catalog, inventory, cart.
- 	Payment gateway integration.
- 	Order lifecycle management.
- 	Recommendation system.
- 	High availability & scaling for big sales.
	
10.	设计一个库存管理系统 (Design Inventory Management System)
- 	Track stock in multiple warehouses.
- 	Handle concurrent updates (race conditions).
- 	Integrate with sales/orders.
- 	Support auditing & analytics.

---

### 🔹 Hard Level

11.	设计谷歌地图 (Design Google Maps)
- 	Map storage (tiles, vector data).
- 	Geospatial indexing.
- 	Routing algorithms (Dijkstra, A*).
- 	Real-time traffic updates.
- 	Scalability for billions of queries.

12.	设计谷歌文档 (Design Google Docs)
- 	Real-time collaborative editing.
- 	Conflict resolution (OT, CRDTs).
- 	Document storage & versioning.
- 	Access control & sharing.

13.	设计一个自动化交易平台 (Design Automated Trading Platform)
- 	Low latency order execution.
- 	Matching engine for buy/sell.
- 	Risk management & compliance.
- 	Fault tolerance.

14.	设计一个关键价值存储 (Design a Key-Value Store)
- 	Read/write performance.
- 	Replication, sharding, consistency models (CAP tradeoffs).
- 	Compaction, indexing.
- 	Fault tolerance & recovery.

15.	设计一个全球内容分发网络 (Design a CDN)
- 	Edge servers & caching strategy.
- 	Load balancing.
- 	Content invalidation.
- 	Geo-distributed storage.

16.	设计一个对等网络 (Design a Peer-to-Peer Network)
- 	Node discovery.
- 	Data replication, consistency.
- 	Fault tolerance when nodes leave.
- 	Security (malicious peers, encryption).

17.	设计一个分布式消息队列 (Design Distributed Message Queue)
- 	Producer-consumer model.
- 	Message ordering & delivery guarantees (at-most-once, at-least-once, exactly-once).
- 	Scalability (partitioning, replication).
- 	Fault tolerance.

---

### ✅ Each of these problems tests trade-offs (consistency vs availability, latency vs throughput), scalability, and real-world constraints (latency, concurrency, fault tolerance, cost).

---

Would you like me to create a structured prep sheet (like a table with problem → key components → common pitfalls → advanced extensions), so you can use it as a System Design Interview Drill Deck?


Perfect ✅ — I’ll create a System Design Interview Drill Deck in a structured table format.

This will include:
- 	Problem
- 	Key Components (what to design)
- 	Common Pitfalls (things candidates often miss)
- 	Advanced Extensions (ways to stand out in interview)

---

### 📘 System Design Interview Drill Deck


| **Problem**                        | **Key Components**                                               | **Common Pitfalls**                               | **Advanced Extensions**                           |
|------------------------------------|-----------------------------------------------------------------|--------------------------------------------------|--------------------------------------------------|
| **Vending Machine System**         | Item catalog, payment (cash/card), inventory mgmt, refunds      | Ignoring concurrency (two users buying last item), change calculation | Mobile payment support, IoT-based restocking alerts |
| **Tagging Service**                | Tag-object mapping, search & filter, indexing                   | Poor schema design (tag explosion), ignoring scalability | Multi-language tags, recommendation (“related tags”) |
| **Craigslist**                     | Classified listings, categories, search, messaging, spam control | No abuse/spam prevention, weak search            | Ranking algorithm, fraud detection, location-based services |
| **Image Collection (multi-device)**| Sync across devices, deduplication, conflict resolution, cloud storage | Missing offline sync & conflict cases            | End-to-end encryption, selective sync           |
| **Instagram**                      | Media upload/storage, feed ranking, follow system, CDN, hashtags| Forgetting feed personalization, large media storage scaling | Stories/live streams, recommender system        |
| **Online Chess Service**           | Matchmaking, game state sync, persistence, anti-cheat           | Handling latency in moves, disconnect recovery   | AI opponent, tournament modes                   |
| **Web Cache**                      | Cache strategies (LRU/LFU/TTL), invalidation, distributed cache | Cache stampede, not handling stale data          | Multi-tier cache (CDN + Redis + local)          |
| **Task Scheduler**                 | Job storage, execution engine, retries, priority queue          | Ignoring failures, race conditions               | Cron + distributed workers, workflow orchestration |
| **E-commerce Service**             | Catalog, inventory, payments, cart, order lifecycle            | Weak transaction handling (race on stock)        | Personalization, flash-sale optimization         |
| **Inventory Mgmt System**          | Stock levels, multi-warehouse sync, auditing                    | Not handling concurrent updates                  | Forecasting, supplier integration               |
| **Google Maps**                    | Map tiles, routing algorithms, geospatial index, traffic updates | Missing geo-scale challenges, route recomputation| AR navigation, offline caching                  |
| **Google Docs**                    | Collaborative editing, OT/CRDTs, version history, permissions  | Not handling real-time conflicts                 | Offline editing, plugin ecosystem               |
| **Automated Trading Platform**     | Matching engine, low-latency infra, risk controls, compliance   | Ignoring latency/jitter, failure recovery        | Algorithmic trading strategies, backtesting     |
| **Key-Value Store**                | Partitioning, replication, consistency models (CAP), indexing   | Weak consistency model explanation               | TTL support, multi-region replication           |
| **CDN**                            | Edge servers, caching, load balancing, invalidation            | Ignoring geo-latency & DDoS resilience           | Dynamic content acceleration, tiered cache      |
| **P2P Network**                    | Node discovery, replication, churn mgmt, security              | Missing Sybil attack & NAT traversal             | Hybrid (P2P + central index), incentive models  |
| **Distributed Message Queue**      | Producers, consumers, partitions, ordering, delivery guarantees | Ignoring exactly-once semantics, backpressure    | Stream processing integration, multi-region queue |



Great 👍 — let’s turn the drill deck into one-page study notes / flashcards.

Each problem will have:
1. Overview (what it is)
2. Core Requirements
3. Architecture Sketch (text-based)
4. Trade-offs / Pitfalls
5. Advanced Extensions

I’ll draft a few as examples, then we can decide if you want me to expand all 17 into a full playbook.

### 📘 System Design Flashcards (Sample)


#### 1. Vending Machine System

Overview: A local embedded system that sells items, handles payments, and manages inventory.

Core Requirements:
* Item selection (buttons or UI)
* Payment: cash, card, mobile
* Inventory management
* Refunds, change return

Architecture Sketch:

[UI] -> [Controller Logic] -> [Inventory DB]
                     ↘
                      [Payment Module] -> [Bank API]

Trade-offs / Pitfalls:
* Race condition if two users pick last item
* Handling out-of-stock gracefully
* Hardware failures (jammed dispenser)

Advanced Extensions:
* IoT-enabled remote monitoring
* Predictive restocking alerts
* Loyalty system integration

#### 2. Instagram

Overview: A large-scale photo & video sharing platform with billions of users.

Core Requirements:
* Upload/store media (images, videos)
* User profiles & social graph (followers)
* Feed ranking & personalization
* Hashtags, search, comments

Architecture Sketch:

[Client] -> [API Gateway] -> [App Servers] -> [Feed Service]
                                 |              ↘
                                 |               [Ranking/ML Model]
                                 |
                               [Media Service] -> [CDN/Blob Storage]


Trade-offs / Pitfalls:
* Feed generation = heavy read/write workload
* Storage costs for billions of media files
* Real-time scaling under sudden spikes

Advanced Extensions:
* Stories, reels, live streaming
* ML-based recommendations
* Multi-region replication for global users


### 3. Google Docs

Overview: A collaborative real-time editing system.

Core Requirements:
* Multiple users editing simultaneously
* Conflict resolution (OT or CRDTs)
* Version history, rollback
* Sharing & permissions

Architecture Sketch:

[Client Editor] <-> [Sync Service] <-> [Doc State Storage]
           ↕
  [Real-time Conflict Resolver (OT/CRDT)]

Trade-offs / Pitfalls:
* Latency in collaborative editing
* Offline sync conflicts
* Maintaining data consistency across users

Advanced Extensions:
* Offline editing mode
* Plugin ecosystem (charts, equations)
* AI-based suggestions (auto-complete)

### 4. Distributed Message Queue

Overview: A backbone service enabling decoupled producers and consumers with reliable message delivery.

Core Requirements:
* Producers publish messages
* Consumers subscribe & process
* Ordering guarantees (FIFO, partitioned)
* Delivery semantics (at-most-once, at-least-once, exactly-once)

Architecture Sketch:

[Producer] -> [Broker Cluster] -> [Partitioned Topics] -> [Consumer Group]

Trade-offs / Pitfalls:
* Throughput vs ordering trade-off
* Exactly-once semantics are expensive
* Backpressure when consumers are slow

Advanced Extensions:
* Stream processing (Kafka Streams, Flink)
* Multi-region replication
* Schema registry for typed messages

⚡ Question for you:Do you want me to continue and build all 17 problems into full flashcards (probably 15–20 pages total, one per system), or do you prefer a condensed version (2–3 per page) for quicker review?

You said:
Yes

ChatGPT said:
Got it ✅ — you want the full set of 17 flashcards / study notes expanded like the samples.
Here’s the plan:

* Each system design problem = 1 page (flashcard format)
* Covers: Overview → Core Requirements → Architecture Sketch → Trade-offs → Advanced Extensions
* Output: a structured document you can print or use digitally

### 📘 System Design Flashcards (Complete Set)

1. Vending Machine System

Overview: Embedded system for automated sales, payments, and stock management.
Core Requirements:
* Item selection (buttons/UI)
* Payment: cash, card, mobile wallet
* Inventory updates in real time
* Refunds, change return

Architecture Sketch:

[User Interface] -> [Controller Logic] -> [Inventory Store]
                        ↘
                         [Payment Module] -> [Bank API]

Trade-offs / Pitfalls:
* Concurrency (two users buy last item)
* Hardware faults (jammed dispenser)
* Payment failure handling

Advanced Extensions:
* IoT monitoring (predictive restocking)
* Remote telemetry for operators
* Integration with loyalty programs

2. Tagging Service

Overview: Allows tagging of entities (posts, users, products) for discovery.

Core Requirements:
* Create, assign, search tags
* Many-to-many mapping (tag ↔ object)
* Fast search queries
* Deduplication / normalization

Architecture Sketch:

[App Server] -> [Tag DB: tag_id, object_id, metadata]
                       ↘
                        [Search Index]
Trade-offs / Pitfalls:
* Tag explosion (millions of tags)
* Poor schema = slow queries
* Handling synonyms and misspellings

Advanced Extensions:
* Multi-language tags
* Related tag recommendations
* Auto-tagging via ML

3. Craigslist

Overview: Classified ads platform with search and messaging.

Core Requirements:
* Post listings with categories & metadata
* Search & filter by category, location
* Messaging between buyer/seller
* Spam prevention

Architecture Sketch:

[Client] -> [API Layer] -> [Listings DB] -> [Search Index]
                              ↘
                              [Messaging Service]

Trade-offs / Pitfalls:
* Spam / fraud prevention often overlooked
* Weak search at scale
* Handling expired listings

Advanced Extensions:
* Ranking & recommendation system
* Geo-aware listings
* Fraud/anomaly detection

4. Multi-device Image Collection

Overview: Syncs and deduplicates user photos across devices.

Core Requirements:
* Device sync (upload/download)
* Conflict resolution for edits
* Deduplication
* Efficient cloud storage

Architecture Sketch:

[Device Client] <-> [Sync Service] <-> [Storage Layer]
                                ↘
                                 [Deduplication Service]

Trade-offs / Pitfalls:
* Conflict resolution across devices
* Storage cost for large images/videos
* Handling offline/spotty connections

Advanced Extensions:
* End-to-end encryption
* Smart compression/deduplication
* Selective sync

5. Instagram

Overview: Large-scale photo/video sharing with social graph.

Core Requirements:
* Upload/store media (photos, reels)
* Feed generation & ranking
* Follow/unfollow graph
* Hashtags & discovery

Architecture Sketch:

[Client] -> [API Gateway] -> [Feed Service] -> [Ranking/ML Engine]
                         ↘
                          [Media Service] -> [CDN/Blob Storage]

Trade-offs / Pitfalls:
* Feed personalization = complex + costly
* Media storage = PB scale
* Handling viral content spikes

Advanced Extensions:
* Stories, reels, live streaming
* ML-based content moderation
* Multi-region replication

6. Online Chess Service

Overview: Real-time online chess matches with persistence.

Core Requirements:
* Matchmaking (ranked/casual)
* Real-time move sync
* Game history persistence
* Anti-cheat detection

Architecture Sketch:

[Player Client] <-> [Match Server] -> [Game DB]
                          ↘
                           [Real-time Sync Service]

Trade-offs / Pitfalls:
* Latency during real-time moves
* Disconnects / reconnection handling
* Cheating (bots, multiple accounts)

Advanced Extensions:
* AI opponents
* Tournament & leaderboard support
* Spectator mode

7. Web Cache

Overview: Improves performance by caching frequently used content.

Core Requirements:
* Cache strategies (LRU, LFU, TTL)
* Cache invalidation
* Distributed cache cluster
* Write-through vs write-back

Architecture Sketch:

[Client] -> [Cache Layer] -> [App Server] -> [DB]

Trade-offs / Pitfalls:
* Cache stampede (thundering herd)
* Stale/invalid data
* Cache consistency

Advanced Extensions:
* Multi-layer caching (browser + CDN + Redis)
* Predictive prefetching
* Adaptive eviction policies

8. Task Scheduler

Overview: Executes delayed/recurring jobs reliably.

Core Requirements:
* Job creation & persistence
* Priority scheduling
* Retry logic, failure handling
* Distributed workers

Architecture Sketch:

[Client] -> [Scheduler API] -> [Job Queue] -> [Worker Pool]
                               ↘
                                [Retry/Failure Manager]

Trade-offs / Pitfalls:
* Race conditions in scheduling
* Node failures cause missed jobs
* Clock drift in distributed systems

Advanced Extensions:
* Workflow orchestration
* Cron + DAG execution
* Multi-region failover

9. E-commerce Service

Overview: Online shopping platform with payments.

Core Requirements:
* Product catalog & search
* Cart management
* Checkout & payments
* Order lifecycle tracking

Architecture Sketch:

[Client] -> [API Gateway] -> [Catalog Service] -> [DB]
                          -> [Cart Service]
                          -> [Order Service] -> [Payment Gateway]

Trade-offs / Pitfalls:
* Stock race condition at checkout
* Payment failures & retries
* High traffic during flash sales

Advanced Extensions:
* Recommendation engine
* Fraud detection
* Multi-warehouse support

10. Inventory Management System

Overview: Tracks stock across warehouses.

Core Requirements:
* Real-time stock updates
* Multi-location management
* Concurrency-safe updates
* Auditing & reporting

Architecture Sketch:

[Warehouse Terminal] -> [Inventory API] -> [Inventory DB]

Trade-offs / Pitfalls:
* Double-selling same stock item
* Eventual consistency vs strong consistency
* Overselling during spikes

Advanced Extensions:
* Demand forecasting
* Supplier auto-replenishment
* Analytics dashboards

11. Google Maps

Overview: Mapping and navigation platform.

Core Requirements:
* Map storage (tiles/vector)
* Geospatial indexing
* Routing (shortest path, A*)
* Real-time traffic

Architecture Sketch:

[Client] -> [API Gateway] -> [Map Tile Service] -> [Tile Storage]
                         -> [Routing Engine] -> [Graph DB]

Trade-offs / Pitfalls:
* Billions of queries at scale
* Route recomputation under traffic changes
* Handling offline usage

Advanced Extensions:
* AR navigation
* Street View integration
* Predictive traffic patterns

12. Google Docs

Overview: Collaborative real-time text editor.

Core Requirements:
* Multi-user editing sync
* Conflict resolution (OT/CRDT)
* Version history
* Permissions & sharing

Architecture Sketch:

[Client Editor] <-> [Collab Service] <-> [Doc DB]
           ↕
   [Conflict Resolver: OT/CRDT]

Trade-offs / Pitfalls:
* Latency in collaboration
* Offline sync conflicts
* Data consistency

Advanced Extensions:
* Offline editing mode
* Plugins ecosystem
* Smart suggestions (AI assist)

13. Automated Trading Platform

Overview: Executes buy/sell orders automatically at scale.

Core Requirements:
* Low-latency order execution
* Matching engine
* Risk management
* Compliance logging

Architecture Sketch:

[Trader Client] -> [Order Gateway] -> [Matching Engine] -> [Exchange]
                                   ↘
                                    [Risk Mgmt Service]

Trade-offs / Pitfalls:
* Microsecond-level latency matters
* Fault tolerance during crashes
* Handling market volatility

Advanced Extensions:
* Algo-trading strategies
* Backtesting engine
* Real-time dashboards

14. Key-Value Store

Overview: Distributed database storing (key, value) pairs.

Core Requirements:
* Partitioning & replication
* Consistency (CP vs AP in CAP)
* Fault tolerance
* Compaction & indexing

Architecture Sketch:

[Client] -> [Coordinator] -> [Shard/Replica Nodes] -> [Storage Engine]

Trade-offs / Pitfalls:
* Eventual consistency vs strong consistency
* Hotspot keys cause imbalance
* Recovery from node failures

Advanced Extensions:
* TTL & eviction policies
* Multi-region replication
* Secondary indexes

15. CDN (Content Delivery Network)

Overview: Geo-distributed network for fast content delivery.

Core Requirements:
* Edge caching servers
* Load balancing
* Cache invalidation
* Origin fallback

Architecture Sketch:

[Client] -> [Edge Node CDN] -> [Origin Server]

Trade-offs / Pitfalls:
* Cache invalidation is hard
* Geo-latency not considered
* DDoS resilience

Advanced Extensions:
* Dynamic content acceleration
* Tiered caching
* Edge computing functions

16. Peer-to-Peer Network

Overview: Decentralized network of nodes sharing data.

Core Requirements:
* Peer discovery
* Data replication
* Churn handling (nodes leaving)
* Security against malicious peers

Architecture Sketch:

[Node A] <-> [Node B] <-> [Node C]

Trade-offs / Pitfalls:
* Sybil attacks
* NAT traversal issues
* Data consistency

Advanced Extensions:
* Hybrid (central + P2P)
* Incentive model (token-based)
* Gossip protocol optimizations

17. Distributed Message Queue

Overview: Reliable async messaging between producers & consumers.

Core Requirements:
* Producers publish → topics/partitions
* Consumers read → consumer groups
* Delivery guarantees (at-most/at-least/exactly-once)
* Scaling horizontally

Architecture Sketch:

[Producer] -> [Broker Cluster] -> [Partitioned Topics] -> [Consumers]

Trade-offs / Pitfalls:
* High throughput vs ordering
* Exactly-once = expensive
* Backpressure handling

Advanced Extensions:
* Stream processing integration
* Multi-region replication
* Schema registry


