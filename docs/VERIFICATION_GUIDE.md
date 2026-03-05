# GABBE Comprehensive Verification Guide

> **Important**: This guide consolidates all testing and verification processes for the GABBE Agentic R&D Engineering Framework into a single, comprehensive source of truth. Use this to explicitly verify the integrity of the framework and its CLI.

---

## 🏗️ 1. Environment & Setup

Before running tests or launching verifiers, ensure the project development environment is correctly bootstrapped.

### Prerequisites:
- **Python:** versions 3.8 to 3.12 support the GABBE framework and test runners.
- **Node.js**: Expected by specific NPM-based tools or workflows, though Python is the framework root.

### Installation:
```bash
git clone https://github.com/andreibesleaga/GABBE.git
cd GABBE
python -m venv .venv
source .venv/bin/activate       # For Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

*Optionally*, establish environment secrets to verify API-driven paths (Required for executing the `gabbe brain`, `gabbe route`, and specific integration scenarios):
```bash
cp .env.example .env
export GABBE_API_KEY="sk-..."    # Add remote LLM keys for deep integration
```

---

## 🧪 2. Core Python Unit & Integration Testing

The heart of the GABBE orchestration, database integration, memory access, and MCP translation occurs in the `gabbe/` module. The core tests target its routing (`route.py`), budget control (`budget.py`), orchestration logic (`brain.py`), and subprocess checking logic (`verify.py`).

**Run the Full Suite:**
```bash
# This discovers all tests in gabbe/tests and scripts/tests
pytest
```

**What is tested here:**
- **System Boundaries:** Mocked interfaces ensuring GABBE doesn't destroy systems or inject rogue data.
- **Brain Mode Logic:** Ensuring Active Inference iteration thresholds and token bounds are honored.
- **Loki Routing Mode:** Ensuring execution boundaries fall back to `gabbe brain`.
- **MCP Servers:** Parsing of the `gabbe serve-mcp` translation structures.
- **Budgeting:** `GABBE_MAX_COST_USD` hard limits.
- **Audit Traces:** Log structuring within SQLite `audit_spans`.

---

## 📁 3. GABBE Agents/Content Integrity Scripts

Because GABBE relies heavily on markdown context structures (`/agents/skills`, `/agents/templates`, `/agents/guides`), syntax errors or broken internal paths can critically affect agent behavior.

A series of purpose-built Python compilation scripts ensure that your modifications conform precisely to the framework rules. All these scripts are stored in the `agents/scripts/` folder.

**Check Structural Integrity:**
```bash
# Checks if skills, templates, guides are valid and that `agents/AGENTS.md` matches `AGENTS_TEMPLATE.md` structures.
python3 agents/scripts/validate_integrity.py
```

**Verify Internal Links & Logic Chains:**
```bash
# Asserts that [links](myfile.md) all point to valid files. Critical to prevent autonomous agents from hallucinating paths.
python3 agents/scripts/validate_links.py

# Verifies that skills match the specific schemas and headers expected array mapping
python3 agents/scripts/validate_skills.py

# Maps use cases end-to-end to ensure personas properly bridge triggers across skills -> templates
python3 agents/scripts/verify_use_cases.py

# Traverses Prompts + MCP configs to guarantee external calls fit configured APIs
python3 agents/scripts/verify_triggers_and_mcps.py
```

**Run Everything Conditionally:**
```bash
# Alternatively use the umbrella runner to aggregate logs across all the python structural checkers:
bash agents/scripts/setup-context.sh
# Additionally, ensure `init.py` cleanly outputs configured configs for VSCode, Cursor, and Gemini:
python3 scripts/init.py
```

---

## 🖥 4. CLI Architecture Testing (`gabbe verify`)

The CLI Enforcer serves as a powerful programmable integrity checking tool when building external apps. We must confirm the standalone GABBE CLI commands operate identically within an SDLC checkpoint.

**Mock a Workspace Sync & Check Workflow:**

```bash
# 1. Initialize SQLite memory (Required once per new project map)
gabbe init

# 2. Sync CLI Tasks with your markdown files
gabbe sync

# 3. Test the verify loop.
# Note: By design, `gabbe verify` will initially FAIL on fresh projects to prevent unauthorized deployment, 
# primarily throwing execution errors until you fill in [PLACEHOLDER] variables inside `project/TASKS.md` or `AGENTS.md`. 
gabbe verify
```
*Expected Behavior:* If `gabbe verify` produces "Verification FAILED" because of `[PLACEHOLDER:]` elements (like `[PLACEHOLDER: pnpm test]`), the verifier is correctly identifying missing human instruction mapping.

---

## 🤖 5. Simulating Agent Workflows

The ultimate verification requires simulating the system acting as an intelligent agent running either Loki or Brain orchestration.

**Verify Cost Forecaster (CLI):**
```bash
# Ensures history parsing works
gabbe forecast
```

**Verify Subprocess Limits:**
```bash
# This forces testing the CLI execution timeouts limit on `gabbe_subprocess_timeout` rules
export GABBE_SUBPROCESS_TIMEOUT=5 
gabbe verify
```

**Verify Model Context Protocol (MCP) Bind:**
```bash
# Launches the JSON-RPC local server. It should start listening via STDIN/STDOUT.
gabbe serve-mcp
# Cancel using CTRL+C
```

**Run The Evolutionary Pipeline (EPO):**
```bash
# Note: An active GABBE_API_KEY must be exported in your terminal context to test evolution.
# Simulates the neural rewiring of a specific skill prompt based on historic error patterns.
gabbe brain evolve --skill tdd-cycle
```

### Verification Complete
Upon passing the elements noted in **Section 2 (Pytest)** and **Section 3 (Verify Python Scripts)**, the core framework is considered 100% operationally armed and safe to be ingested into your LLM coding environments context.
