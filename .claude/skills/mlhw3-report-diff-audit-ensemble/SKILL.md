---
name: mlhw3-report-diff-audit-ensemble
description: Runs N parallel read-only audits of assignment3.tex with rotated lenses (rubric A, rubric B, rubric C/D, notation, report quality). Merges findings into one report with star rating. Persists bundle under .audit/runs/ + active-bundle.json for /mlhw3-report-remediation.
argument-hint: "[n=5]"
---

# Ensemble Report Audit — MLHW3

Goal: **Maximize recall** by running **N independent** read-only audits of `assignment3.tex`, then **merging** into one report.

## Step 0 — Read these files first (orchestrator + every subagent, mandatory)

Orchestrator reads before spawning subagents:
1. `assignment3.tex` — **every sentence**
2. `docs/rubric.md` — A–E checklist
3. `lecture notes.latex` — notation authority
4. `template.tex` — IEEE structure

Every subagent prompt must instruct the subagent to also read items 1–4 above before auditing.

## Parse arguments

- **N**: integer (default **5**). Clamp to **3–7**.

## Execution plan

1. Confirm `assignment3.tex` exists.

2. Spawn **N parallel subagents**. Each runs `mlhw3-report-diff-audit` with:
   - `Pass ID: k/N`
   - `Lens: [from table below]`
   - "Follow mlhw3-report-diff-audit output format exactly, including Rating block with Score X/5, Star glyphs, rating scale table, and Commit Message block."

   **Lens rotation:**

   | k mod 5 | Lens emphasis |
   |--------|----------------|
   | 1 | Rubric A — physics, dimensional analysis, symmetries, loss functions |
   | 2 | Rubric B — network design, augmentation, architectures, hardwiring symmetries |
   | 3 | Rubric C/D — implementation evidence, code snippets, training plots, Kaggle score, param count |
   | 4 | Notation compliance — lecture notes formalism, SI units, equivariance/invariance vocabulary |
   | 0 | Report quality E — figures, captions, language, page limit, reproducibility, bibliography |

   If N ≠ 5, cycle lenses with k mod 5.

3. **Collect** all N outputs.

4. **Merge:**
   - Deduplicate by root cause (not wording).
   - Strong consensus ≥ ceil(2N/3); Majority ≥ floor(N/2)+1; Singleton → needs confirmation.
   - Worst severity wins unless clearly false positive in other passes.
   - Merged IDs: **R1, R2, …**

5. **Persist audit bundle** (orchestrator writes — subagents stay read-only).

## Merge rules

- If passes disagree, document both views.
- Treat singleton notation findings as "needs confirmation" but still list them — notation matters for the grade.
- Every rubric sub-point missed by at least one pass must appear in merged findings, even if other passes found it OK.

## Final output format

### Executive summary
- Top risks (max 7 bullets)
- Consistently found vs noisy/singleton

### Merged findings table
| ID | Severity | Rubric section | Finding | Consensus |
|----|----------|----------------|---------|-----------|

### Rubric coverage (merged)
| Section | Sub-point | Status (pass/fail/partial) |
|---------|-----------|---------------------------|

### Recommended next steps
- Must-fix vs should-fix (ordered by rubric impact on grade)

### Rating (mandatory — merged)
One final assessment (not arithmetic average unless justified):
- **Score: X/5** and **Stars:** (⭐ glyphs)
- Include rating scale table
- **Justification:** how N passes and consensus led to this score

### Commit message (single line)
`docs(report): description`

## Persistence (mandatory)

After merged report is finalized, **orchestrator writes**:

- `run_id` = `YYYY-MM-DD-HHMMSS-report-diff`
- Create `.audit/runs/<run_id>/`
- Write `findings.md` — full merged findings table + executive summary
- Write `manifest.json`:
```json
{
  "run_id": "<run_id>",
  "task": "report",
  "audit_kind": "report-diff",
  "tool": "mlhw3-report-diff-audit-ensemble",
  "created": "<ISO-8601 UTC>",
  "findings_file": "findings.md",
  "in_scope_finding_ids": null
}
```
- Write `.audit/active-bundle.json`:
```json
{
  "bundle_path": ".audit/runs/<run_id>",
  "run_id": "<run_id>",
  "audit_kind": "report-diff",
  "tool": "mlhw3-report-diff-audit-ensemble",
  "created": "<ISO-8601 UTC>"
}
```

Chat output is in addition to these files.
