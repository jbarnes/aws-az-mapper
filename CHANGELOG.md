# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-06-04

### Added
- `pyproject.toml` with packaging metadata, an `az-mapper` console-script entry
  point, a `dev` extras group, and pylint configuration.
- Tests for `--list-regions`, the `main()` stdout and file-output paths, and CSV
  special-character quoting.
- `CHANGELOG.md` and `CONTRIBUTING.md`.

### Changed
- CSV output now uses the standard-library `csv` module, so values containing
  commas, quotes, or newlines are correctly quoted and escaped.
- Output filename timestamps now use UTC for cross-machine consistency.
- The pylint workflow is aligned with the test workflow: `checkout@v4`,
  `setup-python@v5`, a Python 3.9-3.14 matrix, and `main`/pull-request triggers
  only. `setup-python` was also bumped to v5 in the test workflow.
- CI now tests against Python 3.13 and 3.14 in addition to 3.9-3.12.

### Removed
- Support for end-of-life Python 3.8; the project now requires Python 3.9 or
  higher.

### Fixed
- Region discovery now warns loudly when it falls back to the hardcoded region
  list, which may be stale or include regions the account cannot access.

## [1.0.0] - 2026-05-04

### Added
- Initial stable release: map AWS logical availability zones to physical zone
  IDs for the currently authenticated account.
- Non-interactive CLI with JSON and CSV output, region filtering, `--stdout`,
  `--quiet`, and `--list-regions`.
- Testing infrastructure and GitHub Actions workflows for tests and pylint.

[1.1.0]: https://github.com/jbarnes/aws-az-mapper/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/jbarnes/aws-az-mapper/releases/tag/v1.0.0
