# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import hmac
import json
import logging
import os
import shlex
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from . import __version__, config, database, mcp_tools
from .budget import BudgetExceeded
from .context import RunContext
from .gateway import (
    CircuitOpen,
    PolicyDenied,
    RateLimitExceeded,
    ToolDefinition,
    ToolGateway,
    ToolNotFound,
)
from .policy import PolicyEngine

logger = logging.getLogger("gabbe.mcp")

# Two generations of the protocol are served on the same stdio process ("dual-era").
# Legacy (opens with an `initialize` handshake): the newest of these is the default.
MCP_PROTOCOL_VERSION = "2025-11-25"
_SUPPORTED_PROTOCOL_VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")
# Modern (2026-07-28 and later): no handshake; every request carries its protocol
# version in `params._meta` and is served on its own, with no session.
MODERN_PROTOCOL_VERSIONS = ("2026-07-28",)
_META_VERSION = "io.modelcontextprotocol/protocolVersion"
_META_CAPABILITIES = "io.modelcontextprotocol/clientCapabilities"
_META_SERVER_INFO = "io.modelcontextprotocol/serverInfo"
# Where a modern request carries the token (needed only for run_command). Reverse-DNS
# prefix, as the `_meta` key naming rule asks for custom keys.
MCP_TOKEN_META_KEY = "io.github.andreibesleaga.gabbe/token"

# JSON-RPC 2.0 error codes, plus implementation-defined codes (-32000..-32099).
_PARSE_ERROR = -32700
_INVALID_REQUEST = -32600
_METHOD_NOT_FOUND = -32601
_INVALID_PARAMS = -32602
_INTERNAL_ERROR = -32603
_UNAUTHORIZED = -32000
_POLICY_DENIED = -32001
_TOOL_UNAVAILABLE = -32002  # circuit open, rate limit or budget exhausted
_UNSUPPORTED_PROTOCOL_VERSION = -32022  # defined by MCP 2026-07-28

# Input caps, checked before any tracing/redaction/schema work (SW-14): a request
# line above _MAX_LINE_CHARS is refused unparsed; a tools/call line above
# _MAX_CALL_CHARS or with a string argument above _MAX_COMMAND_LEN is refused.
_MAX_LINE_CHARS = 1024 * 1024
_MAX_CALL_CHARS = 64 * 1024
# run_command output kept per stream (stdout, stderr); the rest is cut before the reply
# and before the audit trace.
_MAX_OUTPUT_BYTES = 1024 * 1024

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


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes")


def _insecure_mode() -> bool:
    """Legacy permissive behavior (no auth, allow-all commands) for run_command. Opt in
    ONLY on a trusted, isolated host via GABBE_MCP_INSECURE=1. It does not turn
    run_command on by itself. Read live so tests/process env changes are honored."""
    return _truthy("GABBE_MCP_INSECURE")


def _run_command_env_enabled() -> bool:
    return _truthy("GABBE_MCP_ENABLE_RUN_COMMAND")


def _mcp_token() -> str | None:
    # Token a client must send to use run_command: in `initialize` params (legacy
    # era) or in `_meta` under MCP_TOKEN_META_KEY (modern era). When unset,
    # run_command is refused unless insecure mode is on. Read-only tools need none.
    return os.environ.get("GABBE_MCP_TOKEN")


def _allowed_commands() -> list[str]:
    raw = os.environ.get("GABBE_MCP_ALLOWED_COMMANDS", "")
    return [c.strip() for c in raw.split(",") if c.strip()]


def _command_timeout() -> int:
    try:
        return int(os.environ.get("GABBE_MCP_COMMAND_TIMEOUT", "300"))
    except ValueError:
        return 300


# Environment variables a run_command child process gets (SW-13); the operator can add
# more names in GABBE_MCP_PASS_ENV. Secrets such as GABBE_API_KEY are not passed.
_CHILD_ENV_BASE = ("PATH", "HOME", "LANG", "LC_ALL", "TERM")


