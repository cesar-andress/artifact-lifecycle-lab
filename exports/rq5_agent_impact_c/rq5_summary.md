# RQ5 — Causal Evidence Summary

> **OBSOLETE FOR MANUSCRIPT COUNTS — DO NOT CITE AS PRIMARY.**  
> Prefer `rq5_results.csv` in this directory (105 condition-C rows) and  
> `../rq5_agent_impact/rq5_abc_comparative_analysis.md` for paired ABC analysis.  
> Header text may still describe A/B design; use the CSV row count.  
> See `docs/SCIENTIFIC_EVIDENCE_FREEZE.md` §Stale.

## Design (frozen protocol)

- Condition **A:** truthful instruction blob at pinned commit.
- Condition **B:** confirmed-false natural instruction blob; all else identical.

## Execution

- Cases: **35**
- Agents: **claude_code**
- Replicates per (case × condition × agent): **3**
- Total runs in results file: **105**

## Raw outcome counts

- `claude_code`: success A=0/0, B=0/0

## Statistics (descriptive only)

- `claude_code` paired_success_difference_a_minus_b: value=0.0, CI=[0.0, 0.0], method=bootstrap_cluster_case
- `claude_code` cohens_h: value=0.0, CI=[0.0, 0.0], method=point_estimate
- `claude_code` mcnemar_p_value: value=1.0, CI=[0.0, 1.0], method=exact_mcnemar
- `claude_code` cliffs_delta_execution_time: value=0.0, CI=[0.0, 0.0], method=point_estimate
