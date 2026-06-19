# SPDX-License-Identifier: Apache-2.0
"""Workstream A: the wizard merge never clobbers user data.

`safe_merge_directory` must back up any differing pre-existing file to
`<name>.gabbe-bak` before refreshing it, leave preserve-set files untouched by
default, and re-template them (still backing up first) only when force=True.
"""

import os
import sys
from pathlib import Path

# Ensure scripts directory is importable (mirrors test_init.py).
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import init


def _src(tmp_path: Path) -> Path:
    src = tmp_path / "kit"
    (src / "skills").mkdir(parents=True)
    (src / "AGENTS.md").write_text("KIT AGENTS\n")
    (src / "README.md").write_text("KIT README v2\n")
    (src / "skills" / "a.skill.md").write_text("kit skill\n")
    return src


def test_non_preserved_file_is_backed_up_then_refreshed(tmp_path):
    src = _src(tmp_path)
    dst = tmp_path / "proj" / "agents"
    dst.mkdir(parents=True)
    # README.md is NOT in the preserve-set; a user copy already exists and differs.
    (dst / "README.md").write_text("USER README v1\n")

    init.safe_merge_directory(src, dst, force=False)

    # The kit version is now in place...
    assert (dst / "README.md").read_text() == "KIT README v2\n"
    # ...but the user's original is recoverable, never lost.
    assert (dst / "README.md.gabbe-bak").read_text() == "USER README v1\n"


def test_identical_file_creates_no_backup(tmp_path):
    src = _src(tmp_path)
    dst = tmp_path / "proj" / "agents"
    dst.mkdir(parents=True)
    (dst / "README.md").write_text("KIT README v2\n")  # byte-identical to source

    init.safe_merge_directory(src, dst, force=False)

    assert not (dst / "README.md.gabbe-bak").exists()


def test_preserve_set_untouched_without_force(tmp_path):
    src = _src(tmp_path)
    dst = tmp_path / "proj" / "agents"
    dst.mkdir(parents=True)
    (dst / "AGENTS.md").write_text("USER AGENTS\n")  # preserve-set member

    init.safe_merge_directory(src, dst, force=False)

    # Preserved verbatim; no backup needed because it was never overwritten.
    assert (dst / "AGENTS.md").read_text() == "USER AGENTS\n"
    assert not (dst / "AGENTS.md.gabbe-bak").exists()


def test_force_retemplates_preserve_set_but_backs_up_first(tmp_path):
    src = _src(tmp_path)
    dst = tmp_path / "proj" / "agents"
    dst.mkdir(parents=True)
    (dst / "AGENTS.md").write_text("USER AGENTS\n")

    init.safe_merge_directory(src, dst, force=True)

    assert (dst / "AGENTS.md").read_text() == "KIT AGENTS\n"
    assert (dst / "AGENTS.md.gabbe-bak").read_text() == "USER AGENTS\n"


def test_first_backup_wins_on_reinstall(tmp_path):
    src = _src(tmp_path)
    dst = tmp_path / "proj" / "agents"
    dst.mkdir(parents=True)
    (dst / "README.md").write_text("USER README v1\n")

    init.safe_merge_directory(src, dst, force=False)  # backs up the original
    # Second run: the .gabbe-bak must still hold the user's ORIGINAL, not a kit copy.
    init.safe_merge_directory(src, dst, force=False)

    assert (dst / "README.md.gabbe-bak").read_text() == "USER README v1\n"
