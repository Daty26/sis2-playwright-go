# Playwright Go tests and CI

[![Playwright tests](https://github.com/Daty26/sis2-playwright-go/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/Daty26/sis2-playwright-go/actions/workflows/tests.yml)

Eight browser tests cover registration, login, purchase, product prices, password-reset requests and the homepage. They use isolated browser contexts and generate their own accounts and passwords.

## Run the tests

Install Go 1.26.1 or newer. The reporting helper also needs Python 3.9 or newer.

```bash
go mod download
go run github.com/mxschmitt/playwright-go/cmd/playwright@v0.6201.1 install chromium
BASE_URL=http://localhost:4200 go test ./... -v -count=1 -parallel=2
```

Use the address of your running Toolshop application as `BASE_URL`. Without it, tests use the public site. Public-site CI runs can encounter Cloudflare, so the workflow starts a local Docker application instead. See [the original failure report](Bug_Report.md).

Each test saves a trace in `test-results/local/`. Failed tests also save `page.png` and `page.html`. Test passwords are generated; an optional `TEST_PASSWORD` environment variable can override them.

## CI files

| File | What to read it for |
| --- | --- |
| [.github/workflows/tests.yml](.github/workflows/tests.yml) | The complete pipeline, including application startup |
| [ci/compose.yml](ci/compose.yml) | The test application's UI, API and database |
| [ci/runner.py](ci/runner.py) | Split the tests, retry failures and build reports |
| [ci/test_runner.py](ci/test_runner.py) | Check that failures, missing traces and incorrect shards cannot pass |

The existing `tests/`, `pages/`, `fixtures/` and `data/` folders contain the Go test suite. [AI_CI_Appendix.md](AI_CI_Appendix.md) is reserved for the student's own record of AI use.

## How the pipeline works

The workflow runs on every push and pull request. It has two jobs:

1. **Tests:** four copies run in parallel. Each checks the code, installs Chromium, starts its own application/database, and runs its assigned tests.
2. **Merge reports:** waits for all copies, checks their results, and creates one HTML report and one JUnit XML file. It runs even if a test fails.

The application source is pinned in the workflow. Its Docker project is named `sis2-ci`, with UI port 4201 and API port 8092. Startup resets only this disposable test database; it does not use the developer's existing Toolshop containers.

The runner discovers test names, sorts them, and assigns every fourth test to each shard. Together, the four shards run the full suite. Inside a shard, two tests can run concurrently. With `CI=true`, failed tests get up to two retries. A retry keeps the first attempt's evidence and reports the test as flaky if it later passes.

Go's testing package has no `test.only`, Playwright Test config, native sharding or built-in HTML/JUnit reporters. The small Python helper provides those CI functions; it also rejects skipped or missing tests. It needs no Python packages.

## Reports and merge policy

Download the `playwright-report` artifact and extract it. Open `index.html` for the combined results, failure messages and evidence links. The same folder contains `junit.xml`. Individual shard artifacts are named `test-results-1` through `test-results-4`. All artifacts are retained for 14 days, subject to repository limits.

Open a trace with:

```bash
go run github.com/mxschmitt/playwright-go/cmd/playwright@v0.6201.1 show-trace path/to/trace.zip
```

**Block a merge:** code-check failures, application startup failures, tests still failing after retries, skipped/missing tests, wrong or missing shards, and missing required evidence. Every attempt needs a valid trace and raw logs. Failed attempts also need a screenshot and page HTML, including when a retry passes. Each shard's actual test names must match its assigned names.

**Report a warning:** tests that pass on retry and runtime changes. Investigate flaky tests using their original failure evidence. No coverage, performance or accessibility check is claimed.

To enforce this policy, require the **Merge reports** check on the default branch, `master`. This helper also detects missing results when a test job fails before running the suite. Branch-protection settings have not been changed.

## Check the helper locally

With your application running, use a new output folder for each run:

```bash
python3 -m unittest discover -s ci -p 'test_*.py' -v
BASE_URL=http://localhost:4200 CI=true python3 ci/runner.py run --shard=1/1 --output=test-results/example
python3 ci/runner.py merge --input=test-results/example --shards=1 --output=playwright-report/example
```

## Submission evidence

In GitHub Actions, choose **Run workflow**, first with `shards=1`, then with `shards=4`. Keep `verify_failure=false` for timings and compare the same commit. Record the total run time and the slowest **Run Playwright tests** step. Repeating each mode two or three times gives a more reliable comparison.

| Configuration | Total GitHub time | Slowest test step | Run link |
| --- | --- | --- | --- |
| 1 shard | Awaiting this version's hosted run | Awaiting measurement | — |
| 4 shards | Awaiting this version's hosted run | Awaiting measurement | — |

For failure evidence, run with `verify_failure=true`. The homepage test deliberately fails; the report must remain red and retain all three attempts. Then run normally. Also check cache restoration in a subsequent `setup-go` log, separate push/PR runs, artifact retention, and a passing default-branch badge. Earlier runs belong to the previous implementation and do not validate this simplified version.

## Earlier SIS 2 documentation

[Description.md](Description.md) lists the scenarios. [Prompt.md](Prompt.md) and [Review.md](Review.md) contain the earlier AI record and review. Coverage is limited to Chromium, cash-on-delivery checkout and reset-request responses.
