---
name: user-research-synthesis
description: Synthesize raw user-research data into personas, a journey map, and prioritized insight statements.
triggers: [synthesize user research, affinity mapping interviews, jobs to be done analysis, build user personas, empathy and journey mapping, write insight statements, prioritize research findings]
tags: [product, research, ux]
core: false
context_cost: medium
---
# User Research Synthesis

## Goal
Convert raw, messy research data — interview notes, survey responses, support transcripts, observation
logs — into structured, decision-ready artifacts: synthesized personas, a journey map, and a prioritized
list of insight statements. Synthesis is the act of finding the signal in noise: turning individual
anecdotes into patterns, and patterns into insights that change what the team builds. The discipline is
staying grounded in evidence so insights are *discovered*, not invented.

## Steps
1. **Tag and affinity-map the raw data.**
   - Break notes into atomic observations (one quote or fact per unit), then cluster by similarity into
     affinity groups. Name each group by the pattern it represents, not the topic it covers.
   - Track how many distinct participants support each cluster — a pattern seen once is an anecdote, a
     pattern seen across many participants is a finding.
2. **Extract Jobs-To-Be-Done (JTBD).**
   - For recurring goals, write job statements in the canonical form: "When [situation], I want to [motivation],
     so I can [expected outcome]." JTBD captures the progress a user is trying to make, independent of any
     specific solution, which keeps the team from over-fitting to current features.
3. **Synthesize personas.**
   - Build personas as composites grounded in the clusters — goals, jobs, pains, and context — not
     demographic stereotypes. Each persona attribute should trace to observed evidence.
   - Keep the set small (2-4); too many personas dilute focus.
4. **Map the journey.**
   - For the primary persona, lay out the end-to-end journey in stages. For each stage capture actions,
     thoughts, emotional highs/lows, and pain points. Mark the moments of greatest friction — these are
     where the journey map earns its keep.
5. **Write insight statements.**
   - Convert findings into insight statements that pair an observation with its implication:
     "We observed [pattern]; this matters because [consequence]; therefore [opportunity]." An insight is
     not a raw fact — it carries a "so what."
6. **Prioritize the insights.**
   - Rank insights by evidence strength (how many participants) and potential impact, separating
     high-confidence, high-impact insights from interesting-but-thin ones.

## Constraints
- Every persona attribute, journey pain point, and insight MUST trace back to observed data; the agent
  MUST NOT invent quotes, metrics, or behaviors to fill gaps, and labels any inferred claim as inference.
- Distinguish what users *say* from what they *do*; weight observed behavior over stated preference when
  they conflict.
- Note the evidence base for each insight (number of participants, method) so consumers can judge how far
  to trust it — a finding from 2 interviews is not the same as one from 30.
- Personas are synthesized composites, never real individuals; do not reproduce a single participant as a
  persona.

## Output Format
Produce a synthesis package containing:
- 2-4 personas, each with goals, primary JTBD statements, key pains, and context, every attribute grounded
  in evidence.
- A journey map for the primary persona: stages with actions, emotions, and flagged friction points.
- A prioritized list of insight statements (observation → implication → opportunity), each tagged with its
  evidence strength (participant count / method) and a confidence level.

## Limits and safety
- Remove names, contact details and recording identifiers before emitting any persona or insight; raw transcripts stay in a restricted working file.
- Personas are composites of several participants; no persona maps to one person.
- Quote only verbatim text from the source, trace each number to data, and mark inference as inference.
- Report contradicting observations and who is missing from the sample; show the participant count, since n=1 is not a pattern.
