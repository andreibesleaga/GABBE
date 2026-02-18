# E2E Test Suite Strategy

**Suite**: [Name]
**Tools**: Playwright / Cypress / Selenium

## 1. Critical User Journeys (CUJ)
*Automate these. Run on every deploy.*

### Journey 1: Guest Checkout
- **Steps**:
  1. Go to Home.
  2. Search for "T-Shirt".
  3. Click first result.
  4. Add to Cart.
  5. Checkout as Guest.
  6. Verify "Thank You" page.
- **Assertions**: Order ID exists in DB.

### Journey 2: User Login & Dashboard
- **Steps**:
  1. Click Login.
  2. Enter valid credentials.
  3. Verify Dashboard loads.
  4. Edit Profile.
  5. Logout.

## 2. Edge Cases (Manual / Exploratory)
*Document these for human QA.*
- [ ] Slow network connection checkout.
- [ ] Double-clicking "Pay" button.
- [ ] Back button behavior during payment.

## 3. Data Setup
- **Seed Data**: `fixtures/users.json` (Reloaded before suite).
- **Cleanup**: `afterAll()` hook to wipe test orders.
- **Environment**: Staging (Stubs for Payment Gateway).
