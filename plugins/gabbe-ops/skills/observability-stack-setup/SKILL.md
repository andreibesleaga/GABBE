---
name: observability-stack-setup
description: "Plan OpenTelemetry traces, metrics and logs, GenAI span attributes, SLIs and SLOs, dashboards and alerts that each link to a runbook. Use when you add tracing, define SLOs, or cannot see why a service or LLM call is slow or costly."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/ops/observability-stack-setup.skill.md"
  tags: "ops, observability, opentelemetry, telemetry"
  core: "false"
  context_cost: "medium"
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

## Limits and safety
- Keep prompts, completions, tokens and personal data out of spans and logs; if the Collector supports an attribute filter, use it to enforce this.
- Bound attribute values; do not use raw user input or full URLs as attribute keys.
- Exporter endpoints use TLS and authentication and are pinned in reviewed IaC; a changed endpoint needs the human's review.
- Do not remove instrumentation or lower sampling without the human's approval and an `AUDIT_LOG.md` row.
- Token and cost attributes stay on every LLM span.
