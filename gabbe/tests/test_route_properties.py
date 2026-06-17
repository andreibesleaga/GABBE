# SPDX-License-Identifier: Apache-2.0
"""Property-based tests for the cost-benefit router (Track B Phase 1 / Track C
self-adaptive proof).

Invariants:
  * any prompt containing PII routes LOCAL (privacy override), regardless of
    complexity — and short-circuits before any model call;
  * for non-PII prompts, the decision is REMOTE iff complexity > threshold.
PBT samples; it raises confidence, not proof.
"""

import string
from unittest.mock import patch

from hypothesis import given
from hypothesis import strategies as st

from gabbe import route
from gabbe.config import ROUTE_COMPLEXITY_THRESHOLD

# Safe filler that cannot itself trip a PII regex (letters/spaces only, no digits).
_safe = st.text(alphabet=string.ascii_letters + " ", max_size=60)
# Tokens that DO match a PII pattern (email / phone / SSN / credentials).
_pii = st.sampled_from(
    [
        "user@example.com",
        "555-123-4567",
        "123-45-6789",
        "api_key=supersecretvalue",
        "password: hunter2",
    ]
)


@given(prefix=_safe, token=_pii, suffix=_safe)
def test_pii_always_routes_local(prefix, token, suffix):
    prompt = f"{prefix} {token} {suffix}"
    assert route.detect_pii(prompt) is True
    # Must NOT consult the model when PII is present (privacy short-circuit).
    with patch.object(route, "calculate_complexity") as mock_complexity:
        decision = route.route_request(prompt)
    assert decision == "LOCAL"
    mock_complexity.assert_not_called()


@given(score=st.integers(min_value=0, max_value=100))
def test_complexity_threshold_decides_for_clean_prompts(score):
    clean = "refactor the helper module for clarity"
    assert route.detect_pii(clean) is False
    with patch.object(route, "calculate_complexity", return_value=(score, "mocked")):
        decision = route.route_request(clean)
    expected = "REMOTE" if score > ROUTE_COMPLEXITY_THRESHOLD else "LOCAL"
    assert decision == expected
