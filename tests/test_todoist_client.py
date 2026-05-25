from __future__ import annotations

import json
from urllib import error

import pytest

from email.message import Message

from todoist_to_todotxt.config import Config
from todoist_to_todotxt.todoist_client import (
    TodoistClient,
    TodoistClientError,
    TodoistProject,
    TodoistTask,
)


class FakeResponse:
    def __init__(self, body: str) -> None:
        self._body = body

    def read(self) -> bytes:
        return self._body.encode("utf-8")

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def make_config() -> Config:
    return Config(
        todoist_api_token="secret-token",
        token_source="test",
        todoist_api_base_url="https://example.test",
    )


def test_get_projects_returns_projects(monkeypatch) -> None:
    client = TodoistClient(make_config())

    def fake_urlopen(http_request):
        assert http_request.full_url == "https://example.test/projects"
        assert http_request.get_method() == "GET"
        assert http_request.headers["Authorization"] == "Bearer secret-token"
        return FakeResponse(
            json.dumps(
                {
                    "results": [
                        {"id": "1001", "name": "Inbox"},
                        {"id": 1002, "name": "Work"},
                    ],
                    "next_cursor": None,
                }
            )
        )

    monkeypatch.setattr("todoist_to_todotxt.todoist_client.request.urlopen", fake_urlopen)

    projects = client.get_projects()

    assert projects == [
        TodoistProject(id="1001", name="Inbox"),
        TodoistProject(id="1002", name="Work"),
    ]


def test_get_projects_raises_for_http_error(monkeypatch) -> None:
    client = TodoistClient(make_config())

    def fake_urlopen(http_request):
        raise error.HTTPError(
            url=http_request.full_url,
            code=401,
            msg="Unauthorized",
            hdrs=Message(),
            fp=None,
        )

    monkeypatch.setattr("todoist_to_todotxt.todoist_client.request.urlopen", fake_urlopen)

    with pytest.raises(TodoistClientError, match="status 401"):
        client.get_projects()


def test_get_projects_raises_for_invalid_json(monkeypatch) -> None:
    client = TodoistClient(make_config())

    def fake_urlopen(http_request):
        return FakeResponse("not-json")

    monkeypatch.setattr("todoist_to_todotxt.todoist_client.request.urlopen", fake_urlopen)

    with pytest.raises(TodoistClientError, match="not valid JSON"):
        client.get_projects()


def test_get_projects_raises_for_missing_required_fields(monkeypatch) -> None:
    client = TodoistClient(make_config())

    def fake_urlopen(http_request):
        return FakeResponse(json.dumps({"results": [{"id": "1001"}], "next_cursor": None}))

    monkeypatch.setattr("todoist_to_todotxt.todoist_client.request.urlopen", fake_urlopen)

    with pytest.raises(TodoistClientError, match="missing required fields"):
        client.get_projects()




def test_get_active_tasks_returns_tasks(monkeypatch) -> None:
    client = TodoistClient(make_config())

    def fake_urlopen(http_request):
        assert http_request.full_url == "https://example.test/tasks"
        assert http_request.get_method() == "GET"
        assert http_request.headers["Authorization"] == "Bearer secret-token"
        return FakeResponse(
            json.dumps(
                {
                    "results": [
                        {"id": "2001", "content": "Buy milk", "project_id": "1001"},
                        {"id": 2002, "content": "Write report", "project_id": 1002},
                    ],
                    "next_cursor": None,
                }
            )
        )

    monkeypatch.setattr("todoist_to_todotxt.todoist_client.request.urlopen", fake_urlopen)

    tasks = client.get_active_tasks()

    assert tasks == [
        TodoistTask(id="2001", content="Buy milk", project_id="1001"),
        TodoistTask(id="2002", content="Write report", project_id="1002"),
    ]


def test_get_active_tasks_returns_empty_list(monkeypatch) -> None:
    client = TodoistClient(make_config())

    def fake_urlopen(http_request):
        return FakeResponse(json.dumps({"results": [], "next_cursor": None}))

    monkeypatch.setattr("todoist_to_todotxt.todoist_client.request.urlopen", fake_urlopen)

    tasks = client.get_active_tasks()

    assert tasks == []


def test_get_active_tasks_raises_for_http_error(monkeypatch) -> None:
    client = TodoistClient(make_config())

    def fake_urlopen(http_request):
        raise error.HTTPError(
            url=http_request.full_url,
            code=403,
            msg="Forbidden",
            hdrs=Message(),
            fp=None,
        )

    monkeypatch.setattr("todoist_to_todotxt.todoist_client.request.urlopen", fake_urlopen)

    with pytest.raises(TodoistClientError, match="status 403"):
        client.get_active_tasks()


