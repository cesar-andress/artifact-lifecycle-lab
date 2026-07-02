# E1-1000 dataset lineage

Complete dependency chain from frozen registry to paper exports.  
Each arrow is a **hard dependency**: downstream artifacts must be regenerated if upstream inputs change.

---

## Lineage diagram

```
protocol/experiment_manifest.yaml
protocol/E1_1000_protocol_v1.md
data/registry/e1_1000_repos.csv          (L0 — frozen registry)
data/registry/sources/general_oss_candidates.jsonl   (pool snapshot; registry build input)
         │
         ▼  make e1-1000-extract
         │  inputs: registry, ai_conventions_v1.yaml, git SHA
         │
data/l1/e1_1000/v1/events.parquet        (L1 — file event log)
data/l1/e1_1000/v1/manifest.yaml
data/blobs/                              (L1b — content-addressed text)
data/receipts/                           (per-repo extraction audit)
data/profiling/extraction_profile.parquet (wave e1_1000_v1 rows)
         │
         ▼  make e1-1000-derive
         │  inputs: L1 events, T=180
         │
data/derived/file_state_panel/e1_1000/v1/panel_T180.parquet   (L2)
data/derived/file_state_panel/e1_1000/v1/manifest_T180.yaml
         │
         ▼  make e1-1000-exports
         │  inputs: L1 events, registry (filter scope)
         │
data/derived/adoption_census/e1_1000/v1/
    path_census.parquet
    repo_census.parquet
    repo_family_census.parquet
         │
         ├──────────────────────────────────┐
         ▼                                  ▼
exports/e1_1000/fig1.csv              exports/e1_1000/table1.csv
exports/e1_1000/fig1.pdf                  │
         │                                  │
         └──────────────┬───────────────────┘
                        ▼  make e1-1000-performance + e1-1000-summary
exports/e1_1000/e1_census.md
exports/e1_1000/pilot_performance.md
exports/e1_1000/cohort_summary.md
         │
         ▼  make paper (optional, one-way)
../paper/figures/fig1.pdf
../paper/tables/table1.csv
../paper/main.pdf                        (private paper repo — not artifact)
```

---

## Layer-by-layer dependencies

### L0 — Registry

| Artifact | Depends on |
|----------|------------|
| `data/registry/e1_1000_repos.csv` | VSDLC instruction pool, general-OSS search snapshot, second-frame pool; seed 42; `build_e1_1000.py` |
| `exports/e1_1000/cohort_design.md` | Same build script; documents sampling |

**Frozen for v1.** Changing the registry invalidates all downstream layers.

### L1 — Extraction

| Artifact | Depends on |
|----------|------------|
| `events.parquet` | L0 registry, detector YAML, extraction code, GitHub repo state at clone time |
| `manifest.yaml` | Row count, schema, `registry_version`, `extraction_wave`, `detector_version`, `code_git_sha` |
| `data/blobs/*` | Matched file contents from git objects |
| `extraction_profile.parquet` | Per-repo timings and outcomes for wave `e1_1000_v1` |

Regenerating L1 requires re-cloning all 1,000 repositories.

### L2 — Panel

| Artifact | Depends on |
|----------|------------|
| `panel_T180.parquet` | L1 `events.parquet`; horizon `T=180` days |

Used for current-presence state features. E1 census primary path uses L1 directly; L2 is available for extended analyses within scope.

### E1 — Adoption census

| Artifact | Depends on |
|----------|------------|
| `path_census.parquet` | L1 events grouped by `(repo, path, family)` |
| `repo_census.parquet` | Aggregated from path census |
| `repo_family_census.parquet` | Aggregated by `(repo, artifact_family)` |

Census outputs are **filtered to L0 registry repo_ids** at export time.

### Exports

| Artifact | Depends on |
|----------|------------|
| `fig1.csv` / `fig1.pdf` | L1 events (registry-filtered); monthly first-appearance aggregation |
| `table1.csv` | `repo_family_census` rows (registry-filtered) |
| `e1_census.md` | Census counts + registry size |
| `pilot_performance.md` | `extraction_profile.parquet` filtered to registry; latest-per-repo |
| `cohort_summary.md` | Registry + profiles + census + table1 |

### Paper (external)

The private paper repository (`../paper/`) consumes **export copies only**. It never feeds back into the artifact pipeline.

---

## Version pins (E1-1000 v1)

See `protocol/experiment_manifest.yaml` for authoritative hashes and versions.

| Pin | Value |
|-----|-------|
| Protocol | `E1_1000_protocol_v1` |
| Registry version | `e1_1000_v1` |
| Extraction wave | `e1_1000_v1` |
| Detector family | `ai_conventions_v1` @ `1.0.0` |
| Inspection mode | `head-only` |
| Panel T | `180` days |

---

## Isolation from other cohorts

| Cohort | L1 path | Export path |
|--------|---------|-------------|
| Pilot (17) | `data/l1/file_event_log/v1/` | `exports/e1/` |
| Engineering (100) | `data/l1/e1_100/v1/` | `exports/e1_100/` |
| Scientific (1000) | `data/l1/e1_1000/v1/` | `exports/e1_1000/` |

Profiling parquet is shared but rows are keyed by `(repo_id, extraction_wave)`.
