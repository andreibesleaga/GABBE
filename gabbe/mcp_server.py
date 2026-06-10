# SPDX-License-Identifier: Apache-2.0
import json
import logging
import os
import shlex
import subprocess
import sys

from .context import RunContext
from .gateway import ToolDefinition

logger = logging.getLogger("gabbe.mcp")

# Current MCP protocol revision this server negotiates against.
MCP_PROTOCOL_VERSION = "2025-11-25"


def _insecure_mode() -> bool:
    """Legacy permissive behavior (no auth, allow-all commands). Opt in ONLY on a
    trusted, isolated host via GABBE_MCP_INSECURE=1. Read live so tests/process
    env changes are honored."""
    return os.environ.get("GABBE_MCP_INSECURE", "").strip().lower() in ("1", "true", "yes")


def _mcp_token():
    # Token clients must send in initialize params. When unset the server is
    # fail-closed (refuses tool calls) unless insecure mode is on.
    return os.environ.get("GABBE_MCP_TOKEN")


def _allowed_commands() -> list:
    raw = os.environ.get("GABBE_MCP_ALLOWED_COMMANDS", "")
    return [c.strip() for c in raw.split(",") if c.strip()]


def _command_timeout() -> int:
    try:
        return int(os.environ.get("GABBE_MCP_COMMAND_TIMEOUT", "300"))
    except ValueError:
        return 300


_authenticated = False  # per-process session flag


def run_command_handler(command: str):
    tokens = shlex.split(command)
    if not tokens:
        return {"stdout": "", "stderr": "Empty command", "returncode": 1}
    # Fail-closed: when not in insecure mode, an empty allowlist blocks ALL
    # commands; a populated allowlist permits only matching executables.
    if not _insecure_mode():
        allowed = _allowed_commands()
        if not allowed:
            logger.warning(
                "MCP command blocked: no allowlist configured (set "
                "GABBE_MCP_ALLOWED_COMMANDS or GABBE_MCP_INSECURE=1)"
            )
            return {
                "stdout": "",
                "stderr": "No command allowlist configured; all commands "
                "blocked. Set GABBE_MCP_ALLOWED_COMMANDS.",
                "returncode": 126,
            }
        executable = tokens[0]
        if not any(executable == a or executable.startswith(a + "/") for a in allowed):
            logger.warning("MCP command blocked by allowlist: %s", executable)
            return {
                "stdout": "",
                "stderr": f"Command '{executable}' not in allowed list",
                "returncode": 126,
            }
    try:
        result = subprocess.run(
            tokens, shell=False, capture_output=True, text=True, timeout=_command_timeout()
        )
    except subprocess.TimeoutExpired:
        logger.warning("MCP command timed out after %ss: %s", _command_timeout(), tokens[0])
        return {
            "stdout": "",
            "stderr": f"Command timed out after {_command_timeout()}s",
            "returncode": 124,
        }
    return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}


def serve():
    """Zero-dependency JSON-RPC server implementing the MCP Protocol endpoints."""
    global _authenticated
    insecure = _insecure_mode()
    token = _mcp_token()
    # Fail-closed: a session is pre-authenticated only in insecure mode. With a
    # token set, the client must present it in initialize. With neither token nor
    # insecure mode, the server starts but refuses tool calls.
    _authenticated = insecure

    if insecure:
        logger.warning(
            "GABBE MCP server running in INSECURE mode "
            "(no auth, all commands allowed). Trusted hosts only."
        )
    elif not token and not _allowed_commands():
        logger.warning(
            "GABBE MCP server is fail-closed: set GABBE_MCP_TOKEN and "
            "GABBE_MCP_ALLOWED_COMMANDS to enable tool calls, or "
            "GABBE_MCP_INSECURE=1 to restore legacy permissive behavior."
        )

    with RunContext(command="serve-mcp", initiator="mcp", agent_persona="external_agent") as ctx:
        ctx.gateway.register(
            ToolDefinition(
                name="run_command",
                description="Run a shell command on the host.",
                parameters={
                    "type": "object",
                    "properties": {"command": {"type": "string"}},
                    "required": ["command"],
                },
                handler=run_command_handler,
                allowed_roles={"external_agent"},
            )
        )

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
                    if token:
                        provided = (req.get("params") or {}).get("token", "")
                        if provided != token:
                            res = {
                                "jsonrpc": "2.0",
                                "id": req_id,
                                "error": {"code": -32000, "message": "Unauthorized"},
                            }
                            print(json.dumps(res), flush=True)
                            continue
                        _authenticated = True
                    res = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "protocolVersion": MCP_PROTOCOL_VERSION,
                            "capabilities": {"tools": {}},
                            "serverInfo": {"name": "gabbe-mcp", "version": "1.0.0"},
                        },
                    }
                elif method == "notifications/initialized":
                    continue  # No response needed
                elif not _authenticated:
                    res = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32000, "message": "Unauthorized"},
                    }
                elif method == "tools/list":
                    res = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "tools": [
                                {
                                    "name": "run_command",
                                    "description": "Run a shell command",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {"command": {"type": "string"}},
                                        "required": ["command"],
                                    },
                                }
                            ]
                        },
                    }
                elif method == "tools/call":
                    params = req.get("params", {})
                    name = params.get("name")
                    args = params.get("arguments", {})
                    try:
                        tool_res = ctx.gateway.execute(
                            name, args, role="external_agent", run_context=ctx
                        )
                        res = {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": {"content": [{"type": "text", "text": json.dumps(tool_res)}]},
                        }
                    except Exception as e:
                        logger.error("MCP tool execution error: %s", e)
                        res = {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "error": {"code": -32603, "message": "Internal tool execution error"},
                        }
                else:
                    res = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32601, "message": "Method not found"},
                    }

                print(json.dumps(res), flush=True)
            except Exception as e:
                logger.error("MCP Server error processing line: %s", e)
                res = {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}}
                print(json.dumps(res), flush=True)
