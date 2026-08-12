# Dataset card: UCI Adult / Census Income

## Provenance and access

- Provider: UCI Machine Learning Repository; donated by Barry Becker and Ronny Kohavi.
- DOI: https://doi.org/10.24432/C5XW20
- Provider description: extraction from the 1994 Census database under stated eligibility
  filters; 48,842 records across provider train and test files.
- Accessed: 2026-08-12 from `https://archive.ics.uci.edu/static/public/2/adult.zip`.
- Archive SHA-256: `7537312dd56c2b98035880805ce99e68183a30ee468aa5329d6df0fbb3cc21bb`.
- License displayed by UCI: CC BY 4.0. Raw files are nevertheless not committed; the pinned
  downloader verifies the archive before extraction.

## Study construction

The model uses age, education number, log-transformed capital gain, log-transformed capital
loss, and weekly hours. The historical provider-coded binary `sex` field is used only for
two-group auditing and is never called identity truth. The label is whether recorded annual
income exceeded USD 50,000; it is not qualification, merit, need, or deservingness.

The official provider test file remains held out. Each replication changes only the 80/20
development/tuning split. Sensitivity variants compare the provider age eligibility rule
with age 25+, and complete-case deletion with retaining rows whose missing values occur only
in unused categorical fields.

## Known limitations and prohibited interpretations

UCI does not document individual consent in the dataset record. The table is more than three
decades old; its categories and monetary threshold are historically situated. It omits much
of the causal and institutional context behind income. Missing-value markers and extraction
filters alter the cohort. The official train/test files do not establish temporal or
deployment shift.

Do not use this registry to rank people, infer discrimination in a current population,
recommend a policy, claim legal compliance, or treat lower group gaps as justice.
