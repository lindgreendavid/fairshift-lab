# Data Card: synthetic populations

## Origin and license

All observations are generated locally by `fairshift_lab.data.generate_population`; no external dataset or personal data is used. Generator code is covered by the repository's MIT License.

## Schema

| Field | Type | Meaning |
| --- | --- | --- |
| `feature_one` | float | continuous synthetic predictor influenced by the protected attribute |
| `feature_two` | float | independent continuous synthetic predictor in the source |
| `sensitive` | integer 0/1 | synthetic protected-group indicator |
| `label` | integer 0/1 | Bernoulli outcome from the documented equation |

The model feature matrix includes the protected attribute so that the baseline's behavior is explicit rather than hidden behind proxy-only assumptions.

## Intended uses

Method development, teaching, unit testing, and controlled studies of measurement behavior under shift.

## Prohibited uses

Decisions about real people; claims about any demographic group; legal or regulatory certification; estimating real discrimination; safety-critical deployment.

## Known limitations

Binary groups and outcomes, no missing data, no intersectionality, independent observations, simplified functional form, and no institutional context. Synthetic generation eliminates privacy risk but not interpretation risk.

## Robustness stress populations in version 1.3.0

`fairshift_lab.robustness.generate_robust_population` extends the schema above with an
`subgroup` field: an integer 0/1 intersectional indicator (`sensitive == 1` and `feature_two`
above its population median) that is never included in the model feature matrix and never used
to select a policy. Six controlled stressors — implemented in
`fairshift_lab.robustness` and documented in [`robustness-protocol.md`](robustness-protocol.md)
— can each corrupt or reweight this generator: symmetric label noise, group-conditional label
noise, protected-field measurement error, an unobserved-subgroup outcome penalty, sample-size
reduction, and a feature-by-protected-attribute interaction the models are never given as an
engineered input. Every population remains synthetic; none of these transformations touch UCI
Adult or any other observational dataset, and this module's results must never share an
unlabeled chart, table, or scale with either the base synthetic study or the external evidence.

