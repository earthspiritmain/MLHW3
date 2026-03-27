---
name: mlhw3-plan-remediation
description: Plan-doc remediation for MLHW3 — discover plan-audit bundle, optional triage_first, then fix (-plan/-context/-tasks) → verify → plan proof → post-fix closure. No code edits unless user overrides. task=, bundle=, phase=, skip_fix.
argument-hint: "[triage_first | skip_fix | bundle=path | task=name | phase=...]"
---

# Plan post-audit remediation — MLHW3

**Purpose:** One command runs the full plan-doc remediation sequence in order:

1. **Discover** the on-disk plan audit bundle (`manifest.json` + `findings.md`)
2. **Optional: Triage** — classify each P# as still a gap vs already addressed vs uncertain
3. **Fix** — edit `-plan.md`, `-context.md`, `-tasks.md` only
4. **Verify** — read-only check per P#
5. **Proof** — doc traceability check
6. **Post-fix closure** — plan readiness recommendation

## Step 0 — Read these files first (mandatory)

Before discovering the bundle or doing anything else:
1. `CLAUDE.md` — non-negotiables
2. `assignment3.tex` — **every sentence**; fixes must satisfy this
3. `docs/rubric.md` — rubric checklist (know what "fixed" means before fixing)
4. `docs/coding-workflow.md` — step order and conventions
5. `docs/reusable-functions.md` — function catalog

## Parse `$ARGUMENTS`

- **`triage_first`** — run triage before fix. Recommended when ≥8 findings.
- **`skip_fix`** — skip fix; run verify → proof → post-fix only.
- **`phase=`** — `all` (default) | `triage` | `fix` | `verify` | `proof` | `post-fix`
- **`bundle=`** — path to bundle directory
- **`task=`** — name under `dev/active/`

## Bundle discovery (first match wins)

1. `bundle=` → that path; `manifest.json` must exist.
2. `task=` → `dev/active/<task>/plan-audits/active-bundle.json` → `bundle_path`
3. Glob `dev/active/*/plan-audits/active-bundle.json` — exactly one file.
4. Else error: run `/mlhw3-plan-audit task=<name>` first.

**Typical:** `/mlhw3-plan-audit task=cnn-baseline` → `/mlhw3-plan-remediation task=cnn-baseline`

## Phase triage (read-only, optional)

Spawn 3–7 read-only subagents (use `plan-reviewer`). For each P#, classify:

| Classification | Meaning |
|----------------|---------|
| **`real_issue`** | Gap still in docs; fix should address. |
| **`audit_false_positive`** | Already covered; skip in fix phase. |
| **`uncertain`** | Include in fix scope by default. |

### Output — Phase triage
- Triage table (P# → classification + evidence)
- Fix scope: explicit ID list

## Phase fix (edits plan docs only)

**Scope:** `dev/active/<task>/<task>-plan.md`, `-context.md`, `-tasks.md` only. No notebook or .tex edits unless user explicitly asked.

**Partition workers by lens:**

| Agent | Lens | Typical targets |
|-------|------|-----------------|
| A | Rubric A/B physics + notation | `-context` non-negotiables; plan physics sections |
| B | Rubric C/D implementation + param count | `-plan` implementation; `-tasks` checklist |
| C | Teaching mode + explanations | `-plan` explanation requirements; `-tasks` verification |
| D | Reusable functions + experiment tracking | `-context` function sources; `-tasks` tracking steps |

Rules: one owner per P#; same file → one agent or strict ordering.

### Output — Phase fix
- Assignment table: Agent | Lens | Finding IDs
- Per fix agent: findings attempted, files changed, unresolved IDs
- Merged resolution table: P# → fixed | partially fixed | unresolved | false positive

## Phase verify (read-only)

Spawn 3–7 read-only `plan-reviewer` subagents. Check current state of three task docs against each P#.

Verdict per P#: **fixed** | **partially fixed** | **unresolved** | **false positive**

### Output — Phase verify
- Executive summary: are plan docs stronger? (yes / partially / no)
- Verdict table: ID | Verdict | Evidence | Remaining gap

## Phase proof (doc traceability)

For each in-scope P#: table mapping P# → evidence (section or checkbox in `-plan`/`-context`/`-tasks`) → OK | gap.

If any non-doc file was changed: flag it (unexpected — should not happen).

### Output — Phase proof
- P# → doc evidence table
- "Plan-docs-only remediation" confirmation (or flag if code was touched)

## Phase post-fix (read-only closure)

### Output — Phase post-fix
- Fixed / Partially fixed / Unresolved / False positive per P#
- Contradictions introduced by fixes
- **Plan readiness:** ready to implement | ready with follow-ups | not ready
- Optional: Score X/5 for residual plan risk (same scale as diff-audit)

## Orchestrator output

1. Resolved bundle path + run_id + audit_kind: plan
2. `phase=all`: Triage (if `triage_first`) → Fix → Verify → Proof → Post-fix
3. End: hint to archive `plan-audits/<run-id>/` after plan ships
