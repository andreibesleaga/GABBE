
import pytest
import time
import requests
from unittest.mock import MagicMock, patch
from gabbe.llm import call_llm
from gabbe.config import Colors

@patch("gabbe.llm.time.sleep")
@patch("gabbe.llm.requests.post")
@patch("gabbe.llm.GABBE_API_KEY", "fake-key") 
def test_llm_exponential_backoff_429(mock_post, mock_sleep):
    """
    Test that call_llm retries on 429 using exponential backoff.
    """
    # Setup mock response for 429 then success
    mock_response_429 = MagicMock()
    mock_response_429.raise_for_status.side_effect = requests.exceptions.HTTPError(response=MagicMock(status_code=429))
    
    mock_response_success = MagicMock()
    mock_response_success.json.return_value = {
        "choices": [{"message": {"content": "Success"}}]
    }
    
    # Fail twice with 429, then succeed
    mock_post.side_effect = [
        requests.exceptions.HTTPError(response=MagicMock(status_code=429)),
        requests.exceptions.HTTPError(response=MagicMock(status_code=429)),
        mock_response_success
    ]
    
    result = call_llm("test prompt")
    
    assert result == "Success"
    assert mock_post.call_count == 3
    
    # Check backoff delays: 1s, then 2s
    # assert mock_sleep.call_args_list matches [call(1), call(2)]
    # We use any_order=False implicitly by list order
    expected_calls = [1, 2] 
    actual_calls = [args[0] for args, _ in mock_sleep.call_args_list]
    
    # We only care that it slept with increasing duration
    assert actual_calls == expected_calls

@patch("gabbe.llm.time.sleep")
@patch("gabbe.llm.requests.post")
@patch("gabbe.llm.GABBE_API_KEY", "fake-key") 
def test_llm_sanitizes_errors(mock_post, mock_sleep, capsys):
    """
    Test that sensitive API errors are sanitized in stdout.
    """
    # Simulate a 500 error with a sensitive message
    mock_error = requests.exceptions.HTTPError("Sensitive: API Key Invalid")
    mock_error.response = MagicMock(status_code=500)
    
    # Always fail
    mock_post.side_effect = mock_error
    
    result = call_llm("test prompt")
    
    assert result is None

    # Errors are handled via logger only — stdout must be completely clean
    captured = capsys.readouterr()
    assert captured.out == ""
    # Sensitive exception text must never reach stdout
    assert "Sensitive: API Key Invalid" not in captured.out

@patch("gabbe.llm.time.sleep")
@patch("gabbe.llm.requests.post")
@patch("gabbe.llm.GABBE_API_KEY", "fake-key") 
def test_llm_auth_error_no_retry(mock_post, mock_sleep):
    """
    Test that 401 errors abort immediately without retry.
    """
    mock_post.side_effect = requests.exceptions.HTTPError(response=MagicMock(status_code=401))
    
    result = call_llm("test")
    
    assert result is None
    assert mock_post.call_count == 1 # No retries
    mock_sleep.assert_not_called()
