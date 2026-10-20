"use client";

import { useMemo, useState } from "react";

import registry from "../../reports/v1.2-external-study.json";
import auditSummary from "./external-audit-summary.json";

type Estimate = {
  mean: number;
  standard_deviation: number;
  replication_lower: number;
  replication_upper: number;
};
type Cell = {
  cohort: string;
  missingness: string;
  false_negative_cost: number;
  policy: string;
  replications: number;
  subgroup_counts: Record<string, number>;
  estimates: Record<string, Estimate>;
};

const cells = registry.cells as Cell[];
const labels: Record<string, string> = {
  baseline: "Fixed baseline",
  source_cost_threshold: "Cost-sensitive threshold",
  reweighed_training: "Reweighed training",
  group_threshold: "Group thresholds · λ=1",
};

type AuditPolicy = {
  equalized_odds: number;
  lower: number;
  upper: number;
  noise_floor: number;
  gap_reduction?: number;
  gap_reduction_lower?: number;
  gap_reduction_upper?: number;
  gap_intervals_excluding_zero?: number;
  accuracy_intervals_excluding_zero?: number;
};
type AuditCohort = {
  cohort: string;
  missingness: string;
  test_size: number;
  seeds: number;
  policies: Record<string, AuditPolicy>;
};
const auditCohorts = auditSummary.cohorts as AuditCohort[];
const signed = (value: number) => `${value < 0 ? "−" : "+"}${Math.abs(value).toFixed(3)}`;

const format = (value: number) => value.toFixed(3);
const interval = (estimate: Estimate) =>
  `${format(estimate.mean)} · ${format(estimate.replication_lower)}–${format(estimate.replication_upper)}`;

