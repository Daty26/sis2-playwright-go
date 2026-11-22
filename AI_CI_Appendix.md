# AI use appendix — Playwright Go CI assignment

## Scope of AI assistance

I used AI in more than one chat for this assignment. The assistance included explanations, generated implementation code, configuration, documentation, and code review. AI use was not limited to spelling or formatting.

In another chat, I used AI to generate a Python helper for orchestrating the Go tests, including retries and handling flaky results, and to generate Docker Compose configuration for the test application. In this chat, I asked for explanations of the lecture and assignment, a Go adaptation of the supplied step-by-step guide, and reviews of my implementation. I also asked AI to draft this appendix.

This appendix distinguishes the prompts available in this chat from the other chat's history, which was not available when this appendix was written.

## Tools and models

- This chat: OpenAI Codex desktop application, identified in the session as GPT-6-based Codex. A more specific model version was not recorded here.
- Other chat: AI assistance confirmed by me for the Python helper, flaky-test handling, and Docker Compose. The exact application, model/version, settings, and full prompts were not supplied in this chat.
- Date of this record: 21 November 2026.

I have not inferred the other chat's model or reconstructed its prompts as quotations.

## Inputs supplied to AI

- The Week 10 lecture on CI/CD and QA in DevOps.
- The supplied PDF, *SIS 2: CI pipeline for Playwright — step-by-step guide*.
- The existing SIS2 repository, which uses Playwright Go and Go's `testing` package.
- My questions and implementation files during review.

## Where AI contributed

| Area | Assistance and resulting implementation |
| --- | --- |
| Assignment understanding | Explained CI/CD, artifacts, merge gates, sharding, and the submission requirements. |
| Go adaptation | Explained why the TypeScript guide cannot be copied directly: Go's test runner has no `test.only`, Playwright Test configuration, native Playwright sharding, or its HTML/blob reporters. Generated a separate Go guide and reference examples. |
| Python orchestration | Generated assistance in another chat contributed to `ci/runner.py`: test discovery, shard selection, running `go test -json`, retry handling, and report generation. The repository uses this Python helper rather than the Go-only reference helper generated in this chat. |
| Flaky-result handling | Assisted with preserving failed attempts, retrying failed tests, and labeling a test as flaky when it later passes. The implemented policy reports such tests with a warning; persistent failures remain blocking. |
| Docker Compose | Generated assistance in another chat contributed to `ci/compose.yml`, which defines the disposable database, API, web server, and frontend used by the tests. |
| Review and validation | Inspected the workflow, fixture, helper, reports, and documentation; ran code checks; identified missing validation and submission evidence. |
| Documentation | Generated this appendix and earlier explanatory material. |

This record does not claim that every line in the repository was written independently, or that the assistant had access to the full history of the other chat.

## Prompts available from this chat

The following are actual requests from this chat, reproduced with their original wording:

> summarize the lecture and explain the concepts

> explain me the SIS 3

> can you check added test.yaml

> I will do on my own you will check and help

> can you generate the same step by step guideline but in go?

> can you check what I did accroding to your guid

> check did I finish all ?

The request for this appendix also disclosed that I had used AI in a different chat to generate the Python helper, flaky-test handling, and Docker Compose.

### Other chat's prompt history

The other chat's exact prompts and responses are not included here because they were not available to this assistant. The description above is my disclosure of its scope, not a verbatim transcript. If the course requires the complete prompts and corrections, this appendix must be supplemented with the relevant messages or an export from that chat. Any credentials or tokens should be redacted in that record.

## Corrections and decisions recorded during review

1. **Application HTML versus a results report.** A captured `page.html` contains the application's page, not a test-results summary. The implementation generates separate HTML and JUnit results and retains page HTML as failure evidence.
2. **Go-specific equivalents.** The implementation documents its Python orchestration and custom reports instead of claiming that it uses the JavaScript runner's `forbidOnly`, blob reporter, or native `--shard` flag.
3. **Preserving retries.** A successful retry must not overwrite the original failure. Attempts have separate evidence directories and remain visible in the reports.
4. **Missing evidence.** Review demonstrated that a passing summary without a trace could originally produce a successful report. Validation was added for required logs, trace archives, and failed-attempt screenshots/page HTML, including failures followed by successful retries.
5. **Actual shard coverage.** Review demonstrated that swapped case lists could pass a global coverage check. Validation was added to compare each shard's actual case names with its assigned selection.
6. **Flaky-test policy.** The generated Go reference guide used a stricter policy that blocked flaky results. The repository instead warns about a test that passes on retry. This difference is documented in the README; it is not described as identical behavior.
7. **Hosted evidence.** Successful runs of an earlier implementation do not establish that a later revision passes. Runtime measurements, run links, cache restoration, and the default-branch badge must be checked against the submitted version.

## Verification and limits

During review in this chat, the assistant observed 13 passing helper tests, successful Go compilation without executing the browser scenarios, a successful `go vet`, and a successful Actionlint check. The helper tests included missing/invalid trace detection, preservation of original failure evidence, and incorrect per-shard execution.

These observations apply to the files at the time of that review. They are not a claim that every later edit has been retested, or that the final browser suite and workflow have passed on GitHub. At the latest completion review, the README still contained unfilled hosted timing measurements, and the successful hosted runs inspected belonged to an earlier commit.

No GitHub timings, cache hits, trace-viewer inspections, or passing final badge states are invented in this appendix. The README and actual run links should provide the final submission evidence.

I remain responsible for understanding the generated code, checking it against the assignment requirements, and accurately reporting what I implemented and verified.
