# Semantic Web & Meta-Knowledge Guide

## 1. Introduction
The Semantic Web (Web 3.0 W3C standards, not to be confused with crypto-Web3) provides a common framework that allows data to be shared and reused across application, enterprise, and community boundaries. It enables the creation of Enterprise Knowledge Graphs (EKGs) that machines and AI agents can query and reason over.

## 2. Core Technologies
Rather than storing data in isolated tables (Relational DBs) or documents (NoSQL), Semantic Web technologies store data as a graph of facts.

- **RDF (Resource Description Framework)**: The base data model. Data is stored in "Triples" defining a Subject, Predicate, and Object (e.g., `Employee_123` -> `worksFor` -> `Engineering`).
- **OWL (Web Ontology Language)**: The schema layer. It defines classes, properties, and relationships. It allows for logical deduction (e.g., if X is a Manager of Y, and Y works in Z, then X represents Z).
- **SPARQL**: The query language for RDF graphs (similar to SQL for relational data).

## 3. Why Use It?
1. **Data Silo Elimination**: Merging two relational databases requires complex ETL schemas. Merging two RDF graphs simply requires joining the identical URIs.
2. **AI Interoperability**: AI Agents (via MCP or A2A) require context. A semantic knowledge graph provides perfectly clean, relationship-mapped context for LLMs, eliminating hallucination in RAG deployments (GraphRAG).
3. **Inference**: Reasoners can infer new facts without them being explicitly stated in the database.

## 4. Ontological Design Principles
- **Reusability**: Never invent a new property if an existing standard exists. Use `schema.org` for common entities (Person, Organization), `FOAF` for social structures, and `Dublin Core` for document metadata.
- **URIs as Identifiers**: Every entity and property is a Unique Resource Identifier (URI), ensuring global uniqueness.

## 5. Agentic Implementation
Invoke the `semantic-web` skill when designing complex AI knowledge retrieval mechanisms or when unifying large enterprise datasets. Unstructured data (text/PDFs) is first parsed by an agent, transformed into RDF triples based on the `ONTOLOGY_TEMPLATE.md`, and stored in a Triplestore/Graph Database (like Neo4j or Amazon Neptune).
