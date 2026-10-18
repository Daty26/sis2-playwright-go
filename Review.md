# AI Review

## AI assistance

AI helped explain the assignment, plan the structure, suggest page objects and fixtures, review code, debug failures, and draft documentation. Tool/model details and the redacted prompt record are in [Prompt.md](Prompt.md). An AI-generated implementation was reverted; development then continued step by step.

## Review and corrections

- Checked suggested selectors against the real website and kept browser interactions inside page objects.
- Added resource cleanup, isolated contexts, and unique emails so tests can run independently.
- Corrected the price comparison to Combination Pliers > Pliers, based on observed prices of $14.15 and $12.01.
- Replaced the premature house-number value assertion with a visibility check, then waited for postcode lookup before filling the remaining address fields.
- Checked invoice confirmation after payment validation to prove checkout completion.
- Kept the observed reset confirmation key as the expected text and recorded it as an application translation issue.

These choices keep tests readable and verify outcomes instead of only clicking through pages.


