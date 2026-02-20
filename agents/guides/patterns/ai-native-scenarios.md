# Modern AI-Native Engineering Scenarios

This guide explores advanced "in the wild" use cases where GABBE 2.0 excels, leveraging the full power of Loki Mode and Brain Mode.

## 1. Vibe-to-Code (Prototype to Production)

**The Scenario:** You've used an AI to quickly "vibe-code" a beautiful landing page or dashboard, but now you need to turn it into a production-grade application with types, tests, and clean architecture.

### Workflow:
1. **Prompt:**
   > "Use the vibe-coding skill to analyze my existing prototype in `src/vibe`. Now, use the clean-coder and architecture-design skills to refactor it into a Clean Architecture (Domain, Application, Adapters) with 100% test coverage using Vitest."
2. **Key Steps:**
   - **Extract Logic:** The agent separates UI-only "vibe" code from business logic.
   - **Apply Types:** Moving from `any` or loose JS to strict TypeScript.
   - **Add Gates:** Setting up `ESLint` and `Pretier` to enforce the style discovered during the "vibe" phase.

---

## 2. Autonomous Security Fixing (Patching at Velocity)

**The Scenario:** Your CI pipeline (via Semgrep or Snyk MCP) detects 5 critical vulnerabilities in a large legacy codebase. You want the agent to fix them autonomously without human hand-holding for every line.

### Workflow:
1. **Prompt:**
   > "Run the safety-scan skill on the entire codebase. For every vulnerability found, invoke the self-heal skill. Apply fixes that adhere to OWASP Top 10 standards. Only escalate to me if a fix requires a breaking architecture change."
2. **Key Steps:**
   - **Triage:** Agent categorizes vulnerabilities (e.g., SQL Injection, XSS).
   - **TDD Fix:** Agent writes a failing security test that reproduces the vulnerability, then writes the fix.
   - **Regression Check:** Agent runs the full test suite to ensure the security fix didn't break functionality.

---

## 3. Agentic Database Refactoring (Scaling Schema)

**The Scenario:** You started with a simple flat-file database or a non-normalized SQLite table. Now you need to migrate to a normalized PostgreSQL schema with relations and indices.

### Workflow:
1. **Prompt:**
   > "Use the data-engineering and sql-optimization skills. Analyze my current `database.sqlite` schema. Design a normalized PostgreSQL schema that supports [describe new relationships]. Generate a Sequelize/Prisma migration and the data-porting script."
2. **Key Steps:**
   - **Normalization:** Agent identifies redundancy and creates 3NF relations.
   - **Migration Logic:** Agent generates the `UP` and `DOWN` migration files.
   - **Verification:** Agent spins up a local Postgres container (via docker-dev.skill) and runs the migration to verify it passes.

---

## 4. Multi-Agent Competitive Design (Brain Mode)

**The Scenario:** You have a high-stakes architectural decision (e.g., GraphQL vs REST for a high-traffic API) and want the agent to simulate a debate between two विशेषज्ञ (specialist) personas.

### Workflow:
1. **Prompt:**
   > "Activate Brain Mode. Goal: Decide between GraphQL and REST for our mobile backend. Run a competitive simulation between `arch-architect` (GraphQL proponent) and `ops-sre` (REST proponent). Present a weighted decision matrix in `ARCHITECTURE_DECISION_MATRIX.md`."
2. **Key Steps:**
   - **Debate:** The orchestrator runs 2-3 passes of debate, synthesizing the pros/cons.
   - **Simulation:** Agent creates minimal benchmarks for both approaches.
   - **Conclusion:** A final recommendation based on the project's specific constraints (e.g., bandwidth, latency).

---

## 5. Knowledge Distillation (Legacy to Modern)

**The Scenario:** You are inheriting a project with zero documentation but 10,000 lines of complex code. You need to understand it *today*.

### Workflow:
1. **Prompt:**
   > "Use the research and documentation skills. Recursively analyze the `src/` directory. Create a high-level README_INTERNAL.md explaining the domain model, a C4 component diagram of the wiring, and a list of all known 'gotchas' in `agents/memory/semantic/PROJECT_KNOWLEDGE.md`."
2. **Key Steps:**
   - **Ingestion:** Agent reads the code for patterns (not just comments).
   - **Mapping:** Agent uses `diagramming.skill` to visualize the hidden relationships.
   - **Crystallization:** Saving findings in the permanent memory layer for future sessions.
