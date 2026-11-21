---
name: semantic-web
description: "Ontology and RDF design with a mapping from existing data and SPARQL access. Use when data from several systems must share one vocabulary or a knowledge graph is needed."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/data/semantic-web.skill.md"
  tags: "data, semantic, owl, rdf, knowledge-graph"
  core: "false"
  context_cost: "medium"
---
# semantic-web

## Goal
To architect machine-readable data structures using Semantic Web standards (RDF, OWL, SPARQL) allowing disparate enterprise systems and AI agents to share a unified, interoperable meta-knowledge graph.

## Steps
1. **Domain Modeling**: Analyze the business entities and define the formal Vocabulary/Ontology using OWL (Web Ontology Language).
2. **Data Transformation**: Design pipelines to map existing relational or document data into RDF triples (Subject-Predicate-Object).
3. **Query Interface**: Outline the SPARQL endpoints required for human and agent interaction with the Knowledge Graph.
4. **Output**: Generate the formal definitions and structure using `agents/templates/data/ONTOLOGY_TEMPLATE.md`.

## Constraints
- Reuse existing vocabularies before defining new terms.
- Every mapping from relational or document data is written down.

## Output Format
`ONTOLOGY_TEMPLATE.md` (`agents/templates/data/`) filled in: vocabulary, mappings and SPARQL access points.

## Limits and safety
- Application queries bind parameters; no string concatenation into SPARQL.
- Check whether a reasoner could combine unclassified facts into a classified one, and list the inference risks.
- Reuse established vocabularies (`schema.org`, FOAF, Dublin Core) before inventing property URIs; do not make up namespaces.
