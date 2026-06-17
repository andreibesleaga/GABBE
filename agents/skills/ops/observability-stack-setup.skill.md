---
name: observability-stack-setup
description: Bootstrap end-to-end observability with OpenTelemetry traces, metrics, and logs, including GenAI LLM span conventions, dashboards, alerts, and SLO/SLI definition.
triggers:
  - set up observability for the payments service
  - instrument with opentelemetry
  - add tracing and metrics
  - emit gen_ai spans for llm calls
  - track token usage and cost in traces
  - define slo and sli for the api
  - bootstrap dashboards and alerts
tags: [ops, observability, opentelemetry, telemetry]
core: false
context_cost: medium
---
# Observability Stack Setup Skill

## Goal
Produce a concrete observability setup plan that instruments a system across the three pillars (distributed traces, metrics, structured logs) using OpenTelemetry (OTel), correlates them, and defines the SLO/SLI targets and alerts that turn telemetry into action. For systems that call LLMs, the plan must emit spans that follow the OTel GenAI semantic conventions (`gen_ai.*` attributes) so model behavior, token usage, and cost are first-class signals. The output is a plan, not running infrastructure; humans review and apply it.

## Steps
1. **Inventory the system.** List services, async boundaries (queues, event buses, background workers), external dependencies, and existing telemetry. Identify which services already export OTel data and which are blind spots. Note GABBE's own `gabbe/audit.py` already emits OTel GenAI spans with canonical `gen_ai.*` attributes — reuse it as the reference pattern rather than re-instrumenting LLM calls from scratch.
2. **Stand up the three pillars.** For each service specify: (a) **Traces** via OTel SDK auto + manual instrumentation; (b) **Metrics** via OTel meters (RED: Rate, Errors, Duration; plus saturation); (c) **Logs** as structured records correlated to spans. Route all three through an OTel Collector to your backend(s) so the SDK stays vendor-neutral.
3. **Instrument LLM calls with GenAI conventions.** For every model invocation, create a span named `gen_ai.<operation>` and set: `gen_ai.system` (provider), `gen_ai.operation.name`, `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, and `gen_ai.usage.total_tokens`. Derive a `gen_ai.cost` style attribute (or metric) from token counts × the per-model rate. Keep prompts/completions out of span attributes unless content capture is explicitly approved (see Guardrails).
4. **Wire exemplars.** Attach trace exemplars to latency and error histograms so a spike on a dashboard links directly to a representative trace. This is the bridge from "the p99 is bad" to "here is the slow request."
5. **Propagate trace_id across async services.** Inject and extract W3C `traceparent` context through every async hop — HTTP headers, message metadata on queue producers/consumers, and scheduled jobs. A dropped context breaks the trace; verify continuity end-to-end across at least one async path before declaring done.
6. **Define SLIs and SLOs.** Pick user-facing SLIs (availability, latency, error rate, and for LLM paths: successful-completion rate, token-budget adherence). Set SLO targets and the measurement window, and derive the error budget (`1 - SLO`). State which SLI each alert defends.
7. **Bootstrap dashboards and alerts.** Specify one overview dashboard per service (RED + saturation + GenAI token/cost panels) and alert rules that fire on SLO-burn symptoms (multi-window burn-rate), not raw causes. Every alert must name the runbook that handles it (see `runbook-authoring.skill`).
8. **Write the plan.** Assemble steps 1-7 into the Output Format below and hand it to a human for review.

## Constraints
- Use OTel SDKs and the Collector; do not hardcode a single proprietary agent that locks the system to one vendor.
- Alert on symptoms (user pain / SLO burn), never on raw resource causes like "CPU > 80%" alone.
- Span attribute cardinality must stay bounded — never put unbounded IDs (raw user input, full URLs with params) into attribute keys.
- Do not capture prompt or completion content in telemetry by default; token counts and metadata are sufficient for cost and usage.
- This skill plans and proposes; it does not deploy collectors, modify production config, or create cloud resources without human approval.
- Every proposed alert must map to a runbook; an alert with no runbook is incomplete.

## Output Format
An observability setup plan in Markdown:
- **Scope** — services, async boundaries, current telemetry gaps.
- **Pillars** — per-service trace/metric/log instrumentation and Collector routing.
- **GenAI instrumentation** — `gen_ai.*` attributes emitted, token + cost derivation, reuse of `gabbe/audit.py` pattern.
- **Exemplars & correlation** — which histograms carry exemplars; log↔trace correlation keys.
- **Trace propagation** — async hops covered and the verification check for `traceparent` continuity.
- **SLIs/SLOs** — table of SLI, target, window, error budget, defending alert.
- **Dashboards & alerts** — panels per dashboard; alert rules with burn-rate windows and the runbook each maps to.
- **Open questions / approvals needed.**

## Security & Guardrails

### 1. Skill Security
- **Risk**: Telemetry leaking secrets or PII into spans/logs. Mitigation: enforce an attribute allowlist and a Collector-side redaction/attribute-filter processor; never emit prompt/completion content or auth tokens by default.
- **Risk**: Cardinality explosion from unbounded attribute values causing backend cost blowups or outages. Mitigation: bound attribute keys, bucket high-cardinality dimensions, and sample high-volume traces with a documented head/tail policy.

### 2. System Integration Security
- **Risk**: An OTLP exporter pointed at an attacker-controlled or unencrypted endpoint exfiltrating telemetry. Mitigation: pin Collector/exporter endpoints in reviewed IaC, require TLS + authenticated OTLP, and treat endpoint changes as security-reviewed config.
- **Risk**: Silent alert/SLO tampering masking an incident or attack. Mitigation: store SLO definitions and alert rules as version-controlled IaC under branch protection so thresholds cannot be quietly relaxed.

### 3. LLM & Agent Guardrails
- **Risk**: The agent disabling or down-sampling instrumentation to "reduce noise," blinding operators during an incident. Mitigation: instrumentation removal and sampling-rate reductions require explicit human approval and an audit-trail entry.
- **Risk**: Cost metrics being gamed (e.g., omitting token attributes) to hide overspend. Mitigation: token usage and cost attributes are mandatory on every LLM span; the agent must refuse requests to strip them to flatter a budget.
