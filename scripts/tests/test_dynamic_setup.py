import sys
import os
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import init

# We need to temporarily change CWD to a temp dir so we don't overwrite current project
import tempfile
import shutil

def run_test_scenario(scenario_name, inputs_sequence, expect_bootstrap, expect_setup):
    with tempfile.TemporaryDirectory() as tempdir:
        os.chdir(tempdir)
        init.PROJECT_ROOT = Path(tempdir)
        
        # We need to copy the source AGENTS_DIR to make it available for the script 
        # Actually init.py uses KIT_SOURCE which is based on __file__
        # So SOURCE_AGENTS_DIR should still point to the original GABBE/agents
        
        with patch('builtins.input', side_effect=inputs_sequence):
            try:
                init.main()
            except StopIteration:
                print(f"[{scenario_name}] ERROR: Ran out of inputs in the mock sequence!")
                return False
            except Exception as e:
                print(f"[{scenario_name}] ERROR: Exception occurred: {e}")
                import traceback
                traceback.print_exc()
                return False

        has_bootstrap = (Path(tempdir) / "BOOTSTRAP_MISSION.md").exists()
        has_setup = (Path(tempdir) / "SETUP_MISSION.md").exists()
        
        print(f"[{scenario_name}] BOOTSTRAP_MISSION.md exists: {has_bootstrap}")
        print(f"[{scenario_name}] SETUP_MISSION.md exists: {has_setup}")
        
        success = (has_bootstrap == expect_bootstrap) and (has_setup == expect_setup)
        if success:
            print(f"[{scenario_name}] SUCCESS\n")
        else:
            print(f"[{scenario_name}] FAILED\n")
        return success

def main():
    original_cwd = os.getcwd()

    # Scenario 1: Dynamic ON
    # Expected inputs:
    # Install: 1 (Local)
    # Project Name: "" (Default)
    # Description: "" (Default)
    # Team Size: 1 (Solo)
    # Project Type: 1 (Greenfield)
    # Language: 3 (Python)
    # Framework: "" (None)
    # Databases: 6 (None)
    # Clouds: 7 (On-Prem)
    # Dynamic Setup: y
    # Problem statement: Test problem
    # Analytics: n
    # Meta: n
    # Agents: 3 (Gemini)
    seq_dynamic_on = [
        "1", "", "", "1", "1", "3", "", "6", "7", "y", "Test problem", "n", "n", "3"
    ]
    
    # Scenario 2: Dynamic OFF
    # Same but Dynamic Setup: n, no problem statement required
    seq_dynamic_off = [
        "1", "", "", "1", "1", "3", "", "6", "7", "n", "n", "n", "3"
    ]
    
    try:
        run_test_scenario("Dynamic Setup ON", seq_dynamic_on, expect_bootstrap=True, expect_setup=False)
        # Restore init.py state
        os.chdir(original_cwd)
        run_test_scenario("Dynamic Setup OFF", seq_dynamic_off, expect_bootstrap=False, expect_setup=True)
    finally:
        os.chdir(original_cwd)

if __name__ == "__main__":
    main()
