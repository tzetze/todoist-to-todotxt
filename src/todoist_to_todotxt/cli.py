from __future__ import annotations

import sys

from todoist_to_todotxt.config import ConfigError, load_config
from todoist_to_todotxt.todoist_client import TodoistClient, TodoistClientError


def main() -> int:
    """Run the CLI entry point."""
    try:
        config = load_config()
    except ConfigError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 2

    client = TodoistClient(config)

    # Fetch projects first (fail fast per ADR 0006)
    try:
        projects = client.get_projects()
    except TodoistClientError as error:
        print(f"Failed to fetch projects: {error}", file=sys.stderr)
        return 1

    # Build project lookup
    project_lookup = {project.id: project.name for project in projects}

    # Fetch active tasks (fail fast per ADR 0006)
    try:
        tasks = client.get_active_tasks()
    except TodoistClientError as error:
        print(f"Failed to fetch tasks: {error}", file=sys.stderr)
        return 1

    # Print summary
    print(f"Fetched {len(projects)} projects and {len(tasks)} active tasks")
    print()

    # Print tasks with resolved project names
    for task in tasks:
        project_name = project_lookup.get(task.project_id)
        if project_name is None:
            # Handle missing project reference per ADR 0007
            project_name = "[Unknown Project]"
            print(
                f"Warning: Task {task.id} references unknown project {task.project_id}",
                file=sys.stderr,
            )

        print(f"[{project_name}] {task.content} (id: {task.id})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
