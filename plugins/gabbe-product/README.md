# GABBE — product (Claude Code plugin)

GABBE product skills (19): product: requirements review, user research, story maps, business case, estimation, accessibility, sustainability and change management.

GABBE (Generative Architectural Brain Base Engine) is a Markdown agentic engineering kit. This plugin carries part of its skill library in the Agent Skills format, so Claude Code can load each skill when a task matches its description. The plugin is content only: Markdown skills and the templates they name. It has no hooks, no MCP servers and no executables, and it sends nothing anywhere.

## Install

```bash
claude plugin marketplace add andreibesleaga/GABBE
claude plugin install gabbe-product@gabbe
```

Or install single skills with the skills CLI (skills.sh):

```bash
npx skills@1.9.0 add andreibesleaga/GABBE -a claude-code
```

Version 1.1.4. Generated from `agents/skills/` by `scripts/build_claude_plugin.py`; edit the sources, not these files.

## Skills

- `accessibility` — WCAG 2.2 compliance audit — keyboard navigation, screen reader testing, ARIA, color contrast
- `business-case` — Generate comprehensive business cases, ROI analysis, and strategic justification for new initiatives.
- `change-management` — Plan and drive organizational change through ADKAR, stakeholder comms cadence, training, and resistance management.
- `design-thinking` — Apply the Design Thinking process (Empathize, Define, Ideate, Prototype, Test) to solve complex user problems.
- `estimation-sizing` — Size a backlog with reference-class forecasting, probabilistic ranges, and relative estimation as ranges not commitments.
- `financial-governance` — Govern product spend with budget tracking, cost showback, unit economics, and cloud cost guardrails.
- `green-software` — Review a system for carbon and energy efficiency: architecture, region, scheduling, data retention. Use when asked to reduce the carbon footprint or to choose greener options for a design.
- `ideation-facilitation` — Facilitate divergent and convergent ideation to turn a framed problem into a ranked shortlist of concepts.
- `market-analysis` — Produce a competitor comparison matrix, SWOT, differentiation options and TAM/SAM/SOM, with a source for each figure. Use when validating a product idea against the market or comparing competitors.
- `opportunity-assessment` — Assess a product opportunity with Wardley mapping, market sizing, a North-Star metric, and RICE-ranked bets.
- `product-analytics` — Design event taxonomy, funnels and retention, rigorous A/B experiments, plus DORA and SPACE delivery metrics.
- `professional-practice` — Apply professional, ethical, and teamwork standards to software work using the ACM/IEEE-CS Code of Ethics, sound group dynamics, and clear stakeholder communication.
- `spec-analyze` — Check consistency and alignment between spec.md, plan.md, and project/TASKS.md — detect drift and mismatches
- `stakeholder-management` — Build a power/interest grid, a RACI matrix and a communication plan for the people a project affects. Use when you must align stakeholders, clarify who decides, or plan status updates.
- `sustainability-checks` — Evaluate software architecture for ESG and sustainability impact
- `systems-thinking` — Analyze complex systems, feedback loops, and leverage points. Avoid linear thinking for complex problems.
- `user-research-synthesis` — Synthesize raw user-research data into personas, a journey map, and prioritized insight statements.
- `user-story-mapping` — Produce a user story map (activities, tasks, release slices, walking skeleton) in USER_STORY_MAP_TEMPLATE.md. Use when you need to scope an MVP or order releases from a user journey.
- `visual-specs` — Process visual inputs (scans, sketches, diagrams) into structured product specifications before implementation.

## Licence

The skills are GABBE content under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), © 2026 Andrei Nicolae Besleaga. Source: https://github.com/andreibesleaga/GABBE
