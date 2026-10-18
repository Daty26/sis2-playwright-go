# AI Conversation Log

- **AI tool/model label recorded in the project:** GPT-5.6 Sol Extra-High.
- **Project:** SIS 2 — Test Automation with Playwright, using Go.
- **Website:** https://practicesoftwaretesting.com/

## Reading this log

These are **selected user messages and actual assistant reply excerpts** from the saved export and this conversation. They are not rewritten summaries. Markdown formatting and local file links have been normalized for readability.

`...` marks omitted code, HTML, terminal output, or parts of a long answer. `[REDACTED]` replaces personal information or local paths. The log is intentionally abbreviated, so it is not a complete verbatim transcript. Historical advice and results may have been corrected in later exchanges.

## 01. Understanding the assignment

**User**

> explain me the task for sis asignment
> what should I do there?

**Assistant**

> Your SIS 2 assignment is to create automated browser tests with Playwright for the Toolshop website. Submit your code as a repository.
>
> ...

## 02. Asking for guidance only

**User**

> don't do anything for me, just navigate me from start how to do this project

**Assistant**

> I misunderstood. I’ll guide you one step at a time, and you’ll perform the work yourself. Leave the files I created earlier aside and start in a fresh folder.
>
> ...

## 03. Reviewing the first browser fixture

**User — code excerpt**

```go
package fixtures
...
func NewPage (t *testing.T) playwright.Page{
...
}
```

**Assistant**

> Your setup sequence is correct. Fix these points before we use the helper:
> 1. Change t.Fatal to t.Fatalf in the context error check.
>    Fatalf formats %v; Fatal does not.
>
> ...
>
> 2. Register cleanup immediately after each resource is successfully created.
>
> ...
>
> 3. Use t.Errorf for errors inside cleanup callbacks.
>    This records the cleanup failure while allowing that callback to finish. Keep t.Fatalf for setup failures.
>
> ...

## 04. Reviewing the homepage assertion

**User — code excerpt**

```go
func (h *HomePage) ExpectLoaded() error {
    ...
    err := assert.Page(h.page).ToHaveTitle(
        "Practice Software Testing",
    )
    return err
}
```

**Assistant**

> Your struct, constructor, and navigation method look correct. The title assertion needs one change: a string checks the complete title, while your requirement is to check that it contains Practice Software Testing.
> Add regexp to your imports and change the argument to:

```go
regexp.MustCompile("Practice Software Testing")
```

> ...


## 05. Resuming product comparison

**User**

> let's continue

**Assistant**

> Let’s continue with **product comparison**, one file at a time.
>
> First, correct the expected result: **Combination Pliers ($14.15) costs more than Pliers ($12.01)**, so your test should check **A > B**.
>
> Your next step is to create `pages/product.go`, following the pattern in your `pages/login.go`:
>
> ...

## 06. Asking for larger implementation steps

**User**

```go
func (p *ProductPage) ExpectName(expectedName string) error {
    ...
}
```

> let's do bigger steps at a time

**Assistant**

> Your `ExpectName()` is correct. **Let’s finish the entire product-comparison test in this batch.** You’ll implement four files.
>
> 1. **Finish `pages/product.go`.**
>
> Keep your existing methods and add:

```go
func (p *ProductPage) Name() (string, error)
func (p *ProductPage) Price() (float64, error)
```

> ...
>
> Based on your collected prices, the expected relationship is **$14.15 > $12.01**. Compare the values read from the website.
>
> ...

## 07. Reviewing the passing comparison test

**User — terminal excerpt and request**

```text
go test ./tests -run '^TestCompareTwoProducts$' -v -count=1
...
    compare_test.go:57: Combination Pliers: $14.15; Pliers: $12.01
--- PASS: TestCompareTwoProducts (5.82s)
PASS
...
```

> view them in the folder yourself

**Assistant**

> I reviewed all four files. **Your comparison test is implemented correctly**, and your terminal output confirms it passes.
>
> ...
>
> One correction to my earlier example: your `*playwright.AriaRoleHeading` correctly includes the dereference required by your installed binding.
>
> ...

