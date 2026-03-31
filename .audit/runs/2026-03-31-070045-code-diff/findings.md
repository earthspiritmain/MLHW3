# Ensemble Code Audit — assignment3.ipynb
**Run ID:** 2026-03-31-070045-code-diff
**Passes:** 3 (Physics correctness · Rubric C/D compliance · ML hygiene)
**Notebook scope:** Steps 1–3 only (18 cells)

---

## Executive Summary

**Top risks (grade impact order):**

1. Steps 4–13 are entirely absent — no CNN, no training loop, no loss function, no augmentation, no symmetry comparison, no U-Net, no Kaggle submission. This affects every rubric C and D sub-point.
2. Cell ordering error: the Step 3 `make_dim_hom()` code cell executes before the markdown that explains it — violates teach-before-implement.
3. Second Buckingham π group (π₂ = ΔA/L²) is dismissed as trivially 1 without numerical verification — if it varies across samples the model is under-specified.
4. `v0` is computed inline in Step 2 and again via `make_dim_hom()` in Step 3 — two sources of truth for the same formula (bridged by `assert`, but the inline copy in Step 2 should be removed once `make_dim_hom()` exists).
5. No ε guard on the v0 division (`train_labels / v0[:, None, None]`) — safe in practice but a silent NaN risk.
6. Seed reset pattern (`np.random.seed(SEED)` mid-notebook in Cell 6) will create augmentation-epoch confusion when Steps 4+ are written.
7. Student name/ID/Kaggle ID fields are still placeholder text.

**Consistently found (3/3 consensus):** Steps 4–13 entirely missing. The notebook covers only data exploration and preprocessing.
**Majority (2/3):** Cell ordering issue (Step 3 code before its explanation markdown). v0 double-computation pattern.
**Singleton:** Second π group not numerically verified (P3). Missing split disjointness assert (H12). No ε guard on v0 division (P7).

**Parameter count status:** `num_params()` never called. Bonus (≤120,000 params, 0.5/10) cannot be awarded.

---

## Merged Findings Table

| ID | Severity | Consensus | Category | Finding |
|----|----------|-----------|----------|---------|
| C1 | CRITICAL | 3/3 | Missing implementation | Steps 4–13 entirely absent: no data augmentation, no CNN, no loss function, no training loop, no overfitting prevention, no symmetry comparison, no U-Net, no `num_params()`, no `save_predictions_to_csv()`. Every rubric C and D sub-point is NOT_YET_IMPLEMENTED. |
| C2 | CRITICAL | 3/3 | Rubric D | No Kaggle submission generated. `submissions/` is empty. `save_predictions_to_csv()` never called. `num_params()` never called. Low-complexity bonus cannot be awarded. |
| C3 | MEDIUM | 2/3 | Teaching mode | Step 3 markdown cell (Buckingham π derivation) appears AFTER the Step 3 code cell (`make_dim_hom()` definition + verification). A reader executing cells top-to-bottom runs code before seeing its justification. Violates teach-before-implement. Fix: swap cell order so markdown precedes code. |
| C4 | MEDIUM | 1/3 | Physics — dimensional analysis | The second Buckingham π group π₂ = ΔA/L² is dismissed as "trivially 1" in the markdown without numerical verification. If ΔA ≠ L² across samples, the network needs π₂ as an additional scalar input to be fully specified. Should verify `(train_params['delta_A'] / train_params['L']**2).describe()` and discuss. |
| C5 | MEDIUM | 2/3 | Code structure | `v0` is computed twice: inline in Cell 15 (Step 2) and via `make_dim_hom()` in Cell 16 (Step 3). The `assert np.allclose` bridges them safely, but the inline formula in Step 2 should be replaced with a `make_dim_hom()` call once the function is defined. Current structure requires `make_dim_hom()` to be defined in Step 3 but called only after Step 2 has already computed v0. |
| C6 | LOW | 1/3 | Physics — safety | No ε guard on `train_labels / v0[:, None, None]`. If any v0 value were 0 (ΔP=0 or ΔA=0), this silently produces NaN. Physical parameters are strictly positive so risk is low, but an `assert (v0 > 0).all()` would be a cheap and clear guard. |
| C7 | LOW | 2/3 | ML hygiene | `np.random.seed(SEED)` is called again mid-notebook in Cell 6 (exploration sample selection). Harmless now, but if augmentation cells (Steps 4+) use the same pattern, they risk resetting the seed to the same state on every cell re-run, producing the same augmentation every epoch. Prefer `np.random.default_rng(SEED)` for local draws. |
| C8 | LOW | 1/3 | ML hygiene | No assert that `train_idx` and `val_idx` are disjoint. `torch.randperm` guarantees disjointness by construction, but an explicit assertion is consistent with the defensive style already established (CSV column assert in Cell 15). |
| C9 | INFO | 1/3 | ML hygiene | Placeholder text: student name, student ID, and Kaggle ID in Cell 0 are still `[Your name here]`, `[Your ID here]`, `[Your Kaggle username here]`. Must be filled before submission. |
| C10 | INFO | 3/3 | Positive | Steps 1–3 are high quality: seeds set correctly (both torch and numpy), DataLoader generator seeded, v0 formula dimensionally correct, q/v0 O(1) verification in place, source attribution comments present (`# adapted from lab4: make_dim_hom()`), plots saved with axis labels, `TensorData` adapted from lab6 with changes documented, no data leakage in the split. |

