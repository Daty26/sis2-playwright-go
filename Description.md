# Project Description

**Objective:** Automate five customer workflows on toolshop: registration, login, purchase, product comparison, and password-reset requests.

**Technology:** Go 1.26.1, Playwright Go v0.6201.1, Go's `testing` package, and Chromium.

## Test cases

| ID | Scenario | Steps and expected result |
|---|---|---|
| TC01 | Register a customer | Generate a unique email, register, verify the login redirect, then sign in with the new account. |
| TC02 | Valid login | Submit valid credentials; expect the account URL and customer's display name. |
| TC03 | Invalid password | Submit an incorrect password; expect the error and remain on the login page. |
| TC04 | Purchase | Add two Combination Pliers, verify the cart's item, quantity, unit price, and total; complete billing and cash-on-delivery checkout; verify an invoice confirmation. |
| TC05 | Compare products | Capture the names and prices of Combination Pliers and Pliers; assert that Combination Pliers costs more. |
| TC06 | Registered-email reset | Create an account and request a reset; expect the visible confirmation currently displayed as `page.forgot-password.confirm`. |
| TC07 | Unregistered-email reset | Submit a unique, unregistered email; expect `The selected email is invalid.` |
| TC08 | Homepage smoke check | Open the homepage; expect its title to contain `Practice Software Testing`. |

## Scope and data

Tests use page objects, shared fixtures, isolated browser contexts, and unique registration emails. Login tests require an existing account configured in `DemoCustomer()`. Coverage is limited to Chromium UI workflows, reset-request responses, and cash-on-delivery payment.
