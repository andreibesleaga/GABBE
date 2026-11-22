---
name: attribute-driven-design
description: "ADD 3.0 workbook that traces each structural decision to a quality scenario, one element per round. Use when architecture must be derived step by step from drivers and each choice must be explainable."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/architecture/attribute-driven-design.skill.md"
  tags: "architecture, design, quality-attributes, method"
  core: "false"
  context_cost: "medium"
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

## Limits and safety
- Security and regulatory constraints are non-negotiable drivers: a round that drops one needs a recorded waiver and the human's yes.
- Every driver names its source; a scenario the agent proposed is marked "proposed, unconfirmed" until the human confirms it.
- For each driver say whether it was verified (measured or reviewed) or only addressed; the workbook records intent, not proof.
- A tactic that adds a third-party component, network hop or shared store is logged with its new attack surface; keep at least one security scenario per trust boundary.
- Take tactics and patterns from `arch-patterns.skill` and `design-patterns.skill`; label any other choice bespoke and unproven.