---

## Rubric Coverage (merged)

| Section | Sub-point | Status |
|---------|-----------|--------|
| A | Dimensional analysis — v0 formula, SI units correct | PARTIAL (π₂ not verified — C4) |
| A | Dimensionless learning problem written explicitly | PARTIAL (q/v₀ form correct; π₂ gap) |
| A | Dataset characterisation (distributions, plots) | DONE |
| A | ≥3 loss functions with formulas | MISSING |
| A | Symmetry-penalising loss | MISSING |
| B | Data augmentation using identified symmetries | MISSING |
| B | Non-physical output prevention (masking) | MISSING |
| C1 | Working CNN trained and producing valid predictions | MISSING |
| C2 | Code snippets of key architectural elements | MISSING |
| C3 | Train + val loss curves with axis labels | MISSING |
| C3 | ≥1 anti-overfitting strategy shown working | MISSING |
| C4 | Quantitative symmetry comparison (with/without) | MISSING |
| C5 | CNN vs U-Net parameter efficiency comparison | MISSING |
| D | Kaggle submission generated via save_predictions_to_csv() | MISSING |
| D bonus | num_params() output showing ≤120,000 params | MISSING |
| E | Reproducibility seeds (torch + numpy) | DONE |
| E | DataLoader shuffle seeded | DONE |
| E | Student identity fields filled | MISSING (C9) |
| Workflow step 1 | Data exploration | DONE |
| Workflow step 2 | Preprocessing pipeline, v0, DataLoaders | DONE |
| Workflow step 3 | make_dim_hom() reusable function | DONE (cell ordering issue C3) |
| Workflow steps 4–13 | All remaining steps | MISSING |

---

## Recommended Next Steps

### Must-fix (grade impact)
1. **Implement Steps 4–13** in order per `docs/coding-workflow.md` — this unlocks every C and D rubric point.
2. **Fix cell ordering in Step 3** — move the Step 3 markdown cell before the code cell.

### Should-fix (quality / physics)
3. **Verify π₂ = ΔA/L² range** — print `(train_params['delta_A'] / train_params['L']**2).describe()` and add a sentence to the Step 3 markdown.
4. **Replace inline v0 in Step 2** with a `make_dim_hom()` call — eliminate the double-computation once Step 3 is reordered before Step 2 code.
5. **Add `assert (v0 > 0).all()`** before the division in Cell 15.
6. **Fill placeholder fields** in Cell 0.

---

## Rating

**Score: 1/5**
**Stars:** ⭐

| Score | Meaning |
|-------|---------|
| 5/5 | All rubric C/D sub-points implemented and correct |
| 4/5 | Working CNN + training + submission; minor gaps |
| 3/5 | CNN working; some C sub-points missing |
| 2/5 | Partial implementation; majority of steps present |
| 1/5 | Foundation only; majority of implementation missing |

**Justification:** All three passes independently reached 1/5. The notebook implements only Steps 1–3 (data loading, exploration, preprocessing, and the `make_dim_hom()` function) — roughly 15% of the required content. The foundation is genuinely high quality (correct physics, clean seeding, proper source attribution, no data leakage), but every rubric C sub-point and every rubric D requirement is absent. The score reflects the current state of implementation, not the quality of what exists.

---

## Commit Message

`feat(notebook): steps 1-3 — data exploration, preprocessing pipeline, make_dim_hom() with Buckingham-pi derivation`
