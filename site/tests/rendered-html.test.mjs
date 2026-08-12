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
  assert.match(html, /Target reliability/);
  assert.match(html, /Threshold sensitivity/);
  assert.match(html, /Scientific method/);
  assert.match(html, /Research trail/);
  assert.match(html, /Run the experiment/);
  assert.doesNotMatch(html, /codex-preview|react-loading-skeleton|Starter Project/);
});

test("ships accessible controls, research boundaries, and primary sources", async () => {
  const [page, layout, packageJson] = await Promise.all([
    readFile(new URL("app/page.tsx", root), "utf8"),
    readFile(new URL("app/layout.tsx", root), "utf8"),
    readFile(new URL("package.json", root), "utf8"),
  ]);
  assert.match(page, /aria-label="Experiment controls"/);
  assert.match(page, /htmlFor="magnitude"/);
  assert.match(page, /htmlFor="threshold"/);
  assert.match(page, /aria-live="polite"/);
  assert.match(page, /Source-fitted temperature/);
  assert.match(page, /Can You Trust Your Model’s Uncertainty/);
  assert.match(page, /Inherent Trade-Offs in Fair Risk Scores/);
  assert.match(page, /Unsupported leap/);
  assert.match(page, /proceedings\.mlr\.press/);
  assert.match(page, /proceedings\.neurips\.cc/);
  assert.match(page, /airc\.nist\.gov/);
  assert.match(layout, /Fairshift Lab — Fairness under distribution shift/);
  assert.match(layout, /og-v0\.3\.png/);
  assert.doesNotMatch(packageJson, /react-loading-skeleton|drizzle/);
  try {
    assert.deepEqual(await readdir(new URL("app/_sites-preview", root)), []);
  } catch (error) {
    assert.equal(error.code, "ENOENT");
  }
});
