# System Scalability Guide

## 1. Introduction
Scalability is the property of a system to handle a growing amount of work by adding resources to the system. This guide defines standard approaches to both vertical and horizontal scaling.

## 2. The Scaling Axes (The Scale Cube)

### X-Axis: Horizontal Duplication (Cloning)
- **Concept:** Running multiple identical copies of the application behind a load balancer.
- **Prerequisites:** The application must be stateless. Any session data or cached data must be externalized to a shared store (like Redis or Memcached).
- **Pros:** Conceptually simple, highly available.
- **Cons:** Can be expensive if resources are underutilized; database becomes the bottleneck quickly.

### Y-Axis: Functional Decomposition (Microservices)
- **Concept:** Splitting a monolithic application into multiple, distinct, independent services based on business boundaries.
- **Pros:** Allows independent scaling of high-load features (e.g., scaling the Checkout service independently of the Catalog service).
- **Cons:** High operational complexity, data consistency challenges (requires Sagas or Event Sourcing).

### Z-Axis: Data Partitioning (Sharding)
- **Concept:** Partitioning a database where each instance handles only a subset of the data (e.g., routing users A-M to Database 1, and N-Z to Database 2).
- **Pros:** Solves infinite data growth.
- **Cons:** Extremely complex application logic; cross-shard joins are nearly impossible.

## 3. Vertical Scaling (Scale Up)
- **Concept:** Adding more CPU, RAM, or faster Disks (IOPS) to a single machine.
- **When to use:** Early in a project's lifecycle, or for systems like relational databases (up to a certain physical limit) where horizontal scaling is too expensive to re-architect.
- **Limits:** Hard physical caps on hardware; requires downtime to upgrade.

## 4. Cache Everything
Before complex scaling, utilize aggressive caching:
1.  **CDN / Edge Caching:** Static assets and full HTML pages.
2.  **API Caching:** HTTP Cache-Control headers.
3.  **App Level Caching:** Redis/Memcached for frequent DB queries.

## 5. Agentic Implementation
When working with agents on scalability problems:
- Invoke the `system-scalability` skill.
- The agent will evaluate the system and generate a `SCALABILITY_ANALYSIS_TEMPLATE.md` to map out exactly which axis is best suited to the current bottleneck.
