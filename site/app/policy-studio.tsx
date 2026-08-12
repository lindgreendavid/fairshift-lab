"use client";

import { useMemo, useState } from "react";

import policyStudy from "../../reports/v1.1-policy-study.json";

type ShiftKind = "covariate" | "concept" | "prevalence";

type Estimate = {
  mean: number;
  standard_deviation: number;
  replication_lower: number;
  replication_upper: number;
};

type PolicyCell = {
  shift: ShiftKind;
  magnitude: number;
  false_negative_cost: number;
  false_positive_cost: number;
  policy: string;
  replications: number;
  pareto_efficient: boolean;
  metrics: Record<string, Estimate>;
  threshold_group_zero: Estimate;
  threshold_group_one: Estimate;
};

type PolicyDefinition = {
  key: string;
  label: string;
  access: string;
  selection: string;
};

const cells = policyStudy.cells as PolicyCell[];
const policies = policyStudy.policies as PolicyDefinition[];

const shiftLabels: Record<ShiftKind, string> = {
  covariate: "Covariate shift",
  concept: "Concept shift",
  prevalence: "Group prevalence shift",
};

const costLabels: Record<string, string> = {
  "0.5": "False negatives cost half as much",
  "1": "Both errors cost the same",
  "2": "False negatives cost twice as much",
};

function number(value: number) {
  return value.toFixed(3);
}

function policyNumber(key: string) {
  return policies.findIndex((policy) => policy.key === key) + 1;
}

function policyClass(key: string) {
  if (key === "baseline") return "baseline";
  if (key === "target_recalibration") return "adaptation";
  if (key === "reweighed_training") return "reweighing";
  if (key.startsWith("group_threshold")) return "group-threshold";
  return "threshold";
}

function PolicyPlot({
  scenario,
  selectedPolicy,
}: {
  scenario: PolicyCell[];
  selectedPolicy: string;
}) {
  const width = 760;
  const height = 430;
  const left = 82;
  const right = 718;
  const top = 38;
  const bottom = 350;
  const maximumCost = Math.max(
    ...scenario.map((cell) => cell.metrics.expected_cost.replication_upper),
  ) * 1.08;
  const maximumGap = Math.max(
    ...scenario.map((cell) => cell.metrics.equalized_odds_difference.replication_upper),
  ) * 1.08;
  const x = (value: number) => left + (value / maximumCost) * (right - left);
  const y = (value: number) => bottom - (value / maximumGap) * (bottom - top);
  const ticks = [0, 0.25, 0.5, 0.75, 1];

  return (
    <figure className="policy-plot">
      <div className="policy-plot__heading">
        <div>
          <span>Benchmark-relative frontier</span>
          <strong>Decision cost ↔ equalized-odds gap</strong>
        </div>
        <div className="policy-shape-key" aria-hidden="true">
          <span><i className="shape-diamond" /> Efficient here</span>
          <span><i className="shape-circle" /> Dominated here</span>
        </div>
      </div>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-labelledby="policy-plot-title policy-plot-description"
      >
        <title id="policy-plot-title">Policy cost and equalized-odds comparison</title>
        <desc id="policy-plot-description">
          Eight policies compared by mean normalized expected error cost on the horizontal axis
          and mean equalized-odds gap on the vertical axis. Lower is better on both axes. Whiskers
          show empirical 2.5th to 97.5th percentile ranges across 20 seeded replications. Diamonds
          mark policies that are Pareto-efficient only within this benchmark and scenario.
        </desc>
        <rect className="policy-plot__frame" x={left} y={top} width={right - left} height={bottom - top} />
        {ticks.map((tick) => (
          <g key={`grid-${tick}`} aria-hidden="true">
            <line className="policy-plot__grid" x1={x(maximumCost * tick)} y1={top} x2={x(maximumCost * tick)} y2={bottom} />
            <line className="policy-plot__grid" x1={left} y1={y(maximumGap * tick)} x2={right} y2={y(maximumGap * tick)} />
            <text x={x(maximumCost * tick)} y={bottom + 24} textAnchor="middle">{number(maximumCost * tick)}</text>
            <text x={left - 12} y={y(maximumGap * tick) + 4} textAnchor="end">{number(maximumGap * tick)}</text>
          </g>
        ))}
        <text className="policy-plot__axis" x={(left + right) / 2} y={height - 18} textAnchor="middle">
          Normalized expected error cost · lower is better
        </text>
        <text className="policy-plot__axis" transform={`translate(20 ${(top + bottom) / 2}) rotate(-90)`} textAnchor="middle">
          Equalized-odds gap · lower is better
        </text>
        {scenario.map((cell) => {
          const cost = cell.metrics.expected_cost;
          const gap = cell.metrics.equalized_odds_difference;
          const cx = x(cost.mean);
          const cy = y(gap.mean);
          const active = cell.policy === selectedPolicy;
          const className = `policy-mark policy-mark--${policyClass(cell.policy)} ${active ? "is-selected" : ""}`;
          return (
            <g key={cell.policy} className={className} aria-hidden="true">
              <line className="policy-whisker" x1={x(cost.replication_lower)} y1={cy} x2={x(cost.replication_upper)} y2={cy} />
              <line className="policy-whisker" x1={cx} y1={y(gap.replication_lower)} x2={cx} y2={y(gap.replication_upper)} />
              {cell.pareto_efficient ? (
                <polygon points={`${cx},${cy - 10} ${cx + 10},${cy} ${cx},${cy + 10} ${cx - 10},${cy}`} />
              ) : (
                <circle cx={cx} cy={cy} r="8" />
              )}
              <text x={cx + 12} y={cy - 10}>{policyNumber(cell.policy)}</text>
            </g>
          );
        })}
      </svg>
      <figcaption>
        Lower-left is preferable only for these two declared measurements. It does not settle
        validity, rights, downstream harm, or which errors a real institution should value.
      </figcaption>
    </figure>
  );
}

