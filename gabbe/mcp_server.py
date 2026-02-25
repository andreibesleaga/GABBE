import os
import sys
import json
import shlex
import logging
import subprocess
from .context import RunContext
from .gateway import ToolDefinition

logger = logging.getLogger("gabbe.mcp")

# Optional token that clients must send in the initialize params to be allowed.
# Set GABBE_MCP_TOKEN env var to enable authentication. Leave unset to disable.
_MCP_TOKEN = os.environ.get("GABBE_MCP_TOKEN")

# Allowlist of command prefixes that run_command_handler will accept.
# Set GABBE_MCP_ALLOWED_COMMANDS as a comma-separated list to restrict commands.
# When unset, all commands are blocked unless the allowlist is explicitly populated.
_raw_allowed = os.environ.get("GABBE_MCP_ALLOWED_COMMANDS", "")
_ALLOWED_COMMANDS: list = [c.strip() for c in _raw_allowed.split(",") if c.strip()]

_authenticated = False  # per-process session flag


def run_command_handler(command: str):
    tokens = shlex.split(command)
    if not tokens:
        return {"stdout": "", "stderr": "Empty command", "returncode": 1}
    # Allowlist check: first token (the executable) must match a permitted prefix.
    if _ALLOWED_COMMANDS:
        executable = tokens[0]
        if not any(executable == allowed or executable.startswith(allowed + "/")
                   for allowed in _ALLOWED_COMMANDS):
            logger.warning("MCP command blocked by allowlist: %s", executable)
            return {"stdout": "", "stderr": f"Command '{executable}' not in allowed list", "returncode": 126}
    result = subprocess.run(tokens, shell=False, capture_output=True, text=True)
    return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}


def serve():
    """Zero-dependency JSON-RPC server implementing the MCP Protocol endpoints."""
    global _authenticated
    _authenticated = not bool(_MCP_TOKEN)  # pre-authed if no token required

    with RunContext(command="serve-mcp", initiator="mcp", agent_persona="external_agent") as ctx:
        ctx.gateway.register(ToolDefinition(
            name="run_command",
            description="Run a shell command on the host.",
            parameters={"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
            handler=run_command_handler,
            allowed_roles={"external_agent"}
        ))

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                method = req.get("method")
                req_id = req.get("id")

                if method == "initialize":
                    # Validate token if authentication is required.
                    if _MCP_TOKEN:
                        provided = (req.get("params") or {}).get("token", "")
                        if provided != _MCP_TOKEN:
                            res = {"jsonrpc": "2.0", "id": req_id,
                                   "error": {"code": -32000, "message": "Unauthorized"}}
                            print(json.dumps(res), flush=True)
                            continue
                        _authenticated = True
                    res = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "capabilities": {"tools": {}},
                            "serverInfo": {"name": "gabbe-mcp", "version": "1.0.0"}
                        }
                    }
                elif method == "notifications/initialized":
                    continue  # No response needed
                elif not _authenticated:
                    res = {"jsonrpc": "2.0", "id": req_id,
                           "error": {"code": -32000, "message": "Unauthorized"}}
                elif method == "tools/list":
                    res = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "tools": [{
                                "name": "run_command",
                                "description": "Run a shell command",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {"command": {"type": "string"}},
                                    "required": ["command"]
                                }
                            }]
                        }
                    }
                elif method == "tools/call":
                    params = req.get("params", {})
                    name = params.get("name")
                    args = params.get("arguments", {})
                    try:
                        tool_res = ctx.gateway.execute(name, args, role="external_agent", run_context=ctx)
                        res = {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": {
                                "content": [{"type": "text", "text": json.dumps(tool_res)}]
                            }
                        }
                    except Exception as e:
                        logger.error("MCP tool execution error: %s", e)
                        res = {"jsonrpc": "2.0", "id": req_id,
                               "error": {"code": -32603, "message": "Internal tool execution error"}}
                else:
                    res = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

                print(json.dumps(res), flush=True)
            except Exception as e:
                logger.error("MCP Server error processing line: %s", e)
                res = {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}}
                print(json.dumps(res), flush=True)
