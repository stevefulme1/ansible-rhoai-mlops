# Contributing

Contributions are welcome. Please open an issue or pull request on GitHub.

## Development Setup

```bash
pip install ansible-core>=2.16 ansible-lint yamllint flake8 pytest
```

## Running Tests

```bash
# Lint
ansible-lint --strict
flake8 plugins/ --max-line-length=120 --ignore=E402,W503

# Unit tests
pytest tests/unit/ -v

# Sanity tests
ansible-test sanity --python 3.12 -v
```

## Pull Requests

- Follow existing code patterns and conventions.
- Include unit tests for new modules.
- Update documentation and CHANGELOG.md.
