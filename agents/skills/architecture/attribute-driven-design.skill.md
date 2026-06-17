---
name: attribute-driven-design
description: Drive architecture from quality-attribute scenarios using the iterative ADD 3.0 method, producing a reviewable design workbook.
triggers: [run attribute-driven design, design from quality attribute scenarios, add 3.0 design round, decompose architecture element, choose tactics and patterns, build an add workbook]
tags: [architecture, design, quality-attributes, method]
core: false
context_cost: medium
---
# Attribute-Driven Design (ADD 3.0)

## Goal
Turn architecture from an art into a repeatable, traceable process. Attribute-Driven Design
(ADD 3.0) is a step-by-step method that starts from the system's *drivers* — functional
requirements, quality-attribute scenarios, and constraints — and derives structure through
short iterative rounds. Each round picks one element to refine, selects proven design
concepts (architectural tactics and patterns) to satisfy the drivers, instantiates the
element, sketches the affected views, and records the rationale. The output is an **ADD
workbook** that ties every structural decision back to a driver, so a reviewer can later ask
"why is this here?" and get an answer rather than a shrug.

## Steps
1. **Gather and prioritize the design inputs.** Collect three categories of drivers:
   functional requirements, *quality-attribute scenarios* (each a concrete six-part scenario:
   source, stimulus, environment, artifact, response, response measure — e.g. "under peak
   load, a checkout request returns in <500ms at p99"), and constraints (fixed tech, budget,
   regulatory, team-skill). Prioritize each by business importance and architectural
   difficulty; you cannot satisfy everything, so name the trade-offs explicitly.
2. **Choose the element to decompose this round.** ADD is iterative. Pick the next element to
   refine — the whole system on round 1, then a subsystem, then a module. Decomposing one
   element per round keeps each decision small and reviewable instead of designing the entire
   system in one unaccountable leap.
3. **Select the drivers for this round.** From the prioritized list, choose the subset of
   quality scenarios and constraints that this specific element must address. Record them so
   the round has a clear, bounded objective.
4. **Choose design concepts (tactics + patterns).** Pick the *tactics* (fine-grained design
   decisions that influence one quality attribute — e.g. a cache for performance, a bulkhead
   for availability) and *patterns* (named, reusable structures — e.g. layers, pub/sub,
   pipes-and-filters) that satisfy the selected drivers. For each candidate, note the
   trade-offs it imposes on *other* attributes; a performance tactic often costs modifiability.
   Reuse the catalog in `arch-patterns.skill` and `design-patterns.skill` rather than inventing.
5. **Instantiate the architecture elements.** Apply the chosen concepts: define the concrete
   components, connectors, responsibilities, and interfaces. Assign each selected driver to the
   element(s) responsible for satisfying it so coverage is explicit, not implied.
6. **Sketch the affected views and record decisions.** Update the relevant architecture views
   (module, component-and-connector, allocation/deployment) only where this round changed them.
   Capture every non-obvious choice as a decision record (an ADR via `arch-design.skill`) with
   its driver, the alternatives considered, and the trade-off accepted.
7. **Analyze the round against its drivers.** Before ending the round, verify the instantiated
   element actually satisfies its selected scenarios — walk each scenario through the design,
   or schedule a lightweight review (see `arch-review.skill`). Log unmet drivers and open risks
   as input to the next round. Stop iterating when all high-priority drivers are covered or
   deliberately deferred.

## Constraints
- ADD structures and documents the design; it does **not** guarantee the resulting
  architecture meets its quality scenarios. Verification (measurement, prototyping, review)
  is a separate activity — never report "ADD complete" as "qualities satisfied."
- One element per round. Resist decomposing several elements at once; it destroys the
  traceability that is the method's entire value.
- Every structural decision must trace to at least one driver. A component with no driver is
  either gold-plating or a missing scenario — flag it, do not silently keep it.
- Quality scenarios must be measurable (a response measure), not adjectives. "Fast" and
  "secure" are not scenarios and cannot be designed against or verified.
- Tactics interact: improving one attribute usually degrades another. Record the trade-off; do
  not present a tactic as free.

## Output Format
Produce an **ADD workbook** (one section per iteration round), aligning to the structure in
`ADD_WORKBOOK_TEMPLATE.md`. Each round records:
- The element decomposed and the subset of drivers selected for it.
- The design concepts chosen (tactics + patterns) with their trade-offs.
- The instantiated elements (components, connectors, responsibilities, interfaces) and the
  driver-to-element assignment.
- The view sketches updated this round and the decision records (ADRs) created.
- The round's analysis: which drivers are now satisfied, which remain open, and the risks
  carried forward. Close with a coverage summary mapping every high-priority driver to its
  status (covered / deferred / unmet).

## Security & Guardrails

### 1. Skill Security
- **Risk**: A security or compliance constraint is treated as a soft "nice to have" and
  silently dropped during a design round to simplify the structure. Mitigation: tag security
  and regulatory items as non-negotiable constraints in the driver list; the agent MUST refuse
  to close any round that drops one without an explicit, recorded waiver and human sign-off.
- **Risk**: The workbook is presented as proof the architecture is sound, masking that no
  verification occurred. Mitigation: every round's analysis MUST state whether each driver was
  *verified* (measured/reviewed) or only *addressed* (designed for), and the cover summary MUST
  carry the honest disclaimer that ADD documents intent, not validated behavior.

### 2. System Integration Security
- **Risk**: Security-relevant quality scenarios (authn/authz, data confidentiality, auditability)
  are scattered or absent, so no element is assigned to enforce them. Mitigation: require at
  least one explicit security quality-attribute scenario per trust boundary, and assign each to
  a named responsible element; feed unmet ones into `arch-review.skill` and the threat model.
- **Risk**: A chosen tactic introduces a new external dependency or trust boundary without
  review. Mitigation: any tactic/pattern that adds a third-party component, network hop, or
  shared store MUST be logged as a decision with its new attack surface noted for security review.

### 3. LLM & Agent Guardrails
- **Risk**: The agent hallucinates plausible-sounding quality scenarios or response measures
  the stakeholders never stated, then designs against fiction. Mitigation: every driver MUST be
  sourced to a named stakeholder input or document; the agent MUST mark any agent-proposed
  scenario as "proposed, unconfirmed" and request confirmation before it drives structure.
- **Risk**: The agent invents non-existent tactics or patterns to justify a decision.
  Mitigation: tactics and patterns MUST come from the established catalogs (`arch-patterns.skill`,
  `design-patterns.skill`); the agent MUST NOT present an unrecognized concept as standard
  practice, and MUST label genuinely novel choices as bespoke and unproven.
