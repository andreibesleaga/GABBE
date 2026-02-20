#!/usr/bin/env bash
# setup-context.sh — Context Unification Script
# Run once per project to wire up agents/ kit for all AI coding tools.
#
# Usage: chmod +x agents/setup-context.sh && agents/setup-context.sh
#
# What this does:
#   1. Symlinks AGENTS.md -> all tool-specific context files
#   2. Symlinks agents/skills/ -> tool-specific skill directories
#   3. Creates agents/memory/ directory structure
#   4. Initializes starter memory files
#   5. Creates .gitignore entries for local-only files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd "${AGENTS_DIR}/.." && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  Agentic Engineering Kit — Setup    ${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Step 1: Symlink AGENTS.md to all AI tool context locations
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${YELLOW}Step 1: Unifying agent context (AGENTS.md -> all tools)${NC}"

# Claude Code: .claude/CLAUDE.md
if [ ! -d "${PROJECT_ROOT}/.claude" ]; then
  mkdir -p "${PROJECT_ROOT}/.claude"
fi
if [ -L "${PROJECT_ROOT}/.claude/CLAUDE.md" ]; then
  rm "${PROJECT_ROOT}/.claude/CLAUDE.md"
fi
if [ ! -f "${PROJECT_ROOT}/.claude/CLAUDE.md" ]; then
  # Relative path: from .claude/ to agents/AGENTS.md
  ln -sf "../agents/AGENTS.md" "${PROJECT_ROOT}/.claude/CLAUDE.md"
  echo -e "  ${GREEN}✓${NC} .claude/CLAUDE.md -> ../agents/AGENTS.md"
else
  echo -e "  ${YELLOW}!${NC} .claude/CLAUDE.md already exists (not a symlink — skipped)"
fi

# Cursor: .cursorrules
if [ -L "${PROJECT_ROOT}/.cursorrules" ]; then
  rm "${PROJECT_ROOT}/.cursorrules"
fi
if [ ! -f "${PROJECT_ROOT}/.cursorrules" ]; then
  # Relative path: from root to agents/AGENTS.md
  ln -sf "agents/AGENTS.md" "${PROJECT_ROOT}/.cursorrules"
  echo -e "  ${GREEN}✓${NC} .cursorrules -> agents/AGENTS.md"
else
  echo -e "  ${YELLOW}!${NC} .cursorrules already exists (not a symlink — skipped)"
fi

# Gemini / Antigravity: .gemini/settings.json (agent_instructions field)
# Note: We create a wrapper settings.json that references AGENTS.md
if [ ! -d "${PROJECT_ROOT}/.gemini" ]; then
  mkdir -p "${PROJECT_ROOT}/.gemini"
fi
if [ ! -f "${PROJECT_ROOT}/.gemini/settings.json" ]; then
  cat > "${PROJECT_ROOT}/.gemini/settings.json" << 'EOF'
{
  "agent_instructions_file": "../agents/AGENTS.md",
  "skills_directory": "../agents/skills/",
  "notes": "Managed by agents/setup-context.sh — do not edit manually"
}
EOF
  echo -e "  ${GREEN}✓${NC} .gemini/settings.json created (references agents/AGENTS.md)"
else
  echo -e "  ${YELLOW}!${NC} .gemini/settings.json already exists (skipped)"
fi

# Codex / OpenAI: .codex/AGENTS.md
if [ ! -d "${PROJECT_ROOT}/.codex" ]; then
  mkdir -p "${PROJECT_ROOT}/.codex"
fi
if [ -L "${PROJECT_ROOT}/.codex/AGENTS.md" ]; then
  rm "${PROJECT_ROOT}/.codex/AGENTS.md"
fi
if [ ! -f "${PROJECT_ROOT}/.codex/AGENTS.md" ]; then
  # Relative path: from .codex/ to agents/AGENTS.md
  ln -sf "../agents/AGENTS.md" "${PROJECT_ROOT}/.codex/AGENTS.md"
  echo -e "  ${GREEN}✓${NC} .codex/AGENTS.md -> ../agents/AGENTS.md"
