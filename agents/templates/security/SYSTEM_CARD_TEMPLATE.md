# System Card: [SYSTEM_NAME]

<!-- System Card for a deployed AI system (models + tools + retrieval + guardrails). Fill every [PLACEHOLDER]. -->
<!-- Store in: docs/security/system-cards/[system-name]-system-card.md -->
<!-- A System Card describes the whole deployed system, not a single model. Reference each component's Model Card and Datasheet by name. -->

---

## 1. System Overview and Components

| Field | Value |
|---|---|
| System name | [SYSTEM_NAME] |
| Version | [VERSION] |
| Owner / team | [OWNER_TEAM] |
| Point of contact | [CONTACT] |
| Date / status | [DATE] / [DEV / STAGING / PRODUCTION] |
| One-line description | [WHAT_THE_SYSTEM_DOES] |

### Component inventory

| Component | What it is | Provenance / reference |
|---|---|---|
| Model(s) | [model name + version] | [reference its MODEL_CARD_TEMPLATE entry by name] |
| Training data | [dataset name] | [reference its DATASHEET_TEMPLATE entry by name] |
| Tools / actions | [tools/APIs the system can call] | [allowlist source] |
| Retrieval / knowledge | [RAG sources, vector store, indexes] | [source of truth] |
| Guardrails | [input/output filters, classifiers, policy engine] | [config location] |
| Orchestration | [single agent / multi-agent topology] | [reference relevant guide by name] |

### Data-flow summary
[Describe how a request flows through the components: input -> guardrails -> retrieval -> model -> tools -> output validation -> response. Note trust boundaries.]

---

## 2. Intended Use and Users

### In-scope
- [Intended task(s)]
- [Intended users and their context]

### Out-of-scope
- [Uses the system is NOT validated for]
- [Explicitly prohibited uses]
- [Decisions that must not be fully automated by this system]

---

## 3. Risk Assessment

<!-- Map each risk to a recognized framework so coverage is auditable. -->

| Risk | OWASP LLM Top 10 ref | NIST AI RMF function | Likelihood (L/M/H) | Impact (L/M/H) | Priority |
|---|---|---|---|---|---|
| Prompt injection (direct/indirect) | LLM01 | [Govern/Map/Measure/Manage] | [L/M/H] | [L/M/H] | [Critical/High/Med/Low] |
| Sensitive information disclosure | LLM02 | [function] | | | |
| Excessive agency / unauthorized tool use | LLM06 | [function] | | | |
| System prompt leakage | LLM07 | [function] | | | |
| [Other system-specific risk] | [ref] | [function] | | | |

> Reference `threat-model.skill` for surface enumeration and the project Threat Model (see `THREAT_MODEL_TEMPLATE`).

---

## 4. Safety Mitigations and Guardrails

| Control | Layer | What it mitigates | Reference |
|---|---|---|---|
| Instruction hierarchy / spotlighting | Input | Prompt injection | `prompt-injection-defense.skill` |
| Untrusted-content quarantine (dual-LLM) | Processing | Indirect injection | `prompt-injection-defense.skill` |
| Tool allowlist + least-privilege tokens | Action | Excessive agency | [policy source] |
| Egress filtering | Output | Data exfiltration | [config] |
| Output validation | Output | Unsafe/malformed output | `output-validation.skill` |
| Content/safety classifiers | Input+Output | Policy violations | `ai-safety-guardrails.skill` |
| Human-approval gate | Action | High-impact/irreversible actions | [gate definition] |

---

## 5. Evaluation and Red-Team Results

### Functional evaluation
| Metric | Result | Bar | Pass? |
|---|---|---|---|
| [METRIC_1] | [value] | [target] | [Y/N] |
| [METRIC_2] | [value] | [target] | [Y/N] |

### Red-team / ASR scorecard
<!-- Reference ai-red-teaming.skill. ASR = attack-success-rate. -->

| OWASP category | Technique | Attempts | Successes | ASR | Gate threshold | Pass? |
|---|---|---|---|---|---|---|
| LLM01 | Direct injection | [N] | [N] | [%] | [%] | [Y/N] |
| LLM01 | Indirect injection | [N] | [N] | [%] | [%] | [Y/N] |
| LLM06 | Tool abuse | [N] | [N] | [%] | [%] | [Y/N] |
| [category] | [technique] | | | | | |

> Honesty statement: a passing red-team run means no successful attack in this suite as of [DATE]; it does not prove the system is safe. See `ai-red-teaming.skill`.

---

## 6. Human Oversight and Escalation

- **Where a human is in the loop**: [decision points requiring human approval]
- **Escalation triggers**: [low confidence, guardrail trip, high-impact action, anomaly]
- **Who responds**: [role/on-call]
- **Override / kill switch**: [how to disable or roll back the system]

---

## 7. Monitoring and Incident Response

| Field | Value |
|---|---|
| What is monitored | [latency, refusal rate, guardrail trips, ASR drift, cost, output anomalies] |
| Telemetry standard | [e.g. OTel GenAI conventions] |
| Alert thresholds | [thresholds and owners] |
| Incident runbook | [reference] |
| Logging & attribution | [what is logged, against which agent identity] |
| Retention | [log retention period] |

---

## 8. Known Limitations

| Limitation | Impact | Guidance |
|---|---|---|
| [Limitation 1] | [impact] | [how to compensate] |
| [Limitation 2] | [impact] | [guidance] |
| Prompt injection cannot be fully eliminated | Residual risk of manipulated actions | Keep HITL gates on high-impact actions |

---

## 9. Sign-off

| Role | Name | Status | Date |
|---|---|---|---|
| System owner | [name] | [APPROVED / PENDING] | [date] |
| Security reviewer | [name] | [APPROVED / PENDING] | [date] |
| Responsible-AI / Ethics reviewer | [name] | [APPROVED / PENDING] | [date] |
