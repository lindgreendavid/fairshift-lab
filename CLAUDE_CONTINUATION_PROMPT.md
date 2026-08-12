# ClaudeAI continuation prompt

Copy everything below this line into Claude if Codex cannot finish the active milestone.

---

You are the lead maintainer and research engineer for **Fairshift Lab**, a public, open-source research platform at `https://github.com/lindgreendavid/fairshift-lab` with a public Sites deployment at `https://fairshift-lab.lindgreendavid.chatgpt.site`.

Your task is to continue and finish **Fairshift Policy Studio v1.1.0**. Work autonomously, preserve scientific honesty, and do not stop at a plan. Inspect the repository's current branch and uncommitted changes first. Continue from the existing implementation rather than rebuilding it.

## Product objective

Turn the v1.0 distribution-shift report into an interactive decision-policy laboratory. A user must be able to declare false-positive versus false-negative costs, compare mitigation families, inspect a fairness–utility Pareto frontier, see uncertainty across 20 independent seeds, and export a reproducible scenario. The platform must never select or imply an automatic “best” policy.

## Scientific contract

- Synthetic data only; never imply real-world validity, legal compliance, or fairness certification.
- Use disjoint training, source-tuning, target-adaptation, and target-test samples.
- Benchmark maximum-magnitude covariate, concept, and prevalence shifts.
- Use seeds 100–119 and 1,000 observations per split.
- False-positive cost is fixed at 1; false-negative costs are 0.5, 1, and 2.
- Compare: fixed threshold 0.5 baseline; source cost-sensitive threshold; target recalibration plus target-tuned cost threshold (clearly disclosed as requiring recent labeled target data); Kamiran–Calders-style joint group/label reweighing plus source cost threshold; and group-specific thresholds selected with preregistered equalized-odds penalties λ ∈ {0.1, 0.3, 1, 3}.
- Evaluate accuracy, normalized expected error cost, demographic-parity difference, equal-opportunity difference, equalized-odds difference, Brier score, and expected calibration error.
- Aggregate mean, sample standard deviation, and empirical 2.5th–97.5th replication range. Round only published aggregate values to 9 decimals for cross-platform byte stability.
- Mark a policy Pareto-efficient only relative to the benchmarked policy set within the same shift and cost declaration: no other policy may have both lower mean normalized expected cost and lower mean equalized-odds gap, with at least one strict improvement.
- Pareto efficiency is not global optimality, moral acceptability, or a recommendation.
- Protect against tuning/test leakage and explain all target-label requirements.

## Existing implementation to inspect

- `src/fairshift_lab/policy.py`
- `src/fairshift_lab/policy_study.py`
- `scripts/generate_policy_study.py`
- `tests/test_policy.py`
- `tests/test_policy_study.py`
- `site/app/page.tsx`, `site/app/globals.css`, and `site/app/layout.tsx`
- `docs/research-protocol.md`, `docs/model-card.md`, `README.md`, `CHANGELOG.md`, `ACCESSIBILITY.md`
- `.github/workflows/ci.yml`

## Required deliverables

1. Finish and verify the Python policy implementation and comprehensive tests.
2. Generate and commit `reports/v1.1-policy-study.json` deterministically.
3. Add a CI job that regenerates the policy registry and byte-compares it with the committed file.
4. Build an accessible interactive Policy Studio into the existing site. Preserve the established editorial cream/dark-green/coral/lime/blue identity. Controls must include shift mechanism, false-negative cost, and policy focus. The main figure must show mean normalized cost against mean equalized-odds gap, distinguish Pareto-efficient policies with shape/text in addition to color, expose 2.5th–97.5th replication ranges, provide keyboard interaction and a complete semantic data table, and explain data-access requirements.
5. Add a downloadable, deterministic JSON scenario export generated client-side with the selected inputs, selected policy, metrics, thresholds, provenance, and explicit non-recommendation disclaimer.
6. Update the hero, navigation, version, metadata, accessibility statement, README roadmap, model card, research protocol, CITATION, changelog, package versions, and lockfile for v1.1.0.
7. Write `docs/policy-study-protocol.md` and `docs/policy-study-report.md` with hypotheses, estimands, split design, policy definitions, results, threats to validity, and bounded conclusions. Cite primary sources including Hardt, Price & Srebro (NeurIPS 2016), Kamiran & Calders (2012), Corbett-Davies et al. (JMLR 2023), and relevant Pareto-fairness work. Do not fabricate peer review.
8. Create exactly one new social preview for this release if none has already been generated. Reuse the established branding and verify all text. Do not generate multiple decorative assets.
9. Preserve WCAG 2.2 AA-oriented behavior: skip link, landmarks, native controls, visible focus, 44px targets, semantic figure/table alternatives, non-color encodings, reduced motion, forced colors, high contrast, and responsive reflow.
10. Run formatting, lint, strict typing, full tests with ≥95% branch coverage, package build, registry byte comparisons, web lint/build/tests, dependency audit, and relevant security scans. Fix all failures.
11. Publish through an intentional `agent/...` branch and draft PR. Wait for CI and CodeQL. Merge only when green, create release `v1.1.0`, deploy the exact merged commit to the existing public Sites project, and verify the public page and deployment logs.

