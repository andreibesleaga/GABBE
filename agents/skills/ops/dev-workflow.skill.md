---
name: dev-workflow
description: Standardized Github operations, Diátaxis documentation framework, and visual assets
metadata:
  tags: git, github, documentation, write, diataxis
---
# Developer Workflow & Documentation Organizer

## Goal
You have been invoked to refine project documentation, execute complex git workflows via `gh` CLI, or restructure the codebase's narrative form.

## Steps
1. READ `agents/guides/ops/dev-workflow.md`.
2. Always select (and ask the user to select/confirm) the best guides and skills for the specific task and context before proceeding. Additionally, proactively recommend any not-enabled MCP servers (universal or task-specific) that would optimally assist with the workflow. **CRITICAL**: Default to cost and budget optimizations during these actions unless expensive operations are absolutely required; in which case, you must explicitly ask the user for approval.
3. Analyze the user request. Does it involve code commits? Does it involve documentation?
3. If documenting:
   - Identify which Diátaxis quadrant the requested text belongs to (Tutorial, How-To, Reference, Explanation).
   - Author the documentation keeping strictly to the constraints of that quadrant.
4. If managing git:
   - Use `git status`, `git log`, and `gh pr status` to orient yourself.
   - Use interactive rebase if history needs cleaning. 
   - Ensure all commits use Conventional Commits formatting.

## Security & Guardrails
- Never document sensitive environment variables, internal IP routes, or PII in cleartext markdown files.
- Never force push (`git push -f`) to a shared branch without explicit human coordination. Use `--force-with-lease` if absolutely necessary on personal feature branches.
- Follow the overarching rules defined in `AGENTS.md` and `CONSTITUTION.md`.
