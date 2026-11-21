# SPDX-License-Identifier: Apache-2.0
"""Tests for the content cache + opt-in LLM response caching (cost optimization)."""

from gabbe.cache import ContentCache, content_key


def test_content_key_stable_and_input_sensitive():
    assert content_key("a", 1) == content_key("a", 1)
    assert content_key("a", 1) != content_key("a", 2)


def test_content_cache_roundtrip_and_miss(tmp_path):
    c = ContentCache(tmp_path, namespace="t")
    assert c.get("missing") is None
    c.set("k", {"v": 42})
    assert c.get("k") == {"v": 42}


def test_content_cache_degrades_on_bad_dir():
    # An unwritable root degrades to no-op (never raises).
    c = ContentCache("/proc/nonexistent/cannot-create", namespace="x")
    c.set("k", {"v": 1})  # must not raise
    assert c.get("k") is None


def test_llm_cache_serves_repeat_calls_without_api(tmp_project, monkeypatch):
    """With GABBE_LLM_CACHE on, a second identical call hits the cache (0 tokens)
    and does NOT call the API again."""
    import gabbe.llm as llm

    monkeypatch.setenv("GABBE_LLM_CACHE", "1")
    monkeypatch.setattr("gabbe.config.GABBE_LLM_CACHE", True, raising=False)

    calls = {"n": 0}

    def fake_retry(prompt, system_prompt, temperature, timeout):
        calls["n"] += 1
        return "answer", {"total_tokens": 100, "prompt_tokens": 80, "completion_tokens": 20}

    monkeypatch.setattr(llm, "_call_with_retry", fake_retry)

    c1, u1 = llm.call_llm_with_usage("classify this", "sys", temperature=0)
    c2, u2 = llm.call_llm_with_usage("classify this", "sys", temperature=0)

    assert c1 == c2 == "answer"
    assert calls["n"] == 1  # second call served from cache
    assert u2["total_tokens"] == 0  # cache hit bills nothing


def test_llm_cache_off_by_default(tmp_project, monkeypatch):
    import gabbe.llm as llm

    monkeypatch.setattr("gabbe.config.GABBE_LLM_CACHE", False, raising=False)
    calls = {"n": 0}

    def fake_retry(prompt, system_prompt, temperature, timeout):
        calls["n"] += 1
        return "x", {"total_tokens": 1}

    monkeypatch.setattr(llm, "_call_with_retry", fake_retry)
    llm.call_llm_with_usage("p", "s", temperature=0)
    llm.call_llm_with_usage("p", "s", temperature=0)
    assert calls["n"] == 2  # no caching when disabled


def test_a_link_at_the_entry_path_is_not_written_through(tmp_path):
    import os

    from gabbe.cache import ContentCache, content_key

    cache = ContentCache(tmp_path / "c", namespace="n")
    key = content_key("x")
    victim = tmp_path / "victim.txt"
    os.symlink(victim, cache._path(key))
    cache.set(key, {"a": 1})
    assert not victim.exists()


def test_a_link_at_the_entry_path_is_not_read_through(tmp_path):
    import json
    import os

    from gabbe.cache import ContentCache, content_key

    cache = ContentCache(tmp_path / "c", namespace="n")
    key = content_key("y")
    secret = tmp_path / "outside.json"
    secret.write_text(json.dumps({"value": "from outside the cache"}))
    os.symlink(secret, cache._path(key))
    assert cache.get(key) is None  # a planted link is a miss

    os.unlink(cache._path(key))
    cache.set(key, {"a": 1})
    assert cache.get(key) == {"a": 1}  # an ordinary entry still reads back


def test_a_fifo_at_the_entry_path_is_a_miss_and_does_not_block(tmp_path):
    import os

    import pytest

    from gabbe.cache import ContentCache, content_key

    if not hasattr(os, "mkfifo"):
        pytest.skip("no FIFOs on this platform")
    cache = ContentCache(tmp_path / "c", namespace="n")
    key = content_key("z")
    os.mkfifo(cache._path(key))
    assert cache.get(key) is None
