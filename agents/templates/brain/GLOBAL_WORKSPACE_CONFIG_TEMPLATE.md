# Global Workspace Configuration

**For use with `global-workspace.skill.md`**

Use this template to configure the "Consciousness" of a Multi-Agent Swarm.

---

## 1. The Workspace (Blackboard)
**Context Window Strategy:**
- [ ] FIFO (First-In, First-Out)
- [ ] Importance-Weighted (Salience > Time)
- [ ] Summarized (Periodic compression)

**Broadcast Frequency:**
- [ ] Every Step
- [ ] On "Ignition" (Salience > 0.8)

## 2. Specialized Agents (The Unconscious)

| Agent Name | Persona | Expertise (Filter) | Access Level |
|---|---|---|---|
| `Perception` | Log Monitor | `error`, `exception`, `fail` | Read-Only |
| `Memory` | Librarian | `history`, `context`, `docs` | Read-Write |
| `Planner` | Strategist | `goal`, `step`, `next` | Read-Write |
| `Executor` | Coder | `code`, `fix`, `implement` | **Action** |
| `Critic` | Safety Officer | `security`, `bugs`, `risk` | **Veto** |

## 3. Coalition Policy (Competition)

**Salience Function:**
```python
def calculate_salience(msg):
    # Urgency (0-1) + Novelty (0-1) + Relevance (0-1)
    score = (msg.urgency * 0.5) + (msg.novelty * 0.3) + (msg.relevance * 0.2)
    return score
```

**Ignition Threshold:**
- **Local:** `0.0 - 0.6` (Handled by sub-agent)
- **Global:** `> 0.7` (Broadcast to Workspace)

## 4. Initial Context
> [Define the starting state of the workspace here]
