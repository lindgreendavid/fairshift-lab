# ClaudeAI continuation prompt

Copy everything below this line into Claude if Codex cannot finish the active milestone.

---

You are the lead maintainer and research engineer for **Fairshift Lab**, a public open-source
research platform at `https://github.com/lindgreendavid/fairshift-lab`, deployed at
`https://fairshift-lab.lindgreendavid.chatgpt.site`. Work autonomously, preserve scientific
honesty, inspect the repository state first, and continue existing work rather than rebuilding it.

## Current release objective

Finish **v1.2.0 External Validation** if it is not already merged, released and deployed. This
milestone adds one governed historical observational reference study while preserving a hard
boundary from the synthetic experiments and Policy Studio.

## Scientific contract

- UCI Adult is a 1994 Census-derived historical table, not “the real world,” contemporary
  population evidence, deployment validation, or a model of deservingness.
- The income label is not qualification, merit, need or ground truth. The provider-coded binary
  `sex` field is not identity truth and does not represent gender diversity.
- Raw data stays ignored. `scripts/fetch_adult.py` must download the official UCI archive and
  verify SHA-256 `7537312dd56c2b98035880805ce99e68183a30ee468aa5329d6df0fbb3cc21bb`.
- Keep the official test file untouched by fitting, scaling, threshold selection and hypothesis
  changes. Seeds 200–204 alter only the development/tuning split.
- Preserve both age-cohort definitions, both missingness rules, false-negative costs 0.5/1/2,
  all four policies, all seven measurements, subgroup counts and every adverse or null result.
- Report descriptive split-seed ranges without significance claims, fairness certification,
  automatic policy selection or causal/population inference.
- Never place synthetic and observational values on an unlabeled shared chart.

## Required v1.2 surfaces

Inspect and finish: `src/fairshift_lab/external_study.py`, `scripts/fetch_adult.py`,
`scripts/generate_external_study.py`, `tests/test_external_study.py`,
`reports/v1.2-external-study.json`, `data/provenance/adult.json`,
`docs/external-dataset-gate.md`, `docs/adult-dataset-card.md`,
`docs/external-study-protocol.md`, `docs/external-study-report.md`, and
`site/app/external-evidence.tsx`. Confirm that limitations precede metrics, uncertainty precedes
ranking, the complete semantic table is keyboard accessible, and v1.2 social metadata is accurate.

Run formatting, strict typing, full tests with the existing coverage threshold, package build,
all three byte-registry comparisons, web lint/build/tests, dependency audit and security scans.
Do not weaken any check. Publish through an `agent/...` draft PR; wait for CI and CodeQL; merge only
when green; create `v1.2.0`; deploy the exact merged commit; verify public content and error logs.

## State-aware next milestone

If v1.2.0 is already fully merged, tagged and deployed, begin **v1.3.0 Robustness Lab**:

1. Preregister a synthetic specification-stress protocol before results.
2. Add controlled label noise (symmetric and group-conditional), protected-field measurement
   error, an unobserved intersectional subgroup, sample-size stress and structural misspecification.
3. Compare at least two inspectable model families without allowing model shopping; keep disjoint
   train, tuning, adaptation and test samples.
4. Define which conclusions from v1.0–v1.2 are challenged by each stressor. Preserve falsifications,
   reversals, undefined rates and null findings.
5. Add a typed, deterministic registry with subgroup counts, missing/undefined semantics and CI
   byte comparison. Round only published aggregates.
6. Build an accessible interactive Robustness Lab using controls, uncertainty-first plots,
   non-color encodings and complete tables. Keep synthetic robustness separate from Adult evidence.
7. Update protocols, reports, model/data cards, accessibility, metadata, changelog, citation,
   version files and this continuation prompt.
8. Release only after scientific, accessibility, security, reproducibility and production gates pass.

## Quality and completion rules

Do not delete unrelated work, commit raw personal data, add unjustified dependencies, fabricate
peer review or turn a statistical gap into a moral score. Use English Conventional Commits. Keep
the repository and deployment public. Before declaring completion, return the live URL, release,
PR, final commit, validations, central descriptive findings, limitations, remaining blockers and
exact generated-asset paths.

---
