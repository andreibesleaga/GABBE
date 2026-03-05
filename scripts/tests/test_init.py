import sys
import os
from pathlib import Path
from unittest.mock import patch
import pytest

# Ensure scripts directory is in path so we can import init
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import init

ORIGINAL_KIT_SOURCE = init.KIT_SOURCE

@pytest.fixture
def temp_project():
    """Fixture to provide a clean temporary project directory for each test."""
    import tempfile
    with tempfile.TemporaryDirectory() as tempdir:
        original_cwd = os.getcwd()
        os.chdir(tempdir)
        init.PROJECT_ROOT = Path(tempdir)
        init.TECH_MAP = {}
        init.KIT_SOURCE = ORIGINAL_KIT_SOURCE
        init.SOURCE_AGENTS_DIR = ORIGINAL_KIT_SOURCE / "agents"
        yield Path(tempdir)
        os.chdir(original_cwd)

def test_golden_modern_greenfield(temp_project):
    inputs = [
        "1",              # Install: Local
        "MyTestProj",     # Name
        "Modern SaaS",    # Desc
        "2",              # Team: Small
        "1",              # Type: Greenfield
        "1",              # Lang: TypeScript
        "Next.js",        # Framework
        "1",              # DB: PostgreSQL
        "4",              # Cloud: Vercel
        "y",              # Dynamic Setup
        "Build a SaaS",   # Problem Statement
        "y",              # Analytics
        "y",              # Meta
        "n",              # GABBE CLI: No
        "1",              # PM: npm
        "1,2",            # Agents: Claude Code, Cursor
    ]
    with patch('builtins.input', side_effect=inputs):
        init.main()
    p = temp_project
    assert (p / "agents" / "AGENTS.md").exists()
    assert (p / "BOOTSTRAP_MISSION.md").exists()

def test_legacy_modernization_global(temp_project):
    global_target = temp_project / "global" / "agents"
    inputs = [
        "3",                     # Custom Path
        str(global_target),      # Enter path (ends in 'agents', so PROJECT_ROOT -> global/)
        "LegacyBanking",         # Name
        "Old to New",            # Desc
        "3",                     # Team: Large
        "2",                     # Type: Legacy
        # No compliance asked for Legacy Modernization
        "7",                     # Lang: Java
        "Spring Boot",           # Framework
        "1,5",                   # DB: Postgres, Redis
        "7",                     # Cloud: On-Prem
        "n",                     # Dynamic: NO
        "n",                     # Analytics: NO
        "n",                     # Meta: NO
        "n",                     # GABBE CLI: NO
        # Java doesn't ask for PM explicitly 
        "9,10",                   # Agents: Copilot, VS Code
    ]
    with patch('builtins.input', side_effect=inputs):
        init.main()
    project_root = temp_project / "global"  # PROJECT_ROOT rebound to parent of 'agents'
    assert global_target.exists()
    assert (global_target / "AGENTS.md").exists()
    assert (project_root / "SETUP_MISSION.md").exists()

def test_data_science_ai(temp_project):
    inputs = [
        "1",                    # Local
        "",                     # Name: default
        "",                     # Desc: default
        "1",                    # Team: Solo
        "4",                    # Type: R&D
        "3",                    # Lang: Python
        "FastAPI",              # Framework
        "6",                    # DB: None
        "7",                    # Cloud: On-Prem
        "y",                    # Dynamic Setup
        "AI Modeling",          # Problem Statement
        "y",                    # Analytics
        "y",                    # Meta
        "n",                    # GABBE CLI: NO
        # Python doesn't ask PM explicitly
        "7",                    # Agents: Gemini
    ]
    with patch('builtins.input', side_effect=inputs):
        init.main()
    p = temp_project
    assert (p / ".gemini" / "settings.json").exists()

def test_other_language(temp_project):
    inputs = [
        "1",                    # Local
        "",                     # Name 
        "",                     # Desc
        "1",                    # Team 
        "1",                    # Type
        "9",                    # Lang: Other
        "Elixir",               # Enter Lang
        "Phoenix",              # Framework
        "6",                    # DB
        "7",                    # Cloud
        "n",                    # Dynamic Setup
        "n",                    # Analytics
        "n",                    # Meta
        "n",                    # GABBE CLI: NO
        "mix",                  # Enter PM manually for 'Other' languages
        "7",                    # Agents: Gemini
    ]
    with patch('builtins.input', side_effect=inputs):
        init.main()
    p = temp_project
    agents_md = (p / "agents" / "AGENTS.md").read_text()
    assert 'install: "mix install"' in agents_md

