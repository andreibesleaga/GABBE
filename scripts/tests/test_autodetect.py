# SPDX-License-Identifier: Apache-2.0
"""Autodetection tests for `gabbe doctor` (Track E8).

Proves the installer/doctor correctly auto-detects the OS/arch, available
runtimes, and agent clients present in a target — the "autodetect all env and
agents and platforms and os" guarantee — deterministically and without any
network or real install.
"""

from gabbe.doctor import (
    AGENT_FINGERPRINTS,
    detect_agents,
    detect_os,
    detect_runtimes,
    run_doctor,
)


def test_detect_os_reports_platform_fields():
    env = detect_os()
    assert env["os"] in {"linux", "macos", "windows"} or env["os"]
    assert env["arch"]  # non-empty machine arch
    assert env["python"].count(".") >= 1


def test_detect_runtimes_finds_the_running_interpreter():
    runtimes = detect_runtimes()
    # We are running under python, so at least one python launcher must be visible.
    assert runtimes["python3"] or runtimes.get("pip")
    assert set(runtimes).issuperset({"node", "npm", "npx", "git", "curl"})


def test_detect_agents_fingerprints_each_client(tmp_path):
    # Plant one fingerprint per known agent and assert all are detected.
    for slug, paths in AGENT_FINGERPRINTS.items():
        target = tmp_path / paths[0]
        if target.suffix:  # a file fingerprint
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("x")
        else:  # a directory fingerprint
            target.mkdir(parents=True, exist_ok=True)
    detected = detect_agents(tmp_path)
    assert detected == sorted(
        AGENT_FINGERPRINTS
    ), f"missed: {set(AGENT_FINGERPRINTS) - set(detected)}"


def test_detect_agents_is_failsoft_on_empty_target(tmp_path):
    # Unknown / absent agents are skipped cleanly — never an error.
    assert detect_agents(tmp_path) == []


def test_detect_agents_partial(tmp_path):
    (tmp_path / ".cursor" / "rules").mkdir(parents=True)
    (tmp_path / "GEMINI.md").write_text("x")
    detected = detect_agents(tmp_path)
    assert "cursor" in detected and "gemini" in detected
    assert "claude" not in detected


def test_run_doctor_is_read_only_and_succeeds(tmp_path):
    # Read-only: returns 0 on a supported interpreter and writes nothing.
    before = set(tmp_path.iterdir())
    assert run_doctor(tmp_path) == 0
    assert set(tmp_path.iterdir()) == before
