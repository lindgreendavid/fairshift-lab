# Model Card: logistic baseline

## Model details

Version 0.1.0 uses binary logistic regression with an intercept and three inputs. Full-batch gradient descent starts from zero weights and runs for a configured number of iterations. The decision threshold defaults to `0.5`.

## Intended purpose

Provide a transparent reference model whose source-to-target behavior can be measured. It is not presented as an optimal predictor or fairness intervention.

## Evaluation

The same fitted parameters and threshold are evaluated on independently sampled source and target populations. Performance and group metrics are reported together. Tests establish implementation behavior, not real-world validity.

## Limitations

No calibration analysis, confidence intervals, hyperparameter selection, regularization, threshold optimization, or mitigation is included in v0.1.0. The protected attribute is used directly. Gradient descent has no convergence diagnostic.

## Ethical considerations

Fairness metrics can conflict and depend on construct validity, base rates, thresholds, and social context. A small metric gap is not proof of fairness; a large gap is not by itself a causal explanation. Human and domain review remain necessary.