export default function PolicyStudio() {
  const [shift, setShift] = useState<ShiftKind>("covariate");
  const [falseNegativeCost, setFalseNegativeCost] = useState(1);
  const [selectedPolicy, setSelectedPolicy] = useState("baseline");

  const scenario = useMemo(
    () => cells.filter(
      (cell) => cell.shift === shift && cell.false_negative_cost === falseNegativeCost,
    ),
    [shift, falseNegativeCost],
  );
  const selected = scenario.find((cell) => cell.policy === selectedPolicy) ?? scenario[0];
  const definition = policies.find((policy) => policy.key === selected.policy) ?? policies[0];

  function exportScenario() {
    const payload = {
      schema_version: "1.1-policy-scenario",
      provenance: {
        project: "Fairshift Lab",
        release: "v1.1.0",
        registry: "reports/v1.1-policy-study.json",
        seeds: "100-119",
        replications: selected.replications,
      },
      declaration: {
        shift,
        magnitude: selected.magnitude,
        false_positive_cost: selected.false_positive_cost,
        false_negative_cost: selected.false_negative_cost,
      },
      policy: {
        key: selected.policy,
        label: definition.label,
        data_access: definition.access,
        selection_rule: definition.selection,
        pareto_efficient_within_benchmark: selected.pareto_efficient,
        threshold_group_zero: selected.threshold_group_zero,
        threshold_group_one: selected.threshold_group_one,
      },
      metrics: selected.metrics,
      disclaimer: "Descriptive synthetic benchmark; not a recommendation, fairness certification, legal determination, or deployment approval.",
    };
    const blob = new Blob([`${JSON.stringify(payload, null, 2)}\n`], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `fairshift-policy-${shift}-fn-${falseNegativeCost}-${selected.policy}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  return (
    <section className="policy" id="policy" aria-labelledby="policy-heading">
      <header className="section-heading">
        <div><span className="section-index">04</span><p>Policy Studio</p></div>
        <h2 id="policy-heading">Declare the stakes.<br />See the trade-offs.</h2>
      </header>
      <p className="policy-intro">
        Eight decision policies are evaluated on the same independently sampled target tests.
        Choose an intervention and error-cost declaration; the studio exposes consequences but
        never chooses a policy for you.
      </p>

      <div className="policy-controls">
        <fieldset>
          <legend>Target intervention · magnitude 1.00</legend>
          {(Object.keys(shiftLabels) as ShiftKind[]).map((kind) => (
            <button type="button" key={kind} onClick={() => setShift(kind)} aria-pressed={shift === kind}>
              {shiftLabels[kind]}
            </button>
          ))}
        </fieldset>
        <fieldset>
          <legend>Cost of one false negative · false positive = 1</legend>
          {[0.5, 1, 2].map((cost) => (
            <button type="button" key={cost} onClick={() => setFalseNegativeCost(cost)} aria-pressed={falseNegativeCost === cost}>
              {cost}×
            </button>
          ))}
          <small>{costLabels[String(falseNegativeCost)]}</small>
        </fieldset>
      </div>

      <div className="policy-layout">
        <PolicyPlot scenario={scenario} selectedPolicy={selected.policy} />
        <aside className="policy-list" aria-label="Select a policy for detail">
          <span>Policy focus</span>
          {scenario.map((cell) => {
            const item = policies.find((policy) => policy.key === cell.policy);
            return (
              <button
                type="button"
                key={cell.policy}
                onClick={() => setSelectedPolicy(cell.policy)}
                aria-pressed={selected.policy === cell.policy}
              >
                <b>{policyNumber(cell.policy).toString().padStart(2, "0")}</b>
                <span>{item?.label}</span>
                <small>{cell.pareto_efficient ? "◇ efficient here" : "○ dominated here"}</small>
              </button>
            );
          })}
        </aside>
      </div>

      <article className="policy-detail" aria-live="polite" aria-atomic="true">
        <header>
          <div><span>Selected policy</span><h3>{definition.label}</h3></div>
          <p><strong>Data required:</strong> {definition.access}<br />{definition.selection}</p>
        </header>
        <div className="policy-metrics">
          <div><span>Normalized cost</span><strong>{number(selected.metrics.expected_cost.mean)}</strong><small>{number(selected.metrics.expected_cost.replication_lower)}–{number(selected.metrics.expected_cost.replication_upper)}</small></div>
          <div><span>Equalized-odds gap</span><strong>{number(selected.metrics.equalized_odds_difference.mean)}</strong><small>{number(selected.metrics.equalized_odds_difference.replication_lower)}–{number(selected.metrics.equalized_odds_difference.replication_upper)}</small></div>
          <div><span>Accuracy</span><strong>{number(selected.metrics.accuracy.mean)}</strong><small>{number(selected.metrics.accuracy.replication_lower)}–{number(selected.metrics.accuracy.replication_upper)}</small></div>
          <div><span>Mean thresholds · A=0 / A=1</span><strong>{number(selected.threshold_group_zero.mean)} / {number(selected.threshold_group_one.mean)}</strong><small>selected before target testing</small></div>
        </div>
        <div className="policy-verdict">
          <p><strong>{selected.pareto_efficient ? "Efficient within this comparison." : "Dominated within this comparison."}</strong> This status uses mean cost and mean equalized-odds gap only. It is not a recommendation.</p>
          <button className="button button--primary" type="button" onClick={exportScenario}>Export this scenario</button>
        </div>
      </article>

      <details className="data-alternative policy-data">
        <summary>Read the complete policy comparison</summary>
        {/* Keyboard focus makes the overflowing data region independently scrollable. */}
        {/* eslint-disable-next-line jsx-a11y/no-noninteractive-tabindex */}
        <div className="table-scroll" role="region" tabIndex={0} aria-label="Scrollable policy comparison data table">
          <table>
            <caption>{shiftLabels[shift]} at magnitude 1.00 with false-negative cost {falseNegativeCost}</caption>
            <thead><tr><th scope="col">Policy</th><th scope="col">Data access</th><th scope="col">Cost mean (range)</th><th scope="col">Equalized-odds mean (range)</th><th scope="col">Accuracy mean</th><th scope="col">Status</th></tr></thead>
            <tbody>{scenario.map((cell) => {
              const item = policies.find((policy) => policy.key === cell.policy);
              return <tr key={cell.policy}><th scope="row">{item?.label}</th><td>{item?.access}</td><td>{number(cell.metrics.expected_cost.mean)} ({number(cell.metrics.expected_cost.replication_lower)}–{number(cell.metrics.expected_cost.replication_upper)})</td><td>{number(cell.metrics.equalized_odds_difference.mean)} ({number(cell.metrics.equalized_odds_difference.replication_lower)}–{number(cell.metrics.equalized_odds_difference.replication_upper)})</td><td>{number(cell.metrics.accuracy.mean)}</td><td>{cell.pareto_efficient ? "Efficient here" : "Dominated here"}</td></tr>;
            })}</tbody>
          </table>
        </div>
      </details>

      <div className="policy-boundary">
        <p><strong>Target recalibration is an oracle-like adaptation benchmark.</strong> It uses a recent, representative, independently labeled target sample. Without that access, its result is unavailable—not a deployable promise.</p>
        <p><strong>Group thresholds use protected attributes at decision time.</strong> Their legality, legitimacy, construct validity, and impact depend on context that this synthetic laboratory cannot supply.</p>
      </div>
      <div className="report-actions">
        <a className="button button--ghost" href="https://github.com/lindgreendavid/fairshift-lab/blob/main/docs/policy-study-report.md">Read the policy report</a>
        <a className="button button--ghost" href="https://github.com/lindgreendavid/fairshift-lab/blob/main/reports/v1.1-policy-study.json">Inspect the frozen registry</a>
      </div>
    </section>
  );
}
