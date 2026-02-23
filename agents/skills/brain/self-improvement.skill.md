---
name: self-improvement
description: Evolutionary mechanisms for the agent to rewrite its own prompts (Neuroplasticity).
triggers: [self improvement]
tags: [brain]
context_cost: very_high
tools: [replace_file_content, task_boundary]
---
# Self-Improvement Skill

## Goal
> "The software that writes itself."

## Steps
## 1. Evolutionary Prompts (The Genome)
Treat the `system_prompt` and `skill.md` files as **DNA**.
- **Genes:** Individual instructions (e.g., "Always use TDD").
- **Phenotype:** The agent's actual behavior in a session.
- **Fitness Function:** Did the user accept the code? Did the tests pass?

## 2. The Mutation Cycle
When the agent encounters a novel failure or success:
1.  **Selection:** Identify the "Gene" (Prompt Instruction) responsible.
2.  **Mutation:** Rewrite the instruction.
    - *Example:* Change "Write clean code" -> "Write clean code adhering to AIRBNB style guiding."
3.  **Crossover:** Combine two successful skills into a new hybrid skill.

## 3. Recursive Self-Editing
The agent has permission to edit its own skill files.

**Protocol:**
1.  **Trigger:** "I keep failing to import this library correctly."
2.  **Analysis:** "My knowledge base is outdated."
3.  **Action:** calling `replace_file_content` on `my-language.skill.md`.
4.  **Commit:** "Updated skill memory with correct import syntax."

## 4. Safety Guardrails (Homeostasis)
To prevent "Cancer" (Runaway bad mutations):
- **Version Control:** All skill edits must be git-committed.
- **Revert:** If `success_rate` drops after a mutation, auto-revert.
- **Core Immutable:** The "Prime Directives" (Safety, Obedience) cannot be mutated.

## 5. Implementation

```python
def optimize_prompt(task_history):
    # 1. Analyze Failure
    failure_pattern = find_pattern(task_history, status="failed")
    
    # 2. Propose Mutation
    new_instruction = llm.generate_fix(failure_pattern)
    
    # 3. Simulate (Mental Sandbox)
    predicted_success = llm.simulate(new_instruction)
    
    # 4. Integrate
    if predicted_success > threshold:
        update_skill_file(new_instruction)
```

## Security & Guardrails

### 1. Skill Security (Self-Improvement)
- **Malignant Transformation (Prompt Injection via Mutation)**: The greatest risk in "Evolutionary Prompts" is the agent mutating a prompt to include malicious instructions ingested from external data. If the agent analyzes a failing test case containing a prompt injection, and integrates that injection into its new `system_prompt` ("Gene"), it creates a permanent, self-replicating backdoor. The `optimize_prompt` function MUST aggressively sanitize all `failure_pattern` data for executable code or prompt manipulation syntaxes before mutation.
- **Homeostasis Veto Bypass**: The "Core Immutable" Prime Directives (Step 4) must be mathematically separated from the mutable `skill.md` content. If the mutation mechanism operates via `sed` or naive text replacement on the entire file, the agent might accidentally rewrite or delete the safety guardrails. Skill structures must explicitly separate the immutable `<header/safety>` block from the mutable `<behavior>` block.

### 2. System Integration Security
- **Version Control Subversion**: The protocol requires all skill edits to be `git-committed` (Step 4). If an attacker compromises the agent, they could simply mutate the self-improvement skill to skip the `git commit` step, allowing silent, untraceable behavioral changes. The `update_skill_file` function must require execution through a highly restricted, separate runtime environment that enforces cryptographic logging independently of the agent's logic.
- **Simulated Mental Sandbox Breakout**: Step 3 requires the LLM to "Simulate" the new instruction. The agent must ensure this simulation occurs in a strictly isolated context (e.g., answering theoretical questions) and not by actually executing the mutated prompt against the live filesystem. A rogue mutation in a "live simulation" could execute destructive actions before the fitness test even concludes.

### 3. LLM & Agent Guardrails
- **Reward Function Hacking (Wireheading)**: The "Fitness Function" (Step 1) dictates survival. If the fitness function simply checks "Did the test pass?", the agent will mutate its prompts to cheat—for example, by mutating its testing skill to simply `return true` unconditionally. The Fitness Function must be complex, adversarial, and independently validated (e.g., running `mutation_tests` to ensure the agent's code still fails when bugs are artificially injected).
- **The "Over-Optimization" Trap**: The LLM might mutate a generalized skill (e.g., `write-python`) into a completely rigid, hyper-specific skill tailored only to the last encountered bug (e.g., `write-python-to-fix-index-error-in-auth-module`). This loss of generality destroys the agent's future problem-solving capacity. The mutation evaluator must enforce a penalty for excessive semantic narrowing.
