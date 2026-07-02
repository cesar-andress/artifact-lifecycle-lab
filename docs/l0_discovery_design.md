# L0 discovery integration design

**Status:** design only (Milestone 1.2). No GitHub search implementation in this milestone.

**Goal:** Expand L0 repository registry beyond static CSV without duplicating a fourth discovery stack. Reuse patterns from `~/papers/vsdlc/vsdlc` (`vsdlc_mining`).

---

## Current L0 (artifact-lifecycle-lab)

| Input | Path | Behavior |
|-------|------|----------|
| Pilot registry CSV | `data/registry/pilot_repos.csv` | Columns: `repo_url`, optional `seed_pool`, `notes`, skip flags (`archived`, `skip_reason`, `too_large`) |
| Derived fields | ingest | `repo_id` = SHA-256 prefix of normalized URL; `normalized_repo_url` |

Extract (`artifact_lab.ingest extract`) reads CSV only. No live GitHub API.

---

## Reference implementation: vsdlc Phases 1–2

Location: `~/papers/vsdlc/vsdlc/src/vsdlc_mining/`

### Phase 1 — seed search (`seed_search.py`)

- **Input:** configured code-search query list (`SEED_SEARCH_QUERIES` in `config.py`)
- **API:** `GitHubClient.search_code()` with pagination, rate-limit backoff (`github_client.py`)
- **Output:** `data/raw/repo_candidates.jsonl` — one `RepoCandidate` per line
- **Checkpoint:** `data/interim/seed_search_checkpoint.json`
  - `completed_queries`, `search_completed`, `aggregate` (full_name → queries + matched_paths), `enriched_full_names`
  - Supports resume after rate limits or interruption (`load_checkpoint`, `save_checkpoint`, `repair_checkpoint`)
- **Dedup:** aggregate by `full_name` (GitHub `owner/repo`)

### Phase 2 — repo filter (`repo_filter.py`)

- **Input:** `repo_candidates.jsonl`
- **API:** `GitHubClient.get_repo()` for metadata enrichment
- **Rules:** structural exclusions (fork, archived, mirror, template), keyword exclusions, `MIN_STARS`, `MIN_PUSHED_AT`, CI/test path hints
- **Output:**
  - `data/interim/eligible_repos.jsonl` (`EligibleRepo`)
  - `data/interim/excluded_repos.jsonl` (`ExcludedRepo` + reasons)
  - `data/interim/filter_summary.json`
- **Checkpoint:** append JSONL + summary JSON (filter can resume via candidate cursor)

### Shared infrastructure

| Module | Role |
|--------|------|
| `github_client.py` | httpx client, retries, primary/secondary rate limits |
| `config.py` | path constants, query lists, thresholds |
| `models.py` | Pydantic `RepoCandidate`, `EligibleRepo`, `ExcludedRepo` |
| `metadata.py` | Normalize API payloads |
| `utils.py` | `read_jsonl`, `append_jsonl`, `write_json`, `salvage_json` |

**Explicitly out of scope in vsdlc release:** clone, history extract, release-unit traces (Phases 3+). That boundary matches artifact-lifecycle-lab: vsdlc = discovery frame audit; lab = extract + L1+.

---

## Proposed L0 architecture (future)

```
                    ┌─────────────────────┐
                    │  protocol families   │  (YAML path predicates)
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         ▼                     ▼                     ▼
  pilot_repos.csv      vsdlc JSONL export    github discover (future)
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │  registry normalizer │  → canonical repo_id, URL, metadata
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │  L0 registry store   │  Parquet or JSONL + manifest
                    │  data/registry/v1/   │
                    └──────────┬──────────┘
                               ▼
                    artifact_lab.ingest extract
```

### Registry normalizer (new module, not implemented yet)

Suggested path: `artifact_lab/ingest/registry.py`

Responsibilities:

1. Accept **multiple source formats** (see below).
2. Emit rows with canonical fields:
   - `repo_id` (hash, unchanged)
   - `repo_url` / `normalized_repo_url`
   - `source` (`csv_pilot`, `vsdlc_eligible`, `github_discover`, …)
   - `discovery_queries`, `matched_paths` (optional, from vsdlc)
   - `exclusion_reason` (if filtered out before extract)
   - `seed_pool`, `notes` (provenance)
3. Write `data/registry/v1/registry.parquet` + `manifest.yaml`.

### Input formats (priority order)

