# Guide: AI Risk Standards Map
<!-- Mapping GABBE capabilities to named AI-risk standards: OWASP LLM Top 10, NIST AI RMF, MITRE ATLAS, ISO/IEC 42001, EU AI Act -->

---

## 1. Why This Map Exists

GABBE makes governance claims about agentic and LLM-driven development. To keep those claims grounded — the same way ADD 3.0 and ATAM ground architecture decisions in named methods rather than opinion — this guide maps GABBE's capabilities (skills, gates, personas, and engine controls) onto the recognized AI-risk standards.

Each mapping answers one question per risk: *which concrete GABBE control addresses this?* Where a real control exists it is named in backticks. This is a coverage map, not a compliance certificate (see the honesty note at the end).

## 2. OWASP Top 10 for LLM Applications (2025)

Every row names at least one GABBE control.

| OWASP ID | Risk | GABBE control (skill / gate / persona) |
|---|---|---|
| LLM01 | Prompt Injection | `prompt-injection-defense.skill` (lethal-trifecta + rule-of-two, dual-LLM quarantine, spotlighting), `ai-safety-guardrails.skill` input rails, human-approval gates on trifecta-complete actions |
| LLM02 | Sensitive Information Disclosure | `output-validation.skill` (PII masking before external APIs and logs), `secrets-management.skill`, `ai-safety-guardrails.skill` PII scrubbing |
| LLM03 | Supply Chain | `dependency-security.skill` (SBOM, SCA, vulnerability patching), `integrity-check.skill` (artifact/provenance integrity) |
| LLM04 | Data & Model Poisoning | `integrity-check.skill`, `rag-evaluation.skill` (retrieval quality and source vetting), `threat-model.skill` for poisoning surfaces |
| LLM05 | Improper Output Handling | `output-validation.skill` (schema validation + retry-on-failure, encoding before side-effecting sinks), the fail-closed gateway |
| LLM06 | Excessive Agency | the policy engine / fail-closed gateway, human-approval gates, `prompt-injection-defense.skill` rule-of-two capability limits, least-privilege tokens |
| LLM07 | System Prompt Leakage | `prompt-injection-defense.skill` (no-secrets-in-system-prompt, deny verbatim reflection), `ai-safety-guardrails.skill` output rails |
| LLM08 | Vector & Embedding Weaknesses | `rag-evaluation.skill` (embedding/retrieval evaluation, source provenance), `threat-model.skill` for retrieval-boundary threats |
| LLM09 | Misinformation | `rag-evaluation.skill` (grounding/faithfulness checks), `output-validation.skill` (structure ≠ truth caveat), human-approval gates for high-impact claims |
| LLM10 | Unbounded Consumption | the budget / hardstop caps, `output-validation.skill` bounded retry loop, the policy engine / fail-closed gateway, loop-detection guards |

## 3. NIST AI RMF (and the Generative AI Profile)

The AI Risk Management Framework organizes risk work into five functions. GABBE coverage:

- **Govern**: persona roles (prod-ethicist, ops-security), the policy engine and fail-closed gateway as the organizational control plane; `ai-safety-guardrails.skill` as the standing safety posture.
- **Map**: `threat-model.skill` (STRIDE surfaces) and `prompt-injection-defense.skill` (trifecta/surface enumeration) identify context and risk.
- **Measure**: `rag-evaluation.skill`, `output-validation.skill` validation reports, and the cognitive-testing invariant/convergence reports quantify behavior.
- **Manage**: `dependency-security.skill`, `secrets-management.skill`, `integrity-check.skill`, human-approval gates, and the budget/hardstop caps act on prioritized risk.
- **Monitor**: input/output rails logging in `ai-safety-guardrails.skill`, egress filtering and guard-trigger telemetry from `prompt-injection-defense.skill`.

The **Generative AI Profile** (NIST AI 600-1) overlays GenAI-specific risks (confabulation, data privacy, harmful output); GABBE addresses these via `output-validation.skill`, `rag-evaluation.skill`, and the `ai-safety-guardrails.skill` rails taxonomy.

## 4. MITRE ATLAS (Adversarial Threat Landscape for AI Systems)

ATLAS catalogs adversary tactics against AI. Indicative GABBE coverage by tactic:

- **Reconnaissance / Resource Development**: `threat-model.skill` enumerates exposed surfaces before they are probed.
- **Initial Access (LLM Prompt Injection)**: `prompt-injection-defense.skill` direct + indirect injection defenses, input rails.
- **ML Supply Chain Compromise**: `dependency-security.skill`, `integrity-check.skill`.
- **Defense Evasion / LLM Jailbreak**: layered controls in `prompt-injection-defense.skill` and `ai-safety-guardrails.skill` (no single classifier trusted).
- **Exfiltration (via inference / tool feedback)**: egress filtering and `output-validation.skill` PII masking, human-approval gates on trifecta-complete actions.
- **Impact (Denial of ML Service / cost)**: the budget/hardstop caps and loop-detection guards.

## 5. ISO/IEC 42001 (AI Management System)

ISO/IEC 42001 specifies an Artificial Intelligence Management System (AIMS) — policy, roles, risk treatment, and continual improvement. GABBE supports the management-system intent through:

- **Policy & roles**: the policy engine, fail-closed gateway, and security/ethicist personas provide documented, enforced controls and accountable ownership.
- **Risk assessment & treatment**: `threat-model.skill` and `prompt-injection-defense.skill` for assessment; `output-validation.skill`, `dependency-security.skill`, `secrets-management.skill`, and `integrity-check.skill` for treatment.
- **Operational controls & monitoring**: `ai-safety-guardrails.skill` rails, budget/hardstop caps, and human-approval gates.
- **Continual improvement**: evaluation feedback from `rag-evaluation.skill` and the cognitive-testing reports feeds control refinement.

GABBE provides controls that *support* an AIMS; it does not constitute an AIMS by itself.

## 6. EU AI Act (Obligations Relevant to Agentic Dev Tooling)

For agentic developer tooling, the most relevant EU AI Act themes and GABBE's coverage:

- **Transparency**: provenance tracking and validation reports (`output-validation.skill`, `prompt-injection-defense.skill`) make agent actions auditable; document AI involvement in generated artifacts.
- **Risk management & robustness**: `threat-model.skill`, layered injection defenses, and the fail-closed gateway support documented risk management for higher-risk uses.
- **Data governance & privacy**: PII masking in `output-validation.skill` and `secrets-management.skill` align with data-protection obligations.
- **Human oversight**: human-approval gates and the rule-of-two capability limits in `prompt-injection-defense.skill` keep a human in the loop for high-impact actions.
- **Logging & traceability**: rails logging, egress telemetry, and `integrity-check.skill` support record-keeping expectations.

General-purpose / foundation-model obligations apply to the underlying models GABBE orchestrates, not to GABBE's controls themselves.

## 7. Honesty Note

This guide documents **coverage and intent** — how GABBE's existing controls map onto named AI-risk standards — to keep the framework's governance claims grounded. It is **not** a certification, audit result, or compliance attestation. A control appearing in a mapping row means GABBE provides a relevant mechanism; it does NOT mean GABBE is certified against OWASP, NIST AI RMF, MITRE ATLAS, ISO/IEC 42001, or the EU AI Act. Formal conformance requires independent assessment against the specific standard's normative requirements.