def test_get_active_tasks_raises_for_invalid_json(monkeypatch) -> None:
    client = TodoistClient(make_config())

    def fake_urlopen(http_request):
        return FakeResponse("invalid-json")

    monkeypatch.setattr("todoist_to_todotxt.todoist_client.request.urlopen", fake_urlopen)

    with pytest.raises(TodoistClientError, match="not valid JSON"):
        client.get_active_tasks()


def test_get_active_tasks_raises_for_missing_required_fields(monkeypatch) -> None:
    client = TodoistClient(make_config())

    def fake_urlopen(http_request):
        return FakeResponse(
            json.dumps({"results": [{"id": "2001", "content": "Buy milk"}], "next_cursor": None})
        )

    monkeypatch.setattr("todoist_to_todotxt.todoist_client.request.urlopen", fake_urlopen)

    with pytest.raises(TodoistClientError, match="missing required fields"):
        client.get_active_tasks()


def test_get_active_tasks_raises_for_non_list_response(monkeypatch) -> None:
    client = TodoistClient(make_config())

    def fake_urlopen(http_request):
        return FakeResponse(json.dumps({"error": "not an object with results"}))

    monkeypatch.setattr("todoist_to_todotxt.todoist_client.request.urlopen", fake_urlopen)

    with pytest.raises(TodoistClientError, match="tasks response must contain a results list"):
        client.get_active_tasks()



def test_get_projects_handles_pagination(monkeypatch) -> None:
    client = TodoistClient(make_config())
    call_count = 0

    def fake_urlopen(http_request):
        nonlocal call_count
        call_count += 1

        if call_count == 1:
            # First page
            assert "cursor=" not in http_request.full_url
            return FakeResponse(
                json.dumps(
                    {
                        "results": [{"id": "1001", "name": "Inbox"}],
                        "next_cursor": "page2_cursor",
                    }
                )
            )
        elif call_count == 2:
            # Second page
            assert "cursor=page2_cursor" in http_request.full_url
            return FakeResponse(
                json.dumps(
                    {
                        "results": [{"id": "1002", "name": "Work"}],
                        "next_cursor": None,
                    }
                )
            )
        raise ValueError(f"Unexpected call count: {call_count}")

    monkeypatch.setattr("todoist_to_todotxt.todoist_client.request.urlopen", fake_urlopen)

    projects = client.get_projects()

    assert len(projects) == 2
    assert projects[0] == TodoistProject(id="1001", name="Inbox")
    assert projects[1] == TodoistProject(id="1002", name="Work")
    assert call_count == 2


def test_get_active_tasks_handles_pagination(monkeypatch) -> None:
    client = TodoistClient(make_config())
    call_count = 0

    def fake_urlopen(http_request):
        nonlocal call_count
        call_count += 1

        if call_count == 1:
            # First page
            assert "cursor=" not in http_request.full_url
            return FakeResponse(
                json.dumps(
                    {
                        "results": [{"id": "2001", "content": "Task 1", "project_id": "1001"}],
                        "next_cursor": "page2_cursor",
                    }
                )
            )
        elif call_count == 2:
            # Second page
            assert "cursor=page2_cursor" in http_request.full_url
            return FakeResponse(
                json.dumps(
                    {
                        "results": [{"id": "2002", "content": "Task 2", "project_id": "1002"}],
                        "next_cursor": "page3_cursor",
                    }
                )
            )
        elif call_count == 3:
            # Third page (empty, end of pagination)
            assert "cursor=page3_cursor" in http_request.full_url
            return FakeResponse(
                json.dumps(
                    {
                        "results": [{"id": "2003", "content": "Task 3", "project_id": "1001"}],
                        "next_cursor": None,
                    }
                )
            )
        raise ValueError(f"Unexpected call count: {call_count}")

    monkeypatch.setattr("todoist_to_todotxt.todoist_client.request.urlopen", fake_urlopen)

    tasks = client.get_active_tasks()

    assert len(tasks) == 3
    assert tasks[0] == TodoistTask(id="2001", content="Task 1", project_id="1001")
    assert tasks[1] == TodoistTask(id="2002", content="Task 2", project_id="1002")
    assert tasks[2] == TodoistTask(id="2003", content="Task 3", project_id="1001")
    assert call_count == 3
