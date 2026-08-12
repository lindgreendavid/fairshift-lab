"use client";

import { useMemo, useState } from "react";

type ShiftKind = "covariate" | "concept" | "prevalence";
type MetricKey = "accuracy" | "auc" | "dp" | "eo" | "eodds";

type Observation = {
  x1: number;
  x2: number;
  group: 0 | 1;
  label: 0 | 1;
  score: number;
};

type Rates = {
  selection: number;
  tpr: number;
  fpr: number;
};

type Metrics = {
  accuracy: number;
  auc: number;
  dp: number;
  eo: number;
  eodds: number;
  group0: Rates;
  group1: Rates;
};

type Interval = { lower: number; upper: number };

const shiftCopy: Record<
  ShiftKind,
  { label: string; short: string; mechanism: string; fixed: string }
> = {
  covariate: {
    label: "Covariate shift",
    short: "The people arriving look different to the model.",
    mechanism: "Feature distributions P(X) move",
    fixed: "The label equation P(Y|X,A) stays fixed",
  },
  concept: {
    label: "Concept shift",
    short: "The relationship between evidence and outcome changes.",
    mechanism: "The label equation P(Y|X,A) moves",
    fixed: "The realized features stay fixed",
  },
  prevalence: {
    label: "Group prevalence shift",
    short: "The population mix changes at deployment.",
    mechanism: "The protected-group probability P(A) moves",
    fixed: "The remaining structural equations stay fixed",
  },
};

const metricCopy: Record<
  MetricKey,
  { label: string; question: string; interpretation: string; caution: string }
> = {
  accuracy: {
    label: "Accuracy",
    question: "How often is the thresholded prediction correct?",
    interpretation: "Higher values indicate more correct classifications in this sample.",
    caution: "Aggregate accuracy can hide different error patterns between groups.",
  },
  auc: {
    label: "AUROC",
    question: "How well does the score rank positives above negatives?",
    interpretation: "0.5 is chance ranking; 1.0 is perfect ranking.",
    caution: "AUROC does not select a threshold and does not establish fairness.",
  },
  dp: {
    label: "Demographic parity gap",
    question: "Do groups receive positive predictions at different rates?",
    interpretation: "Zero means equal selection rates in this sample.",
    caution: "Parity may be inappropriate when relevant base rates differ; context is essential.",
  },
  eo: {
    label: "Equal opportunity gap",
    question: "Do qualified positives receive positive predictions at different rates?",
    interpretation: "Zero means equal true-positive rates in this sample.",
    caution: "The metric inherits every limitation of the observed label as a proxy for qualification.",
  },
  eodds: {
    label: "Equalized odds gap",
    question: "Are both true- and false-positive rates aligned across groups?",
    interpretation: "The displayed value is the larger of the two absolute rate gaps.",
    caution: "A single maximum gap hides which error type and group drive the result.",
  },
};

