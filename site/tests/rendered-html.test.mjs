import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import test from "node:test";

const root = new URL("../", import.meta.url);

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(
    new Request("http://localhost/", { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders the finished research laboratory", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /<title>Fairshift Lab/);
  assert.match(html, /Move the population/);
  assert.match(html, /Shift microscope/);
  assert.match(html, /Decision landscape/);
  assert.match(html, /Verified report/);
  assert.match(html, /Policy Studio/);
  assert.match(html, /Declare the stakes/);
  assert.match(html, /No automatic best policy/);
  assert.match(html, /Export this scenario/);
  assert.match(html, /One grid/);
  assert.match(html, /300 complete experiments/);
  assert.match(html, /Target reliability/);
  assert.match(html, /Threshold sensitivity/);
  assert.match(html, /Scientific method/);
  assert.match(html, /Research trail/);
  assert.match(html, /Run the experiment/);
  assert.match(html, /Skip to main content/);
  assert.match(html, /Read reliability data/);
  assert.match(html, /Read threshold data/);
  assert.match(html, /Accessibility/);
  assert.doesNotMatch(html, /codex-preview|react-loading-skeleton|Starter Project/);
});

test("ships accessible controls, research boundaries, and primary sources", async () => {
  const [page, layout, styles, packageJson] = await Promise.all([
    readFile(new URL("app/page.tsx", root), "utf8"),
    readFile(new URL("app/layout.tsx", root), "utf8"),
    readFile(new URL("app/globals.css", root), "utf8"),
    readFile(new URL("package.json", root), "utf8"),
  ]);
  assert.match(page, /aria-label="Experiment controls"/);
  assert.match(page, /htmlFor="magnitude"/);
  assert.match(page, /htmlFor="threshold"/);
  assert.match(page, /aria-live="polite"/);
  assert.match(page, /className="skip-link"/);
  assert.match(page, /<caption>Target reliability bins<\/caption>/);
  assert.match(page, /Scrollable threshold data table/);
  assert.match(page, /role="img" aria-label=\{`Feature X1 histogram/);
  assert.match(styles, /prefers-contrast: more/);
  assert.match(styles, /forced-colors: active/);
  assert.match(styles, /\.nav__links a \{ display: inline-flex; min-height: 44px/);
  assert.match(page, /Source-fitted temperature/);
  assert.match(page, /toFixed\(3\)/);
  assert.match(page, /Can You Trust Your Model’s Uncertainty/);
  assert.match(page, /Inherent Trade-Offs in Fair Risk Scores/);
  assert.match(page, /Unsupported leap/);
  assert.match(page, /proceedings\.mlr\.press/);
  assert.match(page, /proceedings\.neurips\.cc/);
  assert.match(page, /airc\.nist\.gov/);
  assert.match(layout, /Fairshift Lab — Transparent policy trade-offs under shift/);
  assert.match(layout, /og-v1-1\.png/);
  assert.doesNotMatch(packageJson, /react-loading-skeleton|drizzle/);
  try {
    assert.deepEqual(await readdir(new URL("app/_sites-preview", root)), []);
  } catch (error) {
    assert.equal(error.code, "ENOENT");
  }
});

test("ships the complete frozen policy registry into the interactive release", async () => {
  const registry = JSON.parse(
    await readFile(new URL("../reports/v1.1-policy-study.json", root), "utf8"),
  );
  assert.equal(registry.schema_version, "1.1");
  assert.equal(registry.cells.length, 72);
  assert.equal(registry.policies.length, 8);
  assert.deepEqual(registry.config.seeds, Array.from({ length: 20 }, (_, index) => index + 100));
  assert.ok(registry.cells.some((cell) => cell.pareto_efficient));
  assert.ok(registry.cells.every((cell) => cell.replications === 20));
});
