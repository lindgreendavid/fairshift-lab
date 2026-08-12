"use client";

import { useMemo, useState } from "react";

import registry from "../../reports/v1.2-external-study.json";

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

  return (
    <section className="external" id="external" aria-labelledby="external-heading">
      <header className="section-heading">
        <div><span className="section-index">05</span><p>External evidence</p></div>
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

      <div className="external-links">
        <a href="https://github.com/lindgreendavid/fairshift-lab/blob/main/docs/adult-dataset-card.md">Dataset card ↗</a>
        <a href="https://github.com/lindgreendavid/fairshift-lab/blob/main/docs/external-study-protocol.md">Preregistered protocol ↗</a>
        <a href="https://github.com/lindgreendavid/fairshift-lab/blob/main/docs/external-study-report.md">Bounded report ↗</a>
        <a href="https://github.com/lindgreendavid/fairshift-lab/blob/main/reports/v1.2-external-study.json">Frozen registry ↗</a>
      </div>
    </section>
  );
}
