# Legacy map

Reference root: `~/papers/legacy/ai-artifact-cochange/ai-convention-lifecycle-corpus`

## Useful pieces (reuse ideas, reimplement here)

| Legacy path | Useful for |
|-------------|------------|
| `protocol/lifecycle_v1.yaml` | Detector regex patterns for AI instruction paths, exclusion prefixes, stasis threshold T=180 |
| `scripts/lifecycle/detection.py` | Path normalization, exclude-then-match ordering |
| `scripts/lifecycle/extract_history.py` | Git log `--follow` touch extraction, artifact path discovery via `git log --name-only` |
| `scripts/lifecycle/git_utils.py` | `GIT_TERMINAL_PROMPT=0`, GitHub URL parsing, non-UTF8-safe git output |
| `seeds/seeds.txt`, `seeds/seeds_stratified.txt` | Pilot repo URL pools (AI adopters + general OSS) |
| `protocol/gh_actions_v1.yaml`, `protocol/dependabot_v1.yaml` | Future detector families (not in pilot slice) |
| `scripts/lifecycle/decision_impact.py` | Repository-level label aggregation patterns for L4 experiments |

## Do NOT carry over

| Legacy pattern | Why |
|----------------|-----|
| `data/repos/` permanent full clones | Violates ephemeral-clone principle |
| Shallow discover clones (`--depth 1`) | Non-negotiable constraint: no shallow clones |
| Paper-first Makefile orchestration | Platform uses CLI modules + manifests, not paper build targets |
| Frozen panel paths baked into analysis scripts | Datasets must be versioned via manifests, not hard-coded paths |
| `scripts/lifecycle/corpus_paths.py` monorepo layout | New tree is `platform/` with explicit layers L0–L5 |
| PostgreSQL / long-lived DB assumptions | SQLite WAL (future queue) + Parquet only |
| `ACTIVE` / `DORMANT` state names | L2 uses `absent`, `young`, `active`, `stale`, `deleted` |
| Direct experiment writes into `data/lifecycle/` | Experiments are leaves; core datasets are ingest/derive only |
| GitHub `gh` API stars fetch as extraction dependency | Optional covariate, not L1 spine |
| Multi-family paper cohort coupling | Families are protocol YAMLs; cohorts come from registry |

## Pilot repos sourced from legacy

These URLs in `data/registry/pilot_repos.csv` come from legacy seed files:

- AI-weighted: Continue, pydantic-ai, LangChain, OpenHands, claude-code, MCP servers, Aider, open-webui, Prefect, CrewAI, Dify
- General OSS control: Ruff, Django, FastAPI, Next.js, VS Code
- Known artifact example: dagster-io/dagster (CLAUDE.md paths cited in legacy paper figures)
