# SPDX-License-Identifier: Apache-2.0
"""Read-only tools of the GABBE MCP server (on by default).

They answer questions about the kit of the project the server was started in:
the skills and templates under ``<project root>/agents`` and the state under
``<project root>/project``. They change nothing, need no token and no command
allow-list, and never read a file whose real path is outside those two folders
(links included). Text they return is capped at ``MAX_TEXT_BYTES``.

Every handler returns a reply made by :func:`reply`; it never raises, so a bad
request is a normal tool result with ``isError: true`` and a sentence that says why.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from . import config
from .gateway import ReadOnlyToolDefinition, ToolDefinition
from .sync import parse_markdown_tasks

# Largest text one tool call returns (bytes). Longer text is cut with a note.
MAX_TEXT_BYTES = 64 * 1024
_MAX_DESCRIPTION_CHARS = 240  # per skill, in listings
_MAX_SEARCH_RESULTS = 50
_DEFAULT_SEARCH_RESULTS = 10
_NAME_PATTERN = "^[A-Za-z0-9][A-Za-z0-9._-]*$"
_SKILL_SUFFIX = ".skill.md"

_Handler = Callable[..., dict[str, Any]]


# --- replies -----------------------------------------------------------------


def reply(text: str, is_error: bool = False) -> dict[str, Any]:
    """A tool reply: text for the client and whether it is a tool error."""
    return {"mcp_text": text, "mcp_is_error": is_error}


def is_reply(value: Any) -> bool:
    return isinstance(value, dict) and "mcp_text" in value and "mcp_is_error" in value


def _json_reply(payload: dict[str, Any]) -> dict[str, Any]:
    return reply(json.dumps(payload, indent=2, ensure_ascii=False))


# --- confinement ---------------------------------------------------------------


def _root() -> Path:
    return Path(config.PROJECT_ROOT).resolve()


def _allowed_bases() -> list[Path]:
    root = _root()
    return [root / "agents", root / "project"]


def _confined(path: Path) -> bool:
    """True when the real path of ``path`` lies inside agents/ or project/ of the root."""
    try:
        real = path.resolve()
    except (OSError, RuntimeError):
        return False
    for base in _allowed_bases():
        try:
            real.relative_to(base)
            return True
        except ValueError:
            continue
    return False


def _kit_dir(*parts: str) -> Path:
    return _root().joinpath("agents", *parts)


def _missing_kit(what: str, where: Path) -> dict[str, Any]:
    return reply(
        f"No {what} found: looked in {where}. The server reads the kit of the folder it was "
        "started in; run `gabbe init` there or start the server from the project root.",
        is_error=True,
    )


def _read_capped(path: Path) -> tuple[str, int, bool]:
    """Read at most MAX_TEXT_BYTES of a file: (text, file size, was cut)."""
    size = path.stat().st_size
    with path.open("rb") as fh:
        data = fh.read(MAX_TEXT_BYTES)
    text = data.decode("utf-8", errors="replace")
    return text, size, size > MAX_TEXT_BYTES


def _capped_text(path: Path) -> dict[str, Any]:
    try:
        text, size, cut = _read_capped(path)
    except OSError as e:
        return reply(f"Cannot read {path.name}: {e.strerror or e}.", is_error=True)
    if cut:
        text += f"\n\n[Cut at {MAX_TEXT_BYTES} bytes; the file has {size} bytes.]"
    return reply(text)


# --- skills --------------------------------------------------------------------


@dataclass(frozen=True)
class _Skill:
    name: str
    description: str
    category: str
    triggers: tuple[str, ...]
    path: Path


def _split_list(raw: str) -> tuple[str, ...]:
    inner = raw.strip()
    if inner.startswith("[") and inner.endswith("]"):
        inner = inner[1:-1]
    parts = (p.strip().strip("'\"") for p in inner.split(","))
    return tuple(p for p in parts if p)


def parse_frontmatter(text: str) -> dict[str, str]:
    """Read the ``key: value`` lines between the first two ``---`` lines (no YAML library)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    meta: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, sep, value = line.partition(":")
        if sep and key and not key[0].isspace():
            meta[key.strip()] = value.strip().strip("'\"")
    return meta


def _load_skill(path: Path, skills_dir: Path) -> _Skill | None:
    try:
        text, _, _ = _read_capped(path)
    except OSError:
        return None
    meta = parse_frontmatter(text)
    stem = path.name[: -len(_SKILL_SUFFIX)]
    rel = path.relative_to(skills_dir)
    return _Skill(
        name=meta.get("name") or stem,
        description=meta.get("description", ""),
        category=rel.parts[0] if len(rel.parts) > 1 else "",
        triggers=_split_list(meta.get("triggers", "")),
        path=path,
    )


