#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""build_claude_plugin.py — emit GABBE's skills as Claude Code plugins and a marketplace.

Converts every ``agents/skills/**/*.skill.md`` into the Agent Skills format
(``plugins/<plugin>/skills/<name>/SKILL.md``) and writes the plugin manifests, the
plugin READMEs and the repository marketplace (``.claude-plugin/marketplace.json``),
so GABBE installs with::

    claude plugin marketplace add andreibesleaga/GABBE
    claude plugin install gabbe@gabbe

and the same tree is discovered by ``npx skills add andreibesleaga/GABBE`` (skills.sh).

Split. Claude Code lists every installed skill's name and description in context
within a budget of 1% of the model's context window and drops descriptions past it.
All 214 skills need ~45k characters, more than that budget on any context size, so the
skills are split into one marketplace with several plugins:

* ``gabbe``          — every skill in ``agents/skills/core/`` plus every skill flagged
                       ``core: true`` (the everyday SDLC loop);
* ``gabbe-<folder>`` — the remaining skills of each top folder (``ai``, ``architecture``,
                       ``brain``, ``coding``, ``coordination``, ``data``, ``industry``,
                       ``ops``, ``product``, ``security``).

Each skill lives in exactly one plugin, so no name is listed twice.

Per skill: ``name`` is the source file name without ``.skill.md`` (lowercase-hyphen,
unique; a collision fails the build), ``description`` is kept and, when it carries no
"when to use" wording, gets `` Use when: <triggers>`` appended within 1024 characters,
``license`` is CC-BY-SA-4.0 (GABBE's licence for its Markdown content, see LICENSE and
the README licence table), and ``metadata`` carries ``source``, ``tags``, ``core`` and
``context_cost``. The body after the source frontmatter is copied byte for byte.
Templates and guides a skill names by path (``templates/ops/X.md``) or by a unique
file name (``RUNBOOK_TEMPLATE.md``) are copied beside its SKILL.md at that same
relative path, so the reference resolves from the skill's own folder. Only text
files are copied; scripts never are, so every plugin stays content only.

Output is deterministic: sorted, UTF-8, LF line endings, no timestamps. The plugin
icon is the one binary input and lives outside the generated tree, so a build from an
empty ``plugins/`` works: ``docs/assets/claude-plugin-icon.png`` (1024 px, cropped
from ``docs/assets/GABBE.png``, 256-colour palette) is copied to every plugin's
``.claude-plugin/icon.png``. ``--render-icon`` re-creates it from the logo with
ImageMagick; it is committed rather than rendered on every build because ImageMagick
versions encode the same image to different bytes, so ``--check`` compares the copies
with the committed icon, not with the logo.

Usage:
    python scripts/build_claude_plugin.py            # write the tree
    python scripts/build_claude_plugin.py --check    # exit 1 if the tree is stale
    python scripts/build_claude_plugin.py --render-icon
