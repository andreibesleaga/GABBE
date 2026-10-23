# GABBE — industry (Claude Code plugin)

GABBE industry skills (5): industry standards and domains: engineering standards, healthcare FHIR, industrial IoT and telecom networks.

GABBE (Generative Architectural Brain Base Engine) is a Markdown agentic engineering kit. This plugin carries part of its skill library in the Agent Skills format, so Claude Code can load each skill when a task matches its description. The plugin is content only: Markdown skills and the templates they name. It has no hooks, no MCP servers and no executables, and it sends nothing anywhere.

## Install

```bash
claude plugin marketplace add andreibesleaga/GABBE
claude plugin install gabbe-industry@gabbe
```

Or install single skills with the skills CLI (skills.sh):

```bash
npx skills add andreibesleaga/GABBE -a claude-code
```

Version 1.1.2. Generated from `agents/skills/` by `scripts/build_claude_plugin.py`; edit the sources, not these files.

## Skills

- `engineering-standards` — Enforce academic and industry engineering standards (IEEE, ACM, ISO/IEC)
- `global-standards` — Enforce UN, ITU, and Global Open Source (OSI, OpenSSF) software standards
- `healthcare-fhir` — Design RESTful clinical data exchanges using HL7 FHIR standards
- `industrial-iot` — Architect high-throughput industrial telemetry via MQTT & OPC UA
- `telecom-networks` — Architect Telecom interfaces using TM Forum ODA, GSMA CAMARA, and eSIM standards

## Licence

The skills are GABBE content under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), © 2026 Andrei Nicolae Besleaga. Source: https://github.com/andreibesleaga/GABBE
