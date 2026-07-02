# Legacy identifier bridge

The canonical `repo_id` in artifact-lifecycle-lab is always derived from a
normalized repository URL (see [`repo_id.md`](repo_id.md)).

Legacy frozen corpora under `~/papers/legacy/ai-artifact-cochange/` used a
different primary key:

| Field | Example | Where |
|-------|---------|-------|
| `repo_id` | `rails/rails` | `data/lifecycle/discovered_v2.csv` |
| `owner` | `rails` | same |
| `repo` | `rails` | same |
| `repo_url` | `https://github.com/rails/rails` | same |

## Mapping rules

```
legacy_id (owner/repo)
    → normalized_repo_url  (https://github.com/{owner}/{repo}, lowercase)
    → repo_id              (sha256(normalized_url).hexdigest()[:16])
```

Implementation: `artifact_lab/contracts/legacy_id.py`

```python
from artifact_lab.contracts.legacy_id import legacy_mapping

legacy_mapping("astral-sh/ruff")
# {
#   "legacy_id": "astral-sh/ruff",
#   "normalized_repo_url": "https://github.com/astral-sh/ruff",
#   "repo_id": "<16-char hash>",
# }
```

## What this bridge does not do

- It does **not** change the canonical `repo_id` used by ingest or L1 Parquet.
- It does **not** rewrite legacy frozen files.
- It does **not** assert bijection from `repo_id` hash back to legacy slug (hash
  is one-way; keep `repo_url` or legacy slug when joining cohorts).

## Joining legacy Parquet to new L1

1. Build a lookup table from legacy `discovered_v2.csv`: `legacy_id` → `repo_id`.
2. Join on `repo_id` after re-extracting with artifact-lifecycle-lab, **or**
   join on `normalized_repo_url` if legacy rows include `repo_url`.

## Examples

| legacy_id | normalized_repo_url | repo_id (16 hex) |
|-----------|---------------------|------------------|
| `rails/rails` | `https://github.com/rails/rails` | compute via `legacy_id_to_repo_id` |
| `microsoft/vscode` | `https://github.com/microsoft/vscode` | compute via `legacy_id_to_repo_id` |

Use tests in `artifact_lab/tests/test_legacy_id_bridge.py` as regression vectors.