"""

import argparse
import json
import posixpath
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

import yaml

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / "agents"
SKILLS = AGENTS / "skills"


def _tracked_files() -> Optional[set]:
    """Resolved paths of the files git tracks, so the plugin tree depends only on the
    repository's contents and never on ignored or untracked files in a working copy.
    None when git is not available (a source archive), where every file counts."""
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return {(ROOT / name).resolve() for name in out.decode("utf-8").split("\0") if name}


TRACKED = _tracked_files()


def _is_source(p: Path) -> bool:
    """A file the generator may read: present, and tracked when git is available."""
    return p.is_file() and (TRACKED is None or p.resolve() in TRACKED)


PLUGINS = ROOT / "plugins"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
ICON = ROOT / "docs" / "assets" / "claude-plugin-icon.png"
LOGO = ROOT / "docs" / "assets" / "GABBE.png"

CORE_PLUGIN = "gabbe"
# Skill names that are also Claude Code built-in command names. Plugin skills are
# namespaced (/gabbe:debug); a skills.sh install puts them in .claude/skills/ unprefixed.
BUILTIN_NAMES = ("code-review", "debug")
LICENSE = "CC-BY-SA-4.0"
AUTHOR = "Andrei Nicolae Besleaga"
HOMEPAGE = "https://github.com/andreibesleaga/GABBE#readme"
REPOSITORY = "https://github.com/andreibesleaga/GABBE"
MAX_DESCRIPTION = 1024
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# A description already says when to use the skill.
WHEN_RE = re.compile(r"\buse (?:it |this )?(?:when|for|to)\b|\bwhen to use\b|\btrigger", re.I)
# A path a skill names in backticks or as a Markdown link target.
REF_RE = re.compile(
    r"`([A-Za-z0-9_./-]+\.(?:md|json|ya?ml|txt|csv|toml|xml))`"
    r"|\]\(([A-Za-z0-9_./-]+\.(?:md|json|ya?ml|txt|csv|toml|xml))\)"
)
# A relative Markdown link inside a copied file.
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)\s#]+)(?:#[^)]*)?\)")
# Kit folders a supporting file may come from (never memory/, scripts/ or code).
SUPPORT_ROOTS = ("templates", "guides", "skills")
# A file that wires an environment credential into a config (``${GITHUB_TOKEN}``) is
# not copied: the plugin directory holds a plugin that reads a credential from the
# user's machine for review. The skill text still names it; a GABBE install has it.
CREDENTIAL_RE = re.compile(r"\$\{?[A-Z][A-Z0-9_]*(?:TOKEN|KEY|SECRET|PASSWORD|CREDENTIALS?)\b")

TOPICS = {
    "ai": "AI and agent engineering: multi-agent systems, agent UIs and protocols, "
    "context engineering, RAG evaluation, LLM-as-judge and reasoning patterns",
    "architecture": "software architecture: patterns, C4 and diagrams, domain models, "
    "event-driven and microservice design, governance, migration and scalability",
    "brain": "Brain Mode internals: cognitive architectures, active inference, global "
    "workspace, working and episodic memory, self-improvement",
    "coding": "coding: language performance, testing strategies (browser TDD, "
    "property-based, metamorphic, chaos), evals, UI generation and diagram canvases",
    "coordination": "multi-agent coordination: interop and protocols, workflow patterns, "
    "orchestration and swarm consensus",
    "data": "data: pipelines, governance, database migrations, SQL optimisation and the "
    "semantic web",
    "industry": "industry standards and domains: engineering standards, healthcare FHIR, "
    "industrial IoT and telecom networks",
    "ops": "operations: deployment, environments, observability, incidents, performance, "
    "cost and release management",
    "product": "product: requirements review, user research, story maps, business case, "
    "estimation, accessibility, sustainability and change management",
    "security": "security, privacy and AI safety: access control, secrets, cryptography, "
    "prompt-injection defence, red teaming, compliance and legal review",
}


class BuildError(Exception):
    """The source skills cannot be converted (collision, bad name, bad frontmatter)."""


def kit_version() -> str:
    """GABBE's release version: pyproject.toml and package.json must agree."""
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.M)
    if not m:
        raise BuildError("pyproject.toml has no version")
    npm = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["version"]
    if npm != m.group(1):
        raise BuildError(f"pyproject.toml {m.group(1)} != package.json {npm}")
    return m.group(1)


def split_frontmatter(text: str, where: str):
    """Return (frontmatter dict, body) of a ``---``-delimited Markdown file."""
    if not text.startswith("---\n"):
        raise BuildError(f"{where}: no frontmatter")
    end = text.find("\n---\n", 3)
    if end == -1:
        raise BuildError(f"{where}: unterminated frontmatter")
    meta = yaml.safe_load(text[4:end])
    if not isinstance(meta, dict):
        raise BuildError(f"{where}: frontmatter is not a mapping")
    return meta, text[end + len("\n---\n") :]


def q(value: str) -> str:
    """A YAML double-quoted scalar (JSON string syntax is valid YAML)."""
    return json.dumps(value, ensure_ascii=False)


def with_triggers(description: str, triggers) -> str:
    """Append ``Use when: <triggers>`` when the description lacks trigger wording."""
    description = " ".join(str(description).split())
    if WHEN_RE.search(description) or not triggers:
        return description[:MAX_DESCRIPTION]
    head = description if description.endswith((".", "!", "?")) else description + "."
    items = [" ".join(str(t).split()) for t in triggers if str(t).strip()]
    while items:
        out = f"{head} Use when: {', '.join(items)}."
        if len(out) <= MAX_DESCRIPTION:
            return out
        items.pop()
    return head[:MAX_DESCRIPTION]


def plugin_of(rel: Path, meta: dict) -> str:
    top = rel.parts[0]
    if top == "core" or meta.get("core") is True:
        return CORE_PLUGIN
    if top not in TOPICS:
        raise BuildError(f"{rel}: top folder {top!r} has no plugin")
    return f"{CORE_PLUGIN}-{top}"


