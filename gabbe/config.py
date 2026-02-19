import os
from pathlib import Path

# Paths — PROJECT_ROOT is set to the current working directory at import time,
# which is the intended project root when invoking the `gabbe` CLI.
# Tests should patch `gabbe.config.PROJECT_ROOT` (and derivative paths) directly.
PROJECT_ROOT = Path(os.getcwd())
GABBE_DIR = PROJECT_ROOT / ".gabbe"
DB_PATH = GABBE_DIR / "state.db"
TASKS_FILE = PROJECT_ROOT / "TASKS.md"

# Agent Config
AGENTS_DIR = PROJECT_ROOT / ".agents"
SKILLS_DIR = AGENTS_DIR / "skills"
LOKI_DIR = AGENTS_DIR / "loki"

# LLM Config
GABBE_API_URL = os.environ.get("GABBE_API_URL", "https://api.openai.com/v1/chat/completions")
GABBE_API_KEY = os.environ.get("GABBE_API_KEY")
GABBE_API_MODEL = os.environ.get("GABBE_API_MODEL", "gpt-4o")
LLM_TEMPERATURE = float(os.environ.get("GABBE_LLM_TEMPERATURE", "0.7"))
LLM_TIMEOUT = int(os.environ.get("GABBE_LLM_TIMEOUT", "30"))

# Router Config
ROUTE_COMPLEXITY_THRESHOLD = int(os.environ.get("GABBE_ROUTE_THRESHOLD", "50"))

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
