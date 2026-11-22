---
name: final-review
description: "Runs an independent expert review of finished work and returns a verdict (SHIP, FIX-FIRST or NEEDS-DECISION) with must-fix items and simplifications. Use when work is about to be called done, or before a human gate."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/core/final-review.skill.md"
  tags: "core"
  core: "true"
  context_cost: "medium"
---
# Final-Review Skill

## Goal
Before declaring any substantial piece of work "done", run a deliberate **expert
review** — the pass a senior engineer/architect does to catch what the
implementer missed, and to leave the system *better*, not just *working*. This
complements `integrity-check.skill` (which verifies pass/fail across 8 dimensions)
by adding a judgment layer: correctness risks, missing pieces, and concrete
optimizations/simplifications. Use an **independent perspective** — review as if
you did not write the code.

## Review dimensions (score each: OK / FIX / CONSIDER)
1. **Correctness & edge cases** — does it do what the spec says? Untested paths, off-by-one, error handling, concurrency, empty/huge/hostile inputs?
2. **Security** — input validation at boundaries, no secrets in code/logs/state, least privilege, path-traversal/egress on any external input, no weakened guardrails.
3. **Spec & golden thread** — every requirement maps to a test and to code (and back). Anything built that no requirement asked for? Anything asked for that's missing?
4. **Observability** — is the work traced (decisions/spans + token/cost)? Could a human debug it from the audit trail alone? (first-class — never a black box.)
5. **Collaboration (Purpose/Transparency/Control)** — scope/non-goals explicit; reasoning legible; the right human-in-the-loop gates fired for the autonomy level.
6. **Cost** — cheapest reliable path taken? Caching/context-budget/model-tier/batching applied? No expensive/SOTA call slipped in unapproved?
7. **Simplicity** — can anything be removed, merged, or made clearer? Premature abstraction, dead code, duplication, needless config?
8. **Consistency** — matches surrounding conventions, naming, style, error patterns; no broken internal references/links.
9. **All-agents / portability** — if the kit's emitted artifacts changed, do they still emit cleanly for every target (Claude Code, Cursor, Antigravity, OpenCode, Gemini, Copilot, …) and stay backward-compatible (golden additive)?
10. **Tests & gates** — tests exist for the new behavior; the backward-compat gates and validators are green; baselines regenerated + reviewed if intentionally changed.

## Steps
1. Read the diff as if you did not write it.
2. Run the tests, validators and gates yourself and keep the output.
3. Score each review dimension OK, FIX or CONSIDER with the evidence.
4. Write the verdict in the Output Format below.

## Method
- Re-read the diff with fresh eyes; assume nothing is correct until checked.
- Prefer **evidence over assertion** — run the test/command rather than claim it passes (`verify_all.sh`).
- Separate **must-fix** (correctness/security/regression) from **nice-to-have** (optimization/simplification); fix the former now, log the latter.
- For anything uncertain, ask (`clarify.skill`) rather than assume.

## Output Format
```markdown
## FINAL REVIEW — [scope]
- Verdict: SHIP | FIX-FIRST | NEEDS-DECISION
- Must-fix: [items or none]
- Optimizations/simplifications: [items or none]
- Missing/!: [gaps or none]
- Evidence: [commands run + results — gates/tests/validators green?]
```

## Constraints
- Never sign off on unverified claims — run the checks; cite the evidence.
- Must-fix items (correctness, security, regression) block "done"; nice-to-haves do not.
- Review independently — do not rubber-stamp your own implementation.
- Leave the system better than you found it, but scope improvements to the task (no opportunistic rewrites).

## Limits and safety
- Run the checks yourself and quote their output; "looks good" is not evidence.
- A change that lowers a quality gate, a coverage threshold or an autonomy limit is a must-fix.
- When baselines or golden files changed, read the diff; do not accept a regenerated baseline unread.
- Review what the code does, not what its author meant; try at least one hostile input.
