# Fairshift Policy Studio v1.1 — internally verified report

## Executive finding

No mitigation family dominated across covariate, concept, and group-prevalence shift. The finite Pareto set changed with both the shift mechanism and the declared false-negative cost. The result directly rejects a context-free “best fairness intervention” story.

This report covers 72 aggregate cells: three maximum-magnitude shifts × three error-cost declarations × eight policies. Every cell summarizes 20 independent seeded replications. Across four disjoint splits per replication world, the benchmark generated 240,000 rows before policy evaluation. The immutable machine-readable record is [`reports/v1.1-policy-study.json`](../reports/v1.1-policy-study.json).

## Methods

The complete prospective design is in [`policy-study-protocol.md`](policy-study-protocol.md). Briefly, models are trained on unshifted source data. Source policies use a separate source-tuning sample. Target recalibration alone may use a separate labeled target-adaptation sample. All policies are evaluated once on an untouched target test sample.

Normalized decision cost and equalized-odds difference are minimized jointly only for the purpose of marking a benchmark-relative Pareto set. Accuracy, demographic-parity difference, equal-opportunity difference, Brier score, expected calibration error, and both group thresholds are published alongside them. A low measured group gap is not equated with justice or nondiscrimination.

## Results at equal error costs

The following values are means across 20 replications when false-positive and false-negative costs both equal `1`.

| Shift | Policy | Normalized cost | Equalized-odds gap | Accuracy | ECE | Pareto status |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Concept | Fixed baseline | 0.534 | 0.062 | 0.466 | 0.247 | Dominated |
| Concept | Target recalibration | 0.486 | 0.006 | 0.514 | 0.098 | Efficient here |
| Covariate | Fixed baseline | 0.210 | 0.257 | 0.790 | 0.031 | Efficient here |
| Covariate | Group thresholds, `λ=1` | 0.216 | 0.251 | 0.784 | 0.031 | Efficient here |
| Prevalence | Fixed baseline | 0.287 | 0.087 | 0.713 | 0.033 | Efficient here |
| Prevalence | Reweighed training | 0.292 | 0.079 | 0.708 | 0.031 | Efficient here |
| Prevalence | Group thresholds, `λ=1` | 0.300 | 0.071 | 0.700 | 0.033 | Efficient here |

“Efficient here” means only that another policy in the same finite comparison did not improve both mean cost and mean equalized-odds gap. Replication ranges and every omitted policy are available in the registry and interactive data table.

## Four central results

### 1. Concept shift required target evidence to repair calibration

Under maximum concept shift and equal error costs, the source-calibrated baseline had mean ECE `0.247`, accuracy `0.466`, and cost `0.534`. Supervised target recalibration reduced mean ECE to `0.098`, raised accuracy to `0.514`, and reduced cost to `0.486`. It was the only Pareto-efficient benchmarked policy for that scenario.

This is not evidence that recalibration repairs concept shift generally. Performance remained weak, the adaptation required 1,000 recent labeled target cases per seed, and temperature scaling cannot restore ranking information that the changed label mechanism destroyed.

### 2. Source-selected mitigation did not reliably transfer

The equalized-odds penalties were optimized on source tuning data, but their held-out target ordering was not monotone. Under equal-cost covariate shift, increasing `λ` from `0.1` to `1` moved the mean target gap from `0.262` to `0.251`, while `λ=3` moved it back to `0.258` and increased cost to `0.233`. Selection on one population did not guarantee the intended ordering after shift.

### 3. Reweighing was mechanism-dependent

At equal costs, source reweighing was dominated under concept and covariate shift. Under prevalence shift it joined the relative Pareto set: compared with the baseline, mean equalized-odds difference fell from `0.087` to `0.079`, while mean cost rose from `0.287` to `0.292`. The trade-off is small and descriptive, but it demonstrates why a single headline effect would be misleading.

### 4. Declared error costs changed the frontier

The relative frontier was not stable across false-negative costs `0.5`, `1`, and `2`. For maximum covariate shift with false-negative cost `2`, seven policies appeared on the finite frontier because small cost and gap changes traded against one another. Under maximum concept shift, target recalibration remained the only efficient policy across all three declarations. A frontier is therefore a scenario-specific comparison surface, not a ranking of methods.

## Hypothesis dispositions

1. **Supported:** the source cost threshold did not uniformly dominate the fixed baseline.
2. **Supported within this generator:** target recalibration improved Brier/ECE under maximum concept shift, conditional on labeled target access.
3. **Supported:** larger source equalized-odds penalties did not guarantee smaller held-out target gaps.
4. **Supported:** reweighing did not uniformly improve cost and equalized odds across mechanisms.
5. **Supported:** the finite Pareto set varied with shift and error-cost declaration.

These are descriptive dispositions for the preregistered synthetic grid. No frequentist population test or multiplicity-adjusted confirmatory claim is made.

## Internal verification

- The registry is generated from typed Python code and byte-compared in CI.
- Training, source tuning, target adaptation, and target testing use disjoint deterministic seeds.
- Unit tests cover reweighing, cost normalization, group thresholds, deterministic selection, configuration validation, aggregation, and Pareto marking.
- The public site imports the frozen registry rather than maintaining a second hand-copied result table.
- Every chart has an equivalent semantic table, and the scenario export includes provenance and a non-recommendation disclaimer.

Internal verification is not external peer review. No independent researcher has audited the design, code, or interpretations for this release.

## Threats to validity

- One transparent logistic baseline and one synthetic structural process cannot represent real decision systems.
- The protected attribute is binary and directly available; intersectionality and proxy measurement are absent.
- Error costs are arbitrary declared ratios and omit distributional, delayed, and non-quantifiable harms.
- Reweighing and threshold post-processing are limited implementations, not exhaustive versions of their source methods.
- The 19-point threshold grid can miss better intermediate policies.
- Pareto status uses aggregate means and only two objectives; uncertainty and other harms can reverse a practical judgment.
- Target adaptation assumes timely, representative, valid labels, which may be impossible precisely where shift matters.
- ECE is bin-dependent, and calibration is not sufficient for decision validity.

## Interpretation boundary

The study supports one claim: inside this declared generator, mitigation behavior depends materially on shift, data access, and decision costs. It does not establish that group-specific thresholds are appropriate, that reweighing removes discrimination, that target labels are unbiased, or that any policy should be deployed.
