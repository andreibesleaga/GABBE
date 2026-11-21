# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import hmac
import json
import logging
import os
import shlex
import subprocess
import sys
from typing import Any

from . import __version__
from .budget import BudgetExceeded
from .context import RunContext
from .gateway import (
    CircuitOpen,
    PolicyDenied,
    RateLimitExceeded,
    ToolDefinition,
    ToolNotFound,
)

logger = logging.getLogger("gabbe.mcp")

# Latest MCP revision this server implements. It is the last revision that opens
# with an `initialize` handshake; the 2026-07-28 revision (protocol version on every
# request, `server/discover`) is not implemented.
MCP_PROTOCOL_VERSION = "2025-11-25"
# Revisions this server accepts in `initialize`; anything else gets the latest of them.
_SUPPORTED_PROTOCOL_VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")

# JSON-RPC 2.0 error codes, plus implementation-defined codes (-32000..-32099).
_PARSE_ERROR = -32700
_INVALID_REQUEST = -32600
_METHOD_NOT_FOUND = -32601
_INVALID_PARAMS = -32602
_INTERNAL_ERROR = -32603
_UNAUTHORIZED = -32000
_POLICY_DENIED = -32001
_TOOL_UNAVAILABLE = -32002  # circuit open, rate limit or budget exhausted

# Input caps, checked before any tracing/redaction/schema work (SW-14): a request
# line above _MAX_LINE_CHARS is refused unparsed; a tools/call line above
# _MAX_CALL_CHARS or with a string argument above _MAX_COMMAND_LEN is refused.
_MAX_LINE_CHARS = 1024 * 1024
_MAX_CALL_CHARS = 64 * 1024

# Hardened input contract for the run_command tool (Track E5). A single source of
# truth used by BOTH the registered ToolDefinition (gateway-enforced via
# jsonschema) and the tools/list inputSchema (what the client sees), so they can
# never drift. The bounds defend against injection-via-tool-feedback and oversized
# payloads (MCP-38 threat taxonomy / NSA MCP guidance):
#   - charset bound: pattern forbids C0 control chars (incl. NUL) and DEL
#   - length bound: maxLength caps the payload
#   - additionalProperties: False rejects unexpected/smuggled fields
_MAX_COMMAND_LEN = 4096
_RUN_COMMAND_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "command": {
            "type": "string",
            "minLength": 1,
            "maxLength": _MAX_COMMAND_LEN,
            "pattern": "^[^\\x00-\\x1f\\x7f]+$",
        }
    },
    "required": ["command"],
    "additionalProperties": False,
}


def _insecure_mode() -> bool:
    """Legacy permissive behavior (no auth, allow-all commands). Opt in ONLY on a
    trusted, isolated host via GABBE_MCP_INSECURE=1. Read live so tests/process
    env changes are honored."""
    return os.environ.get("GABBE_MCP_INSECURE", "").strip().lower() in ("1", "true", "yes")


def _mcp_token() -> str | None:
    # Token clients must send in initialize params. When unset the server is
    # fail-closed (refuses tool calls) unless insecure mode is on.
    return os.environ.get("GABBE_MCP_TOKEN")


def _allowed_commands() -> list[str]:
    raw = os.environ.get("GABBE_MCP_ALLOWED_COMMANDS", "")
    return [c.strip() for c in raw.split(",") if c.strip()]


def _command_timeout() -> int:
    try:
        return int(os.environ.get("GABBE_MCP_COMMAND_TIMEOUT", "300"))
    except ValueError:
        return 300


_authenticated = False  # per-process session flag


def run_command_handler(command: str) -> dict[str, Any]:
    try:
        tokens = shlex.split(command)
    except ValueError as e:
        # Unbalanced quotes etc.: the caller's mistake, not a tool fault.
        return {"stdout": "", "stderr": f"Invalid command: {e}", "returncode": 2}
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
        # Match by EXACT command string or EXACT basename only. The previous
        # `startswith(a + "/")` turned any directory entry into a wildcard — e.g.
        # an allowlist of `/bin` would have permitted /bin/sh, /bin/rm, /bin/wget,
        # i.e. an unrestricted shell escape from a single innocuous-looking entry.
        # Name-based matching (allow `git`, run `git`/`/usr/bin/git`) is the
        # conventional, predictable semantics; directories are never wildcards.
        exe_base = os.path.basename(executable)
        if not any(executable == a or exe_base == a for a in allowed):
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
    except FileNotFoundError:
        return {
            "stdout": "",
            "stderr": f"Command '{tokens[0]}' not found",
            "returncode": 127,
        }
    except OSError as e:
        return {"stdout": "", "stderr": f"Cannot run '{tokens[0]}': {e}", "returncode": 126}
    except subprocess.TimeoutExpired:
        logger.warning("MCP command timed out after %ss: %s", _command_timeout(), tokens[0])
        return {
            "stdout": "",
            "stderr": f"Command timed out after {_command_timeout()}s",
            "returncode": 124,
        }
    return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}


