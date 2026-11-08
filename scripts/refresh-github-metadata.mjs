#!/usr/bin/env node
import { readFile, writeFile } from "node:fs/promises";

const registry = JSON.parse(await readFile(new URL("../data/projects.json", import.meta.url)));
const cacheUrl = process.env.GITHUB_METADATA_PATH ? new URL(`file://${process.env.GITHUB_METADATA_PATH}`) : new URL("../data/github-metadata.json", import.meta.url);
const expected = new Set(registry.projects.map(({ repository }) => repository.toLowerCase()));
const owner = "nhatminh06";
const headers = { Accept: "application/vnd.github+json", "User-Agent": "myprofile-metadata-refresh" };
if (process.env.GITHUB_TOKEN) headers.Authorization = `Bearer ${process.env.GITHUB_TOKEN}`;

async function github(path) {
  const response = await fetch(`${process.env.GITHUB_API_URL || "https://api.github.com"}${path}`, { headers });
  if (!response.ok) throw new Error(`GitHub ${response.status}: ${response.statusText}`);
  return response;
}

try {
  const publicRepos = [];
  for (let page = 1; ; page += 1) {
    const batch = await (await github(`/users/${owner}/repos?type=public&per_page=100&page=${page}`)).json();
    publicRepos.push(...batch.filter((repo) => repo.visibility === "public" && !repo.private));
    if (batch.length < 100) break;
  }
  const byName = new Map(publicRepos.map((repo) => [repo.full_name.toLowerCase(), repo]));
  const missing = [...expected].filter((repository) => !byName.has(repository));
  const discovered = publicRepos.filter((repo) => !expected.has(repo.full_name.toLowerCase())).map((repo) => repo.full_name).sort();
  const repositories = [...expected].filter((repository) => byName.has(repository)).sort().map((repository) => {
    const repo = byName.get(repository);
    return { repository: repo.full_name, url: repo.html_url, description: repo.description, homepage: repo.homepage || null, topics: repo.topics, pushedAt: repo.pushed_at, archived: repo.archived };
  });
  const output = { checkedAt: new Date().toISOString(), source: "live-github-api", repositories, missing, discovered };
  await writeFile(cacheUrl, `${JSON.stringify(output, null, 2)}\n`);
  console.log(`Verified ${repositories.length} selected public repositories; ${missing.length} missing; ${discovered.length} unlisted public repositories require editorial review.`);
  if (missing.length) { console.error(`Missing or renamed: ${missing.join(", ")}`); process.exitCode = 1; }
} catch (error) {
  const cached = JSON.parse(await readFile(cacheUrl, "utf8"));
  console.error(`GitHub refresh failed (${error.message}). Using cached metadata from ${cached.checkedAt}; it is not freshly verified.`);
  process.exitCode = 2;
}
