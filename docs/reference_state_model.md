# Reference State Model (RQ1)

**Protocol:** `protocol/TRUTH_DECAY_PROTOCOL_v1.md`  
**Implementation:** `artifact_lab/experiments/truth_decay/states.py`  
**Longitudinal output:** `exports/truth_decay_pilot/reference_longitudinal.csv`

---

## Purpose

Each mechanically extracted reference in an instruction file is tracked as a **longitudinal observation**. At every L1 commit snapshot where the file exists, the reference receives a deterministic state. State changes document truth decay, repair, and file death.

This model supports **RQ1**: *How does the truth of machine-consumed documentation evolve over time?*

---

## Observation unit

One row = one reference at one commit snapshot:

```
(repo_id, instruction_path, commit, reference_type, reference) → state
```

Join key: `repo_id + instruction_path + commit/time + reference_type + reference`

---

## States

| State | Meaning |
|-------|---------|
| **VERIFIED** | Reference is mechanically satisfied at the observation commit (path/directory/script/dependency resolves in the commit tree or manifest). |
| **MISSING** | Reference is checkable but not satisfied at the observation commit. |
| **UNVERIFIABLE** | Reference cannot be resolved mechanically (typically shell commands, make targets). |
| **REPAIRED** | Previous state was `MISSING`; current verification succeeds **and** the instruction file was edited in this commit window. Encodes explicit repair of a stale claim. |
| **DELETED** | Instruction file deletion event; all references from the prior snapshot are marked deleted. |

States are **uppercase** in exports and analysis tables.

---

## Base verification mapping

Verification engine output (lowercase) maps to base states before repair logic:

| verify_status | Base state |
|---------------|------------|
| `verified` | VERIFIED |
| `missing` | MISSING |
| `unverifiable` | UNVERIFIABLE |

Repair overlay:

```
if previous_state == MISSING and base_state == VERIFIED:
    state = REPAIRED
else:
    state = base_state
```

---

## Documented transitions

Every observation records `previous_state` and `transition`.

| Transition | Interpretation |
|------------|----------------|
| `INIT→VERIFIED` | First observation; reference present and valid |
| `INIT→MISSING` | First observation; reference already stale |
| `INIT→UNVERIFIABLE` | First observation; command-like reference |
| `VERIFIED→MISSING` | **Truth decay** — reference went stale |
| `MISSING→MISSING` | Persistent stale claim |
| `MISSING→REPAIRED` | **Repair** — instruction or repo now satisfies claim |
| `MISSING→VERIFIED` | Repair without explicit REPAIRED label (repo fixed, instruction unchanged) — encoded as VERIFIED unless prior was MISSING at immediately previous snapshot |
| `*→DELETED` | Instruction file removed |
| `*→REMOVED` | Reference dropped from instruction text (file still exists) |

Reference **additions** and **removals** are flagged separately:

- `reference_added=True` when a reference key first appears in the instruction text.
- `reference_removed=True` when a reference key disappears between snapshots (transition ends with `->REMOVED`).

---

## First failure and repair events

| Flag | Definition |
|------|------------|
| `first_failure` | First time a reference key enters `MISSING` along its trajectory |
| `repair_event` | Observation with state `REPAIRED` |

These flags support exploratory statistics (time-to-first-missing, repair latency) without survival models.

---

## Verification scope (v1)

Verified at **L1 `commit_sha`**, not clone HEAD:

- **path / script_name:** present in `git ls-tree` at commit
- **directory:** prefix match in commit tree
- **dependency:** name found in commit-time manifest blob
- **command:** usually UNVERIFIABLE; script substring may resolve to VERIFIED/MISSING

---

## Longitudinal reconstruction algorithm

For each `(repo_id, instruction_path)`:

1. Sort L1 events by `commit_time`.
2. For each event:
   - **delete:** emit `DELETED` for all references in previous snapshot.
   - **add/modify:** load blob text → extract references → verify each at `commit_sha`.
   - Compare reference key sets with previous snapshot (additions/removals).
   - Assign state using previous state + verification outcome.
3. Emit one longitudinal row per reference per snapshot (+ removal rows).

---

## What this model does not capture

- Semantic correctness (LLM judgment)
- Agent vs human attribution (RQ3)
- Competing risks / hazard rates (RQ2 — deferred)
- Repo-side fixes that satisfy a reference without instruction-file edits (may appear as VERIFIED without REPAIRED)

---

## Related outputs

| Artifact | Path |
|----------|------|
| Longitudinal table | `exports/truth_decay_pilot/reference_longitudinal.csv` |
| Exploratory stats | `exports/truth_decay_pilot/rq1_exploratory_stats.csv` |
| Feasibility report | `exports/truth_decay_pilot/rq1_feasibility.md` |
| Figures A–D | `exports/truth_decay_pilot/figure_*.pdf` |
