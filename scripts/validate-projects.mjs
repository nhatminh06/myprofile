#!/usr/bin/env node
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const registry = JSON.parse(await readFile(new URL("../data/projects.json", import.meta.url)));
const required = ["repository", "name", "slug", "summary", "category", "technologies", "status", "featuredPriority", "demoUrl", "architectureUrl", "evidenceUrl", "limitations", "evidenceSources"];
const values = (key) => registry.projects.map((project) => project[key]);
for (const project of registry.projects) for (const field of required) assert.ok(Object.hasOwn(project, field), `${project.slug || "project"}: missing ${field}`);
assert.equal(new Set(values("repository")).size, registry.projects.length, "duplicate repository");
assert.equal(new Set(values("slug")).size, registry.projects.length, "duplicate slug");
assert.ok(registry.projects.every(({ repository }) => repository.startsWith("nhatminh06/")), "unexpected repository owner");
assert.ok(registry.projects.every(({ summary, limitations, technologies, evidenceSources }) => summary && limitations && technologies.length && evidenceSources.length), "empty required project content");
console.log(`Validated ${registry.projects.length} editorial projects.`);
