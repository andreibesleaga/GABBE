# Active Inference Loop Template

**For use with `active-inference.skill.md`**

Use this template to structure your agent's reasoning loop when acting in uncertain environments.

---

## 1. Goal State (Prior Belief)
*What is the "Expected State" where surprise is minimized?*
- **Goal:** [e.g., All unit tests passed]
- **Success Criteria:**
  - [ ] Criteria 1
  - [ ] Criteria 2

## 2. The Loop (Repeat until Success)

### Cycle 1
**step_id**: `1`
**state**: `OBSERVING`

#### A. Prediction (Generative Model)
> "If I perform [Action], I expect [Result]."
- **Action Hypothesis:** `run_command(npm test)`
- **Expected Observation:** "PASS"

#### B. Observation (Sensory Input)
- **Actual Result:** [Paste tool output here]
- **Surprise Level:** [High/Medium/Low]

#### C. Divergence Analysis (Error)
> Why did the prediction fail?
- [ ] **Bad Model:** My understanding of the code was wrong. -> *Update Docs/Plan*
- [ ] **Bad World:** The code is bugged. -> *Active Inference (Fix Code)*

#### D. Resolution (Next Action)
- **Selected Action:** [Tools call]

---

### Cycle 2
...
