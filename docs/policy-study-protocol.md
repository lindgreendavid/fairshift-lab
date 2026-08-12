# Policy study protocol

## Status and research question

This protocol was fixed before interpreting the complete v1.1 benchmark registry. It asks:

> When the deployment population shifts, how do explicitly declared error costs, data access, and mitigation choices change held-out decision cost and measured group gaps?

The study is synthetic and descriptive. It evaluates a finite set of policies; it does not search for a universally optimal, fair, lawful, or deployable policy.

## Prospective hypotheses

1. A source-selected cost threshold will not uniformly dominate the fixed `0.50` baseline after target shift.
2. Supervised target recalibration will improve Brier score and expected calibration error under maximum concept shift, conditional on access to representative recent target labels.
3. Increasing the preregistered equalized-odds penalty will not guarantee a lower held-out target equalized-odds gap because selection occurs on an independent source population.
4. Reweighing source group-label cells will not uniformly improve target decision cost and equalized-odds difference across shift mechanisms.
5. The benchmark-relative Pareto set will depend on the shift mechanism and declared false-negative cost.

## Design

The design crosses three maximum-magnitude (`1.00`) interventions with false-negative costs `0.5`, `1`, and `2`; false-positive cost is fixed at `1`. Each cell uses seeds `100` through `119` and 1,000 observations in every independently generated split.

For each seed and shift, the generator creates four disjoint populations:

| Split | Seed offset | Permitted use |
| --- | ---: | --- |
| Source training | `+0` | Fit baseline or reweighed logistic model |
| Source tuning | `+1` | Fit source temperature and select source policies |
| Target test | `+3` | Evaluate once; never select a policy |
| Target adaptation | `+7` | Fit the supervised target-adaptation benchmark only |

Target-test labels never influence model fitting, calibration, thresholds, or policy selection. The target-recalibration family is deliberately separated from source-only policies because it requires labeled target access.

## Policy families

1. **Fixed baseline:** source-calibrated probabilities with one `0.50` threshold.
2. **Cost-sensitive threshold:** one threshold from the 19-point source grid minimizes normalized empirical error cost.
3. **Target recalibration:** one temperature and one cost threshold are selected on the independent labeled target-adaptation split.
4. **Reweighed training:** Kamiran–Calders-style source weights make protected group and label independent in weighted expectation; the model is source-calibrated and source-cost-tuned.
5. **Group thresholds:** two source thresholds minimize normalized error cost plus `λ × equalized-odds difference`, for `λ ∈ {0.1, 0.3, 1, 3}`.

Ties prefer the candidate closest to the neutral `0.50` threshold, then the lower numerical threshold. This deterministic rule is not a substantive fairness judgment.

## Estimands

The decision objectives are normalized expected error cost and equalized-odds difference. The raw cost is

`C_FN × FN + C_FP × FP`.

It is divided by sample size and the larger declared unit cost, placing it in `[0, 1]` without claiming that the chosen costs have external validity. Secondary measurements are accuracy, demographic-parity difference, equal-opportunity difference, Brier score, and ten-bin expected calibration error.

For each metric and selected threshold, the registry reports the mean, sample standard deviation, and empirical 2.5th–97.5th percentile range across 20 seeded replications. Published aggregates are rounded to nine decimals only after calculation so Linux and macOS regenerate identical registry bytes.

## Pareto rule

A policy is marked efficient only within one shift and one error-cost declaration when no other benchmarked policy has both lower mean normalized cost and lower mean equalized-odds difference, with at least one strict improvement. This is a finite-set comparison—not proof of global optimality. The status ignores construct validity, individual treatment, calibration, rights, legality, operational capacity, and downstream effects.

## Analysis plan

- Publish every planned policy cell, including adverse and null results.
- Interpret direction, magnitude, and replication ranges rather than thresholding p-values.
- Compare mechanisms rather than pooling them.
- Treat target recalibration as an access-conditional oracle-like benchmark.
- Treat source-to-target mitigation failure as a result, not a reason to change the policy grid.
- Record the hypothesis dispositions in the final report.

## Primary methodological sources

- Hardt, Price, and Srebro, [Equality of Opportunity in Supervised Learning](https://proceedings.neurips.cc/paper_files/paper/2016/hash/6a9659feb1216f14f7384ba499518b38-Abstract.html), NeurIPS 2016.
- Kamiran and Calders, [Data preprocessing techniques for classification without discrimination](https://doi.org/10.1007/s10115-011-0463-8), *Knowledge and Information Systems* 2012.
- Corbett-Davies et al., [The Measure and Mismeasure of Fairness](https://jmlr.org/papers/v24/22-1511.html), *JMLR* 2023.
- Kamani et al., [Pareto Efficient Fairness in Supervised Learning](https://arxiv.org/abs/2104.01634), 2021.

## Ethical boundary

Protected attributes and outcomes are synthetic abstractions. Error costs are user-declared experimental inputs, not monetizations of human worth. Group-specific policies can require protected attributes at decision time and may be prohibited, harmful, or illegitimate in a real context. No registry result authorizes use in a high-impact decision.