def test_reinstallation(temp_project):
    agents_dir = temp_project / "agents"
    agents_dir.mkdir(parents=True)
    (agents_dir / "foo.txt").write_text("bar")
    (agents_dir / "AGENTS.md").write_text("custom user agents")
    inputs = [
        "1",                    # Local, points to temp_project/agents which already exists
        "y",                    # Merge kit files? Yes (dirs_exist_ok=True logic)
        "",                     # Name
        "",                     # Desc
        "1",                    # Team: Solo
        "1",                    # Type: Greenfield
        "3",                    # Python
        "",                     # Framework
        "6",                    # DB
        "7",                    # Cloud
        "n",                    # Dynamic
        "n",                    # Analytics
        "n",                    # Meta
        "n",                    # GABBE CLI: NO
        "7",                    # Gemini
    ]
    with patch('builtins.input', side_effect=inputs):
        init.main()
    # Given the new logic `dirs_exist_ok=True` or the Python < 3.8 fallback,
    # foo.txt should STILL exist because we only overwrite files that match SOURCE_AGENTS_DIR files.
    assert (agents_dir / "foo.txt").exists()
    assert (agents_dir / "AGENTS.md").read_text() == "custom user agents"

def test_install_global_first_time(temp_project):
    global_target = Path.home() / "agents"
    # We need to mock Path.home() so we don't pollute the actual user home dir in tests
    with patch('pathlib.Path.home', return_value=temp_project / "mock_home"):
        inputs = [
            "2",                    # Global
            "",                     # Name
            "",                     # Desc
            "1",                    # Team: Solo
            "1",                    # Type: Greenfield
            "3",                    # Python
            "",                     # Framework
            "6",                    # DB
            "7",                    # Cloud
            "n",                    # Dynamic
            "n",                    # Analytics
            "n",                    # Meta
            "n",                    # GABBE CLI: NO
            "7",                    # Gemini
        ]
        with patch('builtins.input', side_effect=inputs):
            init.main()
        
        expected_target = temp_project / "mock_home" / "agents"
        assert expected_target.exists()
        assert (expected_target / "AGENTS.md").exists()

def test_update_global(temp_project):
    with patch('pathlib.Path.home', return_value=temp_project / "mock_home"):
        global_target = temp_project / "mock_home" / "agents"
        global_target.mkdir(parents=True)
        (global_target / "user_custom_file.txt").write_text("should_not_be_deleted")
        (global_target / "CONSTITUTION.md").write_text("my custom rules")
        mem_dir = global_target / "memory" / "episodic"
        mem_dir.mkdir(parents=True)
        (mem_dir / "SESSION_SNAPSHOT.md").write_text("mem")
        
        proj_dir = global_target / "project"
        proj_dir.mkdir(parents=True)
        (proj_dir / "TASKS.md").write_text("my custom tasks")
        (proj_dir / "policies.yml").write_text("my custom policy")
        
        inputs = [
            "2",                    # Global
            "y",                    # Merge kit files? Yes
            "",                     # Name
            "",                     # Desc
            "1",                    # Team: Solo
            "1",                    # Type: Greenfield
            "3",                    # Python
            "",                     # Framework
            "6",                    # DB
            "7",                    # Cloud
            "n",                    # Dynamic
            "n",                    # Analytics
            "n",                    # Meta
            "n",                    # GABBE CLI: NO
            "7",                    # Gemini
        ]
        with patch('builtins.input', side_effect=inputs):
            init.main()
            
        assert global_target.exists()
        assert (global_target / "AGENTS.md").exists()
        assert (global_target / "user_custom_file.txt").exists()
        assert (global_target / "CONSTITUTION.md").read_text() == "my custom rules"
        assert (mem_dir / "SESSION_SNAPSHOT.md").read_text() == "mem"
        assert (proj_dir / "TASKS.md").read_text() == "my custom tasks"
        assert (proj_dir / "policies.yml").read_text() == "my custom policy"

def test_install_custom_first_time(temp_project):
    custom_target = temp_project / "custom_agents_dir"
    inputs = [
        "3",                    # Custom Path
        str(custom_target),     # The path (not ending in 'agents', so agents/ is appended)
        "",                     # Name
        "",                     # Desc
        "1",                    # Team: Solo
        "1",                    # Type: Greenfield
        "3",                    # Python
        "",                     # Framework
        "6",                    # DB
        "7",                    # Cloud
        "n",                    # Dynamic
        "n",                    # Analytics
        "n",                    # Meta
        "n",                    # GABBE CLI: NO
        "7",                    # Gemini
    ]
    with patch('builtins.input', side_effect=inputs):
        init.main()
    
    agents_dir = custom_target / "agents"
    assert custom_target.exists()
    assert agents_dir.exists()
    assert (agents_dir / "AGENTS.md").exists()
    assert (agents_dir / "skills").exists()
    assert (agents_dir / "templates").exists()
    assert (agents_dir / "guides").exists()
    assert (agents_dir / "personas").exists()
    assert (agents_dir / "memory").exists()
    # Wiring goes into custom_target (PROJECT_ROOT)
    assert (custom_target / ".gemini").exists()