def _unique_basenames() -> dict:
    """File name -> path for text files under agents/templates/ whose name is unique."""
    seen: dict = {}
    for p in sorted((AGENTS / "templates").rglob("*")):
        if _is_source(p):
            seen.setdefault(p.name, []).append(p)
    return {n: ps[0] for n, ps in seen.items() if len(ps) == 1}


def supporting_files(skill_file: Path, body: str, by_name: dict) -> dict:
    """Destination (relative to the skill folder) -> source path for each file the
    skill names that lives in the kit's templates, guides or skills folders."""
    found: dict = {}
    src: Optional[Path]
    kit_rel: Optional[Path]
    for m in REF_RE.finditer(body):
        token = m.group(1) or m.group(2)
        if token.endswith(".skill.md"):
            continue  # another skill: it is its own SKILL.md in the plugins
        norm = posixpath.normpath(token)
        if norm.startswith(("..", "/")) or norm in (".", ""):
            continue
        src = None
        for base in (skill_file.parent, SKILLS, AGENTS / "templates", AGENTS, ROOT):
            cand = (base / norm).resolve()
            if _is_source(cand):
                src = cand
                break
        if src is not None:
            try:
                kit_rel = src.relative_to(AGENTS.resolve())
            except ValueError:
                continue
            if kit_rel.parts[0] not in SUPPORT_ROOTS or src.name.endswith(".skill.md"):
                continue
            dest = norm
        elif "/" not in norm and norm in by_name:
            src, dest = by_name[norm], norm
        else:
            continue
        if CREDENTIAL_RE.search(src.read_text(encoding="utf-8", errors="replace")):
            continue
        if dest in found and found[dest] != src:
            raise BuildError(f"{skill_file}: {dest} names two different files")
        found[dest] = src
    # Close over relative Markdown links inside the copied files, so every link in
    # the plugin still resolves (agents/scripts/validate_links.py checks them all).
    todo = sorted(found)
    while todo:
        dest = todo.pop(0)
        src = found[dest]
        if src.suffix != ".md":
            continue
        text = re.sub(r"```.*?```", "", src.read_text(encoding="utf-8"), flags=re.S)
        text = re.sub(r"`[^`]*`", "", text)
        for link in LINK_RE.findall(text):
            if link.startswith(("http:", "https:", "mailto:", "/")):
                continue
            target = (src.parent / link).resolve()
            # A linked skill (guides/ops/cost-optimization.md links
            # skills/coding/performant-ai.skill.md) is copied as a plain reference
            # file, so the link resolves; only SKILL.md files are listed as skills.
            if not _is_source(target):
                continue
            sub = posixpath.normpath(posixpath.join(posixpath.dirname(dest), link))
            try:
                kit_rel = target.relative_to(AGENTS.resolve())
            except ValueError:
                kit_rel = None
            if sub.startswith("..") or kit_rel is None or kit_rel.parts[0] not in SUPPORT_ROOTS:
                raise BuildError(f"{skill_file}: {dest} links {link}, outside the skill folder")
            if CREDENTIAL_RE.search(target.read_text(encoding="utf-8", errors="replace")):
                raise BuildError(f"{skill_file}: {dest} links {link}, which names a credential")
            if sub not in found:
                found[sub] = target
                todo.append(sub)
    return found


def collect():
    """Read every source skill. Returns a sorted list of skill records."""
    by_name = _unique_basenames()
    records, names = [], {}
    for f in sorted(SKILLS.rglob("*.skill.md")):
        rel = f.relative_to(SKILLS)
        text = f.read_text(encoding="utf-8")
        if "\r" in text:
            raise BuildError(f"{rel}: CR line endings")
        meta, body = split_frontmatter(text, str(rel))
        name = f.name[: -len(".skill.md")]
        if not NAME_RE.match(name) or len(name) > 64:
            raise BuildError(f"{rel}: '{name}' is not a lowercase-hyphen name of <= 64 chars")
        if name in names:
            raise BuildError(f"skill name collision: {name} ({names[name]} and {rel})")
        names[name] = rel
        if not str(meta.get("description", "")).strip():
            raise BuildError(f"{rel}: empty description")
        records.append(
            {
                "name": name,
                "rel": rel,
                "meta": meta,
                "body": body,
                "plugin": plugin_of(rel, meta),
                "support": supporting_files(f, body, by_name),
            }
        )
    return records


