"use client";

import { useMemo, useState } from "react";

import registry from "../../reports/v1.3-robustness-study.json";

type Estimate = {
  mean: number;
  standard_deviation: number;
  replication_lower: number;
  replication_upper: number;
};

type OptionalEstimate = {
  mean: number | null;
  standard_deviation: number | null;
  replication_lower: number | null;
  replication_upper: number | null;
  defined_replications: number;
  total_replications: number;
};

type ConditionalRates = Record<string, Record<string, OptionalEstimate>>;

type Cell = {
  stressor: string;
  magnitude: number;
  model_family: string;
  false_negative_cost: number;
  replications: number;
  train_tuning_samples: number;
  test_samples: number;
  threshold: Estimate;
  stress_diagnostic: OptionalEstimate;
  estimates: Record<string, Estimate>;
  estimates_true_group: Record<string, Estimate>;
  conditional_rates: ConditionalRates;
};

const cells = registry.cells as Cell[];
const magnitudes = registry.magnitudes as number[];
const stressors = registry.stressors as string[];
const modelFamilies = registry.model_families as string[];

type MetricKey =
  | "accuracy"
  | "equalized_odds_difference"
  | "brier_score"
  | "expected_calibration_error";

const metricLabels: Record<MetricKey, string> = {
  accuracy: "Accuracy",
  equalized_odds_difference: "Equalized-odds gap (observed grouping)",
  brier_score: "Brier score",
  expected_calibration_error: "Expected calibration error",
};

const modelCopy: Record<string, { label: string; shape: "square" | "triangle" }> = {
  logistic_regression: { label: "Logistic regression", shape: "square" },
  shallow_decision_tree: { label: "Shallow decision tree", shape: "triangle" },
};

const stressorCopy: Record<
  string,
  { label: string; short: string; mechanism: string; tests: string }
> = {
  symmetric_label_noise: {
    label: "Symmetric label noise",
    short: "Flip training/tuning labels at random, independent of group.",
    mechanism: "Flip probability rises to 35% of training and tuning labels at magnitude 1.00.",
    tests: "v1.0: a fixed baseline model yields a stable, reproducible source measurement.",
  },
  group_conditional_label_noise: {
    label: "Group-conditional label noise",
    short: "Flip training/tuning labels more often for one group than the other.",
    mechanism:
      "Group A=0 stays near a 5% flip rate; group A=1 rises to 45% at magnitude 1.00.",
    tests:
      "v1.0/v1.1: observed group-fairness gaps reflect the declared mechanism, not annotation artifacts.",
  },
  protected_field_measurement_error: {
    label: "Protected-field measurement error",
    short: "Flip the recorded protected attribute on every split, including test.",
    mechanism: "Flip probability rises to 35% of the recorded sensitive field at magnitude 1.00.",
    tests:
      "v1.1/v1.2: group thresholds and audits computed from the protected attribute measure the true group disparity.",
  },
  unobserved_subgroup: {
    label: "Unobserved intersectional subgroup",
    short: "One never-modeled intersectional subgroup receives a worse true outcome.",
    mechanism: "The subgroup's logit penalty rises to 1.5 at magnitude 1.00.",
    tests:
      "v1.0-v1.2: two-group demographic-parity and equal-opportunity differences fully characterize group-conditional behavior.",
  },
  sample_size_stress: {
    label: "Sample-size stress",
    short: "Every split — training, tuning, adaptation, and test — shrinks together.",
    mechanism: "Every split shrinks from 2,000 records at magnitude 0.00 to 60 at magnitude 1.00.",
    tests: "v1.0/v1.1: descriptive replication ranges are narrow and every subgroup rate is defined.",
  },
  structural_misspecification: {
    label: "Structural misspecification",
    short: "The true label mechanism gains an interaction the models never see as a feature.",
    mechanism: "The feature-one × protected-attribute interaction coefficient rises to 1.5.",
    tests: "v1.0: a single inspectable model family is representative of \"the\" model's robustness.",
  },
};

