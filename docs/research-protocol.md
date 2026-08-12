# Research protocol

## Research question

How do controlled target-domain interventions affect predictive performance and group-fairness measurements for a model trained only on an unshifted source population?

## Falsifiable hypotheses

1. Increasing covariate-shift magnitude changes target metrics even when the conditional label equation remains fixed.
2. Concept shift causes a larger target AUROC loss than an equally parameterized prevalence shift in the documented generator.
3. Stable aggregate accuracy does not imply stable demographic-parity or equalized-odds differences.
4. Source-fitted temperature scaling can improve source reliability without improving target reliability under concept shift.
5. A conclusion based on one threshold can reverse or disappear elsewhere on the declared threshold grid.

These hypotheses are prospective for subsequent result releases. Version 0.1.0 supplies the apparatus; it does not report confirmatory findings.

Version 1.0.0 freezes the first descriptive replication grid and records each hypothesis disposition in [`research-report.md`](research-report.md). The study remains synthetic and does not convert these hypotheses into external population claims.

## Experimental unit and estimands

The unit is one independently sampled synthetic person. The primary estimands are source-to-target changes in AUROC, demographic-parity difference, and equalized-odds difference. Accuracy and group-specific rates are secondary measurements.

## Procedure

1. Fix the configuration and random seed before generation.
2. Independently sample unshifted training, source-calibration, and source-evaluation populations.
3. Train one logistic baseline on the training population only.
4. Fit one temperature on source-calibration scores by minimum negative log likelihood.
5. Independently sample a target population under exactly one intervention.
6. Apply the unchanged model and source-fitted temperature to both evaluation populations.
7. Record reliability, the declared threshold metric, uncertainty, and the full threshold grid as JSON.
8. Repeat across the frozen seed–magnitude grid and publish the complete registry.

## Leakage prevention

Target labels and target metrics never influence model or temperature fitting. Training, calibration, source evaluation, and target evaluation use separate seeds, and no preprocessing learns target statistics.

## Confirmatory boundary

Single-run output is diagnostic. Confirmatory claims require a preregistered seed grid, uncertainty intervals, multiplicity handling where appropriate, effect sizes, and publication of all planned runs—including null or adverse findings.

## Uncertainty in version 0.2.0

The package reports two-sided percentile-bootstrap intervals for accuracy, demographic-parity difference, equal-opportunity difference, and equalized-odds difference. Resampling is stratified by the protected attribute, so each bootstrap sample preserves the observed group sizes. This isolates conditional-rate sampling variability from group-composition variability.

The intervals do not quantify uncertainty from dataset construction, label validity, model choice, threshold selection, structural misspecification, unobserved groups, or future distribution shift. They are descriptive intervals for one declared data-generating process, not fairness certificates. The interactive browser release uses fewer resamples for immediate feedback; the Python CLI is the authoritative reproducible implementation.

## Calibration and threshold sensitivity in version 0.3.0

Temperature scaling divides the baseline logit by one positive scalar selected on the independent source-calibration population. Candidate temperatures are searched deterministically on a log-spaced grid from `0.25` to `4.0` by negative log likelihood. This preserves ranking but can change thresholded decisions. Raw and calibrated Brier score, expected calibration error, and reliability bins are reported separately for source and target evaluation populations.

Expected calibration error is bin-dependent and can hide local miscalibration. Source calibration does not guarantee target calibration under shift. The threshold sweep reports all existing performance and group measurements at 19 preregistered cutoffs from `0.05` to `0.95`; it is a sensitivity analysis, not automatic threshold selection. Selecting a cutoff requires an externally justified decision policy, error costs, and domain review.

## Frozen replication grid in version 1.0.0

The report grid crosses three target interventions with magnitudes `0.00`, `0.25`, `0.50`, `0.75`, and `1.00`, using seeds `100` through `119` and 1,000 observations per independently generated population. The grid is generated without target-informed model, calibration, or threshold selection. Means, sample standard deviations, and empirical 2.5th–97.5th percentile replication ranges are recorded for every cell. These ranges are descriptive across the declared seeds and are not population confidence intervals.

## Ethics

Protected attributes and labels are synthetic abstractions. They do not encode the lived meaning of demographic categories. The laboratory is intended for education, method development, and reproducibility—not compliance certification or automated decision-making.
