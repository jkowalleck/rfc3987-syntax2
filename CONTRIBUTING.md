# Contributing

Contributions are welcome! Whether you're fixing a bug, improving documentation, or adding new features — thank you for taking the time to contribute.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Opening Issues](#opening-issues)
- [Pull Requests](#pull-requests)
- [Local Setup](#local-setup)
- [Running Tests](#running-tests)
- [Running Static Analysis](#running-static-analysis)
- [Deployment and Publishing](#deployment-and-publishing)

## Code of Conduct

Please be respectful and considerate in all interactions. Constructive feedback is welcome; harassment or hostile behavior is not.

## Opening Issues

We appreciate bug reports, feature requests, and general feedback.

- **Bug reports**: Please include a minimal reproducible example and the Python version you're using.
- **Feature requests or larger changes**: Please open an issue **before** starting implementation work. This allows us to discuss the scope and approach, and avoids wasted effort if the direction needs to change.
- **Questions and discussions**: Issues are a good place for these too.

## Pull Requests

Pull requests are welcome! Please keep the following in mind:

- **Scope**: Each pull request should be focused on **one thing only** — one bug fix, one feature, one refactor. Mixed-purpose PRs are harder to review and will likely be asked to be split up.
- **Discuss first**: For any larger refactoring or significant code changes, please open an issue to discuss the matter before submitting a PR.
- **Tests**: Please ensure your changes are covered by tests. Existing tests must continue to pass.
- **Style**: Follow the conventions already established in the codebase.

## Local Setup

**Prerequisites**: Python 3.9 or newer.

1. Clone the repository:

   ```sh
   git clone https://github.com/jkowalleck/rfc3987-syntax2.git
   cd rfc3987-syntax2
   ```

2. Install the package in editable mode together with the development dependencies:

   ```sh
   pip install -e ".[testing]"
   ```

## Running Tests

Tests are written with [pytest](https://docs.pytest.org/).

```sh
python -m pytest tests
```

## Running Static Analysis

Type checking is done with [mypy](https://mypy.readthedocs.io/).

```sh
python -m mypy -v
```

The mypy configuration is in [`.mypy.ini`](.mypy.ini).

## Deployment and Publishing

Releases are managed by the maintainers. The process is:

1. A maintainer creates a **GitHub Release** (including a version tag).
2. This triggers the [`python-publish`](.github/workflows/python-publish.yml) GitHub Actions workflow, which builds the package and publishes it to [PyPI](https://pypi.org/project/rfc3987-syntax2/) automatically.

Contributors do not need to do anything special for releases.
