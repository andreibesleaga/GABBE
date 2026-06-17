# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import logging
import os
import re
import warnings
from pathlib import Path
from typing import Any

logger = logging.getLogger("gabbe.config")


# Paths — PROJECT_ROOT is determined by looking for marker files (project, .git, pyproject.toml)
# upwards from the current working directory.
def _find_project_root(start_path: Path) -> Path:
    current = start_path.resolve()
    for _ in range(10):  # Limit recursion depth
        if (
            (current / "project").exists()
            or (current / ".git").exists()
            or (current / "pyproject.toml").exists()
        ):
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return start_path.resolve()  # Fallback to CWD


PROJECT_ROOT = _find_project_root(Path(os.getcwd()))

# Regex Patterns
PII_PATTERNS = [
    re.compile(r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}"),  # email
    re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b"),  # US phone
    # re.compile(r'\b\d{9}\b'),                               # REMOVED: matches any 9-digit number
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN (dashes)
    re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),  # credit card
    re.compile(r"(?i)\b(?:password|passwd|api[_\-]?key|secret|token)\s*[:=]\s*\S+"),  # credentials
]

# Common API-credential / bearer-token shapes (beyond the assignment form above).
# Shared so that audit redaction, PII routing (route.detect_pii), and the
# ContentSafetyPolicy all recognize the SAME secret formats — otherwise a raw
# `sk-…` / bearer / AWS / GitHub token could route to a REMOTE LLM unredacted.
SECRET_PATTERNS = [
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]+"),
    re.compile(r"\bsk-[A-Za-z0-9_\-]{16,}\b"),  # OpenAI-style keys
    re.compile(r"\bsk-or-v1-[A-Za-z0-9]{16,}\b"),  # OpenRouter keys
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{16,}\b"),  # GitHub tokens
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),  # AWS access key id
]
GABBE_DIR = PROJECT_ROOT / "project"
DB_PATH = GABBE_DIR / "state.db"
TASKS_FILE = PROJECT_ROOT / "project/TASKS.md"

# Agent Config
AGENTS_DIR = PROJECT_ROOT / "agents"


# Dynamic Configuration Loading
# We define base required files here, but this could be extended to load from a JSON manifest.
REQUIRED_FILES = [
    PROJECT_ROOT / "agents/AGENTS.md",
    PROJECT_ROOT / "agents/CONSTITUTION.md",
    PROJECT_ROOT / "project/TASKS.md",
]

# Attempt to load extra config from project/config.json if it exists (Future proofing)
GABBE_CONFIG_FILE = GABBE_DIR / "config.json"
if GABBE_CONFIG_FILE.exists():
    import json

    try:
        with open(GABBE_CONFIG_FILE, "r") as f:
            extra_config = json.load(f)
            # Example: extend required files (paths must stay within PROJECT_ROOT)
            if "required_files" in extra_config:
                project_root_resolved = PROJECT_ROOT.resolve()
                for rf in extra_config["required_files"]:
                    candidate = (PROJECT_ROOT / rf).resolve()
                    try:
                        candidate.relative_to(project_root_resolved)
                        REQUIRED_FILES.append(candidate)
                    except ValueError:
                        warnings.warn(f"Skipping config.json path outside project root: {rf}")
    except Exception as e:
        warnings.warn(f"Failed to load extra config from {GABBE_CONFIG_FILE}: {e}")


# LLM Config
def _load_env_file(env_file: Path) -> None:
    """Load KEY=VALUE pairs from a .env file into os.environ (real env wins).

    Wrapped in a function so loop variables do not leak into the module's
    public namespace (which would otherwise vary with whether a .env exists).
    """
    if not env_file.exists():
        return
    with open(env_file, "r") as f:
        for raw in f:
            stripped = raw.strip()
            if stripped and not stripped.startswith("#"):
                k, sep, v = stripped.partition("=")
                if sep:
                    os.environ.setdefault(k.strip(), v.strip().strip("'\""))


_load_env_file(PROJECT_ROOT / ".env")

GABBE_API_URL = os.environ.get("GABBE_API_URL", "https://api.openai.com/v1/chat/completions")
GABBE_API_KEY = os.environ.get("GABBE_API_KEY")
GABBE_API_MODEL = os.environ.get("GABBE_API_MODEL", "gpt-4o")


def _safe_float(env_var: str, default: float) -> float:
    raw = os.environ.get(env_var, str(default))
    try:
        return float(raw)
    except ValueError:
        logger.warning("Invalid value for %s=%r; using default %s", env_var, raw, default)
        return default


