# .audit/ — Audit Bundle Storage

Stores ensemble audit results for `assignment3.tex` and `assignment3.ipynb`.

## Structure

```
.audit/
├── README.md                    ← this file
├── active-bundle.json           ← pointer to the latest audit run
└── runs/
    └── <run_id>/
        ├── manifest.json        ← run metadata
        └── findings.md          ← merged findings (R# for report, C# for code)
```

## Workflow

1. Run `/mlhw3-report-diff-audit-ensemble` → writes to `.audit/runs/<run_id>/` and updates `active-bundle.json`
2. Run `/mlhw3-code-diff-audit-ensemble` → same structure, `audit_kind: code-diff`
3. Run `/mlhw3-report-remediation` or `/mlhw3-code-remediation` → reads from `active-bundle.json`
4. After remediation is complete: archive or delete the run folder

## `active-bundle.json` format

```json
{
  "bundle_path": ".audit/runs/<run_id>",
  "run_id": "<run_id>",
  "audit_kind": "report-diff | code-diff",
  "tool": "mlhw3-report-diff-audit-ensemble | mlhw3-code-diff-audit-ensemble",
  "created": "<ISO-8601 UTC>"
}
```

## Finding ID conventions

- Report findings: `R1`, `R2`, … (from report audits)
- Code findings: `C1`, `C2`, … (from code audits)
- Plan findings: `P1`, `P2`, … (stored under `dev/active/<task>/plan-audits/`)
