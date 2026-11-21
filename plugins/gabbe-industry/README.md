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
npx skills@1.9.0 add andreibesleaga/GABBE -a claude-code
```

Version 1.1.4. Generated from `agents/skills/` by `scripts/build_claude_plugin.py`; edit the sources, not these files.

## Skills

- `engineering-standards` — Compliance review against ISO/IEC/IEEE 42010 and 12207, SWEBOK and the ACM Code of Ethics, written as a report. Use when a project must show conformance to IEEE, ACM or ISO standards.
- `global-standards` — Audit against UN SDG, ITU-T and open source (OSI, OpenSSF) requirements, written as a report. Use when a public-sector or open source project needs a standards or licence check.
- `healthcare-fhir` — FHIR resource mapping, profiles and REST interactions for clinical data exchange. Use when integrating with an electronic health record system or building a healthcare API.
- `industrial-iot` — Edge-to-cloud design for industrial telemetry with Purdue levels, OPC UA, MQTT and cloud ingestion. Use when factory equipment, PLC or SCADA data must reach cloud systems.
- `telecom-networks` — Telecom API and architecture map using TM Forum ODA and Open APIs, GSMA CAMARA and eSIM provisioning. Use when building for carrier BSS or OSS systems or exposing network capabilities to developers.

## Licence

The skills are GABBE content under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), © 2026 Andrei Nicolae Besleaga. Source: https://github.com/andreibesleaga/GABBE
