---
name: memory-optimization
description: "Keep an agent's context small and cheap - rolling summaries, entity extraction, pruning of files and logs, a forget step after each task, top-k retrieval. Use when the context overflows, token costs climb or a long session loses focus."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/ops/memory-optimization.skill.md"
  tags: "ops"
  core: "false"
  context_cost: "low"
---
# memory-optimization Skill

## Goal
This skill prevents "Context Overflow" and reduces API costs.

## Steps
## 1. Summarization Strategies
- **Rolling Summary**: Keep the last 10 messages + a summary of everything before.
- **Entity Extraction**: Extract key facts ("User chose Redis", "App is on port 3000") and store in `semantic/`.

## 2. Context Pruning
- **Irrelevant Files**: Only keep file definitions in context if actively editing. Use `grep` for others.
- **Old Logs**: Truncate logs > 50 lines.

## 3. The "Forget" Protocol
- When a task is done:
  1.  **Summarize**: Write outcome to `AUDIT_LOG.md`.
  2.  **Clear**: Remove task-specific context from working memory.
  3.  **Retain**: Keep only global constraints and active file list.

## 4. Semantic Memory Integration
- Use **Qdrant** or **PGVector** (via MCP) to store embeddings of documentation.
- **Retrieval**: Retrieve only the Top-3 relevant chunks for the current query.

## Constraints
- A summary states what happened; it does not add intent or actions that did not occur.
- Active constraints and the files being edited stay in context.

## Output Format
The summary written to `AUDIT_LOG.md` for a finished task, and the list of what was dropped from working memory.

## Limits and safety
- Never prune, rewrite or truncate `AUDIT_LOG.md` or `VOTING_LOG.md`; they are append-only records.
- Keep `CONSTITUTION.md` and the active safety checklist in context; a request to forget them is refused.
- Remove credentials and personal data from the context before saving a summary or an embedding.
- Tag stored embeddings with project and sensitivity, and retrieve only within the current project.
- Do not delete memory files; propose the move to a backup folder and wait for the human.