def _child_env() -> dict[str, str]:
    extra = [n.strip() for n in os.environ.get("GABBE_MCP_PASS_ENV", "").split(",")]
    names = list(_CHILD_ENV_BASE) + [n for n in extra if n]
    return {n: os.environ[n] for n in names if n in os.environ}


def _entry_matches(entry: str, typed: str, resolved: str | None) -> bool:
    """Does one allow-list entry permit the command the client typed (SW-13)?

    - An absolute entry permits only that exact path.
    - A relative path entry (``./git``) permits nothing.
    - A bare name (``git``) permits the bare command ``git`` and the one path that the
      server's PATH resolves ``git`` to (compared as written, links not followed), but not
      another ``git`` found elsewhere and not another name linked to the same file."""
    if os.path.isabs(entry):
        return resolved is not None and os.path.abspath(resolved) == os.path.normpath(entry)
    if "/" in entry:
        return False
    if typed == entry:
        return True
    canonical = shutil.which(entry)
    if resolved is None or canonical is None:
        return False
    # Links are NOT resolved: busybox-style binaries are one file under many names, and
    # a real-path match would let any of those names stand in for the allowed one.
    return os.path.abspath(resolved) == os.path.abspath(canonical)


def _blocked(stderr: str, code: int = 126) -> dict[str, Any]:
    return {"stdout": "", "stderr": stderr, "returncode": code}


def _allowlist_refusal(typed: str, resolved: str | None) -> dict[str, Any] | None:
    """A refusal result when the allow-list does not permit the command, else None."""
    if _insecure_mode():
        return None
    allowed = _allowed_commands()
    if not allowed:
        logger.warning(
            "MCP command blocked: no allowlist configured (set "
            "GABBE_MCP_ALLOWED_COMMANDS or GABBE_MCP_INSECURE=1)"
        )
        return _blocked(
            "No command allowlist configured; all commands blocked. "
            "Set GABBE_MCP_ALLOWED_COMMANDS."
        )
    if any(_entry_matches(a, typed, resolved) for a in allowed):
        return None
    logger.warning("MCP command blocked by allowlist: %s", typed)
    return _blocked(
        f"Command '{typed}' not in allowed list (an entry must be the bare command name "
        "that the server's PATH resolves, or the exact absolute path)"
    )


def run_command_handler(command: str) -> dict[str, Any]:
    try:
        tokens = shlex.split(command)
    except ValueError as e:
        # Unbalanced quotes etc.: the caller's mistake, not a tool fault.
        return {"stdout": "", "stderr": f"Invalid command: {e}", "returncode": 2}
    if not tokens:
        return {"stdout": "", "stderr": "Empty command", "returncode": 1}
    # Fail-closed: an empty allow-list blocks ALL commands (unless insecure mode is
    # on). Directories are never wildcards; see _entry_matches for the matching rules.
    resolved = shutil.which(tokens[0])
    refusal = _allowlist_refusal(tokens[0], resolved)
    if refusal is not None:
        return refusal
    argv = [resolved] + tokens[1:] if resolved else tokens
    try:
        return _run_capped(argv)
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


def _read_capped(stream: Any) -> tuple[str, bool]:
    """The first _MAX_OUTPUT_BYTES of a captured stream as text, and whether it was cut."""
    stream.seek(0)
    data = stream.read(_MAX_OUTPUT_BYTES + 1)
    cut = len(data) > _MAX_OUTPUT_BYTES
    text = data[:_MAX_OUTPUT_BYTES].decode("utf-8", errors="replace")
    if cut:
        text += f"\n[output cut at {_MAX_OUTPUT_BYTES} bytes]"
    return text, cut


