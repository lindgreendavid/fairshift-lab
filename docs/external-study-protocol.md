# Preregistered v1.2 external-study protocol

Frozen before held-out interpretation on 2026-08-12.

## Confirmatory questions

1. Do mitigation rankings from the synthetic benchmark remain invariant on a historical
   observational reference table? Hypothesis: no policy will uniformly minimize both
   normalized error cost and equalized-odds difference across declarations and cohorts.
2. Are conclusions stable to the declared age-cohort and missingness variations? Hypothesis:
   at least one reported metric or policy ordering will change.

## Design

The provider development file is split 80/20 using seeds 200–204. The provider test file is
never used for fitting, scaling, threshold selection or hypothesis changes. Numeric features
are standardized from training statistics. Four policies are compared: threshold 0.5,
source cost-selected threshold, Kamiran–Calders-style reweighed training with source
cost-selected threshold, and group thresholds selected with λ=1. False-negative costs are
0.5, 1 and 2; false-positive cost is 1.

Outcomes are accuracy, normalized expected cost, demographic-parity difference,
equal-opportunity difference, equalized-odds difference, Brier score and expected calibration
error. The registry reports mean, sample standard deviation and empirical 2.5th–97.5th
replication range plus subgroup counts. Empty rate denominators follow the package's explicit
zero semantics; no such empty subgroup-label cells occur in the admitted held-out cohorts.

## Sensitivity and multiplicity

The two cohort definitions and two missingness rules are co-primary sensitivity analyses,
not undisclosed researcher choices. All cells remain visible; no multiplicity-adjusted claim
of statistical significance is made. Intervals describe split-seed variation only. Null and
adverse results are retained.

## Boundary

This is observational external reference-data validation of a software and analysis pattern,
not validation for a deployment population. Synthetic and observational numbers must never
share an unlabeled scale or chart.
