# Preregistered v1.3 robustness-stress protocol

Frozen before generating or interpreting any v1.3 result on 2026-08-12.

## Status and research question

This protocol is fixed before running `fairshift_lab.robustness.run_robustness_study` or
looking at the resulting registry. It is entirely synthetic; it does not touch UCI Adult or
any other observational data, and it must never share an unlabeled chart, table, or scale
with the synthetic v1.0/v1.1 study or the v1.2 external evidence. It asks:

> When training data, protected-attribute measurement, group composition, sample size, or the
> functional form of the true label mechanism are individually degraded, which v1.0–v1.2
> conclusions still hold, and does the answer depend on the inspectable model family used?

## Prospective, falsifiable hypotheses

1. **Symmetric label noise degrades ranking and calibration monotonically but leaves group
   gaps comparatively small**, because flipping labels independently of the protected
   attribute is not itself a source of differential treatment. Falsified if a fairness gap
   grows materially faster than AUROC degrades.
2. **Group-conditional label noise reverses or inflates group-fairness gaps** relative to the
   symmetric-noise condition at the same total flip rate, because differential label error is
   a documented mechanism for manufacturing spurious disparities. Falsified if gaps under
   group-conditional noise are statistically indistinguishable from symmetric noise.
3. **Protected-field measurement error causes the fairness gaps measured against the
   *observed* (noisy) group label to understate the gaps measured against the *true* group
   label**, because noisy group assignment mixes the two groups toward each other's rates.
   Falsified if the observed-attribute gap is not smaller than the true-attribute gap on
   average.
4. **An unobserved intersectional subgroup can carry a materially worse outcome than either
   marginal protected group**, which standard two-group demographic-parity and
   equal-opportunity differences will not surface, because those statistics never condition on
   the unobserved subgroup indicator. Falsified if the subgroup gap tracks the marginal
   group gap once the stressor is active.
5. **Reducing sample size increases the empirical replication range of every estimate and
   increases the rate of structurally undefined per-group or per-subgroup rates** (an empty
   group-label cell), rather than changing the mean in a consistent direction. Falsified if
   replication ranges do not widen as sample size falls.
6. **Structural misspecification (an unmodeled interaction between one observed feature and
   the protected attribute in the true label mechanism) degrades the logistic-regression
   family's ranking and calibration more than the shallow-decision-tree family**, because a
   depth-limited tree can approximate a low-order interaction through sequential splits while
   an additive linear model cannot represent it at all. Falsified if the two model families
   degrade by a statistically indistinguishable amount.
7. **No single stressor uniformly reverses every v1.0–v1.2 conclusion.** Each stressor is
   expected to challenge some prior descriptive claims and leave others intact; this study
   reports which ones for each stressor rather than asserting a global verdict.

Hypotheses 1–6 are directional predictions, not certainties; §"Findings" in the companion
report records each disposition — confirmed, reversed, or undefined — without suppressing
adverse results.

## Which v1.0–v1.2 conclusions each stressor is designed to test

| Stressor | Prior conclusion under test |
| --- | --- |
| Symmetric label noise | v1.0: a fixed logistic baseline yields a stable, reproducible source measurement. |
| Group-conditional label noise | v1.0/v1.1: observed group-fairness gaps reflect the declared structural mechanism, not annotation artifacts. |
| Protected-field measurement error | v1.1/v1.2: group thresholds and reweighing computed from the protected attribute measure the true group disparity. |
| Unobserved intersectional subgroup | v1.0–v1.2: two-group demographic-parity/equal-opportunity differences fully characterize group-conditional behavior. |
| Sample-size stress | v1.0/v1.1: descriptive replication ranges are narrow and every subgroup rate is defined. |
| Structural misspecification | v1.0: a single inspectable model family is representative of "the" model's robustness. |

## Model families and no-model-shopping declaration

Two inspectable model families are compared, with hyperparameters fixed **before** any stress
condition is run and never adjusted after inspecting fairness or robustness results:

1. **Logistic baseline** (`fairshift_lab.model.LogisticBaseline`): additive linear-in-logit
   model, learning rate `0.2`, `800` full-batch gradient-descent iterations (unchanged from
   v1.0–v1.2).
2. **Shallow decision tree** (`fairshift_lab.model.ShallowDecisionTree`): greedy,
   deterministic CART-style splitting on Gini impurity, maximum depth `3`, minimum `20`
   samples per leaf, Laplace-smoothed leaf probabilities. Ties in split search break on the
   lowest feature index, then the lowest threshold — a deterministic rule, not a substantive
   choice.

Both families receive identical raw inputs (`feature_one`, `feature_two`, `sensitive`) and are
fit on identical stressed training data for each cell. Neither family is retuned, replaced, or
selected based on which one looks fairer or more robust; both are reported for every cell,
including cells where one family performs worse.

## Data-generating process

`fairshift_lab.robustness.generate_robust_population` extends the v1.0 structural equation
(`fairshift_lab.data.generate_population`) with two additions that exist only inside this
module and never touch v1.0–v1.2 code paths:

- An **unobserved intersectional subgroup** indicator, `subgroup = 1` when `sensitive == 1`
  and `feature_two` is above its population median, `0` otherwise. It is generated for every
  population regardless of stressor so that its baseline (no-effect) behavior is itself a
  reported null result. It is never included in the model's feature matrix and never used to
  select a policy.
