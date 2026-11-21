---
name: tool-construction
description: "Build a small script or MCP server for a one-off or recurring task, with one responsibility, least privilege and human review before it runs. Use when the user keeps repeating a manual step or asks for a new tool for the agent."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/coding/tool-construction.skill.md"
  tags: "coding"
  core: "false"
  context_cost: "low"
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
- **Review**: A generated tool that writes, deletes or sends anything is shown to the human and run only after they confirm (the `ops-security` persona may add a review but does not replace the human).

## 4. The "Toolsmith" Loop
1.  **Identify Pain**: "We keep grepping for X manually."
2.  **Spec Tool**: "Build a tool that finds X and formats as JSON."
3.  **Implement**: Write `tools/find_x.py`.
4.  **Register**: Add to `project_tools` in context configuration, only after the human approved the tool.

## Constraints
- One responsibility per tool: a tool that finds X does not also delete X or restart a service.
- A one-off task is a script; build an MCP server only when the LLM needs the tool repeatedly.

## Output Format
The tool's source file (for example `tools/find_x.py` or an MCP server folder), its input schema and the command that runs it.

## Limits and safety
- Generated tools never use `shell=True`, `eval` or `exec` on input; pass argument lists and parse input against a schema.
- Show the source to the human before the first run if the tool writes, deletes or sends anything; register it in `project_tools` only after their yes.
- Give the tool the least access it needs: the one directory or file, no root, no wildcard mounts.
- Take credentials from the environment; never ask the human for a token in chat or hard-code one.
- Check MCP calls against the types of the installed `@modelcontextprotocol/sdk` before relying on them.
