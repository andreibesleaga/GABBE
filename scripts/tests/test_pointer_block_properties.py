# SPDX-License-Identifier: Apache-2.0
"""Property tests for the instruction-file pointer block and the repository URL cleaner
in `scripts/init.py` (assurance ladder level 1).

The pointer block is appended to the user's own instruction file; removing it must give
the user's bytes back. `gabbe/installer.py` has its own copy of the removal rule, and
the two copies must agree on every input.
"""

import sys
from pathlib import Path
from urllib.parse import urlsplit

from hypothesis import given, settings
from hypothesis import strategies as st

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT))

import init as init_mod  # noqa: E402

from gabbe import installer  # noqa: E402

_SETTINGS = settings(max_examples=200, derandomize=True, deadline=None, database=None)
_KIT = "agents/AGENTS.md"

# Text-like lines: no CR or LF inside a line, no marker.
_line = st.text(alphabet="abc xyz#-*`\t", max_size=12).map(lambda s: s.encode())
_ending = st.sampled_from([b"\n", b"\r\n"])


def _join(lines, ending, trailing):
    body = ending.join(lines)
    return body + ending if trailing else body


_documents = st.builds(_join, st.lists(_line, max_size=6), _ending, st.booleans())
_any_bytes = st.binary(max_size=80).filter(lambda b: b"GABBE-KIT" not in b)


def _trim(data):
    return data.rstrip(b"\r\n")


@given(_documents)
@_SETTINGS
def test_removing_the_block_gives_back_the_file_up_to_trailing_line_ends(data):
    """For text with LF or CRLF endings, removing the block after adding it returns the
    same text; only line ends at the very end may differ."""
    out = init_mod.without_pointer_block(init_mod.with_pointer_block(data, _KIT))
    assert _trim(out) == _trim(data)


@given(_any_bytes)
@_SETTINGS
def test_removing_the_block_round_trips_arbitrary_bytes_up_to_trailing_line_ends(data):
    """The same holds for arbitrary bytes (any encoding), which are never decoded."""
    out = init_mod.without_pointer_block(init_mod.with_pointer_block(data, _KIT))
    assert _trim(out) == _trim(data)


@given(st.lists(_line, max_size=6), _ending)
@_SETTINGS
def test_removing_the_block_is_exact_when_the_file_ends_with_one_line_end(lines, ending):
    """If the file ends with exactly one line end (or is empty), the round trip returns
    the identical bytes."""
    data = ending.join(lines) + ending if lines else b""
    while data.endswith(ending + ending):  # exactly one line end
        data = data[: -len(ending)]
    out = init_mod.without_pointer_block(init_mod.with_pointer_block(data, _KIT))
    assert out == data


@given(st.one_of(_documents, _any_bytes))
@_SETTINGS
def test_adding_the_block_keeps_the_original_bytes_in_front(data):
    """The user's bytes stay a prefix of the new file: nothing is rewritten."""
    assert init_mod.with_pointer_block(data, _KIT).startswith(data)


@given(st.one_of(_documents, _any_bytes))
@_SETTINGS
def test_a_file_with_the_block_is_recognised_so_the_block_is_not_added_twice(data):
    """The callers skip a file that contains the begin marker; the block carries it."""
    marked = init_mod.with_pointer_block(data, _KIT)
    assert init_mod.POINTER_BEGIN.encode() in marked
    assert init_mod.POINTER_END.encode() in marked


_fragments = st.sampled_from(
    [
        b"text\n",
        b"\r\n",
        b"\n\n",
        b"<!-- GABBE-KIT:BEGIN",
        b" -->\n",
        b"<!-- GABBE-KIT:END -->",
        b"<!-- GABBE-KIT:END -->\r\n",
        b"\xff\xfe",
        b"\n",
    ]
)


@given(st.one_of(st.lists(_fragments, max_size=8).map(b"".join), st.binary(max_size=60)))
@_SETTINGS
def test_installer_and_init_remove_the_block_identically(data):
    """`gabbe.installer.strip_pointer_block` and `init.without_pointer_block` give the same
    bytes for every input, including inputs with broken or repeated markers."""
    assert installer.strip_pointer_block(data) == init_mod.without_pointer_block(data)


@given(st.one_of(_documents, _any_bytes))
@_SETTINGS
def test_installer_removes_what_init_added(data):
    """The installer's removal rule undoes the init script's addition (up to trailing line ends)."""
    added = init_mod.with_pointer_block(data, _KIT)
    assert _trim(installer.strip_pointer_block(added)) == _trim(data)


# ---- repository URL cleaner -----------------------------------------------------------

_userinfo = st.sampled_from(["", "user@", "user:tok3n@", "a:b:c@", ":@", "@"])
_host = st.sampled_from(["github.com", "example.org", "h.io:8443", "[::1]", "10.0.0.1"])
_path = st.sampled_from(["", "/o/r", "/o/r.git", "/o/r.git/", '/o/"r', "/o/r\\x", "/o/@r", "/o r"])
_urls = st.one_of(
    st.builds(
        lambda s, u, h, p: f"{s}://{u}{h}{p}",
        st.sampled_from(["https", "http", "ssh", "git", "ftp"]),
        _userinfo,
        _host,
        _path,
    ),
    st.builds(lambda u, h, p: f"git@{h}:{p}", _userinfo, _host, _path),
    st.text(alphabet='ab:/@."\\\n \r', max_size=20),
    st.just(""),
)


@given(_urls)
@_SETTINGS
def test_clean_repo_url_never_returns_credentials_or_a_quote(url):
    """The cleaned URL is None or a string without user name, password, quote, backslash
    or line break: safe to write into a quoted field of AGENTS.md."""
    try:
        out = init_mod._clean_repo_url(url)
    except ValueError:
        return  # urlsplit refuses the input; `_detect_repo_url` catches that and returns None
    if out is None:
        return
    assert not any(c in out for c in '"\\\n\r')
    parts = urlsplit(out)
    assert parts.username is None and parts.password is None


@given(_urls)
@_SETTINGS
def test_clean_repo_url_is_stable_when_applied_twice(url):
    """Cleaning an already cleaned URL changes nothing."""
    try:
        once = init_mod._clean_repo_url(url)
    except ValueError:
        return
    if once is not None:
        assert init_mod._clean_repo_url(once) == once


def test_clean_repo_url_keeps_the_brackets_of_an_ipv6_host():
    """`https://[::1]/o/r` should stay a valid URL after cleaning."""
    assert init_mod._clean_repo_url("https://[::1]/o/r") == "https://[::1]/o/r"