def _run_capped(argv: list[str]) -> dict[str, Any]:
    """Run argv with both streams going to temporary files, so a chatty command cannot fill
    this process's memory; only the first _MAX_OUTPUT_BYTES of each are kept."""
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        code = subprocess.run(
            argv,
            shell=False,
            stdin=subprocess.DEVNULL,
            stdout=out,
            stderr=err,
            timeout=_command_timeout(),
            env=_child_env(),
        ).returncode
        stdout, out_cut = _read_capped(out)
        stderr, err_cut = _read_capped(err)
    result: dict[str, Any] = {"stdout": stdout, "stderr": stderr, "returncode": code}
    if out_cut:
        result["stdout_truncated"] = True
    if err_cut:
        result["stderr_truncated"] = True
    return result


_RUN_COMMAND_ENTRY: dict[str, Any] = {
    "name": "run_command",
    "title": "Run a command",
    "description": "Run a shell command on the host.",
    "inputSchema": _RUN_COMMAND_SCHEMA,
    "annotations": {
        "title": "Run a command",
        "readOnlyHint": False,
        "destructiveHint": True,
        "openWorldHint": True,
    },
}


class _RpcError(Exception):
    """A JSON-RPC error to send back for the current request."""

    def __init__(self, code: int, message: str, data: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data


@dataclass
class _Server:
    """What one stdio process serves: the run context and the operator's choices."""

    ctx: Any
    token: str | None
    run_command: bool  # is run_command registered and listed?
    authenticated: bool = False  # legacy era only: set by a correct `initialize` token


def _reply(req_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _error_reply(
    req_id: Any, code: int, message: str, data: dict[str, Any] | None = None
) -> dict[str, Any]:
    error: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": "2.0", "id": req_id, "error": error}


def _check_call_size(line_chars: int, args: dict[str, Any]) -> None:
    """Refuse oversize tool calls before the gateway traces or validates them."""
    too_long = any(isinstance(v, str) and len(v) > _MAX_COMMAND_LEN for v in args.values())
    if too_long or line_chars > _MAX_CALL_CHARS:
        raise _RpcError(_INVALID_PARAMS, "Invalid params: arguments exceed the size limit")


def _tool_result(tool_res: Any) -> dict[str, Any]:
    if mcp_tools.is_reply(tool_res):
        text, failed = tool_res["mcp_text"], tool_res["mcp_is_error"]
        return {"content": [{"type": "text", "text": text}], "isError": failed}
    failed = isinstance(tool_res, dict) and tool_res.get("returncode", 0) != 0
    return {"content": [{"type": "text", "text": json.dumps(tool_res)}], "isError": failed}


def _known_tools(srv: _Server) -> set[str]:
    names = set(mcp_tools.READ_ONLY_TOOL_NAMES)
    if srv.run_command:
        names.add("run_command")
    return names


def _check_tool_access(srv: _Server, name: str, authed: bool) -> None:
    if name not in _known_tools(srv):
        hint = ""
        if name == "run_command":
            hint = " (run_command is off; start the server with --enable-run-command)"
        raise _RpcError(_INVALID_PARAMS, f"Unknown tool: {name}{hint}")
    if name not in mcp_tools.READ_ONLY_TOOL_NAMES and not authed:
        raise _RpcError(_UNAUTHORIZED, "Unauthorized")


def _call_tool(
    srv: _Server, params: dict[str, Any], line_chars: int, authed: bool
) -> dict[str, Any]:
    name = params.get("name")
    args = params.get("arguments", {})
    if not isinstance(name, str):
        raise _RpcError(_INVALID_PARAMS, "Invalid params: 'name' must be a string")
    if not isinstance(args, dict):
        raise _RpcError(_INVALID_PARAMS, "Invalid params: 'arguments' must be an object")
    _check_tool_access(srv, name, authed)
    _check_call_size(line_chars, args)
    try:
        tool_res = srv.ctx.gateway.execute(name, args, role="external_agent", run_context=srv.ctx)
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


def _server_info() -> dict[str, str]:
    return {"name": "gabbe-mcp", "version": __version__}


def _token_matches(given: Any, expected: str) -> bool:
    """Constant-time token compare on bytes (a non-ASCII str would make compare_digest raise)."""
    return hmac.compare_digest(str(given).encode("utf-8"), str(expected).encode("utf-8"))


def _initialize(
    srv: _Server, params: dict[str, Any], line_chars: int, authed: bool
) -> dict[str, Any]:
    if srv.token:
        # A failed attempt drops an earlier login of this connection (insecure mode stays open).
        srv.authenticated = _insecure_mode()
        if not _token_matches(params.get("token", ""), srv.token):
            raise _RpcError(_UNAUTHORIZED, "Unauthorized")
        srv.authenticated = True
    wanted = params.get("protocolVersion")
    version = wanted if wanted in _SUPPORTED_PROTOCOL_VERSIONS else MCP_PROTOCOL_VERSION
    return {
        "protocolVersion": version,
        "capabilities": {"tools": {}},
        "serverInfo": _server_info(),
    }


def _ping(srv: _Server, params: dict[str, Any], line_chars: int, authed: bool) -> dict[str, Any]:
    return {}


def _list_tools(
    srv: _Server, params: dict[str, Any], line_chars: int, authed: bool
) -> dict[str, Any]:
    tools = [mcp_tools.listing_entry(t) for t in mcp_tools.READ_ONLY_TOOLS]
    if srv.run_command:
        tools.append(_RUN_COMMAND_ENTRY)
    return {"tools": tools}


_INSTRUCTIONS = (
    "Read-only tools for the project's GABBE kit (skills, templates, project status) are "
    "always available. run_command is listed only when the operator enabled it."
)


def _discover(
    srv: _Server, params: dict[str, Any], line_chars: int, authed: bool
) -> dict[str, Any]:
    return {
        "supportedVersions": list(MODERN_PROTOCOL_VERSIONS + _SUPPORTED_PROTOCOL_VERSIONS),
        "capabilities": {"tools": {}},
        "instructions": _INSTRUCTIONS,
    }


_Method = Callable[[_Server, dict[str, Any], int, bool], dict[str, Any]]

# Legacy era: the session is the stdio process; `initialize` opens it.
_LEGACY_METHODS: dict[str, _Method] = {
    "initialize": _initialize,
    "ping": _ping,
    "tools/list": _list_tools,
    "tools/call": _call_tool,
}
# Modern era: every request stands alone (MCP 2026-07-28).
_MODERN_METHODS: dict[str, _Method] = {
    "server/discover": _discover,
    "ping": _ping,
    "tools/list": _list_tools,
    "tools/call": _call_tool,
}
_CACHEABLE = ("server/discover", "tools/list")


def _is_modern(method: str, params: dict[str, Any]) -> bool:
    """A request is modern when it is `server/discover` or carries a protocol version in
    `_meta`; `initialize` is always legacy."""
    if method == "initialize":
        return False
    meta = params.get("_meta")
    return method == "server/discover" or (isinstance(meta, dict) and _META_VERSION in meta)


def _check_modern_meta(meta: Any) -> dict[str, Any]:
    """Validate the per-request `_meta` of a modern request; return it."""
    if not isinstance(meta, dict) or not isinstance(meta.get(_META_VERSION), str):
        raise _RpcError(_INVALID_PARAMS, f"Invalid params: _meta needs '{_META_VERSION}'")
    version = meta[_META_VERSION]
    if version not in MODERN_PROTOCOL_VERSIONS:
        supported = list(MODERN_PROTOCOL_VERSIONS + _SUPPORTED_PROTOCOL_VERSIONS)
        raise _RpcError(
            _UNSUPPORTED_PROTOCOL_VERSION,
            "Unsupported protocol version",
            {"supported": supported, "requested": version},
        )
    if not isinstance(meta.get(_META_CAPABILITIES), dict):
        raise _RpcError(_INVALID_PARAMS, f"Invalid params: _meta needs '{_META_CAPABILITIES}'")
    return meta


def _modern_authed(srv: _Server, meta: dict[str, Any]) -> bool:
    """Per-request authorisation: insecure mode, or the configured token in `_meta`."""
    if _insecure_mode():
        return True
    if not srv.token:
        return False
    return _token_matches(meta.get(MCP_TOKEN_META_KEY, ""), srv.token)


def _modernise(method: str, result: dict[str, Any]) -> dict[str, Any]:
    """Add the fields a modern result must carry (`resultType`, server info, cache hints)."""
    out = {**result, "resultType": "complete", "_meta": {_META_SERVER_INFO: _server_info()}}
    if method in _CACHEABLE:
        out.update({"ttlMs": 0, "cacheScope": "public"})
    return out


def _dispatch(srv: _Server, method: str, params: dict[str, Any], line_chars: int) -> dict[str, Any]:
    """Run one request and return its result; raise _RpcError for an error reply."""
    if _is_modern(method, params):
        meta = _check_modern_meta(params.get("_meta"))
        handler = _MODERN_METHODS.get(method)
        if handler is None:
            raise _RpcError(_METHOD_NOT_FOUND, "Method not found")
        result = handler(srv, params, line_chars, _modern_authed(srv, meta))
        return _modernise(method, result)
    handler = _LEGACY_METHODS.get(method)
    if handler is None:
        raise _RpcError(_METHOD_NOT_FOUND, "Method not found")
    return handler(srv, params, line_chars, srv.authenticated)


def _handle_line(srv: _Server, line: str) -> dict[str, Any] | None:
    """Turn one input line into a reply, or None when no reply is allowed."""
    if len(line) > _MAX_LINE_CHARS:
        return _error_reply(None, _INVALID_REQUEST, "Invalid Request: message too large")
    try:
        req = json.loads(line)
    except (ValueError, RecursionError):  # deep nesting raises RecursionError
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
        result = _dispatch(srv, method, params, len(line))
    except _RpcError as e:
        return None if notification else _error_reply(req_id, e.code, e.message, e.data)
    except Exception as e:
        logger.error("MCP Server error processing line: %s", e)
        return None if notification else _error_reply(req_id, _INTERNAL_ERROR, "Internal error")
    return None if notification else _reply(req_id, result)


# --- start-up: audit trail and tool registration -----------------------------------


class _NullTracer:
    """Stands in for the audit tracer when no project database can be kept."""

    def start_span(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return {}

    def end_span(self, *args: Any, **kwargs: Any) -> None:
        return None


class _OfflineContext:
    """Run context without a database: serves the read-only tools, never run_command."""

    def __init__(self) -> None:
        self.gateway = ToolGateway()
        self.tracer = _NullTracer()
        self.policy = PolicyEngine([])  # read-only tools are exempt; run_command is refused
        self.budget = None


def _database_paths() -> tuple[Path, Path]:
    """The project folder and database file that `get_db` uses (read at call time)."""
    return getattr(database, "GABBE_DIR"), getattr(database, "DB_PATH")


def _audit_problem() -> str | None:
    """Make sure the project database exists and is current; else say why it cannot.

    A folder without `project/` is not turned into a project here (that is what
    `gabbe init` is for); the server then runs without an audit trail and says so.
    The migration is idempotent and prints nothing (stdout carries the protocol)."""
    gabbe_dir, db_path = _database_paths()
    link_problem = database.state_path_problem(gabbe_dir)
    if link_problem:
        return link_problem
    if not gabbe_dir.is_dir():
        return f"there is no project/ folder in {config.PROJECT_ROOT}"
    try:
        database.create_private_file(db_path)
        conn = sqlite3.connect(db_path)
        try:
            database._migrate(conn)
        finally:
            conn.close()
    except (sqlite3.Error, RuntimeError, OSError) as e:
        return f"the project database {db_path} cannot be used ({e})"
    return None


def _refuse_run_command(problem: str) -> Callable[[str], dict[str, Any]]:
    message = (
        f"run_command is refused: {problem}, so its audit trail cannot be kept. "
        "Run `gabbe init` in the project root and restart the server."
    )

    def handler(command: str) -> dict[str, Any]:
        return _blocked(message)

    return handler


def _register_tools(ctx: Any, run_command: bool, problem: str | None) -> None:
    for definition in mcp_tools.tool_definitions():
        ctx.gateway.register(definition)
    if run_command:
        handler = run_command_handler if problem is None else _refuse_run_command(problem)
        ctx.gateway.register(
            ToolDefinition(
                name="run_command",
                description="Run a shell command on the host.",
                parameters=_RUN_COMMAND_SCHEMA,
                handler=handler,
                allowed_roles={"external_agent"},
            )
        )


def _warn_at_start(run_command: bool, token: str | None, insecure: bool) -> None:
    if run_command:
        if insecure:
            logger.warning(
                "GABBE MCP server running in INSECURE mode "
                "(no auth, all commands allowed). Trusted hosts only."
            )
        elif not token and not _allowed_commands():
            logger.warning(
                "GABBE MCP server: run_command is on but refused until you set "
                "GABBE_MCP_TOKEN and GABBE_MCP_ALLOWED_COMMANDS (or GABBE_MCP_INSECURE=1)."
            )
    elif token or insecure or _allowed_commands():
        logger.warning(
            "GABBE MCP server: run_command is OFF by default since 1.2.0, so "
            "GABBE_MCP_TOKEN / GABBE_MCP_ALLOWED_COMMANDS / GABBE_MCP_INSECURE have no "
            "effect. Enable it with `gabbe serve-mcp --enable-run-command` or "
            "GABBE_MCP_ENABLE_RUN_COMMAND=1."
        )


def _next_line(stream: Any) -> str | None:
    """Read one input line holding at most about _MAX_LINE_CHARS characters; None at end.

    A longer line is never held whole: its start is returned (the caller refuses it
    as too large) and the rest of it is read and thrown away, so the next line starts clean."""
    raw: str = stream.readline(_MAX_LINE_CHARS + 2)
    if len(raw) > _MAX_LINE_CHARS and not raw.endswith("\n"):
        rest = stream.readline(_MAX_LINE_CHARS)
        while rest and not rest.endswith("\n"):
            rest = stream.readline(_MAX_LINE_CHARS)
    return raw if raw else None


def _read_loop(srv: _Server) -> None:
    while (raw := _next_line(sys.stdin)) is not None:
        line = raw.strip()
        if not line:
            continue
        res = _handle_line(srv, line)
        if res is not None:
            print(json.dumps(res), flush=True)


def serve() -> None:
    """JSON-RPC server implementing the MCP Protocol endpoints (stdio); see serve_stdio."""
    serve_stdio()


def serve_stdio(enable_run_command: bool = False) -> None:
    """Run the stdio server (what `gabbe serve-mcp` calls).

    The read-only tools are always served. ``run_command`` is registered only when
    ``enable_run_command`` is true or GABBE_MCP_ENABLE_RUN_COMMAND is set; it then
    stays fail-closed (token, command allow-list), as before."""
    run_command = enable_run_command or _run_command_env_enabled()
    insecure = _insecure_mode()
    token = _mcp_token()
    _warn_at_start(run_command, token, insecure)
    # Legacy era: a session is pre-authenticated only in insecure mode; otherwise the
    # client presents the token in `initialize`. Modern requests are judged one by one.
    problem = _audit_problem()
    if problem is not None:
        logger.warning(
            "GABBE MCP server: %s; serving the read-only tools without an audit trail.", problem
        )
        ctx: Any = _OfflineContext()
        _register_tools(ctx, run_command, problem)
        _read_loop(_Server(ctx, token, run_command, authenticated=insecure))
        return
    with RunContext(command="serve-mcp", initiator="mcp", agent_persona="external_agent") as ctx:
        _register_tools(ctx, run_command, None)
        _read_loop(_Server(ctx, token, run_command, authenticated=insecure))
