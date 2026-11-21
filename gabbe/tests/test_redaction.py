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

GH_PAT = "github_pat_" + "11ABCDEFG0" + "x" * 30
NPM = "npm_" + "a1B2c3D4e5" * 4
GLPAT = "glpat-" + "abcdefghij" * 2
HF = "hf_" + "aB3dE5gH7j" * 4
STRIPE = "sk_" + "live_" + "a1B2c3D4e5f6g7H8"
B64 = "dXNlcjpGQUtFUEFTU1dPUkQ="
OPENSSH = (
    "-----BEGIN "
    + "OPENSSH PRIVATE KEY-----\n"
    + "b3Bl" * 20
    + "\n-----END "
    + "OPENSSH PRIVATE KEY-----"
)

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
    ("before\n" + OPENSSH + "\nafter", "b3Bl", "after"),
    # RA-10: header forms
    ("Authorization: Basic " + B64, B64, "Authorization: Basic"),
    ("Authorization: Bearer abc.def-" + A, A, "Authorization: Bearer"),
    ('"Authorization": "Bearer ' + A + '"', A, "Authorization"),
    # RA-10: password inside a URL (only the password goes)
    ("postgres://app:" + A + "@db:5432/app", A, "postgres://app:"),
    ("postgresql://app:" + A + "@db.example.com/x", A, "postgresql://app:"),
    ("mysql://root:" + A + "@db/x", A, "mysql://root:"),
    ("mongodb://u:" + A + "@h1:27017,h2/x", A, "mongodb://u:"),
    ("mongodb+srv://u:" + A + "@cluster0.example.net/x", A, "mongodb+srv://u:"),
    ("redis://:" + A + "@cache:6379/0", A, "redis://:"),
    ("amqp://guest:" + A + "@mq:5672/", A, "amqp://guest:"),
    # RA-10: command-line options
    ("tool --password " + A, A, "--password"),
    ("tool --password=" + A, A, "--password="),
    ("tool --token " + A, A, "--token"),
    ("tool --token=" + A, A, "--token="),
    ("tool --api-key " + A + " run", A, "--api-key"),
    ("tool --api-key=" + A, A, "--api-key="),
    ("tool --password 'two words " + A + "' run", A, "--password"),
    # RA-10: JSON members (value replaced, key kept, spaces inside the value too)
    ('{"password": "' + A + ' tail"}', "tail", '"password"'),
    ('{"apiKey": "' + A + '"}', A, '"apiKey"'),
    ('{"secret": "' + A + '"}', A, '"secret"'),
    ('{"token": "' + A + '"}', A, '"token"'),
    ('{"access_token": "' + A + '"}', A, '"access_token"'),
    ('{"refresh_token": "' + A + '"}', A, '"refresh_token"'),
    ('{"client_secret": "' + A + '"}', A, '"client_secret"'),
    # RA-10: token prefixes
    ("t " + GH_PAT + " e", GH_PAT, "t"),
    ("t gho_" + A + " e", A, "t"),
    ("t ghu_" + A + " e", A, "t"),
    ("t ghs_" + A + " e", A, "t"),
    ("t ghr_" + A + " e", A, "t"),
    ("t " + NPM + " e", NPM, "t"),
    ("t " + GLPAT + " e", GLPAT, "t"),
    ("t " + HF + " e", HF, "t"),
    ("t " + STRIPE + " e", STRIPE, "t"),
    ("t ASIA" + "A1B2C3D4E5F6G7H8 e", "A1B2C3D4E5F6", "t"),
    ("AccountKey=" + "abcd1234" * 4 + ";", "abcd1234", "AccountKey="),
    ("https://hooks.slack.com/services/T0000000/B0000000/" + A, A, "https://"),
    ("pwd=" + A, A, "pwd="),
    ("passphrase: " + A, A, "passphrase:"),
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
        "the Authorization header carries the credentials",
        "send Authorization: none when anonymous",
        "see https://example.com/docs and ftp://files.example.org/pub",
        "postgres://db:5432/app has no password",
        "run the tool with --password-file path or --token-url x",
        "the --verbose flag, then --output file",
        "use npm_config_cache for the cache",
        "github_pat is the prefix of fine-grained tokens",
        "glpat- alone is not a token",
        'a JSON key "tokens_per_minute" stays; "name": "plain value"',
        "the secretary and the tokenizer passed",
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

# RA-10: 100 kB of adversarial text per new shape, each under 1 s through every pattern.
BIG = 100_000
ADVERSARIAL_100KB = {
    "authorization": [
        "Authorization:" + " " * BIG,
        "authorization: basic " + "A" * BIG,
        "Authorization:" * 7000,
    ],
    "url": [
        "a://" * 25000,
        "x://" + "u" * BIG,
        "x://u:" + "p" * BIG,
        "x://:" * 20000,
        "a.a." * 25000,
    ],
    "option": [
        "--password " * 9000,
        "--token=" * 12000,
        "--api-key '" + "a" * BIG,
        "--token " + " " * BIG,
    ],
    "json": [
        '"password":"' * 8000,
        '"token": "' + "a" * BIG,
        '"secret": "' + "\\a" * 30000,
        '"' * BIG,
    ],
    "prefix": [
        "github_pat_" * 9000,
        "npm_" + "a" * BIG,
        "glpat-" * 16000,
        "hf_" + "a" * BIG,
        "sk_live_" * 12000,
    ],
    "other": [
        "AccountKey=" * 9000,
        "hooks.slack.com/services/" * 4000,
        "ASIA" * 25000,
        "pwd=" * 25000,
    ],
}


@pytest.mark.parametrize("shape", sorted(ADVERSARIAL_100KB))
def test_each_ra10_shape_is_linear_on_100kb_of_hostile_input(shape):
    for text in ADVERSARIAL_100KB[shape]:
        started = time.perf_counter()
        _redact_text(text)
        assert time.perf_counter() - started < 1.0, (shape, text[:20])


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
