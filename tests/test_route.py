"""Unit tests for gabbe.route."""
import pytest
from unittest.mock import patch
from gabbe.route import detect_pii, calculate_complexity, route_request


# ---------------------------------------------------------------------------
# detect_pii
# ---------------------------------------------------------------------------

class TestDetectPii:
    def test_no_pii(self):
        assert detect_pii("Fix the login bug") is False

    def test_email_detected(self):
        assert detect_pii("Contact user@example.com for details") is True

    def test_phone_detected(self):
        assert detect_pii("Call 555-123-4567 for support") is True

    def test_ssn_dashes_detected(self):
        assert detect_pii("SSN: 123-45-6789") is True

    def test_api_key_credential_detected(self):
        assert detect_pii("api_key=super_secret_value_here") is True

    def test_password_credential_detected(self):
        assert detect_pii("password: hunter2") is True

    def test_credit_card_detected(self):
        assert detect_pii("Card: 4111 1111 1111 1111") is True


# ---------------------------------------------------------------------------
# calculate_complexity
# ---------------------------------------------------------------------------

class TestCalculateComplexity:
    def test_short_prompt_is_simple(self):
        score, reason = calculate_complexity("Fix typo")
        assert score <= 10
        assert "Simple" in reason or "Heuristic" in reason

    @patch("gabbe.route.call_llm", side_effect=EnvironmentError("no key"))
    def test_long_prompt_fallback(self, mock_llm):
        """Fallback heuristic when LLM is unavailable (raises EnvironmentError)."""
        long_prompt = "architect distributed system " * 20
        score, reason = calculate_complexity(long_prompt)
        assert "Fallback" in reason

    @patch("gabbe.route.call_llm", side_effect=EnvironmentError("no key"))
    def test_complex_keywords_increase_score(self, mock_llm):
        # Force LLM failure so heuristic fallback runs
        prompt = "I need to architect a distributed security audit system. " * 10
        score, _ = calculate_complexity(prompt)
        assert score > 0


# ---------------------------------------------------------------------------
# route_request
# ---------------------------------------------------------------------------

class TestRouteRequest:
    def test_simple_prompt_routes_local(self):
        result = route_request("Fix typo in readme")
        assert result == "LOCAL"

    def test_pii_routes_local(self):
        result = route_request("Email user@domain.com about this bug")
        assert result == "LOCAL"

    @patch("gabbe.route.calculate_complexity", return_value=(80, "mocked"))
    def test_complex_prompt_routes_remote(self, mock_complexity):
        # Force complexity score above threshold without calling LLM
        result = route_request("architect a distributed system " * 5)
        assert result == "REMOTE"
