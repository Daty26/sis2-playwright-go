# AI Prompt Log

## Tool and scope

- **AI tool:** GPT-5.6 Extra-High.
- **Project:** SIS 2 — Test Automation with Playwright, using Go.
- **Website:** https://practicesoftwaretesting.com/
- **Source:** The original `Prompt.md` export and the subsequent messages available in this conversation.

## How to read this record

This is an **edited, privacy-redacted prompt log**, not a complete verbatim transcript. Quoted requests retain their original wording, apart from labeled redactions of local paths and terminal prompts. Headings and context notes were added for readability.

- `[CODE OMITTED]` replaces a full code submission.
- `[HTML OMITTED]` replaces copied page markup.
- `[OUTPUT OMITTED]` replaces terminal output, installation logs, or repeated results.
- `[DOCUMENT OMITTED]` replaces a document pasted as context.
- `[REDACTED]` replaces personal information, account credentials, or local paths.

Passwords, personal email addresses, customer details, and full source-code dumps are not reproduced here. Context notes describe omitted material; they are editorial summaries, not invented prompts. The original chat contains the full inputs. Assistant responses are excluded from this prompt log; the student's review and corrections belong in `Review.md`.

## 1. Understanding the assignment and starting the project

### Prompt 01 — Explain the task

> explain me the task for sis asignment
> what should I do there?

Context: `Week_6_Masters_ST.pptx` was attached. Its local filesystem path is `[REDACTED]`.

### Prompt 02 — Provide the assignment requirements

> SIS 2
> Test Automation with Playwright
> DEADLINE - Oct 23
> LINK to Site to be tested
> https://practicesoftwaretesting.com/
>
> 1. At least 5 AT suits mentioned in the Pres - use any language you want with the Playwright framework.
> 2. Description.md - file: explain what you want to do
>    1. List of TCs to be automated
> 3. Prompt.md file save exactly the prompt you used for the AI tool; mark exactly which tool you gonna use, like Claude Opus 5 Max efforts, etc
> 4. Review.md: explain what the AI results were about, how you reviewed and modified them, and justify your decisions
> 5. Screenshots - AI response, Run results or whatever you think matters
> 6. Link to public GitHub repository.
> 7. Google Forms link

Formatting note: Links, line breaks, and numbering in this pasted brief have been normalized for Markdown. The model example above is part of the assignment wording, not a claim about the tool used.

### Prompt 03 — Ask for step-by-step guidance

> let's start from begining intialize the project and navigate me step by step what should I do not writing code for myslef

### Prompt 04 — Clarify who should do the work

> don't do anything for me, just navigate me from start how to do this project

### Prompt 05 — Share installation and initial results

