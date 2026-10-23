# GABBE — data (Claude Code plugin)

GABBE data skills (5): data: pipelines, governance, database migrations, SQL optimisation and the semantic web.

GABBE (Generative Architectural Brain Base Engine) is a Markdown agentic engineering kit. This plugin carries part of its skill library in the Agent Skills format, so Claude Code can load each skill when a task matches its description. The plugin is content only: Markdown skills and the templates they name. It has no hooks, no MCP servers and no executables, and it sends nothing anywhere.

## Install

```bash
claude plugin marketplace add andreibesleaga/GABBE
claude plugin install gabbe-data@gabbe
```

Or install single skills with the skills CLI (skills.sh):

```bash
npx skills add andreibesleaga/GABBE -a claude-code
```

Version 1.1.2. Generated from `agents/skills/` by `scripts/build_claude_plugin.py`; edit the sources, not these files.

## Skills

- `data-engineering` — Design and implement data pipelines (ETL/ELT), warehousing, and analytics engineering.
- `data-governance` — Data lineage, classification (PII/Confidential), and integrity checks (checksums).
- `db-migration` — Database schema changes and migration workflow — safe, reversible, tested
- `semantic-web` — Design Semantic Web structures, Ontologies, and Meta-knowledge graphs
- `sql-optimization` — Query tuning, indexing strategies, and EXPLAIN plan analysis.

## Licence

The skills are GABBE content under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), © 2026 Andrei Nicolae Besleaga. Source: https://github.com/andreibesleaga/GABBE