function format(value: number) {
  return value.toFixed(3);
}

function formatOptional(value: number | null) {
  return value === null ? "undefined" : value.toFixed(3);
}

function chartPoints(points: { x: number; y: number }[]) {
  return points.map((point) => `${point.x.toFixed(3)},${point.y.toFixed(3)}`).join(" ");
}

function RobustnessPlot({
  stressor,
  metric,
}: {
  stressor: string;
  metric: MetricKey;
}) {
  const width = 760;
  const height = 400;
  const left = 88;
  const right = 718;
  const top = 32;
  const bottom = 320;

  const series = modelFamilies.map((family) => ({
    family,
    points: magnitudes.map((magnitude) => {
      const cell = cells.find(
        (candidate) =>
          candidate.stressor === stressor &&
          candidate.magnitude === magnitude &&
          candidate.model_family === family,
      );
      return { magnitude, estimate: cell?.estimates[metric] };
    }),
  }));

  const allValues = series.flatMap((entry) =>
    entry.points.flatMap((point) =>
      point.estimate
        ? [point.estimate.replication_lower, point.estimate.replication_upper]
        : [],
    ),
  );
  const maximumValue = Math.max(0.05, ...allValues) * 1.1;
  const x = (magnitude: number) => left + (magnitude) * (right - left);
  const y = (value: number) => bottom - (value / maximumValue) * (bottom - top);
  const ticks = [0, 0.25, 0.5, 0.75, 1];

  return (
    <figure className="robustness-plot">
      <div className="robustness-plot__heading">
        <div>
          <span>Both model families · same stress</span>
          <strong>{metricLabels[metric]} across magnitude</strong>
        </div>
        <div className="robustness-shape-key" aria-hidden="true">
          <span>
            <i className="shape-square" /> Logistic regression
          </span>
          <span>
            <i className="shape-triangle" /> Shallow decision tree
          </span>
        </div>
      </div>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-labelledby="robustness-plot-title robustness-plot-description"
      >
        <title id="robustness-plot-title">{`${metricLabels[metric]} under ${stressorCopy[stressor]?.label ?? stressor}`}</title>
        <desc id="robustness-plot-description">
          Two inspectable model families, fit and thresholded identically, compared across five
          preregistered stress magnitudes for one stressor. Whiskers show the empirical 2.5th to
          97.5th percentile replication range across seeded replications. The complete values
          follow in a table.
        </desc>
        <rect
          className="robustness-plot__frame"
          x={left}
          y={top}
          width={right - left}
          height={bottom - top}
        />
        {ticks.map((tick) => (
          <g key={`grid-${tick}`} aria-hidden="true">
            <line
              className="robustness-plot__grid"
              x1={x(tick)}
              y1={top}
              x2={x(tick)}
              y2={bottom}
            />
            <line
              className="robustness-plot__grid"
              x1={left}
              y1={y(maximumValue * tick)}
              x2={right}
              y2={y(maximumValue * tick)}
            />
            <text x={x(tick)} y={bottom + 22} textAnchor="middle">
              {tick.toFixed(2)}
            </text>
            <text x={left - 12} y={y(maximumValue * tick) + 4} textAnchor="end">
              {format(maximumValue * tick)}
            </text>
          </g>
        ))}
        <text
          className="robustness-plot__axis"
          x={(left + right) / 2}
          y={height - 6}
          textAnchor="middle"
        >
          Stressor magnitude · 0.00 is the no-stress control
        </text>
        <text
          className="robustness-plot__axis"
          transform={`translate(22 ${(top + bottom) / 2}) rotate(-90)`}
          textAnchor="middle"
        >
          {metricLabels[metric]}
        </text>
        {series.map((entry) => {
          const defined = entry.points.filter(
            (point): point is { magnitude: number; estimate: Estimate } =>
              point.estimate !== undefined,
          );
          const linePoints = chartPoints(
            defined.map((point) => ({ x: x(point.magnitude), y: y(point.estimate.mean) })),
          );
          return (
            <g
              key={entry.family}
              className={`robustness-mark robustness-mark--${entry.family}`}
              aria-hidden="true"
            >
              <polyline className="robustness-line" points={linePoints} />
              {defined.map((point) => {
                const cx = x(point.magnitude);
                const cy = y(point.estimate.mean);
                return (
                  <g key={point.magnitude}>
                    <line
                      className="robustness-whisker"
                      x1={cx}
                      y1={y(point.estimate.replication_lower)}
                      x2={cx}
                      y2={y(point.estimate.replication_upper)}
                    />
                    {modelCopy[entry.family]?.shape === "triangle" ? (
                      <polygon points={`${cx},${cy - 9} ${cx + 9},${cy + 7} ${cx - 9},${cy + 7}`} />
                    ) : (
                      <rect x={cx - 7} y={cy - 7} width="14" height="14" />
                    )}
                  </g>
                );
              })}
            </g>
          );
        })}
      </svg>
      <figcaption>
        Neither shape marks a winner. A model family that degrades less on one metric can
        degrade more on another; both are reported at every magnitude.
      </figcaption>
    </figure>
  );
}

