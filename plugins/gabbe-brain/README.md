# GABBE — brain (Claude Code plugin)

GABBE brain skills (13): Brain Mode internals: cognitive architectures, active inference, global workspace, working and episodic memory, self-improvement.

GABBE (Generative Architectural Brain Base Engine) is a Markdown agentic engineering kit. This plugin carries part of its skill library in the Agent Skills format, so Claude Code can load each skill when a task matches its description. The plugin is content only: Markdown skills and the templates they name. It has no hooks, no MCP servers and no executables, and it sends nothing anywhere.

## Install

```bash
claude plugin marketplace add andreibesleaga/GABBE
claude plugin install gabbe-brain@gabbe
```

Or install single skills with the skills CLI (skills.sh):

```bash
npx skills add andreibesleaga/GABBE -a claude-code
```

Version 1.1.1. Generated from `agents/skills/` by `scripts/build_claude_plugin.py`; edit the sources, not these files.

## Skills

- `active-inference` — Apply Active Inference to minimize prediction error (Surprise).
- `cognitive-architectures` — Patterns from SOAR, ACT-R, and LIDA for advanced agent cognitive cycles
- `cognitive-testing` — Test cognitive and agentic loops by their mechanisms and invariants rather than by output-equality.
- `consciousness-loop` — Recursive self-reference (Strange Loop) and OODA Loop implementation.
- `episodic-consolidation` — Consolidate short-term events into long-term 'Semantic' memory.
- `epistemology-knowledge` — Implement rigorous knowledge representation and update beliefs via Active Inference
- `global-workspace` — Broadcast information across the swarm 'consciousness' (Global Workspace Theory).
- `learning-adaptation` — Mechanisms for In-Context Reinforcement Learning, Meta-Learning, and Neuroplasticity.
- `neuroscience-foundations` — Apply biological brain patterns to agent design
- `self-improvement` — Evolutionary mechanisms for the agent to rewrite its own prompts (Neuroplasticity).
- `sensory-motor` — Embodied cognition patterns for treating tools as muscles and inputs as senses.
- `sequential-thinking` — Break down complex problems into a step-by-step chain of thought for better reasoning
- `working-memory` — Manage Short-Term 'Working Memory' using Cognitive Chunking and Attention.

## Licence

The skills are GABBE content under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), © 2026 Andrei Nicolae Besleaga. Source: https://github.com/andreibesleaga/GABBE
