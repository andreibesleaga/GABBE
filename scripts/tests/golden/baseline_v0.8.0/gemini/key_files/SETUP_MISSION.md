
I have initialized the GABBE Agentic Engineering Kit for this project.
Here is your mission to finalize the setup:

0. Agent instructions
    - Read AGENTS.md and CONSTITUTION.md for more information on this agentic system.
    - Make sure that the project state, audit, gates, human-in-the-loop, and workflows, are always taken into account.
    - Read agents/guides/ skills/ templates/ for any relevant information discovered during research and added by you or other agents.

1.  **Analyze the Gap**: We are using Python and FastAPI.
    -   Missing Skills: fastapi-best-practices.
    -   Project Type: Greenfield (New).
    -   Compliance: None.

2.  **MCP Configuration**:
    -   Review `agents/templates/core/MCP_CONFIG_TEMPLATE.json`.
    -   Install "Context-7 MCP" (Essential for docs).
    -   If we are using Postgres, install "PostgreSQL MCP".

3.  **Research & Create (Deep Context Mode)**:
    -   **Standards Check**: Research SWEBOK/ISO/IEEE standards relevant to a Greenfield (New) project in Python.
    -   **Gap Analysis**: Compare the installed skills against the specific needs of FastAPI in 2026.
    -   **Generate**: Create key missing skills. Example: `agents/skills/fastapi-best-practices.skill.md`.
    -   **Architectural Pattern**: Identify the best pattern (e.g., Clean Arch, Hexagonal, Vertical Slice) for this stack and document it in `AGENTS.md`.

5.  **Mandatory Guardrails**:
    -   **Ethics**: Run `ai-ethics-compliance` skill on the initial specs.
    -   **Safety**: Install `ai-safety-guardrails` hooks.

6.  **Verify**:
    -   Run `integrity-check` skill to ensure all symlinks and configs are valid.
