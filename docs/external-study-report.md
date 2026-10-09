# v1.2 external-validation report

Status: internally verified, not externally peer reviewed.

## Main result

The historical reference table changes the policy story without producing a universal
winner. In the complete-case provider-eligible cohort at equal error costs, the fixed
baseline had mean accuracy 0.79975 and equalized-odds difference 0.03714. Reweighed training
had slightly higher accuracy (0.80090) and lower observed gap (0.02096), while group
thresholds reduced the observed gap further (0.01675) with lower accuracy (0.79564) and
higher normalized cost (0.20436 versus 0.20025). These are descriptive benchmark values,
not moral rankings.

The source cost-selected threshold was close to the fixed baseline at equal costs. Rankings
and thresholds vary across false-negative cost, age cohort, missingness rule and split seed;
all 48 aggregate cells remain in the registry. The confirmatory “no uniformly best policy”
hypothesis is retained. Sensitivity is visible but does not license population inference.

## What this adds—and does not add

Unlike the synthetic study, these records contain historical observational dependencies and
provider categories. That makes the pipeline encounter missingness and cohort choices, but it
removes causal control. The official split is not evidence of real distribution shift, the
income label is not ground truth for a beneficial decision, and the two-valued provider sex
field does not represent gender diversity or identity truth.

See the [inclusion gate](external-dataset-gate.md), [dataset card](adult-dataset-card.md),
[preregistered protocol](external-study-protocol.md), and machine-readable
`reports/v1.2-external-study.json` before using any value.

## Post-release amendment (2026-10-09): test-set sampling uncertainty

**POST-HOC, not preregistered.** The intervals above are replication ranges over five development
splits; the 15,060-person test file was never resampled. `reports/post-release-external-audit.json` adds
a paired person-level bootstrap (2,000 resamples) and a permutation noise floor for every cohort and split
seed. The registered point estimates reproduce exactly. In the primary cohort the equalized-odds gaps are
0.037 (baseline, 95% interval 0.010-0.080), 0.021 (reweighed) and 0.017 (group thresholds) against a
no-association floor of 0.014, and in none of 60 paired baseline-minus-policy comparisons does the interval
exclude zero. The wording that reweighed training and group thresholds "reduced the observed gap" describes
this one test file and is not supported as a general statement at this sample size. Only the accuracy cost of
group thresholds is resolved (18 of 20 cells). The confirmatory hypotheses stand. See `paper/paper.pdf`.
