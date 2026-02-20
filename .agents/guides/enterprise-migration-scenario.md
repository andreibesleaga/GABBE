# Enterprise Migration Scenario (Guide)

This guide documents the common workflow for using GABBE to modernize or migrate a legacy enterprise system to a microservices architecture.

## 1. Initial Assessment (Phase 0)

Start by instantiating the kit and running a discovery phase.
**Prompt:**
> "Activate Loki Mode. Goal: Analyze the massive monolithic application in `src/legacy` and create a migration plan to split it into bounded contexts."

### Expected Output:
- The agent will use `systems-thinking.skill` to map the current state.
- It will invoke `legacy-modernization.skill` to identify domain boundaries.
- It will generate `PLAN.md` with an initial C4 container diagram proposing microservices (e.g., Auth Service, Inventory Service, Order Service).

## 2. Setting Architectural Governance

Once the `PLAN.md` is approved, enforce architectural governance to prevent coupling between the new boundaries.
**Prompt:**
> "Use the architecture-governance skill. Define deptrac or ArchUnit rules for the new microservices to ensure the UI layer never directly queries the database layer, and services communicate only via the Event Bus."

### Expected Output:
- Creation of `deptrac.yaml` (if PHP) or equivalent rules (e.g., `.eslintrc` boundary config if node).
- The `agentic-linter.skill` will enforce these on all subsequent PRs.

## 3. The Strangler Fig Pattern Execution

Migrate one feature at a time using the Strangler Fig pattern.

**Prompt for a single feature:**
> "Use the strangler-fig pattern. We are extracting the 'User Authentication' module from the monolith. Read the existing legacy routes. Create a new microservice in `services/auth` mapped to the identical API contract."

### Execution Flow:
1.  **Spec:** Agent writes OpenAPI spec for the new `/api/v2/auth`.
2.  **Implementation:** Agent uses `tdd-cycle.skill` to build the new service.
3.  **Routing:** Agent updates the API Gateway (e.g., Nginx, Traefik) to route `/auth` traffic to the new service while routing everything else to the monolith.

## 4. Dual-Write Data Migration

If the database must also be split, the agent will guide a dual-write strategy.

**Prompt:**
> "Design a dual-write migration strategy for the 'Orders' database table. Propose the database schema for the new microservice and write the migration script."

### Execution Flow:
1.  **Schema:** Agent defines `schema.sql` for the new `orders_db`.
2.  **Sync:** Agent implements an event listener on the monolith (e.g., CDC using Debezium) to sync old DB writes to the new DB.
3.  **Read Switch:** Once data is verified, Agent modifies the frontend to read from the new microservice APIs.

## 5. Security and Compliance

Enterprise environments demand rigorous compliance.
**Prompt:**
> "Run a full compliance-review skill for SOC2 and GDPR on the newly extracted Auth microservice."

### Expected Output:
- The agent runs `privacy-audit.skill` to check for PII logging.
- The agent fills out the `SECURITY_CHECKLIST.md` confirming encryption in transit and at rest.