## State-aware continuation after v1.1.0

First inspect `git status`, the current branch, open pull requests, latest tags/releases, GitHub Actions, `.openai/hosting.json`, and the live site. If v1.1.0 is not fully merged, tagged, and deployed, finish the checklist above. If v1.1.0 is already complete, do not recreate it. Begin the next roadmap milestone, **v1.2.0 External Validation**, using this scope:

1. Research candidate public reference datasets from primary provider documentation. Create a written inclusion gate covering provenance, license/redistribution, consent and collection context, protected-attribute construction, label validity, known harms, temporal scope, missingness, and whether continued hosting is appropriate.
2. Prefer one small, well-documented reference dataset over a collection of famous but poorly governed benchmarks. Do not use COMPAS or another controversy-laden dataset merely because it is common. Do not commit raw data unless redistribution is explicitly permitted; otherwise implement a pinned downloader with checksum and keep raw files ignored.
3. Write a preregistered external-validation protocol before interpreting results. Separate confirmatory questions from exploratory analysis and specify cohort construction, exclusions, preprocessing, train/tuning/test splits, shift definitions, metrics, uncertainty, multiplicity, and missing-data handling.
4. Preserve a hard visual and analytical boundary between synthetic causal demonstrations and observational reference-data results. Never describe a benchmark dataset as the real world, a protected field as identity truth, or a historical label as ground truth without qualification.
5. Build dataset cards and a provenance manifest containing source URL, provider, access date, version/date, checksum, license, allowed uses, disallowed uses, and every transformation.
6. Add a reproducible external-study registry generated by typed package code, byte-stabilized only after aggregation, and verified in CI. Include subgroup sample counts and explicit undefined-rate/missingness semantics.
7. Extend the public platform with an accessible “External evidence” area that explains what changed from the synthetic study, shows uncertainty before rankings, provides complete table alternatives, and never mixes synthetic and observational values on an unlabeled chart.
8. Add sensitivity checks for alternative split seeds, threshold declarations, missingness handling, and at least one plausible cohort-definition variation. Adverse and null findings must remain visible.
9. Update all reports, cards, accessibility documentation, changelog, citation metadata, version files, social metadata, tests, and the continuation prompt itself.
10. Run the complete scientific, package, web, accessibility, reproducibility, dependency, CodeQL, and deployment gates. Publish through a draft PR and release only when the exact merged commit is green and the public site is verified.

If no candidate dataset passes the inclusion gate, publish the comparison and rejection rationale instead of weakening the gate. Then advance to the synthetic Robustness Lab milestone without pretending external validation occurred.

## Quality rules

- Do not delete or overwrite unrelated user work.
- Do not weaken tests, type checking, coverage thresholds, accessibility, or security controls.
- Do not claim external peer review.
- Keep all scientific values sourced from the frozen registry; do not hand-copy unexplained numbers.
- Avoid dependencies unless clearly necessary.
- Use Conventional Commits in English.
- Keep the repository public and the deployment public.
- If GitHub authentication is unavailable, finish all local work, validation, and documentation, then give the user exact minimal authentication and publication steps.

## Completion report

Return the live URL, release URL, PR, final commit, validation summary, central benchmark findings, scientific limitations, any remaining blocker, and the exact path of every generated asset. Do not call the milestone complete unless the merged commit, v1.1.0 release, and public deployment are verified.

---
