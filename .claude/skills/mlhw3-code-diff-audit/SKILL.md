---
name: mlhw3-code-diff-audit
description: Single-pass read-only audit of changes to assignment3.ipynb. Checks rubric C/D, physics correctness (equivariant augmentation, dimensional analysis, non-physical outputs), ML hygiene (seeds, train/eval modes, no data leakage), teaching mode (explain before implement), and experiment tracking. Outputs structured review with star rating.
argument-hint: "[optional focus notes] [Pass ID: k/N] [Lens: name] [scope=steps-X-Y]"
---

# Code Diff Audit — MLHW3

Audit **current changes to `assignment3.ipynb`** and produce a structured review.

**Read-only — no writes.**

## Parse arguments

- **scope** (optional): `steps-X-Y` (e.g. `steps-1-4`). When provided, **only audit the steps in range X–Y** from `docs/coding-workflow.md`. Do NOT flag steps outside this range as missing or incomplete — those are simply not in scope. Omit all checklist items that belong to out-of-scope steps. If no scope is given, audit the entire notebook.

The 13 steps and their scope groupings:
| Steps | Content |
|-------|---------|
| 1 | Data exploration — load/visualize cross-sections and flow fields, print dataset statistics |
| 2 | Preprocessing pipeline — load npy+csv, normalize (v₀), train/val split, TensorData, DataLoaders |
| 3 | Dimensional analysis — Buckingham π, v₀ = ΔP·ΔA/(μ·L), dimensionless form, make_dim_hom() |
| 4 | Data augmentation — equivariant flip/rotation applied to BOTH input cross-section AND label flow field |
| 5 | Baseline CNN — adapt create_model() from lab7 for 32×64 |
| 6 | Loss function — Kaggle E formula with ε, adapt rmsre() from lab7 |
| 7 | Training loop — adapt train_model() from lab6, checkpoint + JSON log saving |
| 8 | Evaluation and plotting — loss curves saved to experiments/plots/ |
| 9 | Overfitting prevention — implement and demonstrate at least one strategy |
| 10 | Symmetry enforcement — GroupAvgModel from lab7, compare with/without |
| 11 | U-Net design — implement, compare parameter efficiency vs CNN |
| 12 | Parameter count — run num_params(), verify ≤120,000 for bonus |
| 13 | Kaggle submission — save_predictions_to_csv() |

## Step 0 — Read these files first (mandatory, before getting the diff)

1. `assignment3.tex` — **every sentence** of rubric sections C and D; primary authority
2. `docs/rubric.md` — structured C/D checklist; use as audit grid
3. `docs/coding-workflow.md` — experiment tracking convention, notation reference
4. `docs/reusable-functions.md` — function catalog (verify adaptations)
5. `Assignement_3_helper_functions.ipynb` — reference for `save_predictions_to_csv()` and `num_params()`

## Safety

- Do not modify any file.
- Do not execute any notebook cells.
- If fixes are needed, describe them and ask for permission.

## Get the changes

1. `git diff HEAD -- assignment3.ipynb` — staged and unstaged changes
2. If no git: read `assignment3.ipynb` in full and treat entire notebook as in scope.

## Read every file (mandatory)

- Read `assignment3.ipynb` in full.
- Read `assignment3.tex` — rubric sections C and D. Every sentence matters.
- Read `CLAUDE.md` — coding workflow, reusable functions catalog, experiment tracking convention.
- Read `Assignement_3_helper_functions.ipynb` — reference for `save_predictions_to_csv()` and `num_params()`.
- Read cited lab notebooks if verifying a function adaptation (e.g. `reusable code/lab7-solution_34MLS_260317.ipynb` for `create_model()`, `flip()`, `rot()`, `GroupAvgModel`).

## Audit checklist

Only check items whose step number falls within the scope range. Skip (do not mention) items outside the scope.

**Rubric C compliance (Steps 5–11):**
- [ ] [Step 5] At least one CNN model implemented and trained
- [ ] [Step 7–8] Training loss curves (train + val) plotted with axis labels and title
- [ ] [Step 9] At least one anti-overfitting strategy implemented in code (not just mentioned)
- [ ] [Step 9] Effectiveness of anti-overfitting shown in plots
- [ ] [Step 10] Quantitative symmetry comparison: model with symmetry vs without, using a symmetry metric
- [ ] [Step 11] Parameter efficiency comparison: CNN vs U-Net (parameter count vs performance)
- [ ] [Step 11] U-Net or fully convolutional network implemented
- [ ] [Step 5–11] Code snippets for salient elements (in notebook markdown or to be copied to report)