def _safe_int(env_var: str, default: int) -> int:
    raw = os.environ.get(env_var, str(default))
    try:
        return int(raw)
    except ValueError:
        logger.warning("Invalid value for %s=%r; using default %s", env_var, raw, default)
        return default


LLM_TEMPERATURE = _safe_float("GABBE_LLM_TEMPERATURE", 0.7)
# Opt-in: memoize identical deterministic LLM calls to a local content cache
# (zero tokens on a hit). Off by default — only correct for deterministic calls.
GABBE_LLM_CACHE = os.environ.get("GABBE_LLM_CACHE", "false").lower() in ("1", "true", "yes")
LLM_TIMEOUT = max(1, _safe_int("GABBE_LLM_TIMEOUT", 30))
LLM_MAX_RETRIES = max(1, _safe_int("GABBE_LLM_MAX_RETRIES", 3))
LOG_LEVEL = os.environ.get("GABBE_LOG_LEVEL", "INFO").upper()

# Router Config
ROUTE_COMPLEXITY_THRESHOLD = _safe_int("GABBE_ROUTE_THRESHOLD", 50)

# UI Config
PROGRESS_BAR_LEN = 20

# Subprocess timeout for verify commands (test, lint, security_scan) in seconds
SUBPROCESS_TIMEOUT = max(1, _safe_int("GABBE_SUBPROCESS_TIMEOUT", 300))

# MVA Platform Controls
GABBE_MAX_TOKENS_PER_RUN = _safe_int("GABBE_MAX_TOKENS_PER_RUN", 100000)
GABBE_MAX_TOOL_CALLS_PER_RUN = _safe_int("GABBE_MAX_TOOL_CALLS_PER_RUN", 50)
GABBE_MAX_ITERATIONS = _safe_int("GABBE_MAX_ITERATIONS", 25)
GABBE_MAX_WALL_TIME = _safe_int("GABBE_MAX_WALL_TIME", 300)
GABBE_MAX_RECURSION_DEPTH = _safe_int("GABBE_MAX_RECURSION_DEPTH", 5)
GABBE_MAX_RETRIES_PER_TOOL = _safe_int("GABBE_MAX_RETRIES_PER_TOOL", 3)
GABBE_MAX_COST_USD = _safe_float("GABBE_MAX_COST_USD", 5.0)
GABBE_POLICY_FILE = PROJECT_ROOT / os.environ.get("GABBE_POLICY_FILE", "project/policies.yml")
GABBE_ESCALATION_MODE = os.environ.get("GABBE_ESCALATION_MODE", "cli")  # cli, file, silent
GABBE_OTEL_ENABLED = os.environ.get("GABBE_OTEL_ENABLED", "false").lower() == "true"


# Per-project policy the agent + CLI read (runtime-agnostic). project/gabbe.config.json
# may set: autonomy posture, budgets, preferred model tiers, enabled MCPs, registries.
# Loaded best-effort; a malformed file warns and falls back to defaults (never raises).


def _load_project_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        import json

        with open(path, "r") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception as e:  # noqa: BLE001 - config is optional; surface but don't crash
        warnings.warn(f"Failed to load project config {path}: {e}")
        return {}


GABBE_PROJECT_CONFIG_FILE = GABBE_DIR / "gabbe.config.json"
GABBE_PROJECT_CONFIG = _load_project_config(GABBE_PROJECT_CONFIG_FILE)


def _resolve_autonomy() -> str:
    """Autonomy posture precedence: env > project config > default 'hybrid'.

    Valid values: ask | auto | hybrid. Invalid values warn and fall back to hybrid.
    """
    valid = {"ask", "auto", "hybrid"}
    raw = os.environ.get("GABBE_AUTONOMY") or GABBE_PROJECT_CONFIG.get("autonomy") or "hybrid"
    raw = str(raw).strip().lower()
    if raw not in valid:
        logger.warning("Invalid GABBE_AUTONOMY=%r; using 'hybrid'", raw)
        return "hybrid"
    return raw


# ask = always clarify; auto = act when cheap+reversible (still ask for expensive/SOTA/
# irreversible); hybrid (default) = auto-when-cheap, ask-when-expensive.
GABBE_AUTONOMY = _resolve_autonomy()


# Task status constants — single source of truth used across brain, sync, status
TASK_STATUS_TODO = "TODO"
TASK_STATUS_IN_PROGRESS = "IN_PROGRESS"
TASK_STATUS_DONE = "DONE"


# Colors for CLI
class Colors:
    HEADER = "\033[95m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[35m"
    CYAN = "\033[96m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
