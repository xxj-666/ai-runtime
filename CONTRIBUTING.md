# Contributing to ai-runtime

Thank you for helping build a small, credible provider-neutral agent runtime.
The project is early-stage, so concise proposals and focused changes are the
most useful contributions.

## Development setup

Install Python 3.11 or newer and [uv](https://docs.astral.sh/uv/), then:

```bash
git clone https://github.com/xxj-666/ai-runtime.git
cd ai-runtime
uv sync
```

To work on the optional OpenAI adapter:

```bash
uv sync --extra openai
```

No API key is required for normal development or CI.

## Tests and linting

Run all checks before opening a pull request:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run python examples/basic_runtime.py
```

Use `uv run ruff format .` to apply the formatter.

## Bugs

Use the bug-report template and include:

- expected and actual behavior;
- minimal reproduction steps;
- Python, operating-system, and ai-runtime versions;
- relevant logs with credentials and private data removed.

Do not file public issues containing vulnerability details. Follow
[SECURITY.md](SECURITY.md) instead.

## Features

Describe the user problem before the proposed solution. Explain alternatives
and identify whether the change affects provider portability, state, tool
execution, or public APIs.

Open an issue before implementing a large architecture change. Small fixes and
tests can go directly to a pull request.

## Branches, commits, and pull requests

- Create a focused branch from `main`.
- Keep commits understandable; conventional prefixes such as `feat:`, `fix:`,
  `test:`, and `docs:` are welcome but not required.
- Avoid mixing unrelated refactors with behavior changes.
- Add or update tests for observable behavior.
- Update documentation when public behavior changes.
- Complete the pull-request template and state what you tested.

By participating, you agree to follow the
[Code of Conduct](CODE_OF_CONDUCT.md).
