
import pytest
from unittest.mock import MagicMock, patch
from gabbe.sync import sync_tasks, TASKS_FILE, _MARKER_START, _MARKER_END

def test_sync_preserves_preamble_no_markers(tmp_path):
    """
    Test that when project/TASKS.md has no markers, the sync process preserves 
    any content before the first task list item.
    """
    # 1. Setup a fake project/TASKS.md with a custom preamble
    d = tmp_path / "project"
    d.mkdir()
    tasks_file = d / "TASKS.md"
    
    preamble = "# My Project Notes\n\nThis is a custom note that should be saved.\nAnd another line."
    original_content = f"{preamble}\n\n- [ ] Existing Task 1\n"
    tasks_file.write_text(original_content, encoding="utf-8")
    
    # 2. Mock DB to return some new tasks to export
    mock_db = MagicMock()
    mock_cursor = mock_db.cursor.return_value
    # Mock DB timestamps: DB is newer than file
    # file_mtime = 100, db_mtime = 200
    # Mocking get_db_timestamp to return 200
    
    # We need to patch get_db and TASKS_FILE config
    with patch("gabbe.sync.get_db", return_value=mock_db), \
         patch("gabbe.sync.TASKS_FILE", tasks_file), \
         patch("gabbe.sync.get_db_timestamp", return_value=200.0), \
         patch("pathlib.Path.stat") as mock_stat:
        
        # Mock file mtime to be older than DB (100.0 < 200.0)
        mock_stat.return_value.st_mtime = 100.0
        
        # Mock DB tasks fetch
        mock_cursor.fetchone.side_effect = [
             (5,), # count(*) > 0
             (200.0,), # max timestamp
        ]
        
        mock_cursor.fetchall.return_value = [
            {'title': 'New DB Task 1', 'status': 'TODO'},
            {'title': 'New DB Task 2', 'status': 'DONE'},
        ]
        
        # 3. Run Sync
        sync_tasks()
        
        # 4. Verify File Content
        new_content = tasks_file.read_text(encoding="utf-8")
        
        # Assert preamble is preserved
        assert preamble in new_content
        
        # Assert markers are added
        assert _MARKER_START in new_content
        assert _MARKER_END in new_content
        
        # Assert new tasks are there
        assert "- [ ] New DB Task 1" in new_content
        assert "- [x] New DB Task 2" in new_content

def test_sync_appends_if_no_tasks_found(tmp_path):
    """
    Test fallback behavior when no task list is found at all in the file.
    It should append the new task block.
    """
    d = tmp_path / "project"
    d.mkdir()
    tasks_file = d / "project/TASKS.md"
    
    content = "# Just a header\nNo tasks here yet."
    tasks_file.write_text(content, encoding="utf-8")
    
    mock_db = MagicMock()
    mock_cursor = mock_db.cursor.return_value
    
    with patch("gabbe.sync.get_db", return_value=mock_db), \
         patch("gabbe.sync.TASKS_FILE", tasks_file), \
         patch("gabbe.sync.get_db_timestamp", return_value=200.0), \
         patch("pathlib.Path.stat") as mock_stat:
        
        mock_stat.return_value.st_mtime = 100.0
        
        mock_cursor.fetchone.side_effect = [(1,), (200.0,)]
        mock_cursor.fetchall.return_value = [{'title': 'Task A', 'status': 'TODO'}]
        
        sync_tasks()
        
        new_content = tasks_file.read_text(encoding="utf-8")
        
        # Should contain original content AND the new block
        assert content in new_content
        assert _MARKER_START in new_content
        assert "- [ ] Task A" in new_content
