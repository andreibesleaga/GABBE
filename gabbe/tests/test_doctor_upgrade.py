# SPDX-License-Identifier: Apache-2.0
"""`gabbe doctor` warns when a project's kept kit files are older than the CLI (1.2.0)."""

from gabbe import __version__
from gabbe.doctor import kit_upgrade_warnings, run_doctor

ARTICLE0 = "### Article 0 — Operating Safety\n"


def _write(root, agents_stamp, constitution_stamp, article0=True):
    agents = root / "agents"
    agents.mkdir(parents=True, exist_ok=True)
    stamp = lambda v: f"\n---\n\n*GABBE Kit version: {v}*\n" if v else "\n"  # noqa: E731
    (agents / "AGENTS.md").write_text("# Agents\n" + stamp(agents_stamp))
    body = "# Constitution\n" + (ARTICLE0 if article0 else "") + stamp(constitution_stamp)
    (agents / "CONSTITUTION.md").write_text(body)


def test_current_stamp_gives_no_warning(tmp_path):
    _write(tmp_path, __version__, __version__)
    assert kit_upgrade_warnings(tmp_path) == []


def test_older_stamp_warns_per_file(tmp_path):
    _write(tmp_path, "1.1.3", "1.0.9")
    warnings = kit_upgrade_warnings(tmp_path, cli_version="1.2.0")
    assert len(warnings) == 2
    assert "agents/AGENTS.md" in warnings[0] and "1.1.3" in warnings[0] and "1.2.0" in warnings[0]
    assert "agents/CONSTITUTION.md" in warnings[1] and "1.0.9" in warnings[1]
    assert all("docs/UPGRADING.md" in w for w in warnings)


def test_version_compare_is_numeric(tmp_path):
    _write(tmp_path, "1.9.0", "1.9.0")
    assert kit_upgrade_warnings(tmp_path, cli_version="1.10.0") != []
    _write(tmp_path, "1.10.0", "1.10.0")
    assert kit_upgrade_warnings(tmp_path, cli_version="1.9.0") == []


def test_missing_stamp_warns(tmp_path):
    _write(tmp_path, None, __version__)
    warnings = kit_upgrade_warnings(tmp_path)
    assert len(warnings) == 1
    assert "agents/AGENTS.md" in warnings[0] and "no version stamp" in warnings[0]


def test_missing_article_0_warns(tmp_path):
    _write(tmp_path, __version__, __version__, article0=False)
    warnings = kit_upgrade_warnings(tmp_path)
    assert len(warnings) == 1
    assert "Article 0" in warnings[0] and "CONSTITUTION.md" in warnings[0]


def test_no_kit_no_warning(tmp_path):
    assert kit_upgrade_warnings(tmp_path) == []


def test_doctor_prints_warnings_and_keeps_exit_code(tmp_path, capsys):
    _write(tmp_path, "0.9.0", "0.9.0", article0=False)
    assert run_doctor(tmp_path) == 0
    out = capsys.readouterr().out
    assert out.count("[WARN]") >= 3
    assert "docs/UPGRADING.md" in out


def test_doctor_without_kit_unchanged(tmp_path, capsys):
    assert run_doctor(tmp_path) == 0
    assert "UPGRADING" not in capsys.readouterr().out


def test_a_missing_stamp_is_worded_as_missing(tmp_path):
    _write(tmp_path, None, __version__)
    (warning,) = kit_upgrade_warnings(tmp_path)
    assert warning.startswith("agents/AGENTS.md has no version stamp, this CLI is ")
    assert "from kit no" not in warning