function mulberry32(seed: number) {
  let state = seed >>> 0;
  return () => {
    state += 0x6d2b79f5;
    let value = state;
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}

function normal(random: () => number) {
  const u = Math.max(random(), Number.EPSILON);
  const v = random();
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}

function sigmoid(value: number) {
  return 1 / (1 + Math.exp(-Math.max(-35, Math.min(35, value))));
}

function generatePopulation(
  samples: number,
  seed: number,
  shift: ShiftKind | "none",
  magnitude: number,
) {
  const random = mulberry32(seed);
  const observations: Omit<Observation, "score">[] = [];
  const groupProbability = shift === "prevalence" ? 0.5 + 0.4 * magnitude : 0.5;

  for (let index = 0; index < samples; index += 1) {
    const group = (random() < groupProbability ? 1 : 0) as 0 | 1;
    let x1 = normal(random) + 0.35 * group;
    let x2 = normal(random);
    if (shift === "covariate") {
      x1 += magnitude * (0.5 + group);
      x2 -= 0.75 * magnitude;
    }
    let coefficient = 1.1;
    let groupEffect = -0.45;
    if (shift === "concept") {
      coefficient -= 1.8 * magnitude;
      groupEffect += 1.2 * magnitude;
    }
    const probability = sigmoid(-0.15 + coefficient * x1 - 0.7 * x2 + groupEffect * group);
    const label = (random() < probability ? 1 : 0) as 0 | 1;
    observations.push({ x1, x2, group, label });
  }
  return observations;
}

function fitLogistic(source: Omit<Observation, "score">[]) {
  const weights = [0, 0, 0, 0];
  const learningRate = 0.2;
  for (let iteration = 0; iteration < 500; iteration += 1) {
    const gradient = [0, 0, 0, 0];
    for (const row of source) {
      const score = sigmoid(
        weights[0] + weights[1] * row.x1 + weights[2] * row.x2 + weights[3] * row.group,
      );
      const error = score - row.label;
      gradient[0] += error;
      gradient[1] += error * row.x1;
      gradient[2] += error * row.x2;
      gradient[3] += error * row.group;
    }
    for (let weight = 0; weight < weights.length; weight += 1) {
      weights[weight] -= (learningRate * gradient[weight]) / source.length;
    }
  }
  return weights;
}

function scorePopulation(
  population: Omit<Observation, "score">[],
  weights: number[],
): Observation[] {
  return population.map((row) => ({
    ...row,
    score: sigmoid(
      weights[0] + weights[1] * row.x1 + weights[2] * row.x2 + weights[3] * row.group,
    ),
  }));
}

function rates(rows: Observation[], threshold: number, group: 0 | 1): Rates {
  const selected = rows.filter((row) => row.group === group);
  const positives = selected.filter((row) => row.label === 1);
  const negatives = selected.filter((row) => row.label === 0);
  const positivePredictions = (items: Observation[]) =>
    items.filter((row) => row.score >= threshold).length;
  return {
    selection: selected.length ? positivePredictions(selected) / selected.length : 0,
    tpr: positives.length ? positivePredictions(positives) / positives.length : 0,
    fpr: negatives.length ? positivePredictions(negatives) / negatives.length : 0,
  };
}

function auc(rows: Observation[]) {
  const positives = rows.filter((row) => row.label === 1).map((row) => row.score);
  const negatives = rows.filter((row) => row.label === 0).map((row) => row.score);
  if (!positives.length || !negatives.length) return 0.5;
  let wins = 0;
  for (const positive of positives) {
    for (const negative of negatives) {
      wins += positive > negative ? 1 : positive === negative ? 0.5 : 0;
    }
  }
  return wins / (positives.length * negatives.length);
}

function evaluate(rows: Observation[], threshold: number, includeAuc = true): Metrics {
  const group0 = rates(rows, threshold, 0);
  const group1 = rates(rows, threshold, 1);
  const correct = rows.filter((row) => (row.score >= threshold ? 1 : 0) === row.label).length;
  const tprGap = Math.abs(group1.tpr - group0.tpr);
  const fprGap = Math.abs(group1.fpr - group0.fpr);
  return {
    accuracy: correct / rows.length,
    auc: includeAuc ? auc(rows) : 0,
    dp: Math.abs(group1.selection - group0.selection),
    eo: tprGap,
    eodds: Math.max(tprGap, fprGap),
    group0,
    group1,
  };
}

function bootstrap(rows: Observation[], threshold: number, seed: number) {
  const random = mulberry32(seed);
  const group0 = rows.filter((row) => row.group === 0);
  const group1 = rows.filter((row) => row.group === 1);
  const values: Record<Exclude<MetricKey, "auc">, number[]> = {
    accuracy: [],
    dp: [],
    eo: [],
    eodds: [],
  };
  for (let repeat = 0; repeat < 80; repeat += 1) {
    const resample = [...group0, ...group1].map((_, index) => {
      const group = index < group0.length ? group0 : group1;
      return group[Math.floor(random() * group.length)];
    });
    const metrics = evaluate(resample, threshold, false);
    for (const key of Object.keys(values) as (keyof typeof values)[]) values[key].push(metrics[key]);
  }
  return Object.fromEntries(
    Object.entries(values).map(([key, distribution]) => {
      const ordered = [...distribution].sort((a, b) => a - b);
      return [key, { lower: ordered[1], upper: ordered[78] }];
    }),
  ) as Record<Exclude<MetricKey, "auc">, Interval>;
}

function runExperiment(
  shift: ShiftKind,
  magnitude: number,
  threshold: number,
  samples: number,
  seed: number,
) {
  const rawSource = generatePopulation(samples, seed, "none", 0);
  const rawTarget = generatePopulation(samples, seed + 1, shift, magnitude);
  const weights = fitLogistic(rawSource);
  const source = scorePopulation(rawSource, weights);
  const target = scorePopulation(rawTarget, weights);
  return {
    source,
    target,
    sourceMetrics: evaluate(source, threshold),
    targetMetrics: evaluate(target, threshold),
    intervals: bootstrap(target, threshold, seed + 3),
  };
}

function format(value: number) {
  return value.toFixed(3);
}

function histogram(rows: Observation[]) {
  const bins = Array.from({ length: 14 }, () => 0);
  for (const row of rows) {
    const index = Math.max(0, Math.min(13, Math.floor(((row.x1 + 3) / 6) * 14)));
    bins[index] += 1;
  }
  const maximum = Math.max(...bins);
  return bins.map((count) => (maximum ? count / maximum : 0));
}

function MetricCard({
  metric,
  source,
  target,
  interval,
  selected,
  onSelect,
}: {
  metric: MetricKey;
  source: number;
  target: number;
  interval?: Interval;
  selected: boolean;
  onSelect: () => void;
}) {
  const difference = target - source;
  return (
    <button
      className={`metric-card ${selected ? "metric-card--selected" : ""}`}
      onClick={onSelect}
      aria-pressed={selected}
    >
      <span className="metric-card__label">{metricCopy[metric].label}</span>
      <span className="metric-card__value">{format(target)}</span>
      <span className={`metric-card__delta ${difference > 0 ? "is-up" : "is-down"}`}>
        {difference > 0 ? "+" : ""}{format(difference)} from source
      </span>
      {interval ? (
        <span className="metric-card__interval">
          95% bootstrap interval {format(interval.lower)}–{format(interval.upper)}
        </span>
      ) : (
        <span className="metric-card__interval">Ranking metric · no interval in v0.2</span>
      )}
    </button>
  );
}

export default function Home() {
  const [shift, setShift] = useState<ShiftKind>("covariate");
  const [magnitude, setMagnitude] = useState(0.45);
  const [threshold, setThreshold] = useState(0.5);
  const [samples, setSamples] = useState(600);
  const [seed, setSeed] = useState(42);
  const [selectedMetric, setSelectedMetric] = useState<MetricKey>("dp");

  const experiment = useMemo(
    () => runExperiment(shift, magnitude, threshold, samples, seed),
    [shift, magnitude, threshold, samples, seed],
  );
  const sourceHistogram = histogram(experiment.source);
  const targetHistogram = histogram(experiment.target);
  const groupShare = experiment.target.filter((row) => row.group === 1).length / samples;
  const selected = metricCopy[selectedMetric];

  return (
    <main>
      <nav className="nav" aria-label="Primary navigation">
        <a className="brand" href="#top" aria-label="Fairshift Lab home">
          <span className="brand__mark">F↗</span>
          <span>Fairshift Lab</span>
        </a>
        <div className="nav__links">
          <a href="#experiment">Experiment</a>
          <a href="#method">Method</a>
          <a href="#evidence">Evidence</a>
          <a href="https://github.com/lindgreendavid/fairshift-lab">GitHub</a>
        </div>
      </nav>

      <section className="hero" id="top">
        <div className="eyebrow"><span>Interactive research release</span><span>v0.2.0</span></div>
        <h1>Move the population.<br /><em>Watch fairness move.</em></h1>
        <p className="hero__lead">
          A model can keep the same code and still behave differently after deployment.
          Change one data-generating mechanism, then inspect performance, group gaps, and
          uncertainty together.
        </p>
        <div className="hero__actions">
          <a className="button button--primary" href="#experiment">Run the experiment</a>
          <a className="button button--ghost" href="#method">Read the protocol</a>
        </div>
        <div className="hero__principles" aria-label="Research principles">
          <span>One controlled intervention</span>
          <span>Reproducible seed</span>
          <span>Uncertainty visible</span>
          <span>Claims bounded</span>
        </div>
      </section>

      <section className="lab" id="experiment">
        <header className="section-heading">
          <div><span className="section-index">01</span><p>Shift microscope</p></div>
          <h2>Change the mechanism,<br />not the story.</h2>
        </header>

        <div className="scenario-tabs" role="group" aria-label="Distribution shift mechanism">
          {(Object.keys(shiftCopy) as ShiftKind[]).map((kind) => (
            <button
              key={kind}
              onClick={() => setShift(kind)}
              className={shift === kind ? "is-active" : ""}
              aria-pressed={shift === kind}
            >
              <span>{shiftCopy[kind].label}</span>
              <small>{shiftCopy[kind].short}</small>
            </button>
          ))}
        </div>

        <div className="lab-grid">
          <aside className="controls" aria-label="Experiment controls">
            <div className="control">
              <label htmlFor="magnitude"><span>Shift magnitude</span><output>{Math.round(magnitude * 100)}%</output></label>
              <input id="magnitude" type="range" min="0" max="1" step="0.05" value={magnitude} onChange={(event) => setMagnitude(Number(event.target.value))} />
              <div className="range-labels"><span>Source-like</span><span>Severe</span></div>
            </div>
            <div className="control">
              <label htmlFor="threshold"><span>Decision threshold</span><output>{threshold.toFixed(2)}</output></label>
              <input id="threshold" type="range" min="0.2" max="0.8" step="0.02" value={threshold} onChange={(event) => setThreshold(Number(event.target.value))} />
              <div className="range-labels"><span>More positives</span><span>Fewer positives</span></div>
            </div>
            <div className="control">
              <label htmlFor="samples"><span>Sample size</span><output>n = {samples}</output></label>
              <select id="samples" value={samples} onChange={(event) => setSamples(Number(event.target.value))}>
                <option value="300">300 · fast</option>
                <option value="600">600 · balanced</option>
                <option value="1000">1,000 · precise</option>
              </select>
            </div>
            <div className="seed-control">
              <div><span>Reproducible seed</span><strong>{seed}</strong></div>
              <button onClick={() => setSeed((current) => current + 17)}>New sample</button>
            </div>
            <div className="mechanism-note">
              <span>Intervention</span>
              <strong>{shiftCopy[shift].mechanism}</strong>
              <small>{shiftCopy[shift].fixed}</small>
            </div>
          </aside>

          <div className="observation-panel">
            <div className="panel-title">
              <div><span>Observed feature X₁</span><strong>Source → target</strong></div>
              <span className="live-chip"><i /> live simulation</span>
            </div>
            <div className="histogram" aria-label="Comparison of source and target feature distributions">
              {sourceHistogram.map((height, index) => (
                <div className="histogram__bin" key={index}>
                  <span className="bar bar--source" style={{ height: `${height * 86}%` }} />
                  <span className="bar bar--target" style={{ height: `${targetHistogram[index] * 86}%` }} />
                </div>
              ))}
            </div>
            <div className="legend"><span><i className="source-dot" />Source population</span><span><i className="target-dot" />Target population</span></div>
            <div className="population-stats">
              <div><span>Target Group B share</span><strong>{Math.round(groupShare * 100)}%</strong></div>
              <div><span>Threshold</span><strong>{threshold.toFixed(2)}</strong></div>
              <div><span>Independent target seed</span><strong>{seed + 1}</strong></div>
            </div>
          </div>
        </div>

        <div className="metrics-grid">
          {(["accuracy", "auc", "dp", "eo", "eodds"] as MetricKey[]).map((metric) => (
            <MetricCard
              key={metric}
              metric={metric}
              source={experiment.sourceMetrics[metric]}
              target={experiment.targetMetrics[metric]}
              interval={metric === "auc" ? undefined : experiment.intervals[metric]}
              selected={selectedMetric === metric}
              onSelect={() => setSelectedMetric(metric)}
            />
          ))}
        </div>

        <article className="metric-lens" aria-live="polite">
          <div><span className="section-index">Metric lens</span><h3>{selected.label}</h3></div>
          <div><span>Question</span><p>{selected.question}</p></div>
          <div><span>What this run supports</span><p>{selected.interpretation}</p></div>
          <div className="metric-lens__caution"><span>Do not overclaim</span><p>{selected.caution}</p></div>
        </article>
        <p className="uncertainty-note">
          Intervals use 80 group-stratified percentile-bootstrap resamples in the browser.
          They describe sampling variability only—not label validity, model selection, or future drift.
        </p>
      </section>

      <section className="method" id="method">
        <header className="section-heading section-heading--light">
          <div><span className="section-index">02</span><p>Scientific method</p></div>
          <h2>See exactly what<br />the experiment knows.</h2>
        </header>
        <div className="causal-chain" aria-label="Experimental causal chain">
          <div><span>1</span><strong>Generate</strong><p>Sample an explicit structural process.</p></div>
          <i>→</i>
          <div><span>2</span><strong>Train once</strong><p>Fit logistic regression on source data only.</p></div>
          <i>→</i>
          <div><span>3</span><strong>Intervene</strong><p>Change exactly one target mechanism.</p></div>
          <i>→</i>
          <div><span>4</span><strong>Audit</strong><p>Compare performance, gaps, and intervals.</p></div>
        </div>
        <div className="equation-card">
          <div><span>Source structural equation</span><code>P(Y=1) = σ(−0.15 + 1.1X₁ − 0.7X₂ − 0.45A)</code></div>
          <p>
            This equation is a transparent teaching mechanism—not a representation of any real
            demographic group. The protected attribute is synthetic and binary; intersectionality,
            institutions, measurement error, and lived context are outside this release.
          </p>
        </div>
        <div className="interpretation-ladder">
          <article><span>Observation</span><h3>The target gap changed.</h3><p>A numerical statement about this generated sample.</p></article>
          <article><span>Supported inference</span><h3>The intervention altered measured behavior.</h3><p>A reproducible statement inside the declared structural process.</p></article>
          <article><span>Unsupported leap</span><h3>“The model is fair in the real world.”</h3><p>Not established by synthetic data or a single statistical definition.</p></article>
        </div>
      </section>

      <section className="evidence" id="evidence">
        <header className="section-heading">
          <div><span className="section-index">03</span><p>Research trail</p></div>
          <h2>Built on arguments<br />you can inspect.</h2>
        </header>
        <div className="source-list">
          <a href="https://proceedings.neurips.cc/paper_files/paper/2016/hash/6a9659feb1216f14f7384ba499518b38-Abstract.html" target="_blank" rel="noreferrer">
            <span>NeurIPS · 2016</span><strong>Equality of Opportunity in Supervised Learning</strong><p>Hardt, Price & Srebro formalize equal opportunity and equalized odds.</p><b>↗</b>
          </a>
          <a href="https://arxiv.org/abs/2206.00129" target="_blank" rel="noreferrer">
            <span>FAccT · 2022</span><strong>Fairness Transferability Subject to Bounded Distribution Shift</strong><p>Chen et al. study when statistical fairness can transfer across shifted distributions.</p><b>↗</b>
          </a>
          <a href="https://proceedings.mlr.press/v238/barrainkua24a.html" target="_blank" rel="noreferrer">
            <span>AISTATS · 2024</span><strong>Uncertainty Matters</strong><p>Barrainkua et al. show why uncertainty-aware fairness comparisons matter.</p><b>↗</b>
          </a>
          <a href="https://proceedings.mlr.press/v267/agarwal25b.html" target="_blank" rel="noreferrer">
            <span>ICML · 2025</span><strong>Optimal Fair Learning Robust to Adversarial Distribution Shift</strong><p>Agarwal et al. analyze fairness-constrained learning under malicious distribution noise.</p><b>↗</b>
          </a>
          <a href="https://airc.nist.gov/airmf-resources/airmf/3-sec-characteristics/" target="_blank" rel="noreferrer">
            <span>NIST AI RMF · 1.0</span><strong>AI Risks and Trustworthiness</strong><p>Fairness belongs inside a broader socio-technical risk-management process.</p><b>↗</b>
          </a>
        </div>
      </section>

      <footer>
        <div><span className="brand__mark">F↗</span><strong>Fairshift Lab</strong></div>
        <p>Research software by David Lindgreen · MIT License · No personal data</p>
        <div><a href="https://github.com/lindgreendavid/fairshift-lab">Source code</a><a href="https://github.com/lindgreendavid/fairshift-lab/blob/main/docs/research-protocol.md">Protocol</a></div>
      </footer>
    </main>
  );
}
