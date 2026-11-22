#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""registry_import.py — draw external skills from a universal SKILL.md registry
into GABBE, with mandatory validation + a basic security scan before acceptance.

Imported skills are TREATED AS UNTRUSTED supply-chain input: every candidate
must pass frontmatter validation (real YAML), a safe-slug / path-traversal check,
and an egress/secret/executable-payload scan. Skills land NAMESPACED under
agents/skills/<namespace>/ and are never auto-trusted — review before use.

The scan is a heuristic safety net, not a sandbox. It matches common payload shapes
in the text (see _DANGER_PATTERNS, one short reason each); a determined author can
write a payload it does not see. Review every imported skill before use.

Frontmatter is limited to the keys the kit's own skills use (ALLOWED_KEYS). A skill
with any other key (for example `allowed-tools` or `hooks`), or whose name is the
name of a kit skill, is rejected.

Usage:
    python scripts/registry_import.py <source> [--namespace ext] [--apply] [--kit-root DIR]
      <source> = a local path (file/dir/.tar.gz) or an http(s) URL to a SKILL.md / bundle.
    Without --apply it is a dry run (validate + report only).
"""

import argparse
import ipaddress
import re
import shutil
import socket
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

KIT_ROOT_DEFAULT = Path(__file__).resolve().parent.parent

# A skill pack is text; anything larger than this is refused while downloading.
MAX_DOWNLOAD_BYTES = 20 * 1024 * 1024

# Heuristic red flags for a basic egress/secret/executable-payload scan. This is
# a safety net, not a sandbox — imported skills still require human review.
_DANGER_PATTERNS = [
    (re.compile(r"\b(curl|wget|fetch)\b[^|\n]*\|\s*(sh|bash|zsh|dash)\b"), "pipe-to-shell"),
    (re.compile(r"<\(\s*(curl|wget|fetch)\b"), "process-substitution-download"),
    (re.compile(r"(~|\$HOME)?/?\.ssh/|\bid_(rsa|ed25519|ecdsa|dsa)\b"), "ssh-key-access"),
    (re.compile(r"\b(eval|exec)\s*\("), "dynamic-exec"),
    (re.compile(r"https?://[^\s)]+\?[^\s)]*=(?:\$|%)"), "templated-exfil-url"),
    (
        re.compile(
            r"(?i)\b(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9/_+\-]{12,}"
        ),
        "embedded-secret",
    ),
    (re.compile(r"(?i)base64\s+-d|atob\(|b64decode"), "obfuscated-payload"),
    # Reverse shells: a shell wired to a remote host.
    (re.compile(r"/dev/tcp/|\bnc(at)?\b[^\n]*\s-[A-Za-z]*e\b|\bbash\s+-i\s*>&"), "reverse-shell"),
    # Two-step run: a download to a file, then chmod +x or sh <file> within 200 characters
    # (lines included). Does not catch a run after a longer gap, a download by another
    # tool (python, git), or `./file` run without chmod.
    (
        re.compile(
            r"(?s)\b(curl|wget)\b.{0,200}?(-o|-O|>)\s*\S+.{0,200}?"
            r"(chmod\s+\+x|\b(sh|bash)\s+[/.~\w])"
        ),
        "download-then-run",
    ),
    # Secret stores: a read, copy or upload of .env, cloud/GitHub credentials, browser profiles.
    (
        re.compile(
            r"(?i)\b(cat|less|more|head|tail|source|cp|scp|base64|tar|zip)\b[^\n|]*(?<![\w])\.env(?![\w-]|\.\w)"
            r"|(--data[-a-z]*|-d|-F|-T)\s*['\"]?@\S*(\.env(?![\w-]|\.\w)|\.aws/|\.config/gh)"
        ),
        "env-file-access",
    ),
    (re.compile(r"\.aws/(credentials|config)|\.config/gh/|\.netrc\b"), "cloud-credentials-access"),
    (
        re.compile(
            r"(?i)\.mozilla/firefox|\.config/(google-chrome|chromium|BraveSoftware)"
            r"|Application Support/(Google/Chrome|Firefox)|AppData[\\/]+Local[\\/]+(Google|Microsoft)"
        ),
        "browser-profile-access",
    ),
    # PowerShell: download piped into, or passed to, iex / Invoke-Expression.
    (
        re.compile(
            r"(?i)\b(iwr|irm|invoke-webrequest|invoke-restmethod|downloadstring)\b[^\n]*"
            r"\b(iex|invoke-expression)\b|\b(iex|invoke-expression)\b[^\n]*"
            r"\b(iwr|irm|invoke-webrequest|invoke-restmethod|downloadstring)\b"
        ),
        "powershell-download-exec",
    ),
    # Hidden instructions: invisible characters and prompt-override phrases.
    (re.compile("[\u200b-\u200f\u202a-\u202e\u2060-\u2064]"), "hidden-characters"),
    (
        re.compile(r"(?i)ignore\s+(all\s+)?previous\b|disregard\s+the\s+above"),
        "prompt-override-phrase",
    ),
]

# Frontmatter keys an imported skill may carry: exactly the keys the kit's own skills use.
# Keys such as allowed-tools, hooks, permissions or model are never accepted.
ALLOWED_KEYS = frozenset(
    {"name", "description", "tags", "triggers", "context_cost", "core", "role", "tools"}
)
_NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def _load_helpers(kit_root):
    sys.path.insert(0, str(kit_root / "agents" / "scripts"))
    import compile_skills  # noqa: E402
    import validate_skills  # noqa: E402

    return compile_skills, validate_skills


def _validate_remote_url(source: str) -> None:
    """SSRF / MITM guard for a remote registry source.

    Imported skills are untrusted supply-chain input, so the *transport* is locked
    down too: require HTTPS (no plaintext MITM of the payload) and refuse URLs that
    resolve to non-public addresses (loopback / private / link-local / metadata
    endpoints like 169.254.169.254). Best-effort — this is a pre-flight resolution
    check, not a pinned connection — but it closes the obvious SSRF angles.
    """
    parsed = urlparse(source)
    if parsed.scheme != "https":
        raise SystemExit(
            f"refusing non-HTTPS registry URL ({parsed.scheme or 'no-scheme'}://…): "
            "use https:// for supply-chain integrity."
        )
    host = parsed.hostname or ""
    if not host:
        raise SystemExit(f"registry URL has no host: {source}")
    try:
        infos = socket.getaddrinfo(host, parsed.port or 443)
    except socket.gaierror as e:
        raise SystemExit(f"cannot resolve registry host {host!r}: {e}")
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            raise SystemExit(
                f"refusing registry URL pointing at a non-public address: {host} -> {ip}"
            )


class _CheckedRedirects(urllib.request.HTTPRedirectHandler):
    """Apply the first-URL checks (HTTPS, public address) to every redirect hop."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _validate_remote_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _read_limited(response, dest: Path, limit: int = MAX_DOWNLOAD_BYTES) -> None:
    """Copy a response to dest, stopping with a clear error above `limit` bytes."""
    total = 0
    with open(dest, "wb") as out:
        while True:
            chunk = response.read(65536)
            if not chunk:
                return
            total += len(chunk)
            if total > limit:
                raise SystemExit(f"download larger than {limit} bytes; refusing.")
            out.write(chunk)


