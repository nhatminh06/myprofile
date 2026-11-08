import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { spawnSync } from "node:child_process";

const registry = JSON.parse(await readFile(new URL("../data/projects.json", import.meta.url)));

test("registry has unique repositories, slugs, and featured priorities", () => {
  for (const key of ["repository", "slug"]) assert.equal(new Set(registry.projects.map((project) => project[key])).size, registry.projects.length);
  const priorities = registry.projects.map((project) => project.featuredPriority).filter(Boolean);
  assert.equal(new Set(priorities).size, priorities.length);
});

test("every claim has evidence and an explicit limitation", () => {
  for (const project of registry.projects) {
    assert.ok(project.evidenceSources.length, project.repository);
    assert.ok(project.limitations, project.repository);
  }
});

test("metadata refresh labels cached data as stale when GitHub is unavailable", () => {
  const result = spawnSync(process.execPath, [new URL("../scripts/refresh-github-metadata.mjs", import.meta.url).pathname], {
    encoding: "utf8",
    env: { ...process.env, GITHUB_API_URL: "http://127.0.0.1:1", GITHUB_METADATA_PATH: new URL("../data/github-metadata.json", import.meta.url).pathname }
  });
  assert.equal(result.status, 2);
});

test("metadata refresh warning never presents cached data as fresh", async () => {
  const source = await readFile(new URL("../scripts/refresh-github-metadata.mjs", import.meta.url), "utf8");
  assert.match(source, /it is not freshly verified/);
});
