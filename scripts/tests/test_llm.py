"""Unit tests for gabbe.llm."""
import pytest
from unittest.mock import patch, MagicMock


def test_call_llm_raises_without_api_key():
    """call_llm must raise EnvironmentError when GABBE_API_KEY is unset."""
    import gabbe.llm as llm_mod
    with patch("gabbe.llm.GABBE_API_KEY", None):
        with pytest.raises(EnvironmentError, match="GABBE_API_KEY"):
            llm_mod.call_llm("test prompt")


def test_call_llm_returns_content_on_success():
    import gabbe.llm as llm_mod

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "  Hello world  "}}]
    }
    mock_response.raise_for_status = MagicMock()

    with patch("gabbe.llm.GABBE_API_KEY", "test-key"), \
         patch("gabbe.llm.requests.post", return_value=mock_response):
        result = llm_mod.call_llm("prompt")

    assert result == "Hello world"


def test_call_llm_returns_none_on_request_exception():
    import gabbe.llm as llm_mod
    import requests

    with patch("gabbe.llm.GABBE_API_KEY", "test-key"), \
         patch("gabbe.llm.requests.post", side_effect=requests.exceptions.ConnectionError("fail")):
        result = llm_mod.call_llm("prompt")

    assert result is None


def test_call_llm_returns_none_on_empty_choices():
    import gabbe.llm as llm_mod

    mock_response = MagicMock()
    mock_response.json.return_value = {"choices": []}
    mock_response.raise_for_status = MagicMock()

    with patch("gabbe.llm.GABBE_API_KEY", "test-key"), \
         patch("gabbe.llm.requests.post", return_value=mock_response):
        result = llm_mod.call_llm("prompt")

    assert result is None


def test_call_llm_returns_none_on_missing_choices_key():
    import gabbe.llm as llm_mod

    mock_response = MagicMock()
    mock_response.json.return_value = {"error": "bad request"}
    mock_response.raise_for_status = MagicMock()

    with patch("gabbe.llm.GABBE_API_KEY", "test-key"), \
         patch("gabbe.llm.requests.post", return_value=mock_response):
        result = llm_mod.call_llm("prompt")

    assert result is None


def test_call_llm_passes_custom_temperature():
    import gabbe.llm as llm_mod

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "ok"}}]
    }
    mock_response.raise_for_status = MagicMock()
    captured = {}

    def fake_post(url, headers, json, timeout):
        captured["payload"] = json
        return mock_response

    with patch("gabbe.llm.GABBE_API_KEY", "test-key"), \
         patch("gabbe.llm.requests.post", fake_post):
        llm_mod.call_llm("prompt", temperature=0.1)

    assert captured["payload"]["temperature"] == pytest.approx(0.1)
