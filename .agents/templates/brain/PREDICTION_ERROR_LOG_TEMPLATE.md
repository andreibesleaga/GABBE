# PREDICTION_ERROR_LOG_TEMPLATE.md — Surprise Minimization

> **Purpose**: Logging "Surprise" (Prediction Error) to drive Active Inference.
> **Updated by**: `predictive-processing.skill.md`
> **Read by**: `self-improvement.skill.md`, `brain/learning-adaptation.skill.md`

## 1. The Prediction (Prior Belief)
*What did we expect to happen?*
- **Action**: Run the unit tests for `PaymentService`.
- **Expected Outcome**: All tests pass.
- **Confidence**: High (95%) - we only changed a comment.

## 2. The Sensation (Posterior / Observation)
*What actually happened?*
- **Observation**: Test `should_charge_card` FAILED.
- **Error**: `TimeoutError: Connection to Stripe failed`.

## 3. The Surprise (Prediction Error)
*How big is the gap between expectation and reality?*
- **Surprise Level**: High (We expected 0 failures, got 1).
- **Type**: Model Failure (Our model of "comments don't affect code" was correct, but our model of "Stripe is always up" was wrong).

## 4. Policy Selection (Action)
*How do we minimize this error?*
- [ ] **Action A (Perception Update)**: Update our belief. "Stripe connectivity is flaky." -> Retry logic needed.
- [ ] **Action B (Action Update)**: Change the world. "Mock Stripe in tests so we don't rely on network." -> Implement mocks.

## 5. Result
*Did the action reduce surprise?*
- **Chosen Action**: B (Mock Stripe).
- **New Observation**: Tests pass.
- **Surprise**: Zero.
- **Consolidation**: "Always mock external services in unit tests."