def _skill_files(skills_dir: Path) -> list[Path]:
    files = sorted(skills_dir.rglob("*" + _SKILL_SUFFIX))
    return [f for f in files if f.is_file() and _confined(f)]


def _skills() -> list[_Skill] | None:
    """All skills of the kit, or None when the kit has no readable skills folder."""
    skills_dir = _kit_dir("skills")
    if not skills_dir.is_dir() or not _confined(skills_dir):
        return None
    loaded = (_load_skill(f, skills_dir) for f in _skill_files(skills_dir))
    return [s for s in loaded if s is not None]


def _rel(path: Path) -> str:
    return path.relative_to(_root()).as_posix()


def _brief(skill: _Skill) -> dict[str, str]:
    description = skill.description
    if len(description) > _MAX_DESCRIPTION_CHARS:
        description = description[: _MAX_DESCRIPTION_CHARS - 1] + "…"
    return {
        "name": skill.name,
        "description": description,
        "category": skill.category,
        "path": _rel(skill.path),
    }


def _fit_listing(items: list[dict[str, str]], extra: dict[str, Any]) -> dict[str, Any]:
    """A JSON reply listing ``items``, dropping items from the end until it fits the cap."""
    kept = list(items)
    while True:
        payload = {**extra, "count": len(kept), "skills": kept}
        if len(kept) < len(items):
            payload["truncated"] = (
                f"Showing {len(kept)} of {len(items)}; the reply is capped at "
                f"{MAX_TEXT_BYTES} bytes. Pass a category or use search_skills."
            )
        text = json.dumps(payload, indent=2, ensure_ascii=False)
        if len(text.encode("utf-8")) <= MAX_TEXT_BYTES or not kept:
            return reply(text)
        del kept[len(kept) * 9 // 10 :]


def list_skills(category: str = "") -> dict[str, Any]:
    skills = _skills()
    if skills is None:
        return _missing_kit("skills folder", _kit_dir("skills"))
    chosen = [s for s in skills if not category or s.category == category]
    if category and not chosen:
        known = sorted({s.category for s in skills if s.category})
        return reply(f"No skills in category '{category}'. Categories: {', '.join(known)}.", True)
    return _fit_listing([_brief(s) for s in chosen], {})


def _find_skill(skills: list[_Skill], name: str) -> list[_Skill]:
    exact = [s for s in skills if s.name == name]
    if exact:
        return exact
    return [s for s in skills if s.path.name[: -len(_SKILL_SUFFIX)] == name]


def read_skill(name: str) -> dict[str, Any]:
    skills = _skills()
    if skills is None:
        return _missing_kit("skills folder", _kit_dir("skills"))
    found = _find_skill(skills, name)
    if not found:
        return reply(f"No skill named '{name}'. Use list_skills or search_skills.", True)
    if len(found) > 1:
        paths = ", ".join(_rel(s.path) for s in found)
        return reply(f"The name '{name}' matches several skills: {paths}.", True)
    return _capped_text(found[0].path)


def _score(skill: _Skill, terms: list[str]) -> int:
    name, description = skill.name.lower(), skill.description.lower()
    triggers = " ".join(skill.triggers).lower()
    score = 0
    for term in terms:
        score += 5 * (term in name) + 3 * (term in description) + 2 * (term in triggers)
    return score


def search_skills(query: str, limit: int = _DEFAULT_SEARCH_RESULTS) -> dict[str, Any]:
    skills = _skills()
    if skills is None:
        return _missing_kit("skills folder", _kit_dir("skills"))
    terms = query.lower().split()
    scored = [(s, _score(s, terms)) for s in skills]
    ranked = sorted((p for p in scored if p[1] > 0), key=lambda p: (-p[1], p[0].name))
    top = ranked[: max(1, min(limit, _MAX_SEARCH_RESULTS))]
    items = [{**_brief(s), "score": str(score)} for s, score in top]
    return _fit_listing(items, {"query": query, "matches": len(ranked)})


# --- templates -----------------------------------------------------------------


def _template_files() -> list[Path] | None:
    base = _kit_dir("templates")
    if not base.is_dir() or not _confined(base):
        return None
    return [f for f in sorted(base.rglob("*")) if f.is_file() and _confined(f)]


def _template_matches(files: list[Path], name: str) -> list[Path]:
    wanted = name.lower()
    return [f for f in files if f.name.lower() == wanted or f.stem.lower() == wanted]


def get_template(name: str) -> dict[str, Any]:
    files = _template_files()
    if files is None:
        return _missing_kit("templates folder", _kit_dir("templates"))
    found = _template_matches(files, name)
    if not found:
        sample = ", ".join(sorted({f.stem for f in files})[:30])
        return reply(f"No template named '{name}'. Some templates: {sample}.", True)
    if len(found) > 1:
        return reply(
            f"The name '{name}' matches several templates: {', '.join(_rel(f) for f in found)}.",
            True,
        )
    return _capped_text(found[0])


# --- project status --------------------------------------------------------------


def _read_small(path: Path) -> str | None:
    """Text of a file inside the allowed folders, or None when absent or outside."""
    if not path.is_file() or not _confined(path):
        return None
    try:
        return _read_capped(path)[0]
    except OSError:
        return None


def _phase_fields(text: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for label in ("Current Phase", "Phase Status"):
        match = re.search(rf"\|\s*\*\*{label}\*\*\s*\|\s*([^|\n]*?)\s*\|", text)
        if match:
            found[label] = match.group(1)
    return found


def _task_counts(text: str) -> dict[str, int]:
    counts = {"TODO": 0, "IN_PROGRESS": 0, "DONE": 0}
    for task in parse_markdown_tasks(text):
        counts[task["status"]] = counts.get(task["status"], 0) + 1
    counts["total"] = sum(counts.values())
    return counts


def project_status() -> dict[str, Any]:
    root = _root()
    state = _read_small(root / "agents" / "memory" / "PROJECT_STATE.md")
    tasks = _read_small(root / "project" / "TASKS.md")
    missing = []
    if state is None:
        missing.append("agents/memory/PROJECT_STATE.md is missing: no phase is recorded.")
    if tasks is None:
        missing.append("project/TASKS.md is missing: no tasks are recorded.")
    if state is None and tasks is None:
        return reply(
            f"No GABBE project state found: looked for {root / 'agents' / 'memory'} and "
            f"{root / 'project'}. Run `gabbe init` in the project root.",
            is_error=True,
        )
    payload: dict[str, Any] = {"project_root": str(root)}
    if state is not None:
        fields = _phase_fields(state)
        payload["phase"] = fields.get("Current Phase", "unknown")
        payload["phase_status"] = fields.get("Phase Status", "unknown")
    if tasks is not None:
        payload["tasks"] = _task_counts(tasks)
    if missing:
        payload["missing"] = missing
    return _json_reply(payload)


# --- registry of tools -----------------------------------------------------------


def _string(max_length: int, **extra: Any) -> dict[str, Any]:
    return {"type": "string", "minLength": 1, "maxLength": max_length, **extra}


def _schema(properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }


@dataclass(frozen=True)
class ReadOnlyTool:
    name: str
    title: str
    description: str
    schema: dict[str, Any]
    handler: _Handler


_NAME = _string(128, pattern=_NAME_PATTERN)

READ_ONLY_TOOLS: tuple[ReadOnlyTool, ...] = (
    ReadOnlyTool(
        "list_skills",
        "List skills",
        "List the skills of the project's agent kit: name, description, category and path.",
        _schema({"category": _string(64, pattern=_NAME_PATTERN)}, []),
        list_skills,
    ),
    ReadOnlyTool(
        "read_skill",
        "Read a skill",
        "Return the text of one skill, by its name or file name.",
        _schema({"name": _NAME}, ["name"]),
        read_skill,
    ),
    ReadOnlyTool(
        "search_skills",
        "Search skills",
        "Find skills whose name, description or triggers contain the words of the query.",
        _schema(
            {
                "query": _string(200),
                "limit": {"type": "integer", "minimum": 1, "maximum": _MAX_SEARCH_RESULTS},
            },
            ["query"],
        ),
        search_skills,
    ),
    ReadOnlyTool(
        "get_template",
        "Get a template",
        "Return the text of one template of the agent kit, by name.",
        _schema({"name": _NAME}, ["name"]),
        get_template,
    ),
    ReadOnlyTool(
        "project_status",
        "Project status",
        "Current lifecycle phase and task counts of the project, from its state files.",
        _schema({}, []),
        project_status,
    ),
)

READ_ONLY_TOOL_NAMES = frozenset(t.name for t in READ_ONLY_TOOLS)


def listing_entry(tool: ReadOnlyTool) -> dict[str, Any]:
    """The ``tools/list`` entry of a read-only tool (annotation fields as in MCP 2026-07-28)."""
    return {
        "name": tool.name,
        "title": tool.title,
        "description": tool.description,
        "inputSchema": tool.schema,
        "annotations": {"title": tool.title, "readOnlyHint": True, "openWorldHint": False},
    }


def tool_definitions() -> list[ToolDefinition]:
    """Gateway registrations: read-only, role ``external_agent``, no policy allow-list."""
    return [
        ReadOnlyToolDefinition(
            name=t.name,
            description=t.description,
            parameters=t.schema,
            handler=t.handler,
            allowed_roles={"external_agent"},
            rate_limit_per_min=300,
        )
        for t in READ_ONLY_TOOLS
    ]
