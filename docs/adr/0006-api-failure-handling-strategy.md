# ADR 0006: API failure handling strategy

- Status: Accepted
- Date: 2026-05-25

## Context

We need to decide how to handle API failures when fetching data from Todoist.

The tool performs multiple sequential API calls:
1. Fetch all projects
2. Fetch all active tasks

Each call can fail due to network issues, authentication problems, or API errors.

We already decided to use atomic file writes (ADR 0004), which means we either write a complete, valid output file or leave the existing file untouched.

## Decision drivers

- consistency with atomic write approach
- predictable behavior for users
- avoid partial or corrupted output
- clear error reporting

## Decision

Fail fast on any API error.

If any API call fails (projects or tasks), abort the entire operation immediately and return a non-zero exit code. Do not write any output file.

## Consequences

Positive:
- consistent with atomic write philosophy from ADR 0004
- users get complete data or nothing, never partial data
- simpler error handling logic
- clear failure modes

Negative:
- if tasks fetch fails after projects succeed, we discard the project data
- no graceful degradation for partial failures

## Rationale

The atomic write approach already establishes that we prefer all-or-nothing behavior. Failing fast on API errors maintains this principle throughout the entire data pipeline, not just at the write stage.

Users can rely on the tool's behavior: if it exits successfully, the output file contains complete, consistent data. If it fails, the previous output (if any) remains unchanged.