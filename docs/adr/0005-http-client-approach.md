# ADR 0005: HTTP client approach for Todoist reads

- Status: Accepted
- Date: 2026-05-25

## Context

We need a small HTTP client for reading Todoist projects.
We have two real options worth considering now:

- use Python standard library HTTP support via `urllib.request`
- add a small third-party HTTP client such as `httpx`

This choice affects implementation simplicity, dependency management, and how easy it is to write isolated tests for Todoist API reads.

## Decision drivers

- keep the tool small
- keep maintenance burden low
- keep tests easy to write and understand
- avoid unnecessary dependencies
- leave room for future Todoist API reads

## Decision

Use `urllib.request` for Todoist HTTP reads.

## Consequences

- we avoid adding a runtime dependency
- we rely on a standard library module that is stable and likely to remain supported long term
- request and response handling will be more low-level and less ergonomic than with `httpx`
- isolated HTTP mocking may be more awkward than with `httpx` mock transports
- future API work may require more boilerplate than a higher-level HTTP client would
- if the HTTP layer becomes harder to maintain or test, switching to `httpx` remains an acceptable later change