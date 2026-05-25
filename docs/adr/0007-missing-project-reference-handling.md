# ADR 0007: Missing project reference handling

- Status: Accepted
- Date: 2026-05-25

## Context

Tasks in Todoist contain a `project_id` field that references a project. During export, we need to resolve these references to show human-readable project names.

However, data inconsistencies can occur:
- A task references a project_id that doesn't exist in the projects list
- API pagination issues (unlikely with current API but possible)
- Race conditions if data changes between API calls
- Todoist API bugs or data corruption

We need to decide how to handle tasks with unresolvable project references.

## Alternatives

1. **Fail the entire export** - abort if any task has an invalid project reference
2. **Skip invalid tasks silently** - omit tasks with missing project references
3. **Use placeholder and log warning** - show task with placeholder project name, log warning
4. **Use placeholder silently** - show task with placeholder, no warning

## Decision

Use a placeholder project name and log a warning to stderr.

When a task references a non-existent project_id:
- Display the task with a placeholder like `[Unknown Project]`
- Log a warning to stderr with the task_id and invalid project_id
- Continue processing remaining tasks
- Exit successfully if no other errors occur

## Consequences

Positive:
- users get maximum data even with Todoist inconsistencies
- warnings help identify and report data issues
- partial success is better than complete failure for data quality issues
- users can still use the export and investigate problems later

Negative:
- output may contain placeholder values
- users need to check stderr for warnings
- doesn't prevent the issue, only works around it

## Rationale

Unlike API failures (ADR 0006), data inconsistencies are likely rare and may be temporary. Failing the entire export would be too harsh for what might be a single corrupted task.

The placeholder approach balances robustness with transparency:
- Users get their data
- Problems are visible via warnings
- Issues can be reported to Todoist or investigated

This aligns with the principle of being liberal in what we accept while still being transparent about problems.