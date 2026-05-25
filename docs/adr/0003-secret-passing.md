# ADR 0003: Pass the Todoist token via environment variable

- Status: Accepted
- Date: 2026-05-25

## Context

The CLI needs a Todoist API token.

We need a way to pass the secret that keeps the first version simple, works well from shell on macOS and Linux, and avoids unnecessary exposure.

Relevant options considered:

- command-line argument
- environment variable
- config file with secret value

## Decision

Pass the Todoist token via environment variable.

## Consequences

Positive:

- simple to use from shell and scripts
- avoids exposing the token in command history as a CLI flag
- cross-platform enough for the target environments
- easy to document and test

Negative:

- environment variables can still be exposed in some process inspection scenarios
- users must manage shell setup carefully
- weaker protection than more advanced secret management approaches