# Model Card: logistic baseline and shallow decision tree

## Model details

Version 1.2.0 uses binary logistic regression with an intercept. Synthetic studies use three inputs; the separate Adult reference study uses five declared numeric inputs. Full-batch gradient descent starts from zero weights and runs for a configured number of iterations. A source-only scalar temperature is fitted on an independent holdout; the decision threshold defaults to `0.5`. Policy benchmarks can also fit a model with deterministic group-label-cell sample weights.

Version 1.3.0 adds a second inspectable family, `fairshift_lab.model.ShallowDecisionTree`: a greedy, deterministic, depth-limited (default depth `3`, minimum `20` samples per leaf) CART-style classifier that splits on weighted Gini impurity. Ties in the split search break on the lowest feature index, then the lowest threshold — a deterministic rule, not a substantive judgment. Leaf probabilities use add-one Laplace smoothing so they never saturate to exactly `0` or `1`, keeping Brier score and expected calibration error well defined. Both families are fit on identical inputs and are never selected or retuned based on which one looks fairer or more robust; the [robustness protocol](robustness-protocol.md) fixes both configurations before any stressed cell is run.

## Intended purpose

Provide a transparent reference model whose source-to-target behavior can be measured. It is not presented as an optimal predictor or fairness intervention.

## Evaluation

The same fitted parameters and temperature are evaluated on independently sampled source and target populations. Performance, group metrics, raw and calibrated reliability, bootstrap intervals, and a fixed threshold sweep are reported together. Tests establish implementation behavior, not real-world validity.

## Limitations

Temperature scaling is limited to a fixed scalar search and may fail under shift. Expected calibration error depends on binning. Version 1.1 benchmarks only a fixed 19-point threshold grid, one joint-cell reweighing rule, supervised target recalibration, and four equalized-odds penalties. These methods are illustrative rather than exhaustive. Target recalibration requires a recent representative labeled target sample; group thresholds require protected attributes at decision time. Replication ranges do not quantify structural, construct, policy-selection, or future-shift uncertainty. The protected attribute is used directly. Gradient descent has no convergence diagnostic. The shallow decision tree's greedy, depth-limited search is not guaranteed to find a globally optimal tree, and depth `3` is an illustrative choice fixed before results, not a tuned optimum.

## Robustness stress study in version 1.3.0

Both model families are refit under six preregistered synthetic stressors (see [`robustness-protocol.md`](robustness-protocol.md)): symmetric and group-conditional label noise, protected-field measurement error, an unobserved intersectional subgroup, sample-size stress, and a structural misspecification the linear family cannot represent. Findings, including falsifications of the protocol's own prospective hypotheses, are in [`robustness-report.md`](robustness-report.md). No stressor or model-family comparison in this study licenses a claim that either family is "more robust" outside this declared synthetic generator, or that either represents a general property of logistic regression or decision trees in real deployments.

## Ethical considerations

Fairness metrics can conflict and depend on construct validity, base rates, thresholds, and social context. A small metric gap is not proof of fairness; a large gap is not by itself a causal explanation. Human and domain review remain necessary.

## Observational reference study in version 1.2.0

The historical Adult model is refitted for each declared development/tuning split. Scaling
statistics come from training only, and the official provider test file remains untouched.
The model intentionally excludes categorical predictors to keep transformations inspectable;
this is not a claim that those fields are irrelevant. The provider-coded sex field is used for
auditing and selected group-threshold policies, which would require access to that field at
decision time. Historical income prediction has no endorsed deployment purpose here.
