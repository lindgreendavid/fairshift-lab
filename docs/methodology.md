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

