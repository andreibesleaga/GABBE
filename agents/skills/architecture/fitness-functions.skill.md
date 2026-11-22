---
name: fitness-functions
description: Set of measurable architecture checks (dependency rules, complexity, latency budgets) with thresholds, tools and CI wiring. Use when architectural properties should be tested automatically instead of reviewed by hand.
triggers: [write architecture fitness functions, measure architectural characteristics, enforce layering rules in ci, set a latency budget test, atomic vs holistic fitness function, catch architectural drift automatically]
tags: [architecture, governance, evolutionary-architecture, ci, testing]
core: false
context_cost: medium
---
# Fitness Functions

## Goal
Make architecture an executable, enforced thing rather than a diagram that rots. A *fitness
function* is an objective, measurable test of an architectural characteristic — the
evolutionary-architecture mechanism for governing the "-ilities" the same way unit tests
govern logic. Where a unit test asserts a feature works, a fitness function asserts a
*structural property* holds: cyclomatic complexity stays under a limit, the domain layer never
imports infrastructure, p99 latency stays inside its budget, afferent/efferent coupling stays
bounded. Wired into CI, fitness functions turn architectural intent into automated governance
that fails the build the moment the system drifts away from its target characteristics.

## Steps
1. **Name the architectural characteristic to protect.** Pick one measurable "-ility" the
   architecture must preserve (maintainability, performance, modularity, security boundary,
   scalability). Vague goals cannot be governed — "should be maintainable" is not a fitness
   function; "no module may have efferent coupling above 20" is.
2. **Define the objective, measurable test.** Translate the characteristic into a pass/fail
   check with a concrete threshold and a clear unit of measure. Examples:
   - *Maintainability*: cyclomatic complexity per method below a limit; max file/function length.
   - *Modularity / layering*: dependency rules ("`domain` must not depend on `infrastructure`"),
     no cyclic dependencies between packages.
   - *Performance*: p99 latency under a budget; payload size under a cap.
   - *Coupling*: afferent/efferent coupling or instability metric within bounds.
   Each must be *objective* — two people running it get the same verdict.
3. **Classify each function on two axes.** This drives where and how it runs.
   - **Atomic vs holistic**: atomic checks one characteristic in isolation (a single layering
     rule). Holistic checks several interacting characteristics together (security *under*
     load), and exists because some properties only emerge from combination.
   - **Triggered vs continuous**: triggered runs on an event (per commit, per PR, on a schedule);
     continuous runs constantly in production as a monitor (e.g. live latency/SLO alarms).
4. **Pick the right tool per function.** Use static-analysis frameworks for structure and
   dependency rules (ArchUnit for Java/Kotlin, NetArchTest for .NET, `dependency-cruiser` or
   bespoke ESLint rules for TS, Deptrac/PHPArkitect for PHP), complexity tools (lizard,
   radon, ESLint complexity rules) for code metrics, and load/observability tooling (k6,
   Locust, SLO monitors) for runtime budgets. Defer custom lint-rule authoring to
   `agentic-linter.skill`.
5. **Wire triggered functions into CI as governance gates.** Run atomic, fast static checks on
   every PR; run heavier holistic and load-based checks on a schedule or pre-merge. Fail the
   build on violation — an architectural breach is a broken build, not a warning. Order
   cheapest-first to keep PR feedback fast. This is the automated half of
   `architecture-governance.skill`.
6. **Define waivers and continuous monitors.** For continuous functions, wire production
   alarms/SLOs. For unavoidable violations, require an explicit, ticketed, time-boxed waiver
   (an ADR plus a suppression comment referencing it) — never an unaudited silent bypass.
7. **Maintain the suite as a living asset.** Review thresholds when the system legitimately
   evolves, retire functions for retired characteristics, and add new ones for new drivers.
   Stale fitness functions either block valid change or rot into ignored noise.

## Constraints
- A fitness function tests the **characteristic it measures and nothing else**. A green suite
  means "the checked properties hold," not "the architecture is good." Be honest about coverage:
  unmeasured characteristics are ungoverned.
- Functions MUST be objective and deterministic where possible. A check whose verdict depends
  on who ran it or on flaky timing erodes trust and gets disabled.
- Performance/latency budgets sampled in CI are estimates under test conditions, not a
  production guarantee; pair them with continuous production monitors and say so.
- Governance checks MUST fail-closed in CI. If the analysis tool crashes or cannot load its
  ruleset, the pipeline blocks — never treat "tool errored" as "passed."
- Thresholds are engineering judgments, not laws of nature. Record the rationale for each limit
  so future maintainers can adjust it deliberately rather than cargo-cult it.

## Output Format
Produce a **set of fitness functions** following the structure of `FITNESS_FUNCTION_TEMPLATE.md`.
For each function record:
- The architectural characteristic it protects and the concrete metric + threshold (with unit).
- Its classification: atomic/holistic and triggered/continuous.
- The tool/implementation and where it runs (PR gate, scheduled, production monitor).
- The pass/fail criterion and the fail-closed behavior on tool error.
- The waiver policy (ticket + ADR reference) and the rationale for the chosen threshold.
Close with a coverage note listing which characteristics are governed and which remain
unmeasured. Hand the CI-gate wiring to `architecture-governance.skill` and custom rule authoring
to `agentic-linter.skill`.

## Limits and safety
- Threshold and rule files change only with the human's review. If your platform provides CODEOWNERS, use it. Do not raise a threshold or delete a function to turn a build green.
- CI fails closed: a crashed analyser or missing ruleset blocks the pipeline.
- Run every generated rule against a known violation and see it fail; never present an unrun rule as enforcing.
- Report a green suite as "the measured properties hold" and list what is unmeasured.
- A bypass needs a ticketed, time-boxed waiver with an ADR.