def _download(source: str, dest: Path) -> None:
    opener = urllib.request.build_opener(_CheckedRedirects)
    # nosec: scheme/host validated before and on every redirect; content validated later.
    with opener.open(source, timeout=60) as response:  # noqa: S310
        _read_limited(response, dest)


def _fetch(source: str, stage: Path) -> Path:
    """Resolve <source> (URL or path) into a staging dir; return the staging root."""
    if source.startswith(("http://", "https://")):
        _validate_remote_url(source)
        dest = stage / Path(source.split("?")[0]).name
        _download(source, dest)
        src = dest
    else:
        src = Path(source)
        if not src.exists():
            raise SystemExit(f"source not found: {source}")
    if str(src).endswith((".tar.gz", ".tgz")):
        with tarfile.open(src) as tf:
            _safe_extract(tf, stage)
        return stage
    if src.is_dir():
        shutil.copytree(src, stage / src.name, dirs_exist_ok=True)
        return stage / src.name
    # single file. For the URL path src is already inside `stage`, so copying it to
    # `stage / src.name` would be a copy-onto-self (shutil.SameFileError) — guard it.
    target = stage / src.name
    if src.resolve() != target.resolve():
        shutil.copy2(src, target)
    return stage


def _safe_extract(tf: tarfile.TarFile, dest: Path):
    """Extract a tarball, refusing any member that escapes dest or is a link.

    Defends against path traversal (absolute paths / ``..``) AND symlink/hardlink
    members, which can otherwise redirect a write outside the staging dir during
    extraction. The containment test uses real path-ancestry (a plain string
    prefix would wrongly accept ``/tmp/xx`` as inside ``/tmp/x``).
    """
    dest = dest.resolve()
    for member in tf.getmembers():
        if member.issym() or member.islnk():
            raise SystemExit(f"refusing link member (symlink/hardlink): {member.name}")
        if not (member.isfile() or member.isdir()):
            raise SystemExit(f"refusing special member (device/FIFO): {member.name}")
        target = (dest / member.name).resolve()
        if target != dest and dest not in target.parents:
            raise SystemExit(f"refusing path-traversal member: {member.name}")
    if hasattr(tarfile, "data_filter"):  # Python 3.12+ (and security backports)
        tf.extractall(dest, filter="data")  # noqa: S202
    else:
        tf.extractall(dest)  # noqa: S202 - members validated above (no links, contained paths)


