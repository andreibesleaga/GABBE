#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

# --- Configuration ---
# KIT_SOURCE: Where the script and correct agents folder currently live
KIT_SOURCE = Path(__file__).parent.parent.absolute()
SOURCE_AGENTS_DIR = KIT_SOURCE / "agents"

# PROJECT_ROOT: Where the user is running the script from (the project they want to configure)
PROJECT_ROOT = Path.cwd()

# FORCE: when True, re-template even preserve-set files (still backed up first).
# Set from the --force CLI flag in main(). Default False = never overwrite user files.
FORCE = False

# HOOKS: when True (the --hooks CLI flag), also install the optional enforcement hooks.
# Off by default; adds no wizard question (see install_hooks).
HOOKS = False

# --- Install manifest recorder ---------------------------------------------
# The wizard records everything it creates under PROJECT_ROOT into
# `.gabbe/manifest.json` (the same schema gabbe/installer.py reads), so that
# `gabbe uninstall` can fully reverse a wizard install — symlinks, generated
# trees, config files and copied kit files alike. Paths outside PROJECT_ROOT
# (e.g. a global `~/agents` install) cannot live in a project manifest and are
# skipped; their wiring under PROJECT_ROOT is still recorded and reversible.
MANIFEST_SCHEMA_VERSION = 1
_MANIFEST_ENTRIES: list[dict] = []
_RECORDED_PATHS: set[str] = set()
# Recorded paths this run replaced by something else (an old skills link that became a
# folder): the merge with the earlier record must not bring them back.
_DROPPED_PATHS: set[str] = set()


def _agent_slug(name):
    """The slug an agent's artifacts are recorded under: "Claude Code" -> "claude-code".

    Same rule as `agentSlug()` in bin/install.js, so `gabbe uninstall --agents <slug>`
    removes the same things whichever installer wrote them.
    """
    slug = "".join(c if (c.isalnum() or c in "-_") else "-" for c in name.lower())
    return slug.strip("-") or "shared"


def _rel_to_project(path):
    """Return `path` relative to PROJECT_ROOT, or None if it escapes it.

    Resolves the PARENT only — never dereferences the leaf — so a freshly-created
    symlink (e.g. the wired root AGENTS.md) is recorded under its own name rather
    than its link target (which would collide with the copied kit file).
    """
    p = Path(path)
    try:
        full = p.parent.resolve() / p.name
        return str(full.relative_to(PROJECT_ROOT.resolve()))
    except (ValueError, OSError):
        return None


def _record(path, kind, agent="shared", backup_of=None, extra=None):
    """Record a created artifact for the uninstall manifest (idempotent per path)."""
    rel = _rel_to_project(path)
    if rel is None or rel in (".", ""):
        return
    entry = {"path": rel, "kind": kind, "agent": agent, "backup_of": backup_of, **(extra or {})}
    if kind == "copy":
        try:
            import hashlib

            entry["hash"] = hashlib.sha256(Path(path).read_bytes()).hexdigest()
        except OSError:
            entry["hash"] = ""
    # Last write wins, but prefer keeping a backup_of linkage if one was recorded.
    if rel in _RECORDED_PATHS:
        for e in _MANIFEST_ENTRIES:
            if e["path"] == rel:
                if backup_of and not e.get("backup_of"):
                    e["backup_of"] = backup_of
                if kind == "copy" and "hash" in entry:
                    e["hash"] = entry["hash"]
                if extra:
                    e.update(extra)
                return
    _MANIFEST_ENTRIES.append(entry)
    _RECORDED_PATHS.add(rel)


def _recorded_path_problem(rel):
    """Why a recorded path cannot be used, or None. Same rule as `_check_recorded_path` in
    gabbe/installer.py: not empty or `.`, not absolute, no `..` part."""
    if not isinstance(rel, str) or rel in ("", "."):
        return "it is empty or not text"
    if "\x00" in rel or Path(rel).is_absolute() or rel.startswith(("/", "\\")):
        return "it is absolute"
    parts = rel.replace("\\", "/").split("/")
    if ".." in parts or all(p in ("", ".") for p in parts):
        return "it climbs out of the project"
    return None


def _usable_record_entries(raw_entries):
    """The entries of an earlier record that are dicts with a safe `path`, keyed by path.

    An entry whose path is unsafe is skipped with one message naming it; an unsafe
    `backup_of` is cleared. Nothing outside the project can be reached through the record.
    """
    usable = {}
    for e in raw_entries:
        if not isinstance(e, dict) or "path" not in e:
            continue
        problem = _recorded_path_problem(e["path"])
        if problem:
            print(f"  {YELLOW}! Skipped record entry {e['path']!r}: {problem}{NC}")
            continue
        if e.get("backup_of") and _recorded_path_problem(e["backup_of"]):
            print(f"  {YELLOW}! Ignored backup_of {e['backup_of']!r} of {e['path']!r}{NC}")
            e = dict(e, backup_of=None)
        usable[e["path"]] = e
    return usable


_PRIOR_CACHE: dict = {}


def _prior_manifest_entries():
    """Entries of the manifest an earlier install wrote, keyed by path ({} if none).

    Read once per manifest version (the wizard asks about every file it touches).
    """
    mp = PROJECT_ROOT / ".gabbe" / "manifest.json"
    try:
        stat = mp.stat()
    except OSError:
        return {}
    key = (str(mp), stat.st_mtime_ns, stat.st_size)
    if key not in _PRIOR_CACHE:
        _PRIOR_CACHE.clear()
        try:
            prior = json.loads(mp.read_text())
            _PRIOR_CACHE[key] = _usable_record_entries(prior.get("entries", []))
        except (ValueError, OSError, AttributeError):
            _PRIOR_CACHE[key] = {}
    return _PRIOR_CACHE[key]


def _is_unchanged_kit_file(path, data):
    """True if `data` (the bytes of `path`) is exactly what an earlier install recorded."""
    import hashlib

    entry = _prior_manifest_entries().get(_rel_to_project(path) or "")
    return bool(entry and entry.get("hash") == hashlib.sha256(data).hexdigest())


def _make_dirs(path):
    """Create `path` and its parents unless a link of the user's lies on the way to it
    (a folder created there would land outside the project). Returns True when it exists."""
    path = Path(path)
    if _is_behind_link(path) or path.is_symlink():
        return path.is_dir()
    path.mkdir(parents=True, exist_ok=True)
    return True


def _record_tree(root):
    """Record every file under an installed kit dir (kind=copy) for reversal."""
    root = Path(root)
    if not root.exists():
        return
    for p in sorted(root.rglob("*")):
        if p.is_file() and not p.is_symlink():
            _record(p, "copy")


def _manifest_leaf_problem(mp):
    """A message when the record file is a link (it would be written through), else None."""
    if Path(mp).is_symlink():
        return f"{mp} is a symbolic link; nothing is written through it"
    return None


def write_install_manifest():
    """Write `.gabbe/manifest.json` capturing the wizard's tracked artifacts."""
    if not _MANIFEST_ENTRIES:
        return
    import importlib

    try:
        version = importlib.import_module("gabbe").__version__
    except Exception:
        version = "wizard"
    mp = PROJECT_ROOT / ".gabbe" / "manifest.json"
    if mp.parent.is_symlink():
        print(f"  {YELLOW}! .gabbe is a link of yours: no install record was written{NC}")
        return
    # Merge with any prior manifest so a re-run never drops earlier wiring (e.g.
    # agents selected in a previous install). New entries win on path collisions.
    merged: dict[str, dict] = {}
    if mp.exists():
        try:
            prior = json.loads(mp.read_text())
            merged.update(_usable_record_entries(prior.get("entries", [])))
        except (ValueError, OSError):
            pass
    for rel in _DROPPED_PATHS:
        merged.pop(rel, None)
    for e in _MANIFEST_ENTRIES:
        prior_entry = merged.get(e["path"])
        # A re-run finds its own link or file in place, so it records no backup.
        # Keep the link to the user's original that the first run recorded.
        if prior_entry and prior_entry.get("backup_of") and not e.get("backup_of"):
            e = dict(e, backup_of=prior_entry["backup_of"])
        merged[e["path"]] = e
    entries = sorted(merged.values(), key=lambda e: e["path"])
    agents = sorted({e.get("agent", "shared") for e in entries if e.get("agent") != "shared"})
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "installer_version": version,
        "timestamp": "",
        "agents": agents,
        "entries": entries,
    }
    problem = _manifest_leaf_problem(mp)
    if problem:
        print(f"  {RED}x {problem}; the install record was not written{NC}")
        raise SystemExit(1)
    mp.parent.mkdir(parents=True, exist_ok=True)
    tmp = mp.with_name(f"{mp.name}.tmp-{os.getpid()}")
    try:
        tmp.write_text(json.dumps(manifest, indent=2, sort_keys=True))
        os.replace(tmp, mp)
    finally:
        tmp.unlink(missing_ok=True)
    print(
        f"  {GREEN}✓ Recorded install manifest ({len(_MANIFEST_ENTRIES)} entries) for uninstall{NC}"
    )


# Colors
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
RED = "\033[0;31m"
NC = "\033[0m"

# --- Knowledge Base (Dynamic Discovery) ---


def build_tech_map_from_skills(agents_dir):
    """
    Scans all .skill.md files in agents_dir/skills and builds a TECH_MAP
    based on the 'tags' frontmatter field.
    """
    tech_map = {}
    skills_dir = agents_dir / "skills"

    if not skills_dir.exists():
        return tech_map

    for skill_file in skills_dir.rglob("*.skill.md"):
        try:
            content = skill_file.read_text()
            meta, _ = ensure_yaml_frontmatter(content, skill_file.name)

            # Get tags (list of strings)
            tags = meta.get("tags", [])
            # Also support 'tech' or 'stack' as aliases
            if not tags:
                tags = meta.get("tech", [])
            if not tags:
                tags = meta.get("stack", [])

            # Normalize to list
            if isinstance(tags, str):
                # Remove brackets first if present
                tags = tags.strip("[]")
                tags = [t.strip() for t in tags.split(",")]

            skill_name = meta.get("name", skill_file.stem.replace(".skill", ""))

            for tag in tags:
                tag = tag.lower().strip()
                if tag not in tech_map:
                    tech_map[tag] = {"skills": [], "guides": [], "templates": []}

                if skill_name not in tech_map[tag]["skills"]:
                    tech_map[tag]["skills"].append(skill_name)

        except Exception:
            # print(f"Warning: Failed to parse {skill_file.name}: {e}")
            pass

    # Hardcoded Guides/Templates mapping (logic removed as unused)

    return tech_map


# Initial placeholders - will be populated in main()
TECH_MAP: dict[str, Any] = {}


# Remaining unfilled [PLACEHOLDER:] fields after population, surfaced as an
# end-of-install warning so users are never silently shipped blank fields.
# Field names only; free-text placeholders (not a `name: "..."` field) are counted.
_UNFILLED_PLACEHOLDERS: list[str] = []
_UNFILLED_FREE_TEXT = [0]

