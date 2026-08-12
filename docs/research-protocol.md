# Research protocol

## Research question

How do controlled target-domain interventions affect predictive performance and group-fairness measurements for a model trained only on an unshifted source population?

## Falsifiable hypotheses

1. Increasing covariate-shift magnitude changes target metrics even when the conditional label equation remains fixed.
2. Concept shift causes a larger target AUROC loss than an equally parameterized prevalence shift in the documented generator.
3. Stable aggregate accuracy does not imply stable demographic-parity or equalized-odds differences.

These hypotheses are prospective for subsequent result releases. Version 0.1.0 supplies the apparatus; it does not report confirmatory findings.

## Experimental unit and estimands

The unit is one independently sampled synthetic person. The primary estimands are source-to-target changes in AUROC, demographic-parity difference, and equalized-odds difference. Accuracy and group-specific rates are secondary measurements.

## Procedure

1. Fix the configuration and random seed before generation.
2. Sample an unshifted source population.
3. Train one logistic baseline on source features and outcomes.
4. Independently sample a target population under exactly one intervention.
5. Apply the unchanged model and decision threshold to both populations.
6. Record configuration and metrics as JSON.
7. Repeat across seeds and magnitudes in a later statistical-analysis release.

## Leakage prevention

Target labels and target metrics never influence model fitting. The target seed differs from the source seed, and no preprocessing learns target statistics.

## Confirmatory boundary

Single-run output is diagnostic. Confirmatory claims require a preregistered seed grid, uncertainty intervals, multiplicity handling where appropriate, effect sizes, and publication of all planned runs—including null or adverse findings.

## Uncertainty in version 0.2.0

The package reports two-sided percentile-bootstrap intervals for accuracy, demographic-parity difference, equal-opportunity difference, and equalized-odds difference. Resampling is stratified by the protected attribute, so each bootstrap sample preserves the observed group sizes. This isolates conditional-rate sampling variability from group-composition variability.

The intervals do not quantify uncertainty from dataset construction, label validity, model choice, threshold selection, structural misspecification, unobserved groups, or future distribution shift. They are descriptive intervals for one declared data-generating process, not fairness certificates. The interactive browser release uses fewer resamples for immediate feedback; the Python CLI is the authoritative reproducible implementation.

## Ethics

Protected attributes and labels are synthetic abstractions. They do not encode the lived meaning of demographic categories. The laboratory is intended for education, method development, and reproducibility—not compliance certification or automated decision-making.
