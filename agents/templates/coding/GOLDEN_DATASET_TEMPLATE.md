# Golden Dataset Template

A golden dataset is the small, curated set of input/expected pairs that defines "good"
for a probabilistic system. This template uses a **promptfoo-compatible** YAML shape so
the same file can be run by two harnesses:

- the external `promptfoo` CLI (`npx promptfoo eval`), or
- GABBE's home-grown harness `agents/scripts/eval_skills.py`, which reuses `gabbe/llm.py`
  for model calls instead of promptfoo's provider plumbing.

Keep it small to start (20–50 cases). Every time a real failure is found, add a case here
so it can never silently regress again. Commit and version this file alongside the system
it evaluates.

Each test has `vars:` (the inputs you fill into the prompt) and `assert:` (a list of
checks). Assertion `type:` is one of: `equals`, `contains`, `regex`, `is-json`, `similar`
(embedding similarity, needs a `threshold:`), or `llm-rubric` (LLM-as-judge, takes a
rubric in `value:`).

```yaml
description: "[Golden dataset for <system> — what this set covers]"

prompts:
  # The prompt template(s) under evaluation. {{var}} placeholders are filled from each test's vars.
  - "[Your prompt template here, e.g. 'Summarize the following ticket:\n{{ticket}}']"

providers:
  # promptfoo expects a provider here (e.g. anthropic:messages:claude-...).
  # NOTE: GABBE's home-grown harness (agents/scripts/eval_skills.py) IGNORES this block
  #       and routes all model calls through gabbe/llm.py instead. Keep it only for
  #       promptfoo-CLI compatibility.
  - "[provider id for promptfoo, e.g. anthropic:messages:claude-3-7-sonnet]"

tests:
  # --- Example 1: deterministic assert (Tier 1) ---
  - description: "Exact/structural check — fully deterministic"
    vars:
      ticket: "[input text for this case]"
    assert:
      - type: contains
        value: "[required substring that MUST appear]"
      - type: is-json
        # passes only if the output parses as JSON
      - type: regex
        value: "^TICKET-[0-9]{4}"

  # --- Example 2: semantic similarity assert (Tier 2) ---
  - description: "Meaning matches reference, wording may differ"
    vars:
      ticket: "[input text for this case]"
    assert:
      - type: similar
        value: "[reference answer to compare meaning against]"
        threshold: 0.82   # cosine similarity; case passes only if >= threshold

  # --- Example 3: llm-rubric assert (Tier 3, LLM-as-judge) ---
  - description: "Subjective quality scored by a judge model"
    vars:
      ticket: "[input text for this case]"
    assert:
      - type: llm-rubric
        value: >
          Score the summary 1-5. It must: (a) state the customer's core problem,
          (b) omit PII, (c) be under 3 sentences. Pass only if score >= 4.
        threshold: 0.8   # normalized judge score required to pass
```

Notes:
- This same file is consumed unchanged by either the external `promptfoo` CLI **or**
  GABBE's `agents/scripts/eval_skills.py`. The only field the two harnesses treat
  differently is `providers:` (promptfoo uses it; GABBE substitutes `gabbe/llm.py`).
- Pair this dataset with an `EVAL_PLAN_TEMPLATE.md` (scope, tiers, gating) and, for
  `llm-rubric` asserts, an `EVAL_RUBRIC_TEMPLATE.md` (the judging criteria).
