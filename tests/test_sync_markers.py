import pytest
from pathlib import Path
from gabbe.sync import parse_markdown_tasks, generate_markdown_tasks, _generate_task_lines, _MARKER_START, _MARKER_END

def test_generate_task_lines():
    tasks = [
        {'title': 'Task 1', 'status': 'TODO'},
        {'title': 'Task 2', 'status': 'DONE'},
    ]
    lines = _generate_task_lines(tasks)
    assert "- [ ] Task 1" in lines
    assert "- [x] Task 2" in lines
    assert _MARKER_START not in lines # Should checks just lines not markers

def test_parse_markdown_tasks_legacy():
    content = """
- [ ] Legacy Task 1
- [x] Legacy Task 2
    """
    tasks = parse_markdown_tasks(content)
    assert len(tasks) == 2
    assert tasks[0]['title'] == 'Legacy Task 1'
    assert tasks[1]['status'] == 'DONE'

def test_parse_markdown_tasks_with_markers():
    content = f"""
# Header
Some notes...

{_MARKER_START}
- [ ] Marked Task 1
{_MARKER_END}

Footer notes...
- [ ] Ignored Task Outside
    """
    tasks = parse_markdown_tasks(content)
    assert len(tasks) == 1
    assert tasks[0]['title'] == 'Marked Task 1'

def test_import_reads_only_marked_section():
    content = f"""
{_MARKER_START}
- [ ] Real Task
{_MARKER_END}
- [ ] Fake Task
    """
    tasks = parse_markdown_tasks(content)
    assert len(tasks) == 1
    assert tasks[0]['title'] == 'Real Task'