export default function RobustnessLab() {
  const [stressor, setStressor] = useState("group_conditional_label_noise");
  const [metric, setMetric] = useState<MetricKey>("equalized_odds_difference");
  const [magnitude, setMagnitude] = useState(1);
  const [modelFamily, setModelFamily] = useState("logistic_regression");

  const focusCell = useMemo(
    () =>
      cells.find(
        (cell) =>
          cell.stressor === stressor &&
          cell.magnitude === magnitude &&
          cell.model_family === modelFamily,
      ),
    [stressor, magnitude, modelFamily],
  );
  const stressorRows = useMemo(
    () => cells.filter((cell) => cell.stressor === stressor).sort((a, b) => a.magnitude - b.magnitude || a.model_family.localeCompare(b.model_family)),
    [stressor],
  );

  const conditionalGroups = focusCell ? Object.entries(focusCell.conditional_rates) : [];
  const totalUndefinedRates = conditionalGroups.reduce(
    (total, [, rates]) =>
      total +
      Object.values(rates).filter((estimate) => estimate.defined_replications === 0).length,
    0,
  );
  const partiallyDefinedRates = conditionalGroups.reduce(
    (total, [, rates]) =>
      total +
      Object.values(rates).filter(
        (estimate) =>
          estimate.defined_replications > 0 &&
          estimate.defined_replications < estimate.total_replications,
      ).length,
    0,
  );

  return (
    <section className="robustness" id="robustness" aria-labelledby="robustness-heading">
      <header className="section-heading">
        <div>
          <span className="section-index">06</span>
          <p>Robustness Lab</p>
        </div>
        <h2 id="robustness-heading">
          Break the assumptions.
          <br />
          <em>See what still holds.</em>
        </h2>
      </header>

      <div className="robustness-boundary">
        <strong>Synthetic stress-test boundary</strong>
        <p>
          Every value on this page comes from the preregistered v1.3 specification-stress
          protocol on entirely synthetic populations. It is visually and analytically separate
          from both the base synthetic experiments above and the governed UCI Adult external
          evidence: it must never share an unlabeled chart, table, or scale with either. No
          protected attribute, label, or subgroup here describes a real person or community.
        </p>
        <a href="https://github.com/lindgreendavid/fairshift-lab/blob/main/docs/robustness-protocol.md">
          Read the preregistered protocol ↗
        </a>
      </div>

      <div className="robustness-controls">
        <fieldset>
          <legend>Stressor</legend>
          <div className="robustness-stressor-grid">
            {stressors.map((key) => (
              <button
                type="button"
                key={key}
                onClick={() => setStressor(key)}
                aria-pressed={stressor === key}
              >
                <span>{stressorCopy[key]?.label ?? key}</span>
                <small>{stressorCopy[key]?.short}</small>
              </button>
            ))}
          </div>
        </fieldset>
      </div>

      <div className="robustness-subcontrols">
        <fieldset>
          <legend>Metric</legend>
          {(Object.keys(metricLabels) as MetricKey[]).map((key) => (
            <button
              type="button"
              key={key}
              onClick={() => setMetric(key)}
              aria-pressed={metric === key}
            >
              {metricLabels[key]}
            </button>
          ))}
        </fieldset>
        <fieldset>
          <legend>Magnitude for the table and undefined-rate summary below</legend>
          {magnitudes.map((value) => (
            <button
              type="button"
              key={value}
              onClick={() => setMagnitude(value)}
              aria-pressed={magnitude === value}
            >
              {value.toFixed(2)}
            </button>
          ))}
        </fieldset>
        <fieldset>
          <legend>Model family for the undefined-rate summary below</legend>
          {modelFamilies.map((key) => (
            <button
              type="button"
              key={key}
              onClick={() => setModelFamily(key)}
              aria-pressed={modelFamily === key}
            >
              {modelCopy[key]?.label ?? key}
            </button>
          ))}
        </fieldset>
      </div>

      <div className="robustness-reading" aria-live="polite">
        <h3>Uncertainty and limitations come before the ranking</h3>
        <p>
          {stressorCopy[stressor]?.mechanism} At the selected magnitude and model family,{" "}
          {focusCell ? focusCell.replications : "—"} seeded replications defined{" "}
          {conditionalGroups.length * 3 - totalUndefinedRates - partiallyDefinedRates} of{" "}
          {conditionalGroups.length * 3} disaggregated rates in every replication,{" "}
          {partiallyDefinedRates} were defined in only some replications, and{" "}
          {totalUndefinedRates} were undefined in every replication (an empty group, label, or
          subgroup cell — not a rate of zero). This tests: {stressorCopy[stressor]?.tests}
        </p>
      </div>

      <RobustnessPlot stressor={stressor} metric={metric} />

      {focusCell && (
        <div className="robustness-summary">
          <article>
            <span>Train/tuning · test samples</span>
            <strong>
              {focusCell.train_tuning_samples.toLocaleString()} ·{" "}
              {focusCell.test_samples.toLocaleString()}
            </strong>
            <small>Disjoint seeds; test is evaluated once per replication.</small>
          </article>
          <article>
            <span>Realized stress diagnostic</span>
            <strong>{formatOptional(focusCell.stress_diagnostic.mean)}</strong>
            <small>
              Measured on the adaptation split, never used for fitting or thresholding.
            </small>
          </article>
          <article>
            <span>Selected global threshold</span>
            <strong>{format(focusCell.threshold.mean)}</strong>
            <small>
              Range {format(focusCell.threshold.replication_lower)}–
              {format(focusCell.threshold.replication_upper)}
            </small>
          </article>
          <article className="robustness-summary__warning">
            <span>Observed vs. true grouping</span>
            <strong>
              {format(focusCell.estimates.equalized_odds_difference.mean)} vs.{" "}
              {format(focusCell.estimates_true_group.equalized_odds_difference.mean)}
            </strong>
            <small>Equalized-odds gap by recorded vs. ground-truth protected attribute.</small>
          </article>
        </div>
      )}

      {/* Keyboard focus makes the overflowing data region independently scrollable. */}
      {/* eslint-disable-next-line jsx-a11y/no-noninteractive-tabindex */}
      <div className="table-scroll" role="region" tabIndex={0} aria-label="Complete robustness stress results for the selected stressor">
        <table>
          <caption>
            {stressorCopy[stressor]?.label ?? stressor}: every magnitude and model family
          </caption>
          <thead>
            <tr>
              <th scope="col">Magnitude</th>
              <th scope="col">Model family</th>
              <th scope="col">Accuracy</th>
              <th scope="col">Normalized cost</th>
              <th scope="col">DP gap</th>
              <th scope="col">EO gap</th>
              <th scope="col">EOdds gap</th>
              <th scope="col">Brier</th>
              <th scope="col">ECE</th>
              <th scope="col">Stress diagnostic</th>
            </tr>
          </thead>
          <tbody>
            {stressorRows.map((cell) => (
              <tr key={`${cell.magnitude}-${cell.model_family}`}>
                <th scope="row">{cell.magnitude.toFixed(2)}</th>
                <td>{modelCopy[cell.model_family]?.label ?? cell.model_family}</td>
                <td>{format(cell.estimates.accuracy.mean)}</td>
                <td>{format(cell.estimates.expected_cost.mean)}</td>
                <td>{format(cell.estimates.demographic_parity_difference.mean)}</td>
                <td>{format(cell.estimates.equal_opportunity_difference.mean)}</td>
                <td>{format(cell.estimates.equalized_odds_difference.mean)}</td>
                <td>{format(cell.estimates.brier_score.mean)}</td>
                <td>{format(cell.estimates.expected_calibration_error.mean)}</td>
                <td>{formatOptional(cell.stress_diagnostic.mean)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <details className="data-alternative robustness-data">
        <summary>Read disaggregated group and subgroup rates for the selected cell</summary>
        {focusCell && (
          // eslint-disable-next-line jsx-a11y/no-noninteractive-tabindex
          <div className="table-scroll" role="region" tabIndex={0} aria-label="Group and subgroup conditional rates with undefined-replication counts">
            <table>
              <caption>
                {stressorCopy[stressor]?.label ?? stressor} at magnitude{" "}
                {magnitude.toFixed(2)}, {modelCopy[modelFamily]?.label ?? modelFamily}
              </caption>
              <thead>
                <tr>
                  <th scope="col">Group</th>
                  <th scope="col">Selection rate</th>
                  <th scope="col">True-positive rate</th>
                  <th scope="col">False-positive rate</th>
                  <th scope="col">Defined replications</th>
                </tr>
              </thead>
              <tbody>
                {conditionalGroups.map(([groupName, rates]) => (
                  <tr key={groupName}>
                    <th scope="row">{groupName.replace(/_/g, " ")}</th>
                    <td>{formatOptional(rates.selection_rate.mean)}</td>
                    <td>{formatOptional(rates.true_positive_rate.mean)}</td>
                    <td>{formatOptional(rates.false_positive_rate.mean)}</td>
                    <td>
                      {rates.selection_rate.defined_replications}/
                      {rates.selection_rate.total_replications} ·{" "}
                      {rates.true_positive_rate.defined_replications}/
                      {rates.true_positive_rate.total_replications} ·{" "}
                      {rates.false_positive_rate.defined_replications}/
                      {rates.false_positive_rate.total_replications}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </details>

      <div className="robustness-boundary robustness-boundary--footnote">
        <p>
          A <code>null</code>/&quot;undefined&quot; rate above means zero replications had any
          record in that group-label cell at this magnitude and model family — not that the
          rate is zero. This is this module&apos;s own explicit missing-value convention; it
          does not change how earlier releases report zero-denominator rates as{" "}
          <code>0.0</code>.
        </p>
      </div>

      <div className="robustness-links">
        <a href="https://github.com/lindgreendavid/fairshift-lab/blob/main/docs/robustness-protocol.md">
          Preregistered protocol ↗
        </a>
        <a href="https://github.com/lindgreendavid/fairshift-lab/blob/main/docs/robustness-report.md">
          Bounded report ↗
        </a>
        <a href="https://github.com/lindgreendavid/fairshift-lab/blob/main/reports/v1.3-robustness-study.json">
          Frozen registry ↗
        </a>
      </div>
    </section>
  );
}
