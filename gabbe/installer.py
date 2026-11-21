# SPDX-License-Identifier: Apache-2.0
"""Reversible, manifest-backed install / update / uninstall (Track D).

Every install records exactly what it created in `.gabbe/manifest.json` so the
operation is fully reversible and isolated:
  * install copies a kit `source` tree into a `target`, wires the selected agents,
    backs up any pre-existing user file before replacing it, and records every path;
  * uninstall reads the manifest and removes EXACTLY what was recorded (restoring
    linked backups, pruning now-empty dirs) — never touching unrelated files;
  * update refreshes kit files, keeps what the user changed, merges the earlier
    record instead of replacing it, and prunes only unmodified orphaned kit files;
  * remove_agents deletes only one agent's wiring.

Backup rule, shared by every code path here (and mirrored by `scripts/init.py`
and `bin/install.js`): back up first, and never overwrite an existing backup.

Isolation invariant: nothing is ever written outside `target`. Idempotent: a
re-install/uninstall is safe to run twice.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any, Iterator

from . import __version__

MANIFEST_SCHEMA_VERSION = 1
_MANIFEST_REL = ".gabbe/manifest.json"
# User-owned files: an update keeps them once the user has changed them, and an
# uninstall never deletes them. Same set as `scripts/init.py` and `bin/install.js`.
_PRESERVE = {"AGENTS.md", "CONSTITUTION.md", "TASKS.md", "policies.yml", "config.json"}
# Folders whose contents belong to the user once they exist.
_USER_DIRS = {"memory", "project"}
_BACKUP_SUFFIX = ".gabbe-bak"
# Every skill file the installers emit carries this line; it identifies generated
# files inside a directory recorded as one `tree` entry by releases before 1.1.4.
_GENERATED_MARKER = b"gabbe-schema-version:"
# The pointer block the installers append to a user's own instruction file. Matched
# on bytes so that the user's encoding and line endings are never touched.
_BLOCK_RE = re.compile(rb"<!-- GABBE-KIT:BEGIN.*?<!-- GABBE-KIT:END -->(\r?\n)?", re.DOTALL)
# Agent slugs are used to build file paths, so they must be strictly bounded
# (no separators / traversal). Enforces the isolation invariant.
_AGENT_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


# Short names accepted by `--agents`, mapped to the agent's full name. Same table as
# AGENT_ALIASES in bin/install.js (a test compares the two so they cannot drift).
AGENT_ALIASES: dict[str, str] = {
    "claude": "Claude Code",
    "claude-code": "Claude Code",
    "cursor": "Cursor",
    "windsurf": "Windsurf",
    "cline": "Cline",
    "aider": "Aider",
    "devin": "Devin / Cognition",
    "cognition": "Devin / Cognition",
    "gemini": "Gemini",
    "antigravity": "Antigravity",
    "opencode": "OpenCode",
    "zed": "Zed",
    "continue": "Continue",
    "roo": "Roo Code",
    "roo-code": "Roo Code",
    "kilo": "Kilo Code",
    "kilo-code": "Kilo Code",
    "codex": "OpenAI / Codex",
    "openai": "OpenAI / Codex",
    "copilot": "GitHub Copilot",
    "github-copilot": "GitHub Copilot",
    "vscode": "VS Code",
    "vs-code": "VS Code",
}


def agent_slug(name: str) -> str:
    """The slug an agent is recorded under: a known short name ("claude") maps through
    its full name ("Claude Code") to "claude-code"; anything else is returned as given.
    Gives the same result as `agentSlugsFromArgs` in bin/install.js.
    """
    full = AGENT_ALIASES.get(name.lower())
    if full is None:
        return name
    slug = "".join(c if (c.isalnum() or c in "-_") else "-" for c in full.lower())
    return slug.strip("-") or "shared"


def _empty_manifest() -> dict[str, Any]:
    return {"schema_version": MANIFEST_SCHEMA_VERSION, "entries": [], "agents": []}


def _validate_agents(agents: list[str]) -> None:
    for agent in agents:
        if not _AGENT_RE.match(agent):
            raise ValueError(f"invalid agent name (must match {_AGENT_RE.pattern}): {agent!r}")


def _check_recorded_path(rel: str) -> None:
    """Refuse a recorded path that is not a plain relative path: empty, `.`, absolute,
    or with a `..` part. Raises ValueError."""
    if not isinstance(rel, str) or rel in ("", "."):
        raise ValueError(f"refusing an empty or non-text recorded path: {rel!r}")
    if "\x00" in rel or Path(rel).is_absolute() or rel.startswith(("/", "\\")):
        raise ValueError(f"refusing an absolute recorded path: {rel!r}")
    parts = rel.replace("\\", "/").split("/")
    if ".." in parts or all(p in ("", ".") for p in parts):
        raise ValueError(f"refusing a recorded path that climbs out of the target: {rel!r}")


def _resolve_within(target: Path, rel: str) -> Path:
    """Resolve `rel` under `target`, refusing any path that escapes the target.

    Hard guarantee for the isolation invariant: a tampered/malicious manifest path
    ('../../etc/x', 'x/..', an absolute path) can never make uninstall or update touch a
    file outside the target. Every record field that becomes a path goes through here.

    The leaf is NOT dereferenced: we resolve the PARENT directory and re-attach the
    final component, so a symlink entry (e.g. a wired `.cursorrules`) is acted on
    directly — `.resolve()` on the full path would follow the link to its target
    and the symlink itself would never be removed.
    """
    _check_recorded_path(rel)
    base = target.resolve()
    raw = base / rel
    parent = raw.parent.resolve()
    if parent != base and base not in parent.parents:
        raise ValueError(f"refusing path outside target: {rel!r}")
    result = parent / raw.name
    if result == base or base not in result.parents:
        raise ValueError(f"refusing path outside target: {rel!r}")
    return result


def _skip_message(what: str, err: Exception) -> None:
    import sys

    print(f"warning: skipped {what}: {err}", file=sys.stderr)


def manifest_path(target: Path) -> Path:
    return target / _MANIFEST_REL


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_problem(target: Path) -> str | None:
    """Why the install record cannot be used, or None when it is absent or valid.

    A damaged record must stop `update` and `uninstall`: treating it as empty would
    leave every installed file behind and then delete the only record of them.
    """
    mp = manifest_path(target)
    if mp.parent.is_symlink():
        return f"{mp.parent} is a symbolic link; the install record must be a real folder"
    if mp.is_symlink():
        return f"{mp} is a symbolic link; the install record must be a real file"
    if not mp.exists():
        return None
    try:
        m = json.loads(mp.read_text())
    except (ValueError, OSError) as e:
        return f"{mp} cannot be read as JSON ({e})"
    if not isinstance(m, dict) or not isinstance(m.get("entries"), list):
        return f"{mp} is not an install record (no list of entries)"
    return None


def read_manifest(target: Path) -> dict[str, Any]:
    mp = manifest_path(target)
    if not mp.exists():
        return _empty_manifest()
    try:
        m = json.loads(mp.read_text())
    except (ValueError, OSError):
        return _empty_manifest()
    # Defensive: a corrupt manifest must degrade gracefully, not crash callers.
    if not isinstance(m, dict) or not isinstance(m.get("entries"), list):
        return _empty_manifest()
    m.setdefault("agents", [])
    return m


def _write_manifest(target: Path, manifest: dict[str, Any]) -> None:
    mp = manifest_path(target)
    if mp.parent.is_symlink():
        raise ValueError(f"{mp.parent} is a symbolic link; refusing to write the record there")
    if mp.is_symlink():
        raise ValueError(f"{mp} is a symbolic link; refusing to write the record through it")
    mp.parent.mkdir(parents=True, exist_ok=True)
    tmp = mp.with_name(f"{mp.name}.tmp-{os.getpid()}")
    try:
        tmp.write_text(json.dumps(manifest, indent=2, sort_keys=True))
        os.replace(tmp, mp)
    finally:
        tmp.unlink(missing_ok=True)


def _iter_source_files(source: Path) -> Iterator[tuple[Path, Path]]:
    for p in sorted(source.rglob("*")):
        if p.is_file():
            yield p, p.relative_to(source)


def _entries_by_path(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        e["path"]: e
        for e in manifest.get("entries", [])
        if isinstance(e, dict) and isinstance(e.get("path"), str)
    }


def free_backup_path(path: Path) -> Path:
    """First unused backup name for `path`: `<name>.gabbe-bak`, then `.gabbe-bak.1`, ..."""
    candidate = Path(str(path) + _BACKUP_SUFFIX)
    n = 0
    while candidate.exists() or candidate.is_symlink():
        n += 1
        candidate = Path(f"{path}{_BACKUP_SUFFIX}.{n}")
    return candidate


def backup_file(path: Path) -> Path:
    """Copy `path` to a new backup next to it. An existing backup is never overwritten."""
    backup = free_backup_path(path)
    shutil.copy2(path, backup)
    return backup


def _is_user_owned(rel: Path) -> bool:
    return rel.name in _PRESERVE or bool(_USER_DIRS.intersection(rel.parts[:-1]))


def _refresh_file(
    src: Path, dest: Path, rel: Path, tracked: dict[str, Any] | None, target: Path
) -> dict[str, Any] | None:
    """Bring one kit file up to date without losing anything the user wrote.

    Returns the manifest entry for `dest`, or None when the file is the user's own
    (never recorded, so never removed). Cases, with `tracked` = the earlier record:
      * a symbolic link              -> the user's: never written through;
      * no file yet                  -> copy;
      * same bytes, never recorded   -> it was there before us: left unrecorded;
      * user-owned and changed       -> keep the user's file;
      * recorded and unchanged       -> replace, no backup;
      * anything else (changed)      -> back up to a new name, then replace. The
        backup is linked for restore only when the file was there before any record.
    """
    if dest.is_symlink() or dest.is_dir():
        return None  # a link or a folder at a kit file's path is the user's
    backup_of = tracked.get("backup_of") if tracked else None
    if dest.exists():
        current = _sha256(dest)
        if tracked is None and current == _sha256(src):
            return None
        changed = tracked is None or tracked.get("hash") != current
        if current != _sha256(src) and changed:
            if _is_user_owned(rel):
                return tracked
            backup = backup_file(dest)
            if tracked is None:
                backup_of = str(backup.relative_to(target))
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return {
        "path": str(dest.relative_to(target)),
        "kind": "copy",
        "agent": "shared",
        "hash": _sha256(dest),
        "backup_of": backup_of,
    }


_NEW_SUFFIX = ".gabbe-new"


def _new_version_entry(
    src: Path, dest: Path, rel: Path, tracked: dict[str, Any] | None, new_tracked: Any, target: Path
) -> dict[str, Any] | None:
    """After `update` kept a preserved file the user changed: write the kit's version next
    to it as `<name>.gabbe-new` and return that file's record entry (None: nothing written).

    Rules (the same as `offerNewVersion` in bin/install.js): only a preserved file (not under
    `memory/` or `project/`) that the earlier record names and whose bytes changed since;
    nothing when the kit's file equals it or a link is on the `.gabbe-new` path; an existing
    `.gabbe-new` the record does not own, or that changed, is left alone with one message.
    """
    if rel.name not in _PRESERVE or _USER_DIRS.intersection(rel.parts[:-1]) or tracked is None:
        return None
    if dest.is_symlink() or not dest.is_file():
        return None
    if _sha256(dest) == _sha256(src) or tracked.get("hash") == _sha256(dest):
        return None
    new = dest.with_name(dest.name + _NEW_SUFFIX)
    mine, theirs = str(dest.relative_to(target)), str(new.relative_to(target))
    if new.is_symlink() or new.is_dir():
        return None
    owned = isinstance(new_tracked, dict) and new_tracked.get("hash") == (
        _sha256(new) if new.is_file() else None
    )
    if new.exists() and not owned:
        print(f"kept your {mine}; {theirs} is not ours or was changed: left alone")
        return new_tracked if isinstance(new_tracked, dict) else None
    if not new.exists() or _sha256(new) != _sha256(src):
        shutil.copy2(src, new)
    print(f"kept your {mine}; the kit's new version is {theirs} (compare, merge, then delete it)")
    return {
        "path": theirs,
        "kind": "copy",
        "agent": "shared",
        "hash": _sha256(new),
        "backup_of": None,
    }


def _write_agent_stubs(
    target: Path, agents: list[str], prior: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Per-agent wiring stubs (one small file per selected agent).

    A file already at a stub's path that no install recorded is the user's: it is
    backed up first (and linked for restore); a symbolic link there is left alone.
    """
    entries = []
    for agent in agents:
        stub = target / ".gabbe-agents" / f"{agent}.md"
        rel = str(stub.relative_to(target))
        text = f"# GABBE wiring for {agent}\nKit: agents/\n"
        tracked = prior.get(rel)
        if stub.is_symlink() or stub.parent.is_symlink():
            continue
        backup_of = tracked.get("backup_of") if tracked else None
        if stub.exists() and tracked is None and stub.read_bytes() != text.encode():
            backup_of = str(backup_file(stub).relative_to(target))
        stub.parent.mkdir(parents=True, exist_ok=True)
        stub.write_text(text)
        entries.append(
            {
                "path": rel,
                "kind": "skill-emit",
                "agent": agent,
                "hash": _sha256(stub),
                "backup_of": backup_of,
            }
        )
    return entries


