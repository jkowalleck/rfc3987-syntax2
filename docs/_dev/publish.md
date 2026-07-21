# Publish & Release process

1. Add the respective note in the [CHANGELOG](../../CHANGELOG.md)
1. Bump `project.version` in the [package manifest](../../pyproject.toml)
1. Create a release on GitHub
   * Release tag SHOULD be prefixed with `v`
   * Release tag MUST match the new version

The GitHub release will trigger the [publihs workflow](../../.github/workflows/python-publish.yml)
