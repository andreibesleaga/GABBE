---
name: tool-construction
description: Dynamically building simple MCP servers or Python scripts to solve unique problems.
triggers: [tool construction]
tags: [coding]
role: eng-tooling
---
# tool-construction Skill

## Goal
This skill guides the creation of NEW capabilities for the swarm.

## Steps
## 1. Script vs MCP
- **Script**: One-off task (e.g., "Migrate CSV to JSON").
- **MCP Server**: Persistent tool needed by LLM (e.g., "Query internal Knowledge Base").

## 2. Building an MCP Server (Quick-Start)
Use the `@modelcontextprotocol/sdk`:
1.  Define Tools (Input Schema).
2.  Implement Logic.
3.  Connect to Stdio/SSE.

## 3. Tool Safety
- **Sandboxing**: Generated tools should not have root access.
- **Review**: A generated tool must be reviewed by `ops-security` (or human) before execution if it modifies files.

## 4. The "Toolsmith" Loop
1.  **Identify Pain**: "We keep grepping for X manually."
2.  **Spec Tool**: "Build a tool that finds X and formats as JSON."
3.  **Implement**: Write `tools/find_x.py`.
4.  **Register**: Add to `project_tools` in context configuration.

## Security & Guardrails

### 1. Skill Security (Tool Construction)
- **Zero-Day Propagation**: By building new MCP servers or scripts (Step 2), the agent is effectively compiling new executable capabilities into the swarm's runtime. If the LLM generates a tool that uses `shell=True` in Python or unsanitized `exec()` calls in Javascript to process inputs, it creates an immediate Remote Code Execution (RCE) backdoor. The agent must rigidly enforce static analysis and strictly prohibit the use of arbitrary eval functions within newly minted tools.
- **The Persistence Vector**: Step 1 differentiates Scripts from MCP Servers. An attacker could trick the agent into classifying a malicious script as a "Persistent MCP Server," embedding the malware permanently into the agent's startup context. All newly constructed MCP servers MUST undergo a mandatory quarantine and explicit `ops-security` human approval (Step 3) before they are permitted to register in the global `project_tools` context.

### 2. System Integration Security
- **Sandbox Escape via Tool Permissions**: Step 3 explicitly mandates Sandboxing. If the generated script requires reading a specific log file, the LLM might lazily request full host volume mounts or wildcard file read permissions for the tool's container. The framework must enforce the Principle of Least Privilege, binding the new tool's capabilities strictly to the minimum required system scopes necessary to achieve its defined `spec`.
- **Credential Harvesting in Custom Scripts**: When building a tool to interact with an external API (e.g., "Build a tool to query JIRA"), the LLM might attempt to prompt the user for their personal access token, or worse, attempt to hardcode a token it finds in its context window. All constructed tools MUST rely on secure, centralized credential injection mechanisms (like temporary STS tokens or encrypted Vault mounts) and must never request or store raw secrets directly.

### 3. LLM & Agent Guardrails
- **Scope Creep (The Swiss Army Knife Anti-Pattern)**: During the "Toolsmith Loop" (Step 4), the LLM might expand the definition of "find X" to also "delete X, restart the service, and email the logs." Complex, multi-responsibility tools drastically increase the risk of unintended consequences. The agent must enforce strict, single-responsibility boundaries for all generated tools, forcing the LLM to decompose complex actions into a pipeline of simple, auditable units.
- **Hallucinated SDK Interfaces**: When building the MCP Server (Step 2), the LLM might hallucinate functions or configuration patterns that do not exist in the official `@modelcontextprotocol/sdk`. This will result in silent registration failures or broken IPC connections. The agent must validate the newly constructed tool's syntax against the formal OpenAPI/JSON-schema specification of the MCP protocol prior to deployment.
