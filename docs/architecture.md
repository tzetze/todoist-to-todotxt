# Architecture Plan

This document describes the current target architecture of the project. It captures the current solution shape only.
For decision background and rationale, refer to the ADRs under `docs/adr/`.

## Goal

Build a read-only CLI that fetches data from [`Todoist`](https://todoist.com) and writes a local [`todo.txt`](http://todotxt.org) file.

First version non-goals:

- write back to Todoist
- bidirectional sync
- background service
- hosted or multi-user deployment

## Runtime flow

A run should:

1. load config and credentials
2. fetch [`Todoist`](https://todoist.com) projects and tasks
3. map API data into internal models
4. render `todo.txt` lines
5. write the target file atomically
6. exit with useful status and errors

## Components

### CLI

Parses arguments, loads config, starts the export, prints concise errors, and returns exit codes.

### Todoist client

Handles authentication, API calls, and pagination, and isolates Todoist-specific behavior.

### Mapper

Converts Todoist responses into internal models and normalizes optional fields.

### Renderer

Transforms internal models into deterministic `todo.txt` output.

### Writer

Replaces the target file atomically to avoid partial output.

## Data flow

```text
CLI -> Config -> Todoist client -> Mapper -> Renderer -> Writer
```

## Configuration

Current required input:

- Todoist API token

## Errors

Handle and report:

- invalid config
- auth, network, or API failures
- unexpected API payloads
- render failures
- file write failures

On failure, return non-zero exit code and leave existing output untouched.

## Python environment and dependencies

Use `venv` for local isolation and `pyproject.toml` as the canonical project and dependency definition.

## Testing

Plan tests from the start:

- unit tests for mapping
- unit tests for rendering
- mocked HTTP tests for the Todoist client
- file write tests for atomic replacement
- end-to-end CLI tests with fixtures

Golden-file tests are a good fit for [`todo.txt`](http://todotxt.org) output.

## Proposed structure

```text
docs/
  adr/
src/
  todoist_to_todotxt/
    cli.py
    config.py
    todoist_client.py
    models.py
    mapper.py
    renderer.py
    writer.py
tests/
```
