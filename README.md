# Fairshift Lab

[![CI](https://github.com/lindgreendavid/fairshift-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/lindgreendavid/fairshift-lab/actions/workflows/ci.yml)
[![CodeQL](https://github.com/lindgreendavid/fairshift-lab/actions/workflows/codeql.yml/badge.svg)](https://github.com/lindgreendavid/fairshift-lab/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](pyproject.toml)

A reproducible research laboratory for answering a narrow question:

> How do model performance and group-fairness measurements change when the deployment population differs from the training population?

Version `1.0.1` adds a frozen 300-experiment replication registry, an internally verified research report, WCAG 2.2 AA-oriented accessibility with measured palette contrast, and failure-tolerant public presentation to the inspectable synthetic process, source-only calibration, threshold sensitivity, and uncertainty laboratory. It remains a research instrument—not evidence that fairness has been “solved.”

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
- `reports/`: frozen v1 registry; transient `reports/generated/` outputs remain uncommitted
- `.github/`: continuous integration, security analysis, and dependency maintenance

Read [the v1 research report](docs/research-report.md), [research protocol](docs/research-protocol.md), [methodology](docs/methodology.md), [Data Card](docs/data-card.md), [Model Card](docs/model-card.md), [accessibility statement](ACCESSIBILITY.md), and [architecture decision](docs/adr/0001-synthetic-first.md) before interpreting results.

## Limitations and responsible use

This release uses synthetic data, one binary protected attribute, one baseline, and associational group metrics. It must not be used to make high-impact decisions, rank people, certify legal compliance, or infer real-world discrimination. Synthetic simplicity supports causal clarity but does not represent intersectionality or social context.

## Release path

- `v0.2.0`: bootstrap confidence intervals and interactive uncertainty-aware comparisons
- `v0.3.0`: source-calibrated baseline and formal threshold sensitivity analysis
- `v1.0.0`: frozen experiment registry, internally verified research report, comprehensive accessibility work, and stable public laboratory

Next: a policy studio for explicitly declared error costs, mitigation methods, and fairness–utility Pareto analysis. It will expose trade-offs without presenting an automatic “best” policy.

See [CHANGELOG.md](CHANGELOG.md) for released changes and [CONTRIBUTING.md](CONTRIBUTING.md) for the quality contract.

## Citation and license

Citation metadata is available in [CITATION.cff](CITATION.cff). Code and documentation are released under the [MIT License](LICENSE).
