# Fairshift Robustness Lab v1.3 — internally verified report

Status: internally verified, not externally peer reviewed.

## Executive finding

No single stressor reversed every v1.0–v1.2 conclusion, and no single model family was
uniformly more robust. Each of the six preregistered stressors challenged a different prior
claim, sometimes confirming the [protocol's](robustness-protocol.md) directional hypothesis and
sometimes falsifying it. The report below states each disposition plainly, including where the
prospective hypothesis was wrong.

This report covers 60 aggregate cells: six stressors × five magnitudes × two model families.
Every cell summarizes 12 independent seeded replications across disjoint training, tuning,
adaptation, and test splits. The immutable machine-readable record is
[`reports/v1.3-robustness-study.json`](../reports/v1.3-robustness-study.json). All figures below
are means at magnitude `1.00` versus the `0.00` no-stress control unless stated otherwise; full
replication ranges are in the registry.

## Hypothesis dispositions

### 1. Symmetric label noise — falsified as stated

The protocol predicted noise would degrade ranking/calibration while leaving group gaps
"comparatively small." Instead, expected calibration error grew sharply for both families
(logistic `0.023 → 0.145`; tree `0.032 → 0.098`) — a large change, not a small one — while the
equalized-odds gap moved in **opposite directions** for the two families (logistic `0.047 →
0.095`; tree `0.134 → 0.110`, a slight decrease). **Disposition: falsified.** Calibration
damage was not small, and the fairness-gap direction was not consistent across model families.

### 2. Group-conditional label noise — confirmed, but only for one model family

At the same total realized flip rate (~25%), the equalized-odds gap under group-conditional
noise was close to the symmetric-noise result for logistic regression (`0.100` vs `0.095`) but
far larger for the decision tree (`0.395` vs `0.110`) — the tree's gap nearly quadrupled.
**Disposition: confirmed for the tree family, not confirmed for logistic regression.** This is
itself a central finding: whether differential label noise "shows up" as a fairness gap
depends on which inspectable model family is fit, which is exactly why comparing two families
was a hard requirement of this study.

### 3. Protected-field measurement error — confirmed

At magnitude `1.00`, the equalized-odds gap computed against the noisy *observed* attribute
understated the gap computed against the *true* attribute for both families: logistic `0.050`
(observed) vs `0.135` (true); tree `0.066` (observed) vs `0.133` (true). The same pattern held
at magnitude `0.50`. **Disposition: confirmed.** An audit that only has access to an
error-prone protected field will systematically understate the true disparity in this
generator — a direct challenge to treating v1.1/v1.2 group-threshold and audit results as
measuring the true group split whenever the protected field carries measurement error.

### 4. Unobserved intersectional subgroup — confirmed, with an important caveat

At magnitude `1.00`, the marginal two-group demographic-parity gap was `0.166` (selection rate
`0.446` for group A=0 vs `0.279` for group A=1), while the gap between the unobserved subgroup
and the rest of its own marginal group was `0.375` (`0.466` for the rest of group A=1 vs
`0.091` for the subgroup) — more than double the marginal statistic. **Disposition: confirmed.**
Two-group statistics materially understated the disparity actually carried by the
intersectional subgroup.

**Caveat preserved rather than hidden:** the subgroup indicator is partly defined by
`feature_two`, which already affects the true label in the unstressed structural equation. So
even at magnitude `0.00` (subgroup logit penalty exactly zero), the subgroup already showed a
lower selection rate than the rest of its group (`0.262` vs `0.616`) purely from that shared
mechanism. The `1.5 × magnitude` penalty widens a preexisting structural gap; it does not
create disparity from nothing. This is reported explicitly because a null-stressor "control"
that already carries the effect it is meant to isolate is a genuine limitation of this specific
subgroup construction, not a result to gloss over.

### 5. Sample-size stress — confirmed

Every replication range widened sharply at the smallest sample size (`n=60` per split,
magnitude `1.00`): the accuracy standard deviation rose from `0.011` at magnitude `0.00` to
`0.065`–`0.105` depending on model family, and the equalized-odds gap's 2.5th–97.5th
replication range widened to roughly `0.03`–`0.53`. The subgroup false-positive rate was
undefined (no record in that cell) in 11 of 12 replications for both model families at this
magnitude. **Disposition: confirmed.** Small samples widened every reported range and produced
genuinely undefined disaggregated rates, exactly as preregistered — none were suppressed or
treated as zero.

### 6. Structural misspecification — mixed, falsified in one direction and confirmed in another

The protocol predicted the unmodeled feature-one × protected-attribute interaction would
*degrade* ranking and calibration more for logistic regression than for the tree. Instead,
**accuracy and Brier score improved for both families** as the interaction grew (logistic
accuracy `0.713 → 0.757`, Brier `0.187 → 0.163`; tree accuracy `0.692 → 0.740`, Brier `0.201 →
0.175`) — the added interaction supplied net predictive signal rather than destroying it.
**That half of the hypothesis is falsified.** On the fairness axis, however, the prediction
held: the equalized-odds gap grew more in absolute terms for logistic regression (`0.047 →
0.171`, +`0.125`) than for the tree (`0.134 → 0.212`, +`0.077`), consistent with the linear
family being structurally unable to represent the interaction while the depth-limited tree can
partially approximate it through sequential splits. **Disposition: confirmed for the
group-fairness gap, falsified for the predictive-quality claim.**

## Which v1.0–v1.2 conclusions are challenged, stressor by stressor

| Stressor | v1.0–v1.2 conclusion under test | Outcome here |
| --- | --- | --- |
| Symmetric label noise | A fixed logistic baseline yields a stable, reproducible source measurement. | Challenged: calibration error grew sharply; fairness-gap direction was not even consistent between model families. |
| Group-conditional label noise | Observed group-fairness gaps reflect the declared mechanism, not annotation artifacts. | Challenged for the tree family (gap nearly quadrupled from noise alone); largely held for logistic regression. |
| Protected-field measurement error | Group thresholds/audits computed from the protected attribute measure the true group disparity. | Challenged: the observed-attribute gap understated the true-attribute gap by roughly half, for both families. |
| Unobserved intersectional subgroup | Two-group demographic-parity/equal-opportunity differences fully characterize group-conditional behavior. | Challenged: the subgroup-vs-rest gap was more than double the marginal two-group gap. |
| Sample-size stress | Descriptive replication ranges are narrow and every subgroup rate is defined. | Challenged: ranges widened five-to-nine-fold and some disaggregated rates became undefined. |
| Structural misspecification | A single inspectable model family is representative of "the" model's robustness. | Challenged: the two families disagreed on both the sign of the accuracy/Brier change and the magnitude of the fairness-gap change. |

## Internal verification

- The registry is generated from typed Python code and byte-compared in CI, alongside the
  existing v1.0, v1.1, and v1.2 registries.
- Training, tuning, adaptation, and test use disjoint deterministic seeds every replication;
  the adaptation split is diagnostic-only and never influences fitting, calibration, or
  thresholding.
- Model-family hyperparameters (logistic learning rate/iterations; tree depth/leaf size) were
  fixed before any cell was run and never adjusted based on a result.
- Unit tests cover the stressor transforms, the population generator, the missing/undefined
  aggregation semantics, and full-grid reproducibility.
- The public Robustness Lab imports the frozen registry rather than maintaining a second
  hand-copied result table, and keeps its synthetic values visually and analytically separate
  from both the base synthetic experiments and the governed UCI Adult evidence.

Internal verification is not external peer review. No independent researcher has audited the
design, code, or interpretations for this release.

## Threats to validity

- Every population, label, protected attribute, and subgroup is a synthetic abstraction; no
  result describes a real annotation process, protected class, or deployment population.
- Six stressors are studied one at a time; combined or compounding stressors (for example,
  small samples *and* measurement error together) are out of scope for this release.
- The two model families are illustrative, not exhaustive; neither is exempt from selection
  after the fact — both are reported at every magnitude regardless of which looks better.
- The unobserved-subgroup construction is confounded with an existing structural mechanism at
  the "no stress" control, as documented under hypothesis 4 above.
- A single global cost threshold (equal-cost declaration) is used throughout; cost-sensitivity
  interactions with these stressors were out of scope to keep the six-stressor grid tractable
  (see the [protocol](robustness-protocol.md)).
- Twelve replications per cell is fewer than the 20 used in v1.0/v1.1; replication ranges here
  are correspondingly less precise, which is itself visible in the reported ranges.

## Interpretation boundary

This study supports one claim: inside this declared synthetic generator, each stressor changes
some, but never all, prior descriptive conclusions, and the direction and size of that change
can depend on which inspectable model family was fit. It does not establish that either model
family is "more robust" in general, that any specific stressor magnitude is realistic for a
real deployment, or that any result here transfers to the governed UCI Adult evidence in
[`external-study-report.md`](external-study-report.md) or to a real population.
