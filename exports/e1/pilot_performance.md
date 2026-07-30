# Pilot extraction performance

Documentation-only summary of pilot registry extraction profiling.

## Summary

- Profiled repositories: **17**
- Total execution time (sum of per-repo totals): **1279.5 s**
- Median extraction time: **32.2 s**
- Mean extraction time: **75.3 s**
- Successful extractions: **17**
- Skipped repositories: **0**
- Failed repositories: **0**
- Slow-repo threshold: **300 s**

## Slowest repositories

| Rank | Repository | Total | Clone | Inspection | History | Detector | Blobs | Status |
|------|------------|-------|-------|------------|---------|----------|-------|--------|
| 1 | microsoft/vscode | 478.4 s | 13.9 s | 0.0 s | 358.9 s | 0.2 s | 105.4 s | ok |
| 2 | pydantic/pydantic-ai | 171.1 s | 1.2 s | 67.4 s | 39.8 s | 0.0 s | 62.6 s | ok |
| 3 | prefecthq/prefect | 140.3 s | 2.6 s | 0.0 s | 52.5 s | 0.0 s | 85.1 s | ok |
| 4 | langgenius/dify | 120.7 s | 3.5 s | 0.0 s | 72.4 s | 0.1 s | 44.6 s | ok |
| 5 | vercel/next.js | 114.4 s | 5.5 s | 0.0 s | 70.8 s | 0.3 s | 37.7 s | ok |
| 6 | dagster-io/dagster | 66.6 s | 7.1 s | 0.0 s | 36.4 s | 0.2 s | 22.8 s | ok |
| 7 | all-hands-ai/openhands | 47.7 s | 2.6 s | 0.0 s | 13.2 s | 0.0 s | 31.8 s | ok |
| 8 | astral-sh/ruff | 36.9 s | 3.3 s | 0.0 s | 15.0 s | 0.1 s | 18.5 s | ok |
| 9 | langchain-ai/langchain | 32.2 s | 2.8 s | 0.0 s | 12.9 s | 0.0 s | 16.4 s | ok |
| 10 | crewaiinc/crewai | 19.7 s | 1.4 s | 0.0 s | 15.2 s | 0.2 s | 2.8 s | ok |

## Slowest phases (aggregate)

- **history**: 715.7 s (55.9% of attributed phase time)
- **blobs**: 438.8 s (34.3% of attributed phase time)
- **inspection**: 67.5 s (5.3% of attributed phase time)
- **clone**: 55.7 s (4.4% of attributed phase time)
- **detector**: 1.4 s (0.1% of attributed phase time)
- **cleanup**: 0.2 s (0.0% of attributed phase time)
- **parquet_write**: 0.0 s (0.0% of attributed phase time)
- **manifest_write**: 0.0 s (0.0% of attributed phase time)

## Clone sizes

- Median clone size: **26.1 MB**
- Mean clone size: **51.1 MB**
- Largest clone: **321.2 MB**

| Repository | Clone size |
|------------|------------|
| microsoft/vscode | 321.2 MB |
| vercel/next.js | 107.7 MB |
| dagster-io/dagster | 87.1 MB |
| django/django | 69.5 MB |
| langgenius/dify | 53.9 MB |
| prefecthq/prefect | 42.3 MB |
| astral-sh/ruff | 41.5 MB |
| langchain-ai/langchain | 40.6 MB |
| all-hands-ai/openhands | 26.1 MB |
| continuedev/continue | 23.3 MB |
| open-webui/open-webui | 19.5 MB |
| crewaiinc/crewai | 10.0 MB |
| tiangolo/fastapi | 8.2 MB |
| aider-ai/aider | 6.7 MB |
| pydantic/pydantic-ai | 6.2 MB |
| modelcontextprotocol/servers | 3.8 MB |
| anthropics/claude-code | 0.6 MB |

## Repositories skipped

None.

## Repositories failed

None.

## Recommendations

- History traversal dominates aggregate time: quantify `git log --follow` calls per matched path before changing traversal strategy.
- Clone size is heavy-tailed (max 321.2 MB): mark oversized repos in the registry before scaling beyond the pilot.
- Measure first, optimize second — do not change detectors or infrastructure until variance is understood.

## Regeneration

```bash
make e1-pilot   # development
make e1         # full pilot
make paper      # copy exports to ../paper/
```
