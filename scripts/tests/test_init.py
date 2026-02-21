import sys
import os
import shutil
import json
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
        str(global_target),      # Enter path
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
        # Java doesn't ask for PM explicitly 
        "5,6",                   # Agents: Copilot, VS Code
    ]
    with patch('builtins.input', side_effect=inputs):
        init.main()
    p = temp_project
    assert global_target.exists()
    assert (global_target / "AGENTS.md").exists()
    assert (p / "SETUP_MISSION.md").exists()

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
        # Python doesn't ask PM explicitly
        "3",                    # Agents: Gemini
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
        "mix",                  # Enter PM manually for 'Other' languages
        "3",                    # Agents
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
    inputs = [
        "1",                    # Local, points to temp_project/agents which already exists
        "y",                    # Overwrite? Yes
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
        "3",                    # Gemini
    ]
    with patch('builtins.input', side_effect=inputs):
        init.main()
    assert not (agents_dir / "foo.txt").exists()

def test_missing_source_directory(temp_project):
    init.SOURCE_AGENTS_DIR = init.KIT_SOURCE / "invalid_non_existent"
    with pytest.raises(SystemExit) as e:
        init.main()
    assert e.value.code == 1

