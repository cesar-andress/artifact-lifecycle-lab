# Evidence

Case-level evidence for each of the 121 events is embedded in:

- `../rq2_audit_form.xlsx` (sheet `audit_form`)
- `../rq2_audit_blinded.csv`

Key fields include repository URL, instruction path, reference text, failure
commit, transition, verified-before-failure, return-after-missing,
basename-collision flag, observation counts, and snippet context.

Use those fields together with public repository inspection at the listed URL
and commit. No separate per-event evidence dumps are required beyond what is
already in the blinded table.
