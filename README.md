# todoist-to-todotxt

Export your [`Todoist`](https://todoist.com) tasks into [`todo.txt`](http://todotxt.org) with a small local CLI.

## Why this project exists

This is an AI-assisted, spec-driven experiment with the main goal of helping users migrate from Todoist into the open [`todo.txt`](http://todotxt.org) ecosystem. It is also useful for anyone who wants a local backup of their Todoist content or a small CLI for working with plain-text task data.

The project specification lives under `docs/`, and the related architectural decisions are tracked under `docs/adr/`.

## Goals

- read data from [`Todoist`](https://todoist.com)
- generate a local [`todo.txt`](http://todotxt.org) file
- keep the tool small, transparent, and automation-friendly

## Setup for a fresh clone

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Current local usage

```bash
TODOIST_API_TOKEN='your-token-here' .venv/bin/todoist-to-todotxt
```

Current behavior:
- exits with code `2` if `TODOIST_API_TOKEN` is missing
- prints a configuration-loaded message when the token is present
