import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const root = new URL("../", import.meta.url);

async function source(name) {
  return readFile(new URL(name, root), "utf8");
}

function luminance(hex) {
  const channels = hex.match(/[0-9a-f]{2}/gi).map((value) => Number.parseInt(value, 16) / 255);
  const linear = channels.map((value) =>
    value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4,
  );
  return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2];
}

function contrast(first, second) {
  const values = [luminance(first), luminance(second)].sort((a, b) => b - a);
  return (values[0] + 0.05) / (values[1] + 0.05);
}

test("keeps the WCAG 2.2-oriented keyboard and structure contract", async () => {
  const [page, styles, layout] = await Promise.all([
    source("app/page.tsx"),
    source("app/globals.css"),
    source("app/layout.tsx"),
  ]);
  assert.match(layout, /<html lang="en">/);
  assert.match(page, /href="#main-content">Skip to main content/);
  assert.match(page, /<main id="main-content">/);
  assert.match(page, /<nav className="nav" aria-label="Primary navigation">/);
  for (const id of ["magnitude", "threshold", "samples"]) {
    assert.match(page, new RegExp(`htmlFor="${id}"`));
    assert.match(page, new RegExp(`id="${id}"`));
  }
  assert.match(page, /<legend className="sr-only">Distribution shift mechanism<\/legend>/);
  assert.match(page, /aria-pressed=/);
  assert.match(page, /aria-live="polite"/);
  assert.match(styles, /:focus-visible \{ outline: 3px solid/);
  assert.match(styles, /\.nav__links a \{ display: inline-flex; min-height: 44px/);
  assert.doesNotMatch(styles, /nav__links a:not\(:last-child\).*display: none/);
});

test("keeps equivalent text and data for every scientific visual", async () => {
  const [page, styles] = await Promise.all([
    source("app/page.tsx"),
    source("app/globals.css"),
  ]);
  assert.match(page, /role="img" aria-label=\{`Feature X1 histogram/);
  assert.equal((page.match(/<title id=/g) ?? []).length, 2);
  assert.match(page, /<title id="threshold-title">\{`\$\{metricCopy\[metric\]\.label\} threshold sensitivity`\}<\/title>/);
  assert.equal((page.match(/<desc id=/g) ?? []).length, 2);
  assert.equal((page.match(/<caption>/g) ?? []).length, 2);
  assert.match(page, /Read reliability data/);
  assert.match(page, /Read threshold data/);
  assert.match(styles, /chart-line--raw[^}]*stroke-dasharray/);
  assert.match(styles, /chart-line--target[^}]*stroke-dasharray/);
});

test("keeps reflow, contrast preference, forced colors, and reduced motion", async () => {
  const styles = await source("app/globals.css");
  assert.match(styles, /@media \(max-width: 720px\)/);
  assert.match(styles, /@media \(prefers-reduced-motion: reduce\)/);
  assert.match(styles, /@media \(prefers-contrast: more\)/);
  assert.match(styles, /@media \(forced-colors: active\)/);
  assert.match(styles, /\.nav__links \{ max-width: calc\(100vw - 82px\); overflow-x: auto/);
});

test("keeps normal-text palette combinations above WCAG AA contrast", async () => {
  const styles = await source("app/globals.css");
  const colors = Object.fromEntries(
    [...styles.matchAll(/--([a-z]+): (#[0-9a-f]{6})/gi)].map((match) => [match[1], match[2]]),
  );
  for (const [foreground, background] of [
    ["ink", "paper"],
    ["muted", "paper"],
    ["muted", "white"],
    ["ink", "coral"],
    ["blue", "paper"],
  ]) {
    assert.ok(
      contrast(colors[foreground], colors[background]) >= 4.5,
      `${foreground} on ${background} must meet 4.5:1`,
    );
  }
});

test("ships recovery pages with direct, keyboard-operable actions", async () => {
  const [errorPage, notFound] = await Promise.all([
    source("app/error.tsx"),
    source("app/not-found.tsx"),
  ]);
  assert.match(errorPage, /type="button" onClick=\{reset\}>Try again/);
  assert.match(errorPage, /Return to the laboratory/);
  assert.match(notFound, /Return to Fairshift Lab/);
});

test("keeps the Policy Studio operable and equivalent beyond the plot", async () => {
  const [studio, styles] = await Promise.all([
    source("app/policy-studio.tsx"),
    source("app/globals.css"),
  ]);
  assert.match(studio, /<section className="policy" id="policy" aria-labelledby="policy-heading">/);
  assert.match(studio, /aria-labelledby="policy-plot-title policy-plot-description"/);
  assert.match(studio, /Diamonds[\s\S]*Pareto-efficient/);
  assert.match(studio, /aria-label="Select a policy for detail"/);
  assert.match(studio, /aria-pressed=/);
  assert.match(studio, /aria-live="polite"/);
  assert.match(studio, /<caption>/);
  assert.match(studio, /Scrollable policy comparison data table/);
  assert.match(studio, /Export this scenario/);
  assert.match(studio, /not a recommendation/);
  assert.match(styles, /\.shape-diamond/);
  assert.match(styles, /\.shape-circle/);
  assert.match(styles, /\.policy-controls button \{ min-height: 48px/);
});

test("keeps the Robustness Lab uncertainty-first, non-color-coded, and boundary-separated", async () => {
  const [lab, styles, page] = await Promise.all([
    source("app/robustness-lab.tsx"),
    source("app/globals.css"),
    source("app/page.tsx"),
  ]);
  assert.match(page, /<RobustnessLab \/>/);
  assert.match(lab, /<section className="robustness" id="robustness" aria-labelledby="robustness-heading">/);
  assert.match(lab, /Synthetic stress-test boundary/);
  assert.match(lab, /visually and analytically separate/);
  assert.match(lab, /Uncertainty and limitations come before the ranking/);
  const uncertaintyIndex = lab.indexOf("Uncertainty and limitations come before the ranking");
  const plotIndex = lab.indexOf("<RobustnessPlot");
  assert.ok(uncertaintyIndex > 0 && plotIndex > uncertaintyIndex, "uncertainty reading must precede the plot");
  assert.match(lab, /aria-labelledby="robustness-plot-title robustness-plot-description"/);
  assert.match(lab, /aria-pressed=/);
  assert.match(lab, /aria-live="polite"/);
  assert.match(lab, /<caption>/);
  assert.match(lab, /undefined-replication counts/);
  assert.match(lab, /formatOptional/);
  assert.match(styles, /\.shape-square/);
  assert.match(styles, /\.shape-triangle/);
  assert.match(styles, /\.robustness-mark--shallow_decision_tree \.robustness-line \{ stroke-dasharray/);
});