def test_update_custom(temp_project):
    custom_target = temp_project / "custom_agents_dir"
    custom_agents = custom_target / "agents"
    custom_agents.mkdir(parents=True)
    (custom_agents / "user_data.json").write_text('{"key": "value"}')
    (custom_agents / "project").mkdir()
    (custom_agents / "project" / "TASKS.md").write_text('my tasks')
    
    inputs = [
        "3",                    # Custom Path
        str(custom_target),     # The path (not ending in 'agents', so agents/ appended)
        "y",                    # Merge kit files? Yes
        "",                     # Name
        "",                     # Desc
        "1",                    # Team: Solo
        "1",                    # Type: Greenfield
        "3",                    # Python
        "",                     # Framework
        "6",                    # DB
        "7",                    # Cloud
        "n",                    # Dynamic
        "n",                    # Analytics
        "n",                    # Meta
        "n",                    # GABBE CLI: NO
        "7",                    # Gemini
    ]
    with patch('builtins.input', side_effect=inputs):
        init.main()
        
    assert custom_agents.exists()
    assert (custom_agents / "AGENTS.md").exists()
    assert (custom_agents / "user_data.json").exists()
    assert (custom_agents / "project" / "TASKS.md").read_text() == 'my tasks'

def test_missing_source_directory(temp_project):
    init.SOURCE_AGENTS_DIR = init.KIT_SOURCE / "invalid_non_existent"
    with pytest.raises(SystemExit) as e:
        init.main()
    assert e.value.code == 1

def test_same_source_and_target_directory(temp_project):
    # Simulate running the kit inside the source folder itself
    init.SOURCE_AGENTS_DIR = temp_project / "agents"
    init.SOURCE_AGENTS_DIR.mkdir(parents=True)
    # create required directories to pass early validation
    for subdir in ["guides", "skills", "templates", "personas", "memory", "scripts"]:
        (init.SOURCE_AGENTS_DIR / subdir).mkdir(parents=True, exist_ok=True)
        
    (init.SOURCE_AGENTS_DIR / "foo.txt").write_text("bar")
    
    inputs = [
        "1",                    # Local, points to temp_project/agents which IS SOURCE_AGENTS_DIR
        # NO prompt for Overwrite/Merge because it skips!
        "",                     # Name
        "",                     # Desc
        "1",                    # Team: Solo
        "1",                    # Type: Greenfield
        "3",                    # Python
        "",                     # Framework
        "6",                    # DB
        "7",                    # Cloud
        "n",                    # Dynamic
        "n",                    # Analytics
        "n",                    # Meta
        "n",                    # GABBE CLI: NO
        "7",                    # Gemini
    ]
    with patch('builtins.input', side_effect=inputs):
        init.main()
    
    # Should complete without throwing SameFileError and foo.txt should still exist
    assert (init.SOURCE_AGENTS_DIR / "foo.txt").exists()


def test_setup_context_sh_only_on_linux(temp_project):
    """On Linux/macOS, only setup-context.sh is installed (not .ps1)."""
    inputs = [
        "1",  # Local
        "",   # Name
        "",   # Desc
        "1",  # Team
        "1",  # Greenfield
        "3",  # Python
        "",   # Framework
        "6",  # DB: None
        "7",  # Cloud: On-Prem
        "n",  # Dynamic
        "n",  # Analytics
        "n",  # Meta
        "n",  # GABBE CLI: NO
        "7",  # Gemini
    ]
    with patch("sys.platform", "linux"), \
         patch("builtins.input", side_effect=inputs):
        init.main()

    assert (temp_project / "setup-context.sh").exists()
    assert not (temp_project / "setup-context.ps1").exists()


def test_setup_context_ps1_only_on_windows(temp_project):
    """On Windows, only setup-context.ps1 is installed (not .sh)."""
    inputs = [
        "1",  # Local
        "",   # Name
        "",   # Desc
        "1",  # Team
        "1",  # Greenfield
        "3",  # Python
        "",   # Framework
        "6",  # DB: None
        "7",  # Cloud: On-Prem
        "n",  # Dynamic
        "n",  # Analytics
        "n",  # Meta
        "n",  # GABBE CLI: NO
        "7",  # Gemini
    ]
    with patch("sys.platform", "win32"), \
         patch("builtins.input", side_effect=inputs):
        init.main()

    assert (temp_project / "setup-context.ps1").exists()
    assert not (temp_project / "setup-context.sh").exists()
