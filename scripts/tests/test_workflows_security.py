"""Static checks on the GitHub workflows: pinned actions, one release gate, least privilege.

Reads `.github/workflows/*.yml` only (no network, no clock). These are the rules from the
1.2.0 pre-release audit: a workflow edit that breaks one of them fails here before a tag.
"""

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
GATE_FILE = "./.github/workflows/gate.yml"
PUBLISHING_WORKFLOWS = ["release.yml", "publish-npm.yml", "publish-github-packages.yml"]
# Steps that attach release assets or publish a package.
PUBLISHING_ACTIONS = ("softprops/action-gh-release@", "pypa/gh-action-pypi-publish@")
PUBLISHING_COMMANDS = ("npm publish", "twine upload")
PINNED_USES = re.compile(r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}\s+#\s*\S+")


def _files():
    return sorted(WORKFLOWS.glob("*.yml"))


def _load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _triggers(doc):
    # PyYAML reads the bare key `on` as the boolean True.
    on = doc.get("on", doc.get(True))
    if isinstance(on, str):
        return {on}
    return set(on or [])


def _steps(job):
    return job.get("steps") or []


def _is_publishing(job):
    for step in _steps(job):
        if str(step.get("uses", "")).startswith(PUBLISHING_ACTIONS):
            return True
        if any(cmd in str(step.get("run", "")) for cmd in PUBLISHING_COMMANDS):
            return True
    return False


def _needs(job):
    needs = job.get("needs") or []
    return [needs] if isinstance(needs, str) else list(needs)


def _depends_on(jobs, name, target_ok):
    """True when job `name` needs, directly or through other jobs, a job satisfying target_ok."""
    seen, todo = set(), _needs(jobs[name])
    while todo:
        dep = todo.pop()
        if dep in seen:
            continue
        seen.add(dep)
        if target_ok(jobs[dep]):
            return True
        todo.extend(_needs(jobs[dep]))
    return False


def _is_gate_call(job):
    return job.get("uses") == GATE_FILE


def test_workflow_files_are_found():
    assert (WORKFLOWS / "gate.yml").exists()
    assert len(_files()) >= 8


def test_scorecard_analysis_publishes_and_uploads_sarif():
    job = _load(WORKFLOWS / "scorecard.yml")["jobs"]["analysis"]
    steps = _steps(job)
    analysis = next(s for s in steps if s.get("name") == "Run analysis")
    assert analysis["uses"].startswith("ossf/scorecard-action@")
    assert analysis["with"] == {
        "results_file": "results.sarif",
        "results_format": "sarif",
        "publish_results": True,
    }
    artifact = next(s for s in steps if s.get("name") == "Upload artifact")
    code_scanning = next(s for s in steps if s.get("name") == "Upload to code-scanning")
    assert artifact["with"]["path"] == analysis["with"]["results_file"]
    assert code_scanning["with"]["sarif_file"] == analysis["with"]["results_file"]


@pytest.mark.parametrize("path", _files(), ids=lambda p: p.name)
def test_every_uses_is_pinned_to_a_commit_sha_with_a_version_comment(path):
    bad = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = re.match(r"^\s*(?:-\s+)?uses:\s*(\S.*)$", line)
        if not match:
            continue
        value = match.group(1)
        if value.startswith("./.github/workflows/"):
            continue  # a reusable workflow in this repository
        if not PINNED_USES.match(value):
            bad.append(f"{path.name}:{number}: {value}")
    assert not bad, "unpinned actions:\n" + "\n".join(bad)


@pytest.mark.parametrize("path", _files(), ids=lambda p: p.name)
def test_no_pull_request_target(path):
    assert "pull_request_target" not in _triggers(_load(path))


@pytest.mark.parametrize("path", _files(), ids=lambda p: p.name)
def test_no_run_block_interpolates_event_text(path):
    bad = []
    for name, job in (_load(path).get("jobs") or {}).items():
        for step in _steps(job):
            run = str(step.get("run", ""))
            if "${{ github.event." in run or "${{ github.head_ref" in run:
                bad.append(f"{path.name}: job {name}: {run.strip()[:60]}")
    assert not bad, "event text inside run: blocks (pass it through env:):\n" + "\n".join(bad)


def test_release_has_workflow_level_read_only_permissions():
    assert _load(WORKFLOWS / "release.yml").get("permissions") == {"contents": "read"}


