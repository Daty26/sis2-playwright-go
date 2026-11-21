# SIS 2 / SIS 3 — Playwright Go and CI

[![Playwright tests](https://github.com/Daty26/sis2-playwright-go/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/Daty26/sis2-playwright-go/actions/workflows/tests.yml)

Eight browser tests cover registration, positive/negative login, purchase, product comparison, positive/negative password-reset requests, and a homepage smoke check on [Toolshop](https://practicesoftwaretesting.com/).

## Setup and run

Requirements: Go 1.26.1 or newer, Python 3.9 or newer for CI reporting, and internet access. Docker with Compose is needed to provision the isolated test application. Run commands from this repository's root directory.

Tests create disposable accounts with unique `example.test` email addresses and generated passwords. The invalid-password test also creates its own account first. No personal login, GitHub secret, or manual account setup is required. An optional `TEST_PASSWORD` environment variable overrides the generated password; do not commit a real password.

```bash
go mod download
go run github.com/mxschmitt/playwright-go/cmd/playwright@v0.6201.1 install chromium
go test ./... -v -count=1
```

Without `BASE_URL`, tests use the public Toolshop site. That site can present a Cloudflare challenge to GitHub-hosted browsers (see [CI-001](Bug_Report.md)); CI therefore provisions its own application instead.

### Isolated local application

The pipeline uses the official Toolshop Sprint 5 source pinned in [ci/toolshop-revision.txt](ci/toolshop-revision.txt). Reproduce that environment locally:

```bash
git clone --filter=blob:none https://github.com/testsmith-io/practice-software-testing.git .ci/toolshop
git -C .ci/toolshop checkout ae7caecb811dd8952c09d997e69be7cb946ecd44
bash scripts/toolshop.sh up
BASE_URL=http://localhost:4201 go test ./... -v -count=1 -parallel=2
```

The dedicated `sis2-ci` Docker Compose project uses UI port 4201 and API port 8092. It does not restart an existing Toolshop on ports 4200/8091. Its database is disposable, with a test-only password configurable through `TOOLSHOP_DB_PASSWORD`. Every `up` recreates and seeds only that project's test database. The startup script installs locked dependencies, generates application keys, and probes the UI and API before tests start. Mail uses the application's log transport, so reset tests do not send email.

When finished, `bash scripts/toolshop.sh down` removes only this project's containers and database. The upstream checkout and downloaded dependencies remain in ignored `.ci/`.

Run one test:

```bash
go test ./tests -run '^TestBuyProduct$' -v -count=1
```


## Structure and decisions

- `tests/`: scenarios and assertions through page-object methods.
- `pages/`: selectors and browser actions.
- `fixtures/`: shared setup and cleanup, with an isolated context per test and trace recording.
- `data/`: unique registration data and generated credentials.
- `scripts/ci.py`: shard selection, retries, HTML and JUnit reports.
- `ci/`: Docker configuration and the pinned application revision.
- `test-results/` and `playwright-report/`: generated evidence, excluded from Git.
- `screenshots/`: historical SIS 2 evidence.

Only Chromium, cash-on-delivery checkout, and reset-request responses are covered. Other browsers, payment methods, and reset-email delivery are outside scope. Product selection searches by name rather than assuming a particular pagination order. Navigation and URL assertions use the same `BASE_URL`.

## CI

**System:** GitHub Actions, because the repository is already on GitHub and a matrix can run independent shards without maintaining a CI server.

[.github/workflows/tests.yml](.github/workflows/tests.yml) runs on every push and pull request without branch filters. It also supports manual runs:

1. **Build and check CI tooling:** compile every Go package, run `go vet`, and check the reporting tool's failure and shard handling.
2. **Four test jobs:** restore Go's dependency/build cache, download dependencies, install matching Chromium and Linux libraries, start a separate pinned application per runner, and run one quarter of the browser suite. `fail-fast: false` lets every shard finish.
3. **Merge reports:** download all shard results and generate one HTML report and one JUnit XML file, including results from failing shards. Missing shards, inconsistent inventories, skipped tests, and persistent failures keep the result red.

The runner discovers all top-level browser tests in `./tests` and distributes the sorted list round-robin. Shards collectively cover the full suite. Each shard uses up to two Go test workers and disables Go test-result caching with `-count=1`. The dependency cache speeds setup; it never substitutes an old test result.

### Go adaptation of the provided guide

The guide explicitly assumes the JavaScript/TypeScript Playwright Test runner. This repository uses the Go Playwright bindings and Go's `testing` package, so it has no `playwright.config.ts`, `test.only`, blob reporter, or native `--shard` option. Their equivalents are:

| Guide feature | Go implementation |
| --- | --- |
| `forbidOnly` | Go has no `.only` API. The CI command exposes no arbitrary test-name filter, automatically discovers the suite, and validates complete shard coverage. Skipped/missing results fail the gate. |
| CI retries: 2 | With `CI=true`, `scripts/ci.py` retries only failed tests up to twice in fresh `go test` processes. Local reporting defaults to zero retries. |
| Sharding / blob merge | Four matrix jobs write JSON summaries; the merge job validates coverage and combines all attempts into HTML and JUnit. |
| HTML and JUnit reporters | Standard-library HTML and XML generation from real `go test -json` events, including failure messages, durations and retry history. |
| Trace on first retry | The fixture records every attempt, including the original failure and successful attempts. Traces contain browser operations/network snapshots; Go assertion messages are in the report and logs. |
| Screenshots on failure | Failure cleanup saves a screenshot, page HTML, URL and title. |

A test that passes on retry is labeled **flaky** in HTML, JUnit properties, and the job summary, with a GitHub warning. The first failure is preserved. Build/runner failures do not trigger blind test retries. A test that still fails after all retries fails the job.

### Artifacts and debugging

All artifacts have **14-day retention**, subject to the repository's retention cap being at least seven days:

- `test-results-1` through `test-results-4`: raw JSON events, stderr, per-attempt traces, failure screenshots/page HTML, the shard report/JUnit, and application logs.
- `playwright-report`: merged `index.html`, `junit.xml`, and a copy of all shard evidence with working relative links.
- `junit-report`: the merged XML on its own.

Download and extract `playwright-report`, then open `index.html`. Open a trace with the matching Go Playwright CLI:

```bash
go run github.com/mxschmitt/playwright-go/cmd/playwright@v0.6201.1 show-trace path/to/trace.zip
```

Reports are uploaded after passing and failing test runs. Before success is reported, every attempt must have a nonempty, readable trace ZIP containing trace data, a nonempty raw event log, and a stderr log (which may be empty). Failed attempts must also retain nonempty screenshots and page HTML, even if a retry passes. The merger compares each shard’s actual case names with its expected selection as well as checking combined coverage. A workflow that fails before tests start retains application logs, and the merge job detects missing test summaries.

### Running the reporting pipeline locally

Use a fresh output directory for each run; the runner refuses to reuse stale results.

```bash
BASE_URL=http://localhost:4201 CI=true python3 scripts/ci.py run --shard=1/1 --output=test-results/one-shard
python3 scripts/ci.py merge --input=test-results/one-shard --shards=1 --output=playwright-report/one-shard
```

For a local four-shard check, launch all four commands together and wait for each process. The `run` command covers its entire assigned shard; do not add separate test filters.

```bash
BASE_URL=http://localhost:4201 CI=true python3 scripts/ci.py run --shard=1/4 --output=test-results/four-shards &
BASE_URL=http://localhost:4201 CI=true python3 scripts/ci.py run --shard=2/4 --output=test-results/four-shards &
BASE_URL=http://localhost:4201 CI=true python3 scripts/ci.py run --shard=3/4 --output=test-results/four-shards &
BASE_URL=http://localhost:4201 CI=true python3 scripts/ci.py run --shard=4/4 --output=test-results/four-shards &
wait
python3 scripts/ci.py merge --input=test-results/four-shards --shards=4 --output=playwright-report/four-shards
```

Each GitHub shard has its own application/database; these local commands share one local application, so their timing is only a local diagnostic.

### Merge gates and reporting policy

**Block merging:** compilation/static-check failures, CI-tooling checks, application startup failures, skipped/missing tests, missing shards or artifacts, and any browser test that still fails after its retries. Both login tests and the homepage smoke test are included. No tests are currently quarantined.

**Report with a warning:** tests that pass only on retry and runtime changes. Preserve the first failure, investigate the trace, and track a confirmed flaky test with an owner and fix. A warning is evidence to investigate, not permission to ignore repeated instability. There is no coverage, accessibility or performance-budget gate in this suite, so the workflow makes no claim to check them.

To enforce the policy, the repository owner must configure `master` branch protection/rulesets to require **Build and check CI tooling** and **Merge reports**. A workflow file alone cannot prohibit merging. The merge job checks all shard results, so it remains the same required check for one- and four-shard runs.

### Runtime comparison required for submission

Use **Actions → Playwright tests → Run workflow** on the same commit, with `shards=1`, then `shards=4`. Keep `verify_failure=false`. Both modes use the same app version, workers and retry policy. Run each mode two or three times and record the median workflow duration plus the slowest **Run Playwright tests** step. Link the runs and check a restored Go cache in a subsequent run's setup log.

| Configuration | Total GitHub run time | Test step (slowest shard) | Run links |
| --- | --- | --- | --- |
| 1 shard + merge | Pending GitHub execution | Pending | Pending |
| 4 shards + merge | Pending GitHub execution | Pending | Pending |

No GitHub speedup is claimed until those runs exist. Four jobs repeat application setup, and the merge job adds overhead, so a small eight-test suite may gain little total wall time even when test execution becomes faster. The earlier Cloudflare-failed public-site run is not a valid baseline for this local application.

Local verification on 21 November 2026 used the same final test code and shared isolated app: the one-shard command took **8.521 seconds**, and the four parallel commands took **6.211 seconds** before merging. Both covered all eight tests with **zero retries**. These are single macOS measurements of test commands, exclude application startup/report merging, and do not replace the required GitHub table.

### Intentional-failure evidence

For the submission check, manually run the workflow with `verify_failure=true`. The fixture adds an intentional failure to `TestHomePageLoads` during cleanup, before evidence capture. That run must be red and the merged report must show the failure and all retry traces. Run again with the option off to restore a normal passing run. This switch is off for automatic pushes/PRs.

### Remaining hosted submission evidence

- A run from a feature-branch push and a separate pull-request run.
- Cache-restoration evidence on a subsequent run.
- One-shard/four-shard runtime measurements and run links in the table above.
- A failed verification run with downloadable artifacts.
- A normal passing `master` branch run so the badge displays master's actual status.

These items require the workflow to be pushed to GitHub. Local validation does not establish GitHub cache behavior, retention, the badge state, or hosted timings.

## Documentation and submission

[Description.md](Description.md) lists the test cases; [Prompt.md](Prompt.md) records earlier redacted AI inputs; [Review.md](Review.md) explains earlier corrections and decisions. [AI_CI_Appendix.md](AI_CI_Appendix.md) records AI use for this CI assignment and its verification status.
