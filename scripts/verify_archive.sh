#!/usr/bin/env bash
# Fail if any archival path required by REPLICATION.md is missing.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

required=(
  LICENSE
  CITATION.cff
  .zenodo.json
  REPLICATION.md
  RELEASE_NOTES.md
  CHANGELOG.md
  README.md
  docs/SCIENTIFIC_EVIDENCE_FREEZE.md
  protocol/TRUTH_DECAY_PROTOCOL_v1.md
  exports/paper_synthesis/late_binding_evidence_table.csv
  exports/truth_decay_pilot/rq2_failure_audit_summary.md
  exports/truth_decay_pilot/gfc_confirmatory_summary.md
  exports/truth_decay_pilot/born_stale_summary.md
  exports/truth_decay_pilot/rq1_feasibility.md
  exports/truth_decay_pilot/rq2_summary.md
  exports/truth_decay_pilot/rq3_summary.md
  exports/truth_decay_pilot/rq4_summary.md
  exports/truth_pilot/p4_validation.md
  exports/truth_pilot/agent_attribution_gold_worksheet.csv
  exports/rq5_agent_impact/rq5_uptake_analysis.md
  exports/rq5_agent_impact/rq5_abc_comparative_analysis.md
  exports/rq5_agent_impact/rq5_results.csv
  exports/rq5_agent_impact_c/rq5_results.csv
  exports/rq5_lb_blind_annotation/WITHDRAWN.md
)

missing=0
for f in "${required[@]}"; do
  if [[ ! -e "$f" ]]; then
    echo "MISSING: $f"
    missing=1
  fi
done

# Superseded summaries must carry an obsolete banner
for f in exports/rq5_agent_impact/rq5_summary.md exports/rq5_agent_impact_c/rq5_summary.md; do
  if ! grep -q 'OBSOLETE' "$f"; then
    echo "MISSING OBSOLETE BANNER: $f"
    missing=1
  fi
done

# Annotation kits must not be present
if [[ -d exports/rq5_lb_blind_annotation/human_annotation_kit ]]; then
  echo "UNEXPECTED: human_annotation_kit still present"
  missing=1
fi

# No absolute home-directory defaults in Makefile
if grep -nE '/home/|/Users/' Makefile | grep -v '^#' ; then
  echo "UNEXPECTED absolute path in Makefile"
  missing=1
fi

if [[ "$missing" -ne 0 ]]; then
  echo "verify_archive: FAILED"
  exit 1
fi
echo "verify_archive: OK (${#required[@]} required paths present)"
