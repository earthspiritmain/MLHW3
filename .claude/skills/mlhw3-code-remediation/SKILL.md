---
name: mlhw3-code-remediation
description: Single remediation command for assignment3.ipynb — discover bundle, optional triage_first, then fix (notebook) → verify → closure. Fixes rubric C/D gaps, physics errors, ML hygiene, teaching mode issues. bundle=, phase=, skip_fix.
argument-hint: "[triage_first | skip_fix | bundle=path | phase=...]"
---

# Code Remediation — MLHW3

**Purpose:** One command runs the full notebook remediation sequence for `assignment3.ipynb`:

1. **Discover** the on-disk audit bundle
2. **Optional: Triage** — classify each C# as real gap vs already addressed
3. **Fix** — edit `assignment3.ipynb` to resolve rubric gaps, physics errors, hygiene issues
4. **Verify** — read-only check per C#
5. **Post-fix closure** — final verdict

## Step 0 — Read these files first (mandatory)

Before discovering the bundle or doing anything else:
1. `assignment3.tex` — **every sentence** of rubric C and D; fixes must satisfy this
2. `docs/rubric.md` — C/D checklist (know what "fixed" means for each C#)
3. `docs/coding-workflow.md` — step order, experiment tracking, notation
4. `docs/reusable-functions.md` — function catalog (fixes must use lab functions where possible)
5. `Assignement_3_helper_functions.ipynb` — `save_predictions_to_csv()`, `num_params()` reference

## Parse `$ARGUMENTS`

- **`triage_first`** — recommended when ≥8 findings or audit_kind: full
- **`skip_fix`** — skip fix; run verify → post-fix only
- **`phase=`** — `all` (default) | `triage` | `fix` | `verify` | `post-fix`
- **`bundle=`** — path to bundle directory

## Bundle discovery (first match wins)

1. `bundle=` → that path; `audit_kind` must be `code-diff`.
2. `.audit/active-bundle.json` → `bundle_path` → `audit_kind: code-diff`.
3. Else error: run `/mlhw3-code-diff-audit-ensemble` first.

**Typical:** `/mlhw3-code-diff-audit-ensemble` → `/mlhw3-code-remediation`

## Phase triage (read-only, optional)

Spawn 3–5 `code-reviewer` subagents. For each C#, classify:

| Classification | Meaning |
|----------------|---------|
| **`real_issue`** | Rubric point missing, physics error, or ML hygiene problem. |
| **`audit_false_positive`** | Already in notebook; audit misread. Skip in fix phase. |
| **`uncertain`** | Include in fix scope by default. |

## Phase fix (edits `assignment3.ipynb`)

**Non-negotiables:**
- **Teaching mode ALWAYS** — every new or changed code cell gets a markdown explanation cell BEFORE it, in plain language the student can repeat
- Every fix must be something the student can explain — no black-box solutions
- Step-by-step: implement one component, test it, document it — do not batch multiple components
- Use reusable functions from labs where possible (see CLAUDE.md catalog)
- Physics must be correct: equivariant augmentations, correct loss formula, seeds set

**Partition workers by lens:**

| Agent | Lens | Typical targets |
|-------|------|-----------------|
| A | Physics + augmentation | Equivariant flip/rot, loss formula, dimensional preprocessing |
| B | Rubric C — models + training | CNN architecture, training loop, loss curves |
| C | Rubric C — symmetry + U-Net | GroupAvgModel adaptation, U-Net, comparison |
| D | ML hygiene + experiment tracking | Seeds, train/eval modes, saves to experiments/ |
| E | Rubric D + teaching mode | num_params(), save_predictions_to_csv(), explanation cells |

Rules: one owner per C#; same cell → one agent or strict ordering; no agent implements more than one major component per run.

### Output — Phase fix
- Assignment table: Agent | Lens | Finding IDs
- Per fix agent: findings addressed, cells changed/added, unresolved IDs
- Merged resolution table: C# → fixed | partially fixed | unresolved | false positive

## Phase verify (read-only)

Spawn 3–5 `code-reviewer` subagents. Check current `assignment3.ipynb` against each C#.

### Output — Phase verify
- Executive summary: is notebook actually closer to a 10/10? (yes / partially / no)
- Verdict table: ID | Verdict | Evidence | Remaining gap
- Teaching mode compliance still missing?
- Parameter count still >120,000?

## Phase post-fix (read-only closure)

### Output — Phase post-fix
- Fixed / Partially fixed / Unresolved / False positive per C#
- **Parameter count status** — state the total from num_params() if available
- **Submission readiness** — can `/mlhw3-kaggle-submit` be run now?
- **Merge recommendation:** ready to submit | ready with follow-ups | not ready

## Safety
- Fix phase edits `assignment3.ipynb` only.
- Verify and post-fix are read-only.
- Never implement a component the student cannot explain.
