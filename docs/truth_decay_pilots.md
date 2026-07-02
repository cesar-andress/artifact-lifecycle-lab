# TOSEM Go/No-Go Pilot — Half-Life of Truth

**Status:** E1-1000 scaling **paused**. Scientific viability pilot only.

Working concept: *The Half-Life of Truth in Machine-Consumed Documentation.*

## Pilots

| Pilot | Question | Command |
|-------|----------|---------|
| **P1** | Is reference density sufficient for truth-decay measurement? | `make truth-pilot-p1` |
| **P2** | Is agent attribution sufficient for self-maintenance RQs? | `make truth-pilot-p2` |
| **Go/no-go** | Should TOSEM pivot to lifecycle/truth-decay? | `make truth-pilot-go-no-go` |

Run all: `make truth-pilots`

## P1 — Reference Density

- **Sample:** 300–500 instruction files (default 400), stratified across AGENTS.md, CLAUDE.md, Cursor rules, Copilot, GitHub instructions, Skills, prompts
- **Input:** L1 + L1b from pilot + E1-100 (+ E1-1000 if populated)
- **Extract:** paths, directories, commands, script names, dependencies
- **Verify:** against repository HEAD where mechanically possible

**Outputs** (`exports/truth_pilot/`):
- `reference_density.md`
- `reference_examples.csv`
- `reference_summary.csv`

## P2 — Agent Attribution

- **Input:** all L1 commit events touching instruction files
- **Detect:** Co-Authored-By, bot accounts, Claude/Cursor/Copilot strings, tool patterns

**Outputs:**
- `agent_attribution.md`
- `agent_commit_candidates.csv`
- `agent_attribution_summary.csv`

## Go/no-go

- `go_no_go.md` — RQs that survive, RQs to drop, recommended next step

## Constraints

- No E1-1000 extraction
- No paper writing
- No changes to existing E1 outputs
- No optimization passes — viability only

## Implementation

```
artifact_lab/experiments/truth_pilots/
  sample.py           # stratified sampling + L1 commit loader
  references.py       # mechanical extraction
  verify_refs.py      # HEAD verification
  attribution.py      # agent heuristics
  p1_reference.py     # P1 runner
  p2_attribution.py   # P2 runner
  go_no_go.py         # viability report
  __main__.py         # CLI
```
