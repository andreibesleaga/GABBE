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
npx skills@1.9.0 add andreibesleaga/GABBE -a claude-code
```

Version 1.1.4. Generated from `agents/skills/` by `scripts/build_claude_plugin.py`; edit the sources, not these files.

## Skills

- `data-engineering` — Pipeline and warehouse design — ELT, orchestration, dbt models, idempotent loads, data quality checks and PII handling. Use when data must be moved or transformed for analytics, or when a pipeline is unreliable.
- `data-governance` — Data classification, lineage, integrity and retention rules with a deletion workflow. Use when handling personal or confidential data, or when asked where a value came from or how long data may be kept.
- `db-migration` — Schema change workflow — forward and rollback migration, compatibility check, test on a copy and safe rename or drop. Use when a table, column, index or constraint must change.
- `semantic-web` — Ontology and RDF design with a mapping from existing data and SPARQL access. Use when data from several systems must share one vocabulary or a knowledge graph is needed.
- `sql-optimization` — Query tuning plan — reading EXPLAIN ANALYZE, index design, keyset pagination, N+1 and transaction fixes. Use when a query is slow, a table scan shows up, or a database workload needs review.

## Licence

The skills are GABBE content under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), © 2026 Andrei Nicolae Besleaga. Source: https://github.com/andreibesleaga/GABBE
