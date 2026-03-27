---
name: mlhw3-plan-audit
description: N parallel read-only passes over dev/active task docs for MLHW3. Audits rubric coverage, teaching mode, step-by-step order, reusable function reuse, and physics correctness. Merges findings with star rating. Persists plan-audit bundle on disk for /mlhw3-plan-remediation.
argument-hint: "\"<task>\" [n=5] [challenge_round | apply_edits]"
---

# Plan audit — MLHW3 porous media flow assignment

Goal: **Stress-test** an on-disk plan under `dev/active/<task>/` before implementation, using **N** independent read-only passes, then **merge** with a star rating. **Persist a machine-readable bundle** (mandatory). **Doc edits** optional (`apply_edits`); otherwise use `/mlhw3-plan-remediation`.

## Step 0 — Read these files first (orchestrator + every subagent, mandatory)

Before spawning any subagent, the orchestrator reads:
1. `CLAUDE.md` — non-negotiables
2. `assignment3.tex` — **every sentence**; rubric authority
3. `docs/rubric.md` — structured rubric checklist
4. `docs/coding-workflow.md` — step order, experiment tracking
5. `docs/reusable-functions.md` — function catalog

Every subagent prompt must instruct the subagent to also read items 2–5 above plus the three task docs.

## Parse arguments

- **Task**: first positional token or `task=<name>`. If missing, stop and ask.
- **N**: integer (default **5**). Clamp to **3–7**.
- **`challenge_round`** (optional): after merge, run one extra challenge pass where each lens reacts to the top 2 risks from other lenses.
- **`apply_edits`** (optional): after bundle, also apply merged edits to the three task docs.

Files that must exist under `dev/active/<task>/`:
- `<task>-plan.md`
- `<task>-context.md`
- `<task>-tasks.md`

## Execution plan

1. Confirm `dev/active/<task>/` and three files exist. If missing, stop with instructions.

2. Spawn **N parallel subagents** (use `plan-reviewer` agent). Each is **read-only**.

   **Lens rotation** (pass k of N):

   | k mod 5 | Lens emphasis |
   |--------|----------------|
   | 1 | Rubric A coverage — physics, dimensional analysis, symmetries, loss functions |
   | 2 | Rubric B coverage — network design, augmentation, architectures, hardwiring |
   | 3 | Rubric C/D coverage — implementation, training, comparison, parameter count |
   | 4 | Teaching mode — every component explained before implement, student-explainable |
   | 0 | Reusable functions + experiment tracking — correct sources, correct adaptations, logs/plots/checkpoints |

   Each subagent prompt must include:
   - `Pass ID: k/N`
   - `Lens: [from table]`
   - Read: `dev/active/<task>/<task>-plan.md`, `-context.md`, `-tasks.md`
   - Read: `CLAUDE.md` fully (rubric + non-negotiables)
   - Read: relevant sections of `assignment3.tex`
   - Output: **Top insights** (≤5), **Risks** (≤5, severity), **Concrete edits** (bullets), **Open questions** (≤5)
   - **Rating (mandatory):** Score X/5, Stars (⭐/☆), Justification (1–4 sentences), full rating scale table. Interpret as **plan readiness to implement**.

3. **Merge:**
   - Deduplicate by root cause.
   - Strong consensus ≥ ceil(2N/3); Majority ≥ floor(N/2)+1; Singletons → needs confirmation.
   - Worst severity wins unless clearly false positive.
   - Assign stable IDs **P1, P2, …**

4. **Persistence (mandatory — orchestrator writes):**

   - `run_id` = `YYYY-MM-DD-HHMMSS-plan`
   - Create `dev/active/<task>/plan-audits/<run_id>/`
   - Write `manifest.json`:
   ```json
   {
     "run_id": "<run_id>",
     "task": "<task>",
     "audit_kind": "plan",
     "tool": "mlhw3-plan-audit",
     "created": "<ISO-8601 UTC>",
     "findings_file": "findings.md",
     "in_scope_finding_ids": null
   }
   ```
   - Write `findings.md` — executive summary + Merged findings table (P1, P2, … with severity, summary, target file/section) + Open questions + Rating block.
   - Write `dev/active/<task>/plan-audits/active-bundle.json`:
   ```json
   {
     "bundle_path": "dev/active/<task>/plan-audits/<run_id>",
     "run_id": "<run_id>",
     "audit_kind": "plan",
     "tool": "mlhw3-plan-audit",
     "created": "<ISO-8601 UTC>",
     "task": "<task>"
   }
   ```

5. **Edit task docs (optional — only if `apply_edits`):** Update `-plan.md`, `-context.md`, `-tasks.md` with concrete edits from merged findings. Add Plan change log entry. Do not implement application code.

## Mandatory invariant checks (every pass must flag if plan violates)

From `CLAUDE.md`:
- **Rubric completeness** — every sub-point in the relevant rubric sections must be addressed
- **Teaching mode** — explain before implement, student must be able to explain every component
- **Step-by-step order** — follows the coding workflow in CLAUDE.md
- **Physics** — augmentations equivariant, dimensional analysis correct

## Final output (chat)

1. **Executive summary** — plan ready to implement or what is missing?
2. **Merged findings** — P1, P2, … (severity, one-line summary, target)
3. **On-disk bundle** — paths written
4. **Open questions** — for human decision
5. **Rating (mandatory — merged):** Score X/5, Stars, Justification, rating scale table
6. **Next step:** suggest `/mlhw3-plan-remediation task=<task>` unless `apply_edits` ran
