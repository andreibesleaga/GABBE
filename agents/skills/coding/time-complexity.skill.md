---
name: time-complexity
description: Estimate Big-O time complexity of code via static analysis (tree-sitter MCP).
triggers: [complexity, big-o, performance, hotspot, time complexity, analyze complexity]
tags: [coding, performance, analysis]
context_cost: medium
---
# Time Complexity Skill

## Goal
Estimate Big-O time complexity of functions, files, directories, or entire GitHub repositories using the **time-complexity-mcp** server — a static-analysis engine powered by tree-sitter. No code execution; code is parsed into ASTs and inspected.

## Prerequisites
- **MCP Server**: `time-complexity` must be configured in your MCP config (see `templates/core/MCP_CONFIG_TEMPLATE.json`).
- **Runtime**: Node.js 18+ on the host machine.
- **Optional**: `git` in PATH (required only for `analyze_github_repo`).

## Supported Languages
JavaScript (`.js`, `.mjs`, `.cjs`, `.jsx`), TypeScript (`.ts`, `.tsx`), Python (`.py`), Java (`.java`), Go (`.go`), PHP (`.php`), Dart (`.dart`), Kotlin (`.kt`, `.kts`).

## Capabilities

### 1. MCP Tools Available
| Tool | Purpose |
|---|---|
| `analyze_file` | Analyze all functions in a single source file |
| `analyze_function` | Analyze a specific named function in a file |
| `analyze_directory` | Scan an entire directory for complexity hotspots |
| `analyze_github_repo` | Clone and analyze a public GitHub repo (requires `git`) |
| `get_supported_languages` | List all file extensions the server can parse |

### 2. What It Detects
- **Loop nesting** — `for`, `while`, `do-while` with depth tracking. Constant-bound loops (e.g., `for i in range(10)`) recognized as O(1).
- **Recursion** — Linear recursion (O(n)) vs branching recursion like Fibonacci (O(2^n)).
- **Known stdlib methods** — `.sort()` as O(n log n), `.filter()`/`.map()` as O(n), `.push()`/`.pop()` as O(1). Each language has its own patterns.
- **Combined complexity** — An O(n) method inside an O(n) loop correctly reports O(n²).

### 3. Output Format
Results include per-function complexity with:
- **Function name and line range**
- **Big-O classification** (O(1), O(n), O(n log n), O(n²), O(n³), O(2^n))
- **Reasoning** (loop counts, nesting depth, recursion type)
- **Line-level annotations** (which line contributes which complexity)

## Steps

1. **Scope the analysis**
   - Single function → `analyze_function`
   - Entire file → `analyze_file`
   - Directory / codebase → `analyze_directory`
   - External repo → `analyze_github_repo`

2. **Interpret results**
   - Focus on functions with O(n²) or worse — these are performance hotspots.
   - Check line annotations to understand *where* complexity accumulates.
   - Verify constant-bound loops are correctly recognized as O(1).

3. **Act on findings**
   - Use `refactor.skill` to restructure high-complexity functions.
   - Use `performant-*.skill` for language-specific optimizations.
   - Document findings in `TIME_COMPLEXITY_REPORT_TEMPLATE.md`.

4. **Integrate into workflow**
   - Run before code reviews (`code-review.skill`) to flag regression.
   - Run on PR diffs to catch new O(n²)+ code.
   - Run on full codebase periodically to track complexity trends.

## Deliverables
- `TIME_COMPLEXITY_REPORT_TEMPLATE.md`: Structured complexity analysis with hotspots and recommendations.

## Usage Examples

### Analyze a single file
```
> Analyze the complexity of src/utils/sort.ts
```

### Analyze a specific function
```
> What's the complexity of the fibonacci function in recursion.py?
```

### Scan an entire codebase for hotspots
```
> Scan src/ for complexity hotspots
```

### Analyze a GitHub repository
```
> Analyze the complexity of facebook/react
```

### Focus on a subdirectory of a remote repo
```
> Analyze https://github.com/expressjs/express, focus on the lib/ directory
```

## Security & Guardrails

### 1. Skill Security (Time Complexity)
- **Static Analysis Only**: Code is parsed into ASTs and inspected — never evaluated, executed, or imported. No risk of running malicious code.
- **Read-Only File Access**: Source files are read for parsing. Nothing is written, modified, or deleted.
- **Scope Limiting**: When analyzing directories, be aware of repo size. For very large codebases, scope to specific subdirectories.

### 2. System Integration Security
- **Network Access (opt-in)**: The `analyze_github_repo` tool invokes `git clone` to fetch public GitHub repos. All other tools run locally with no network access. Clone URLs are restricted to HTTPS GitHub URLs only.
- **No Secrets Exposure**: The tool does not process environment variables, config files, or secrets — only source code syntax.

### 3. LLM & Agent Guardrails
- **Over-reliance on Static Analysis**: Big-O from static analysis is an *estimate*. It cannot account for runtime data distributions, caching effects, or algorithm-specific constants. Always note: "Static estimate — verify with runtime profiling for critical paths."
- **False Precision**: The tool may report O(n) for a function that is effectively O(1) due to bounded inputs in practice. Do not blindly optimize functions flagged as complex without considering real-world usage context.
- **Hallucinated Remediation**: When suggesting fixes for high-complexity functions, the agent must provide concrete, tested alternatives — not theoretical rewrites that may introduce bugs.
