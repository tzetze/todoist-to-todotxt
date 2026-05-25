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
                [
                    {"id": "1001", "name": "Inbox"},
                    {"id": 1002, "name": "Work"},
                ]
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
        return FakeResponse(json.dumps([{"id": "1001"}]))

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
                [
                    {"id": "2001", "content": "Buy milk", "project_id": "1001"},
                    {"id": 2002, "content": "Write report", "project_id": 1002},
                ]
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
        return FakeResponse(json.dumps([]))

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
        return FakeResponse(json.dumps([{"id": "2001", "content": "Buy milk"}]))

    monkeypatch.setattr("todoist_to_todotxt.todoist_client.request.urlopen", fake_urlopen)

    with pytest.raises(TodoistClientError, match="missing required fields"):
        client.get_active_tasks()


def test_get_active_tasks_raises_for_non_list_response(monkeypatch) -> None:
    client = TodoistClient(make_config())

    def fake_urlopen(http_request):
        return FakeResponse(json.dumps({"error": "not a list"}))

    monkeypatch.setattr("todoist_to_todotxt.todoist_client.request.urlopen", fake_urlopen)

    with pytest.raises(TodoistClientError, match="tasks response must be a list"):
        client.get_active_tasks()
