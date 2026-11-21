---
name: dev-workflow
description: "Handle git and GitHub tasks with the gh CLI and organise documentation with the Diataxis quadrants (tutorial, how-to, reference, explanation). Use when you restructure docs, prepare commits or a PR, or need to pick a doc type."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/ops/dev-workflow.skill.md"
  tags: "git, github, documentation, diataxis"
  core: "false"
  context_cost: "low"
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
   - If history needs cleaning, propose a rebase to the human and run it only after they confirm.
   - Ensure all commits use Conventional Commits formatting.

## Constraints
- Each document belongs to one Diataxis quadrant and keeps to its rules.
- Commits use Conventional Commits; the human decides what is committed and pushed.

## Output Format
The edited or new documentation files, or the exact git and `gh` commands proposed for the human to run.

## Limits and safety
- Do not write secret values, internal addresses or personal data into Markdown files.
- Do not force-push to a shared branch without explicit human coordination; on a personal feature branch use `--force-with-lease` only after the human confirms.
- If history needs cleaning, propose the rebase to the human and run it only after they confirm.