## 08. Planning the password-reset tests

**User — observation excerpt**

> 1. Forgot-password URL. [https://practicesoftwaretesting.com/auth/forgot-password](https://practicesoftwaretesting.com/auth/forgot-password)
>
> ...
>
> 5. Whether submitting the request immediately changes the password or requires an email link. just show up alert
>
> ...

**Assistant**

> We can now build **both password-reset request tests** in one batch. The success alert shows an untranslated key; use the literal text you observed and note that UI issue in `Review.md`.
>
> ...
>
> Creating a fresh account keeps this test independent of your existing login account.
>
> ...
>
> These tests verify the reset-request responses. The success alert alone does not prove that the password changed.
>
> Send the terminal output afterward; I’ll review the files directly from your folder.

## 09. Reviewing password-reset results

**User — terminal excerpt**

```text
gofmt -w pages/password_reset.go fixtures/password_reset.go tests/password_reset_test.go
go test ./tests -run '^TestResetPassword' -v -count=1
lstat fixtures/password_reset.go: no such file or directory
...
--- PASS: TestResetPasswordWithKnownEmail (6.88s)
--- PASS: TestResetPasswordWithUnknownEmail (6.97s)
PASS
...
```

**Assistant**

> **Both reset tests passed, and the code matches the planned cases.** I reviewed the files: the registered-email test creates its own account, the unknown-email test leaves its generated account unregistered, and both verify visible alerts and their exact text.
>
> The formatting error comes from the filename: your fixture is in [fixtures/browser.go](fixtures/browser.go). Keeping it there is fine. Use:

```bash
gofmt -w pages/password_reset.go fixtures/browser.go tests/password_reset_test.go
```

> ...

## 10. Planning the purchase flow

**User — HTML and observation excerpts**

```html
<div formgroupname="address" class="ng-dirty ng-touched ng-valid">
...
```

```text
...
data-test="payment-method"
value="cash-on-delivery"
...
```

**Assistant**

> We have enough to build the **complete purchase test**.
>
> One detail to verify manually: the public source suggests that the first **Confirm** validates payment, and another **Confirm** creates the invoice. It exposes `#order-confirmation` and `#invoice-number` afterward. Your final assertion should reach that invoice confirmation. [Payment implementation](https://github.com/testsmith-io/practice-software-testing/blob/main/sprint5/UI/src/app/checkout/payment/payment.component.ts)
>
> Implement this batch yourself:
>
> ...
>
> Check every returned error with a meaningful `t.Fatalf()` message.
>
> Then run:

```bash
gofmt -w pages/product.go pages/checkout.go fixtures/browser.go tests/purchase_test.go
go test ./tests -run '^TestBuyProduct$' -v -count=1
```

> Send the output afterward; I’ll inspect your files directly.

## 11. Debugging the house-number failure

**User — terminal excerpt**

```text
go test ./tests -run '^TestBuyProduct$' -v -count=1
...
    purchase_test.go:67: complete billing address: Locator expected to have Value '10'
        Actual value:
...
               - unexpected value ""
--- FAIL: TestBuyProduct (16.24s)
...
```

**Assistant**

> The failure comes from [checkout.go:73](pages/checkout.go): you check that the house number is already `"10"` **before your code fills it**.
>
> `ToHaveValue()` waits for a value; it doesn’t enter one. The failure prevents execution from reaching your filling loop.
>
> Replace this initial check:

```go
ToHaveValue(customer.HouseNumber)
```

> with:

```go
ToBeVisible()
```

> Your loop below already fills the house number and waits for postcode lookup. Move the original `ToHaveValue(customer.HouseNumber)` assertion **after that loop** to verify the final value.
>
> ...

## 12. Requesting a complete project review

**User**

> now check everything

**Assistant**

> **All five workflows are implemented, but the project still needs one code fix and submission documents.** I didn’t edit your files.
>
> 1. **Fix the successful-login URL** in [login.go:36](pages/login.go).
>
> `ExpectSignedIn()` currently expects `loginURL`. Change its expected URL to:

```go
"https://practicesoftwaretesting.com/account"
```

> Keep `loginURL` in `ExpectInvalidCredentials()`. The current success assertion can pass before the redirect or fail afterward, depending on timing.
>
> ...

## 13. Requesting a readable, redacted prompt log

**User**

> remake prompt md in normal readable format md maybe when I give my code don't expose everything that I send maybe just beep it somehow

**Assistant**

> Updated [Prompt.md](Prompt.md) with readable sections and chronological prompts.
>
> Full code, HTML, and logs use labeled omission placeholders; personal details are redacted. The document clearly discloses these edits. Other project files are unchanged.

## 14. Requesting the other documentation

**User**

> write review and description and Readme for me but don't write too much keep it simple checking all the boxes

**Assistant**

> Written concise versions of:
>
> - [Description.md](Description.md)
> - [Review.md](Review.md)
> - [README.md](README.md)
>
> They cover test cases, AI assistance, corrections, setup, and submission. The remaining login URL issue is documented. Code is unchanged.

## 15. Asking about GitHub upload readiness

**User**

> now can I upload to github?

**Assistant**

> **Make these two fixes before uploading publicly:**
>
> 1. In [customer.go](data/customer.go), replace your personal email/password with dedicated demo credentials, or load them from environment variables.
> 2. In [login.go:36](pages/login.go), change the successful-login assertion to expect:

```go
"https://practicesoftwaretesting.com/account"
```

> ...

## 16. Fixing the shared login URL constant

**User — terminal excerpt**

```text
go test ./... -v -count=1
...
    login_test.go:46: verify rejected login: Page URL expected to be 'https://practicesoftwaretesting.com/account'
        Actual value: https://practicesoftwaretesting.com/auth/login
...
--- FAIL: TestLoginWithInvalidPassword (9.88s)
...
FAIL
```

**Assistant**

> The shared `loginURL` constant now points to `/account`, so **both login assertions expect the account page**.
>
> In [login.go](pages/login.go), replace the constant with:

```go
const (
    loginURL   = "https://practicesoftwaretesting.com/auth/login"
    accountURL = "https://practicesoftwaretesting.com/account"
)
```

> Then use:
>
> - **`ExpectSignedIn()`** → `ToHaveURL(accountURL)`
> - **`ExpectInvalidCredentials()`** → `ToHaveURL(loginURL)`
>
> The invalid-password case correctly stayed on the login page; its expected URL was wrong.
>
> Run again:

```bash
gofmt -w pages/login.go
go test ./... -v -count=1
```

## 17. Checking the successful full-suite run

**User — terminal excerpt and request**

```text
go test ./... -v -count=1
...
--- PASS: TestResetPasswordWithUnknownEmail (5.01s)
--- PASS: TestLoginWithInvalidPassword (5.65s)
...
--- PASS: TestCompareTwoProducts (6.29s)
--- PASS: TestRegisterNewCustomer (6.46s)
--- PASS: TestLoginWithValidCredentials (6.53s)
--- PASS: TestResetPasswordWithKnownEmail (6.60s)
--- PASS: TestBuyProduct (11.46s)
PASS
ok      sis2/tests      14.756s
...
```

> check again

**Assistant**

> **The login assertions are now correct, and all 8 tests passed.** Three things remain before uploading publicly:
>
> 1. **Credentials:** your Gmail address and plaintext password are still in [customer.go](data/customer.go), including the staged copy. Replace them with dedicated demo credentials.
> 2. **Git staging:** your corrected `login.go` is **not staged yet**. Git currently holds the older, incorrect version.
> 3. **Documentation:** update `Review.md` to record the passing full suite and resolved login issue. Remove the outdated references to the pending login fix and TypeScript starter files from `README.md`.
>
> ...

## 18. Requesting paired prompts and replies

**User**

> can you actlually write exact prompt I used and the answer you gave me in prompt.md in this conversation maybe no need to fill out everything you can use .... if the code or answer is too big in prompt.md file

**Assistant — initial response in this turn**

> I’ll rewrite `Prompt.md` as user/assistant exchanges, using the actual wording available in this conversation. I’ll mark long code and answer omissions with `...` and keep credentials and personal details redacted.
