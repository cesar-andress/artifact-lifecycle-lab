# E1-1000 pre-execution checklist

Complete every item before running `make e1-1000` for the first time.

Record completion date and operator initials in the **Execution log** at the bottom.

---

## Freeze verification

- [ ] **Registry frozen** — `data/registry/e1_1000_repos.csv` committed; hash matches `protocol/experiment_manifest.yaml`
- [ ] **Protocol frozen** — `protocol/E1_1000_protocol_v1.md` committed; no post-freeze edits without version bump
- [ ] **Detector frozen** — `artifact_lab/protocol/families/ai_conventions_v1.yaml` unchanged; hash matches manifest
- [ ] **Manifests frozen** — `protocol/experiment_manifest.yaml` committed with `execution_date: null`
- [ ] **Cohort design documented** — `exports/e1_1000/cohort_design.md` includes sampling rationale sections
- [ ] **Dataset lineage documented** — `docs/dataset_lineage.md` committed

## Quality gates

- [ ] **Tests pass** — `make test` (or `python3.12 -m pytest artifact_lab/tests -q`) exits 0
- [ ] **Registry QA** — `make e1-1000-qa` confirms 1,000 unique repo_ids/URLs (pre-extraction: `missing=1000` expected)
- [ ] **Git clean** — no uncommitted changes to registry, protocol, or detector files
- [ ] **Commit pushed** — freeze commit on `main` pushed to remote

## Execution readiness

- [ ] **Execution command recorded** — `make e1-1000` documented in protocol and manifest
- [ ] **Expected outputs listed** — fig1, table1, cohort_summary, pilot_performance, e1_census paths verified in protocol
- [ ] **Disk space** — ≥5 GB free for clones, blobs, and Parquet (estimate; adjust for environment)
- [ ] **Network / GitHub access** — API and git clone access confirmed
- [ ] **Time budget** — operator aware of ~12–24 h sequential runtime estimate
- [ ] **Export isolation** — confirm `exports/e1/` and `exports/e1_100/` will not be overwritten

## Post-freeze prohibitions (until execution completes)

- [ ] Do **not** edit `data/registry/e1_1000_repos.csv`
- [ ] Do **not** change detector patterns or protocol YAML
- [ ] Do **not** change Makefile E1-1000 paths or wave id
- [ ] Do **not** run `make e1-1000-registry` (would regenerate registry)

---

## Execution log

| Field | Value |
|-------|-------|
| Operator | |
| Checklist completed (UTC) | |
| Git SHA at execution | |
| Command | `make e1-1000` |
| Started (UTC) | |
| Completed (UTC) | |
| QA result | |
| Notes | |

After successful execution, update `protocol/experiment_manifest.yaml`:

- `execution_date: <ISO-8601 UTC>`
- `wave_id: e1_1000_v1`
- `git_sha: <commit at execution>`
