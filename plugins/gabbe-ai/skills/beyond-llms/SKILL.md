---
name: beyond-llms
description: "Combine an LLM with deterministic rules, genetic algorithms or an active-inference loop so hard constraints override model output. Use when a problem needs guaranteed rules, search or optimisation that a prompt alone cannot give."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/ai/beyond-llms.skill.md"
  tags: "ai"
  core: "false"
  context_cost: "high"
---
# beyond-llms

## Goal
Implement and integrate advanced AI methodologies that go beyond basic foundational models, including neuro-symbolic logic, genetic algorithms, or active inference loops.

## Steps
1. **Analyze Constraints**: Determine the problem domain requiring non-LLM or hybrid-AI reasoning.
2. **Design Algorithm**: Combine semantic parsing (LLM) with deterministic rule-engines (symbolic).
3. **Integrate Logic**: Build the hybrid pipeline, ensuring symbolic constraints can override probabilistic LLM outputs.
4. **Verification**: Run extensive tests to verify the symbolic engine successfully enforces hard rules over hallucinatory LLM outputs.

## Constraints
- The rule engine is the authority: a rule failure rejects the LLM output, never the other way round.
- Rules are changed only in code review, never by the model at run time.

## Output Format
The hybrid pipeline code, the rule set as a file under version control, and a test that shows a rule overriding a wrong LLM output.

## Limits and safety
- Set a maximum number of generations or loops, a time limit and a population size for every genetic or active-inference run.
- Run dynamic formulas or generated code from the model in a sandbox, never with eval in the main process.
- The model has no write access to the rule files; check the file permissions or the diff.
- Log which part (LLM or rule engine) made the final decision for each result.
- The rule engine and the reasoner read data through the same access checks and tenant boundaries as the rest of the system; they get no wider read access than the caller has.
