---
name: browser-tdd
description: Browser-based visual TDD using Playwright — verify UI produces correct visual output, not just syntactic correctness
triggers: [visual, playwright, frontend, UI, browser, screenshot, sticky, layout, DOM, visual test]
tags: [coding]
context_cost: medium
---
# Browser TDD Skill

## Goal
Verify that UI code produces correct visual output through actual browser execution — not just code that compiles or passes unit tests. Uses Playwright to check DOM structure, computed styles, scroll behavior, and visual rendering.

## When to Use
- Implementing CSS layout (sticky elements, flexbox, grid, responsive breakpoints)
- Implementing interactive components (modals, dropdowns, accordions)
- Implementing animations or transitions
- Any UI feature where "works" means "looks and behaves correctly in a browser"

## Steps

1. **Analyze the UI requirement**
   - Understand what the UI should look like and how it should behave
   - Identify testable assertions: position, computed styles, DOM structure, visibility, scroll behavior
   - Examples:
     - "Sticky navbar stays at top of viewport when scrolling" → check `getBoundingClientRect().top === 0`
     - "Modal closes on Escape key" → keyboard event + `expect(modal).not.toBeVisible()`
     - "Grid has 3 columns on desktop" → check computed `grid-template-columns` value

2. **Write the Playwright test (Red phase)**
   ```typescript
   // tests/ui/navbar.spec.ts
   import { test, expect } from '@playwright/test';

   test('navbar is sticky after scrolling 200px', async ({ page }) => {
     await page.goto('/');
     await page.evaluate(() => window.scrollBy(0, 200));
     const navTop = await page.locator('nav').evaluate(
       el => el.getBoundingClientRect().top
     );
     expect(navTop).toBe(0);
   });
   ```

3. **Confirm Red** — run test, MUST FAIL
   ```bash
   npx playwright test tests/ui/navbar.spec.ts
   ```
   - If test passes immediately: the test assertion is wrong — fix the test
   - Common false-positive causes: wrong selector, assertion always true, wrong page route

4. **Implement the CSS/component change**
   - Make the minimal CSS or component change to achieve the desired behavior
   - Common pitfalls to check during implementation:
     - `overflow: hidden` on a parent element breaks `position: sticky`
     - `transform` on a parent breaks `position: fixed`
     - Missing `top:` value with `position: sticky`
     - Z-index stacking context issues

5. **Confirm Green** — run Playwright test
   ```bash
   npx playwright test tests/ui/navbar.spec.ts
   ```
   - Verify: test passes
   - If fail: read error carefully — Playwright gives precise computed value vs expected
   - Debug: use `page.screenshot({ path: 'debug.png' })` to see the actual state

6. **If test still fails after fix attempts**
   - Take screenshot: `await page.screenshot({ path: 'tests/ui/screenshots/debug.png' })`
   - Log computed styles: `await page.locator('nav').evaluate(el => getComputedStyle(el))`
   - Check parent overflow: walk up the DOM tree
   - Invoke self-heal.skill if stuck for > 5 attempts

7. **Run full test suite** (no regressions)
   ```bash
   npx playwright test        # All browser tests
   [unit test command]        # All unit tests still pass
   ```

8. **Capture visual regression baseline** (optional but recommended)
   ```bash
   npx playwright test --update-snapshots  # Update baseline screenshots
   ```

9. **Refactor** while keeping all tests green

## Useful Playwright Patterns

```typescript
// Check computed CSS property
const display = await page.locator('.grid').evaluate(
  el => getComputedStyle(el).display
);
expect(display).toBe('grid');

// Check element is in viewport
await expect(page.locator('.sticky-header')).toBeInViewport();

// Check keyboard navigation
await page.keyboard.press('Tab');
await expect(page.locator(':focus')).toHaveAttribute('data-testid', 'next-button');

// Check scroll position
await page.evaluate(() => window.scrollTo(0, 500));
const scrollY = await page.evaluate(() => window.scrollY);
expect(scrollY).toBe(500);

// Visual screenshot comparison
await expect(page).toHaveScreenshot('homepage.png');
```

## Constraints
- NEVER mark a visual UI task done without a passing Playwright browser test
- Always run in headless mode for CI; headed mode is for local debugging only
- Screenshot comparisons require a committed baseline — take one after first Green

## Output Format
Passing Playwright test + implemented UI change. Report: "VISUAL TDD GREEN — [test name] passes in [browser]."

## Security & Guardrails

### 1. Skill Security (Browser TDD)
- **Test Payload Sanitization**: When creating visual tests (Step 2), the agent might accidentally embed real customer PII or sensitive session tokens into the test fixtures or mock responses to make the UI render correctly. The agent must strictly utilize deterministic, anonymized, and synthetic dummy data (e.g., Faker.js) for all UI rendering tests to prevent secrets from being committed to the test repository.
- **Visual Baseline Tampering**: In Step 8, the agent updates the visual snapshots (`--update-snapshots`). An attacker who compromised the UI could instruct the agent to "update the baseline" to legitimize a malicious visual change (e.g., an invisible phishing overlay). The agent must require explicit Human Authorization before executing any command that overwrites the "Golden Master" visual baselines.

### 2. System Integration Security
- **Headless Browser Sandbox Escape**: Playwright executes a real browser engine. If the UI being tested contains a zero-day browser exploit, the automated test runner could be compromised. The system integration must ensure that the Playwright browser context runs within a tightly restricted Docker container with dropped capabilities and no access to the host machine's sensitive internal networks or IAM metadata.
- **Third-Party Script Execution**: During UI tests (Step 5), the browser evaluates all scripts on the page, including tracking pixels, analytics, and external CDN dependencies. This can inadvertently trigger rate limits, pollute production analytics, or execute malicious external code. The Playwright configuration MUST intercept and block requests to all non-essential third-party domains during the test suite execution.

### 3. LLM & Agent Guardrails
- **Self-Heal Hallucination (CSS Hacks)**: If a visual test fails repeatedly, the LLM might resort to destructive CSS hacks (like `opacity: 0` or `display: none` applied globally, or `!important` tags) just to make the Playwright assertion pass, destroying the actual visual layout for real users. The agent must reject self-healing suggestions that introduce high-risk CSS anti-patterns.
- **Accessibility (a11y) Erasure**: Visual TDD focuses on how things *look*. The LLM might implement a feature that passes the visual snapshot but completely breaks the semantic DOM structure (e.g., using a visually styled `<div>` instead of a `<button>`), severely damaging accessibility. The agent must mathematically require passing automated DOM accessibility checks (e.g., `axe-core`) alongside visual assertions.
