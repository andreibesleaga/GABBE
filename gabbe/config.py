import os
import warnings
from pathlib import Path

# Paths — PROJECT_ROOT is set to the current working directory at import time,
# which is the intended project root when invoking the `gabbe` CLI.
# Tests should patch `gabbe.config.PROJECT_ROOT` (and derivative paths) directly.
PROJECT_ROOT = Path(os.getcwd())

# Regex Patterns
import re
PII_PATTERNS = [
    re.compile(r'[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}'),          # email
    re.compile(r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b'),           # US phone
    # re.compile(r'\b\d{9}\b'),                               # REMOVED: matches any 9-digit number
    re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),                     # SSN (dashes)
    re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),               # credit card
    re.compile(r'(?i)\b(?:password|passwd|api[_\-]?key|secret|token)\s*[:=]\s*\S+'),  # credentials
]
GABBE_DIR = PROJECT_ROOT / ".gabbe"
DB_PATH = GABBE_DIR / "state.db"
TASKS_FILE = PROJECT_ROOT / "TASKS.md"

# Agent Config
AGENTS_DIR = PROJECT_ROOT / ".agents"
SKILLS_DIR = AGENTS_DIR / "skills"
LOKI_DIR = AGENTS_DIR / "loki"

# Dynamic Configuration Loading
# We define base required files here, but this could be extended to load from a JSON manifest.
REQUIRED_FILES = [
    PROJECT_ROOT / ".agents/AGENTS.md",
    PROJECT_ROOT / ".agents/CONSTITUTION.md",
    PROJECT_ROOT / "TASKS.md",
]

# Attempt to load extra config from .gabbe/config.json if it exists (Future proofing)
GABBE_CONFIG_FILE = GABBE_DIR / "config.json"
if GABBE_CONFIG_FILE.exists():
    import json
    try:
        with open(GABBE_CONFIG_FILE, 'r') as f:
            extra_config = json.load(f)
            # Example: extend required files
            if "required_files" in extra_config:
                for rf in extra_config["required_files"]:
                    REQUIRED_FILES.append(PROJECT_ROOT / rf)
    except Exception as e:
        warnings.warn(f"Failed to load extra config from {GABBE_CONFIG_FILE}: {e}")

# LLM Config
GABBE_API_URL = os.environ.get("GABBE_API_URL", "https://api.openai.com/v1/chat/completions")
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
LLM_TIMEOUT = _safe_int("GABBE_LLM_TIMEOUT", 30)

# Router Config
ROUTE_COMPLEXITY_THRESHOLD = _safe_int("GABBE_ROUTE_THRESHOLD", 50)

# UI Config
PROGRESS_BAR_LEN = 20

# Colors for CLI
class Colors:
    HEADER = '\033[95m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[35m'
    CYAN = '\033[96m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
