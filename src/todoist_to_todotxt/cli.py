from __future__ import annotations

import sys

from todoist_to_todotxt.config import ConfigError, load_config


def main() -> int:
    """Run the CLI entry point."""
    try:
        config = load_config()
    except ConfigError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 2

    print(
        "todoist-to-todotxt: configuration loaded successfully "
        f"(token source: {config.token_source})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