class _RpcError(Exception):
    """A JSON-RPC error to send back for the current request."""

    def __init__(self, code: int, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _reply(req_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _error_reply(req_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def _check_call_size(line_chars: int, args: dict[str, Any]) -> None:
    """Refuse oversize tool calls before the gateway traces or validates them."""
    too_long = any(isinstance(v, str) and len(v) > _MAX_COMMAND_LEN for v in args.values())
    if too_long or line_chars > _MAX_CALL_CHARS:
        raise _RpcError(_INVALID_PARAMS, "Invalid params: arguments exceed the size limit")


def _tool_result(tool_res: Any) -> dict[str, Any]:
    failed = isinstance(tool_res, dict) and tool_res.get("returncode", 0) != 0
    return {"content": [{"type": "text", "text": json.dumps(tool_res)}], "isError": failed}


def _call_tool(ctx: Any, params: dict[str, Any], line_chars: int) -> dict[str, Any]:
    name = params.get("name")
    args = params.get("arguments", {})
    if not isinstance(name, str):
        raise _RpcError(_INVALID_PARAMS, "Invalid params: 'name' must be a string")
    if not isinstance(args, dict):
        raise _RpcError(_INVALID_PARAMS, "Invalid params: 'arguments' must be an object")
    _check_call_size(line_chars, args)
    try:
        tool_res = ctx.gateway.execute(name, args, role="external_agent", run_context=ctx)
    except ToolNotFound:
        raise _RpcError(_INVALID_PARAMS, f"Unknown tool: {name}")
    except ValueError as e:
        raise _RpcError(_INVALID_PARAMS, f"Invalid params: {e}")
    except PolicyDenied as e:
        raise _RpcError(_POLICY_DENIED, str(e))
    except (CircuitOpen, RateLimitExceeded, BudgetExceeded) as e:
        raise _RpcError(_TOOL_UNAVAILABLE, str(e))
    except Exception as e:
        logger.error("MCP tool execution error: %s", e)
        raise _RpcError(_INTERNAL_ERROR, "Internal tool execution error")
    return _tool_result(tool_res)


def _initialize(params: dict[str, Any], token: str | None) -> dict[str, Any]:
    global _authenticated
    if token:
        # Constant-time compare: a short-circuiting `!=` leaks the length of the
        # matching prefix via timing; compare_digest does not.
        if not hmac.compare_digest(str(params.get("token", "")), str(token)):
            raise _RpcError(_UNAUTHORIZED, "Unauthorized")
        _authenticated = True
    wanted = params.get("protocolVersion")
    version = wanted if wanted in _SUPPORTED_PROTOCOL_VERSIONS else MCP_PROTOCOL_VERSION
    return {
        "protocolVersion": version,
        "capabilities": {"tools": {}},
        "serverInfo": {"name": "gabbe-mcp", "version": __version__},
    }


def _list_tools() -> dict[str, Any]:
    tool = {
        "name": "run_command",
        "description": "Run a shell command",
        "inputSchema": _RUN_COMMAND_SCHEMA,
    }
    return {"tools": [tool]}


def _dispatch(
    ctx: Any, method: str, params: dict[str, Any], token: str | None, line_chars: int
) -> dict[str, Any]:
    """Run one request and return its result; raise _RpcError for an error reply."""
    if method == "initialize":
        return _initialize(params, token)
    if method == "ping":
        return {}
    if not _authenticated:
        raise _RpcError(_UNAUTHORIZED, "Unauthorized")
    if method == "tools/list":
        return _list_tools()
    if method == "tools/call":
        return _call_tool(ctx, params, line_chars)
    raise _RpcError(_METHOD_NOT_FOUND, "Method not found")


def _handle_line(ctx: Any, line: str, token: str | None) -> dict[str, Any] | None:
    """Turn one input line into a reply, or None when no reply is allowed."""
    if len(line) > _MAX_LINE_CHARS:
        return _error_reply(None, _INVALID_REQUEST, "Invalid Request: message too large")
    try:
        req = json.loads(line)
    except ValueError:
        return _error_reply(None, _PARSE_ERROR, "Parse error")
    if not isinstance(req, dict):
        return _error_reply(None, _INVALID_REQUEST, "Invalid Request: expected a JSON object")
    notification = "id" not in req  # notifications never get a reply
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})
    try:
        if not isinstance(method, str) or not isinstance(params, dict):
            raise _RpcError(_INVALID_REQUEST, "Invalid Request: bad method or params")
        result = _dispatch(ctx, method, params, token, len(line))
    except _RpcError as e:
        return None if notification else _error_reply(req_id, e.code, e.message)
    except Exception as e:
        logger.error("MCP Server error processing line: %s", e)
        return None if notification else _error_reply(req_id, _INTERNAL_ERROR, "Internal error")
    return None if notification else _reply(req_id, result)


def serve() -> None:
    """JSON-RPC server implementing the MCP Protocol endpoints (stdio)."""
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
                parameters=_RUN_COMMAND_SCHEMA,
                handler=run_command_handler,
                allowed_roles={"external_agent"},
            )
        )

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            res = _handle_line(ctx, line, token)
            if res is not None:
                print(json.dumps(res), flush=True)
