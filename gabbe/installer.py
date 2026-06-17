# SPDX-License-Identifier: Apache-2.0
"""Reversible, manifest-backed install / update / uninstall (Track D).

Every install records exactly what it created in `.gabbe/manifest.json` so the
operation is fully reversible and isolated:
  * install copies a kit `source` tree into a `target`, wires the selected agents,
    backs up any pre-existing user file to `<file>.bak`, and records every path;
  * uninstall reads the manifest and removes EXACTLY what was created (restoring
    `.bak` backups, pruning now-empty dirs) — never touching unrelated files;
  * update refreshes kit files additively and prunes orphaned ones;
  * remove_agents deletes only one agent's wiring.

Isolation invariant: nothing is ever written outside `target`. Idempotent: a
re-install/uninstall is safe to run twice.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any

from . import __version__

MANIFEST_SCHEMA_VERSION = 1
_MANIFEST_REL = ".gabbe/manifest.json"
# User/preserve files an update or uninstall must never clobber or delete.
_PRESERVE = {"CONSTITUTION.md", "policies.yml"}
# Agent slugs are used to build file paths, so they must be strictly bounded
# (no separators / traversal). Enforces the isolation invariant.
_AGENT_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


def _empty_manifest() -> dict[str, Any]:
    return {"schema_version": MANIFEST_SCHEMA_VERSION, "entries": [], "agents": []}


def _validate_agents(agents: list[str]) -> None:
    for agent in agents:
        if not _AGENT_RE.match(agent):
            raise ValueError(f"invalid agent name (must match {_AGENT_RE.pattern}): {agent!r}")


def _resolve_within(target: Path, rel: str) -> Path:
    """Resolve `rel` under `target`, refusing any path that escapes the target.

    Hard guarantee for the isolation invariant: a tampered/malicious manifest path
    (e.g. '../../etc/x') can never make uninstall touch a file outside the target.
    """
    base = target.resolve()
    p = (base / rel).resolve()
    if p != base and base not in p.parents:
        raise ValueError(f"refusing path outside target: {rel!r}")
    return p


def manifest_path(target: Path) -> Path:
    return target / _MANIFEST_REL


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    mp.parent.mkdir(parents=True, exist_ok=True)
    mp.write_text(json.dumps(manifest, indent=2, sort_keys=True))


def _iter_source_files(source: Path):
    for p in sorted(source.rglob("*")):
        if p.is_file():
            yield p, p.relative_to(source)


def install_kit(
    target: Path,
    source: Path,
    agents: list[str],
    *,
    timestamp: str = "",
) -> dict[str, Any]:
    """Install the kit at `source` into `target` for `agents`, recording a manifest.

    Returns the manifest. Idempotent (re-install replaces files without duplicate
    manifest entries). Backs up pre-existing non-kit files to `<file>.bak`.
    """
    _validate_agents(agents)
    target = target.resolve()
    entries: list[dict[str, Any]] = []

    # 1. Shared kit files (copied once under the target).
    for src, rel in _iter_source_files(source):
        dest = target / "agents" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        backup_of = None
        if dest.exists() and not _is_kit_managed(target, dest):
            backup = dest.with_suffix(dest.suffix + ".bak")
            shutil.copy2(dest, backup)
            backup_of = str(backup.relative_to(target))
        shutil.copy2(src, dest)
        entries.append(
            {
                "path": str(dest.relative_to(target)),
                "kind": "copy",
                "agent": "shared",
                "hash": _sha256(dest),
                "backup_of": backup_of,
            }
        )

    # 2. Per-agent wiring stubs (one small file per selected agent).
    for agent in agents:
        stub = target / ".gabbe-agents" / f"{agent}.md"
        stub.parent.mkdir(parents=True, exist_ok=True)
        stub.write_text(f"# GABBE wiring for {agent}\nKit: agents/\n")
        entries.append(
            {
                "path": str(stub.relative_to(target)),
                "kind": "skill-emit",
                "agent": agent,
                "hash": _sha256(stub),
                "backup_of": None,
            }
        )

    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "installer_version": __version__,
        "timestamp": timestamp,
        "agents": sorted(set(agents)),
        "entries": entries,
    }
    _write_manifest(target, manifest)
    return manifest


def _is_kit_managed(target: Path, path: Path) -> bool:
    """True if `path` is already tracked by the manifest (so it's ours to replace)."""
    rel = str(path.relative_to(target))
    return any(e["path"] == rel for e in read_manifest(target).get("entries", []))


def update_kit(
    target: Path, source: Path, agents: list[str] | None = None, *, timestamp: str = ""
) -> dict[str, Any]:
    """Additively refresh kit files; prune orphaned emitted files; preserve user files."""
    target = target.resolve()
    prior = read_manifest(target)
    keep_agents = agents if agents is not None else prior.get("agents", [])
    prior_paths = {e["path"] for e in prior.get("entries", [])}
    manifest = install_kit(target, source, keep_agents, timestamp=timestamp)
    # Prune orphans: previously-managed paths no longer emitted (and not preserve files).
    new_paths = {e["path"] for e in manifest["entries"]}
    for orphan in sorted(prior_paths - new_paths):
        if Path(orphan).name in _PRESERVE:
            continue
        fp = target / orphan
        if fp.exists():
            fp.unlink()
    return manifest


def uninstall(
    target: Path,
    *,
    agents: list[str] | None = None,
    dry_run: bool = False,
    purge: bool = False,
) -> list[str]:
    """Remove exactly what was installed (restoring `.bak`). Returns removed paths.

    With `agents`, removes only those agents' wiring. `dry_run` changes nothing.
    `purge` also removes the `.gabbe/` manifest dir and the shared `agents/` kit.
    """
    target = target.resolve()
    manifest = read_manifest(target)
    removed: list[str] = []
    kept_entries: list[dict[str, Any]] = []

    for entry in manifest.get("entries", []):
        # Containment guard: never act on a path that escapes the target, even if
        # the manifest was tampered with. A bad entry is kept (skipped), not crashed.
        try:
            path = _resolve_within(target, entry["path"])
        except (ValueError, KeyError, TypeError):
            kept_entries.append(entry)
            continue
        scope_match = agents is None or entry.get("agent") in agents
        is_shared = entry.get("agent") == "shared"
        # When scoping to specific agents, never remove shared kit files.
        if not scope_match or (agents is not None and is_shared):
            kept_entries.append(entry)
            continue
        if Path(entry["path"]).name in _PRESERVE:
            kept_entries.append(entry)
            continue
        removed.append(entry["path"])
        if dry_run:
            continue
        if path.exists() or path.is_symlink():
            path.unlink()
        # Restore a backup if this install shadowed a user file (also containment-checked).
        if entry.get("backup_of"):
            try:
                backup = _resolve_within(target, entry["backup_of"])
            except ValueError:
                continue
            if backup.exists():
                shutil.move(str(backup), str(path))

    if dry_run:
        return removed

    # Rewrite the manifest with whatever we kept (or drop it entirely on full uninstall).
    if kept_entries and agents is not None:
        manifest["entries"] = kept_entries
        manifest["agents"] = sorted(a for a in manifest.get("agents", []) if a not in agents)
        _write_manifest(target, manifest)
    else:
        mp = manifest_path(target)
        if mp.exists():
            mp.unlink()

    _prune_empty_dirs(target, purge=purge)
    return removed


def remove_agents(target: Path, agents: list[str]) -> list[str]:
    """Deselect agents: remove only their wiring, leaving everything else intact."""
    return uninstall(target, agents=agents, dry_run=False)


def _prune_empty_dirs(target: Path, *, purge: bool) -> None:
    for d in (target / ".gabbe-agents", target / ".gabbe"):
        if d.exists() and not any(d.iterdir()):
            d.rmdir()
    if purge:
        for d in (target / "agents", target / ".gabbe"):
            if d.exists():
                shutil.rmtree(d, ignore_errors=True)
