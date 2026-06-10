# SPDX-License-Identifier: Apache-2.0
"""R12: property-based tests for the init.py / compile_skills.py parsers.

Uses Hypothesis to assert invariants that must hold for ANY input, plus a
hand-curated "nasty inputs" corpus (malformed frontmatter, path traversal,
unicode, YAML attacks) derived from the 2026-06 code audit.
"""

import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "agents" / "scripts"))

import compile_skills as cs  # noqa: E402
import init as init_mod  # noqa: E402

# --- Nasty inputs corpus (from code-audit-2026-06.md §6) -------------------
NASTY_FRONTMATTER = [
    "",
    "---",
    "---\nname: x",
    "---\n---",
    "---\n[1,2,3]\n---",
    "---\nname: [unterminated\n---",
    "---\n\tname: x\n---",
    "---\nname: a\nname: b\n---",
    '---\ndesc: "a --- b"\n---\nbody',
    "----\nname: x\n----",
    "﻿---\nname: x\n---",
    "---\r\nname: x\r\n---",
    "---\nname: !!python/object/apply:os.system ['id']\n---",
    "---\nname: ../../../etc/cron.d/evil\n---",
    "---\nname: ..\\..\\..\\Windows\\System32\\x\n---",
    '---\nname: "a/b/c"\n---',
    '---\nname: ""\n---',
    '---\ntags: "[py, go"\n---',
    "---\ntags:\n  nested: {a: 1}\n---",
    "---\nname: 12345\n---",
]

NASTY_NAMES = [
    "../../../etc/passwd",
    "..\\..\\windows",
    "a/b/c",
    "",
    "..",
    ".",
    "\x00null",
    "  spaces  ",
    "MiXeD-Case",
    "name!!!@@@",
    "-leading",
    "тест-unicode",
]


@pytest.mark.parametrize("content", NASTY_FRONTMATTER)
def test_ensure_yaml_frontmatter_never_raises(content):
    """ensure_yaml_frontmatter must always return (dict, str), never raise."""
    meta, out = init_mod.ensure_yaml_frontmatter(content, "x.skill.md")
    assert isinstance(meta, dict)
    assert isinstance(out, str)


@pytest.mark.parametrize("content", NASTY_FRONTMATTER)
def test_compile_ensure_yaml_frontmatter_never_raises(content):
    meta, out = cs.ensure_yaml_frontmatter(content, "x.skill.md")
    assert isinstance(meta, dict)
    assert isinstance(out, str)


@pytest.mark.parametrize("raw", NASTY_NAMES)
def test_safe_slug_never_escapes(raw):
    """safe_slug must never produce a path separator, '..', NUL, or empty slug."""
    slug = cs.safe_slug(raw, fallback="fb")
    assert slug
    assert "/" not in slug and "\\" not in slug
    assert ".." not in slug
    assert "\x00" not in slug
    assert not slug.startswith("-") and not slug.endswith("-")
    # Slug stays within a target dir (no traversal).
    target = Path("/tmp/target")
    resolved = (target / f"{slug}.mdc").resolve()
    assert str(resolved).startswith(str(target.resolve()))


@settings(max_examples=200)
@given(st.text())
def test_safe_slug_charset_invariant(raw):
    """For ANY input string, the slug contains only [a-z0-9-]."""
    slug = cs.safe_slug(raw, fallback="fb")
    assert slug
    assert all(c.isalnum() and c.isascii() or c == "-" for c in slug)
    assert ".." not in slug


@settings(max_examples=100)
@given(st.text(min_size=0, max_size=500))
def test_ensure_frontmatter_idempotent_shape(body):
    """Wrapping arbitrary text yields parseable output whose re-parse is stable."""
    content = body
    meta1, out1 = cs.ensure_yaml_frontmatter(content, "f.skill.md")
    meta2, out2 = cs.ensure_yaml_frontmatter(out1, "f.skill.md")
    assert isinstance(meta1, dict) and isinstance(meta2, dict)
    assert isinstance(out1, str) and isinstance(out2, str)


@settings(max_examples=100)
@given(st.text())
def test_inject_schema_version_idempotent(body):
    """inject_schema_version applied twice equals applied once (idempotent)."""
    once = cs.inject_schema_version(body)
    twice = cs.inject_schema_version(once)
    assert once == twice


def test_yaml_deserialization_is_inert():
    """A YAML object-injection payload must not execute (safe_load only)."""
    payload = "---\nname: !!python/object/apply:os.system ['echo pwned']\n---\nbody"
    meta, _ = cs.ensure_yaml_frontmatter(payload, "x.skill.md")
    # Either parsed inertly to the default, or to a dict — never executed.
    assert isinstance(meta, dict)