def test_release_write_access_is_job_level_only_on_asset_jobs():
    jobs = _load(WORKFLOWS / "release.yml")["jobs"]
    writers = {
        n for n, j in jobs.items() if (j.get("permissions") or {}).get("contents") == "write"
    }
    attaching = {
        n
        for n, j in jobs.items()
        if any(str(s.get("uses", "")).startswith("softprops/") for s in _steps(j))
    }
    assert writers == attaching and writers


@pytest.mark.parametrize("name", PUBLISHING_WORKFLOWS)
def test_every_publishing_job_depends_on_the_gate(name):
    jobs = _load(WORKFLOWS / name)["jobs"]
    publishing = [n for n, j in jobs.items() if _is_publishing(j)]
    assert publishing, f"{name} has no publishing job: update this test if that is intended"
    for job in publishing:
        assert _depends_on(jobs, job, _is_gate_call), f"{name}: job {job} can run without the gate"


@pytest.mark.parametrize("name", ["publish-npm.yml", "publish-github-packages.yml"])
def test_manual_runs_of_the_npm_workflows_need_a_version_tag(name):
    doc = _load(WORKFLOWS / name)
    jobs = doc["jobs"]
    assert "workflow_dispatch" in _triggers(doc)
    guard = jobs["require-tag"]
    assert "github.ref_type" in str(guard["steps"])
    for job in (n for n, j in jobs.items() if _is_publishing(j)):
        assert "require-tag" in _needs(jobs[job])


def test_gate_is_a_reusable_workflow_with_a_ref_input_and_read_only_token():
    doc = _load(WORKFLOWS / "gate.yml")
    assert "workflow_call" in _triggers(doc)
    on = doc.get("on", doc.get(True))
    assert on["workflow_call"]["inputs"]["ref_name"]["required"] is True
    assert doc["permissions"] == {"contents": "read"}


def test_gate_checks_every_version_file_that_exists():
    text = (WORKFLOWS / "gate.yml").read_text(encoding="utf-8")
    checked = ["pyproject.toml", "gabbe/__init__.py", "package.json", "server.json", "CITATION.cff"]
    missing = [f for f in checked if (ROOT / f).exists() and f not in text]
    assert not missing, f"gate.yml does not check: {missing}"
    # server.json carries the version twice.
    if (ROOT / "server.json").exists():
        assert "packages" in text


def test_gate_can_also_be_run_by_hand_as_a_dry_run():
    """`workflow_dispatch` with the same required `ref_name` input as `workflow_call`, both
    feeding the one TAG_NAME the version step reads."""
    path = WORKFLOWS / "gate.yml"
    doc = _load(path)
    assert {"workflow_call", "workflow_dispatch"} <= _triggers(doc)
    on = doc.get("on", doc.get(True))
    assert (
        on["workflow_dispatch"]["inputs"]["ref_name"] == on["workflow_call"]["inputs"]["ref_name"]
    )
    steps = _steps(doc["jobs"]["release-gate"])
    version_step = next(s for s in steps if s.get("name") == "Tag equals every version number")
    assert version_step["env"]["TAG_NAME"] == "${{ inputs.ref_name }}"
    assert "publishes nothing" in path.read_text(encoding="utf-8")


def test_gate_checks_the_version_line_of_the_four_bootstrap_scripts():
    text = (WORKFLOWS / "gate.yml").read_text(encoding="utf-8")
    for script in ("install.sh", "uninstall.sh", "install.ps1", "uninstall.ps1"):
        assert f'"{script}"' in text, f"gate.yml does not check {script}"
    assert "GABBE_KIT_DEFAULT_VERSION" in text and "GabbeKitDefaultVersion" in text


def test_gate_installs_from_the_hashed_lock():
    text = (WORKFLOWS / "gate.yml").read_text(encoding="utf-8")
    assert "pip install --require-hashes -r requirements-lock.txt" in text
    assert "pip install --no-deps -e ." in text


def test_pypi_job_fails_instead_of_skipping_and_holds_only_oidc_and_read():
    job = _load(WORKFLOWS / "release.yml")["jobs"]["publish-pypi"]
    assert "if" not in job, "a job-level if could end the release green without a PyPI upload"
    assert job["permissions"] == {"contents": "read", "id-token": "write"}
    assert job.get("environment") == "pypi"
    uses = [str(s.get("uses", "")) for s in _steps(job)]
    assert any(u.startswith("pypa/gh-action-pypi-publish@") for u in uses)


def test_npm_publish_job_keeps_the_registered_workflow_and_has_no_environment():
    # The trusted publisher on npmjs.com is registered for this file name, without an environment.
    job = _load(WORKFLOWS / "publish-npm.yml")["jobs"]["publish-npm"]
    assert "environment" not in job
    assert job["permissions"]["id-token"] == "write"
