import pytest
import requests
from unittest.mock import patch, MagicMock
from gabbe.llm import call_llm, _LLM_MAX_RETRIES

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("GABBE_API_KEY", "test-key")

@patch("gabbe.llm.requests.post")
@patch("gabbe.llm.time.sleep")
@patch("gabbe.llm.GABBE_API_KEY", "test-key")
def test_call_llm_success_first_try(mock_sleep, mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"choices": [{"message": {"content": "Hello"}}]}
    mock_post.return_value = mock_response

    result = call_llm("prompt")
    assert result == "Hello"
    assert mock_post.call_count == 1
    mock_sleep.assert_not_called()

@patch("gabbe.llm.requests.post")
@patch("gabbe.llm.time.sleep")
@patch("gabbe.llm.GABBE_API_KEY", "test-key")
def test_call_llm_retries_on_connection_error(mock_sleep, mock_post):
    # Fail twice, succeed third time
    mock_success = MagicMock()
    mock_success.json.return_value = {"choices": [{"message": {"content": "Success"}}]}
    
    mock_post.side_effect = [
        requests.exceptions.ConnectionError("Fail 1"),
        requests.exceptions.Timeout("Fail 2"),
        mock_success
    ]

    result = call_llm("prompt")
    assert result == "Success"
    assert mock_post.call_count == 3
    assert mock_sleep.call_count == 2

@patch("gabbe.llm.requests.post")
@patch("gabbe.llm.time.sleep")
@patch("gabbe.llm.GABBE_API_KEY", "test-key")
def test_call_llm_exhausts_retries(mock_sleep, mock_post):
    mock_post.side_effect = requests.exceptions.ConnectionError("Fail Always")

    result = call_llm("prompt")
    assert result is None
    assert mock_post.call_count == _LLM_MAX_RETRIES
    assert mock_sleep.call_count == _LLM_MAX_RETRIES - 1 # Sleeps after 1st and 2nd attempt, not after last

@patch("gabbe.llm.requests.post")
@patch("gabbe.llm.time.sleep")
@patch("gabbe.llm.GABBE_API_KEY", "test-key")
def test_call_llm_no_retry_on_400(mock_sleep, mock_post):
    mock_response = MagicMock()
    error = requests.exceptions.HTTPError("400 Bad Request")
    error.response = MagicMock(status_code=400)
    mock_response.raise_for_status.side_effect = error
    mock_post.return_value = mock_response

    result = call_llm("prompt")
    assert result is None
    assert mock_post.call_count == 1 # Should not retry
    mock_sleep.assert_not_called()
