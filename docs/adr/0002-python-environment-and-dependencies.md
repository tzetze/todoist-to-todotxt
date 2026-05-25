# ADR 0002: Use pyproject.toml with venv

- Status: Accepted
- Date: 2026-05-25

## Context

We need a simple but maintainable way to manage the Python environment and dependencies for a small CLI run from shell.

Relevant options considered:

- `venv` + `pip` + requirements files
- `pyproject.toml` based project configuration

## Decision

Use `venv` for local environment isolation and `pyproject.toml` as the primary place for project metadata and dependencies.

## Consequences

Positive:

- modern standard Python project layout
- one main place for dependencies and project config
- scales better if tooling, packaging, or entry points grow later
- still simple enough for a small CLI

Negative:

- slightly more setup choice up front
- may feel heavier than plain requirements files for a very small project
- exact supporting tool choice may still need to be decided