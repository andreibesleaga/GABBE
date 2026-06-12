# SPDX-License-Identifier: Apache-2.0
"""Permanent doc/code sync guard: every top-level command and `brain`
subcommand registered in gabbe/main.py must be documented in
docs/CLI_REFERENCE.md, and vice versa. Keeps Pillar 7 (docs) honest as the
CLI evolves. Source-parsed (no side effects).
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MAIN_SRC = (REPO_ROOT / "gabbe" / "main.py").read_text()
CLI_REF = (REPO_ROOT / "docs" / "CLI_REFERENCE.md").read_text()


def _top_level_registered():
    # `subparsers.add_parser("name", ...)` — the main command group.
    return set(re.findall(r'subparsers\.add_parser\(\s*["\']([a-z][a-z-]+)["\']', MAIN_SRC))


def _brain_subcommands_registered():
    return set(re.findall(r'brain_sub\.add_parser\(\s*["\']([a-z][a-z-]+)["\']', MAIN_SRC))


def _documented_top_level():
    # First token after `gabbe ` in inline code spans.
    cmds = set(re.findall(r"`gabbe ([a-z][a-z-]+)", CLI_REF))
    return {c for c in cmds if c not in {"x", "command"}}


def _documented_brain_subcommands():
    return set(re.findall(r"`gabbe brain ([a-z][a-z-]+)", CLI_REF))


def test_documented_top_level_commands_exist():
    missing = _documented_top_level() - _top_level_registered()
    assert not missing, f"Documented but not implemented: {sorted(missing)}"


def test_registered_top_level_commands_are_documented():
    undocumented = _top_level_registered() - _documented_top_level()
    assert not undocumented, f"Implemented but undocumented: {sorted(undocumented)}"


def test_brain_subcommands_match_docs():
    registered = _brain_subcommands_registered()
    documented = _documented_brain_subcommands()
    assert registered, "expected brain subcommands in main.py"
    assert (
        registered == documented
    ), f"brain subcommand drift: registered={sorted(registered)} documented={sorted(documented)}"
