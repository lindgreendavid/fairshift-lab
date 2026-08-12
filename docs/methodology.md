# Methodology

## Structural process

Let the protected attribute be `A ~ Bernoulli(p)`, with `p = 0.5` in the source. Two observed variables are sampled as `X1 ~ Normal(0,1) + 0.35A` and `X2 ~ Normal(0,1)`. The source label probability is:

`P(Y=1) = sigmoid(-0.15 + 1.1X1 - 0.7X2 - 0.45A)`.

This equation deliberately creates an observable group association. It is a pedagogical mechanism, not a model of a real social process.

## Interventions

- **Covariate:** moves `X1` by `m(0.5 + A)` and `X2` by `-0.75m`.
- **Concept:** changes the `X1` coefficient to `1.1 - 1.8m` and the group coefficient to `-0.45 + 1.2m`.
- **Prevalence:** changes `p` to `0.5 + 0.4m`.

Magnitude `m` lies in `[0,1]`. Intervention formulas are part of the public contract and tested.

## Baseline

The baseline is binary logistic regression optimized by deterministic full-batch gradient descent. An explicit implementation keeps the educational release auditable. It is not optimized for large data and should be compared with a mature library implementation before substantive research use.

Training, calibration, source evaluation, and target evaluation use independent populations. The package fits one scalar temperature on the source calibration population by minimizing negative log likelihood over a deterministic log-spaced grid. For a raw probability `p`, the calibrated probability is `sigmoid(logit(p) / T)`. The same fitted temperature is applied unchanged to source and target evaluation scores.

## Metrics

- Accuracy: fraction of correct thresholded predictions.
- AUROC: probability that a randomly chosen positive receives a higher score than a negative, with half credit for ties.
- Demographic-parity difference: absolute selection-rate gap.
- Equal-opportunity difference: absolute true-positive-rate gap.
- Equalized-odds difference: maximum of the absolute true-positive- and false-positive-rate gaps.
- Brier score: mean squared error between probability and binary outcome.
- Expected calibration error: sample-weighted absolute difference between mean probability and observed outcome rate in equal-width bins.

The threshold-sensitivity output evaluates all performance and group measurements at 19 fixed cutoffs from `0.05` through `0.95`. It exposes how conclusions depend on the decision rule. It does not choose an operational threshold or encode the relative consequences of false positives and false negatives.

Undefined conditional rates caused by an empty subgroup condition are reported as `0.0` in v0.1.0. Consumers must inspect group counts before substantive interpretation; a future release will add explicit uncertainty and missingness metadata.

## Reproducibility

Randomness is isolated in NumPy's generator and controlled by recorded seeds. CI tests supported Python versions, formatting, lint, typing, coverage, and package construction. Generated reports are excluded from version control so that every published result must declare how it was produced.

The reviewed registries are explicit exceptions. `reports/v1-study.json` and `reports/v1.1-policy-study.json` are committed as immutable release artifacts and regenerated from the public package API by their matching scripts. Both retain 20-seed descriptive variation rather than only a grand mean, and CI rejects any byte-level divergence from regenerated output.

## Decision policies in version 1.1.0

Policy selection is separated from target testing. Normalized error cost makes the declared false-positive and false-negative ratio visible without pretending it captures every consequence. Reweighing changes source training weights; global and group-specific thresholds change decisions without retraining; supervised target recalibration is isolated because it requires recent labeled target data. The complete selection rules, tie handling, and finite-set Pareto definition are fixed in [`policy-study-protocol.md`](policy-study-protocol.md).

## Bootstrap uncertainty

Version 0.2.0 adds a group-stratified nonparametric percentile bootstrap. Within each protected group, observations are sampled with replacement to the original group size. Metrics are recomputed for every resample, and the configured lower and upper quantiles form the interval. Stratification is intentional: prevalence shift is an experimental mechanism in this project and should not be reintroduced accidentally as bootstrap composition noise.

The method is transparent and distribution-light, but percentile intervals can have imperfect coverage, especially for bounded, non-smooth fairness gaps and small conditional subgroups. The intervals should therefore be read as a stability diagnostic. Research on subgroup evaluation shows that smaller subpopulations produce higher-variance metric estimates, while uncertainty-aware fairness research warns against ranking methods from point estimates alone.

## Scientific references

- Hardt, Price, and Srebro (2016), *Equality of Opportunity in Supervised Learning*: definitions of equal opportunity and equalized odds. https://proceedings.neurips.cc/paper_files/paper/2016/hash/6a9659feb1216f14f7384ba499518b38-Abstract.html
- Chen, Raab, Wang, and Liu (2022), *Fairness Transferability Subject to Bounded Distribution Shift*: transfer bounds for demographic parity and equalized odds under shift. https://arxiv.org/abs/2206.00129
- Miller et al. (2021), *Model-based metrics*: subgroup performance estimation and confidence intervals under small subgroup samples. https://proceedings.mlr.press/v149/miller21a.html
- Barrainkua et al. (2024), *Uncertainty Matters*: uncertainty-aware joint comparison of performance and fairness. https://proceedings.mlr.press/v238/barrainkua24a.html
- Agarwal et al. (2025), *Optimal Fair Learning Robust to Adversarial Distribution Shift*: robustness of fairness-constrained learning under malicious distribution noise. https://proceedings.mlr.press/v267/agarwal25b.html
- NIST AI RMF 1.0, *AI Risks and Trustworthiness*: fairness is one socio-technical trustworthiness characteristic that must be balanced with validity, transparency, explainability, privacy, safety, and security. https://airc.nist.gov/airmf-resources/airmf/3-sec-characteristics/
- Guo et al. (2017), *On Calibration of Modern Neural Networks*: held-out post-hoc calibration and temperature scaling. https://proceedings.mlr.press/v70/guo17a.html
- Ovadia et al. (2019), *Can You Trust Your Model’s Uncertainty?*: empirical evaluation of predictive uncertainty and calibration under dataset shift. https://proceedings.neurips.cc/paper_files/paper/2019/hash/8558cb408c1d76621371888657d2eb1d-Abstract.html
- Kleinberg, Mullainathan, and Raghavan (2017), *Inherent Trade-Offs in the Fair Determination of Risk Scores*: incompatibilities among statistical fairness conditions. https://arxiv.org/abs/1609.05807
- Kamiran and Calders (2012), *Data preprocessing techniques for classification without discrimination*: reweighing and related preprocessing methods. https://doi.org/10.1007/s10115-011-0463-8
- Corbett-Davies et al. (2023), *The Measure and Mismeasure of Fairness*: decision-policy utility and Pareto-dominance critiques of formal fairness constraints. https://jmlr.org/papers/v24/22-1511.html
- Kamani et al. (2021), *Pareto Efficient Fairness in Supervised Learning*: multi-objective loss and fairness frontier analysis. https://arxiv.org/abs/2104.01634
