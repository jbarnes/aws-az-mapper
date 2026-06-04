# Contributing

Thanks for your interest in improving aws-az-mapper. Issues and pull requests are
welcome.

## Development setup

Requires Python 3.9 or higher and AWS CLI credentials only if you want to run the
tool against a real account (the test suite mocks all AWS calls).

```bash
python3 -m venv venv
source venv/bin/activate
make install   # installs runtime + dev dependencies (pytest, pylint)
```

## Running tests and linting

```bash
make test   # pytest tests/ -v
make lint   # pylint az_mapper.py --fail-under=9.0
```

Tests use `pytest` with mocked AWS API calls, so no AWS credentials are required.

## Pull request guidelines

- Branch off `main` and open a pull request against `main`.
- Keep changes focused; one logical change per pull request where practical.
- Add or update tests for any behaviour change.
- CI must pass on all supported Python versions (3.9-3.12). This runs both the
  test suite and pylint; the pylint score must stay at or above 9.0.
- Update `CHANGELOG.md` under an `## [Unreleased]` heading (create it if needed)
  describing your change.

## Releasing

Releases follow [Semantic Versioning](https://semver.org/). To cut a release:

1. Move the `Unreleased` changelog entries under a new version heading with the
   release date, and update the comparison links at the bottom of the file.
2. Bump `version` in `pyproject.toml`.
3. Tag the merge commit on `main` (`git tag -a vX.Y.Z`) and push the tag.
4. Publish a GitHub release from the tag.
