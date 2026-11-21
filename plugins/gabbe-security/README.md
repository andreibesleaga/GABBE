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
npx skills@1.9.0 add andreibesleaga/GABBE -a claude-code
```

Version 1.1.4. Generated from `agents/skills/` by `scripts/build_claude_plugin.py`; edit the sources, not these files.

## Skills

- `access-control` — Design roles and permissions with least privilege and review authorisation checks. Use when adding roles, permissions or admin features, or when auditing who can access what.
- `agent-sandboxing` — Intrinsic least-privilege isolation for agents touching a local OS, shell, or filesystem — the enforcement layer behind prompt-injection-defense and ai-safety-guardrails.
- `agent-tool-review` — Review which tools, permissions and data an AI agent in the software has, and cut them to what its task needs. Use at S02 and S07 for any product or feature in which a model can call tools, write files, send messages or run code.
- `ai-ethics-compliance` — Check an AI feature against EU AI Act and GDPR duties, test for bias and proxy variables, and screen for dark patterns. Use before shipping a feature that scores, ranks or profiles people, or that talks to users as an AI.
- `ai-red-teaming` — Proactively attack your own AI and agent system to find failures before adversaries, scoring attack-success-rate and gating CI on it.
- `ai-safety-guardrails` — Add input, output, retrieval and execution rails around an LLM feature: PII scrubbing, output checks, and human approval for high-stakes actions. Use when building or reviewing a feature that sends user data to a model or acts on model output.
- `api-security` — Audit and harden REST or GraphQL endpoints against broken object-level authorisation, weak authentication and resource abuse. Use when adding or reviewing an API, tokens or rate limits.
- `backup-recovery` — Set recovery objectives (RPO, RTO), choose a backup method and run a restore test. Use at S09 to S11 when planning disaster recovery or when checking that backups can be restored.
- `compliance-review` — Regulatory compliance check for SOC2, PCI-DSS, GDPR, HIPAA — checklists, audit trails, access controls
- `cryptography-standards` — Choose and check cryptographic algorithms, password hashing and TLS settings. Use when code encrypts data, hashes passwords, stores keys or sets a TLS policy.
- `hazard-analysis` — Run FMEA and STPA on a safety-relevant design and fill the hazard log. Use when failure could harm people or assets, or before approving safety-critical requirements.
- `legal-review` — Check for license compliance, PII, and IP risks
- `log-analysis` — Read structured logs to find a cause: scope the time range, group by message, follow one trace id. Also flags secrets and personal data in logs. Use when investigating an error or incident from logs, or when reviewing what an application logs.
- `network-security` — Design and review network segmentation, firewall rules, TLS and egress controls for a deployment. Use at S02 for the network design and at S09 to S10 before go-live.
- `privacy-audit` — PII detection, data flow mapping, GDPR/CCPA/HIPAA compliance verification
- `privacy-data-protection` — Map personal data, minimise it, protect it, and design deletion and export for GDPR or CCPA duties. Use when designing a feature that stores personal or payment data.
- `reliability-engineering` — Design failover, redundancy and stability patterns, and compute availability from MTBF and MTTR. Use when a requirement sets an availability target or when one failure must not stop the service.
- `safety-scan` — Active security enforcement — scan for vulnerabilities (SAST), secrets (Gitleaks), insecure deps (SCA) before commit/deploy.
- `secure-architecture` — Design defence in depth: trust zones, least-privilege access policy and encryption boundaries. Use at S02 when drawing the architecture of a system that handles untrusted input, personal data or money.
- `security-requirements` — Turn a feature list into security and privacy requirements and abuse cases, written as testable EARS lines. Use at S01 when writing or reviewing a PRD for software with logins, personal data, uploads, payments or an AI agent.
- `traceability-audit` — Check that every requirement ID has a test and code, and flag code with no requirement. Use before a release or when a PRD changes. Security requirements are checked first.

## Licence

The skills are GABBE content under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), © 2026 Andrei Nicolae Besleaga. Source: https://github.com/andreibesleaga/GABBE
