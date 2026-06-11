---
name: sensory-motor
description: Embodied cognition patterns for treating tools as muscles and inputs as senses.
triggers: [sensory motor]
tags: [brain]
context_cost: medium
tools: [run_command, read_file]
---
# Sensory-Motor Skill (Embodied Cognition)

> "Intelligence is not a brain in a jar; it is a body in a world."

## 1. The Body Schema (Proprioception)
An agent must know the state of its "body" (tools + context).
- **Senses:** `read_file`, `list_dir`, `search_web`.
- **Muscles:** `write_to_file`, `run_command`, `replace_file_content`.
- **Proprioception:** "Do I have write access here?", "Is the linter running?", "What's my cwd?"

## 2. Multimodal Binding (Perception)
Inputs are "percepts" to bind together, not just strings: **Visual** (screenshots, images), **Auditory** (TTS logs), **Symbolic** (code, JSON). **Binding problem:** integrate `Visual(error screenshot)` + `Symbolic(log file)` into a unified `Concept(System Failure)`.

## 3. Optimal Feedback Control (Action)
Don't fire-and-forget — control the "limb" (tool) continuously: (1) **motor command** `run_command(npm test)`; (2) **sensory feedback** "taking too long..."; (3) **correction** `send_command_input(Ctrl+C)` (reflex arc).

## 4. System Prompt Parameters
```markdown
### Body State (Proprioception)
- Muscles Available: [Bash, Python, FileSystem]
- Senses Active: [Linter, TestRunner, Browser]
- Health: [Filesystem: RW, Network: Connected]

### Motor Control Policy
"I will not just execute; I will monitor. If a tool fails (muscle failure) I will not hallucinate success — I will acknowledge the physical limitation and try a different strategy."
```

## 5. Implementation Example
```python
def execute_motor_command(command):
    expected_duration = estimate_duration(command)   # forward model: predict outcome
    process = subprocess.Popen(command)              # motor command
    start_time = time.time()
    while process.poll() is None:                    # feedback loop (OFC)
        if time.time() - start_time > expected_duration * 1.5:
            process.kill()                           # reflex: abort
            raise MotorError("Muscle fatigue (Timeout)")
    return process.returncode
```

## Security & Guardrails

### 1. Skill Security (Sensory-Motor)
- **Motor Command Escalation (Muscle Spasms)**: given `Bash` as a muscle, an LLM may run concatenated commands (`cmd1 && cmd2 || rm -rf /`). Clamp motor commands to singular well-defined tools, parsing and validating each command string against a strict allow-list before execution.
- **Multimodal Perception Poisoning**: attackers can embed instructions invisibly in screenshots (steganography/faint text) or inject XSS into logs. Treat all raw sensory input as toxic; enforce a rigorous sanitization boundary before binding into the central `Concept` state.

### 2. System Integration Security
- **Proprioceptive Spoofing (Body Transfer Illusion)**: manipulating env vars or mock filesystem responses can trick the agent into believing it has root, causing impossible plans and a failure-loop DoS. The framework must supply cryptographically verified environment state to the agent's context.
- **Reflex Arc Override Delay**: the timeout reflex (`process.kill()`) won't stop a fast-but-destructive op (`truncate -s 0 database.sqlite`) that completes before the timeout fires. Reflex arcs are for hang prevention only — not a substitute for pre-execution authorization.

### 3. LLM & Agent Guardrails
- **Sensory Hallucination (Phantom Internals)**: the LLM may hallucinate feedback that never occurred (commands `npm test`, it crashes, but the LLM proceeds as if tests passed). The pipeline must physically block subsequent `Thought:` tokens until the real `Observation:` token is injected by the environment.
- **Tool Blindness (Learned Helplessness)**: after a muscle (e.g. `search_web`) fails on transient errors, the LLM may internally deprecate it as unavailable. Routinely reset "Body State" assertions at task boundaries so transient errors don't become permanent phantom-limb syndromes.