else
  echo -e "  ${YELLOW}!${NC} .codex/AGENTS.md already exists (not a symlink — skipped)"
fi

# GitHub Copilot: .github/copilot-instructions.md
if [ ! -d "${PROJECT_ROOT}/.github" ]; then
  mkdir -p "${PROJECT_ROOT}/.github"
fi
if [ -L "${PROJECT_ROOT}/.github/copilot-instructions.md" ]; then
  rm "${PROJECT_ROOT}/.github/copilot-instructions.md"
fi
if [ ! -f "${PROJECT_ROOT}/.github/copilot-instructions.md" ]; then
  # Relative path: from .github/ to agents/AGENTS.md
  ln -sf "../agents/AGENTS.md" "${PROJECT_ROOT}/.github/copilot-instructions.md"
  echo -e "  ${GREEN}✓${NC} .github/copilot-instructions.md -> ../agents/AGENTS.md"
else
  echo -e "  ${YELLOW}!${NC} .github/copilot-instructions.md already exists (not a symlink — skipped)"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Step 2: Symlink agents/skills/ to tool-specific skill directories
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${YELLOW}Step 2: Wiring skills directories${NC}"

# Claude Code: .claude/skills/
if [ ! -d "${PROJECT_ROOT}/.claude" ]; then
  mkdir -p "${PROJECT_ROOT}/.claude"
fi
if [ -L "${PROJECT_ROOT}/.claude/skills" ]; then
  rm "${PROJECT_ROOT}/.claude/skills"
fi
if [ ! -d "${PROJECT_ROOT}/.claude/skills" ]; then
  # Relative path: from .claude/ to agents/skills/
  ln -sf "../agents/skills" "${PROJECT_ROOT}/.claude/skills"
  echo -e "  ${GREEN}✓${NC} .claude/skills/ -> ../agents/skills/"
else
  echo -e "  ${YELLOW}!${NC} .claude/skills/ already exists (not a symlink — skipped)"
fi

# Antigravity / Gemini: .agent/skills/
if [ ! -d "${PROJECT_ROOT}/.agent" ]; then
  mkdir -p "${PROJECT_ROOT}/.agent"
fi
if [ -L "${PROJECT_ROOT}/.agent/skills" ]; then
  rm "${PROJECT_ROOT}/.agent/skills"
fi
if [ ! -d "${PROJECT_ROOT}/.agent/skills" ]; then
  # Relative path: from .agent/ to agents/skills/
  ln -sf "../agents/skills" "${PROJECT_ROOT}/.agent/skills"
  echo -e "  ${GREEN}✓${NC} .agent/skills/ -> ../agents/skills/"
else
  echo -e "  ${YELLOW}!${NC} .agent/skills/ already exists (not a symlink — skipped)"
fi

# Cursor and VS Code: Compile skills
if [ -f "${AGENTS_DIR}/scripts/compile_skills.py" ]; then
    echo -e "${YELLOW}Compiling skills for Cursor and VS Code...${NC}"
    
    # Cursor
    python3 "${AGENTS_DIR}/scripts/compile_skills.py" \
        --platform "Cursor" \
        --skills-dir "${AGENTS_DIR}/skills" \
        --target-dir "${PROJECT_ROOT}/.cursor/rules" \
        --project-root "${PROJECT_ROOT}"

    # VS Code / Copilot
    python3 "${AGENTS_DIR}/scripts/compile_skills.py" \
        --platform "VS Code" \
        --skills-dir "${AGENTS_DIR}/skills" \
        --target-dir "${PROJECT_ROOT}/.github/skills" \
        --project-root "${PROJECT_ROOT}"
else
    echo -e "${RED}x Warning: compile_skills.py not found. Skipping Cursor/VS Code skill generation.${NC}"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Step 3: Create agents/memory/ directory structure
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${YELLOW}Step 3: Initializing agents/memory/ directory structure${NC}"