def _kit_dest(target: Path, rel: Path) -> Path:
    """Where the kit file `rel` goes under `target`. Refuses a destination that a
    directory link takes outside the target (the isolation invariant)."""
    try:
        _resolve_within(target, str(Path("agents") / rel))
    except ValueError:
        raise ValueError(
            f"{target / 'agents' / rel.parent} leads outside {target} through a link; "
            "refusing to write there. Point --dir at the folder that really holds the kit."
        ) from None
    return target / "agents" / rel


def install_kit(
    target: Path,
    source: Path,
    agents: list[str],
    *,
    timestamp: str = "",
) -> dict[str, Any]:
    """Install the kit at `source` into `target` for `agents`, recording a manifest.

    Returns the manifest. Idempotent (re-install replaces files without duplicate
    manifest entries). A pre-existing file that differs is backed up first; the
    user-owned files (`_PRESERVE`, `memory/`, `project/`) are kept as they are.
    """
    _validate_agents(agents)
    target = target.resolve()
    _require_usable_record(target)
    prior = _safe_entries(target, _entries_by_path(read_manifest(target)))
    entries: list[dict[str, Any]] = []

    # 1. Shared kit files (copied once under the target).
    for src, rel in _iter_source_files(source):
        dest = _kit_dest(target, rel)
        entry = _refresh_file(src, dest, rel, prior.get(str(dest.relative_to(target))), target)
        if entry is not None:
            entries.append(entry)

    # 2. Per-agent wiring stubs.
    entries.extend(_write_agent_stubs(target, agents, prior))

    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "installer_version": __version__,
        "timestamp": timestamp,
        "agents": sorted(set(agents)),
        "entries": entries,
    }
    _write_manifest(target, manifest)
    return manifest


