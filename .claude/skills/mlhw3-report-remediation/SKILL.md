---
name: mlhw3-report-remediation
description: Single remediation command for assignment3.tex — discover bundle, optional triage_first, then fix (report tex) → verify → closure. Fixes rubric gaps, notation errors, figure issues. bundle=, task=, phase=, skip_fix.
argument-hint: "[triage_first | skip_fix | bundle=path | phase=...]"
---

# Report Remediation — MLHW3

**Purpose:** One command runs the full report remediation sequence for `assignment3.tex`:

1. **Discover** the on-disk audit bundle (`.audit/active-bundle.json` or `bundle=`)
2. **Optional: Triage** — classify each R# as real gap vs already addressed vs uncertain
3. **Fix** — edit `assignment3.tex` to resolve rubric gaps and notation errors
4. **Verify** — read-only check per R#
5. **Post-fix closure** — final verdict and grade impact

## Step 0 — Read these files first (mandatory)

Before discovering the bundle or doing anything else:
1. `assignment3.tex` — **every sentence**; fixes must satisfy this
2. `docs/rubric.md` — rubric checklist (know what "fixed" means for each R#)
3. `lecture notes.latex` — notation authority (for notation fixes)
4. `template.tex` — IEEE structure reference

## Parse `$ARGUMENTS`

- **`triage_first`** — run triage before fix. Recommended when ≥8 findings or `audit_kind: full`.
- **`skip_fix`** — skip fix; run verify → post-fix only.
- **`phase=`** — `all` (default) | `triage` | `fix` | `verify` | `post-fix`
- **`bundle=`** — path to bundle directory
- **`task=report`** — use `.audit/active-bundle.json` with audit_kind=report-diff

## Bundle discovery (first match wins)

1. `bundle=` → that path; `manifest.json` must exist; `audit_kind` must be `report-diff`.
2. `.audit/active-bundle.json` → `bundle_path` → `manifest.json` with `audit_kind: report-diff`.
3. Else error: run `/mlhw3-report-diff-audit-ensemble` first.

**Typical:** `/mlhw3-report-diff-audit-ensemble` → `/mlhw3-report-remediation`

## Phase triage (read-only, optional)

Spawn 3–5 read-only `report-reviewer` subagents. For each R#, classify:

| Classification | Meaning |
|----------------|---------|
| **`real_issue`** | Rubric point still missing or notation still wrong. |
| **`audit_false_positive`** | Already in report; audit misread. Skip in fix phase. |
| **`uncertain`** | Include in fix scope by default. |

## Phase fix (edits `assignment3.tex`)

**Scope:** `assignment3.tex` only. Do not touch notebook or other files.

**Non-negotiables:**
- Every added sentence must be understood by the student — teaching mode applies
- Use lecture notes notation exactly
- Never remove content that satisfies a rubric point (only add or correct)
- Respect the 6-page limit — if content must be cut, move to conclusion or note "see notebook appendix"

**Partition workers by lens:**

| Agent | Lens | Typical targets |
|-------|------|-----------------|
| A | Rubric A gaps — physics, dimensional analysis, symmetries, loss functions | Sections A sub-points |
| B | Rubric B gaps — network design, architectures, hardwiring | Sections B sub-points |
| C | Rubric C/D gaps — implementation evidence, code snippets, Kaggle score | Section Part 2, D claims |
| D | Notation + figures — lecture notes compliance, axis labels, captions, language | Throughout |

Rules: one owner per R#; same section → one agent or strict ordering.

### Output — Phase fix
- Assignment table: Agent | Lens | Finding IDs
- Per fix agent: findings addressed, lines changed, unresolved IDs
- Merged resolution table: R# → fixed | partially fixed | unresolved | false positive

## Phase verify (read-only)

Spawn 3–5 `report-reviewer` subagents. Check current `assignment3.tex` against each R#.

### Output — Phase verify
- Executive summary: is report actually closer to 10/10? (yes / partially / no)
- Verdict table: ID | Verdict | Evidence | Remaining gap
- Notation issues still present

## Phase post-fix (read-only closure)

### Output — Phase post-fix
- Fixed / Partially fixed / Unresolved / False positive per R#
- **Estimated grade impact** — for each section A/B/C/D/E: what score the report now likely achieves
- **Merge recommendation:** ready to submit to Overleaf | ready with follow-ups | not ready

## Safety
- Fix phase edits `assignment3.tex` only.
- Verify and post-fix are read-only.
- Never reduce page count below what is needed for rubric coverage.
