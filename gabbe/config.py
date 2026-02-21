import os
import warnings
from pathlib import Path

# Paths — PROJECT_ROOT is determined by looking for marker files (project, .git, pyproject.toml)
# upwards from the current working directory.
def _find_project_root(start_path):
    current = start_path.resolve()
    for _ in range(10):  # Limit recursion depth
        if (current / "project").exists() or (current / ".git").exists() or (current / "pyproject.toml").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return start_path.resolve()  # Fallback to CWD

PROJECT_ROOT = _find_project_root(Path(os.getcwd()))

# Regex Patterns
import re

PII_PATTERNS = [
    re.compile(r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}"),  # email
    re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b"),  # US phone
    # re.compile(r'\b\d{9}\b'),                               # REMOVED: matches any 9-digit number
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN (dashes)
    re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),  # credit card
    re.compile(
        r"(?i)\b(?:password|passwd|api[_\-]?key|secret|token)\s*[:=]\s*\S+"
    ),  # credentials
]
GABBE_DIR = PROJECT_ROOT / "project"
DB_PATH = GABBE_DIR / "state.db"
TASKS_FILE = PROJECT_ROOT / "project/TASKS.md"

# Agent Config
AGENTS_DIR = PROJECT_ROOT / "agents"
SKILLS_DIR = AGENTS_DIR / "skills"


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
                        warnings.warn(
                            f"Skipping config.json path outside project root: {rf}"
                        )
    except Exception as e:
        warnings.warn(f"Failed to load extra config from {GABBE_CONFIG_FILE}: {e}")

# LLM Config
GABBE_API_URL = os.environ.get(
    "GABBE_API_URL", "https://api.openai.com/v1/chat/completions"
)
GABBE_API_KEY = os.environ.get("GABBE_API_KEY")
GABBE_API_MODEL = os.environ.get("GABBE_API_MODEL", "gpt-4o")


def _safe_float(env_var, default):
    raw = os.environ.get(env_var, str(default))
    try:
        return float(raw)
    except ValueError:
        warnings.warn(f"Invalid value for {env_var}={raw!r}; using default {default}")
        return default


def _safe_int(env_var, default):
    raw = os.environ.get(env_var, str(default))
    try:
        return int(raw)
    except ValueError:
        warnings.warn(f"Invalid value for {env_var}={raw!r}; using default {default}")
        return default


LLM_TEMPERATURE = _safe_float("GABBE_LLM_TEMPERATURE", 0.7)
LLM_TIMEOUT = max(1, _safe_int("GABBE_LLM_TIMEOUT", 30))

# Router Config
ROUTE_COMPLEXITY_THRESHOLD = _safe_int("GABBE_ROUTE_THRESHOLD", 50)

# UI Config
PROGRESS_BAR_LEN = 20

# Subprocess timeout for verify commands (test, lint, security_scan) in seconds
SUBPROCESS_TIMEOUT = max(1, _safe_int("GABBE_SUBPROCESS_TIMEOUT", 300))

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
    ENDC = "\0.2.0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
