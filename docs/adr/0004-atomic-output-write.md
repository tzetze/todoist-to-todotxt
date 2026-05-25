# ADR 0004: Write todo.txt atomically

- Status: Accepted
- Date: 2026-05-25

## Context

We need to decide whether to write the target file directly or replace it atomically after a successful temporary write.

Relevant options considered:

- direct overwrite of the target file
- atomic replace after writing a temporary file

## Decision

Write the output to a temporary file and replace the target file only after the write succeeds.

## Consequences

Positive:

- avoids partially written output files
- keeps the previous file if generation or write fails
- makes failures safer for repeated local use

Negative:

- slightly more implementation complexity
- requires temporary file handling
- some file metadata behavior may differ after replacement