def skill_md(rec: dict) -> str:
    meta = rec["meta"]
    tags = meta.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    lines = [
        "---",
        f"name: {rec['name']}",
        f"description: {q(with_triggers(meta['description'], meta.get('triggers') or []))}",
        f"license: {LICENSE}",
        "metadata:",
        f"  source: {q('agents/skills/' + rec['rel'].as_posix())}",
        f"  tags: {q(', '.join(str(t) for t in tags))}",
        f"  core: {q('true' if meta.get('core') is True else 'false')}",
        f"  context_cost: {q(str(meta.get('context_cost', '')))}",
        "---",
    ]
    return "\n".join(lines) + "\n" + rec["body"]


def plugin_description(plugin: str, count: int, total: int) -> str:
    if plugin == CORE_PLUGIN:
        return (
            f"GABBE core: {count} agent skills for the everyday engineering loop — "
            "spec, plan, TDD, review, research, security, memory and audit, with Brain "
            "and Loki mode. Add the gabbe-* "
            f"topic plugins from the same marketplace for the rest of the {total}."
        )
    topic = plugin[len(CORE_PLUGIN) + 1 :]
    return f"GABBE {topic} skills ({count}): {TOPICS[topic]}."


def plugin_keywords(plugin: str) -> list:
    base = ["gabbe", "agent-skills", "sdlc", "agentic-engineering"]
    if plugin != CORE_PLUGIN:
        base.append(plugin[len(CORE_PLUGIN) + 1 :])
    return base


def readme(plugin: str, recs: list, version: str, total: int) -> str:
    title = "GABBE" if plugin == CORE_PLUGIN else f"GABBE — {plugin[len(CORE_PLUGIN) + 1:]}"
    out = [
        f"# {title} (Claude Code plugin)",
        "",
        plugin_description(plugin, len(recs), total),
        "",
        "GABBE (Generative Architectural Brain Base Engine) is a Markdown agentic "
        "engineering kit. This plugin carries part of its skill library in the Agent "
        "Skills format, so Claude Code can load each skill when a task matches its "
        "description. The plugin is content only: Markdown skills and the templates "
        "they name. It has no hooks, no MCP servers and no executables, and it sends "
        "nothing anywhere.",
        "",
        "## Install",
        "",
        "```bash",
        "claude plugin marketplace add andreibesleaga/GABBE",
        f"claude plugin install {plugin}@gabbe",
        "```",
        "",
        "Or install single skills with the skills CLI (skills.sh):",
        "",
        "```bash",
        "npx skills add andreibesleaga/GABBE -a claude-code",
        "```",
        "",
    ]
    shadow = [r["name"] for r in recs if r["name"] in BUILTIN_NAMES]
    if shadow:
        names = " and ".join(f"`{n}`" for n in shadow)
        cmds = " and ".join(f"`/{n}`" for n in shadow)
        out += [
            f"Installed as this plugin, {names} are namespaced (`/{plugin}:{shadow[0]}`). "
            f"The skills CLI writes them unprefixed to `.claude/skills/`, where they take "
            f"the place of Claude Code's built-in {cmds} in that project.",
            "",
        ]
    if plugin == CORE_PLUGIN:
        out += [
            "Claude Code keeps each installed skill's name and description in context "
            "within about 1% of the context window. This plugin costs about 2,700 tokens "
            "per session (`claude plugin details gabbe`): over the budget of a 200k "
            "context, where Claude Code drops the descriptions of the least-used skills "
            "(nothing fails), and within that of a 1M context.",
            "",
        ]
    out += [
        f"Version {version}. Generated from `agents/skills/` by "
        "`scripts/build_claude_plugin.py`; edit the sources, not these files.",
        "",
        "## Skills",
        "",
    ]
    for r in recs:
        out.append(f"- `{r['name']}` — {' '.join(str(r['meta']['description']).split())}")
    out += [
        "",
        "## Licence",
        "",
        "The skills are GABBE content under CC BY-SA 4.0 "
        "(https://creativecommons.org/licenses/by-sa/4.0/), © 2026 Andrei Nicolae "
        "Besleaga. Source: https://github.com/andreibesleaga/GABBE",
        "",
    ]
    return "\n".join(out)


def plugin_json(plugin: str, count: int, version: str, total: int) -> dict:
    return {
        "name": plugin,
        "version": version,
        "description": plugin_description(plugin, count, total),
        "author": {"name": AUTHOR, "url": REPOSITORY},
        "homepage": HOMEPAGE,
        "repository": REPOSITORY,
        "license": LICENSE,
        "keywords": plugin_keywords(plugin),
    }