def _kit_slugs(skills_dir: Path, compile_skills) -> set:
    """Slugs of the kit's own skills (folders the compiler lists as the kit's)."""
    slugs = set()
    for f in skills_dir.rglob("*.skill.md"):
        rel = f.relative_to(skills_dir).parts
        if len(rel) > 1 and rel[0] not in compile_skills.KIT_SKILL_DIRS:
            continue
        meta, _ = compile_skills.ensure_yaml_frontmatter(f.read_text(errors="replace"), f.name)
        slugs.add(compile_skills.safe_slug(str(meta.get("name", f.stem.replace(".skill", "")))))
    return slugs


def _scan(text: str):
    return [label for pat, label in _DANGER_PATTERNS if pat.search(text)]


def validate_candidate(path: Path, compile_skills, validate_skills, kit_slugs=frozenset()):
    """Return (ok, slug, reason). Rejects on frontmatter/slug/security failure."""
    text = path.read_text(errors="replace")
    ok, msg = validate_skills.validate_frontmatter(path)
    if not ok:
        return False, None, f"frontmatter: {msg}"
    meta, _ = compile_skills.ensure_yaml_frontmatter(text, path.name)
    name = str(meta.get("name", path.stem))
    slug = compile_skills.safe_slug(name)
    if not slug or slug in (".", ".."):
        return False, None, "unsafe slug"
    if not _NAME_RE.match(name):
        return False, slug, "name must be lowercase letters, digits and single hyphens"
    extra = sorted(str(k) for k in meta if str(k) not in ALLOWED_KEYS)
    if extra:
        return False, slug, f"frontmatter keys not allowed: {', '.join(extra)}"
    if kit_slugs and slug in kit_slugs:
        return False, slug, f"name '{slug}' is already a kit skill"
    flags = _scan(text)
    if flags:
        return False, slug, f"security: {', '.join(flags)}"
    return True, slug, "ok"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", help="local path / .tar.gz / http(s) URL")
    ap.add_argument("--namespace", default="ext", help="land under agents/skills/<namespace>/")
    ap.add_argument("--apply", action="store_true", help="actually write (default: dry run)")
    ap.add_argument("--kit-root", default=str(KIT_ROOT_DEFAULT))
    args = ap.parse_args()

    kit_root = Path(args.kit_root).resolve()
    compile_skills, validate_skills = _load_helpers(kit_root)
    skills_dir = kit_root / "agents" / "skills"
    namespace = re.sub(r"[^a-z0-9_-]+", "-", args.namespace.lower())
    if not namespace.strip("-_") or namespace in compile_skills.KIT_SKILL_DIRS:
        raise SystemExit(f"refusing namespace {args.namespace!r}: empty or a kit skill folder")
    ns_dir = skills_dir / namespace
    kit_slugs = _kit_slugs(skills_dir, compile_skills)

    with tempfile.TemporaryDirectory(prefix="gabbe-import-") as tmp:
        root = _fetch(args.source, Path(tmp))
        candidates = sorted(set(root.rglob("*.skill.md")) | set(root.rglob("SKILL.md")))
        if not candidates:
            print("No SKILL.md / *.skill.md found in source.")
            return

        accepted, rejected = [], []
        for c in candidates:
            ok, slug, reason = validate_candidate(c, compile_skills, validate_skills, kit_slugs)
            (accepted if ok else rejected).append((c, slug, reason))

        print(
            f"Candidates: {len(candidates)}  accepted: {len(accepted)}  rejected: {len(rejected)}"
        )
        for c, slug, reason in rejected:
            print(f"  [REJECT] {c.name}: {reason}")
        for c, slug, reason in accepted:
            print(f"  [OK]     {c.name} -> {args.namespace}/{slug}.skill.md")

        if not args.apply:
            print(
                "\nDry run. Re-run with --apply to import accepted skills (namespaced, for review)."
            )
            return

        ns_dir.mkdir(parents=True, exist_ok=True)
        # Disambiguate slug collisions WITHIN this import run so two distinct
        # source skills that slugify identically don't silently overwrite each
        # other (data loss). Re-importing the same skill still overwrites/updates
        # (we only track slugs used in this run, not pre-existing files).
        used: set[str] = set()
        for c, slug, _ in accepted:
            final = slug
            if final in used:
                n = 2
                while f"{slug}-{n}" in used:
                    n += 1
                final = f"{slug}-{n}"
                print(f"  [DEDUP]  {c.name}: duplicate slug '{slug}' -> '{final}'")
            used.add(final)
            (ns_dir / f"{final}.skill.md").write_text(c.read_text(errors="replace"))
        print(
            f"\nImported {len(accepted)} skills -> {ns_dir} (NAMESPACED, untrusted — review before use)."
        )


if __name__ == "__main__":
    main()
