"""The kit must not tell users to run package launchers without a pinned version.

Covers `npx`-style launchers, `uvx`, `docker run` images (a tag that is not `latest`) and hosted
`http` servers.

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


def _docker_image(args):
    """The image of `docker run ...` (its last argument), or "" for any other docker command."""
    return args[-1] if args and args[0] == "run" else ""


def _docker_entries():
    return {k: v for k, v in _servers().items() if v.get("command") == "docker"}


def _http_entries():
    return {k: v for k, v in _servers().items() if v.get("type") == "http"}


def _image_is_pinned(image):
    name, _, tag = image.rpartition(":")
    return bool(name) and "/" not in tag and tag not in ("", "latest")


def _is_pinned(entry):
    """True when the entry names an exact version: npm/PyPI `@x.y.z` or `==x.y.z`, or an image tag."""
    command, args = entry.get("command"), entry.get("args", [])
    if command == "docker":
        return _image_is_pinned(_docker_image(args))
    return bool(PINNED.search(_package_arg(args)))


def test_template_launchers_are_pinned_or_disabled_with_review_note():
    entries = {**_launcher_entries(), **_docker_entries()}
    assert entries, "template has no launcher entries: the test would be empty"
    for name, entry in entries.items():
        if _is_pinned(entry):
            continue
        assert entry.get("_enabled") is False, f"{name}: no pinned version but enabled"
        assert entry.get("_review"), f"{name}: no pinned version without a _review note"


def test_template_uvx_packages_carry_a_version():
    uvx = {k: v for k, v in _launcher_entries().items() if v["command"] == "uvx"}
    assert uvx, "template has no uvx entries: the test would be empty"
    for name, entry in uvx.items():
        package = _package_arg(entry["args"])
        assert "latest" not in package, f"{name}: uvx package '{package}' is not pinned"
        assert PINNED.search(package), f"{name}: uvx package '{package}' has no version"


def test_template_docker_images_have_a_tag_that_is_not_latest():
    for name, entry in _docker_entries().items():
        image = _docker_image(entry.get("args", []))
        if image:
            assert _image_is_pinned(image), f"{name}: image '{image}' has no tag or uses latest"
        else:  # a docker plug-in command (`docker mcp ...`): its version is the local install's
            assert entry.get("_review") and entry.get("_enabled") is False, name


def test_template_http_entries_are_https_and_name_their_source():
    entries = _http_entries()
    assert entries, "template has no http entries: the test would be empty"
    for name, entry in entries.items():
        assert entry.get("url", "").startswith("https://"), f"{name}: url is not https"
        assert "command" not in entry, f"{name}: both a command and a remote url"
        assert entry.get("_source") or entry.get("_review"), f"{name}: no _source or _review"


def test_template_review_entries_are_disabled_and_checked_on_2026_11_22():
    for name, entry in _servers().items():
        if "_review" in entry and not entry["_review"].startswith("deprecated on npm"):
            assert entry.get("_enabled") is False, f"{name}: _review but enabled"
            assert "2026-11-22" in entry["_review"] or "Docker Desktop" in entry["_review"], name
        if "_source" in entry:
            assert "checked 2026-11-22" in entry["_source"], f"{name}: _source without a date"
        if entry.get("_review", "").startswith("deprecated on npm"):
            assert entry.get("_enabled") is False, f"{name}: deprecated but enabled"


def test_template_has_no_latest_and_carries_the_pin_note():
    text = TEMPLATE.read_text(encoding="utf-8")
    assert "@latest" not in text
    assert "2026-11-21" in text and "2026-11-22" in text and "re-pin" in text


def _guide_blocks(text):
    """Server blocks of the guide: {key: {"command": ..., "args": [...]}} or {"type", "url"}."""
    blocks = {}
    pattern = r'^  "([\w-]+)": \{\n((?:    .*\n|\n)*?)  \}'
    for m in re.finditer(pattern, text, re.M):
        try:
            body = json.loads("{" + m.group(2).rstrip().rstrip(",") + "}")
        except ValueError:
            continue
        if "command" in body or "type" in body:
            blocks[m.group(1)] = body
    return blocks


def test_mcp_guide_launcher_lines_are_pinned():
    text = GUIDE.read_text(encoding="utf-8")
    assert "@latest" not in text
    assert "2026-11-21" in text and "2026-11-22" in text and "re-pin" in text
    unversioned = {k for k, v in _servers().items() if v.get("_review") and not _is_pinned(v)}
    blocks = _guide_blocks(text)
    assert blocks, "no server block found in the guide: the test would be empty"
    for key, body in blocks.items():
        if body.get("command") in LAUNCHERS | {"docker"}:
            if key in unversioned:
                continue
            assert _is_pinned(body), f"unpinned in the guide: {key}"


def test_mcp_guide_launcher_lines_match_the_template():
    servers = _servers()
    blocks = _guide_blocks(GUIDE.read_text(encoding="utf-8"))
    for key, body in blocks.items():
        entry = servers.get(key, {})
        if entry.get("command") not in LAUNCHERS | {"docker"} and entry.get("type") != "http":
            continue  # local builds and absolute paths differ on purpose
        for field in ("command", "args", "type", "url"):
            assert body.get(field) == servers[key].get(field), f"{key}: guide differs in {field}"


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
