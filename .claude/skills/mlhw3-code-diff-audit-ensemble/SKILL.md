---
name: mlhw3-code-diff-audit-ensemble
description: Runs N parallel read-only audits of assignment3.ipynb with rotated lenses (physics correctness, rubric C/D compliance, ML hygiene, teaching mode, experiment tracking + param count). Merges findings. Persists bundle under .audit/runs/ + active-bundle.json for /mlhw3-code-remediation.
argument-hint: "[n=5]"
---

# Ensemble Code Audit — MLHW3

Goal: **Maximize recall** by running **N independent** read-only audits of `assignment3.ipynb`, then **merging** into one report.

## Step 0 — Read these files first (orchestrator + every subagent, mandatory)

Orchestrator reads before spawning subagents:
1. `assignment3.tex` — **every sentence** of rubric C and D
2. `docs/rubric.md` — C/D checklist
3. `docs/coding-workflow.md` — experiment tracking, notation
4. `docs/reusable-functions.md` — function catalog
5. `Assignement_3_helper_functions.ipynb` — `save_predictions_to_csv()`, `num_params()` reference

Every subagent prompt must instruct the subagent to also read items 1–5 above before auditing.

## Parse arguments

- **N**: integer (default **5**). Clamp to **3–7**.
- **scope** (optional): `steps-X-Y` (e.g. `scope=steps-1-4`). When provided, pass `scope=steps-X-Y` to every subagent. Subagents must only audit steps in that range and must NOT flag steps outside the range as missing or incomplete. Adjust the lens rotation descriptions below to focus on what is relevant for the scoped steps only.

## Execution plan

1. Confirm `assignment3.ipynb` exists.

2. Spawn **N parallel subagents**. Each runs `mlhw3-code-diff-audit` with:
   - `Pass ID: k/N`
   - `Lens: [from table below]`
   - `scope=steps-X-Y` if provided (pass exactly as received)
   - "Follow mlhw3-code-diff-audit output format exactly, including Rating block and Commit Message block."
   - "Only audit steps within the scope range. Do NOT flag steps outside the scope as missing."

   **Lens rotation:**

   | k mod 5 | Lens emphasis |
   |--------|----------------|
   | 1 | Physics correctness — equivariant augmentation, non-physical outputs, dimensional preprocessing, loss formula |
   | 2 | Rubric C/D compliance — CNN, training viz, overfitting, symmetry comparison, U-Net, param count, submission |
   | 3 | ML hygiene — seeds, train/eval modes, data leakage, device handling, gradient flow |
   | 4 | Teaching mode — explanation cells before code, plain language, rubric references, no magic numbers |
   | 0 | Experiment tracking + reusable functions — logs/plots/checkpoints saved, correct source attribution, correct adaptations |

   If N ≠ 5, cycle lenses with k mod 5.

3. **Collect** all N outputs.

4. **Merge** (orchestrator):
   - Deduplicate by root cause.
   - Strong consensus ≥ ceil(2N/3); Majority ≥ floor(N/2)+1; Singleton → needs confirmation.
   - Worst severity wins unless clearly false positive.
   - Merged IDs: **C1, C2, …**

5. **Persist audit bundle** (orchestrator writes — subagents read-only).

## Final output format

### Executive summary
- Top risks (max 7 bullets)
- Consistently found vs noisy/singleton
- Parameter count status (≤120,000 for bonus?)

### Merged findings table
| ID | Severity | Category | Finding | Consensus |
|----|----------|----------|---------|-----------|

### Rubric coverage (merged)
| Section | Sub-point | Status |
|---------|-----------|--------|

### Recommended next steps
- Must-fix vs should-fix (ordered by grade impact)

### Rating (mandatory — merged)
- **Score: X/5** and **Stars:** (⭐ glyphs)
- Rating scale table
- **Justification:** how N passes led to this score

### Commit message (single line)
`feat(notebook): description`

## Persistence (mandatory)

After merged report is finalized, **orchestrator writes**:

- `run_id` = `YYYY-MM-DD-HHMMSS-code-diff`
- Create `.audit/runs/<run_id>/`
- Write `findings.md` — full merged findings table + executive summary
- Write `manifest.json`:
```json
{
  "run_id": "<run_id>",
  "task": "notebook",
  "audit_kind": "code-diff",
  "tool": "mlhw3-code-diff-audit-ensemble",
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
  "audit_kind": "code-diff",
  "tool": "mlhw3-code-diff-audit-ensemble",
  "created": "<ISO-8601 UTC>"
}
```