def dumps(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def build() -> dict:
    """The full generated tree: repo-relative POSIX path -> bytes."""
    version = kit_version()
    if not ICON.is_file():
        raise BuildError(f"missing {ICON.relative_to(ROOT)} (run with --render-icon)")
    icon = ICON.read_bytes()
    records = collect()
    plugins: dict = {}
    for r in records:
        plugins.setdefault(r["plugin"], []).append(r)
    order = [CORE_PLUGIN] + sorted(p for p in plugins if p != CORE_PLUGIN)

    out: dict = {}
    for plugin in order:
        recs = sorted(plugins[plugin], key=lambda r: r["name"])
        base = f"plugins/{plugin}"
        out[f"{base}/.claude-plugin/plugin.json"] = dumps(
            plugin_json(plugin, len(recs), version, len(records))
        )
        out[f"{base}/.claude-plugin/icon.png"] = icon
        out[f"{base}/README.md"] = readme(plugin, recs, version, len(records))
        for r in recs:
            sdir = f"{base}/skills/{r['name']}"
            out[f"{sdir}/SKILL.md"] = skill_md(r)
            for dest, src in sorted(r["support"].items()):
                out[f"{sdir}/{dest}"] = src.read_bytes()

    market = {
        "name": "gabbe",
        "owner": {"name": AUTHOR, "url": REPOSITORY},
        "metadata": {
            "description": "GABBE agent skills for Claude Code: the core SDLC loop plus "
            "topic plugins (AI, architecture, brain, coding, coordination, data, "
            "industry, ops, product, security).",
            "version": version,
        },
        "plugins": [
            {
                "name": p,
                "source": f"./plugins/{p}",
                "version": version,
                "description": plugin_description(p, len(plugins[p]), len(records)),
                "author": {"name": AUTHOR},
                "license": LICENSE,
                "homepage": HOMEPAGE,
                "repository": REPOSITORY,
                "keywords": plugin_keywords(p),
                "category": "development",
            }
            for p in order
        ],
    }
    out[".claude-plugin/marketplace.json"] = dumps(market)
    return {k: (v.encode("utf-8") if isinstance(v, str) else v) for k, v in sorted(out.items())}


def existing(root: Path) -> dict:
    found = {}
    if (root / "plugins").is_dir():
        for p in sorted((root / "plugins").rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                found[p.relative_to(root).as_posix()] = p.read_bytes()
    mk = root / ".claude-plugin" / "marketplace.json"
    if mk.is_file():
        found[".claude-plugin/marketplace.json"] = mk.read_bytes()
    return found


def diff(tree: dict, root: Path = ROOT) -> list:
    """Paths that differ between the generated tree and the files on disk."""
    disk = existing(root)
    return sorted(
        [f"stale: {p}" for p in tree if disk.get(p) != tree[p]]
        + [f"extra: {p}" for p in disk if p not in tree]
    )


def write(tree: dict) -> None:
    if PLUGINS.is_dir():
        shutil.rmtree(PLUGINS)
    for rel, data in tree.items():
        dest = ROOT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)


def render_icon() -> None:
    """Crop the GABBE logo (mark + wordmark) to a square 1024 px PNG."""
    ICON.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "convert",
            str(LOGO),
            "-crop",
            "1120x880+760+15",
            "+repage",
            "-background",
            "#FDFDFD",
            "-gravity",
            "center",
            "-extent",
            "1120x1120",
            "-resize",
            "1024x1024",
            "-dither",
            "None",
            "-colors",
            "256",
            "-strip",
            "-define",
            "png:exclude-chunks=date,time",
            f"PNG8:{ICON}",
        ],
        check=True,
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if the tree is stale")
    ap.add_argument("--render-icon", action="store_true", help="re-create the icon PNG")
    args = ap.parse_args(argv)
    try:
        if args.render_icon:
            render_icon()
        tree = build()
    except BuildError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    if args.check:
        problems = diff(tree)
        for p in problems:
            print(p)
        if problems:
            print("Plugin tree is stale: run python scripts/build_claude_plugin.py")
            return 1
        print(f"Plugin tree up to date ({len(tree)} files).")
        return 0
    write(tree)
    skills = sum(1 for p in tree if p.endswith("/SKILL.md"))
    plugins = sum(1 for p in tree if p.endswith("/plugin.json"))
    print(f"Wrote {plugins} plugins, {skills} skills, {len(tree)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
