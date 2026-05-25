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


class TodoistClient:
    """Small Todoist REST client."""

    def __init__(self, config: Config) -> None:
        self._config = config

    def get_projects(self) -> list[TodoistProject]:
        """Fetch all Todoist projects."""
        response_body = self._get_json("/projects")
        if not isinstance(response_body, list):
            raise TodoistClientError("Todoist projects response must be a list")

        projects: list[TodoistProject] = []
        for item in response_body:
            if not isinstance(item, dict):
                raise TodoistClientError("Todoist project entry must be an object")

            project_id = item.get("id")
            project_name = item.get("name")
            if project_id is None or not isinstance(project_name, str) or not project_name:
                raise TodoistClientError("Todoist project entry is missing required fields")

            projects.append(TodoistProject(id=str(project_id), name=project_name))

        return projects

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

