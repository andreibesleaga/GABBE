---
name: clean-coder
description: Enforces Clean Code standards, identifies code smells, and ensures SOLID principles.
context_cost: medium
---
# Clean Coder Skill

## Triggers
- clean code
- code smell
- SOLID
- refactor
- quality check

## Purpose
To ensure code is readable, maintainable, and free of technical debt "smells" before it merges.

## Core Principles (2025 Standards)
1.  **SOLID**:
    -   **S**ingle Responsibility: One reason to change.
    -   **O**pen/Closed: Open for extension, closed for modification.
    -   **L**iskov Substitution: Subtypes must be substitutable.
    -   **I**nterface Segregation: Tiny, focused interfaces.
    -   **D**ependency Inversion: Depend on abstractions, not concretions.
2.  **DRY (Don't Repeat Yourself)**: Abstract logic, not just code.
3.  **KISS (Keep It Simple, Stupid)**: Simplest solution that works.
4.  **YAGNI (You Ain't Gonna Need It)**: Don't implement future features now.

## Common Code Smells
-   **Long Method**: > 20 lines (heuristic). Extract Method.
-   **Large Class**: Too many responsibilities. Extract Class.
-   **Primitive Obsession**: Using strings/ints instead of Value Objects.
-   **Feature Envy**: Using data from another object more than its own.
-   **Shotgun Surgery**: One change requires edits in many classes.

## Instructions
When reviewing or writing code:
1.  **Scan for Smells**: Check against the `clean-code-principles.md` guide.
2.  **Suggest Refactoring**: "Split this huge function into 3 smaller ones: `validateInput`, `processData`, `saveResult`."
3.  **Verify Naming**: Variables should be descriptive (`userAssumingRole` vs `u`).
4.  **Check Comments**: Code should be self-documenting. Comments explain *why*, not *what*.

## Checklist
-   [ ] Descriptive naming?
-   [ ] Functions do one thing?
-   [ ] No duplicated logic?
-   [ ] No magic numbers/strings?
-   [ ] Dependencies injected?
