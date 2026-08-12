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

## Metrics

- Accuracy: fraction of correct thresholded predictions.
- AUROC: probability that a randomly chosen positive receives a higher score than a negative, with half credit for ties.
- Demographic-parity difference: absolute selection-rate gap.
- Equal-opportunity difference: absolute true-positive-rate gap.
- Equalized-odds difference: maximum of the absolute true-positive- and false-positive-rate gaps.

Undefined conditional rates caused by an empty subgroup condition are reported as `0.0` in v0.1.0. Consumers must inspect group counts before substantive interpretation; a future release will add explicit uncertainty and missingness metadata.

## Reproducibility

Randomness is isolated in NumPy's generator and controlled by recorded seeds. CI tests supported Python versions, formatting, lint, typing, coverage, and package construction. Generated reports are excluded from version control so that every published result must declare how it was produced.

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
