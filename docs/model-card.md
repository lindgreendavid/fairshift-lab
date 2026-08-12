# Model Card: logistic baseline

## Model details

Version 0.3.0 uses binary logistic regression with an intercept and three inputs. Full-batch gradient descent starts from zero weights and runs for a configured number of iterations. A source-only scalar temperature is fitted on an independent holdout; the decision threshold defaults to `0.5`.

## Intended purpose

Provide a transparent reference model whose source-to-target behavior can be measured. It is not presented as an optimal predictor or fairness intervention.

## Evaluation

The same fitted parameters and temperature are evaluated on independently sampled source and target populations. Performance, group metrics, raw and calibrated reliability, bootstrap intervals, and a fixed threshold sweep are reported together. Tests establish implementation behavior, not real-world validity.

## Limitations

Temperature scaling is limited to a fixed scalar search and may fail under shift. Expected calibration error depends on binning. No hyperparameter selection, regularization, threshold optimization, decision-cost model, or mitigation is included in v0.3.0. Percentile-bootstrap intervals cover selected test-sample metrics only and do not quantify model-selection or structural uncertainty. The protected attribute is used directly. Gradient descent has no convergence diagnostic.

## Ethical considerations

Fairness metrics can conflict and depend on construct validity, base rates, thresholds, and social context. A small metric gap is not proof of fairness; a large gap is not by itself a causal explanation. Human and domain review remain necessary.
