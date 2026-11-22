# SPDX-License-Identifier: Apache-2.0
"""Property tests for the project `.env` loader in `gabbe/config.py` (assurance ladder level 1).

A `.env` file travels with a repository, so it must never widen what a cloned
repository can do: only allow-listed keys are read, the user's real environment always
wins, the API URL cannot be redirected while the key comes from the real environment,
and the warning about refused keys never prints a value.
"""

import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from hypothesis import given, settings
from hypothesis import strategies as st

from gabbe import config

_SETTINGS = settings(max_examples=100, derandomize=True, deadline=None, database=None)

_KEYS = [
    "GABBE_API_KEY",
    "GABBE_API_URL",
    "GABBE_API_MODEL",
    "GABBE_LLM_CACHE",
    "GABBE_MAX_TOKENS",
    "GABBE_MCP_ALLOW_ALL",
    "GABBE_POLICY_FILE",
    "GABBE_ROUTE_THRESHOLD",
    "PATH",
    "PYTHONPATH",
    "HOME",
    "SOMETHING_ELSE",
]
_key = st.one_of(st.sampled_from(_KEYS), st.text(alphabet="ABCGLMX_", min_size=1, max_size=10))
# Values start with a marker no key contains, so a leak is easy to see.
_value = st.builds(
    lambda n, tail: "sEcReT%d%s" % (n, tail),
    st.integers(0, 999),
    st.sampled_from(["", "#x", " y", "'q'", '"dq"']),
)
_line = st.one_of(
    st.builds(lambda k, v: f"{k}={v}", _key, _value),
    st.builds(lambda k, v: f"  {k} = {v}  ", _key, _value),
    st.builds(lambda c: f"# {c}", st.text(alphabet="ab =", max_size=8)),
    st.just(""),
    st.text(alphabet="abc =#", max_size=12),
)
_env_text = st.builds(
    lambda lines, nl: nl.join(lines) + nl,
    st.lists(_line, max_size=10),
    st.sampled_from(["\n", "\r\n"]),
)
_real_env = st.dictionaries(
    st.sampled_from(_KEYS), st.sampled_from(["real1", "real2", ""]), max_size=6
)


class _Capture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


def _load(text, real):
    """Run the loader on `text` with `real` as the whole environment.

    Returns (environment after, log messages)."""
    handler = _Capture()
    logger = config.logger
    logger.addHandler(handler)
    old_level = logger.level
    logger.setLevel(logging.DEBUG)
    try:
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, real, clear=True):
            path = Path(d) / ".env"
            path.write_bytes(text.encode("utf-8"))  # exact bytes; newline= needs 3.10
            config._load_env_file(path)
            return dict(os.environ), handler.messages
    finally:
        logger.removeHandler(handler)
        logger.setLevel(old_level)


@given(_env_text, _real_env)
@_SETTINGS
def test_a_key_outside_the_allow_list_never_reaches_the_environment(text, real):
    """Every variable the loader adds is allow-listed (or is the API URL, which has its
    own rule): PATH, PYTHONPATH, the tool-server switches and the policy file never come
    from a `.env`."""
    after, _ = _load(text, real)
    for key in set(after) - set(real):
        assert config._env_file_key_allowed(key) or key == "GABBE_API_URL", key


@given(_env_text, _real_env)
@_SETTINGS
def test_a_real_environment_value_is_never_replaced(text, real):
    """A variable already in the real environment keeps its value."""
    after, _ = _load(text, real)
    for key, value in real.items():
        assert after[key] == value


@given(_env_text, _real_env)
@_SETTINGS
def test_api_url_is_not_taken_from_the_file_when_the_key_is_in_the_real_environment(text, real):
    """With GABBE_API_KEY exported, a `.env` cannot set GABBE_API_URL (it could send the
    user's key anywhere)."""
    real = dict(real, GABBE_API_KEY="real-key")
    real.pop("GABBE_API_URL", None)
    after, _ = _load(text, real)
    assert "GABBE_API_URL" not in after


@given(_env_text, _real_env)
@_SETTINGS
def test_the_warning_never_contains_a_value(text, real):
    """The log message that lists refused keys names keys only, never a value."""
    _, messages = _load(text, real)
    for message in messages:
        assert "sEcReT" not in message


@given(_env_text)
@_SETTINGS
def test_loading_twice_gives_the_same_environment(text):
    """Loading is idempotent: a second load adds and changes nothing."""
    real = {"HOME": "h"}
    first, _ = _load(text, real)
    with patch.dict(os.environ, first, clear=True):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / ".env"
            path.write_bytes(text.encode("utf-8"))  # exact bytes; newline= needs 3.10
            config._load_env_file(path)
            assert dict(os.environ) == first


@given(_env_text)
@_SETTINGS
def test_parse_returns_stripped_pairs_without_comments(text):
    """Parsed pairs have no comment lines, no blank keys and no surrounding quotes."""
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / ".env"
        path.write_bytes(text.encode("utf-8"))  # exact bytes; newline= needs 3.10
        pairs = config._parse_env_file(path)
    for key, value in pairs.items():
        assert key == key.strip() and not key.startswith("#") and "=" not in key
        assert "\n" not in value and "\r" not in value


def test_missing_file_adds_nothing():
    """A project without a `.env` loads nothing and does not fail."""
    with tempfile.TemporaryDirectory() as d:
        assert config._parse_env_file(Path(d) / ".env") == {}


def test_defect_a_binary_env_file_does_not_crash_the_import():
    """A `.env` holding bytes that are not UTF-8 should be ignored, not crash `import gabbe`."""
    with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {}, clear=True):
        path = Path(d) / ".env"
        path.write_bytes(b"GABBE_API_MODEL=\xff\xfe\n")
        config._load_env_file(path)
        assert "GABBE_API_MODEL" not in os.environ  # a damaged value is never loaded
        assert config._parse_env_file(path) == {}
