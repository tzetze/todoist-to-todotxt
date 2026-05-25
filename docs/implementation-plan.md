# Implementation Plan

This document describes the planned implementation details and delivery sequence for the current solution shape. For decision rationale, refer to the ADRs under `docs/adr/`.

## Scope

Build the tool in small phases. Each phase should stay useful, testable, and limited to the data it really needs.

## Current baseline

Done:

- repository initialized
- Python chosen
- `venv` with `pyproject.toml` chosen
- initial ADRs written
- architecture plan written

## Phase 1: Todoist read POC

Goal:

- prove the CLI can authenticate to [`Todoist`](https://todoist.com)
- fetch projects and tasks
- expose the raw fetched data in a simple way
- avoid internal models and avoid [`todo.txt`](http://todotxt.org) output for now

### Phase 1 / Stage 1

Deliver:

- minimal CLI entry point
- config loading from environment
- simple error handling

Proposed example call:

```bash
todoist-to-todotxt
```

Tests:

- config validation tests
- CLI smoke tests

### Phase 1 / Stage 2

Deliver:

- Todoist client for basic project reads
- mocked HTTP tests for project reads

### Phase 1 / Stage 3

Deliver:

- Todoist client for basic task reads
- mocked HTTP tests for task reads

### Phase 1 / Stage 4

Deliver:

- simple CLI command that executes the read flow
- simple output of fetched data for manual inspection
- end-to-end smoke test for the POC flow

## Phase 2: Basic export

Goal:

- generate a first local [`todo.txt`](http://todotxt.org) file
- support basic project and simple todo export
- focus on title and description only

### Phase 2 / Stage 1

Deliver:

- introduce only the internal structures needed for basic export
- define first basic mapping rules

Proposed example call:

```bash
todoist-to-todotxt
```

Optional output override:

```bash
todoist-to-todotxt --output custom-todo.txt
```

Tests:

- mapper tests

### Phase 2 / Stage 2

Deliver:

- render basic `todo.txt` output

Tests:

- renderer tests
- fixture-based output tests

### Phase 2 / Stage 3

Deliver:

- atomically write the output file
- complete the CLI export flow
- make `--output` optional with default value `todo.txt`

Tests:

- atomic file write tests
- end-to-end export tests

## Later phases

Possible next topics:

- due dates
- priority mapping
- labels or contexts
- completed task handling
- comments or other separately fetched data
- formatting refinements

Rule:

- each new feature gets its own phase or stage when the scope is clear
- model only the data needed for the current phase
- add tests in the same phase that introduces the behavior

## Module plan by maturity

Early modules:

- `cli.py`
- `config.py`
- `todoist_client.py`

Modules introduced in export phases:

- `models.py`
- `mapper.py`
- `renderer.py`
- `writer.py`

Keep modules absent until they are justified by the current phase.

## Configuration plan

Initial environment variable:

- `TODOIST_API_TOKEN` for the Todoist API token


## Working style

- keep phases and stages small
- review decisions before locking them
- commit frequently
- push regularly