[OUTPUT OMITTED: Playwright's npm installer output, browser downloads, two passing Chromium example tests, and starting/stopping the HTML report server. The same log was pasted several times; repeated copies and local terminal paths are omitted.]

### Prompt 06 — Introduce the project description

> here is my description md

### Prompt 07 — Submit the description for review

[DOCUMENT OMITTED: The draft `Description.md` identified Go/Golang and the five workflows: registration, login, purchase, product comparison, and password reset.]

## 2. Go setup and browser fixtures

### Prompt 08 — Confirm Go is installed

[OUTPUT OMITTED: `go version` reported Go 1.26.1 on darwin/arm64.]

### Prompt 09 — Share module setup

[OUTPUT OMITTED: `go mod init sis2`, installation of `github.com/mxschmitt/playwright-go`, and confirmation that version `v0.6201.1` was installed.]

### Prompt 10 — Share Chromium installation

[OUTPUT OMITTED: The Playwright Go CLI successfully downloaded Chromium and its headless shell. Local cache paths are redacted.]

### Prompt 11 — Confirm completion

> finished

### Prompt 12 — Submit the first browser fixture

[CODE OMITTED: Initial `fixtures.NewPage(t)` implementation with Playwright startup, Chromium launch, context creation, page creation, and browser cleanup.]

### Prompt 13 — Submit the revised fixture

[CODE OMITTED: Updated browser fixture with cleanup for Playwright, the browser, and the browser context.]

[OUTPUT OMITTED: `gofmt` and `go test ./fixtures`; the package compiled with no test files.]

## 3. Homepage and reusable page objects

### Prompt 14 — Submit the homepage object

[CODE OMITTED: `HomePage`, its constructor, `Open()`, and `ExpectLoaded()`.]

[OUTPUT OMITTED: Formatting and successful compilation of the pages package.]

### Prompt 15 — Submit the homepage test

[CODE OMITTED: `TestHomePageLoads` using a fixture, navigation, and a homepage assertion.]

[OUTPUT OMITTED: The homepage browser test passed.]

### Prompt 16 — Clarify the fixture's return type

[CODE OMITTED: A browser fixture returning `*pages.HomePage` instead of a raw `playwright.Page`.]

### Prompt 17 — Share the result after refactoring

[OUTPUT OMITTED: `go test ./tests` passed after separating browser setup from homepage-object construction.]

## 4. Login tests

### Prompt 18 — Provide manually inspected login details

[HTML OMITTED: Email and password inputs, the login submit button, the invalid-login error, and the signed-in navigation element.]

Context supplied:

- Login URL: `https://practicesoftwaretesting.com/auth/login`.
- Test IDs: `email`, `password`, `login-submit`, and `nav-menu`.
- Invalid-login text: `Invalid email or password`.
- Successful-login URL: `https://practicesoftwaretesting.com/account`.
- Signed-in customer's name: `[REDACTED]`.

### Prompt 19 — Submit the login page object

[CODE OMITTED: `LoginPage` with `Open()`, `SignIn()`, `ExpectSignedIn()`, and `ExpectInvalidCredentials()`.]

[OUTPUT OMITTED: Successful compilation of the pages and fixtures packages.]

### Prompt 20 — Submit login results and test data

[OUTPUT OMITTED: Both login tests passed; the formatting command also referenced a nonexistent `fixtures/pages.go`.]

[CODE OMITTED: `Customer` and `DemoCustomer()`. Personal email, password, and display name are redacted.]

### Prompt 21 — Submit the login tests and negative assertion

[CODE OMITTED: Parallel valid-login and invalid-password tests, plus the updated `ExpectInvalidCredentials()` URL assertion. Credentials and the submitted password strings are redacted.]

## 5. Registration tests

### Prompt 22 — Provide registration observations

[HTML OMITTED: Inspected registration fields and selectors.]

Context supplied: registration URL, required field test IDs, `YYYY-MM-DD` date format, password requirements, country option, and redirect to the login page without a success message. Personal customer values are redacted.

### Prompt 23 — Submit the registration data factory

[CODE OMITTED: Expanded `Customer` struct and `NewRegistrationCustomer()` with a unique email. Passwords, customer details, and address/contact values are redacted.]

[OUTPUT OMITTED: Formatting and successful compilation of the data package.]

### Prompt 24 — Submit the registration page object

[CODE OMITTED: `RegistrationPage`, field-filling logic, country selection, submission, and login-redirect assertion.]

[OUTPUT OMITTED: Successful compilation of the pages and data packages.]

### Prompt 25 — Submit the registration test and results

[CODE OMITTED: Independent registration test using a fresh customer, followed by login with that account.]

[OUTPUT OMITTED: Two passing registration runs and formatting messages about nonexistent filenames.]

## 6. Product comparison and changes to the working approach

### Prompt 26 — Provide product observations

[HTML OMITTED: Full catalogue cards, dynamic product IDs, SVG icons, and product-detail markup.]

Context supplied:

- Product A: `Combination Pliers`, observed price `$14.15`.
- Product B: `Pliers`, observed price `$12.01`.
- Catalogue URL: `https://practicesoftwaretesting.com/category/hand-tools`.
- Detail test IDs: `product-name` and `unit-price`.

The originally stated relationship was:

> Expected price relationship:product a costs less than product b

Context note: This statement is preserved as a historical input. The later comparison test checks A > B, consistent with the observed prices.

### Prompt 27 — Request implementation of the remaining tests

> okay now please finish the rest of the tests by yourself the project located under the [REDACTED: local project path and terminal prompt] in the same way I did previous tests, format naming and so on don't change previous tests that I have already done

### Prompt 28 — Request the changes be reverted

> revert it back and let me do it myself

Context note: The assistant's additions from that implementation attempt were reverted. The user then resumed writing the tests with guidance.

### Prompt 29 — Resume the guided work

> let's continue

### Prompt 30 — Submit the initial product page object

[CODE OMITTED: `ProductPage`, its constructor, and `Open(url string)`.]

### Prompt 31 — Request larger steps

> let's do bigger steps at a time

### Prompt 32 — Repeat the request with the updated method

[CODE OMITTED: `ProductPage.ExpectName(expectedName string)`.]

> let's do bigger steps at a time

### Prompt 33 — Share the comparison result and request direct file review

[OUTPUT OMITTED: `TestCompareTwoProducts` passed and logged Combination Pliers at $14.15 and Pliers at $12.01.]

> view them in the folder yourself

## 7. Password-reset request tests

### Prompt 34 — Provide password-reset observations

[HTML OMITTED: Full markup for the success and error alerts.]

Context supplied:

- URL: `https://practicesoftwaretesting.com/auth/forgot-password`.
- Test IDs: `email` and `forgot-password-submit`.
- Registered-email response: `page.forgot-password.confirm`.
- Unregistered-email response: `The selected email is invalid.`

The observation about what happened after submission was:

> just show up alert

### Prompt 35 — Repeat the password-reset observations

[REPEATED CONTEXT OMITTED: The same forgot-password URL, selectors, success/error markup, and alert-only observation were submitted again.]

### Prompt 36 — Share the reset-test results

[OUTPUT OMITTED: Both known-email and unknown-email reset tests passed. The formatting command referenced a nonexistent `fixtures/password_reset.go`; the fixture was stored in `fixtures/browser.go`.]

## 8. Purchase and checkout

### Prompt 37 — Provide checkout observations

[HTML OMITTED: Full address form, country-option list, and checkout markup.]

[DOCUMENT OMITTED: The observations table covering product quantity, cart contents, checkout transitions, billing, payment, and completion.]

Public UI details supplied included:

- Quantity increase and add-to-cart test IDs: `increase-quantity`, `add-to-cart`.
- Checkout URL: `https://practicesoftwaretesting.com/checkout`.
- Cart test IDs: `product-title`, `product-quantity`, `product-price`, `cart-total`.
- Proceed buttons observed: `proceed-1`, `proceed-3`.
- Billing test IDs: `country`, `postal_code`, `house_number`, `street`, `city`, `state`.
- Payment test ID/value: `payment-method` / `cash-on-delivery`.
- Submission and response test IDs: `finish`, `payment-success-message`.
- Payment response: `Payment was successful`.

The signed-in customer's name and address/contact values are `[REDACTED]`.

### Prompt 38 — Share a purchase-test failure

[OUTPUT OMITTED: The full `TestBuyProduct` failure log and terminal paths.]

Relevant error excerpt:

```text
complete billing address: Locator expected to have Value '10'
Actual value:
waiting for getByTestId('house_number')
unexpected value ""
```

## 9. Project review and prompt-log formatting

### Prompt 39 — Request a complete review

> now check everything

### Prompt 40 — Request a readable, redacted prompt log

> remake prompt md in normal readable format md maybe when I give my code don't expose everything that I send maybe just beep it somehow

The omissions and redaction labels in this document implement that request. They identify removed context explicitly rather than presenting shortened inputs as complete, verbatim prompts.
