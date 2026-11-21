# AI appendix — CI pipeline assignment

## Tool and model

- Tool: OpenAI Codex desktop application.
- Model: GPT-6-based Codex, as identified by the session. A more specific model version was not exposed to the assistant.
- Date: 21 November 2026, Asia/Almaty.
- Supplied material: the Week 10 lecture, the existing SIS2 Go repository, and `SIS 2_ CI pipeline for Playwright  step-by-step guide.pdf`.

## Prompts and scope

The task request was:

> help me finish the task here is step by step guide can you do it?\
> here

An equivalent request was submitted immediately before it and interrupted before implementation. Earlier review context identified missing parallelism, traces, HTML/JUnit reporting, retries, a badge, and runtime/gating documentation.

AI inspected the supplied guide and repository, drafted the workflow and reporting helper, adapted browser tracing and test data, diagnosed failures during verification, and drafted the README. This involved generated implementation code as well as explanations. The student should review and understand the files before submission.

## Decisions and corrections

1. The guide states that its sample uses JavaScript/TypeScript Playwright Test. The repository uses Go. Copying its YAML and `playwright.config.ts` would not execute the existing suite. The implementation preserves Go and documents each equivalent, including the absence of `.only` in Go's testing API.
2. A saved application's `page.html` is not a results report. The reporting helper creates a separate HTML results page and JUnit XML from actual Go test events.
3. Retries retain the initial failure and each subsequent attempt separately. A test that passes only on retry is explicitly reported as flaky. Missing/skipped tests and incomplete shard coverage cannot silently pass.
4. Existing evidence documented a Cloudflare challenge on public-site CI runs. A pinned, disposable Toolshop application/database replaces that external dependency in CI.
5. Local verification found that the product comparison and purchase tests assumed Combination Pliers appeared on the first category page. Catalog selection now searches by name instead of relying on pagination order.
6. The invalid-password test previously depended on a fixed demo identity. It now creates its own account first and submits an incorrect password. Test identities and passwords are synthetic and generated; no personal credential is required.
7. A Composer archive extraction failure occurred while installing the isolated app on a Docker bind mount. Setting `COMPOSER_MAX_PARALLEL_PROCESSES=1` allowed serial extraction and successful startup.
8. The first attempted local baseline failed on pagination. Its runtime must not be presented as a valid speed comparison with the corrected suite. GitHub timings and links must come from successful runs of the final workflow on the same commit.
9. The first simultaneous four-shard local run exposed registration redirect assertions firing while the API POST was still pending. Registration now waits for the POST's response/status before checking navigation. An extra `Response.Finished()` wait introduced during this fix stalled one run; it was removed and the run was stopped. Fresh final one-shard/four-shard runs both passed without retries.

## Verification

The implementation checks suite partitioning, retry history, persistent failure status, missing-shard detection, report evidence links, and skipped/infrastructure failure status. The workflow is also checked with pinned Actionlint, and Go packages are compiled and vetted.

Actual local results:

| Check | Observed result |
| --- | --- |
| Compilation, `go vet`, Actionlint v1.7.7 | Passed |
| CI helper checks | 13 passed, including missing/corrupt evidence and cases swapped between shards |
| Isolated Docker application startup | Passed using cached images from the same pinned source revision; API/UI dependencies installed from their locks and a fresh database seeded |
| Final one-shard suite | 8 passed, 0 retries; command wall time 8.521 seconds |
| Final four-shard suite | 8 passed, 0 retries; parallel command wall time 6.211 seconds |
| Merged report | Contains all 8 scenarios and links to their evidence |
| Intentional homepage failure | Run and merge returned nonzero; all 3 attempts retained screenshots and valid trace ZIPs |

Evidence is generated under ignored `test-results/` and `playwright-report/`. Browser traces were checked as ZIP archives with trace entries, and relative evidence links were checked on disk. The reports were not inspected in a hosted GitHub run.

GitHub-only evidence remains pending until the changes are published and the workflow runs there. No run URLs, hosted timings, cache hits, or passing badge states are fabricated.

## Follow-up review request

The user asked to strengthen evidence validation and per-shard actual-case checks, push a feature branch, open a PR, measure one/four-shard GitHub runs, inspect intentional-failure artifacts, and verify cache restoration, required checks and the passing default-branch badge. Evidence validation now checks every recorded attempt, including failed attempts followed by a passing retry. The repository’s actual default branch is `master`; it is preserved. Hosted outcomes will be recorded only after inspection.