MEMORY_DIR="${AGENTS_DIR}/agents/memory"
mkdir -p "${MEMORY_DIR}/episodic/SESSION_SNAPSHOT"
mkdir -p "${MEMORY_DIR}/semantic"
echo -e "  ${GREEN}✓${NC} agents/memory/episodic/SESSION_SNAPSHOT/ created"
echo -e "  ${GREEN}✓${NC} agents/memory/semantic/ created"

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Step 4: Initialize starter memory files (if not already present)
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${YELLOW}Step 4: Initializing memory files${NC}"

# PROJECT_STATE.md
if [ ! -f "${MEMORY_DIR}/PROJECT_STATE.md" ]; then
  cat > "${MEMORY_DIR}/PROJECT_STATE.md" << 'EOF'
# PROJECT_STATE.md — Master Project State

> Updated by: sdlc-checkpoint.skill
> Read by: session-resume.skill, loki-mode.skill

## Current SDLC Phase

```
Phase: S00_INITIALIZED
Status: NOT_STARTED
Last checkpoint: [DATE]
Last checkpoint by: [agent/human]
```

## SDLC Progress

| Phase | Status | Started | Completed | Gate Criteria Met |
|---|---|---|---|---|
| S01 Requirements | NOT_STARTED | — | — | — |
| S02 Design | NOT_STARTED | — | — | — |
| S03 Specification | NOT_STARTED | — | — | — |
| S04 Tasks | NOT_STARTED | — | — | — |
| S05 Implementation | NOT_STARTED | — | — | — |
| S06 Testing | NOT_STARTED | — | — | — |
| S07 Security | NOT_STARTED | — | — | — |
| S08 Review | NOT_STARTED | — | — | — |
| S09 Staging | NOT_STARTED | — | — | — |
| S10 Production | NOT_STARTED | — | — | — |

## Current Blockers

_None yet_

## Next Actions

1. Fill in AGENTS.md placeholders for this project
2. Run spec-writer.skill to create initial PRD.md

## Open Human Decisions

_None pending_

## Last Test Status

```
Last run: never
Pass: —  Fail: —  Skip: —
Coverage: —
```

## Key Artifacts

```
PRD.md:        does not exist
SPEC.md:       does not exist
PLAN.md:       does not exist
project/tasks.md:      does not exist
```
EOF
  echo -e "  ${GREEN}✓${NC} agents/memory/PROJECT_STATE.md initialized"
else
  echo -e "  ${YELLOW}!${NC} agents/memory/PROJECT_STATE.md already exists (skipped)"
fi

# AUDIT_LOG.md
if [ ! -f "${MEMORY_DIR}/AUDIT_LOG.md" ]; then
  cat > "${MEMORY_DIR}/AUDIT_LOG.md" << 'EOF'
# AUDIT_LOG.md — Project Audit Trail

> APPEND ONLY — never delete or modify existing entries.
> Updated by: audit-trail.skill
> Read by: session-resume.skill (last 50 entries), integrity-check.skill

## Log Format

| Timestamp | Session | Agent/Human | Action Type | Description | Outcome | References |
|---|---|---|---|---|---|---|

## Action Types
- DECISION — a choice was made between options
- PHASE_TRANSITION — SDLC phase changed
- TASK_DONE — a task was completed
- TASK_BLOCKED — a task is stuck, human needed
- QUALITY_GATE — gate pass/fail result
- SECURITY_FINDING — security issue found
- ADR_CREATED — architecture decision recorded
- HUMAN_ESCALATION — agent escalated to human
- SELF_HEAL_ATTEMPT — agent tried to fix itself
- RESEARCH_FINDING — authoritative source found
- ERROR — unexpected error encountered
- ROLLBACK — change was reverted

## Log Entries

| Timestamp | Session | Agent/Human | Action Type | Description | Outcome | References |
|---|---|---|---|---|---|---|
| INIT | S00 | setup-context.sh | PHASE_TRANSITION | Kit initialized | SUCCESS | README_FULL.md |

EOF
  echo -e "  ${GREEN}✓${NC} agents/memory/AUDIT_LOG.md initialized"
else
  echo -e "  ${YELLOW}!${NC} agents/memory/AUDIT_LOG.md already exists (skipped)"
fi

