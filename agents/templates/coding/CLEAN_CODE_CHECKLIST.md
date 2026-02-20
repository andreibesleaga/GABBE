# Clean Code Checklist

Use this checklist during code reviews to ensure high quality.

## 1. Naming & Readability
- [ ] **Descriptive Names**: Variables/functions describe *what* they are/do, not *how*.
- [ ] **No Magic Numbers**: All constants are named (e.g., `MAX_RETRIES` vs `5`).
- [ ] **Boolean Flag**: Avoid boolean arguments like `process(true)`. Split into `processFast()` and `processFull()`.
- [ ] **Self-Documenting**: Comments explain *why* (intent), not *what* (syntax).

## 2. Functions & Classes
- [ ] **Small Functions**: Fit on a screen (~20 lines). One level of abstraction.
- [ ] **Single Responsibility (SRP)**: Class/function has one reason to change.
- [ ] **No Side Effects**: Functions avoid hidden state mutations.
- [ ] **Low Argument Count**: Max 3 arguments. Use an object/struct for more.

## 3. Complexity & Logic
- [ ] **Flatten Nesting**: Return early (`guard clauses`) instead of deep `if/else`.
- [ ] **DRY (Don't Repeat Yourself)**: Logic is not duplicated.
- [ ] **Positive Conditionals**: `if (isValid)` is better than `if (!isInvalid)`.

## 4. Reliability & Testing
- [ ] **Error Handling**: Errors are caught or propagated explicitly. No empty `catch`.
- [ ] **Testable**: Dependencies are injected (DI), not hardcoded.
- [ ] **Boundary Checks**: Inputs are validated.

## 5. Modern Best Practices (2025)
- [ ] **Immutable Default**: Prefer `const`/`final` over mutable variables.
- [ ] **Async/Await**: properly used; no blocking main threads.
- [ ] **Type Safety**: No `any` or loose types unless strictly necessary.
