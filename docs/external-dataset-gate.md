# External dataset inclusion gate

Decision date: 2026-08-12. The gate was written before inspecting model results.

## Admission criteria

A reference dataset must have an identifiable provider and version, a stable source, an
explicit license or public-use basis, documented collection and field definitions, a
defensible non-deployment research purpose, manageable privacy risk, and reproducible
acquisition. Unknown consent, constructed protected fields, historical labels, missingness,
temporal staleness and known harms must be disclosed rather than silently converted into
technical variables.

| Candidate | Decision | Evidence and rationale |
| --- | --- | --- |
| UCI Adult / Census Income | Admit with severe use limits | UCI identifies a 1994 Census extraction, 48,842 rows, missing values, a DOI and CC BY 4.0. The archive is small and checksum-able. Collection consent is not documented by UCI, its `sex` and `race` categories are reductive historical provider codes, and income is not qualification or deservingness. It is admitted only to test whether conclusions survive contact with a historical observational table. |
| 2024 ACS PUMS | Defer | The Census Bureau supplies disclosure-protected public-use records, annual documentation, weights, accuracy material and data dictionaries. A valid study must honor its sample design and weighting rather than treating rows as a simple benchmark; that is a future survey-specific protocol. |
| Statlog German Credit | Reject | Although UCI now displays CC BY 4.0, UCI's corrected South German Credit record states that the famous original has severe coding errors and lacks background information. That fails provenance and construct-validity gates. |
| COMPAS-derived benchmarks | Reject for this milestone | Common use is not adequate provenance or governance. No provider-controlled, purpose-compatible version was identified that would justify making criminal-justice labels a convenience benchmark. |

Primary provider records: [UCI Adult](https://archive.ics.uci.edu/dataset/2/adult),
[ACS PUMS](https://www.census.gov/programs-surveys/acs/microdata.html),
[ACS documentation](https://www.census.gov/programs-surveys/acs/microdata/documentation.html),
and [UCI South German Credit](https://archive.ics.uci.edu/dataset/573/south%2Bgerman%2Bcredit%2Bupdate).

Passing this gate means “usable for this bounded methods exercise,” not ethical approval,
representativeness, contemporary validity, or permission for decisions about people.