# CONTINUITY.md
if [ ! -f "${MEMORY_DIR}/CONTINUITY.md" ]; then
  cat > "${MEMORY_DIR}/CONTINUITY.md" << 'EOF'
# CONTINUITY.md — Project Memory: Past Failures & Lessons

> Read this at the START of every RARV Reason phase.
> Prevents repeating failed approaches across sessions.
> Updated by: self-heal.skill (on escalation), audit-trail.skill

## How to Add Entries

When an approach fails after multiple attempts, add an entry:

```markdown
### [DATE] — [Brief title of the failure]
**Context:** What were you trying to do?
**Approach tried:** What did you try?
**Why it failed:** Root cause
**Resolution:** What actually worked (or "unresolved — awaiting human decision")
**Tags:** [library-conflict | type-error | test-failure | architecture | security | performance]
```

## Past Failures & Lessons

_No entries yet. Entries are added automatically by self-heal.skill on escalation._

EOF
  echo -e "  ${GREEN}✓${NC} agents/memory/CONTINUITY.md initialized"
else
  echo -e "  ${YELLOW}!${NC} agents/memory/CONTINUITY.md already exists (skipped)"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Step 5: Update .gitignore
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${YELLOW}Step 5: Updating .gitignore${NC}"

GITIGNORE="${PROJECT_ROOT}/.gitignore"

add_to_gitignore() {
  local entry="$1"
  local comment="$2"
  if ! grep -qF "$entry" "$GITIGNORE" 2>/dev/null; then
    echo "" >> "$GITIGNORE"
    echo "# $comment" >> "$GITIGNORE"
    echo "$entry" >> "$GITIGNORE"
    echo -e "  ${GREEN}✓${NC} Added $entry to .gitignore"
  else
    echo -e "  ${YELLOW}!${NC} $entry already in .gitignore (skipped)"
  fi
}

# Create .gitignore if it doesn't exist
if [ ! -f "$GITIGNORE" ]; then
  touch "$GITIGNORE"
  echo -e "  ${GREEN}✓${NC} Created .gitignore"
fi

add_to_gitignore ".env" "Environment secrets"
add_to_gitignore ".env.local" "Local environment overrides"
add_to_gitignore ".env.*.local" "Environment-specific local overrides"

# Note: we do NOT gitignore agents/memory/ — project memory should be committed
# to preserve continuity across team members and CI/CD environments.
# Individual developers may add local-only entries to .git/info/exclude.

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Optional: Global skills symlink (for cross-project availability)
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${YELLOW}Optional: Global skills setup${NC}"
echo -e "  To make these skills available globally across all projects, run:"
echo -e "  ${BLUE}mkdir -p ~/.claude/skills && ln -sf ${AGENTS_DIR}/skills/* ~/.claude/skills/${NC}"
echo -e "  Or for Gemini/Antigravity:"
echo -e "  ${BLUE}mkdir -p ~/.agent/skills && ln -sf ${AGENTS_DIR}/skills/* ~/.agent/skills/${NC}"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Done
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  Context Unification Complete!      ${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "Kit is ready. Next steps:"
echo -e "  1. ${BLUE}Fill in AGENTS.md placeholders${NC} for your project"
echo -e "  2. ${BLUE}Adapt CONSTITUTION.md${NC} — keep universal articles, add project-specific ones"
echo -e "  3. Tell your AI agent: ${BLUE}\"Read AGENTS.md and start with spec-writer skill\"${NC}"
echo ""
echo -e "Files created/linked:"
echo -e "  .claude/CLAUDE.md    -> agents/AGENTS.md"
echo -e "  .cursorrules         -> agents/AGENTS.md"
echo -e "  .codex/AGENTS.md     -> agents/AGENTS.md"
echo -e "  .github/copilot-instructions.md -> agents/AGENTS.md"
echo -e "  .gemini/settings.json (references agents/AGENTS.md)"
echo -e "  .claude/skills/      -> agents/skills/"
echo -e "  .agent/skills/       -> agents/skills/"
echo -e "  agents/memory/ (initialized)"
echo ""
