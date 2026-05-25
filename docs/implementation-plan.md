# Implementation Plan

This document describes the planned implementation details for the current solution shape. For decision rationale, refer to the ADRs under `docs/adr/`.

## Scope

Build the tool in small phases. Each phase should stay useful, testable, and limited to the data it really needs.

## Phase 1: Todoist read POC

Goal:

- prove the CLI can authenticate to [`Todoist`](https://todoist.com)
- fetch projects and tasks
- print or otherwise expose the raw fetched data in a simple way
- avoid internal models and avoid [`todo.txt`](http://todotxt.org) output for now

Planned work:

- minimal CLI entry point
- config loading from environment
- Todoist client for basic read operations
- simple error handling
- tests for config validation and mocked Todoist reads

## Phase 2: Basic export

Goal:

- generate a first local [`todo.txt`](http://todotxt.org) file
- support basic project and simple todo export
- focus on title and description only

Planned work:

- introduce only the internal structures needed for basic export
- map Todoist projects and tasks into basic export input
- render basic `todo.txt` output
- write output atomically
- tests for mapping, rendering, and file writing

## Later phases

Add features step by step only when needed.

Possible next phases:

- due date support
- priority mapping
- labels or contexts
- completed task handling
- comments or other separately fetched data
- richer formatting options

Each feature should be introduced together with the smallest necessary model changes and tests.

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

Initial environment variables:

- `TODOIST_API_TOKEN`
- `TODOTXT_OUTPUT_PATH` for export phases

Add more only when a real phase needs them.

## Testing plan

Phase 1:

- config validation tests
- Todoist client tests with mocked HTTP
- CLI smoke tests

Phase 2:

- mapper tests
- renderer tests
- atomic file write tests
- end-to-end export tests with fixture payloads

Later phases:

- add tests together with each new data type or formatting rule

## Open questions

- which Todoist endpoints give the simplest first read path
- what the first basic `todo.txt` line format should be
- when descriptions should become part of output
- which extra Todoist fields are worth adding after the basic export works