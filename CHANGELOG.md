# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/).

## [0.3.1] - 2026-08-12

### Fixed

- Stabilized generated chart coordinates to prevent server/client hydration warnings caused by sub-pixel floating-point serialization differences.

## [0.3.0] - 2026-08-12

### Added

- Source-only temperature scaling fitted on an independent calibration population.
- Brier score, expected calibration error, and populated reliability-diagram bins for raw and calibrated source and target scores.
- Formal 19-point source and target threshold sweeps across performance and group-fairness measurements.
- Interactive target reliability diagram and linked source-to-target decision curves.
- Primary-source explanations of calibration under shift and incompatibilities among fairness criteria.

### Changed

- Separated training, calibration, source evaluation, and target evaluation populations.
- Published the interactive laboratory for unrestricted public access.
- Updated the web runtime and build chain to patched React, Vite, Cloudflare, and Vinext releases; CI now audits production dependencies.
- Upgraded package, site, and citation metadata to version 0.3.0.

## [0.2.0] - 2026-08-12

### Added

- Group-stratified percentile-bootstrap intervals for accuracy and three fairness gaps.
- Configurable resample count and confidence level in the typed API and JSON CLI.
- Interactive, responsive, keyboard-accessible research laboratory for manipulating shift mechanism, magnitude, decision threshold, sample size, and seed.
- Explicit metric interpretation boundaries and a primary-source research trail.

### Changed

- Expanded the research protocol, methodology, and Model Card with uncertainty semantics and limitations.
- Upgraded package and citation metadata to version 0.2.0.

## [0.1.0] - 2026-08-12

### Added

- Validated experiment and shift configuration.
- Reproducible structural generator with covariate, concept, and group-prevalence interventions.
- Inspectable logistic-regression baseline.
- Performance and group-fairness evaluation.
- JSON command-line interface.
- Research protocol, methodology, Data Card, Model Card, ADR, citation metadata, tests, CI, CodeQL, and dependency automation.

[0.1.0]: https://github.com/lindgreendavid/fairshift-lab/releases/tag/v0.1.0
[0.2.0]: https://github.com/lindgreendavid/fairshift-lab/releases/tag/v0.2.0
[0.3.0]: https://github.com/lindgreendavid/fairshift-lab/releases/tag/v0.3.0
[0.3.1]: https://github.com/lindgreendavid/fairshift-lab/releases/tag/v0.3.1