| Format | Source | Mapping |
|--------|--------|---------|
| **CSV** (current) | `data/registry/pilot_repos.csv` | `repo_url` required; skip columns preserved |
| **vsdlc eligible JSONL** | `eligible_repos.jsonl` | `full_name` → URL; carry `matched_paths`, `evidence_flags`, filter reasons from exclusion file |
| **vsdlc candidates JSONL** | pre-filter pool | optional wider pool before eligibility |
| **GitHub discover** (future) | new `artifact_lab.ingest discover` | Port or wrap `vsdlc_mining.github_client` + checkpoint pattern — **do not reimplement rate limits** |

### CLI sketch (future, not Milestone 1.2)

```bash
# Phase A: discover (optional, needs GITHUB_TOKEN)
python -m artifact_lab.ingest discover \
  --family ai_conventions_v1 \
  --output data/discovery/v1/candidates.jsonl \
  --checkpoint data/state/discovery_checkpoint.json

# Phase B: normalize to L0 registry
python -m artifact_lab.ingest registry build \
  --csv data/registry/pilot_repos.csv \
  --vsdlc-eligible ~/papers/vsdlc/vsdlc/data/interim/eligible_repos.jsonl \
  --output data/registry/v1/

# Phase C: extract (existing)
python -m artifact_lab.ingest extract --registry data/registry/v1/registry.parquet ...
```

Extract should accept **either** CSV or registry Parquet via `--registry` autodetect.

---

## Reuse vs rewrite (vsdlc)

| vsdlc component | Recommendation |
|-----------------|----------------|
| `github_client.py` | **REFERENCE / COPY SMALL PARTS** when implementing discover — rate-limit logic is battle-tested |
| `seed_search.py` checkpoint aggregate | **REFERENCE** — same resume semantics as SQLite job queue for extract |
| `repo_filter.py` eligibility rules | **REFERENCE** — convert thresholds to registry YAML or config, not hard-coded duplication |
| `models.py` | **REFERENCE** — map to L0 schema columns; do not import vsdlc as runtime dependency |
| Pydantic + httpx stack | **OPTIONAL** — lab currently minimal deps; add only when discover is implemented |

**Do not** add `vsdlc` package as a git submodule or pip dependency without a version pin strategy. Prefer copying the client into `artifact_lab/ingest/github/` in a dedicated commit when implementation starts.

---

## Checkpoint and state alignment

| Concern | vsdlc | artifact-lifecycle-lab today | Future L0 |
|---------|-------|------------------------------|-----------|
| Discovery resume | JSON checkpoint + JSONL | — | JSON or SQLite table `discovery_jobs` |
| Extract resume | — | SQLite `extraction_jobs` | unchanged |
| Permanent outputs | JSONL interim | Parquet L1 | Registry Parquet `v1/` |

Keep discovery checkpoints under `data/state/` or `data/discovery/v1/` (regenerable), separate from L1.

---

## Contamination / frame metadata (vsdlc-specific)

vsdlc records **why** a repo entered the frame (`queries`, `matched_paths`, contamination labels). L0 should preserve these as **optional columns** for downstream papers, even if extract ignores them.

Suggested columns:

- `discovery_frame_id` (e.g. `instruction_artifact_pilot`, `second_frame_topic`)
- `matched_paths` (list)
- `query_labels` (list)

This avoids re-running expensive GitHub search when reproducing a cohort.

---

## Non-goals (this design)

- No GitHub API calls in Milestone 1.2
- No new detector families
- No merge of vsdlc contamination analysis into core derive
- No Snakemake / DAG orchestration yet (`artifact_lab/dag/` remains stub)

---

## Open decisions (before implementation)

1. **Registry primary store:** Parquet vs JSONL for L0 (recommend Parquet + manifest for consistency with L1).
2. **Discover command location:** `artifact_lab.ingest discover` vs separate `artifact_lab.discover` top-level module.
3. **vsdlc import strategy:** vendored `github_client.py` vs optional extra `[github]` dependency group.
4. **Overlap with legacy `discover_v2.py`:** legacy is HEAD-only discovery on permanent clones — **do not port**; vsdlc supersedes for API-based discovery.

---

## Success criteria for L0 implementation (future milestone)

- [ ] Ingest `discover` resumes from checkpoint after rate limit
- [ ] `registry build` merges CSV + vsdlc JSONL without `repo_id` collisions
- [ ] Manifest documents `input_datasets` including vsdlc export paths and `code_git_sha`
- [ ] Extract unchanged except `--registry` accepts Parquet
- [ ] Tests use fixture JSONL, no live API in CI
