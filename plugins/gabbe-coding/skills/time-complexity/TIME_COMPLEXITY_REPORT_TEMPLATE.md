# Time Complexity Analysis Report: [Project Name]

**Version**: 1.0
**Date**: [YYYY-MM-DD]
**Scope**: [File / Directory / Repository analyzed]
**Tool**: time-complexity-mcp (tree-sitter static analysis)

## 1. Summary

| Metric | Value |
|---|---|
| Files analyzed | [N] |
| Total functions | [N] |
| O(1) | [N] |
| O(n) | [N] |
| O(n log n) | [N] |
| O(n²) | [N] |
| O(n³) | [N] |
| O(2^n) | [N] |

## 2. Hotspots (Top 5 Most Complex Functions)

| # | File | Function | Lines | Complexity | Reasoning |
|---|---|---|---|---|---|
| 1 | [path/to/file] | [functionName] | [L1–L2] | [O(?)] | [e.g., 2 nested variable-bound loops] |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

## 3. Detailed Findings

### [File: path/to/file.ext]

#### [functionName] (lines [L1]–[L2]): [O(?)]
**Detection**: [e.g., "Found 2 variable-bound loops, max nesting depth: 2"]
**Line Annotations**:
- Line [N]: [O(?)] — [description, e.g., "for_statement loop (nesting depth: 1)"]
- Line [N]: [O(?)] — [description]

**Impact**: [HIGH / MEDIUM / LOW] — [Justification, e.g., "Called on every API request with unbounded input"]

**Recommendation**:
- [Specific fix, e.g., "Replace linear search with Set lookup to reduce from O(n²) to O(n)"]

---

## 4. Comparison (Before / After)

*Fill this section when re-running analysis after refactoring.*

| Function | Before | After | Improvement |
|---|---|---|---|
| [functionName] | [O(n²)] | [O(n)] | [Quadratic → Linear] |

## 5. Caveats

- Static analysis estimates — does not account for runtime data distributions or caching.
- Constant-bound loops are treated as O(1).
- Inter-procedural complexity (function A calling function B) may not be fully combined.
- Verify critical hotspots with runtime profiling (e.g., `Py-Spy`, `perf`, Chrome DevTools).
