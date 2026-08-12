# Fairshift Lab

[![CI](https://github.com/lindgreendavid/fairshift-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/lindgreendavid/fairshift-lab/actions/workflows/ci.yml)
[![CodeQL](https://github.com/lindgreendavid/fairshift-lab/actions/workflows/codeql.yml/badge.svg)](https://github.com/lindgreendavid/fairshift-lab/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](pyproject.toml)

A reproducible research laboratory for answering a narrow question:

> How do model performance and group-fairness measurements change when the deployment population differs from the training population?

Version `1.1.0` adds Fairshift Policy Studio: a frozen 20-seed mitigation benchmark, explicit error-cost declarations, a fairness–utility Pareto explorer, uncertainty-aware policy comparisons, and reproducible scenario exports. It builds on the 300-experiment shift report and WCAG 2.2 AA-oriented public laboratory. It remains a research instrument—not evidence that fairness has been “solved.”

**[Open the public interactive laboratory](https://fairshift-lab.lindgreendavid.chatgpt.site)**

## Why this project matters

Fairness measured on an in-distribution test set is not a permanent property. Population composition, observed features, and label-generating mechanisms can change after deployment. Fairshift Lab makes those changes explicit and reproducible so that accuracy and fairness degradation can be studied together.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
fairshift --shift covariate --magnitude 0.5 --samples 2000 --seed 42
pytest
ruff check .
mypy src
python -m build
python scripts/generate_study.py
```

The CLI emits stable JSON containing the full configuration, source and target metrics, reproducible percentile-bootstrap intervals, raw and calibrated reliability summaries, and 19-point threshold sweeps. The interactive web laboratory lives in `site/`; its browser simulation favors immediate explanation, while the Python package remains the authoritative numerical implementation.

## Scientific scope

The generator exposes one protected binary attribute, two continuous features, and a binary outcome. Each target experiment changes exactly one mechanism:

| Intervention | What changes | What remains fixed |
| --- | --- | --- |
| Covariate shift | Feature distributions | Conditional label equation |
| Concept shift | Label equation | Feature realization |
| Prevalence shift | Protected-group probability | Remaining structural equations |

Reported metrics are accuracy, AUROC, demographic-parity difference, equal-opportunity difference, equalized-odds difference, and group-level selection/true-positive/false-positive rates. A value of zero for a fairness *difference* means parity on that measurement; it does not establish justice, causality, or suitability for deployment.

Training, source calibration, source evaluation, and target evaluation use independent generated populations. One temperature is selected on the source calibration population by minimum negative log likelihood, then applied unchanged to both evaluation populations. Reliability is reported with Brier score, expected calibration error, and populated reliability bins. Calibration can degrade under shift; it is measured, not assumed.

## Architecture

```text
configuration -> structural generator -> source population -> baseline training
                              \-------> target population -> paired evaluation
```

- `src/fairshift_lab/`: typed production code
- `tests/`: deterministic unit and integration tests
- `site/`: accessible interactive research laboratory
- `docs/`: research protocol, methodology, cards, and decisions
- `reports/`: frozen synthetic, policy, and observational registries; transient outputs remain uncommitted
- `.github/`: continuous integration, security analysis, and dependency maintenance

Read [the v1 shift report](docs/research-report.md), [policy report](docs/policy-study-report.md), [policy protocol](docs/policy-study-protocol.md), [research protocol](docs/research-protocol.md), [methodology](docs/methodology.md), [Data Card](docs/data-card.md), [Model Card](docs/model-card.md), [accessibility statement](ACCESSIBILITY.md), and [architecture decision](docs/adr/0001-synthetic-first.md) before interpreting results.

## Limitations and responsible use

The synthetic work uses one binary protected attribute and simplified structural assumptions. The separate v1.2 reference study uses historical observational records and provider-coded binary sex categories. Neither surface may be used to make high-impact decisions, rank people, certify legal compliance, or infer present-day discrimination.

## Release path

- `v0.2.0`: bootstrap confidence intervals and interactive uncertainty-aware comparisons
- `v0.3.0`: source-calibrated baseline and formal threshold sensitivity analysis
- `v1.0.0`: frozen experiment registry, internally verified research report, comprehensive accessibility work, and stable public laboratory
- `v1.1.0`: declared error costs, mitigation benchmark, fairness–utility Pareto analysis, and reproducible Policy Studio exports
- `v1.2.0`: governed historical reference-data validation with provenance, cohort and missingness sensitivity, and a strict synthetic/observational boundary

Next: a survey-design-aware ACS PUMS protocol, followed by a synthetic robustness laboratory for unobserved groups, label noise, alternative models, and specification stress tests.

See [CHANGELOG.md](CHANGELOG.md) for released changes and [CONTRIBUTING.md](CONTRIBUTING.md) for the quality contract.

## Citation and license

Citation metadata is available in [CITATION.cff](CITATION.cff). Code and documentation are released under the [MIT License](LICENSE).
