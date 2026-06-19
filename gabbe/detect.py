# SPDX-License-Identifier: Apache-2.0
"""Brownfield project detection (Workstream C).

`detect_project(cwd)` sniffs a target directory for the signs of an EXISTING
codebase — language/runtime manifests, framework dependencies, a package
manager, a git repo — so the install wizard can (a) recognise that it is being
dropped into a brownfield project rather than an empty dir, and (b) prefill its
questions with sensible, evidence-based defaults instead of asking blind.

Detection is best-effort and fail-soft: an unreadable or absent manifest simply
yields fewer hints, never an error. Nothing here writes or mutates anything.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

# Manifest file -> (canonical language, package manager). First hit wins, in the
# order listed, so more specific/!common ecosystems can take precedence.
_LANGUAGE_MANIFESTS: list[tuple[str, str, str]] = [
    # filename, language, package_manager
    ("pnpm-lock.yaml", "TypeScript", "pnpm"),
    ("yarn.lock", "TypeScript", "yarn"),
    ("package.json", "TypeScript", "npm"),
    ("pyproject.toml", "Python", "pip"),
    ("requirements.txt", "Python", "pip"),
    ("Pipfile", "Python", "pip"),
    ("go.mod", "Go", "go mod"),
    ("Cargo.toml", "Rust", "cargo"),
    ("composer.json", "PHP", "composer"),
    ("pom.xml", "Java", "maven"),
    ("build.gradle", "Java", "gradle"),
    ("build.gradle.kts", "Kotlin", "gradle"),
    ("Gemfile", "Ruby", "bundler"),
    ("*.csproj", "C#", "dotnet"),
    ("*.sln", "C#", "dotnet"),
]

# Framework name -> dependency-string fragments that imply it. Checked against
# the raw text of the relevant manifest (cheap and robust across formats).
_FRAMEWORK_HINTS: dict[str, list[str]] = {
    "Next.js": ["next"],
    "React": ["react"],
    "Vue": ["vue"],
    "Svelte": ["svelte"],
    "Angular": ["@angular/core"],
    "NestJS": ["@nestjs/core"],
    "Express": ["express"],
    "FastAPI": ["fastapi"],
    "Django": ["django"],
    "Flask": ["flask"],
    "Laravel": ["laravel/framework"],
    "Spring Boot": ["spring-boot", "spring-boot-starter"],
    "Rails": ["rails"],
    "Gin": ["gin-gonic/gin"],
    "Actix": ["actix-web"],
}


def _first_existing(base: Path, name: str) -> Path | None:
    """Return the first match for `name` (supports a leading-glob like '*.csproj')."""
    if name.startswith("*."):
        matches = sorted(base.glob(name))
        return matches[0] if matches else None
    p = base / name
    return p if p.exists() else None


def _detect_language(base: Path) -> tuple[str | None, str | None, Path | None]:
    for name, language, pm in _LANGUAGE_MANIFESTS:
        hit = _first_existing(base, name)
        if hit is not None:
            return language, pm, hit
    return None, None, None


def _detect_framework(base: Path, manifest: Path | None) -> str | None:
    texts: list[str] = []
    # Always consider the detected manifest, plus a couple of common dependency
    # files, so a framework in requirements.txt is found even if pyproject led.
    candidates = [manifest] if manifest else []
    for extra in ("package.json", "requirements.txt", "pyproject.toml", "composer.json"):
        candidates.append(base / extra)
    for c in candidates:
        if c and c.exists():
            try:
                texts.append(c.read_text(errors="ignore").lower())
            except OSError:
                pass
    blob = "\n".join(texts)
    for framework, needles in _FRAMEWORK_HINTS.items():
        for needle in needles:
            # Word-ish boundary so "next" doesn't match "context".
            if re.search(r"[\"'/\b]" + re.escape(needle.lower()) + r"[\"'@\b/]", blob):
                return framework
    return None


def _project_name(base: Path, manifest: Path | None) -> str | None:
    """Best-effort project name from package.json / pyproject.toml, else dir name."""
    pkg = base / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(errors="ignore"))
            if isinstance(data, dict) and data.get("name"):
                return str(data["name"])
        except (ValueError, OSError):
            pass
    pyproject = base / "pyproject.toml"
    if pyproject.exists():
        try:
            m = re.search(r'(?m)^\s*name\s*=\s*["\']([^"\']+)["\']', pyproject.read_text())
            if m:
                return m.group(1)
        except OSError:
            pass
    return None


def detect_project(cwd: Path | str | None = None) -> dict[str, Any]:
    """Inspect `cwd` and report what existing-project signals it carries.

    Returns a dict with keys:
      is_existing      bool  — any source manifest / git repo / source tree present
      language         str|None
      framework        str|None
      package_manager  str|None
      project_name     str|None
      has_git          bool
      signals          list[str]  — human-readable evidence for the above
    """
    base = Path(cwd) if cwd else Path.cwd()
    signals: list[str] = []

    language, pm, manifest = _detect_language(base)
    if manifest is not None:
        signals.append(f"found {manifest.name}")

    framework = _detect_framework(base, manifest)
    if framework:
        signals.append(f"framework looks like {framework}")

    has_git = (base / ".git").exists()
    if has_git:
        signals.append("git repository")

    # A bare dir with only the kit's own scaffolding is NOT 'existing'. We treat
    # a project as existing if it has a language manifest, a git repo, or obvious
    # source files that predate us.
    has_source = any(
        p.is_file()
        for p in base.glob("*")
        if p.suffix in {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".php", ".rb"}
    )
    if has_source:
        signals.append("source files in root")

    is_existing = bool(manifest is not None or has_git or has_source)

    return {
        "is_existing": is_existing,
        "language": language,
        "framework": framework,
        "package_manager": pm,
        "project_name": _project_name(base, manifest),
        "has_git": has_git,
        "signals": signals,
    }
