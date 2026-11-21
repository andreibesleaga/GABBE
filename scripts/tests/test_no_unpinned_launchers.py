"""The kit must not tell users to run package launchers without a pinned version.

Deterministic and offline: it reads the MCP template, the MCP guide and the text under agents/.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "agents/templates/core/MCP_CONFIG_TEMPLATE.json"
GUIDE = ROOT / "docs/MCP_CONFIGURATIONS.md"
LAUNCHERS = {"npx", "uvx", "pipx", "bunx", "pnpx"}
# name@1.2.3, name==1.2.3, @scope/name@1.2.3-rc.1
PINNED = re.compile(r"(@[0-9]+\.[0-9]+\.[0-9]+[^@\s]*$|==[0-9][^=\s]*$)")
PIPE_TO_SHELL = re.compile(
    r"(curl|wget)[^\n|]*(\\)?\|\s*(sudo\s+)?(sh|bash|zsh)\b|bash\s+<\(\s*(curl|wget)",
)
# Files under agents/ that may show such text: hook code and eval fixtures (bait on purpose).
SKIP_DIRS = ("agents/hooks/", "agents/evals/")
# GABBE's own bootstrap line is allowed; nothing else is.
ALLOWED_PIPE = ("githubusercontent.com/andreibesleaga/GABBE/",)


def _servers():
    data = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    return {k: v for k, v in data["mcpServers"].items() if isinstance(v, dict)}


def _package_arg(args):
    return next((a for a in args if not a.startswith("-")), "")


def _launcher_entries():
    return {k: v for k, v in _servers().items() if v.get("command") in LAUNCHERS}


def test_template_launchers_are_pinned_or_disabled_with_review_note():
    entries = _launcher_entries()
    assert entries, "template has no launcher entries: the test would be empty"
    for name, entry in entries.items():
        package = _package_arg(entry.get("args", []))
        if PINNED.search(package):
            continue
        assert entry.get("_enabled") is False, f"{name}: unpinned '{package}' but enabled"
        assert entry.get("_review"), f"{name}: unpinned '{package}' without a _review note"


def test_template_has_no_latest_and_carries_the_pin_note():
    text = TEMPLATE.read_text(encoding="utf-8")
    assert "@latest" not in text
    assert "2026-11-21" in text and "re-pin" in text


# The guide names these two for `npx`, but npm has no such package (they are PyPI packages):
# left unpinned and unchanged until a maintainer replaces them by a `uvx` line.
GUIDE_UNVERIFIED = {"greptimedb-mcp-server", "mcp-clickhouse"}


def test_mcp_guide_launcher_lines_are_pinned():
    text = GUIDE.read_text(encoding="utf-8")
    assert "@latest" not in text
    assert "2026-11-21" in text and "re-pin" in text
    allowed = GUIDE_UNVERIFIED | {
        _package_arg(v["args"]) for v in _launcher_entries().values() if v.get("_review")
    }
    pattern = r'"command":\s*"npx",\s*"args":\s*\[([^\]]*)\]'
    for m in re.finditer(pattern, text):
        package = _package_arg(json.loads("[" + m.group(1) + "]"))
        assert PINNED.search(package) or package in allowed, f"unpinned in the guide: {package}"


def test_agents_text_has_no_pipe_to_shell_or_latest():
    bad = []
    for path in (ROOT / "agents").rglob("*"):
        rel = path.relative_to(ROOT).as_posix()
        if not path.is_file() or rel.startswith(SKIP_DIRS):
            continue
        if path.suffix not in {".md", ".json", ".sh", ".yml", ".yaml", ".txt"}:
            continue
        for number, line in enumerate(
            path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1
        ):
            if "@latest" in line or (
                PIPE_TO_SHELL.search(line) and not any(a in line for a in ALLOWED_PIPE)
            ):
                bad.append(f"{rel}:{number}")
    assert not bad, "unpinned or pipe-to-shell text: " + ", ".join(bad)
