---
name: pbt-strategy
description: Property-based testing with Python Hypothesis — find invariants, write @given strategies, and model stateful systems with RuleBasedStateMachine.
triggers: [write property based tests, find invariants for testing, use hypothesis given strategies, build a rulebasedstatemachine, fuzz json against a schema, shrink to a minimal counterexample]
tags: [coding, testing, hypothesis, property-based-testing, python]
core: false
context_cost: medium
---
# Property-Based Testing Strategy (Hypothesis)

## Goal
Stop hand-picking a few example inputs and instead state the *properties* that must hold for
*all* inputs, then let Hypothesis generate hundreds of diverse cases to attack them. A
property-based test asserts an invariant ("the output is always sorted", "decode(encode(x))
== x") rather than a single example. When it finds a failure, Hypothesis *shrinks* the
counterexample to the smallest input that still breaks the property, handing you a minimal
reproduction. The output of this skill is a **property test plan**: the invariants you will
check, the strategies that generate inputs for them, and — for stateful systems — the state
machine that drives them. Be clear from the start: PBT *samples* the input space to raise
confidence; it does not enumerate it and does not prove correctness.

## Steps
1. **Find the invariants.** Look for properties that hold regardless of the specific input. The
   common families:
   - **Round-trip**: `decode(encode(x)) == x`, `parse(serialize(x)) == x`.
   - **Idempotence**: `f(f(x)) == f(x)` (normalize, dedupe, clamp).
   - **Oracle/equivalence**: a slow-but-obviously-correct reference agrees with the optimized
     implementation; or two code paths that must agree.
   - **Invariant preservation**: an operation never violates a structural rule (a balanced tree
     stays balanced; a total never goes negative; output length never exceeds input).
   - **Metamorphic relations** when there is no oracle for the absolute output — delegate those
     to `metamorphic-testing.skill`.
2. **Write the `@given` strategies.** Generate inputs with Hypothesis strategies
   (`integers()`, `text()`, `lists()`, `dictionaries()`, `builds()`, `composite`). Constrain to
   the *valid* domain with `.filter()` sparingly and `.map()`/`assume()` so generation stays
   efficient — over-filtering makes Hypothesis give up. Compose custom strategies with
   `@composite` for domain objects. Keep each test focused on one invariant.
3. **Fuzz structured data against its schema.** For JSON APIs and configs, use
   `hypothesis-jsonschema`'s `from_schema()` to generate inputs that conform to a JSON Schema,
   then assert your handler never crashes and always returns schema-valid output. This catches
   the edge cases hand-written fixtures miss (empty arrays, unicode, boundary numbers, missing
   optional fields).
4. **Model stateful systems with `RuleBasedStateMachine`.** When behavior depends on a sequence
   of operations (a cache, a queue, a connection pool, a small DB), subclass
   `RuleBasedStateMachine` and let Hypothesis generate *sequences* of actions:
   - `@initialize` seeds starting state once per run.
   - `@rule` defines an action; Hypothesis picks rules and arguments to build random valid
     sequences.
   - `Bundle` holds values produced by one rule (e.g. a created handle) to feed as input to
     later rules, so generated sequences are realistic.
   - `@precondition` gates a rule so it only fires in valid states.
   - `@invariant` is checked after *every* step — the core safety property that must always hold.
   Run it as a normal test; Hypothesis searches for an action sequence that breaks an invariant.
5. **Use shrinking and the example database.** On failure, let Hypothesis shrink to the minimal
   counterexample and read it as your bug report. Pin a found failure with `@example(...)` so it
   becomes a permanent regression case. Keep Hypothesis's example database in CI so previously
   failing inputs are replayed first.
6. **Tune effort honestly.** Set `max_examples` and `deadline` for the time budget; more examples
   = more confidence, never certainty. In CI, raise `max_examples` for critical properties and
   use `derandomize`/a fixed seed only when you need reproducible runs (knowing it narrows the
   search).

## Constraints
- PBT **samples** the input space and **raises confidence**; it does **NOT prove correctness**.
  Unlike formal methods (model checking, proof assistants) which reason over *all* states, a
  passing property test means "no counterexample was found in N sampled cases." State this limit
  in the plan and never claim a property is "proven."
- A property is only as good as its strategy: if the generator never produces the bad input, the
  bug hides. Check the strategy actually covers the domain (use `target()`/coverage if unsure).
- Over-constrained strategies (heavy `.filter()`/`assume()`) cause Hypothesis to abandon
  generation; build valid data directly with `@composite` instead.
- Flaky properties (depending on time, randomness, ordering of external systems) produce
  non-reproducing failures; make the system-under-test deterministic for the test or inject seams.
- Stateful tests grow expensive fast; keep the rule set minimal and the invariant sharp.

## Output Format
Produce a **property test plan** containing:
- The list of invariants, each tagged by family (round-trip / idempotence / oracle /
  invariant-preservation / metamorphic-handoff).
- For each invariant: the Hypothesis strategy (or `from_schema` reference) that generates its
  inputs, and the assertion.
- For stateful components: the `RuleBasedStateMachine` design — rules, bundles, preconditions,
  initialize, and the `@invariant`(s).
- The effort settings (`max_examples`, `deadline`) and any pinned `@example` regression cases.
- An explicit honesty note: the suite samples inputs and raises confidence; it does not prove
  correctness. Cross-reference `metamorphic-testing.skill` for oracle-free relations.

## Security & Guardrails

### 1. Skill Security
- **Risk**: A green property suite is reported as a correctness proof, giving false assurance for
  safety- or security-critical code. Mitigation: every report MUST state PBT samples and does not
  prove; the agent MUST NOT use "property passed" to mean "cannot fail," and MUST recommend formal
  methods where a real proof is required.
- **Risk**: A weak or over-filtered strategy never generates the dangerous input, so the test
  passes vacuously. Mitigation: the agent MUST sanity-check coverage of the strategy (it produces
  edge/boundary/empty/unicode values) and flag any property whose generator cannot reach the
  failure region as low-value.

### 2. System Integration Security
- **Risk**: A stateful or schema-fuzzing test executes real side effects (writes a real DB,
  calls a paid/external API, mutates shared state) and corrupts data or runs up cost. Mitigation:
  run PBT against isolated fixtures, in-memory/transactional fakes, or sandboxes; never point
  generators at production resources, and bound `max_examples` to control blast radius and spend.
- **Risk**: `hypothesis-jsonschema` generates pathological payloads (huge strings, deep nesting)
  that exhaust memory or hang the handler. Mitigation: set `deadline`/size limits in strategies
  and treat resource exhaustion as a finding to fix (input validation), not a test to silence.

### 3. LLM & Agent Guardrails
- **Risk**: The agent invents a plausible but false invariant (asserting a property the spec
  never required), turning the test green while masking real behavior. Mitigation: each invariant
  MUST trace to a stated requirement or contract; the agent MUST mark agent-derived invariants as
  proposed and ask for confirmation before trusting them.
- **Risk**: The agent hallucinates Hypothesis API surface (non-existent strategies or state-machine
  decorators) that errors or silently skips. Mitigation: emit only real, current Hypothesis APIs
  (`@given`, `@rule`, `@initialize`, `@precondition`, `@invariant`, `Bundle`, `from_schema`); the
  agent MUST verify the test actually runs and can fail before presenting it as coverage.
