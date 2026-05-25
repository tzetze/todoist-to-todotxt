from __future__ import annotations

import json

from todoist_to_todotxt.cli import main
from todoist_to_todotxt.config import ConfigError, load_config


def test_load_config_requires_todoist_api_token(monkeypatch) -> None:
    monkeypatch.delenv("TODOIST_API_TOKEN", raising=False)

    try:
        load_config()
    except ConfigError as error:
        assert str(error) == "TODOIST_API_TOKEN is required"
    else:
        raise AssertionError("Expected ConfigError when TODOIST_API_TOKEN is missing")


def test_load_config_reads_todoist_api_token_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("TODOIST_API_TOKEN", "secret-token")

    config = load_config()

    assert config.todoist_api_token == "secret-token"
    assert config.token_source == "environment variable TODOIST_API_TOKEN"


def test_cli_returns_error_when_config_is_missing(monkeypatch, capsys) -> None:
    monkeypatch.delenv("TODOIST_API_TOKEN", raising=False)

    exit_code = main()

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Configuration error: TODOIST_API_TOKEN is required" in captured.err


def test_cli_reports_success_when_config_is_present(monkeypatch, capsys) -> None:
    monkeypatch.setenv("TODOIST_API_TOKEN", "secret-token")

    # Mock successful API calls
    call_count = {"projects": 0, "tasks": 0}

    def fake_urlopen(http_request):
        if "/projects" in http_request.full_url:
            call_count["projects"] += 1
            return FakeResponse(
                json.dumps({"results": [{"id": "1001", "name": "Inbox"}], "next_cursor": None})
            )
        elif "/tasks" in http_request.full_url:
            call_count["tasks"] += 1
            return FakeResponse(
                json.dumps(
                    {
                        "results": [{"id": "2001", "content": "Buy milk", "project_id": "1001"}],
                        "next_cursor": None,
                    }
                )
            )
        raise ValueError(f"Unexpected URL: {http_request.full_url}")

    monkeypatch.setattr("todoist_to_todotxt.todoist_client.request.urlopen", fake_urlopen)

    exit_code = main()

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Fetched 1 projects and 1 active tasks" in captured.out
    assert "[Inbox] Buy milk (id: 2001)" in captured.out
    assert call_count["projects"] == 1
    assert call_count["tasks"] == 1


def test_cli_end_to_end_with_multiple_tasks(monkeypatch, capsys) -> None:
    monkeypatch.setenv("TODOIST_API_TOKEN", "secret-token")

    def fake_urlopen(http_request):
        if "/projects" in http_request.full_url:
            return FakeResponse(
                json.dumps(
                    {
                        "results": [
                            {"id": "1001", "name": "Inbox"},
                            {"id": "1002", "name": "Work"},
                        ],
                        "next_cursor": None,
                    }
                )
            )
        elif "/tasks" in http_request.full_url:
            return FakeResponse(
                json.dumps(
                    {
                        "results": [
                            {"id": "2001", "content": "Buy milk", "project_id": "1001"},
                            {"id": "2002", "content": "Write report", "project_id": "1002"},
                            {"id": "2003", "content": "Call dentist", "project_id": "1001"},
                        ],
                        "next_cursor": None,
                    }
                )
            )
        raise ValueError(f"Unexpected URL: {http_request.full_url}")

    monkeypatch.setattr("todoist_to_todotxt.todoist_client.request.urlopen", fake_urlopen)

    exit_code = main()

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Fetched 2 projects and 3 active tasks" in captured.out
    assert "[Inbox] Buy milk (id: 2001)" in captured.out
    assert "[Work] Write report (id: 2002)" in captured.out
    assert "[Inbox] Call dentist (id: 2003)" in captured.out


def test_cli_handles_missing_project_reference(monkeypatch, capsys) -> None:
    monkeypatch.setenv("TODOIST_API_TOKEN", "secret-token")

    def fake_urlopen(http_request):
        if "/projects" in http_request.full_url:
            return FakeResponse(
                json.dumps({"results": [{"id": "1001", "name": "Inbox"}], "next_cursor": None})
            )
        elif "/tasks" in http_request.full_url:
            return FakeResponse(
                json.dumps(
                    {
                        "results": [
                            {"id": "2001", "content": "Buy milk", "project_id": "1001"},
                            {"id": "2002", "content": "Orphaned task", "project_id": "9999"},
                        ],
                        "next_cursor": None,
                    }
                )
            )
        raise ValueError(f"Unexpected URL: {http_request.full_url}")

    monkeypatch.setattr("todoist_to_todotxt.todoist_client.request.urlopen", fake_urlopen)

    exit_code = main()

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "[Inbox] Buy milk (id: 2001)" in captured.out
    assert "[[Unknown Project]] Orphaned task (id: 2002)" in captured.out
    assert "Warning: Task 2002 references unknown project 9999" in captured.err


def test_cli_fails_when_projects_fetch_fails(monkeypatch, capsys) -> None:
    monkeypatch.setenv("TODOIST_API_TOKEN", "secret-token")

    def fake_urlopen(http_request):
        from urllib.error import HTTPError
        from email.message import Message

        raise HTTPError(
            url=http_request.full_url,
            code=401,
            msg="Unauthorized",
            hdrs=Message(),
            fp=None,
        )

    monkeypatch.setattr("todoist_to_todotxt.todoist_client.request.urlopen", fake_urlopen)

    exit_code = main()

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Failed to fetch projects" in captured.err
    assert "status 401" in captured.err


def test_cli_fails_when_tasks_fetch_fails(monkeypatch, capsys) -> None:
    monkeypatch.setenv("TODOIST_API_TOKEN", "secret-token")

    def fake_urlopen(http_request):
        if "/projects" in http_request.full_url:
            return FakeResponse(
                json.dumps({"results": [{"id": "1001", "name": "Inbox"}], "next_cursor": None})
            )
        elif "/tasks" in http_request.full_url:
            from urllib.error import HTTPError
            from email.message import Message

            raise HTTPError(
                url=http_request.full_url,
                code=500,
                msg="Internal Server Error",
                hdrs=Message(),
                fp=None,
            )
        raise ValueError(f"Unexpected URL: {http_request.full_url}")

    monkeypatch.setattr("todoist_to_todotxt.todoist_client.request.urlopen", fake_urlopen)

    exit_code = main()

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Failed to fetch tasks" in captured.err
    assert "status 500" in captured.err


class FakeResponse:
    def __init__(self, body: str) -> None:
        self._body = body

    def read(self) -> bytes:
        return self._body.encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None
