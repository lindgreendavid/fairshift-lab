# Contributing

Fairshift Lab welcomes small, evidence-backed changes.

1. Open an issue for new research scope or metric semantics.
2. Create a focused branch.
3. Add or update tests and documentation with the implementation.
4. Run `pytest`, `ruff check .`, `ruff format --check .`, `mypy src`, `python -m build`, both registry generators with byte comparisons, and the complete web lint/test build.
5. Use English Conventional Commits and submit a draft pull request.

Never commit personal data, secrets, transient generated reports, model artifacts, or claims unsupported by the implemented experiment. The two frozen release registries are reviewed exceptions and may change only with their versioned protocols, generators, tests, and reports. Scientific changes must state assumptions, provenance, uncertainty, limitations, and the difference between evidence and interpretation.
