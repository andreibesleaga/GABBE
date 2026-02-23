---
name: semantic-web
description: Design Semantic Web structures, Ontologies, and Meta-knowledge graphs
triggers: [design ontology, semantic web, knowledge graph architecture, rdf data model, sparql, linked data]
tags: [data, semantic, owl, rdf, knowledge-graph]
context_cost: medium
---
# semantic-web

## Goal
To architect machine-readable data structures using Semantic Web standards (RDF, OWL, SPARQL) allowing disparate enterprise systems and AI agents to share a unified, interoperable meta-knowledge graph.

## Steps
1. **Domain Modeling**: Analyze the business entities and define the formal Vocabulary/Ontology using OWL (Web Ontology Language).
2. **Data Transformation**: Design pipelines to map existing relational or document data into RDF triples (Subject-Predicate-Object).
3. **Query Interface**: Outline the SPARQL endpoints required for human and agent interaction with the Knowledge Graph.
4. **Output**: Generate the formal definitions and structure using `agents/templates/data/ONTOLOGY_TEMPLATE.md`.

## Security & Guardrails

### 1. Skill Security
- **SPARQL Injection**: Ensure the agent explicitly enforces parameterized queries when designing applications that interface with graph databases to prevent malicious graph traversals.

### 2. System Integration Security
- **Inference Leakage**: Agents must account for automated inference engines (reasoners) inadvertently linking two unclassified data points to deduce classified information (aggregation attacks).

### 3. LLM & Agent Guardrails
- **URI Standardization**: The LLM must not hallucinate random namespaces. It must use established ontologies (e.g., `schema.org`, `foaf`, `dublin core`) before inventing custom property URIs.
