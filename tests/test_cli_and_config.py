from __future__ import annotations

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

    exit_code = main()

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "configuration loaded successfully" in captured.out
