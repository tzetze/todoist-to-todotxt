# Open Questions

This document collects open questions that are not yet fixed by the current architecture, implementation plan, or ADRs.

## Product and behavior

- what the first basic [`todo.txt`](http://todotxt.org) line format should be
- when descriptions should become part of output
- which extra Todoist fields are worth adding after the basic export works
- task sorting strategy: The Todoist API itself returns tasks as they appear in the system and does not directly support server-side sorting parameters. Consider client-side sorting options (by project, by date, by priority, etc.)

## Data mapping

- final Todoist to [`todo.txt`](http://todotxt.org) mapping rules
- how projects, labels, priorities, and due dates should appear