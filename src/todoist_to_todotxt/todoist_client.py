from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib import error, request

from todoist_to_todotxt.config import Config


class TodoistClientError(RuntimeError):
    """Raised when a Todoist API request fails."""


@dataclass(frozen=True)
class TodoistProject:
    """Minimal Todoist project representation for read operations."""

    id: str
    name: str


@dataclass(frozen=True)
class TodoistTask:
    """Minimal Todoist task representation for read operations."""

    id: str
    content: str
    project_id: str


class TodoistClient:
    """Small Todoist REST client."""

    def __init__(self, config: Config) -> None:
        self._config = config

    def get_projects(self) -> list[TodoistProject]:
        """Fetch all Todoist projects."""
        all_results = self._get_all_pages("/projects")

        projects: list[TodoistProject] = []
        for item in all_results:
            if not isinstance(item, dict):
                raise TodoistClientError("Todoist project entry must be an object")

            project_id = item.get("id")
            project_name = item.get("name")
            if project_id is None or not isinstance(project_name, str) or not project_name:
                raise TodoistClientError("Todoist project entry is missing required fields")

            projects.append(TodoistProject(id=str(project_id), name=project_name))

        return projects

    def get_active_tasks(self) -> list[TodoistTask]:
        """Fetch all active Todoist tasks."""
        all_results = self._get_all_pages("/tasks")

        tasks: list[TodoistTask] = []
        for item in all_results:
            if not isinstance(item, dict):
                raise TodoistClientError("Todoist task entry must be an object")

            task_id = item.get("id")
            task_content = item.get("content")
            task_project_id = item.get("project_id")
            if (
                task_id is None
                or not isinstance(task_content, str)
                or not task_content
                or task_project_id is None
            ):
                raise TodoistClientError("Todoist task entry is missing required fields")

            tasks.append(
                TodoistTask(
                    id=str(task_id),
                    content=task_content,
                    project_id=str(task_project_id),
                )
            )

        return tasks

    def _get_all_pages(self, path: str) -> list[Any]:
        """Fetch all pages from a paginated endpoint."""
        all_results: list[Any] = []
        cursor: str | None = None

        while True:
            # Add cursor parameter if we have one
            request_path = path
            if cursor:
                separator = "&" if "?" in path else "?"
                request_path = f"{path}{separator}cursor={cursor}"

            response_body = self._get_json(request_path)

            # New API wraps response in an object with "results" array
            if not isinstance(response_body, dict):
                raise TodoistClientError(f"Todoist {path} response must be an object")

            results = response_body.get("results")
            if not isinstance(results, list):
                raise TodoistClientError(f"Todoist {path} response must contain a results list")

            all_results.extend(results)

            # Check if there are more pages
            next_cursor = response_body.get("next_cursor")
            if next_cursor is None or next_cursor == "":
                break

            cursor = next_cursor

        return all_results

    def _get_json(self, path: str) -> Any:
        request_url = f"{self._config.todoist_api_base_url}{path}"
        http_request = request.Request(
            request_url,
            headers={
                "Authorization": f"Bearer {self._config.todoist_api_token}",
                "Accept": "application/json",
            },
            method="GET",
        )

        try:
            with request.urlopen(http_request) as response:
                response_text = response.read().decode("utf-8")
        except error.HTTPError as exc:
            raise TodoistClientError(
                f"Todoist API request failed with status {exc.code}"
            ) from exc
        except error.URLError as exc:
            raise TodoistClientError(f"Todoist API request failed: {exc.reason}") from exc

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as exc:
            raise TodoistClientError("Todoist API response is not valid JSON") from exc

