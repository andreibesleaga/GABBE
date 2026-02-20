# OODA Loop Trace

**For use with `consciousness-loop.skill.md`**

Use this template to document the "Stream of Consciousness" for critical decisions.

---

## Decision ID: [Unique ID]

### 1. OBSERVE (Sensation)
**Raw Data Inputs:**
- User Request: "..."
- Tool Output: "..."
- System State: "..."

### 2. ORIENT (Perception)
**Contextualization:**
- **Cultural Heritage:** (What do our docs/standards say?)
  - *Ref:* `AGENTS.md` - "Always use TDD"
- **Genetic Heritage:** (What is in my system prompt?)
  - *Ref:* "You are a Senior Engineer"
- **New Information:**
  - "The test failed with a TypeError."

**Synthesis:**
> "I am viewing this error through the lens of a Senior Engineer. The error implies a mismatch in the API contract."

### 3. DECIDE (Hypothesis)
**Alternatives Generation:**
1.  **Option A:** Quick fix (Type cast). *Risk: High Tech Debt.*
2.  **Option B:** Refactor interface. *Risk: Low, but slow.*
3.  **Option C:** Ignore. *Risk: unacceptable.*

**Selection:**
> "I select Option B because it aligns with our 'Clean Code' value."

### 4. ACT (Motor)
**Motor Command:**
- Tool: `replace_file_content`
- Target: `src/interfaces.ts`

**Expected Feedback:**
- "Test suite should pass."
