# Fairshift Lab v1.0 research report

## Status and review boundary

This is the first complete, reproducible report for the synthetic Fairshift Lab
experiment. The numbers were regenerated from the tagged source, checked against the
preregistered protocol, and reviewed for internal consistency. This is **not external peer
review**, a fairness certification, or evidence about people in any real population.

## Question

How do controlled target-domain interventions affect predictive performance, probability
reliability, and associational group-fairness measurements for a logistic model trained and
calibrated only on an unshifted source population?

## Design

The frozen grid contains three interventions, five magnitudes (`0.00`, `0.25`, `0.50`,
`0.75`, and `1.00`), and 20 independent seeds (`100` through `119`). Every cell therefore
contains 20 replications and 1,000 independently generated observations in each of the
training, calibration, source-evaluation, and target-evaluation populations. Across the 15
cells, this is 300 complete experiments and 1.2 million generated rows before bootstrap
resampling.

The model, temperature, and decision threshold are never selected with target data. The
threshold is fixed at `0.50`. For each metric, the report gives the mean across replications
and an empirical 2.5th–97.5th percentile replication range. That range describes variation
over the declared seeds; it is not a population confidence interval.

The complete machine-readable registry is [`reports/v1-study.json`](../reports/v1-study.json).
Regenerate it with:

```bash
python scripts/generate_study.py
```

## Main results

The table reports target means. Parentheses contain mean source-to-target change. Fairness
gaps use absolute differences, so larger values indicate greater measured disparity under
that definition. Lower Brier score and expected calibration error (ECE) are better.

| Intervention | Magnitude | Accuracy | AUROC | DP gap | EOds gap | Brier | ECE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Covariate | 0.00 | .710 (−.001) | .783 (−.001) | .046 (−.007) | .059 (−.012) | .189 (+.000) | .030 (−.003) |
| Covariate | 0.50 | .729 (+.018) | .789 (+.005) | .127 (+.074) | .131 (+.059) | .180 (−.010) | .034 (+.001) |
| Covariate | 1.00 | .790 (+.079) | .807 (+.024) | .176 (+.123) | .257 (+.186) | .145 (−.044) | .031 (−.002) |
| Concept | 0.00 | .710 (−.001) | .783 (−.001) | .046 (−.007) | .059 (−.012) | .189 (+.000) | .030 (−.003) |
| Concept | 0.50 | .596 (−.115) | .633 (−.151) | .046 (−.007) | .085 (+.013) | .254 (+.065) | .120 (+.087) |
| Concept | 1.00 | .466 (−.246) | .451 (−.333) | .046 (−.007) | .062 (−.010) | .333 (+.144) | .247 (+.214) |
| Prevalence | 0.00 | .710 (−.001) | .783 (−.001) | .046 (−.007) | .059 (−.012) | .189 (+.000) | .030 (−.003) |
| Prevalence | 0.50 | .713 (+.002) | .783 (−.001) | .039 (−.014) | .062 (−.009) | .189 (−.000) | .032 (−.001) |
| Prevalence | 1.00 | .713 (+.002) | .783 (−.001) | .051 (−.002) | .087 (+.016) | .189 (−.000) | .033 (−.000) |

### Result 1: accuracy and measured disparity can move in opposite directions

Under maximum covariate shift, mean target accuracy increased by `.079` while the
demographic-parity gap increased by `.123` and the equalized-odds gap by `.186`. Within
this generator, improved aggregate performance therefore did not imply improved group
parity.

### Result 2: concept shift was the dominant failure mode

At magnitude `1.00`, concept shift reduced mean AUROC by `.333` and accuracy by `.246`.
Mean Brier score worsened by `.144`, while ECE worsened by `.214`. Source-only temperature
scaling did not repair the changed target label mechanism.

### Result 3: prevalence shift was comparatively quiet in conditional metrics

Changing only the group mixture produced small mean changes in accuracy, AUROC, Brier
score, and ECE. This is expected inside the declared structural process because the
within-group feature and label equations remain fixed. It must not be generalized to an
unobserved deployment system.

### Result 4: a zero-magnitude target is a useful negative control

All three zero-magnitude rows are identical by construction. Their small nonzero
source-to-target changes reflect independent evaluation samples rather than an
intervention. This negative control guards against interpreting ordinary sampling
variation as shift impact.

## Hypothesis disposition

1. **Supported in the declared grid:** covariate shift changed target measurements as
   magnitude increased.
2. **Supported in the declared grid:** maximum concept shift caused a much larger mean
   AUROC loss than maximum prevalence shift (`−.333` versus `−.001`).
3. **Supported by the covariate intervention:** aggregate accuracy improved while two
   fairness gaps increased.
4. **Supported by the concept intervention:** source-fitted calibration did not preserve
   target reliability after the label mechanism changed.
5. **Demonstrated as sensitivity, not confirmed as a population claim:** the interactive
   threshold sweep shows that measured gaps and decisions vary with the cutoff. The report
   does not choose an operating threshold.

These dispositions are descriptive consequences of the frozen synthetic process. No
statistical test was used to turn them into claims about an external population.

## Verification record

- The registry is deterministic and records every seed, magnitude, sample count, target
  mean, source-to-target change, standard deviation, and replication range.
- Training, source calibration, source evaluation, and target evaluation are independent.
- Unit tests cover the generator, model, metrics, calibration, uncertainty, threshold
  sweep, study registry, serialization, and deterministic reproduction.
- Continuous integration checks three Python versions, strict typing, linting, branch
  coverage, package construction, web linting, production dependency audit, and the
  rendered research page.
- Code scanning and dependency monitoring remain enabled on the public repository.

## Threats to validity

The study uses one synthetic binary protected attribute, one binary label, one explicit
logistic baseline, one source-only calibrator, independent observations, and no missing
data. ECE depends on arbitrary bins. Absolute group gaps suppress direction. Empty
conditional subgroups still use the package's documented `0.0` fallback. The seed range
does not capture structural uncertainty, construct validity, labeling error, unobserved
groups, strategic response, institutional effects, or future shift. Multiple rows in the
grid are related descriptive views, not independent confirmatory tests.

## Interpretation boundary

The strongest supported statement is: **inside this explicit generator, different shift
mechanisms produced materially different combinations of predictive, calibration, and
group-gap behavior.** The study cannot say that a real model is fair, that any person was
treated justly, or that any decision system is lawful or ready for deployment.

## Primary research trail

- Hardt, Price, and Srebro (2016), *Equality of Opportunity in Supervised Learning*.
  https://proceedings.neurips.cc/paper_files/paper/2016/hash/6a9659feb1216f14f7384ba499518b38-Abstract.html
- Guo et al. (2017), *On Calibration of Modern Neural Networks*.
  https://proceedings.mlr.press/v70/guo17a.html
- Kleinberg, Mullainathan, and Raghavan (2017), *Inherent Trade-Offs in the Fair
  Determination of Risk Scores*. https://arxiv.org/abs/1609.05807
- Ovadia et al. (2019), *Can You Trust Your Model’s Uncertainty?*.
  https://proceedings.neurips.cc/paper_files/paper/2019/hash/8558cb408c1d76621371888657d2eb1d-Abstract.html
- Chen et al. (2022), *Fairness Transferability Subject to Bounded Distribution Shift*.
  https://arxiv.org/abs/2206.00129
- Barrainkua et al. (2024), *Uncertainty Matters*.
  https://proceedings.mlr.press/v238/barrainkua24a.html
- NIST (2023), *Artificial Intelligence Risk Management Framework 1.0*.
  https://doi.org/10.6028/NIST.AI.100-1
