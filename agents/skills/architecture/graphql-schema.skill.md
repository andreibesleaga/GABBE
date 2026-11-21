---
name: graphql-schema
description: Design of a GraphQL schema — nullability, DataLoader batching, cursor pagination, depth and cost limits, federation. Use when writing or reviewing a GraphQL API or fixing N+1 resolvers.
triggers: [graphql schema, graphql, dataloader, n+1 resolvers, apollo federation, relay pagination]
tags: [architecture]
role: eng-api
context_cost: low
---
# graphql-schema Skill

## Goal
This skill prevents "Graph Spaghetti" and ensuring performant Graph APIs.

## Steps
## 1. Schema Design
- **Consumption-First**: Design for the UI needs, not the DB schema.
- **Naming**: `User.posts` (Good), `User.getPosts` (Bad - it's a field, not a method).
- **Nullability**:
  - Default to **Nullable** for fields (resilience: if one field fails, partial data returns).
  - Use **Non-Null (!)** only for IDs and essential arguments.

## 2. N+1 Problem (The Graph Killer)
- **Scenario**: Querying `users { posts { comments } }`.
- **Solution**: **DataLoader** pattern.
  - Batches IDs from multiple resolvers.
  - Runs *one* DB query: `SELECT * FROM posts WHERE user_id IN (1, 2, 3)`.
  - Distributes results back to resolvers.

## 3. Pagination
- Avoid `offset`/`limit`.
- Use **Relay Connection Specification** (Cursor-based):
  ```graphql
  users(first: 10, after: "cursor") {
    edges {
      node { name }
      cursor
    }
    pageInfo { hasNextPage }
  }
  ```

## 4. Security
- **Depth Limiting**: Block queries deeper than 5 levels (prevent cyclic recursion DoS).
- **Cost Analysis**: Assign points to fields. Block query if Cost > 1000.
- **Introspection**: Disable in Production.

## 5. Federation (Apollo)
- Use when splitting Graph across microservices.
- **Entity**: A type shared across subgraphs (`@key(fields: "id")`).
- **Gateway**: Composes the Supergraph.

## Constraints
- Design for what the UI needs, not for the database schema.
- Batch resolvers with DataLoader; no offset pagination.

## Output Format
The schema in SDL with notes on resolvers, limits and federation.

## Limits and safety
- The design carries depth, cost and pagination limits, and introspection is off in production; confirm the production setting with the human.
- Authorization sits in the field resolvers, not only at the HTTP endpoint; a sensitive field the user may not see returns an authorization error or is hidden, never `null`.
- Never put fields such as `passwordHash` into the schema.
- Mutations take idempotency keys, and rate limits count every mutation in a batched request.
- In federation, subgraphs authenticate the gateway and are not reachable directly.
