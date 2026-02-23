# Semantic Web & Ontology Design Template

**Domain / Subject Area:** [Domain Name]
**Date:** [YYYY-MM-DD]
**Architect / Agent:** [Agent Name]
**Base Namespace URI:** `http://example.org/ontology/[domain]#`

## 1. Domain Overview
[Describe the business domain being modeled. E.g., This ontology models the relationships between employees, departments, and corporate assets to facilitate a unified knowledge graph.]

## 2. Core Concepts (Classes / OWL:Class)
| Class Name | Description | Superclass (Parent) |
| :--- | :--- | :--- |
| `Employee` | A person working for the company | `Person (foaf:Person)` |
| `Department` | A structural division of the company | `Organization (schema:Organization)` |
| `Asset` | A physical or digital resource | `Thing (owl:Thing)` |

## 3. Relationships (Object Properties / OWL:ObjectProperty)
| Property URI | Domain (Subject) | Range (Object) | Description | Inverse Property |
| :--- | :--- | :--- | :--- | :--- |
| `worksFor` | `Employee` | `Department` | Links an employee to their dept. | `hasEmployee` |
| `manages` | `Employee` | `Department` | Indicates dept. leadership | `managedBy` |
| `assignedTo` | `Asset` | `Employee` | Shows asset ownership | `ownsAsset` |

## 4. Attributes (Datatype Properties / OWL:DatatypeProperty)
| Property URI | Domain (Subject) | Data Type | Description |
| :--- | :--- | :--- | :--- |
| `employeeId` | `Employee` | `xsd:string` | Unique identifier |
| `hireDate` | `Employee` | `xsd:date` | Date of joining |
| `budget` | `Department` | `xsd:decimal`| Annual fiscal allocation |

## 5. Existing Ontology Reuse (External Namespaces)
*Do not reinvent the wheel. Map internal concepts to global standards.*
- `foaf:` (Friend of a Friend) - *Used for Person definitions.*
- `schema:` (Schema.org) - *Used for general organization logic.*
- `dc:` (Dublin Core) - *Used for document metadata.*

## 6. Logic & Rules (Reasoning)
- **Transitivity**: E.g., If `AssetA` is part of `AssetB` (hasPart), and `AssetB` is part of `AssetC`, then `AssetA` is part of `AssetC`.
- **Disjointness**: E.g., `Employee` and `Asset` are defined as `owl:disjointWith` (An entity cannot be both).

## 7. Sample RDF Output (Turtle Format)
```turtle
@prefix ex: <http://example.org/ontology/corp#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

ex:JohnDoe a ex:Employee, foaf:Person ;
    ex:employeeId "E12345" ;
    ex:worksFor ex:EngineeringDept .

ex:EngineeringDept a ex:Department .
```
