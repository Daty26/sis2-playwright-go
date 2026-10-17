# SIS 2 — Playwright Go

Eight browser tests cover registration, positive/negative login, purchase, product comparison, positive/negative password-reset requests, and a homepage smoke check on [Toolshop](https://practicesoftwaretesting.com/).

## Setup and run

Requirements: Go 1.26.1 or newer and internet access. Clone or download this repository and open its root directory.

Login tests use `DemoCustomer()` in `data/customer.go`; configure a valid, dedicated Toolshop account there. Registration, purchase, and registered-email reset tests generate their own accounts. Keep personal credentials out of the public repository.

```bash
go mod download
go run github.com/mxschmitt/playwright-go/cmd/playwright@v0.6201.1 install chromium
go test ./... -v -count=1
```

Run one test:

```bash
go test ./tests -run '^TestBuyProduct$' -v -count=1
```

Use these Go commands for the assignment suite. The remaining npm/TypeScript files are starter examples.

## Structure and decisions

- `tests/`: scenarios and assertions through page-object methods.
- `pages/`: selectors and browser actions.
- `fixtures/`: shared setup and cleanup, with an isolated context per test.
- `data/`: existing-account data and unique registration data.
- `screenshots/`: saved test-run evidence.

Only Chromium, cash-on-delivery checkout, and reset-request responses are covered. Other browsers, payment methods, and reset-email delivery are outside scope. See [Review.md](Review.md) for validation status and the remaining login URL correction.

## Documentation and submission

[Description.md](Description.md) lists the test cases; [Prompt.md](Prompt.md) records redacted AI inputs; [Review.md](Review.md) explains corrections and decisions.
