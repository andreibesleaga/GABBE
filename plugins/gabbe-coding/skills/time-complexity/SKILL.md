---
name: time-complexity
description: "Estimate the Big-O of functions, files or directories by static analysis with the time-complexity MCP server, and list hotspots. Use when the user asks about algorithm complexity, performance hotspots in code, or complexity before a review."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/coding/time-complexity.skill.md"
  tags: "coding, performance, analysis"
  core: "false"
  context_cost: "medium"
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

## Output Format
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

## Constraints
- Results are an estimate from the code's structure; they cannot see data sizes, caching or constants.

## Limits and safety
- `analyze_github_repo` clones a remote repository: tell the human first, and clone into a temporary directory outside the project.
- Label every result "static estimate"; confirm hot paths with a profiler before optimising.
- Do not optimise a flagged function without looking at how it is used; bounded inputs can make an O(n) function cheap in practice.
- Test a suggested rewrite (run the project's tests) before recommending it.
- On a large codebase scope the analysis to subdirectories.