# Where the value of a field comes from, for the end-of-install list.
_FIELD_HINTS = {
    "project_name": "what you call the project",
    "description": "one sentence about the project",
    "repo_url": "your git remote (`git remote get-url origin`)",
    "runtime": "your stack: see your package or build file",
    "language": "your stack: see your package or build file",
    "framework": "your stack: see your package or build file",
    "package_manager": "your lock file (pnpm, npm, yarn, pip, ...)",
    "database": "your data layer: see your docker-compose or config files",
    "orm": "your data layer: see your dependencies",
    "cache": "your data layer: see your docker-compose or config files",
    "deployment_target": "your Dockerfile, serverless or hosting config",
    "ci_cd": "your CI files (.github/workflows, .gitlab-ci.yml, ...)",
    "security_scan": "your CI files or package scripts",
}
_FIELD_HINT_DEFAULT = "the command in your package scripts, Makefile or CI"

# Per-package-manager command derivations for the [PLACEHOLDER:] command fields
# the Jinja substitution does not cover. Keyed by the resolved package manager.
_PM_COMMANDS = {
    "npm": {
        "dev": "npm run dev",
        "test_coverage": "npm test -- --coverage",
        "test_single": "npm test -- path/to/file.test.ts",
        "typecheck": "tsc --noEmit",
        "lint": "eslint .",
        "format": "prettier --write .",
    },
    "pnpm": {
        "dev": "pnpm dev",
        "test_coverage": "pnpm test --coverage",
        "test_single": "pnpm vitest run src/path/to/file.test.ts",
        "typecheck": "pnpm tsc --noEmit",
        "lint": "pnpm eslint .",
        "format": "pnpm prettier --write .",
    },
    "yarn": {
        "dev": "yarn dev",
        "test_coverage": "yarn test --coverage",
        "test_single": "yarn test path/to/file.test.ts",
        "typecheck": "yarn tsc --noEmit",
        "lint": "yarn eslint .",
        "format": "yarn prettier --write .",
    },
    "pip": {
        "dev": "uvicorn main:app --reload",
        "test_coverage": "pytest --cov",
        "test_single": "pytest path/to/test_file.py::test_name",
        "typecheck": "mypy .",
        "lint": "ruff check .",
        "format": "ruff format .",
    },
    "go mod": {
        "dev": "go run .",
        "test_coverage": "go test -cover ./...",
        "test_single": "go test ./path/to/pkg -run TestName",
        "typecheck": "go vet ./...",
        "lint": "golangci-lint run",
        "format": "gofmt -w .",
    },
    "cargo": {
        "dev": "cargo run",
        "test_coverage": "cargo tarpaulin",
        "test_single": "cargo test test_name",
        "typecheck": "cargo check",
        "lint": "cargo clippy",
        "format": "cargo fmt",
    },
    "composer": {
        "dev": "php artisan serve",
        "test_coverage": "php artisan test --coverage",
        "test_single": "php artisan test --filter=TestName",
        "typecheck": "phpstan analyse --level=9",
        "lint": "pint --test",
        "format": "pint",
    },
}


