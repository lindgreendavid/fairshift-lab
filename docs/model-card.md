# Model Card: logistic baseline

## Model details

Version 1.2.0 uses binary logistic regression with an intercept. Synthetic studies use three inputs; the separate Adult reference study uses five declared numeric inputs. Full-batch gradient descent starts from zero weights and runs for a configured number of iterations. A source-only scalar temperature is fitted on an independent holdout; the decision threshold defaults to `0.5`. Policy benchmarks can also fit a model with deterministic group-label-cell sample weights.

## Intended purpose

Provide a transparent reference model whose source-to-target behavior can be measured. It is not presented as an optimal predictor or fairness intervention.

## Evaluation

The same fitted parameters and temperature are evaluated on independently sampled source and target populations. Performance, group metrics, raw and calibrated reliability, bootstrap intervals, and a fixed threshold sweep are reported together. Tests establish implementation behavior, not real-world validity.

## Limitations

Temperature scaling is limited to a fixed scalar search and may fail under shift. Expected calibration error depends on binning. Version 1.1 benchmarks only a fixed 19-point threshold grid, one joint-cell reweighing rule, supervised target recalibration, and four equalized-odds penalties. These methods are illustrative rather than exhaustive. Target recalibration requires a recent representative labeled target sample; group thresholds require protected attributes at decision time. Replication ranges do not quantify structural, construct, policy-selection, or future-shift uncertainty. The protected attribute is used directly. Gradient descent has no convergence diagnostic.

## Ethical considerations

Fairness metrics can conflict and depend on construct validity, base rates, thresholds, and social context. A small metric gap is not proof of fairness; a large gap is not by itself a causal explanation. Human and domain review remain necessary.

## Observational reference study in version 1.2.0

The historical Adult model is refitted for each declared development/tuning split. Scaling
statistics come from training only, and the official provider test file remains untouched.
The model intentionally excludes categorical predictors to keep transformations inspectable;
this is not a claim that those fields are irrelevant. The provider-coded sex field is used for
auditing and selected group-threshold policies, which would require access to that field at
decision time. Historical income prediction has no endorsed deployment purpose here.
