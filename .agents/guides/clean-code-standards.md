# Clean Code Principles (2025 Standards)

Code is read 10x more than it is written. Optimize for readability and maintainability.

## 1. Core Principles

### SOLID
-   **S - Single Responsibility**: A class/function should have one reason to change. *Start here.*
-   **O - Open/Closed**: Open for extension, closed for modification. (Use inheritance/interfaces, don't modify core logic).
-   **L - Liskov Substitution**: Subclasses must be drop-in replacements for parents.
-   **I - Interface Segregation**: Many specific interfaces are better than one general-purpose interface.
-   **D - Dependency Inversion**: Depend on abstractions (interfaces), not concretions (classes).

### DRY (Don't Repeat Yourself)
-   Every piece of knowledge needs a single, unambiguous representation.
-   **Nuance**: duplication of *code* is sometimes verified to avoid coupling. Duplication of *business logic* is always bad.

### KISS (Keep It Simple, Stupid)
-   Avoid "clever" one-liners.
-   Explicit > Implicit.
-   Boring code is good code.

## 2. Naming Conventions
-   **Intent-Revealing**: `daysSinceCreation` > `d`.
-   **Pronounceable**: `generateTimestamp` > `genVmDtTm`.
-   **Searchable**: Avoid magic numbers. `const MAX_RETRIES = 5` > `5`.
-   **Boolean**: Prefix with `is`, `has`, `should`. `isValid` vs `valid`.

## 3. Functions
-   **Micro-Functions**: A function ideally does **one** thing.
-   **Level of Abstraction**: Statements within a function should be at the same level of abstraction.
-   **Arguments**: 0-2 is ideal. 3+ suggests you need a configuration object.

## 4. Comments
-   **Comments Lie**: Code changes, comments rarely do.
-   **Explain "Why"**: Use comments for business context or weird workarounds.
-   **Avoid "What"**: `// increment i` -> `i++` (Useless comment).

## 5. Code Smells (Refactoring Triggers)
-   **Long Method**: >20 lines. Hard to test/read.
-   **Large Class**: "God Object". Violates SRP.
-   **Primitive Obsession**: Passing `string email` everywhere instead of an `EmailAddress` objects.
-   **Feature Envy**: A method that accesses data of another object more than its own.
-   **Shotgun Surgery**: A single change requires cascading edits across many files.
