---
name: prompt-injection-defense
description: "Defend agentic systems against direct and indirect prompt injection using defense-in-depth. Use when: prompt injection, indirect injection, lethal trifecta, rule of two, jailbreak defense, tool output poisoning, untrusted content."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/security/prompt-injection-defense.skill.md"
  tags: "security"
  core: "true"
  context_cost: "medium"
---
# Prompt Injection Defense Skill

## Goal
Defend agentic systems against direct and indirect prompt injection using defense-in-depth. No single control is sufficient: frontier labs publicly acknowledge that prompt injection cannot be fully solved in current LLM architectures, so the objective is to layer controls, contain the blast radius, and gate high-impact actions behind a human. Grounded in OWASP LLM01:2025 (Prompt Injection).

## Where it fits
Phase and gate: S02 (trifecta assessment), S05 (build), S07 (review). Evidence: the defence report (surfaces, trifecta assessment, controls, human gates) in `docs/security/THREAT_MODEL.md`. Part of `security-baseline.skill.md` for AI software. For tool permissions see `agent-tool-review.skill.md`.

## Steps

1. **Classify the injection surface**
   - **DIRECT injection**: a malicious instruction supplied in the user's own prompt.
   - **INDIRECT injection**: malicious instructions hidden inside content the agent ingests but did not author — tool output, RAG documents, web fetches, file contents, tool metadata/descriptions, image alt-text, and error strings.
   - Treat ALL external and tool-returned content as UNTRUSTED by default. Trust is earned by provenance, never assumed from format.

2. **Apply the LETHAL TRIFECTA test, then the RULE OF TWO**
   - Risk is highest when a single agent simultaneously has: (a) access to private/sensitive data, (b) exposure to untrusted content, and (c) the ability to exfiltrate data or act externally (send, write, call, commit).
   - Apply Meta's RULE OF TWO: an agent should hold at most **2 of those 3** capabilities at once without a human-in-the-loop gate. If all three are present, a trifecta-complete path exists and the action MUST be gated.
   - Record the assessment per agent/tool-chain, not per request.

3. **Apply layered defenses (defense-in-depth)**
   - **Instruction hierarchy**: enforce a strict priority — system > developer > user > tool-output. Lower tiers can never override higher-tier instructions.
   - **Spotlighting / delimiting**: wrap all untrusted content in explicit delimiters and explicitly mark it as untrusted data, never as instructions.
   - **DUAL-LLM / quarantine pattern**: a privileged planner LLM that never sees raw untrusted text, paired with a quarantined LLM that processes untrusted content and returns only structured/symbolic results (IDs, enums, validated fields) the planner can act on.
   - **Tool allowlisting**: restrict each agent to an explicit allowlist of tools and parameter shapes.
   - **Content-provenance tracking**: tag every datum with its source so trust decisions are traceable.
   - **Egress filtering**: constrain outbound destinations and payloads to block exfiltration channels.

4. **Add a detection pre-filter (necessary, not sufficient)**
   - Run a small, fast classifier as a pre-filter before privileged processing (named examples: Llama Guard, Prompt Guard, NeMo Guardrails).
   - Understand that detectors REDUCE but do not ELIMINATE risk. They are one layer behind the structural controls above, never the only line of defense.

5. **Require human-in-the-loop approval for high-impact or trifecta-complete actions**
   - Any action that is irreversible, externally visible, or completes the lethal trifecta requires explicit human approval before execution. The agent proposes; the human approves.

## Constraints
- NEVER rely on a single defense. Pattern-matching filters and "ask the LLM to detect the injection" are known-weak and trivially bypassed.
- Assume the LLM layer CAN be compromised; design so a compromised model still cannot reach private data or an exfiltration channel without passing a structural gate.
- Indirect injection is the dominant agentic threat — never exempt tool output, RAG, or file content from untrusted-content handling.
- Detection classifiers are pre-filters, not authorization. A "clean" classifier verdict does not grant a trifecta-complete action.

## Output Format
A defense report containing:
- **Surfaces identified**: direct and indirect injection surfaces for this agent/tool-chain.
- **Trifecta assessment**: which of (private data / untrusted content / external action) are present, and whether the Rule of Two holds.
- **Controls applied**: which layered defenses are in place (hierarchy, spotlighting, dual-LLM, allowlist, provenance, egress, detection).
- **Residual risk**: what remains unmitigated after the layers.
- **Required HITL gates**: the specific actions that must be human-approved.

## Limits and safety
- Assess per agent and tool chain, not per request, and record the result in the defence report.
- Any action that is irreversible, external or completes the trifecta waits for the human's yes.
- Add provenance tags to untrusted data and limit outbound destinations.
- A clean detector verdict is not permission to act.