def _require_usable_record(target: Path) -> None:
    problem = manifest_problem(target)
    if problem:
        raise ValueError(f"The install record is damaged: {problem}. Nothing was changed.")


def _is_kit_managed(target: Path, path: Path) -> bool:
    """True if `path` is already tracked by the manifest (so it's ours to replace)."""
    rel = str(path.relative_to(target))
    return any(e["path"] == rel for e in read_manifest(target).get("entries", []))


def _safe_entries(target: Path, entries: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """The record entries whose path (and `backup_of`) stay inside the target. Any other
    entry is dropped from the new record with one message; nothing on disk is touched."""
    safe: dict[str, dict[str, Any]] = {}
    for key, entry in entries.items():
        try:
            _resolve_within(target, key)
        except ValueError as e:
            _skip_message(f"record entry {key!r}", e)
            continue
        safe[key] = _safe_backup_of(target, entry)
    return safe


def _safe_backup_of(target: Path, entry: dict[str, Any]) -> dict[str, Any]:
    """`entry`, with a `backup_of` that leaves the target replaced by None (with a message)."""
    backup = entry.get("backup_of")
    if not backup:
        return entry
    try:
        _resolve_within(target, backup)
    except ValueError as e:
        _skip_message(f"backup_of of {entry['path']!r}", e)
        return {**entry, "backup_of": None}
    return entry


def _is_unmodified_kit_copy(target: Path, entry: dict[str, Any]) -> bool:
    """True for a recorded kit file under `agents/` that still has its recorded bytes."""
    if entry.get("kind") != "copy" or entry.get("agent") != "shared":
        return False
    rel = Path(entry["path"])
    if rel.parts[:1] != ("agents",) or _is_user_owned(rel):
        return False
    try:
        path = _resolve_within(target, entry["path"])
    except ValueError:
        return False
    return path.is_file() and not path.is_symlink() and _sha256(path) == entry.get("hash")


def _update_one(
    src: Path, rel: Path, target: Path, merged: dict[str, dict[str, Any]], emitted: set[str]
) -> None:
    """Refresh one kit file into `merged` (the record being built); note what was emitted."""
    dest = _kit_dest(target, rel)
    key = str(dest.relative_to(target))
    earlier = merged.get(key)
    entry = _refresh_file(src, dest, rel, earlier, target)
    emitted.add(key)
    if entry is not None:
        merged[key] = entry
    elif dest.is_symlink() or dest.is_dir():
        merged.pop(key, None)  # the user put a link or a folder here: no longer ours
    new_key = key + _NEW_SUFFIX
    new_entry = _new_version_entry(src, dest, rel, earlier, merged.get(new_key), target)
    if new_entry is not None:
        merged[new_key] = new_entry
        emitted.add(new_key)


def update_kit(
    target: Path, source: Path, agents: list[str] | None = None, *, timestamp: str = ""
) -> dict[str, Any]:
    """Refresh kit files and keep everything else the earlier install recorded.

    The earlier record is merged, not replaced: wiring links, generated skill folders
    and anything else an installer recorded stay in the manifest and on disk. A kit
    file that is no longer shipped is removed only when the user never changed it.
    The manifest is written last, so a failure part-way leaves the old record intact.
    """
    target = target.resolve()
    _require_usable_record(target)
    prior = read_manifest(target)
    merged = _safe_entries(target, _entries_by_path(prior))
    stubbed = {e.get("agent") for e in merged.values() if e.get("kind") == "skill-emit"}
    stub_agents = agents if agents is not None else sorted(a for a in stubbed if a)
    _validate_agents(stub_agents)

    emitted: set[str] = set()
    for src, rel in _iter_source_files(source):
        _update_one(src, rel, target, merged, emitted)
    for entry in _write_agent_stubs(target, stub_agents, merged):
        merged[entry["path"]] = entry
        emitted.add(entry["path"])

    for key in sorted(set(merged) - emitted):
        if _is_unmodified_kit_copy(target, merged[key]):
            _resolve_within(target, key).unlink()
            del merged[key]

    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "installer_version": __version__,
        "timestamp": timestamp,
        "agents": sorted(set(prior.get("agents", [])) | set(stub_agents)),
        "entries": sorted(merged.values(), key=lambda e: e["path"]),
    }
    _write_manifest(target, manifest)
    return manifest


