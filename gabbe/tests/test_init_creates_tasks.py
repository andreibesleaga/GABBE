# SPDX-License-Identifier: Apache-2.0
"""`gabbe init` creates `project/TASKS.md`, which `gabbe verify` requires, and never replaces one."""

from gabbe import sync


def test_creates_an_empty_task_file_once(tmp_path, monkeypatch):
    tasks = tmp_path / "project" / "TASKS.md"
    tasks.parent.mkdir()
    monkeypatch.setattr(sync, "TASKS_FILE", tasks)
    assert sync.ensure_task_file() is True
    assert sync.parse_markdown_tasks(tasks.read_text(encoding="utf-8")) == []
    tasks.write_text("# My tasks\n- [ ] mine\n", encoding="utf-8")
    assert sync.ensure_task_file() is False
    assert tasks.read_text(encoding="utf-8") == "# My tasks\n- [ ] mine\n"


def test_a_link_is_never_replaced(tmp_path, monkeypatch):
    target = tmp_path / "elsewhere.md"
    target.write_text("theirs\n", encoding="utf-8")
    tasks = tmp_path / "project" / "TASKS.md"
    tasks.parent.mkdir()
    tasks.symlink_to(target)
    monkeypatch.setattr(sync, "TASKS_FILE", tasks)
    assert sync.ensure_task_file() is False
    assert tasks.is_symlink() and target.read_text(encoding="utf-8") == "theirs\n"
