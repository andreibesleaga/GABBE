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

## Steps

1. **Design threat-led scenarios mapped to OWASP LLM Top 10**
   - Start from threat actors and goals (insider, untrusted external content author, compromised tool/MCP server, end user seeking disallowed output), not from a generic checklist. Reuse the surface enumeration from `threat-model.skill` rather than re-deriving it.
   - Map each scenario to the relevant OWASP LLM Top 10 category (e.g. LLM01 Prompt Injection, LLM02 Sensitive Information Disclosure, LLM06 Excessive Agency, LLM07 System Prompt Leakage) so coverage is auditable and gaps are visible.

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

## Security & Guardrails

### 1. Skill Security
- **Risk**: The attack corpus this skill produces is itself a weapon — if leaked it hands adversaries a working playbook against the live system. Mitigation: store the corpus and findings as restricted artifacts with access control, keep them out of public repos and model training data, and treat unresolved high-severity findings as embargoed until fixed.
- **Risk**: Tests run with real production credentials or against production data cause real harm (data leakage, side effects) in the name of testing. Mitigation: run against isolated, synthetic-data environments with scoped throwaway credentials; require explicit authorization and a blast-radius review before any test touches production.

### 2. System Integration Security
- **Risk**: A red-team agent driving live tools can trigger genuine external actions — sends, writes, commits, payments — turning a simulated attack into a real incident. Mitigation: execute tool-abuse and exfiltration scenarios against mocked or sandboxed tool endpoints with egress disabled, and gate any real external call behind a human approval even in the test harness.
- **Risk**: A passing CI gate creates false assurance, letting teams ship on the belief the system is "red-team clean". Mitigation: surface the honesty caveat on the scorecard itself, pair the ASR gate with the defensive controls of `prompt-injection-defense.skill`, and require human sign-off for high-impact releases regardless of ASR.

### 3. LLM & Agent Guardrails
- **Risk**: An LLM judge scoring attack success can itself be jailbroken or biased, producing an inflated (too-safe) ASR. Mitigation: validate the judge against human-labeled samples per `llm-as-judge.skill`, isolate it from the attacker model's output channel, and periodically re-audit judge accuracy.
- **Risk**: Optimizing to drive ASR to zero on a fixed suite overfits the system to known attacks while real-world novel attacks still succeed. Mitigation: continuously rotate and expand the corpus, fold human-red-team discoveries back in, and never treat a zero-ASR snapshot as a terminal state.
