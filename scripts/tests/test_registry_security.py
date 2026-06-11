# SPDX-License-Identifier: Apache-2.0
"""Regression tests for the skills-registry import hardening (path traversal,
symlink/hardlink rejection). Guards the fixes for the PR #9 review findings."""

import io
import sys
import tarfile
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import registry_import as ri  # noqa: E402


def _tar_with(members):
    """Build an in-memory .tar.gz from a list of (TarInfo, bytes|None)."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for info, data in members:
            tf.addfile(info, io.BytesIO(data) if data is not None else None)
    buf.seek(0)
    return tarfile.open(fileobj=buf)


def test_safe_extract_rejects_parent_traversal():
    info = tarfile.TarInfo("../escaped.txt")
    info.size = 1
    with tempfile.TemporaryDirectory() as d:
        with pytest.raises(SystemExit, match="path-traversal"):
            ri._safe_extract(_tar_with([(info, b"x")]), Path(d))


def test_safe_extract_rejects_absolute_path():
    info = tarfile.TarInfo("/etc/evil")
    info.size = 1
    with tempfile.TemporaryDirectory() as d:
        with pytest.raises(SystemExit):
            ri._safe_extract(_tar_with([(info, b"x")]), Path(d))


def test_safe_extract_rejects_symlink_member():
    link = tarfile.TarInfo("link")
    link.type = tarfile.SYMTYPE
    link.linkname = "/etc/passwd"
    with tempfile.TemporaryDirectory() as d:
        with pytest.raises(SystemExit, match="link member"):
            ri._safe_extract(_tar_with([(link, None)]), Path(d))


def test_safe_extract_rejects_hardlink_member():
    link = tarfile.TarInfo("hard")
    link.type = tarfile.LNKTYPE
    link.linkname = "victim"
    with tempfile.TemporaryDirectory() as d:
        with pytest.raises(SystemExit, match="link member"):
            ri._safe_extract(_tar_with([(link, None)]), Path(d))


def test_safe_extract_accepts_contained_member():
    info = tarfile.TarInfo("skills/ok.skill.md")
    payload = b"---\nname: ok\n---\n"
    info.size = len(payload)
    with tempfile.TemporaryDirectory() as d:
        ri._safe_extract(_tar_with([(info, payload)]), Path(d))
        assert (Path(d) / "skills" / "ok.skill.md").exists()


def test_sibling_prefix_is_not_treated_as_contained(tmp_path):
    """A plain string-prefix check would wrongly accept /x/yy as inside /x/y."""
    info = tarfile.TarInfo("ok.txt")
    info.size = 1
    dest = tmp_path / "y"
    dest.mkdir()
    # Sanity: a normal member under dest is accepted (no false rejection).
    ri._safe_extract(_tar_with([(info, b"x")]), dest)
    assert (dest / "ok.txt").exists()
