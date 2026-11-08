# Portfolio verification audit — 2026-11-08

The GitHub API returned 40 public repositories with pagination. Forks, course exercises, profile/configuration repositories, and unrelated small projects were reviewed but not automatically added. The editorial registry selects 14 repositories; discovery never changes the public site.

## Findings addressed

- `projects.html` duplicated MatchSense, Market Pulse, Linux Kernel Lab, Personal Cognitive Load Monitor, and Company Research across its primary and earlier-project grids.
- EdgeCloud Vision Lab was public and evidence-backed but missing.
- TensorForge now has committed RTX 3050 Laptop GPU measurements, while remaining an analytical model rather than a cycle-accurate simulator.
- QuorumKV has a checksum-verified captured failover run and incident viewer; this is a run observation, not a formal guarantee.
- Wirestack's TCP and packet-level Linux interoperability coverage had outgrown the portfolio copy; several TCP and IP features remain explicitly unimplemented.
- PageDB now reaches a loopback server and read-only SQL pipeline, but transactions, WAL, recovery, optimizer, DML, and the Java client remain unfinished.
- CogniFlow has configuration readiness and reviewed local kind qualification for a synthetic fixture. Its own compatibility matrix still blocks GKE; no successful cloud runtime evidence was found.
- The served resume records VietinBank as May–August 2026. No editable resume source was found in this repository, so the PDF was not rewritten.

## GitHub metadata recommendations

- Add concise descriptions to `tensorforge`, `quorumkv`, `wirestack`, and `pagedb`.
- Add the existing showcase URL to `tensorforge` and `quorumkv`; add evidence or case-study URLs to `wirestack`, `pagedb`, `commercecore`, and `pgsentry` where useful.
- Keep `aeigs` as the real repository identifier even though the display name is Aegis.
- Add a small, consistent topic set (for example `distributed-systems`, `ml-systems`, `cuda`, `raft`, `tcp`, `database`, or `gitops`) only where each topic accurately describes implemented work.