- An optional **interaction term** `coefficient * feature_one * sensitive` added to the true
  logit, active only under the structural-misspecification stressor.

Stressors are applied as explicit, composable transformations on top of one clean generated
population per split, sharing the v1.0 magnitude convention: each stressor has its own
`0.00`–`1.00` magnitude, and `0.00` always means "stressor inactive" (a shared, comparable
control across every stressor family, mirroring `StudyConfig.magnitudes`).

| Stressor | Magnitude → mechanism |
| --- | --- |
| `symmetric_label_noise` | Flip each training/tuning label independently with probability `0.35 × magnitude`. |
| `group_conditional_label_noise` | Flip `sensitive == 0` training/tuning labels with probability `0.05`; flip `sensitive == 1` labels with probability `0.05 + 0.40 × magnitude`. |
| `protected_field_measurement_error` | Flip the *observed* `sensitive` field (used for model input and threshold selection) with probability `0.35 × magnitude`; the true field is retained separately for evaluation-only comparison. |
| `unobserved_subgroup` | Add `-1.5 × magnitude` to the true logit for records with `subgroup == 1`. |
| `sample_size_stress` | Training/tuning sample size shrinks from `2,000` at magnitude `0.00` to `60` at magnitude `1.00` (`2000, 800, 300, 120, 60` at magnitudes `0.00, 0.25, 0.50, 0.75, 1.00`); the test sample size is fixed at `2,000` throughout so degradation is attributable to training data, not evaluation noise. |
| `structural_misspecification` | Add interaction coefficient `1.5 × magnitude` on `feature_one × sensitive` to the true logit; this term is never given to either model as an engineered feature. |

Label noise and measurement error are applied **only to the training and tuning splits**,
never to the test split, so degradation is attributable to what the model learned rather than
to what it is evaluated against. This is a documented, deliberate scope boundary: it studies
robustness of fitting and threshold selection to corrupted supervision, not robustness of
measurement itself.

## Disjoint samples

Every cell independently samples four populations from non-overlapping seed offsets, mirroring
the v1.1 policy-study split design:

| Split | Seed offset | Permitted use |
| --- | ---: | --- |
| Training | `+0` | Fit the logistic and tree models under the active stressor. |
| Tuning | `+1` | Select one global cost threshold per model under the active stressor. |
| Adaptation | `+2` | Diagnostic only: estimate the realized flip rate, subgroup effect, or interaction magnitude actually present in this replication. Never used for fitting, calibration, or threshold selection. |
| Test | `+3` | Evaluate once. Never stressed; always the clean, fully labeled population with true and observed protected attributes both retained. |

## Estimands and registry

For every `(stressor, magnitude, model family)` cell, the registry reports, across seeded
replications: accuracy, normalized expected cost (false-negative cost fixed at `1.0`,
equal-cost declaration — cost sensitivity was the subject of v1.1 and is out of scope here to
keep the six-stressor grid tractable), demographic-parity difference, equal-opportunity
difference, equalized-odds difference, Brier score, and expected calibration error, each as a
mean, sample standard deviation, and empirical 2.5th–97.5th percentile replication range,
exactly as in `fairshift_lab.study.StudyEstimate`.

In addition, the registry reports, for the observed and (separately) true protected attribute:
group-conditional selection/true-positive/false-positive rates, and subgroup-conditional
selection/true-positive rates for the unobserved-subgroup indicator. **Missing/undefined
semantics:** unlike `fairshift_lab.metrics.group_rates` (which reports `0.0` for an empty
denominator, the existing v1.0–v1.2 convention, left unchanged), every new rate this module
adds is `null` in the JSON registry, not `0.0`, whenever its denominator is zero in that
replication — for example, an empty group-label cell in a small stressed sample. A `null`
rate is aggregated by dropping it, not treating it as zero; if every replication in a cell is
undefined for a given rate, the aggregate itself is reported as `null` rather than fabricating
a mean of no data. Published aggregates are rounded to nine decimals only after every
computation; internal values are never rounded before aggregation, so macOS and Linux
regenerate byte-identical registry files.

## Sensitivity and multiplicity

The six stressors and five magnitudes are co-primary, preregistered sensitivity axes, not
undisclosed researcher choices. Every cell is published, including adverse, null, and
undefined cells. No p-values or multiplicity-adjusted significance claims are made; intervals
describe split-seed variation only, exactly as in v1.0–v1.2.

## Analysis plan

- Publish every planned `(stressor, magnitude, model family)` cell.
- For each stressor, state in the report which v1.0–v1.2 conclusion(s) it was designed to
  test (table above) and whether that conclusion is confirmed, reversed, or undefined at
  magnitude `1.00`.
- Compare the two model families at identical stress levels; never select one family as "the"
  result.
- Treat every `null` rate as a reported finding (a sample too small to define the quantity),
  not as a gap to silently fill.
- Never combine a robustness-stress value with a v1.0/v1.1 synthetic-shift value or a v1.2
  Adult value in one chart, table, or scale.

## Ethical boundary

Every population, label, protected attribute, and subgroup here is a synthetic abstraction
constructed to stress-test software and analysis behavior. No result in this study is a claim
about a real annotation process, a real protected class, a real intersectional community, or a
real deployment population. Findings describe this generator's behavior under declared,
reversible corruptions of its own synthetic data — nothing more.
