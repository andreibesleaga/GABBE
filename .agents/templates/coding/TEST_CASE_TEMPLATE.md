# Test Case: [TC-ID] - [Title]

**Feature**: [Feature Name]
**Priority**: [P0 - Blocker / P1 - Critical / P2 - Normal]
**Type**: [Functional / UI / Performance / Security]
**Automated**: [Yes / No / To Be Automated]

## Pre-conditions
1.  [User is logged in]
2.  [Cart is empty]

## Test Steps
| Step # | Action | Expected Result |
|---|---|---|
| 1 | Navigate to `/products` | Product list loads within 2s |
| 2 | Click "Add to Cart" on Item A | "Item added" toast appears |
| 3 | Click Cart Icon | Cart drawer opens showing Item A |

## Post-conditions
-   [Item A remains in cart]
-   [Inventory count is unchanged (until checkout)]

## Test Data
-   **User**: `test-user@example.com`
-   **Item**: `SKU-12345`

## Notes
-   [Edge cases to watch out for, e.g., "Slow network"]
