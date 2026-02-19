"""Unit tests for gabbe.route."""
import pytest
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

    def test_long_prompt_fallback(self, monkeypatch):
        """Fallback heuristic when LLM is unavailable (raises EnvironmentError)."""
        import gabbe.route as route_mod
        monkeypatch.setattr(
            route_mod, "call_llm",
            lambda *a, **kw: (_ for _ in ()).throw(EnvironmentError("no key"))
        )
        long_prompt = "architect distributed system " * 20
        score, reason = calculate_complexity(long_prompt)
        assert "Fallback" in reason

    def test_complex_keywords_increase_score(self, monkeypatch):
        import gabbe.route as route_mod
        # Force LLM failure so heuristic fallback runs
        monkeypatch.setattr(
            route_mod, "call_llm",
            lambda *a, **kw: (_ for _ in ()).throw(EnvironmentError("no key"))
        )
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

    def test_complex_prompt_routes_remote(self, monkeypatch):
        import gabbe.route as route_mod
        # Force complexity score above threshold without calling LLM
        monkeypatch.setattr(route_mod, "calculate_complexity", lambda p: (80, "mocked"))
        result = route_request("architect a distributed system " * 5)
        assert result == "REMOTE"
