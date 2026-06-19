# SPDX-License-Identifier: Apache-2.0
"""Workstream C: brownfield project detection sniffs language/framework/PM and
distinguishes an existing codebase from an empty greenfield directory."""

import json

from gabbe import detect


def test_empty_dir_is_greenfield(tmp_path):
    info = detect.detect_project(tmp_path)
    assert info["is_existing"] is False
    assert info["language"] is None
    assert info["framework"] is None


def test_detects_node_next_project(tmp_path):
    (tmp_path / "package.json").write_text(
        json.dumps({"name": "my-web", "dependencies": {"next": "^14", "react": "^18"}})
    )
    info = detect.detect_project(tmp_path)
    assert info["is_existing"] is True
    assert info["language"] == "TypeScript"
    assert info["package_manager"] == "npm"
    assert info["framework"] == "Next.js"
    assert info["project_name"] == "my-web"


def test_pnpm_lock_takes_precedence_for_pm(tmp_path):
    (tmp_path / "package.json").write_text(json.dumps({"name": "x", "dependencies": {}}))
    (tmp_path / "pnpm-lock.yaml").write_text("lockfileVersion: 6.0\n")
    info = detect.detect_project(tmp_path)
    assert info["package_manager"] == "pnpm"


def test_detects_python_fastapi(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "svc"\ndependencies = ["fastapi"]\n'
    )
    (tmp_path / "requirements.txt").write_text("fastapi==0.110\nuvicorn\n")
    info = detect.detect_project(tmp_path)
    assert info["language"] == "Python"
    assert info["package_manager"] == "pip"
    assert info["framework"] == "FastAPI"
    assert info["project_name"] == "svc"


def test_detects_go_module(tmp_path):
    (tmp_path / "go.mod").write_text("module example.com/app\n\ngo 1.22\n")
    info = detect.detect_project(tmp_path)
    assert info["language"] == "Go"
    assert info["package_manager"] == "go mod"


def test_git_repo_alone_marks_existing(tmp_path):
    (tmp_path / ".git").mkdir()
    info = detect.detect_project(tmp_path)
    assert info["is_existing"] is True
    assert info["has_git"] is True


def test_source_files_alone_mark_existing(tmp_path):
    (tmp_path / "main.go").write_text("package main\n")
    info = detect.detect_project(tmp_path)
    assert info["is_existing"] is True
