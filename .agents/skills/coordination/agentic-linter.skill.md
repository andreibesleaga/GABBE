---
name: agentic-linter
description: Enforce architecture layer boundaries defined in AGENTS.md — detect and fix import violations
triggers: [architecture lint, boundary, import violation, layer check, ADD, circular dependency, dependency check]
context_cost: medium
---

# Agentic Linter Skill

## Goal
Enforce the architectural layer rules defined in AGENTS.md Section 3. Act as a semantic linter that detects boundary violations and proposes concrete fixes using the Dependency Inversion Principle.

## Steps

1. **Load architecture rules from AGENTS.md**
   - Read AGENTS.md Section 3 (Architecture Rules / Layer Definitions)
   - Map each layer to its allowed imports
   - Note any project-specific forbidden patterns

2. **Run import graph analysis**

   **For TypeScript/JavaScript (Node.js):**
   ```bash
   # Check circular dependencies
   npx madge --circular --extensions ts,js src/

   # Check layer violations (if .dependency-cruiser.cjs configured)
   npx dependency-cruiser --config .dependency-cruiser.cjs src/
   ```

   **For PHP/Laravel:**
   ```bash
   # Deptrac for DDD layer enforcement
   vendor/bin/deptrac analyse --config-file deptrac.yaml
   ```

   **For Python/FastAPI:**
   ```bash
   # Import Linter (layer rules defined in .import-linter.ini)
   lint-imports
   ```

   **Manual check (if tools not installed):**
   - Read each file in inner layers (domain, application)
   - Scan imports for references to outer layers (infrastructure, HTTP, database)

3. **Classify violations**
   - **Circular dependency:** A → B → A (any length cycle)
   - **Layer inversion:** Inner layer imports outer layer (domain imports infrastructure)
   - **God object:** Class > 500 lines or > 20 public methods
   - **Framework leak:** Domain entity imports from web framework or ORM

4. **For each violation, propose a concrete fix**

   **Circular dependency fix:**
   ```typescript
   // PROBLEM: UserService imports OrderService, OrderService imports UserService

   // SOLUTION: Extract shared interface
   // src/domain/ports/user-query-port.ts
   export interface IUserQueryPort {
     findById(id: string): Promise<User | null>;
   }
   // UserService implements IUserQueryPort
   // OrderService depends on IUserQueryPort (not UserService directly)
   ```

   **Layer inversion fix (Dependency Inversion Principle):**
   ```typescript
   // PROBLEM: domain/User.ts imports from infrastructure/PrismaClient

   // SOLUTION: Create interface in inner layer
   // src/domain/ports/user-repository.ts
   export interface IUserRepository {
     save(user: User): Promise<void>;
     findById(id: string): Promise<User | null>;
   }

   // src/infrastructure/prisma-user-repository.ts
   // implements IUserRepository (infrastructure depends on domain, not reverse)
   ```

5. **Apply fixes** (if instructed, or propose for human review)
   - Create the interface file in the inner layer
   - Update the outer layer implementation to implement the interface
   - Update dependency injection wiring in main/composition root
   - Run tests to verify nothing broke

6. **Re-run analysis** — confirm violations are resolved

7. **Generate configuration file** (if requested)
   ```javascript
   // .dependency-cruiser.cjs — generated configuration
   module.exports = {
     forbidden: [
       {
         name: 'domain-not-to-infrastructure',
         severity: 'error',
         from: { path: '^src/domain' },
         to: { path: '^src/infrastructure' }
       },
       {
         name: 'no-circular',
         severity: 'error',
         from: {},
         to: { circular: true }
       }
     ]
   };
   ```

## Constraints
- Do not just report violations — always provide a concrete fix proposal
- Fix proposals must not change the external behavior of the code
- New interface files should be placed in the innermost layer that uses them
- After applying fixes, all existing tests must still pass

## Output Format
Violation report with file:line references + concrete fix for each. Run summary: "[N] violations found, [N] fixed, [N] proposed for review."