export default function ExternalEvidence() {
  const [cohort, setCohort] = useState("provider_eligible");
  const [missingness, setMissingness] = useState("complete_case");
  const [cost, setCost] = useState(1);
  const selected = useMemo(
    () =>
      cells.filter(
        (cell) =>
          cell.cohort === cohort &&
          cell.missingness === missingness &&
          cell.false_negative_cost === cost,
      ),
    [cohort, missingness, cost],
  );
  const baseline = selected.find((cell) => cell.policy === "baseline") ?? selected[0];
  const audit = auditCohorts.find((item) => item.cohort === cohort && item.missingness === missingness);
  const mitigations = ["source_cost_threshold", "reweighed_training", "group_threshold"];

  return (
    <section className="external" id="external" aria-labelledby="external-heading">
      <header className="section-heading">
        <h2 id="external-heading">History is evidence.<br /><em>Not ground truth.</em></h2>
      </header>

      <div className="external-boundary">
        <strong>Observational boundary</strong>
        <p>
          This section uses a 1994 Census-derived UCI table. It is visually and analytically
          separate from the synthetic experiments above. The income label is not merit,
          qualification, need, or deservingness; the provider-coded binary sex field is not
          identity truth.
        </p>
        <a href="https://github.com/lindgreendavid/fairshift-lab/blob/main/docs/external-dataset-gate.md">
          Read the admission gate ↗
        </a>
      </div>

      <div className="external-controls">
        <label>
          <span>Cohort definition</span>
          <select value={cohort} onChange={(event) => setCohort(event.target.value)}>
            <option value="provider_eligible">Provider eligibility · age 17+</option>
            <option value="age_25_plus">Sensitivity cohort · age 25+</option>
          </select>
        </label>
        <label>
          <span>Missingness rule</span>
          <select value={missingness} onChange={(event) => setMissingness(event.target.value)}>
            <option value="complete_case">Drop any row with ?</option>
            <option value="numeric_complete">Retain ? in unused fields</option>
          </select>
        </label>
        <label>
          <span>False-negative cost</span>
          <select value={cost} onChange={(event) => setCost(Number(event.target.value))}>
            <option value="0.5">0.5 × false positive</option>
            <option value="1">Equal costs</option>
            <option value="2">2 × false positive</option>
          </select>
        </label>
      </div>

      {baseline && (
        <div className="external-summary" aria-live="polite">
          <article><span>Held-out records</span><strong>{baseline.subgroup_counts.test_total.toLocaleString()}</strong><small>Female-coded {baseline.subgroup_counts.test_group_female.toLocaleString()} · Male-coded {baseline.subgroup_counts.test_group_male.toLocaleString()}</small></article>
          <article><span>Baseline accuracy</span><strong>{format(baseline.estimates.accuracy.mean)}</strong><small>Range {format(baseline.estimates.accuracy.replication_lower)}–{format(baseline.estimates.accuracy.replication_upper)}</small></article>
          <article><span>Baseline equalized-odds gap</span><strong>{format(baseline.estimates.equalized_odds_difference.mean)}</strong><small>Descriptive split-seed range, not a justice score</small></article>
          <article className="external-summary__warning"><span>Replications</span><strong>{baseline.replications}</strong><small>Only the development/tuning split changes</small></article>
        </div>
      )}

      <div className="external-reading">
        <h3>Uncertainty before ranking</h3>
        <p>
          Mean · empirical 2.5th–97.5th split-seed range. Small differences can reverse under
          another declared cohort, missingness rule, cost, or split. No policy is selected.
        </p>
      </div>

      {/* Keyboard focus makes the overflowing data region independently scrollable. */}
      {/* eslint-disable-next-line jsx-a11y/no-noninteractive-tabindex */}
      <div className="table-scroll" role="region" tabIndex={0} aria-label="Complete observational policy results">
        <table>
          <caption>All policies for the selected historical cohort and decision-cost declaration</caption>
          <thead><tr><th scope="col">Policy</th><th scope="col">Accuracy</th><th scope="col">Normalized cost</th><th scope="col">DP gap</th><th scope="col">EO gap</th><th scope="col">EOdds gap</th><th scope="col">Brier</th><th scope="col">ECE</th></tr></thead>
          <tbody>
            {selected.map((cell) => (
              <tr key={cell.policy}>
                <th scope="row">{labels[cell.policy]}</th>
                <td>{interval(cell.estimates.accuracy)}</td>
                <td>{interval(cell.estimates.expected_cost)}</td>
                <td>{interval(cell.estimates.demographic_parity_difference)}</td>
                <td>{interval(cell.estimates.equal_opportunity_difference)}</td>
                <td>{interval(cell.estimates.equalized_odds_difference)}</td>
                <td>{interval(cell.estimates.brier_score)}</td>
                <td>{interval(cell.estimates.expected_calibration_error)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {audit && (
        <div className="audit">
          <div className="audit__lead">
            <h3>Post-hoc check: are the gap differences bigger than test-set noise?</h3>
            <p>
              The ranges above only reflect how the development file was split. Resampling the {audit.test_size.toLocaleString("en-GB")} held-out
              people shows how much the gaps move for a different draw of test people. In this cohort,{" "}
              {mitigations.reduce((sum, key) => sum + (audit.policies[key].gap_intervals_excluding_zero ?? 0), 0) === 0
                ? `none of the ${mitigations.length * audit.seeds} paired comparisons with the baseline separates from zero`
                : `${mitigations.reduce((sum, key) => sum + (audit.policies[key].gap_intervals_excluding_zero ?? 0), 0)} of ${mitigations.length * audit.seeds} paired comparisons separate from zero`}.
              Not preregistered; run at 1× false-negative cost only.
            </p>
          </div>
          <div className="audit__table">
            {/* eslint-disable-next-line jsx-a11y/no-noninteractive-tabindex */}
            <div className="table-scroll" role="region" tabIndex={0} aria-label="Test-set uncertainty of the equalized-odds gap">
              <table>
                <caption>Equalized-odds gap with 95% person-level bootstrap interval, the gap expected with no group information, and the paired change from the baseline (mean over {audit.seeds} split seeds)</caption>
                <thead><tr><th scope="col">Policy</th><th scope="col">Gap</th><th scope="col">95% interval</th><th scope="col">No-information floor</th><th scope="col">Baseline minus policy</th></tr></thead>
                <tbody>
                  {Object.keys(labels).map((key) => {
                    const row = audit.policies[key];
                    return (
                      <tr key={key}>
                        <th scope="row">{labels[key]}</th>
                        <td>{format(row.equalized_odds)}</td>
                        <td>{format(row.lower)}–{format(row.upper)}</td>
                        <td>{format(row.noise_floor)}</td>
                        <td>{row.gap_reduction === undefined ? "—" : `${signed(row.gap_reduction)} (${signed(row.gap_reduction_lower ?? 0)} to ${signed(row.gap_reduction_upper ?? 0)})`}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      <div className="external-links">
        <a href="https://github.com/lindgreendavid/fairshift-lab/blob/main/docs/adult-dataset-card.md">Dataset card ↗</a>
        <a href="https://github.com/lindgreendavid/fairshift-lab/blob/main/docs/external-study-protocol.md">Preregistered protocol ↗</a>
        <a href="https://github.com/lindgreendavid/fairshift-lab/blob/main/docs/external-study-report.md">Bounded report ↗</a>
        <a href="https://github.com/lindgreendavid/fairshift-lab/blob/main/reports/v1.2-external-study.json">Frozen registry ↗</a>
      </div>
    </section>
  );
}