**Rubric D compliance (Steps 12–13):**
- [ ] [Step 12] `num_params()` called on the submitted model
- [ ] [Step 12] Parameter count ≤ 120,000 (if claiming bonus) — FLAG if exceeded
- [ ] [Step 13] `save_predictions_to_csv()` produces correct format: `id` column (integer, not float) + 2048 columns, shape [500, 2049]

**Physics correctness:**
- [ ] [Step 4] **Equivariant augmentation** — when input cross-section is transformed (flip/rotate), the SAME transformation is applied to the label flow field
- [ ] [Step 5] **Non-physical output prevention** — is there any mechanism preventing positive flow predictions at closed pixels (pixel=0)?
- [ ] [Step 3] **Dimensional preprocessing** — are physical parameters (ΔP, L, μ, ΔA) preprocessed into dimensionless or scaling variables (v₀ = ΔP·ΔA/(μ·L))?
- [ ] [Step 6] **Loss function formula** — does the implemented loss match the Kaggle formula: E = (1/N)(1/NₓNᵧ) Σ |q_pred - q_true| / (q_true + ε)?

**ML hygiene:**
- [ ] [Step 2] `torch.manual_seed()` set at top of notebook
- [ ] [Step 2] `np.random.seed()` set at top of notebook
- [ ] [Step 7] `model.train()` called before training batches
- [ ] [Step 7] `model.eval()` called before validation
- [ ] [Step 7] `optimizer.zero_grad()` called correctly
- [ ] [Step 2] Validation set strictly held out (no data leakage)
- [ ] [Step 2] Normalization statistics computed only on training data
- [ ] [Step 2] `device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')` present

**Teaching mode:**
- [ ] [All steps] Every major code cell has a markdown explanation cell BEFORE it
- [ ] [All steps] Explanations written in plain language (student can repeat them)
- [ ] [All steps] Each explanation references which rubric point it addresses
- [ ] [All steps] No "magic numbers" without explanation

**Experiment tracking:**
- [ ] [Step 7] Loss dicts saved to `experiments/logs/` as JSON
- [ ] [Step 8] All plots saved to `experiments/plots/`
- [ ] [Step 7] Best model saved to `experiments/checkpoints/`
- [ ] [Step 7] Run naming follows `{model_name}_{YYYYMMDD_HHMMSS}` convention

**Reusable function adaptation:**
- [ ] [All steps] Adapted functions have a comment noting the source (e.g. `# adapted from lab7: create_model()`)
- [ ] [Step 5] `create_model()` from lab7 correctly adapted for 32×64 (not 40×40)
- [ ] [Step 7] `train_model()` from lab6 correctly adapted for regression (no accuracy_fn needed)
- [ ] [Step 4] `flip()`, `rot()` from lab7 applied to BOTH input and label

## Output format

### Change Summary
[What changed in the notebook]

### Analysis
[Detailed breakdown — rubric compliance, physics issues, hygiene issues]

### Bugs Found
[Actual bugs — or **None.** if clean]

### Rubric Coverage
| Section | Sub-point | Status |
|---------|-----------|--------|

### Physics Issues
[List — or **None.**]

### ML Hygiene Issues
[List — or **None.**]

### Teaching Mode Issues
[Missing explanations — or **None.**]

### Parameter Count
[State count if num_params() called; FLAG if >120,000]

---

## Rating (mandatory)

**Score: X/5**  **Stars:** [⭐ glyphs]

**Justification:** [1–4 sentences]

| Score | Meaning |
|-------|--------|
| ⭐⭐⭐⭐⭐ 5/5 | Perfect — all rubric C/D points, correct physics, clean hygiene, full teaching mode |
| ⭐⭐⭐⭐ 4/5 | Good — minor gaps, solid overall |
| ⭐⭐⭐ 3/5 | Acceptable — some rubric points missing or hygiene issues |
| ⭐⭐ 2/5 | Needs work — significant rubric misses or physics errors |
| ⭐ 1/5 | Major issues — core implementations missing |
| 0/5 | Do not submit — broken code, major physics violations |

---

## Commit Message

```text
feat(notebook): description
```

Single line, conventional commits. Do not actually commit.

---

## Ensemble / Pass ID

If Pass ID / Lens was given, echo at the top. Use issue IDs C1, C2, … in findings.
