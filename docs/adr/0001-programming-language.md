# ADR 0001: Use Python

- Status: Proposed
- Date: 2026-05-25

## Context

We are building a read-only CLI that fetches data from Todoist and writes a local `todo.txt`.

Current priorities are fast delivery, easy iteration, and solid library support for API access and testing.

## Alternatives

- Go
- Python

## Decision

Use Python for the first implementation.

## Consequences

Positive:

- fast to implement and change
- strong ecosystem for HTTP, CLI, and testing
- simple path to direct Todoist API usage
- easy to test mapping and output generation
- runs from a shell on macOS, Linux, or another compatible OS with Python 3 available

Negative:

- requires Python 3 on the target system
- less self-contained than a Go binary
- weaker static guarantees than Go