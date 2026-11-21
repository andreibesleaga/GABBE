# SPDX-License-Identifier: Apache-2.0
"""A project `.env` may set ordinary GABBE settings, never security switches.

A `.env` travels with a repository. These tests pin what a cloned repository's
`.env` can and cannot change (release 1.1.4).
"""

import logging
import os
import time
from unittest.mock import patch

from gabbe.config import PII_PATTERNS, _load_env_file


def _load(tmp_path, text, real_env=None):
    """Load a .env with `text` into a clean environment; return that environment."""
    env_file = tmp_path / ".env"
    env_file.write_text(text)
    with patch.dict(os.environ, real_env or {}, clear=True):
        _load_env_file(env_file)
        return dict(os.environ)


def test_allowed_keys_are_loaded(tmp_path):
    env = _load(
        tmp_path,
        "# comment\nGABBE_API_KEY='k1'\nGABBE_API_MODEL=m1\nGABBE_LLM_TIMEOUT=9\n"
        "GABBE_MAX_ITERATIONS=3\n",
    )
    assert env == {
        "GABBE_API_KEY": "k1",
        "GABBE_API_MODEL": "m1",
        "GABBE_LLM_TIMEOUT": "9",
        "GABBE_MAX_ITERATIONS": "3",
    }


def test_real_environment_wins(tmp_path):
    env = _load(tmp_path, "GABBE_API_MODEL=from-file\n", {"GABBE_API_MODEL": "from-shell"})
    assert env["GABBE_API_MODEL"] == "from-shell"


def test_tool_server_switches_are_never_read(tmp_path, caplog):
    with caplog.at_level(logging.WARNING, logger="gabbe.config"):
        env = _load(
            tmp_path,
            "GABBE_MCP_INSECURE=1\nGABBE_MCP_ALLOWED_COMMANDS=sh\nGABBE_MCP_TOKEN=t\n"
            "GABBE_POLICY_FILE=../x.yml\n",
        )
    assert env == {}
    assert "GABBE_MCP_INSECURE" in caplog.text
    assert "GABBE_POLICY_FILE" in caplog.text


def test_non_gabbe_variables_are_ignored_silently(tmp_path, caplog):
    with caplog.at_level(logging.WARNING, logger="gabbe.config"):
        env = _load(tmp_path, "PATH=/evil\nPYTHONPATH=/evil\nDATABASE_URL=postgres://x\n")
    assert env == {}
    assert caplog.text == ""


def test_api_url_is_read_when_the_key_is_in_the_same_file(tmp_path):
    env = _load(tmp_path, "GABBE_API_URL=http://localhost:11434/v1\nGABBE_API_KEY=k\n")
    assert env["GABBE_API_URL"] == "http://localhost:11434/v1"


def test_api_url_is_read_when_there_is_no_key_at_all(tmp_path):
    env = _load(tmp_path, "GABBE_API_URL=http://localhost:11434/v1\n")
    assert env["GABBE_API_URL"] == "http://localhost:11434/v1"


def test_api_url_is_refused_when_the_key_comes_from_the_shell(tmp_path, caplog):
    """Otherwise a cloned repository could send the user's own key to its URL."""
    with caplog.at_level(logging.WARNING, logger="gabbe.config"):
        env = _load(
            tmp_path, "GABBE_API_URL=https://attacker.example/v1\n", {"GABBE_API_KEY": "mine"}
        )
    assert "GABBE_API_URL" not in env
    assert "GABBE_API_URL" in caplog.text


def test_warning_names_keys_not_values(tmp_path, caplog):
    with caplog.at_level(logging.WARNING, logger="gabbe.config"):
        _load(tmp_path, "GABBE_MCP_TOKEN=super-secret-value\n")
    assert "super-secret-value" not in caplog.text


def test_missing_file_is_a_no_op(tmp_path):
    with patch.dict(os.environ, {}, clear=True):
        _load_env_file(tmp_path / "absent.env")
        assert dict(os.environ) == {}


def test_email_redaction_is_linear_on_long_input():
    """The unbounded pattern took about 8 s on 40 kB; the bounded one is milliseconds."""
    started = time.perf_counter()
    PII_PATTERNS[0].sub("x", "a" * 40_000)
    assert time.perf_counter() - started < 2.0
    assert PII_PATTERNS[0].sub("<E>", "mail john.doe+tag@example.co.uk now") == "mail <E> now"
