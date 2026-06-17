---
name: agent-sandboxing
description: Intrinsic least-privilege isolation for agents touching a local OS, shell, or filesystem — the enforcement layer behind prompt-injection-defense and ai-safety-guardrails.
triggers: [agent sandbox, sandbox policy, least privilege isolation, filesystem allowlist, egress deny-by-default, syscall restriction, microVM agent isolation, contain agent blast radius]
tags: [security]
core: false
context_cost: medium
---
# Agent Sandboxing Skill

## Goal
Provide the intrinsic, infrastructure-level isolation layer for any agent that touches a local OS, shell, or filesystem. Prompt-injection and guardrail rails (`prompt-injection-defense.skill`, `ai-safety-guardrails.skill`) reduce the probability that an agent is subverted; sandboxing bounds the *consequence* if one is. The design assumption is **assumed compromise**: the planner LLM may already be injected, so the controls must hold even when the agent actively tries to relax them.

The defining property is that all four isolation domains are **LOCKED at sandbox-creation time** and are **immutable for the lifetime of the run**. A prompt-injected agent cannot widen its own filesystem scope, open new egress, escalate privilege, or re-route inference, because those decisions were made by the host before the agent's non-deterministic logic ever ran. Container and microVM runtimes (gVisor, Kata, Firecracker) implement exactly this shape — a thin, host-enforced boundary the workload cannot reach around.

## Steps

1. **Declare the four isolation policies (deny-by-default).**
   Author a single declarative policy covering all four domains. Everything not explicitly allowed is denied.
   - **Filesystem**: read/write permitted ONLY inside explicit path allowlists (e.g. the task workspace and a scratch dir). Host binaries, system config directories, credential stores, SSH keys, and the agent's own runtime config are unreachable — not merely read-only, but absent from the mount namespace.
   - **Network**: egress is deny-by-default. A forward proxy is the only route out, and it enforces allow rules at **HTTP method + path granularity** (not just host/port), so `GET /v1/models` can be allowed while `POST /exfil` on the same host is refused. No raw sockets, no DNS to arbitrary resolvers.
   - **Process**: no privilege escalation (no setuid, `no_new_privs` set), a restrictive syscall filter blocking dangerous calls (ptrace, mount, kernel-module load, raw `clone` for daemons), no spawning of background daemons or detached processes, and capped CPU/memory/PID/file-descriptor limits.
   - **Inference routing**: all model calls are routed through controlled backends so prompt context and tool output stay within the trust boundary. The agent cannot redirect inference to an attacker-chosen endpoint, which would itself be an exfiltration channel.

2. **Lock the policy at sandbox creation.**
   The host (runtime supervisor / `policy` engine) materializes the sandbox from the declared policy and seals it BEFORE handing control to the agent. The four domains become immutable for the run: there is no in-band API, tool, or syscall by which the agent can edit its own allowlists, add egress rules, drop the syscall filter, or change the inference backend. Policy changes require tearing down and recreating the sandbox from outside — never a mid-run mutation. This is what makes the boundary robust to prompt injection: the attacker can only ask the agent to do something, and the agent has no privilege to grant it.

3. **Verify escape attempts fail (negative testing).**
   Treat the sandbox as untrusted-until-proven and run the escape-verification checklist (below) as part of provisioning and CI. Each probe MUST fail closed. A probe that succeeds is a sandbox defect, not an agent bug. On any verified escape or a runtime policy-violation signal, hand off to `self-heal.skill` to quarantine the sandbox, snapshot evidence for audit, and rebuild from the sealed policy rather than patching the live instance.

## Constraints
- Policies are immutable mid-run. If a legitimate task genuinely needs broader scope, the correct path is to tear down and recreate a new sandbox with a new sealed policy under human review — NEVER to relax a live one.
- Deny-by-default everywhere. An empty or missing allowlist means "nothing," not "everything."
- Network allow rules are matched at method + path granularity; host/port allowlisting alone is insufficient because it leaves wide exfiltration paths open on otherwise-legitimate hosts.
- Read-only is not enough for the filesystem: sensitive host paths must be absent from the namespace, so they cannot be enumerated or leaked even when only readable.
- Sandboxing bounds blast radius; it does not replace the upstream rails. Pair it with `prompt-injection-defense.skill` (so fewer compromises happen) and HITL gates on trifecta-complete actions (so the remaining ones are caught).
- The inference route is part of the trust boundary: an unrestricted model endpoint is an egress channel and must be locked like any other.

## Output Format
1. **Declarative sandbox policy** — a single document with four sections:
   - `filesystem`: read paths, write paths, explicitly-denied/absent paths.
   - `network`: proxy endpoint + ordered allow rules as `METHOD path-prefix → allow|deny`, default `deny`.
   - `process`: privilege flags (`no_new_privs`, no setuid), syscall allow/deny set, resource caps (CPU, memory, PIDs, FDs), daemon-spawn = denied.
   - `inference`: approved backend(s) and the enforcement point that pins them.
   Plus `runtime`: the chosen isolation runtime (gVisor / Kata / Firecracker / equivalent) and the `lock-at-creation: true` flag.
2. **Escape-verification checklist** — each item expected to FAIL CLOSED:
   - [ ] Write outside the filesystem allowlist is refused.
   - [ ] Read of a host credential/config path returns "not found" (path absent from namespace).
   - [ ] Egress to a non-allowlisted host is blocked at the proxy.
   - [ ] An allowlisted host but non-allowlisted method+path is blocked.
   - [ ] Privilege escalation (setuid / capability gain) is refused.
   - [ ] A blocked syscall (ptrace / mount / module load) is refused.
   - [ ] Spawning a detached daemon/background process is refused.
   - [ ] An attempt to re-point inference at an external endpoint is refused.
   - [ ] An in-band attempt to edit any of the four policies mid-run has no effect (immutability holds).

## Security & Guardrails

### 1. Skill Security
- **Risk**: a self-modifying or overly-permissive policy lets the agent widen its own scope — mitigation: policies are declarative, externally owned, and sealed by the host at creation; there is no in-band mutation path, and policy changes require an out-of-band teardown-and-recreate under review.
- **Risk**: a default-allow gap (empty allowlist read as "everything") silently grants full access — mitigation: deny-by-default is the only default; provisioning fails closed if any of the four domains is undeclared, and the escape checklist must pass before the sandbox is handed to the agent.

### 2. System Integration Security
- **Risk**: a sandbox escape pivots into the host OS, credential stores, or the broader network — mitigation: enforce isolation with a host-level runtime (gVisor / Kata / Firecracker), keep sensitive host paths absent from the namespace, route all egress through a method+path-granular proxy, and block ptrace/mount/module-load syscalls so kernel-boundary escapes have no primitive.
- **Risk**: the model endpoint becomes an unmonitored exfiltration channel — mitigation: pin inference to controlled backends inside the trust boundary, treat the inference route as egress, and refuse any redirect to an external endpoint.

### 3. LLM & Agent Guardrails
- **Risk**: a prompt-injected agent is socially engineered into trying to relax its own sandbox — mitigation: the four domains are immutable mid-run, so the agent has nothing to grant; the worst case is a refused request, not a widened boundary, and the refusal is logged as a violation signal.
- **Risk**: a compromised agent spawns daemons or background processes to outlive the run or stage exfiltration — mitigation: daemon/detached-process spawning is denied by the syscall filter and PID caps, and any violation triggers `self-heal.skill` to quarantine, snapshot, and rebuild from the sealed policy rather than patch the live instance.
