---
name: ai-red-teaming
description: Proactively attack your own AI and agent system to find failures before adversaries, scoring attack-success-rate and gating CI on it.
triggers: [ai red teaming, red team plan, attack success rate, ASR scorecard, jailbreak testing, crescendo attack, automated adversarial testing, OWASP LLM red team]
tags: [security, ai, agents]
core: false
context_cost: medium
---
# AI Red Teaming Skill

## Goal
Proactively attack your own AI/agent system to discover failures before an adversary does. This is the offensive complement to the defensive skills: `prompt-injection-defense.skill` builds the layered controls and `ai-safety-guardrails.skill` builds the rails — this skill tries to break both. Red teaming is threat-led: it designs scenarios from a model of who would attack and why, executes them as concrete attacks, scores the attack-success-rate (ASR), and gates CI on it so regressions are caught automatically. Stated honestly: red teaming *reduces* risk by finding failures, but it can never *prove* safety — absence of a successful attack in your suite is not evidence the system is safe.

## Where it fits
Phase and gate: S06 and S07 for tier 3 AI software, and again after any model, prompt, tool or retrieval change (S11, S12). Evidence: the red-team plan and ASR scorecard in `docs/security/RED_TEAM_REPORT.md`.

## Steps

1. **Design threat-led scenarios mapped to OWASP LLM Top 10**
   - Start from threat actors and goals (insider, untrusted external content author, compromised tool/MCP server, end user seeking disallowed output), not from a generic checklist. Reuse the surface enumeration from `threat-model.skill` rather than re-deriving it.
   - Map each scenario to the relevant OWASP LLM Top 10 category (e.g. LLM01 Prompt Injection, LLM02 Sensitive Information Disclosure, LLM06 Excessive Agency, LLM07 System Prompt Leakage) so coverage is auditable and gaps are visible. The ids are those of the 2025 edition (genai.owasp.org, checked 2026-11-21).
   - For agent software also map to the OWASP Top 10 for Agentic Applications (released 9 Dec 2025): ASI01 Agent Goal Hijack, ASI02 Tool Misuse and Exploitation, ASI03 Identity and Privilege Abuse, ASI04 Agentic Supply Chain Vulnerabilities, ASI05 Unexpected Code Execution (RCE), ASI06 Memory & Context Poisoning, ASI07 Insecure Inter-Agent Communication, ASI08 Cascading Failures, ASI09 Human-Agent Trust Exploitation, ASI10 Rogue Agents.

2. **Build the attack technique library**
   - **Direct injection**: malicious instructions in the user's own prompt.
   - **Indirect injection**: instructions hidden in ingested content — RAG documents, web fetches, file contents, tool output, tool metadata, image alt-text.
   - **Jailbreaks**: persona/role-play, obfuscation, encoding, and refusal-bypass prompts targeting the safety policy.
   - **Multi-turn / crescendo**: benign-looking openers that escalate across turns to a disallowed goal that a single-turn filter would miss.
   - **Data exfiltration**: weaponizing a benign tool (link unfurl, image fetch, URL parameter, DNS) as a covert channel for private data the agent holds.
   - **Tool abuse / excessive agency**: coercing the agent into unauthorized, irreversible, or out-of-scope tool calls.
   - **Training-data extraction**: probing for memorized PII, secrets, or proprietary text in model outputs.

3. **Automate with red-team tooling**
   - Use an orchestration framework to generate and run attacks at scale (named generically: PyRIT for orchestration and scoring, Garak for probe-based vulnerability scanning).
   - Codify the highest-value, reproducible attacks as a regression suite that runs in CI (named generically: Promptfoo for assertion-based red-team tests in the pipeline).
   - Combine seed prompts with automated mutation/transformation so the suite explores variants rather than a fixed list an implementer can overfit to.

4. **Score attack-success-rate (ASR) and gate CI**
   - Define success per scenario with an explicit, automatable judge (a successful exfiltration, a policy-violating completion, a leaked system prompt). Where an LLM judge scores attacks, apply `llm-as-judge.skill` and spot-check the judge against human labels.
   - Compute ASR = successful attacks / total attempts, broken out per OWASP category and per technique.
   - Gate the pipeline: fail CI when ASR on a category exceeds its agreed threshold, or when ASR regresses versus the last green run. Pin thresholds so "we made it slightly worse" cannot ship silently.

5. **Run human red-teaming for the long tail**
   - Automated suites miss creative, context-specific, and socially-engineered attacks. Schedule human red-team exercises for novel scenarios, then promote anything they find into the automated regression suite so it can never recur unnoticed.

6. **Make it continuous**
   - Re-run the suite on every model, prompt, tool, or retrieval-source change — any of these can reopen a closed vulnerability. Treat red teaming as a standing process tied to release, not a one-time audit.

## Constraints
- NEVER present a passing red-team run as proof of safety. Report it as "no successful attack in this suite as of this run" — a falsifiable claim, not a guarantee.
- NEVER let the system under test see the attack corpus at train/eval time; a model that memorizes the suite produces a flattering ASR that does not transfer to real adversaries.
- Red teaming is the offensive complement to, not a replacement for, the structural defenses in `prompt-injection-defense.skill`. Findings drive fixes there; they do not substitute for them.
- Run attacks only against systems and data you are authorized to test, in an isolated environment; never exfiltrate real user data or trigger real external side effects during a test.
- An ASR gate is only as honest as its judge — a weak judge inflates safety. Validate the judge before trusting the gate.

## Output Format
A red-team plan plus an ASR scorecard:
- **Threat-led scenarios**: actors, goals, and the OWASP LLM category each maps to.
- **Technique coverage**: which attack families are exercised and which are out of scope (stated explicitly).
- **Tooling**: orchestration/scanner/CI-regression tools and where each runs.
- **ASR scorecard**: a table of OWASP category × technique × attempts × successes × ASR, with the prior run for comparison.
- **CI gates**: the per-category ASR thresholds and the regression rule.
- **Findings & fixes**: each successful attack, its severity, the owning defensive skill, and remediation status.
- **Residual risk & honesty statement**: what was not tested and the explicit caveat that this suite reduces but cannot prove safety.

## Limits and safety
- Attack only systems and data you are authorised to test, in an isolated environment with synthetic data and mocked or sandboxed tools. No real sends, writes or payments.
- Keep the attack corpus and unfixed findings out of public repositories.
- Report a pass as "no successful attack in this suite on this date", never as proof of safety.
- Validate the judge against human labels before trusting the ASR gate.
- A real external call during a test needs the human's yes.