def _generated_files(tree: Path) -> list[Path]:
    """Files inside `tree` that an installer generated (they carry the kit's marker)."""
    found = []
    for p in sorted(tree.rglob("*")):
        if p.is_file() and not p.is_symlink():
            try:
                with open(p, "rb") as f:
                    is_generated = _GENERATED_MARKER in f.read(4096)
            except OSError:
                is_generated = False
            if is_generated:
                found.append(p)
    return found


def _is_modified_copy(entry: dict[str, Any], path: Path) -> bool:
    if entry.get("kind") != "copy" or not entry.get("hash"):
        return False
    if not path.is_file() or path.is_symlink():
        return False
    try:
        return bool(_sha256(path) != entry["hash"])
    except OSError:
        return False


def strip_pointer_block(data: bytes) -> bytes:
    """`data` without the kit's pointer block and the blank line put before it.

    Works on bytes: the user's encoding and line endings stay exactly as they are.
    """
    m = _BLOCK_RE.search(data)
    if not m:
        return data
    before = data[: m.start()]
    for blank in (b"\r\n\r\n", b"\n\n"):
        if before.endswith(blank):
            before = before[: len(before) - len(blank) // 2]  # drop one line end
            break
    return before + data[m.end() :]


def _remove_block(path: Path, backup: Path | None) -> None:
    """Take the kit's pointer block out of a user's file; restore the exact original
    bytes from `backup` when nothing else in the file changed since install."""
    if not path.is_file() or path.is_symlink():
        return
    stripped = strip_pointer_block(path.read_bytes())
    if backup is not None and backup.is_file():
        if backup.read_bytes().rstrip(b"\r\n") == stripped.rstrip(b"\r\n"):
            shutil.move(str(backup), str(path))
            return
    path.write_bytes(stripped)


def _same_hook_entry(a: Any, b: Any) -> bool:
    """Two hook entries are the same when event-level matcher and command strings are equal."""

    def commands(item: Any) -> list[Any]:
        if isinstance(item, dict) and isinstance(item.get("hooks"), list):
            return [h.get("command") if isinstance(h, dict) else None for h in item["hooks"]]
        return [item.get("command") if isinstance(item, dict) else None]

    def matcher(item: Any) -> Any:
        return item.get("matcher") if isinstance(item, dict) else None

    return bool(matcher(a) == matcher(b) and commands(a) == commands(b))


def remove_hook_fragment(
    doc: dict[str, Any], fragment: dict[str, Any], *, added_version: bool = False
) -> dict[str, Any]:
    """`doc` without exactly the entries of `fragment` (same event, matcher and command).

    Same rule as `removeFragment` in agents/hooks/merge-hooks.js: an event list or `hooks`
    left empty is dropped; `version` goes only when `added_version` says the install added it.
    Raises ValueError when `doc` or its `hooks` has an unexpected shape.
    """
    if not isinstance(doc, dict) or not isinstance(doc.get("hooks", {}), dict):
        raise ValueError("the settings file has an unexpected shape")
    cleaned = json.loads(json.dumps(doc))
    hooks = cleaned.get("hooks")
    if hooks is not None:
        for event, items in fragment["hooks"].items():
            if event not in hooks:
                continue
            if not isinstance(hooks[event], list):
                raise ValueError(f"hooks.{event} is not a list")
            kept = [x for x in hooks[event] if not any(_same_hook_entry(x, i) for i in items)]
            if kept:
                hooks[event] = kept
            else:
                del hooks[event]
        if not hooks:
            del cleaned["hooks"]
    if added_version and cleaned.get("version") == fragment.get("version"):
        del cleaned["version"]
    return cleaned  # type: ignore[no-any-return]


def _remove_hook_merge(
    target: Path, entry: dict[str, Any], path: Path, backup: Path | None
) -> None:
    """Undo a `hook-merge` entry: take the recorded fragment's entries out of the user's
    settings file. A file the installer created and nothing else uses is removed. When the
    file minus our entries equals the backup as JSON, the backup's exact bytes come back;
    otherwise the cleaned JSON is written and the backup stays."""
    import sys

    if not path.is_file() or path.is_symlink():
        return
    fragment = entry.get("fragment_doc")
    try:
        if not isinstance(fragment, dict) or not isinstance(fragment.get("hooks"), dict):
            fragment = json.loads(
                _resolve_within(target, entry["fragment"]).read_text(encoding="utf-8")
            )
        cleaned = remove_hook_fragment(
            json.loads(path.read_text(encoding="utf-8")),
            fragment,
            added_version=entry.get("added_version") is True,
        )
    except (ValueError, KeyError, TypeError, OSError, AttributeError) as e:
        print(
            f"warning: {entry['path']} was left as it is ({e}); "
            "remove the GABBE hook entries by hand",
            file=sys.stderr,
        )
        return
    if entry.get("created") is True and not cleaned:
        path.unlink()
        return
    if backup is not None and backup.is_file() and not backup.is_symlink():
        try:
            if json.loads(backup.read_text(encoding="utf-8")) == cleaned:
                shutil.move(str(backup), str(path))
                return
        except (ValueError, OSError):
            pass  # the backup is not JSON: keep it and write the cleaned file
    path.write_text(json.dumps(cleaned, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _remove_entry(target: Path, entry: dict[str, Any], path: Path) -> list[str]:
    """Remove one recorded artifact. Returns files kept in place as backups."""
    preserved: list[str] = []
    kind = entry.get("kind")
    backup: Path | None = None
    if entry.get("backup_of"):
        try:
            backup = _resolve_within(target, entry["backup_of"])
        except ValueError:
            backup = None
    if kind == "block":
        _remove_block(path, backup)
        return preserved
    if kind == "hook-merge":
        _remove_hook_merge(target, entry, path, backup)
        return preserved
    if kind == "tree":
        # Recorded as one directory by releases before 1.1.4. The directory may hold
        # the user's own files, so remove only the files an installer generated.
        if path.is_dir() and not path.is_symlink():
            for generated in _generated_files(path):
                generated.unlink()
    else:
        if _is_modified_copy(entry, path):
            # The user edited an installed file: keep their text as a backup.
            backup_file(path)
            preserved.append(entry["path"])
        if path.exists() or path.is_symlink():
            path.unlink()
    # Restore a backup if this install shadowed a user file.
    if backup is not None and backup.exists() and not path.exists():
        shutil.move(str(backup), str(path))
    return preserved


def _removal_plan(
    target: Path, manifest: dict[str, Any], agents: list[str] | None
) -> tuple[list[tuple[dict[str, Any], Path]], list[dict[str, Any]]]:
    """Split the manifest into (entries to remove with their paths, entries to keep).

    Kept: paths that escape the target (tampered manifest); entries outside the
    requested agents; shared kit files when only some agents are removed; user-owned
    files (`_PRESERVE`, `memory/`, `project/`) unless the file still has exactly the
    bytes the install wrote (then it is the kit's untouched copy and is removed).
    """
    to_remove: list[tuple[dict[str, Any], Path]] = []
    kept: list[dict[str, Any]] = []
    for entry in manifest.get("entries", []):
        try:
            path = _resolve_within(target, entry["path"])
        except (ValueError, KeyError, TypeError) as e:
            _skip_message(
                (
                    f"record entry {entry.get('path')!r}"
                    if isinstance(entry, dict)
                    else "a record entry"
                ),
                e,
            )
            kept.append(entry)
            continue
        in_scope = agents is None or (
            entry.get("agent") in agents and entry.get("agent") != "shared"
        )
        user_owned = entry.get("kind") == "copy" and _is_user_owned(Path(entry["path"]))
        if user_owned and entry.get("hash"):
            user_owned = _is_modified_copy(entry, path)
        if not user_owned:
            user_owned = _is_not_what_was_recorded(entry, path)
        if in_scope and not user_owned:
            to_remove.append((entry, path))
        else:
            kept.append(entry)
    return to_remove, kept


def _is_not_what_was_recorded(entry: dict[str, Any], path: Path) -> bool:
    """True when the user replaced a recorded file with a link or a folder, or a
    recorded link with a file or folder of their own. It is theirs now: kept."""
    kind = entry.get("kind")
    if kind in ("tree", "block") or not (path.exists() or path.is_symlink()):
        return False
    if kind == "symlink":
        return not path.is_symlink()
    return path.is_symlink() or path.is_dir()


def _removed_paths(target: Path, to_remove: list[tuple[dict[str, Any], Path]]) -> list[str]:
    """The paths an uninstall removes or changes, as the manifest names them."""
    paths: list[str] = []
    for entry, path in to_remove:
        if entry.get("kind") == "tree" and path.is_dir() and not path.is_symlink():
            paths.extend(str(p.relative_to(target)) for p in _generated_files(path))
        else:
            paths.append(entry["path"])
    return paths


def uninstall(
    target: Path,
    *,
    agents: list[str] | None = None,
    dry_run: bool = False,
    purge: bool = False,
) -> list[str]:
    """Remove exactly what was recorded (restoring linked backups). Returns removed paths.

    With `agents`, removes only those agents' wiring. `dry_run` changes nothing and
    returns the same list a real run would. `purge` also removes empty directories
    left under `agents/`. Nothing that was not recorded is ever deleted, and a
    user-owned file (`_PRESERVE`, `memory/`, `project/`) the user changed stays in
    place: backups, memory files and the user's own files stay.
    """
    target = target.resolve()
    if manifest_problem(target):
        return []  # a damaged record is never acted on and never deleted
    manifest = read_manifest(target)
    to_remove, kept_entries = _removal_plan(target, manifest, agents)
    removed = _removed_paths(target, to_remove)
    if dry_run:
        return removed

    modified: list[str] = []  # user-edited files preserved as a backup on removal
    for entry, path in to_remove:
        modified.extend(_remove_entry(target, entry, path))

    # Rewrite the manifest with whatever we kept (or drop it entirely on full uninstall).
    if kept_entries and agents is not None:
        manifest["entries"] = kept_entries
        manifest["agents"] = sorted(a for a in manifest.get("agents", []) if a not in agents)
        _write_manifest(target, manifest)
    else:
        mp = manifest_path(target)
        if mp.exists():
            mp.unlink()

    if modified:
        import sys

        print(
            "warning: preserved your edits to "
            f"{len(modified)} modified file(s) as <name>.gabbe-bak: " + ", ".join(sorted(modified)),
            file=sys.stderr,
        )
    _prune_empty_ancestors(target, removed)
    _prune_empty_dirs(target, purge=purge)
    return removed


def _prune_empty_ancestors(target: Path, removed: list[str]) -> None:
    """Remove directories that became empty once their entries were removed.

    Walks each removed path's ancestor chain bottom-up and rmdir()s any directory
    that is now empty, stopping at `target`. Leaves no empty wiring dirs (e.g.
    `.claude/`, `.cursor/`) behind. Bounded to within `target`.
    """
    base = target.resolve()
    for rel in removed:
        if rel.startswith(".git/"):
            continue  # git's own folders are never pruned
        d = (base / rel).parent
        while d != base:
            try:
                d.relative_to(base)  # stay within target
            except ValueError:
                break
            try:
                if d.is_dir() and not d.is_symlink() and not any(d.iterdir()):
                    d.rmdir()
                else:
                    break
            except OSError:
                break
            d = d.parent


def remove_agents(target: Path, agents: list[str]) -> list[str]:
    """Deselect agents: remove only their wiring, leaving everything else intact."""
    return uninstall(target, agents=agents, dry_run=False)


def remaining_kit_files(target: Path) -> list[str]:
    """Files still under `agents/` after an uninstall: the user's own files, files
    the user changed, memory files and backups. Uninstall never deletes these."""
    kit = target / "agents"
    if not kit.is_dir():
        return []
    return sorted(str(p.relative_to(target)) for p in kit.rglob("*") if p.is_file())


def _prune_empty_dirs(target: Path, *, purge: bool) -> None:
    """Remove the installer's own directories once empty, and the empty directories
    left under `agents/`. A directory that holds a file is never removed. (`purge` is
    accepted for compatibility: since 1.1.4 it changes nothing here.)"""
    for d in (target / ".gabbe-agents", target / ".gabbe"):
        if d.is_dir() and not d.is_symlink() and not any(d.iterdir()):
            d.rmdir()
    kit = target / "agents"
    if kit.is_dir() and not kit.is_symlink():
        for d in sorted((p for p in kit.rglob("*") if p.is_dir()), reverse=True):
            if not d.is_symlink() and not any(d.iterdir()):
                d.rmdir()
        if not any(kit.iterdir()):
            kit.rmdir()
