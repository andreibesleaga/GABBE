# Beyond LLMs: Advanced AI Paradigms

**The frontier of Agentic Intelligence in 2026.**

This guide explores paradigms that extend beyond pure Large Language Models, offering Explainability, Evolution, and Epistemic clarity.

---

## 1. Neuro-Symbolic AI (Hybrid)
**The Best of Both Worlds:**
*   **Neural (System 1):** Fast, intuitive, handles fuzzy data (Images, Text).
*   **Symbolic (System 2):** Slow, logical, guarantees correctness (Logic, Math, Rules).

### Application in Engineering
*   **Formal Verification:** LLM translates code to Formal Logic (TLA+ / Coq). Symbolic Prover verifies it.
*   **Constraint Solving:** LLM formulates the problem. SMT Solver (Z3) finds the optimal solution.
*   **Agent Pattern:** The "Judge" (`orch-judge`) should be Neuro-Symbolic, verifying the "Artist's" work against hard rules.

---

## 2. Evolutionary & Genetic Algorithms (GA)
**Code that Evolves.**
Instead of "one-shot" generation, use "Population-based" improvement.

### The "Darwinian Code" Loop
1.  **Population:** Generate 50 variants of a function (`ui-gen` skill).
2.  **Fitness Function:** Run unit tests + performance benchmarks (e.g., execution time).
3.  **Selection:** Keep top 5.
4.  **Crossover/Mutation:** Ask LLM to "Mix strategy A and B" or "Mutate parameter X".
5.  **Repeat:** Until optimal.

*See `brain/learning-adaptation.skill.md` and `brain/self-improvement.skill.md`.*

---

## 3. Active Inference & The Free Energy Principle
**Minimizing Surprise.**
Based on Karl Friston's work. Agents act to confirm their predictions about the world.
*See `brain/active-inference.skill.md`.*

*   **Generative Model:** The Agent maintains a belief state of the Project.
*   **Prediction Error:** The difference between "Expected State" (All tests pass) and "Sensed State" (Build failed).
*   **Action:** The Agent codes *solely* to minimize this Prediction Error.
*   **Epistemic Exploration:** Agent acts not just to fix, but to *learn* ("I will add a log to see what's happening").

---

## 4. Bayesian Networks
**Probabilistic Reasoning.**
LLMs are often overconfident. Bayesian Agents quantify uncertainty.
*   **Application:** Risk Assessment. "There is a 12% probability this refactor breaks the Legacy API."
*   **Pattern:** Update "Priors" based on "Evidence" (Test results).

---

## 5. Implementation Strategy
Do not abandon LLMs. **Orchestrate** them with these paradigms.
*   Use GAs to *prompt* LLMs.
*   Use Symbolic Logic to *filter* LLM outputs.
*   Use Active Inference to *drive* LLM goals.