def _detect_repo_url(base):
    """Best-effort git remote URL (https form), or None."""
    try:
        import subprocess

        out = subprocess.run(
            ["git", "-C", str(base), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return _clean_repo_url(out.stdout.strip())
    except Exception:
        pass
    return None


def _clean_repo_url(url):
    """Remote URL in https form without credentials, or None.

    A remote such as `https://user:token@host/o/r.git` must never reach AGENTS.md,
    a file that agents read and people commit: the `user:token@` part is dropped.
    A value that could break out of the quoted field it is written into is refused.
    """
    from urllib.parse import urlsplit

    if not url:
        return None
    if url.startswith("git@") and ":" in url:
        host, path = url[4:].split(":", 1)
        url = f"https://{host}/{path}"
    parts = urlsplit(url)
    if parts.scheme and parts.hostname:
        name = f"[{parts.hostname}]" if ":" in parts.hostname else parts.hostname
        host = name + (f":{parts.port}" if parts.port else "")
        url = f"{parts.scheme}://{host}{parts.path}"
    elif "@" in url:
        return None
    if any(c in url for c in '"\\\n\r'):
        return None
    return url.removesuffix(".git")


def _detect_ci_cd(base):
    if (base / ".github" / "workflows").exists():
        return "GitHub Actions"
    if (base / ".gitlab-ci.yml").exists():
        return "GitLab CI"
    if (base / ".circleci").exists():
        return "CircleCI"
    return None


def _detect_deploy_target(base):
    if (base / "vercel.json").exists():
        return "Vercel"
    if (base / "Dockerfile").exists() or (base / "docker-compose.yml").exists():
        return "Docker/K8s"
    if (base / "serverless.yml").exists():
        return "AWS Lambda"
    return None


def populate_placeholders(content, pm, base):
    """Fill derivable [PLACEHOLDER:] fields, tag the rest OPTIONAL, and record
    which remain so the installer can warn the user to complete them.

    Returns the updated content. Appends remaining field names to the module
    global `_UNFILLED_PLACEHOLDERS` for the end-of-install warning.
    """
    import re

    cmds = _PM_COMMANDS.get(pm, _PM_COMMANDS["npm"])
    derived = dict(cmds)
    repo = _detect_repo_url(base)
    if repo:
        derived["repo_url"] = repo
    ci = _detect_ci_cd(base)
    if ci:
        derived["ci_cd"] = ci
    deploy = _detect_deploy_target(base)
    if deploy:
        derived["deployment_target"] = deploy

    out_lines = []
    # Matches `key: "[PLACEHOLDER: ...]"` (the YAML-ish command/config fields).
    kv_re = re.compile(r'^(\s*)([a-z_]+):\s*"\[PLACEHOLDER:[^"]*\]"\s*$')
    for line in content.splitlines():
        m = kv_re.match(line)
        if m:
            indent, key = m.group(1), m.group(2)
            if key in derived:
                out_lines.append(f'{indent}{key}: "{derived[key]}"')
                continue
            # Unknown value: keep the field, mark it clearly OPTIONAL, and record it.
            _UNFILLED_PLACEHOLDERS.append(key)
            out_lines.append(line + "  # <!-- OPTIONAL: fill this in yourself -->")
            continue
        # Prose / inline placeholders: tag the line OPTIONAL (don't fabricate prose).
        if "[PLACEHOLDER" in line:
            _UNFILLED_FREE_TEXT[0] += 1
            if "OPTIONAL" not in line:
                out_lines.append(line + "  <!-- OPTIONAL: fill this in yourself -->")
            else:
                out_lines.append(line)
            continue
        out_lines.append(line)
    return "\n".join(out_lines)


def detect_existing_project(cwd):
    """Detect whether `cwd` is an existing codebase and infer its stack.

    Prefers the richer, unit-tested gabbe.detect module when GABBE is importable
    (pip install); falls back to a self-contained sniff so the wizard still works
    when run standalone via npx/curl (where the gabbe package is not present).
    """
    try:
        from gabbe import detect as _detect  # type: ignore

        return _detect.detect_project(cwd)
    except Exception:
        pass
    base = Path(cwd)
    manifests = [
        ("pnpm-lock.yaml", "TypeScript", "pnpm"),
        ("yarn.lock", "TypeScript", "yarn"),
        ("package.json", "TypeScript", "npm"),
        ("pyproject.toml", "Python", "pip"),
        ("requirements.txt", "Python", "pip"),
        ("go.mod", "Go", "go mod"),
        ("Cargo.toml", "Rust", "cargo"),
        ("composer.json", "PHP", "composer"),
        ("pom.xml", "Java", "maven"),
        ("build.gradle", "Java", "gradle"),
        ("Gemfile", "Ruby", "bundler"),
    ]
    language = pm = None
    signals = []
    for name, lang, pmgr in manifests:
        if (base / name).exists():
            language, pm = lang, pmgr
            signals.append(f"found {name}")
            break
    has_git = (base / ".git").exists()
    if has_git:
        signals.append("git repository")
    is_existing = bool(language or has_git)
    return {
        "is_existing": is_existing,
        "language": language,
        "framework": None,
        "package_manager": pm,
        "project_name": None,
        "has_git": has_git,
        "signals": signals,
    }


# --- Helper Functions ---


def _print_unfilled_fields():
    """List the fields still to fill in agents/AGENTS.md: names with where each value
    comes from, then how to fill them."""
    names = list(dict.fromkeys(_UNFILLED_PLACEHOLDERS))
    free = _UNFILLED_FREE_TEXT[0]
    total = len(names) + free
    print(
        f"\n{YELLOW}⚠ {total} optional field(s) in agents/AGENTS.md still need your input "
        f"(marked with <!-- OPTIONAL -->):{NC}"
    )
    for name in names:
        print(f"    - {name}: {_FIELD_HINTS.get(name, _FIELD_HINT_DEFAULT)}")
    if free:
        print(f"    - {free} free-text spot(s) (architecture, forbidden patterns, secrets, ...)")
    print(
        f"  {BLUE}→ Edit agents/AGENTS.md, or ask your agent: it is step 2 of "
        f"BOOTSTRAP_MISSION.md.{NC}"
    )


def clear_screen():
    """Clear the terminal; do nothing when there is no `clear` command or no terminal."""
    if not sys.stdout.isatty():
        return
    if os.name == "nt":
        os.system("cls")
    elif shutil.which("clear"):
        os.system("clear")


def print_header():
    print(f"{BLUE}" + "=" * 60 + f"{NC}")
    print(f"{BLUE}🤖  Agentic Engineering Kit - Setup & Install Wizard v2.2{NC}")
    print(f"{BLUE}" + "=" * 60 + f"{NC}")
    print("This script will:")
    print("  1. Install the Kit (Locally or Globally)")
    print("  2. Configure Project Identity, Stack, & Type (Legacy/Enterprise)")
    print("  3. Wire up AI tools & MCPs")
    print("  4. Generate a 'Research Mission' for your AI")
    print()


def ask(question, default=None):
    prompt = f"{question}"
    if default:
        prompt += f" [{default}]"
    prompt += ": "
    response = input(prompt).strip()
    return response if response else default


def select_index(question, options):
    print(f"\n{question}")
    for i, opt in enumerate(options):
        print(f"  {i + 1}) {opt}")
    while True:
        choice = input(f"Select (1-{len(options)}): ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return idx


def select(question, options):
    idx = select_index(question, options)
    return options[idx]


def ask_multiselect(question, options):
    print(f"\n{question} (comma separated, e.g. 1,3)")
    for i, opt in enumerate(options):
        print(f"  {i + 1}) {opt}")
    choice = input("Select: ").strip()
    selected = []
    if not choice:
        return selected
    try:
        indices = [int(x.strip()) - 1 for x in choice.split(",") if x.strip().isdigit()]
        for idx in indices:
            if 0 <= idx < len(options):
                selected.append(options[idx])
    except Exception:
        pass
    return selected


def _free_backup_path(path, suffix=".gabbe-bak"):
    """First unused backup name: `<name>.gabbe-bak`, then `<name>.gabbe-bak.1`, ..."""
    candidate = Path(str(path) + suffix)
    n = 0
    while candidate.exists() or candidate.is_symlink():
        n += 1
        candidate = Path(f"{path}{suffix}.{n}")
    return candidate


def _backup_before_overwrite(dst_file):
    """Back up an existing target file before it is overwritten. Returns the backup.

    Guarantees the never-clobber invariant: any pre-existing content is always
    recoverable. An existing backup is never overwritten: the first one keeps the
    user's ORIGINAL, and a later, different version of the file gets the next free
    name (`.gabbe-bak.1`, ...). A file whose bytes are already in a backup, or that
    an earlier install wrote and nobody changed, needs no new backup.
    """
    dst_file = Path(dst_file)
    try:
        data = dst_file.read_bytes()
    except OSError as e:
        _backup_failed(dst_file, e)
    first = Path(str(dst_file) + ".gabbe-bak")
    if _is_unchanged_kit_file(dst_file, data):
        return first if first.exists() else None
    existing = [first] + sorted(dst_file.parent.glob(dst_file.name + ".gabbe-bak.*"))
    for backup in existing:
        try:
            if backup.is_file() and backup.read_bytes() == data:
                return backup
        except OSError:
            continue
    backup = _free_backup_path(dst_file)
    try:
        shutil.copy2(dst_file, backup)
    except OSError as e:
        _backup_failed(dst_file, e)
    print(f"  {YELLOW}! Backed up existing {dst_file.name} -> {backup.name}{NC}")
    return backup


def _backup_failed(path, error):
    """Stop the install: without a backup the file would be the user's only copy."""
    raise SystemExit(
        f"{RED}x Could not back up {path} ({error}). Nothing was overwritten; "
        f"fix the cause and run the installer again.{NC}"
    )


def _is_behind_link(path):
    """True if `path` is a symbolic link, or a directory between PROJECT_ROOT and it
    is one. Such a path is the user's: writing there could land outside the project."""
    path = Path(path)
    if path.is_symlink():
        return True
    try:
        rel = path.absolute().relative_to(PROJECT_ROOT.absolute())
    except ValueError:
        return False  # a kit location the user chose outside the project
    current = PROJECT_ROOT.absolute()
    for part in rel.parts[:-1]:
        current = current / part
        if current.is_symlink():
            return True
    return False


# --- Optional hooks (--hooks) -------------------------------------------------
# Same rules as bin/install.js: off unless asked; nothing of the user's is replaced; every
# touched file is recorded (kind "hook-merge" for a merged settings file, "copy" for a git hook).
HOOK_MARK = "GABBE-HOOK"
GIT_HOOKS = ("pre-commit", "pre-push")
# agent -> (fragment, file it is merged into, script the fragment runs)
HOOK_MERGES = {
    "Claude Code": (
        "claude-code/settings.fragment.json",
        (".claude", "settings.json"),
        "claude-code/gabbe-hook.js",
    ),
    "Cursor": (
        "cursor/hooks.fragment.json",
        (".cursor", "hooks.json"),
        "cursor/gabbe-hook.js",
    ),
}


def _hook_command_key(item):
    """The command strings of one hook entry (a Claude Code group or a Cursor entry)."""
    if isinstance(item, dict) and isinstance(item.get("hooks"), list):
        return [h.get("command") if isinstance(h, dict) else None for h in item["hooks"]]
    return [item.get("command") if isinstance(item, dict) else None]


def _same_hook_entry(a, b):
    """Same event-level matcher and same command strings: the rule of merge-hooks.js."""
    ma = a.get("matcher") if isinstance(a, dict) else None
    mb = b.get("matcher") if isinstance(b, dict) else None
    return ma == mb and _hook_command_key(a) == _hook_command_key(b)


def merge_hook_fragment(doc, fragment):
    """Add the fragment's hook entries that `doc` lacks. Returns (new_doc, changed, added_version).

    The one merge function of the wizard (same result as `mergeFragment` in
    agents/hooks/merge-hooks.js). Raises ValueError when `doc` has an unexpected shape.
    """
    if not isinstance(doc, dict):
        raise ValueError("it is not a JSON object")
    if "hooks" in doc and not isinstance(doc["hooks"], dict):
        raise ValueError('"hooks" has an unexpected shape')
    for event in fragment["hooks"]:
        if event in doc.get("hooks", {}) and not isinstance(doc["hooks"][event], list):
            raise ValueError(f"hooks.{event} is not a list")
    new = json.loads(json.dumps(doc))
    changed = False
    for event, items in fragment["hooks"].items():
        for item in items:
            lst = new.setdefault("hooks", {}).setdefault(event, [])
            if not any(_same_hook_entry(x, item) for x in lst):
                lst.append(item)
                changed = True
    added_version = False
    if changed and "version" in fragment and "version" not in new:
        new["version"] = fragment["version"]
        added_version = True
    return new, changed, added_version


def _hook_by_hand(rel, why, fragment):
    print(f"  {YELLOW}! {rel}: {why}. Nothing was changed. Add this by hand:{NC}")
    for line in json.dumps(fragment, indent=2).splitlines():
        print("      " + line)


def _install_hook_merge(agent, agents_dir, lines):
    """Merge one agent's fragment into the project's hooks file. Never replaces user content."""
    fragment_name, target_parts, script = HOOK_MERGES[agent]
    target = PROJECT_ROOT.joinpath(*target_parts)
    rel = _rel_to_project(target)
    fragment = json.loads((SOURCE_AGENTS_DIR / "hooks" / fragment_name).read_text(encoding="utf-8"))
    if not (Path(agents_dir) / "hooks" / script).is_file():
        print(
            f"  {YELLOW}! {rel}: agents/hooks/{script} is not in the project, no hook installed{NC}"
        )
        return
    if _is_behind_link(target):
        print(f"  {YELLOW}! {rel}: a link of yours, or behind one; hooks not installed there{NC}")
        return
    exists = target.exists()
    if exists and not target.is_file():
        print(f"  {YELLOW}! {rel} is not a regular file; hooks not installed there{NC}")
        return
    doc = {}
    if exists:
        try:
            doc = json.loads(target.read_text(encoding="utf-8"))
        except ValueError:
            _hook_by_hand(rel, "it is not plain JSON (comments?)", fragment)
            return
    try:
        merged, changed, added_version = merge_hook_fragment(doc, fragment)
    except ValueError as e:
        _hook_by_hand(rel, str(e), fragment)
        return
    if not changed:
        print(f"  {BLUE}→ {rel}: the GABBE hook entries are already there{NC}")
        return
    earlier = _prior_manifest_entries().get(rel or "")
    was_ours = bool(earlier and earlier.get("kind") == "hook-merge")
    created = (not exists and not was_ours) or bool(was_ours and earlier.get("created"))
    backup_of = earlier.get("backup_of") if was_ours else None
    if exists and not (was_ours and earlier.get("created")):
        backup = _backup_before_overwrite(target)
        if backup is not None and not was_ours:
            backup_of = _rel_to_project(backup)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _record(
        target,
        "hook-merge",
        agent=_agent_slug(agent),
        backup_of=backup_of,
        extra={
            "fragment": "agents/hooks/" + fragment_name,
            "fragment_doc": fragment,
            "created": created,
            "added_version": bool(added_version or (was_ours and earlier.get("added_version"))),
        },
    )
    lines.append(f"{agent} hooks (shell guard, edit guard, session start) -> {rel}")


def _git_out(args):
    try:
        done = subprocess.run(
            ["git", *args], cwd=PROJECT_ROOT, capture_output=True, text=True, check=False
        )
    except OSError:
        return None
    return done.stdout.strip() if done.returncode == 0 else None


def _install_git_hooks(lines):
    """The two git hooks, by the rules of agents/hooks/git/install.sh (fixed git arguments only)."""
    common = _git_out(["rev-parse", "--git-common-dir"])
    if common is None:
        print(f"  {BLUE}→ Git hooks skipped: this folder is not a git repository{NC}")
        return
    if _git_out(["config", "--get", "core.hooksPath"]):
        print(
            f"  {YELLOW}! Git hooks not installed: core.hooksPath is set. Call "
            f"agents/hooks/git/pre-commit and pre-push from your own hooks "
            f"(see agents/guides/ops/hooks.md){NC}"
        )
        return
    hooks_dir = (PROJECT_ROOT / common / "hooks").absolute()
    if _rel_to_project(hooks_dir / "pre-commit") is None:
        print(
            f"  {YELLOW}! Git hooks not installed: the git folder is outside the project "
            f'(worktree or submodule). Run "sh agents/hooks/git/install.sh" there yourself{NC}'
        )
        return
    for name in GIT_HOOKS:
        dst = hooks_dir / name
        rel = _rel_to_project(dst)
        data = (SOURCE_AGENTS_DIR / "hooks" / "git" / name).read_bytes()
        if _is_behind_link(dst):
            print(f"  {YELLOW}! {rel} is a link of yours, or behind one: left alone{NC}")
            continue
        exists = dst.exists() or dst.is_symlink()
        if exists and (not dst.is_file() or HOOK_MARK.encode() not in dst.read_bytes()):
            print(
                f"  {YELLOW}! {rel} already exists and is not GABBE's: not replaced. To chain, "
                f'add a line to it that runs agents/hooks/git/{name} "$@"{NC}'
            )
            continue
        if not exists or dst.read_bytes() != data:
            if exists:
                _backup_before_overwrite(dst)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)
        dst.chmod(0o755)
        _record(dst, "copy", agent="shared")
        lines.append(f"git {name} hook -> {rel}")


def install_hooks(agents, agents_dir):
    """`--hooks`: install the optional hooks for the agents chosen in the wizard."""
    print(f"\n{YELLOW}Optional hooks (--hooks){NC}")
    lines = []
    for agent in HOOK_MERGES:
        if agent in agents:
            _install_hook_merge(agent, agents_dir, lines)
    _install_git_hooks(lines)
    for line in lines:
        print(f"  {GREEN}✓ Installed {line}{NC}")
    if lines:
        print(
            "  Guide: agents/guides/ops/hooks.md. Remove them with `gabbe uninstall` (1.2.0 or later)."
        )


def write_generated_file(path, text, agent="shared"):
    """Write a file the wizard generates, backing up a different file already there.

    Records the file for uninstall. The backup is linked for restore only when the
    file was not written by an earlier install (so it is the user's own).
    """
    path = Path(path)
    backup_of = None
    if _is_behind_link(path):
        print(f"  {YELLOW}! {path.name} is a link, or sits behind one: left as is{NC}")
        return
    if path.is_file() and path.read_text(errors="replace") != text:
        ours = (_rel_to_project(path) or "") in _prior_manifest_entries()
        backup = _backup_before_overwrite(path)
        if backup is not None and not ours:
            backup_of = _rel_to_project(backup)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    _record(path, "copy", agent=agent, backup_of=backup_of)


# The block appended to an instruction file the user already had. `bin/install.js`
# writes the same text; `gabbe uninstall` removes it by its two marker lines.
POINTER_BEGIN = (
    "<!-- GABBE-KIT:BEGIN (added by the GABBE installer; delete this block to detach the kit) -->"
)
POINTER_END = "<!-- GABBE-KIT:END -->"


def pointer_block(kit_agents_md):
    return (
        f"{POINTER_BEGIN}\n"
        "## GABBE kit\n\n"
        f"This project also uses the GABBE engineering kit. Read `{kit_agents_md}` together with\n"
        "this file: it holds the kit's rules, lifecycle and skills index. Where the two disagree,\n"
        "this file wins.\n"
        f"{POINTER_END}\n"
    )


def with_pointer_block(data, kit_agents_md):
    """The bytes of a user's file with the pointer block appended.

    Works on bytes and uses the file's own line ending, so the user's encoding and
    line endings are never changed.
    """
    nl = b"\r\n" if b"\r\n" in data else b"\n"
    block = pointer_block(kit_agents_md).encode("utf-8").replace(b"\n", nl)
    if not data or data.endswith(nl + nl):
        joiner = b""
    elif data.endswith(nl):
        joiner = nl
    else:
        joiner = nl + nl
    return data + joiner + block


def without_pointer_block(data):
    """The bytes of a user's file without the pointer block (same rule as
    `gabbe/installer.py` strip_pointer_block)."""
    import re

    m = re.search(rb"<!-- GABBE-KIT:BEGIN.*?<!-- GABBE-KIT:END -->(\r?\n)?", data, re.DOTALL)
    if not m:
        return data
    before = data[: m.start()]
    for blank in (b"\r\n\r\n", b"\n\n"):
        if before.endswith(blank):
            before = before[: len(before) - len(blank) // 2]  # drop one line end
            break
    return before + data[m.end() :]


def add_pointer_block(target, kit_agents_md, agent="shared"):
    """Keep the user's own instruction file and append a pointer to the kit's.

    The original is copied to a backup first and the change is recorded, so
    `gabbe uninstall` takes the block out again. Idempotent.
    """
    data = target.read_bytes()
    if POINTER_BEGIN.encode() in data:
        print(f"  {BLUE}→ {target.name} already points to the kit; left as is{NC}")
        return
    if not os.access(target, os.W_OK):
        print(
            f"  {YELLOW}! {target.name} is read-only: left as is. Add a line that points to "
            f"{kit_agents_md} yourself{NC}"
        )
        return
    backup = _backup_before_overwrite(target)
    target.write_bytes(with_pointer_block(data, kit_agents_md))
    _record(target, "block", agent=agent, backup_of=_rel_to_project(backup) if backup else None)
    print(
        f"  {YELLOW}! Kept your {target.name} and added a pointer to {kit_agents_md} "
        f"(original saved as {backup.name if backup else 'a backup'}){NC}"
    )


def safe_merge_directory(src_root, dst_root, is_kit_root=False, force=None):
    """Merge the kit tree into a target without ever losing user data.

    Preserve-set files (and memory/project trees) are left untouched. Any OTHER
    pre-existing file is backed up to <name>.gabbe-bak before being refreshed, so
    nothing is clobbered. With force=True, even preserve-set files are re-templated
    (still backed up first).
    """
    if force is None:
        force = FORCE
    PRESERVE_FILES = {"AGENTS.md", "CONSTITUTION.md", "TASKS.md", "policies.yml", "config.json"}
    notified_preservations = set()

    for src_dir, dirs, files in os.walk(src_root):
        rel_path = os.path.relpath(src_dir, src_root)
        dst_dir = Path(dst_root) / (rel_path if rel_path != "." else "")

        dst_dir.mkdir(parents=True, exist_ok=True)
        in_memory = "memory" in Path(rel_path).parts
        in_project = "project" in Path(rel_path).parts

        if dst_dir != Path(dst_root) and dst_dir.is_symlink():
            # A folder of the user's that is a link: never copy through it.
            print(f"  {YELLOW}! {dst_dir} is a link: left as is, nothing copied into it{NC}")
            dirs[:] = []
            continue

        for file_ in files:
            src_file = Path(src_dir) / file_
            dst_file = dst_dir / file_
            if dst_file.is_symlink():
                print(f"  {YELLOW}! {dst_file.name} is a link of yours: left as is{NC}")
                continue

            preserve = False
            # Honor the preserve-set unconditionally. Previously this only ran
            # when is_kit_root=True, so the symlink-fallback path (is_kit_root
            # defaults to False) clobbered existing user files. User content
            # must never be overwritten regardless of how the merge was reached.
            # With force=True the user explicitly opted into re-templating these.
            if dst_file.exists() and not force:
                if in_memory:
                    preserve = True
                elif in_project:
                    preserve = True
                elif file_ in PRESERVE_FILES:
                    preserve = True
                elif file_.startswith("PROJECT") and file_.endswith(".md"):
                    preserve = True

            if preserve:
                log_path = str(dst_file.relative_to(dst_root))
                if in_memory:
                    log_path = "memory/*"
                elif in_project:
                    log_path = "project/*"
                if log_path not in notified_preservations:
                    print(
                        f"  {YELLOW}→ Preserved user file(s): {log_path} (check kit templates to update manually){NC}"
                    )
                    notified_preservations.add(log_path)
                continue

            if dst_file.exists():
                # Never clobber: only files whose bytes differ from the incoming kit
                # file are backed up (identical files need no backup). This covers
                # user-modified kit files AND, with force=True, preserve-set files.
                try:
                    differs = src_file.read_bytes() != dst_file.read_bytes()
                except Exception:
                    differs = True
                if differs:
                    _backup_before_overwrite(dst_file)
                try:
                    dst_file.unlink()
                except Exception:
                    pass
            shutil.copy2(src_file, dst_file)
            # Link the FIRST backup (the user's original) for restore on uninstall.
            bak = str(dst_file) + ".gabbe-bak"
            _record(
                dst_file,
                "copy",
                backup_of=_rel_to_project(bak) if os.path.exists(bak) else None,
            )


def _move_aside_without_block(target):
    """Remove `target` (a user's file that carries the pointer block) so a link can
    take its place; return the manifest path of the backup that holds the user's text.

    If the file is unchanged since the block was added, the backup made then already
    is the original. Otherwise the text without the block goes to a new `.bak`.
    """
    stripped = without_pointer_block(target.read_bytes())
    entry = _prior_manifest_entries().get(_rel_to_project(target) or "", {})
    earlier = PROJECT_ROOT / entry["backup_of"] if entry.get("backup_of") else None
    if earlier and earlier.is_file():
        if earlier.read_bytes().rstrip(b"\r\n") == stripped.rstrip(b"\r\n"):
            target.unlink()
            return entry["backup_of"]
    backup = _free_backup_path(target, suffix=".bak")
    backup.write_bytes(stripped)
    target.unlink()
    print(f"  {YELLOW}! Moved your {target.name} to {backup.name}{NC}")
    return _rel_to_project(backup)


def _is_our_link(target, source):
    """True if the link at `target` was made by an installer: an earlier install
    recorded it, or it already points at the kit file we are about to link."""
    entry = _prior_manifest_entries().get(_rel_to_project(target) or "")
    if entry and entry.get("kind") == "symlink":
        return True
    try:
        return target.resolve() == Path(source).resolve()
    except OSError:
        return False


def create_symlink(source, target, agent="shared"):
    """Creates a symlink from target to source, backing up if exists.

    Records the created link (and any backup) in the install manifest so
    `gabbe uninstall` can reverse it and restore the user's original.
    """
    backup_of = None
    if _is_behind_link(target.parent):
        print(
            f"  {YELLOW}! {target.parent} is a link, or sits behind one: {target.name} not wired{NC}"
        )
        return
    if target.is_symlink() and not _is_our_link(target, source):
        # A link of the user's (for example AGENTS.md -> CLAUDE.md): keep it.
        if not FORCE:
            print(
                f"  {YELLOW}! {target.name} is a link of yours: left as is. Point it at the "
                f"kit yourself, or re-run with --force (it is moved to a backup first){NC}"
            )
            return
        backup = _free_backup_path(target, suffix=".bak")
        target.rename(backup)
        backup_of = _rel_to_project(backup)
        print(f"  {YELLOW}! Moved your link {target.name} to {backup.name}{NC}")
    elif target.is_symlink():
        target.unlink()
    elif target.exists():
        # An existing backup is never overwritten: take the next free name.
        backup = _free_backup_path(target, suffix=".bak")
        if target.is_dir():
            print(f"  {YELLOW}! Backing up existing directory {target.name} to {backup.name}{NC}")
            shutil.move(str(target), str(backup))
            backup_of = _rel_to_project(backup)
        elif source.is_file() and FORCE and POINTER_BEGIN.encode() in target.read_bytes():
            # --force after an earlier run that added the pointer block: put the
            # user's file back without the block before it is moved aside.
            backup_of = _move_aside_without_block(target)
        elif (
            source.is_file()
            and not FORCE
            and not _is_unchanged_kit_file(target, target.read_bytes())
        ):
            # The user's own instruction file: keep it, point it at the kit's file.
            try:
                shown = str(source.absolute().relative_to(PROJECT_ROOT.resolve()))
            except ValueError:
                shown = str(source.absolute())
            add_pointer_block(target, shown.replace(os.sep, "/"), agent=agent)
            return
        else:
            print(f"  {YELLOW}! Backing up existing file {target.name} to {backup.name}{NC}")
            target.rename(backup)
            backup_of = _rel_to_project(backup)

    # Ensure parent dir exists
    target.parent.mkdir(parents=True, exist_ok=True)

    # Calculate relative path if source is inside PROJECT_ROOT, else absolute
    try:
        source.absolute().relative_to(PROJECT_ROOT.resolve())  # raises ValueError if not inside
        link_path = os.path.relpath(source, target.parent)
    except ValueError:
        link_path = source.absolute()
    try:
        os.symlink(link_path, target)
        print(f"  {GREEN}✓ Linked {target.name} -> {link_path}{NC}")
        _record(target, "symlink", agent=agent, backup_of=backup_of)
    except OSError as e:
        # Fallback for Windows (no admin rights) or restricted environments
        print(f"  {YELLOW}! Symlink failed ({e}), falling back to copy...{NC}")
        try:
            if source.is_dir():
                safe_merge_directory(source, target)
                _record(target, "tree", agent=agent, backup_of=backup_of)
            else:
                if target.exists():
                    target.unlink()
                shutil.copy2(source, target)
                _record(target, "copy", agent=agent, backup_of=backup_of)
            print(f"  {GREEN}✓ Copied {target.name} (Symlink fallback){NC}")
        except Exception as e2:
            print(f"  {RED}x Failed to copy {target}: {e2}{NC}")
    except Exception as e:
        print(f"  {RED}x Failed to link {target}: {e}{NC}")


def ensure_yaml_frontmatter(content, filename):
    """Ensures content has valid YAML frontmatter using PyYAML. Returns (frontmatter_dict, content)."""
    try:
        import yaml

        if content.startswith("---"):
            end_yaml = content.find("---", 3)
            if end_yaml != -1:
                yaml_text = content[3:end_yaml]
                data = yaml.safe_load(yaml_text)
                if isinstance(data, dict):
                    return data, content
    except ImportError:
        print(f"{YELLOW}Warning: PyYAML not installed. Falling back to simple parsing.{NC}")
        # Fallback to simple parser if PyYAML is missing (bootstrapping edge case)
        if content.startswith("---"):
            end_yaml = content.find("---", 3)
            if end_yaml != -1:
                yaml_text = content[3:end_yaml]
                data = {}
                for line in yaml_text.strip().split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        data[k.strip()] = v.strip().strip("\"'")
                return data, content
    except Exception:
        # print(f"Warning: Failed to parse YAML for {filename}: {e}")
        pass

    # Default frontmatter if missing or failed
    name = filename.replace(".skill.md", "").replace(".md", "").replace(".mdc", "")
    frontmatter = f"""---
name: {name}
description: AI Skill for {name}
version: 1.0
author: GABBE-Kit
---
"""
    return {"name": name}, frontmatter + content


def _snapshot_files(root):
    """Bytes of every regular file under `root`, keyed by path ({} if absent)."""
    root = Path(root)
    if not root.is_dir() or root.is_symlink():
        return {}
    return {p: p.read_bytes() for p in root.rglob("*") if p.is_file() and not p.is_symlink()}


def _record_generated_files(target_dir, before, agent):
    """Record each file the skill compiler wrote into `target_dir`, one entry per file.

    The directory may hold the user's own skills or rules, so it is never recorded
    as a whole. A user's file the compiler replaced (same name as a kit skill) is
    written back next to it as a backup and linked for restore on uninstall.
    """
    for path, data in sorted(_snapshot_files(target_dir).items()):
        old = before.get(path)
        if old is None:
            _record(path, "copy", agent=agent)
        elif old != data:
            backup_of = None
            if not _is_unchanged_kit_file(path, old):
                backup = _free_backup_path(path)
                backup.write_bytes(old)
                backup_of = _rel_to_project(backup)
                print(f"  {YELLOW}! Kept your {path.name} as {backup.name}{NC}")
            _record(path, "copy", agent=agent, backup_of=backup_of)
        elif (_rel_to_project(path) or "") in _prior_manifest_entries():
            _record(path, "copy", agent=agent)


def _kit_compiler():
    """The skill compiler of the kit being installed (this wizard's own source).

    Never the copy in the target project: that file may be the project's own code, or a
    link to it, and the wizard must not run it.
    """
    return SOURCE_AGENTS_DIR / "scripts" / "compile_skills.py"


def _emitted_skill_paths(agents_dir, base):
    """Every path the skill compiler writes under `base` for this kit, or None when its
    slug rules cannot be loaded. Uses the compiler's own `safe_slug`, so the two agree."""
    import importlib.util

    script = _kit_compiler()
    try:
        spec = importlib.util.spec_from_file_location("_gabbe_compile_skills", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        paths = set()
        for skill_file in (Path(agents_dir) / "skills").rglob("*.skill.md"):
            meta, _ = module.ensure_yaml_frontmatter(skill_file.read_text(), skill_file.name)
            stem = skill_file.stem.replace(".skill", "")
            slug = module.safe_slug(meta.get("name", stem), fallback=stem)
            paths.update({f"{base}/{slug}/SKILL.md", f"{base}/{slug}.mdc"})
        return paths
    except Exception:
        return None


def _remove_stale_generated_files(target_dir, agents_dir):
    """Remove generated skill or rule files that an older install recorded and the kit
    no longer emits.

    Why: a skill renamed between kit versions is emitted under a new folder or file
    name, and the old copy would stay beside it (the same skill twice). Called after
    `target_dir` was emitted into. A file is removed only when ALL hold: the earlier
    record names it; the compiler does not emit it (its slug rules decide, since the
    record cannot tell a re-written file from a leftover); it lies under `target_dir`; it is a
    recorded copy with the kit's marker in its first 4 KB; it is a regular file with
    no link on its path; and its bytes still equal the recorded hash. One the user
    changed is kept and reported. Removed paths leave the record.
    """
    import hashlib

    base = _rel_to_project(target_dir)
    if base is None or _is_behind_link(target_dir):
        return
    emitted = _emitted_skill_paths(agents_dir, base)
    if emitted is None:
        return
    removed, changed = 0, []
    for rel, entry in sorted(_prior_manifest_entries().items()):
        if rel in emitted or entry.get("kind") != "copy" or not entry.get("hash"):
            continue
        if not rel.startswith(base + "/") or not rel.endswith(("/SKILL.md", ".mdc")):
            continue
        path = PROJECT_ROOT / rel
        try:
            if _is_behind_link(path) or not path.is_file() or path.is_symlink():
                continue
            data = path.read_bytes()
            if b"gabbe-schema-version:" not in data[:4096]:
                continue
            if hashlib.sha256(data).hexdigest() != entry["hash"]:
                changed.append(rel)
                continue
            path.unlink()
            _DROPPED_PATHS.add(rel)
            _RECORDED_PATHS.discard(rel)
            _MANIFEST_ENTRIES[:] = [e for e in _MANIFEST_ENTRIES if e["path"] != rel]
            removed += 1
            if rel.endswith("/SKILL.md") and not any(path.parent.iterdir()):
                path.parent.rmdir()
        except OSError:
            continue
    if removed:
        print(
            f"  {GREEN}✓ Removed {removed} generated file(s) the kit no longer emits "
            f"(renamed skills){NC}"
        )
    if changed:
        print(
            f"  {YELLOW}! Kept {len(changed)} old generated file(s) you changed: "
            f"{', '.join(changed[:5])}{NC}"
        )


def _replace_own_skills_link(target_dir):
    """Take away the link an earlier wizard made at `target_dir` (for example
    `.windsurf/skills -> agents/skills`) so real `<slug>/SKILL.md` folders can be emitted.

    Only a link the earlier install recorded is the kit's own; any other link is the
    user's and stays. A folder of the user's that the link had replaced (moved to its
    recorded backup) is put back first, so their files are still there.
    """
    rel = _rel_to_project(target_dir) or ""
    prior = _prior_manifest_entries().get(rel)
    if not target_dir.is_symlink() or not prior or prior.get("kind") != "symlink":
        return
    target_dir.unlink()
    _DROPPED_PATHS.add(rel)
    backup = PROJECT_ROOT / prior["backup_of"] if prior.get("backup_of") else None
    if backup and _rel_to_project(backup) and backup.is_dir() and not backup.is_symlink():
        backup.rename(target_dir)
    print(f"  {BLUE}→ Replaced the kit's old link {rel} by skill folders{NC}")


def setup_skills_for_platform(platform, agents_dir, target_dir, agent=None):
    """
    Setup Skills for selected platform using the external compiler script.

    `agent` is the slug the emitted files are recorded under (default: from `platform`).
    """
    print(f"\n{BLUE}→ Setting up skills used by {platform}...{NC}")

    # Use external script for skill compilation to ensure consistency with setup-context.sh
    compile_script = _kit_compiler()
    _replace_own_skills_link(target_dir)
    if _is_behind_link(target_dir):
        # e.g. `.claude/skills -> agents/skills` made by another tool: compiling
        # into it would write through the link.
        print(
            f"  {YELLOW}! {target_dir} is a link, or sits behind one: skills not emitted there{NC}"
        )
        return
    if compile_script.exists():
        try:
            import subprocess

            cmd = [
                sys.executable,
                "-I",  # isolated: the project folder is not on the child's import path
                str(compile_script),
                "--platform",
                platform,
                "--skills-dir",
                str(agents_dir / "skills"),
                # For Cursor, target is .cursor/rules. For others, .github/skills usually.
                # However, the init logic passes specific target_dir.
                # We need to respect that or map it.
                # compile_skills.py expects a specific structure for 'All' or specific for others.
                # The arguments passed to this function in main() are:
                # Cursor: cursor_rules_dir (.cursor/rules)
                # VS Code: gh_dir / "skills" (.github/skills)
                # Claude: .claude/skills (symlinked, so maybe skipped here or handled by script)
                "--target-dir",
                str(target_dir),
                "--project-root",
                str(PROJECT_ROOT),
            ]
            before = _snapshot_files(target_dir)
            subprocess.run(cmd, check=True)
            print(f"  {GREEN}✓ Processed skills for {platform}{NC}")
            _record_generated_files(target_dir, before, agent=agent or _agent_slug(platform))
            _remove_stale_generated_files(target_dir, agents_dir)
        except Exception as e:
            print(f"{RED}Error running skill compiler: {e}{NC}")
    else:
        print(f"{RED}Warning: compile_skills.py not found at {compile_script}{NC}")
        # Fallback logic could go here, but we want to enforce the script usage.


# --- Main Logic ---


def run_bench():
    """R13: time a full skill-catalogue emit per platform (Pillar 8 regression
    gate). Non-interactive; prints a JSON report and exits. Invoked with
    `python scripts/init.py --bench`."""
    import json as _json
    import tempfile
    import time

    platforms = {
        "cursor": "Cursor",
        "copilot": "GitHub Copilot",
        "claude": "Claude Code",
    }
    results = {}
    skill_count = len(list((SOURCE_AGENTS_DIR / "skills").rglob("*.skill.md")))
    for key, platform in platforms.items():
        with tempfile.TemporaryDirectory(prefix=f"gabbe-bench-{key}-") as tmp:
            target = Path(tmp) / "out"
            t0 = time.perf_counter()
            setup_skills_for_platform(platform, SOURCE_AGENTS_DIR, target)
            results[key] = round(time.perf_counter() - t0, 4)
    report = {"skill_count": skill_count, "emit_seconds": results}
    print(_json.dumps(report, indent=2))
    return report


def main():
    """Run the wizard. If it stops part-way, what it had written is still recorded,
    so `gabbe uninstall` can remove it."""
    try:
        _run_wizard()
    except BaseException as stop:
        try:
            write_install_manifest()
        except Exception:
            pass
        if isinstance(stop, EOFError):
            raise SystemExit(
                f"{RED}x The wizard asks questions and its input ended. Run it in a terminal, or "
                f"use `npx gabbe-kit init --yes --agents <list>` for an install without "
                f"questions.{NC}"
            ) from None
        raise


def _run_wizard():
    global PROJECT_ROOT, FORCE, HOOKS
    # Start each run with a clean manifest recorder (globals persist in-process).
    _MANIFEST_ENTRIES.clear()
    _RECORDED_PATHS.clear()
    _UNFILLED_PLACEHOLDERS.clear()
    _UNFILLED_FREE_TEXT[0] = 0
    _DROPPED_PATHS.clear()
    if "--bench" in sys.argv:
        run_bench()
        return
    if "--force" in sys.argv:
        FORCE = True
    HOOKS = "--hooks" in sys.argv
    if not SOURCE_AGENTS_DIR.exists():
        if (KIT_SOURCE / "AGENTS.md").exists():
            pass
        else:
            print(f"{RED}Error: Could not find source agents directory at {SOURCE_AGENTS_DIR}{NC}")
            sys.exit(1)

    # Validate required subdirectories exist before proceeding
    for subdir in ["guides", "skills", "templates", "personas", "memory", "scripts"]:
        if not (SOURCE_AGENTS_DIR / subdir).exists():
            print(f"{RED}Error: Missing required subdirectory: agents/{subdir}/{NC}")
            sys.exit(1)

    # Initialize Dynamic Tech Map
    global TECH_MAP
    TECH_MAP = build_tech_map_from_skills(SOURCE_AGENTS_DIR)

    clear_screen()
    print_header()

    # --- Step 1: Install Location ---
    print(f"{YELLOW}Part 1: Installation{NC}")
    print("Where should the Agent Kit be installed?")

    install_opts = [
        f"Local (Recommended) - Installs to {PROJECT_ROOT}/agents",
        f"Global - Installs to {Path.home()}/agents (All projects share this)",
        "Custom Path",
    ]

    choice_idx = select_index("Select Install Location", install_opts)

    target_agents_dir = None

    if choice_idx == 0:
        target_agents_dir = PROJECT_ROOT / "agents"
    elif choice_idx == 1:
        target_agents_dir = Path.home() / "agents"
        print(
            f"  {YELLOW}! Global installs the kit to {target_agents_dir}. That install is not "
            f"recorded in .gabbe/manifest.json, and it is not the place that "
            f"`gabbe update --global` and `gabbe uninstall --global` use "
            f"($XDG_DATA_HOME/gabbe).{NC}"
        )
    else:
        path_str = ask("Enter absolute path")
        user_path = Path(path_str).resolve()

        if user_path.name == "agents":
            target_agents_dir = user_path
            PROJECT_ROOT = user_path.parent
        else:
            target_agents_dir = user_path / "agents"
            PROJECT_ROOT = user_path

    leaf_problem = _manifest_leaf_problem(PROJECT_ROOT / ".gabbe" / "manifest.json")
    if leaf_problem:
        raise SystemExit(
            f"{RED}x {leaf_problem}. Remove the link or point it at nothing, then run the "
            f"installer again. Nothing was changed.{NC}"
        )

    # Perform Install / Copy
    IS_UPDATE = False
    if target_agents_dir.exists() and not target_agents_dir.is_dir():
        raise SystemExit(
            f"{RED}x {target_agents_dir} exists and is not a folder. Move it away and run "
            f"the installer again. Nothing was changed.{NC}"
        )
    if target_agents_dir.is_symlink():
        # A link of the user's to a kit kept elsewhere: use it, never copy into it.
        print(
            f"  {BLUE}→ {target_agents_dir} is a link to {target_agents_dir.resolve()}: "
            f"using the kit there as it is; nothing is copied into it.{NC}"
        )
        IS_UPDATE = True
    elif target_agents_dir.exists():
        if target_agents_dir.resolve() == SOURCE_AGENTS_DIR.resolve():
            print(
                f"  {BLUE}→ Target is the same as source directory ({target_agents_dir}), skipping copy.{NC}"
            )
            IS_UPDATE = True
        else:
            print(f"\n{YELLOW}! Directory {target_agents_dir} already exists.{NC}")
            update = ask("Install/Merge kit files into this directory? (y/n)", "y")
            if update.lower() == "y":
                IS_UPDATE = True
                safe_merge_directory(SOURCE_AGENTS_DIR, target_agents_dir, is_kit_root=True)
                print(f"  {GREEN}✓ Kit merged/updated at {target_agents_dir}{NC}")
            else:
                IS_UPDATE = True
                print(f"  {BLUE}→ Using existing files at {target_agents_dir}{NC}")
    else:
        shutil.copytree(SOURCE_AGENTS_DIR, target_agents_dir)
        print(f"  {GREEN}✓ Kit installed to {target_agents_dir}{NC}")
        # Record the freshly-copied kit tree (only if it lives under PROJECT_ROOT;
        # global/custom installs outside the project are not in its manifest).
        _record_tree(target_agents_dir)

    AGENTS_DIR = target_agents_dir

    # --- Step 2: Interview ---
    print(f"\n{YELLOW}Part 2: Project Context{NC}")

    # Brownfield autodetect: recognise an existing codebase and prefill from it.
    detected = detect_existing_project(PROJECT_ROOT)
    refactor_mode = False
    if detected.get("is_existing"):
        print(
            f"  {BLUE}→ Existing project detected ({', '.join(detected.get('signals', [])) or 'source present'}).{NC}"
        )
        if detected.get("language"):
            print(f"  {BLUE}→ Stack looks like: {detected['language']}", end="")
            if detected.get("framework"):
                print(f" / {detected['framework']}", end="")
            print(f"{NC}")
        mode_idx = select_index(
            "How should GABBE engage this project?",
            [
                "Greenfield build — scaffold a new system here",
                "Upgrade / Refactor — onboard onto the EXISTING codebase",
            ],
        )
        refactor_mode = mode_idx == 1

    project_name = ask("Project Name", detected.get("project_name") or PROJECT_ROOT.name)
    description = ask("One-line Description", "A new software project")

    # Team & Type
    team_size_idx = select_index(
        "Team Size", ["Solo (1 dev)", "Small (2-5 devs)", "Large (6+ devs, Enterprise)"]
    )
    team_size = ["Solo", "Small", "Large"][team_size_idx]

    project_type = select(
        "Project Type",
        [
            "Greenfield (New)",
            "Legacy Modernization",
            "Enterprise / Regulated",
            "R&D / Prototype",
        ],
    )

    compliance = []
    if project_type == "Enterprise / Regulated":
        compliance = ask_multiselect(
            "Compliance Requirements", ["GDPR", "HIPAA", "PCI-DSS", "SOC2", "ISO 27001"]
        )

    # Tech Stack
    print(f"\n{YELLOW}Part 3: Technology Stack{NC}")
    language_choice = select(
        "Primary Language",
        [
            "TypeScript",
            "JavaScript",
            "Python",
            "PHP",
            "Go",
            "Rust",
            "Java",
            "C#",
            "Other",
        ],
    )
    language = language_choice
    if language_choice == "Other":
        language = ask("Enter Language")

    framework = ask(
        "Primary Framework (e.g. Next.js, FastAPI, Laravel)",
        detected.get("framework") or "None",
    )

    db_options = ["PostgreSQL", "MySQL/MariaDB", "MongoDB", "SQLite", "Redis", "None"]
    databases = ask_multiselect("Databases used", db_options)

    cloud_options = [
        "AWS",
        "Google Cloud",
        "Azure",
        "Vercel",
        "Railway",
        "DigitalOcean",
        "On-Prem",
    ]
    clouds = ask_multiselect("Infrastructure / Cloud", cloud_options)  # noqa: F841

    # --- Dynamic Setup Check ---
    dynamic_setup = False
    problem_statement = ""
    print(f"\n{YELLOW}Part 3.1: Dynamic Agent Capabilities{NC}")
    if (
        ask(
            "Enable Dynamic Agent Setup (Live Research & Auto-Configuration)? (y/n)",
            "y",
        ).lower()
        == "y"
    ):
        dynamic_setup = True
        while True:
            problem_statement = ask(
                "What specific problem is this system solving? (e.g. 'High-frequency trading bot', 'Medical image analysis')"
            )
            if problem_statement.strip():
                break
            print(
                f"{RED}⚠ Problem statement cannot be empty. Please describe the problem this system solves.{NC}"
            )

    # --- Analytics Check ---
    enable_analytics = False
    if (
        ask(
            "Enable Agent Analytics (Track tokens, loops, and success rates)? (y/n)",
            "y",
        ).lower()
        == "y"
    ):
        enable_analytics = True

    # --- Meta-Evolution Check ---
    enable_meta = False
    if ask("Enable Self-Evolving Capabilities (Meta-Optimization)? (y/n)", "y").lower() == "y":
        enable_meta = True  # noqa: F841

    # --- GABBE CLI Integration ---
    enable_gabbe_cli = False
    gabbe_cli_mode = "manual"  # "manual" | "mcp"
    print(f"\n{YELLOW}Part 3.2: GABBE CLI Platform Controls{NC}")
    print("The GABBE CLI provides optional budget enforcement, audit trails,")
    print("replay, escalation, and cost routing for agent runs.")
    print("It can be used manually or enforced through the MCP server.")
    if (
        ask(
            "Enable GABBE CLI platform controls? (y/n)",
            "n",
        ).lower()
        == "y"
    ):
        enable_gabbe_cli = True
        mode_idx = select_index(
            "CLI Integration Mode",
            [
                "Manual Only — You run gabbe commands yourself when needed",
                "MCP Enforced — Agents use gabbe exclusively through the MCP server",
            ],
        )
        gabbe_cli_mode = ["manual", "mcp"][mode_idx]

    # --- Step 3: Gap Analysis ---

    missing_skills = []
    # Framework gap
    fw_key = framework.lower()
    if fw_key not in TECH_MAP and fw_key != "none":
        missing_skills.append(f"{fw_key}-best-practices")

    # Language gap
    lang_key = language.lower()
    if lang_key not in TECH_MAP and lang_key != "other":
        missing_skills.append(f"{lang_key}-idioms")

    # Domain gap
    if project_type == "Legacy Modernization":
        missing_skills.extend(TECH_MAP.get("legacy", {}).get("skills", []))
    if project_type == "Enterprise / Regulated":
        missing_skills.extend(TECH_MAP.get("enterprise", {}).get("skills", []))
    if compliance:
        missing_skills.extend(TECH_MAP.get("regulated", {}).get("skills", []))

    # --- Step 4: Generate AGENTS.md ---
    print(f"\n{YELLOW}Part 4: Configuring Installed Kit{NC}")

    target_agents_md = AGENTS_DIR / "AGENTS.md"
    template_path = AGENTS_DIR / "templates/coordination/AGENTS_TEMPLATE.md"

    skip_step_4 = False
    if IS_UPDATE and target_agents_md.exists():
        print(
            f"  {BLUE}→ AGENTS.md already exists. Skipping auto-generation to preserve user modifications.{NC}"
        )
        print(f"  {BLUE}→ Check {template_path.name} for any new additions.{NC}")
        skip_step_4 = True

    if not skip_step_4 and template_path.exists():
        content = template_path.read_text()

        # Replacements
        content = content.replace("{{ project_name }}", project_name)
        content = content.replace("{{ description }}", description)
        content = content.replace("{{ language }}", language)
        content = content.replace("{{ framework }}", framework)
        content = content.replace("{{ runtime }}", "Latest")
        content = content.replace("{{ database }}", ", ".join(databases) if databases else "None")

        # Package Manager
        pm = "npm"
        if language.lower() in ["python"]:
            pm = "pip"
        if language.lower() in ["php"]:
            pm = "composer"
        if language.lower() in ["go"]:
            pm = "go mod"
        if language.lower() in ["rust"]:
            pm = "cargo"
        elif language_choice == "Other":
            pm = ask("Which package manager? (e.g. cargo, mix, gradle, make, none)", "none")

        if language.lower() in ["javascript", "typescript"]:
            pm_choice = select("Package Manager", ["npm", "pnpm", "yarn"])
            pm = pm_choice

        content = content.replace("{{ package_manager }}", pm)

        # Commands
        install_cmd = f"{pm} install"
        test_cmd = f"{pm} test"
        if pm == "pip":
            install_cmd = "pip install -r requirements.txt"
            test_cmd = "pytest"
        if pm == "go mod":
            install_cmd = "go mod download"
            test_cmd = "go test ./..."
        if pm == "cargo":
            install_cmd = "cargo build"
            test_cmd = "cargo test"

        lines = content.splitlines()
        new_lines = []
        for line in lines:
            if "install:" in line and "{{" in line:
                new_lines.append(f'install: "{install_cmd}"')
            elif (
                ("test:" in line or "test_cmd" in line)
                and "{{" in line
                and "test_single" not in line
            ):
                new_lines.append(f'test: "{test_cmd}"')
            elif "security_scan:" in line and "{{" in line:
                audit_cmd = f"{pm} audit"
                if pm == "pip":
                    audit_cmd = "pip-audit"
                if pm == "go mod":
                    audit_cmd = "govulncheck ./..."
                if pm == "cargo":
                    audit_cmd = "cargo audit"
                new_lines.append(f'security_scan: "{audit_cmd}"')
            elif "build:" in line and "{{" in line:
                build_cmd = f"{pm} run build"
                if pm == "go mod":
                    build_cmd = "go build -o app"
                if pm == "cargo":
                    build_cmd = "cargo build --release"
                if pm == "pip":
                    build_cmd = "# No build step for Python"
                new_lines.append(f'build: "{build_cmd}"')
            else:
                new_lines.append(line)

        content = "\n".join(new_lines)

        # --- Conditional GABBE CLI Section ---
        cli_start = "<!-- GABBE_CLI_START -->"
        cli_end = "<!-- GABBE_CLI_END -->"
        if not enable_gabbe_cli:
            # Strip the entire CLI section
            if cli_start in content and cli_end in content:
                before = content[: content.find(cli_start)]
                after = content[content.find(cli_end) + len(cli_end) :]
                content = before + after
                print(f"  {BLUE}→ GABBE CLI section removed (disabled){NC}")
        else:
            # Keep the section, inject mode-specific notice
            if gabbe_cli_mode == "mcp":
                mcp_notice = (
                    "\n> [!IMPORTANT]\n"
                    "> **MCP Enforced Mode**: All gabbe CLI commands MUST be executed through the `gabbe serve-mcp` MCP server.\n"
                    "> Agents must NOT run `gabbe` commands directly. Use the MCP `tools/call` JSON-RPC method instead.\n"
                )
                content = content.replace(cli_start, cli_start + mcp_notice)
                print(f"  {GREEN}✓ GABBE CLI enabled (MCP Enforced mode){NC}")
            else:
                manual_notice = (
                    "\n> [!NOTE]\n"
                    "> **Manual Mode**: The gabbe CLI is available for human use. Run commands directly when needed.\n"
                    "> Agents are NOT required to use these commands but may reference them.\n"
                )
                content = content.replace(cli_start, cli_start + manual_notice)
                print(f"  {GREEN}✓ GABBE CLI enabled (Manual mode){NC}")
            # Strip the marker comments themselves for clean output
            content = content.replace(cli_start, "").replace(cli_end, "")

        # Fill derivable [PLACEHOLDER:] fields (commands, repo_url, ci/cd,
        # deploy target); tag the rest OPTIONAL and record them for a warning.
        content = populate_placeholders(content, pm, PROJECT_ROOT)

        target_agents_md = AGENTS_DIR / "AGENTS.md"
        if _is_behind_link(target_agents_md):
            print(f"  {YELLOW}! {target_agents_md} is a link of yours: left as is{NC}")
        else:
            target_agents_md.write_text(content)
            # Refresh the manifest hash now that AGENTS.md holds substituted content
            # (the earlier copy recorded the raw template hash).
            _record(target_agents_md, "copy", agent="shared")
            print(f"  {GREEN}✓ Configured {target_agents_md}{NC}")
    else:
        print(f"  {RED}x Template not found: {template_path}{NC}")

    # --- Step 4.1: Append to CONSTITUTION.md ---
    if not IS_UPDATE and (compliance or project_type == "Legacy Modernization"):
        const_path = AGENTS_DIR / "CONSTITUTION.md"
        if const_path.exists() and not _is_behind_link(const_path):
            with open(const_path, "a") as f:
                f.write("\n\n## Project-Specific Articles (Auto-Generated)\n")
                # Number project-specific articles after the universal set
                # (I–XI) to avoid colliding with Articles VIII/IX/X.
                if "Legacy Modernization" in project_type:
                    f.write("\n### Article XII. The Modernization Mandate\n")
                    f.write(
                        "All new code must adhere to modern patterns. Legacy code touched must be refactored to >99% coverage (Boy Scout Rule).\n"
                    )
                if compliance:
                    f.write(
                        f"\n### Article XIII. Regulatory Compliance ({', '.join(compliance)})\n"
                    )
                    f.write(
                        "No PII shall be logged. All data at rest must be encrypted. Security audit is mandatory before Release.\n"
                    )
            print(f"  {GREEN}✓ Updated CONSTITUTION.md with specific Articles{NC}")

    # --- Step 5: Directory Wiring ---
    print(f"\n{YELLOW}Part 5: Wiring Agent Context{NC}")

    loki_mem = AGENTS_DIR / "memory"
    _make_dirs(loki_mem / "episodic/SESSION_SNAPSHOT")
    _make_dirs(loki_mem / "semantic")

    if enable_analytics:
        _make_dirs(loki_mem / "metrics")
        print(f"  {GREEN}✓ Initialized Analytics Directory{NC}")

        state_file = loki_mem / "PROJECT_STATE.md"
        if _is_behind_link(state_file):
            print(
                f"  {YELLOW}! {state_file.name} is a link of yours, or behind one: left as is{NC}"
            )
        else:
            state_file.write_text("# PROJECT_STATE.md\n\nPhase: S00_INITIALIZED\n")
            print(f"  {GREEN}✓ Initialized Loki Memory{NC}")

    _is_windows = sys.platform == "win32"

    # setup-context.sh/.ps1 stay in agents/scripts/: the script derives the project
    # root from its own location (scripts/../..), so a copy at the project root
    # would write .claude/, .cursorrules, memory/ ... into the folder above it.
    _setup_name = "setup-context.ps1" if _is_windows else "setup-context.sh"
    _setup_path = AGENTS_DIR / "scripts" / _setup_name
    if _setup_path.exists():
        try:
            _setup_shown = _setup_path.relative_to(PROJECT_ROOT)
        except ValueError:
            _setup_shown = _setup_path
        print(f"  {GREEN}✓ Context script: {_setup_shown} (run it from there){NC}")

    # Symlinks
    skills_src = AGENTS_DIR / "skills"
    agents_md_src = AGENTS_DIR / "AGENTS.md"

    agents = ask_multiselect(
        "Which AI Agents are you using?",
        [
            "Claude Code",
            "Cursor",
            "Windsurf",
            "Cline",
            "Aider",
            "Devin / Cognition",
            "Gemini",
            "Antigravity",
            "OpenCode",
            "Zed",
            "Continue",
            "Roo Code",
            "Kilo Code",
            "OpenAI / Codex",
            "GitHub Copilot",
            "VS Code",
        ],
    )

    if "Claude Code" in agents:
        claude_dir = PROJECT_ROOT / ".claude"
        claude_dir.mkdir(exist_ok=True)
        create_symlink(agents_md_src, claude_dir / "CLAUDE.md", agent=_agent_slug("Claude Code"))
        # Generate real .claude/skills/<slug>/SKILL.md directories (the agent-skills
        # open standard). Claude Code only discovers <name>/SKILL.md directories,
        # not the legacy <name>.skill.md file tree, so we must NOT symlink the
        # source skills/ dir here.
        setup_skills_for_platform("Claude Code", AGENTS_DIR, claude_dir / "skills")

    if "Cursor" in agents:
        cursor_dir = PROJECT_ROOT / ".cursor"
        cursor_rules_dir = cursor_dir / "rules"
        create_symlink(agents_md_src, PROJECT_ROOT / ".cursorrules", agent=_agent_slug("Cursor"))
        setup_skills_for_platform("Cursor", AGENTS_DIR, cursor_rules_dir)

    if "Windsurf" in agents:
        slug = _agent_slug("Windsurf")
        create_symlink(agents_md_src, PROJECT_ROOT / ".windsurfrules", agent=slug)
        windsurf_dir = PROJECT_ROOT / ".windsurf"
        windsurf_dir.mkdir(exist_ok=True)
        # Real <slug>/SKILL.md folders, as the Node installer emits: a tree of
        # `*.skill.md` files is not discovered by these tools.
        setup_skills_for_platform("Universal", AGENTS_DIR, windsurf_dir / "skills", agent=slug)

    if "Cline" in agents:
        slug = _agent_slug("Cline")
        create_symlink(agents_md_src, PROJECT_ROOT / ".clinerules", agent=slug)
        cline_dir = PROJECT_ROOT / ".cline"
        cline_dir.mkdir(exist_ok=True)
        setup_skills_for_platform("Universal", AGENTS_DIR, cline_dir / "skills", agent=slug)

    if "Devin / Cognition" in agents:
        slug = _agent_slug("Devin / Cognition")
        create_symlink(agents_md_src, PROJECT_ROOT / ".devinrules", agent=slug)
        devin_dir = PROJECT_ROOT / ".devin"
        devin_dir.mkdir(exist_ok=True)
        setup_skills_for_platform("Universal", AGENTS_DIR, devin_dir / "skills", agent=slug)

    if "Aider" in agents:
        aider_conf = PROJECT_ROOT / ".aider.conf.yml"
        if not (aider_conf.exists() or aider_conf.is_symlink()):
            aider_conf.write_text("read:\n  - agents/AGENTS.md\n  - agents/skills/\n")
            _record(aider_conf, "copy", agent="aider")
            print(f"  {GREEN}✓ Wired .aider.conf.yml{NC}")

    # "Gemini" is the split-out target; "Gemini / Antigravity" kept for backward
    # compatibility with older saved selections and the emitter golden harness.
    if "Gemini" in agents or "Gemini / Antigravity" in agents:
        gemini_dir = PROJECT_ROOT / ".gemini"
        gemini_dir.mkdir(exist_ok=True)
        try:
            # Use paths relative to PROJECT_ROOT for cleaner config
            rel_agents = os.path.relpath(agents_md_src, PROJECT_ROOT)
            rel_skills = os.path.relpath(skills_src, PROJECT_ROOT)
        except Exception:
            rel_agents = str(agents_md_src.absolute())
            rel_skills = str(skills_src.absolute())

        settings_content = {
            "agent_instructions_file": rel_agents,
            "skills_directory": rel_skills,
            "contextFileName": "GEMINI.md",
            "gabbe-schema-version": 1,
            "notes": "Managed by init.py",
        }
        gemini_settings = gemini_dir / "settings.json"
        if gemini_settings.exists() and not _is_unchanged_kit_file(
            gemini_settings, gemini_settings.read_bytes()
        ):
            # The user's own settings: never replace them (same as the Node installer).
            print(f"  {BLUE}→ .gemini/settings.json exists, leaving as-is{NC}")
        else:
            write_generated_file(
                gemini_settings, json.dumps(settings_content, indent=2), agent="gemini"
            )
        # Gemini CLI natively reads a GEMINI.md context file; point it at AGENTS.md.
        create_symlink(agents_md_src, PROJECT_ROOT / "GEMINI.md", agent="gemini")
        print(f"  {GREEN}✓ Wired .gemini/settings.json + GEMINI.md{NC}")

    # Universal agentskills.io target: .agents/skills/<slug>/SKILL.md is read by
    # Antigravity, OpenCode, GitHub Copilot CLI, ~/.agents/skills, and any
    # agentskills.io-conformant tool — emitted once when any such agent is selected.
    if "Antigravity" in agents:
        # Antigravity (v1.20.3+) reads the root AGENTS.md (emitted below) and
        # discovers skills at .agents/skills/<slug>/SKILL.md.
        setup_skills_for_platform("Antigravity", AGENTS_DIR, PROJECT_ROOT / ".agents" / "skills")
        print(f"  {GREEN}✓ Wired Antigravity (.agents/skills + root AGENTS.md){NC}")

    if "OpenCode" in agents:
        # OpenCode reads the root AGENTS.md and an opencode.json `instructions` array.
        opencode_conf = PROJECT_ROOT / "opencode.json"
        if not (opencode_conf.exists() or opencode_conf.is_symlink()):
            opencode_conf.write_text(
                json.dumps(
                    {
                        "$schema": "https://opencode.ai/config.json",
                        "instructions": ["AGENTS.md", "agents/skills/"],
                    },
                    indent=2,
                )
                + "\n"
            )
            _record(opencode_conf, "copy", agent="opencode")
        setup_skills_for_platform("OpenCode", AGENTS_DIR, PROJECT_ROOT / ".agents" / "skills")
        print(f"  {GREEN}✓ Wired opencode.json + .agents/skills{NC}")

    if "Zed" in agents:
        # Zed reads the root AGENTS.md natively; also wire its `.rules` convention.
        create_symlink(agents_md_src, PROJECT_ROOT / ".rules", agent=_agent_slug("Zed"))

    if "Continue" in agents:
        cont_dir = PROJECT_ROOT / ".continue" / "rules"
        _make_dirs(cont_dir)
        create_symlink(agents_md_src, cont_dir / "agents.md", agent=_agent_slug("Continue"))

    if "Roo Code" in agents:
        roo_dir = PROJECT_ROOT / ".roo" / "rules"
        _make_dirs(roo_dir)
        create_symlink(agents_md_src, roo_dir / "agents.md", agent=_agent_slug("Roo Code"))

    if "Kilo Code" in agents:
        kilo_dir = PROJECT_ROOT / ".kilocode" / "rules"
        _make_dirs(kilo_dir)
        create_symlink(agents_md_src, kilo_dir / "agents.md", agent=_agent_slug("Kilo Code"))

    if "OpenAI / Codex" in agents:
        codex_dir = PROJECT_ROOT / ".codex"
        codex_dir.mkdir(exist_ok=True)
        create_symlink(agents_md_src, codex_dir / "AGENTS.md", agent=_agent_slug("OpenAI / Codex"))

    if "GitHub Copilot" in agents:
        gh_dir = PROJECT_ROOT / ".github"
        gh_dir.mkdir(exist_ok=True)
        create_symlink(
            agents_md_src,
            gh_dir / "copilot-instructions.md",
            agent=_agent_slug("GitHub Copilot"),
        )
        setup_skills_for_platform("GitHub Copilot", AGENTS_DIR, gh_dir / "skills")

    if "VS Code" in agents:  # Added VS Code explicitly if requested, reusing logic
        gh_dir = PROJECT_ROOT / ".github"
        setup_skills_for_platform("VS Code", AGENTS_DIR, gh_dir / "skills")

    # Optional hooks: only with the --hooks flag (no wizard question is asked).
    if HOOKS:
        install_hooks(agents, AGENTS_DIR)

    # Root AGENTS.md (the agents.md open standard, read by Codex, Cursor,
    # Gemini CLI, and the Copilot coding agent). Emitted once for all agents.
    root_agents_md = PROJECT_ROOT / "AGENTS.md"
    if root_agents_md.resolve() != agents_md_src.resolve():
        create_symlink(agents_md_src, root_agents_md)
        print(f"  {GREEN}✓ Wired root AGENTS.md (agents.md standard){NC}")

    # --- Step 6: Gitignore ---
    gitignore = PROJECT_ROOT / ".gitignore"
    if gitignore.exists() and not gitignore.is_symlink():
        content = gitignore.read_text()
        if ".env" not in content:
            with open(gitignore, "a") as f:
                f.write("\n.env\n.env.local\n")
            print(f"  {GREEN}✓ Added .env to .gitignore{NC}")

    # --- Step 7: Mission Generation ---
    print(f"\n{YELLOW}Part 6: Agent Mission Generation{NC}")

    if dynamic_setup:
        mission = f"""
# BOOTSTRAP MISSION: Dynamic Agent Setup
**Goal**: Research, Configure, and Build a robust {project_type} system for "{project_name}".

## Context
- **Problem**: {problem_statement}
- **Stack**: {language} / {framework}
- **Constraints**: {", ".join(compliance) if compliance else "None"}
- **Missing Skills**: {", ".join(missing_skills) if missing_skills else "Standard Set"}

## Agent instructions
- Read AGENTS.md and CONSTITUTION.md for more information on this agentic system.
- Make sure that the project state, audit, gates, human-in-the-loop, and workflows, are always taken into account.
- Read agents/guides/ skills/ templates/ for any relevant information discovered during research and added by you or other agents.

## Phase 1: Dynamic Research (The "Search" Phase)
You are authorized to use `search_web` and `run_command` freely.
1.  **Landscape Analysis**: Search for "best {language} libraries for {problem_statement} in 2026".
2.  **Skill Acquisition**:
    -   Check `github.com/heilcheng/awesome-agent-skills` or similar repos.
    -   Download relevant skill templates or create new `.skill.md` files for discovered tools.
    -   Example: If building a trading bot, create `financial-analysis.skill.md`.

## Phase 2: Rigorous "Definition of Done" Setup
You MUST NOT write implementation code until these artifacts are approved:
1.  **Requirements**: `PRD.md` with clear User Stories.
2.  **Architecture**: `PLAN.md` with C4 diagrams and "System Context".
3.  **Specs**: `SPEC.md` with API schemas and Database models.
4.  **Acceptance Criteria**: E2E test scenarios defined in `features/` or `tests/`.

## Phase 3: Execution Strategy
-   Run `init` on the project framework (e.g., `npm init`, `cargo new`).
-   Install the dependencies found in Phase 1.
-   Execute the **Loki Loop** (Plan -> Test -> Code -> Verify).

## Mandatory Checkpoints
-   [ ] Research completed & Skills added
-   [ ] Architecture approved by Human
-   [ ] CI/CD Pipeline configured
-   [ ] Compliance Audit passed (if regulated)

Start by running: `agents/scripts/setup-context.sh` to confirm your environment.
"""
        mission_file = PROJECT_ROOT / "BOOTSTRAP_MISSION.md"
        write_generated_file(mission_file, mission)
        print(f"\n{GREEN}✓ Generated Dynamic BOOTSTRAP_MISSION.md{NC}")
        print(
            f"{BLUE}>> INSTRUCTION: Agent, please read BOOTSTRAP_MISSION.md and begin Phase 1 immediately.{NC}"
        )

    else:
        # Standard Static Mission
        mission = f"""
I have initialized the GABBE Agentic Engineering Kit for this project.
Here is your mission to finalize the setup:

0. Agent instructions
    - Read AGENTS.md and CONSTITUTION.md for more information on this agentic system.
    - Make sure that the project state, audit, gates, human-in-the-loop, and workflows, are always taken into account.
    - Read agents/guides/ skills/ templates/ for any relevant information discovered during research and added by you or other agents.

1.  **Analyze the Gap**: We are using {language} and {framework}.
    -   Missing Skills: {", ".join(missing_skills) if missing_skills else "None detected"}.
    -   Project Type: {project_type}.
    -   Compliance: {", ".join(compliance) if compliance else "None"}.

2.  **MCP Configuration**:
    -   Review `agents/templates/core/MCP_CONFIG_TEMPLATE.json`.
    -   Install "Context-7 MCP" (Essential for docs).
    -   If we are using Postgres, install "PostgreSQL MCP".

3.  **Research & Create (Deep Context Mode)**:
    -   **Standards Check**: Research SWEBOK/ISO/IEEE standards relevant to a {project_type} project in {language}.
    -   **Gap Analysis**: Compare the installed skills against the specific needs of {framework} in 2026.
    -   **Generate**: Create key missing skills. Example: `agents/skills/{framework.lower()}-best-practices.skill.md`.
    -   **Architectural Pattern**: Identify the best pattern (e.g., Clean Arch, Hexagonal, Vertical Slice) for this stack and document it in `AGENTS.md`.
"""
        if team_size == "Large":
            mission += "\n4.  **Loki Mode Activation**:\n    -   Review `agents/skills/brain/README_ORCHESTRATORS.md`.\n    -   Deploy the Personas from `agents/personas/` to my active tool context.\n"

        mission += """
5.  **Mandatory Guardrails**:
    -   **Ethics**: Run `ai-ethics-compliance` skill on the initial specs.
    -   **Safety**: Install `ai-safety-guardrails` hooks.
"""

        mission += "\n6.  **Verify**:\n    -   Run `integrity-check` skill to ensure all symlinks and configs are valid.\n"

        print("-" * 60)
        print(mission)
        print("-" * 60)

        mission_file = PROJECT_ROOT / "SETUP_MISSION.md"
        write_generated_file(mission_file, mission)
        print(f"\n{GREEN}✓ Mission saved to SETUP_MISSION.md{NC}")

    # --- Brownfield onboarding artifact ---
    # In Upgrade/Refactor mode the first job is to UNDERSTAND the existing code,
    # not scaffold greenfield mission docs. Emit a discovery brief that steers the
    # agent to map the codebase before changing anything.
    if refactor_mode:
        write_brownfield_assessment(project_name, detected)

    # Persist the uninstall manifest of everything we created under PROJECT_ROOT.
    write_install_manifest()

    # Never ship blank fields silently: if any [PLACEHOLDER:] remain (skipped
    # interactive setup, or genuinely project-specific fields), tell the user
    # exactly what to complete and how.
    if _UNFILLED_PLACEHOLDERS or _UNFILLED_FREE_TEXT[0]:
        _print_unfilled_fields()

    print(f"{BLUE}Setup Complete! The kit is installed at: {AGENTS_DIR}{NC}")


def write_brownfield_assessment(project_name, detected):
    """Scaffold a discovery/onboarding brief for an existing codebase."""
    stack = detected.get("language") or "unknown"
    if detected.get("framework"):
        stack += f" / {detected['framework']}"
    signals = ", ".join(detected.get("signals", [])) or "existing source"
    doc = f"""# Brownfield Onboarding — {project_name}

> GABBE installed in **Upgrade / Refactor** mode. This is an EXISTING codebase
> ({signals}). Do NOT scaffold a greenfield system. First understand, then change.

## Detected
- Stack: {stack}
- Package manager: {detected.get('package_manager') or 'unknown'}
- Git repository: {'yes' if detected.get('has_git') else 'no'}

## Phase 0 — Discovery (do this before any change)
1. **Map the codebase**: entry points, modules, data flow, external deps. Record
   findings in `agents/memory/semantic/` and a top-level `CODEBASE_MAP.md`.
2. **Assess current state**: build/test/CI status, obvious tech debt, risky areas,
   test coverage. Capture in `ASSESSMENT.md`.
3. **Establish a baseline**: get the existing build + tests green and recorded
   BEFORE refactoring, so regressions are detectable.
4. **Backlog**: turn findings into a prioritised improvement backlog in `TASKS.md`
   (use the kit's task templates). Sequence by risk/value.

## Phase 1+ — Change safely
- Work in small, reversible increments; keep the baseline green at every step.
- Apply the relevant kit guides/skills for {stack}.
- Use `gabbe verify` / your SDLC gates on each increment.

## Safety
- GABBE is additive: it has NOT modified your source. Any file it would have
  overwritten was backed up to `<name>.gabbe-bak`. `gabbe uninstall` reverses
  the install and restores backups.
"""
    out = PROJECT_ROOT / "BROWNFIELD_ONBOARDING.md"
    write_generated_file(out, doc)
    print(f"  {GREEN}✓ Brownfield onboarding brief saved to BROWNFIELD_ONBOARDING.md{NC}")


def _drop_project_from_import_path():
    """Keep the project folder (the current folder) off `sys.path`, so a `gabbe/` or any
    module planted there is never imported by the wizard (for example `import gabbe`)."""
    here = Path.cwd().resolve()
    sys.path[:] = [p for p in sys.path if p not in ("", ".") and Path(p).resolve() != here]


def _run():
    """Run the wizard; a filesystem error (for example a dangling link where a folder
    is needed) ends it with one line instead of a traceback."""
    try:
        main()
    except OSError as exc:
        print(f"\n{RED}Error: {exc}{NC}", file=sys.stderr)
        print(
            "The install stopped here. What was written so far is in .gabbe/manifest.json;"
            " remove what blocks the path and run the installer again, or reverse it with"
            " the uninstall command.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    _drop_project_from_import_path()
    _run()
