# SPDX-License-Identifier: Apache-2.0
"""Audit redaction shapes and private file modes (SEC-C-08).

Fake secrets are built from pieces so that no secret scanner flags this file."""

import os
import stat
import time

import pytest

from gabbe.audit import _redact_text
from gabbe.config import PII_PATTERNS, SECRET_PATTERNS

A = "A" * 20
SLACK = "xox" + "b-" + "1234567890-" + "abcdefghij"
GOOGLE = "AI" + "za" + "Sy" + "B" * 33
JWT = ".".join(["ey" + "J" + "hbGciOiJIUzI1NiJ9", "ey" + "J" + "zdWIiOiIxMjM0In0", "c2lnbmF0dXJl"])
PEM = "-----BEGIN " + "PRIVATE KEY-----\n" + "MIIB" * 20 + "\n-----END " + "PRIVATE KEY-----"
RSA_PEM = PEM.replace("BEGIN ", "BEGIN RSA ").replace("END ", "END RSA ")

# (text, the secret value that must be gone, the part that must stay)
CASES = [
    ("OPENAI_API_KEY=" + A, A, "OPENAI_API_KEY="),
    ("AWS_SECRET_ACCESS_KEY=" + A, A, "AWS_SECRET_ACCESS_KEY="),
    ("GABBE_MCP_TOKEN=tok-" + A, A, "GABBE_MCP_TOKEN="),
    ("DB_PASSWORD: hunter2" + A, A, "DB_PASSWORD:"),
    ('{"api_key": "' + A + '"}', A, "api_key"),
    ("password = " + A, A, "password ="),
    ("send " + SLACK + " now", SLACK, "send"),
    ("key " + GOOGLE + " here", GOOGLE, "key"),
    ("jwt " + JWT + " end", JWT, "jwt"),
    ("before\n" + PEM + "\nafter", "MIIB", "before"),
    ("before\n" + RSA_PEM + "\nafter", "MIIB", "after"),
]


@pytest.mark.parametrize(("text", "gone", "kept"), CASES)
def test_secret_shapes_are_redacted_and_the_name_is_kept(text, gone, kept):
    out = _redact_text(text)
    assert gone not in out
    assert kept in out
    assert "[REDACTED]" in out


@pytest.mark.parametrize(
    "prose",
    [
        "the token is refreshed every hour",
        "secret santa is on Friday",
        "reset your password at the help desk",
        "api key rotation policy",
        "a JSON web token has three parts",
        "xox is not a token",
        "-----BEGIN CERTIFICATE----- is public",
    ],
)
def test_ordinary_prose_is_left_alone(prose):
    assert _redact_text(prose) == prose


SLOW_INPUTS = {
    "assignment": ["token" * 8000, "a_" * 20000, "token " + " " * 40000, "x=" * 20000],
    "slack": ["xoxb-" * 8000, "xoxb-" + "a" * 40000],
    "google": ["AIza" * 10000, "AIza" + "a" * 40000],
    "jwt": ["eyJ" * 13000, "eyJ" + "a" * 40000, "eyJaaaaa." * 5000],
    "pem": ["-----BEGIN PRIVATE KEY-----" * 1500, "-----BEGIN PRIVATE KEY-----" + "A" * 40000],
}


def _pattern_for(name):
    pats = list(PII_PATTERNS) + list(SECRET_PATTERNS)
    sample = {
        "assignment": "OPENAI_API_KEY=x",
        "slack": SLACK,
        "google": GOOGLE,
        "jwt": JWT,
        "pem": PEM,
    }[name]
    return [p for p in pats if p.search(sample)]


@pytest.mark.parametrize("name", sorted(SLOW_INPUTS))
def test_each_new_pattern_is_linear_on_40kb_of_hostile_input(name):
    patterns = _pattern_for(name)
    assert patterns, f"no pattern matches the {name} sample"
    for text in SLOW_INPUTS[name]:
        started = time.perf_counter()
        for pat in patterns:
            pat.sub("x", text)
        assert time.perf_counter() - started < 2.0, (name, text[:20])


@pytest.mark.skipif(os.name == "nt", reason="no POSIX modes on Windows")
def test_logs_folder_is_0700_and_state_files_are_0600(tmp_project):
    from gabbe import database
    from gabbe.audit import AuditTracer

    database.init_db()
    tracer = AuditTracer("run-modes", db_conn=database.get_db())
    span = tracer.start_span("tool", "t", {"command": "echo hi"})
    tracer.end_span(span, output_data={"stdout": "hi"})
    logs = tmp_project / "project" / "logs"
    assert stat.S_IMODE(logs.stat().st_mode) == 0o700
    assert stat.S_IMODE((tmp_project / "project" / "state.db").stat().st_mode) == 0o600
    jsonl = logs / "run_run-modes.jsonl"
    assert jsonl.exists() and stat.S_IMODE(jsonl.stat().st_mode) == 0o600


@pytest.mark.skipif(os.name == "nt", reason="no POSIX modes on Windows")
def test_a_file_that_exists_keeps_its_mode(tmp_project):
    from gabbe import database

    db = tmp_project / "project" / "state.db"
    db.write_bytes(b"")
    db.chmod(0o644)
    database.init_db()
    assert stat.S_IMODE(db.stat().st_mode) == 0o644
