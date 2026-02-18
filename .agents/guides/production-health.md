# Production Health & Optimization Guide

> **Goal**: Keep agentic systems stable, cost-effective, and sane in production.

---

## 1. The Recursion Danger (Agentic Loops)

Agents can get stuck in infinite loops ("thought spirals"). The system must detect and break these.

**Detection Strategy:**
1.  **N-Gram Analysis**: Detect if a sequence of tools (e.g., `read_file` -> `edit_file` -> `test`) repeats 3x with same args.
2.  **Semantic Similarity**: Check if "Thought" content is >95% similar to previous steps.
3.  **Cost Velocity**: If spend spikes ($1/min), trigger emergency brake.

**Remediation:**
*   **Trip Circuit Breaker**: Pause execution.
*   **Inject Human**: Send notification: "Agent stuck in loop. Human help needed."
*   **Backoff**: Exponential backoff (1s, 2s, 4s, 8s...).

---

## 2. System Sleep & Scale-to-Zero

Agents shouldn't run 24/7 if no one is watching.

**Sleep Patterns:**
*   **Deep Sleep**: No active triggers. Infrastructure logic scales to 0 (Serverless).
*   **Light Sleep**: Polling interval reduced (e.g., check email every 1h instead of 1m).
*   **Wake-on-LAN/Event**: System wakes only on specific high-priority webhooks (e.g., PagerDuty, GitHub PR).

**Implementation:**
*   Use `ops/production-health.skill.md` logic hooks.
*   Configure Serverless timeouts (AWS Lambda / Cloud Run).

---

## 3. Cost Optimization (FinOps)

**Golden Rules:**
1.  **Model Cascading**: Try cheap model first. If confidence < 0.8, escalate to smart model.
2.  **Context Caching**: Cache the "System Prompt" and "Knowledge Base" headers.
3.  **Summarization**: Don't keep raw logs in context. Summarize logs every 10 steps.

**Daily Limits:**
*   Hard Cap: $50/day (System shuts down).
*   Soft Cap: $25/day (Admin alert).

---

## 4. Self-Healing vs. Looping

Self-healing is good; infinite retry is bad.

**The "5-Attempt Rule":**
*   Attempt 1: Try standard fix.
*   Attempt 2: Try alternative strategy.
*   Attempt 3: Research authoritative docs.
*   Attempt 4: Ask clarifying question.
*   Attempt 5: **STOP**. Report failure to Human.

*Never* attempt 6. Attempt 6 is madness.
