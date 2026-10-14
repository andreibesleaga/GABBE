# GABBE — security (Claude Code plugin)

GABBE security skills (21): security, privacy and AI safety: access control, secrets, cryptography, prompt-injection defence, red teaming, compliance and legal review.

GABBE (Generative Architectural Brain Base Engine) is a Markdown agentic engineering kit. This plugin carries part of its skill library in the Agent Skills format, so Claude Code can load each skill when a task matches its description. The plugin is content only: Markdown skills and the templates they name. It has no hooks, no MCP servers and no executables, and it sends nothing anywhere.

## Install

```bash
claude plugin marketplace add andreibesleaga/GABBE
claude plugin install gabbe-security@gabbe
```

Or install single skills with the skills CLI (skills.sh):

```bash
npx skills add andreibesleaga/GABBE -a claude-code
```

Version 1.1.1. Generated from `agents/skills/` by `scripts/build_claude_plugin.py`; edit the sources, not these files.

## Skills

- `access-control` — Design RBAC/ABAC models, Principle of Least Privilege, Identity Management.
- `agent-sandboxing` — Intrinsic least-privilege isolation for agents touching a local OS, shell, or filesystem — the enforcement layer behind prompt-injection-defense and ai-safety-guardrails.
- `ai-ethics-compliance` — Assessing Bias, Fairness, Transparency, and Legal (EU AI Act, GDPR).
- `ai-red-teaming` — Proactively attack your own AI and agent system to find failures before adversaries, scoring attack-success-rate and gating CI on it.
- `ai-safety-guardrails` — Security-by-design for AI (Prompt Injection defense, Hallucination checks, PII filters).
- `api-security` — Design and enforce REST/GraphQL API Security paradigms
- `backup-recovery` — Define RPO/RTO, implement PITR/Snapshots, and test restores.
- `compliance-review` — Regulatory compliance check for SOC2, PCI-DSS, GDPR, HIPAA — checklists, audit trails, access controls
- `cryptography-standards` — Enforce correct cryptographic algorithms, hashing, and TLS standards
- `dependency-security` — Managing Supply Chain Security, SBOM generation, and vulnerability patching (SCA).
- `hazard-analysis` — Conducting FMEA (Failure Mode & Effects Analysis) and identifying hazards.
- `legal-review` — Check for license compliance, PII, and IP risks
- `log-analysis` — Parsing structured logs, finding patterns in noise, and ELK/Splunk querying.
- `network-security` — Firewall rules, VPC design, TLS config, and subnet isolation.
- `privacy-audit` — PII detection, data flow mapping, GDPR/CCPA/HIPAA compliance verification
- `privacy-data-protection` — Elicit and enforce GDPR, CCPA, and general privacy by design rules
- `prompt-injection-defense` — Defend agentic systems against direct and indirect prompt injection using defense-in-depth.
- `reliability-engineering` — Designing failover patterns (Hot Standby, TMR), redundancy, and MTBF/availability calculations.
- `secrets-management` — Safe handling of API keys, Vault/AWS Secrets Manager patterns, rotation.
- `secure-architecture` — Architect systems with defense-in-depth and Zero Trust principles
- `traceability-audit` — Verifies that every PRD requirement has a linked Test Case and Code Implementation.

## Licence

The skills are GABBE content under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), © 2026 Andrei Nicolae Besleaga. Source: https://github.com/andreibesleaga/GABBE
