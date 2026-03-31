# Ensemble Code Audit — Steps 5–7 | 2026-03-31-180000-code-diff

**Scope:** steps-5-7 (Baseline CNN, Loss function, Training loop)
**Passes:** 5 (Physics correctness, Rubric C/D, ML hygiene, Teaching mode, Experiment tracking)

---

## Executive Summary

**Top risks:**

1. **Step 7 (training loop) is entirely absent** — the single most critical finding, found by all 5 passes at CRITICAL/HIGH severity. No `train_model()`, no `model.train()`/`model.eval()`, no optimizer, no backward pass, no checkpoint saving, no JSON log, no loss curve. The model is defined but has never been trained.
2. **No experiment tracking artifacts** — `experiments/logs/`, `experiments/checkpoints/`, `experiments/plots/` are empty. The `run_id` naming convention is not applied anywhere.
3. **No Kaggle submission CSV** — `save_predictions_to_csv()` is never called. No submission exists.
4. **Negative flow at open pixels not prevented** — no output activation (Softplus deferred); documented gap but live physics violation.
5. **Loss instability risk** — `|pred - truth| / (truth + ε)` with ε=1e-6 can spike massively for over-predictions at near-zero-ground-truth pixels.
6. **Epsilon applied to dimensionless labels** — subtle: the loss computes `|q_norm - pred_norm| / (q_norm + ε)`, not `|q - pred| / (q + ε)`. Numerically equivalent only if v0 is constant across samples (it isn't). Low-severity but worth noting.
7. **Receptive field not computed** in Step 5 teaching cell (rubric B requirement bleeds into C).

**Consistently found vs. singleton:**
- Step 7 absent: **5/5 passes** — highest confidence finding
- No experiment tracking: **3/5 passes** (passes 2, 3, 5)
- Negative flow at open pixels: **2/5 passes** (passes 1, 4) — Majority
- Loss epsilon instability: **2/5 passes** (passes 1, 2) — Majority
- Receptive field missing: **1/5** (pass 4) — Singleton, needs confirmation
- Epsilon dimensionless mismatch: **2/5 passes** (passes 1, 2) — Majority

**Parameter count status:** ~18,600 parameters at C=16 — well within ≤120,000 bonus threshold. Not yet confirmed with executed cell output.

---

## Merged Findings Table

| ID | Severity | Category | Finding | Consensus |
|----|----------|----------|---------|-----------|
| C1 | CRITICAL | Step 7 absent | Training loop entirely missing from notebook. No `train_model()`, no `model.train()`/`model.eval()`, no optimizer, no loss backward, no epoch loop. Model defined but never trained. | 5/5 |
| C2 | CRITICAL | Experiment tracking | Zero experiment tracking artifacts: `experiments/logs/` empty (no JSON), `experiments/checkpoints/` empty (no `.pt`), `experiments/plots/` has no run-named loss curve. `run_id` naming convention never applied. | 3/5 |
| C3 | HIGH | Kaggle submission | `save_predictions_to_csv()` never called. No submission CSV generated. Consequence of C1. | 2/5 |
| C4 | HIGH | Physics — non-physical outputs | No output activation: negative flow predictions possible at open pixels. Deferred to overfitting step and documented, but remains a live physics violation. | 2/5 |
| C5 | HIGH | Loss instability | `|pred - truth| / (truth + ε)` with ε=1e-6: for open pixels with very small ground-truth flow, large positive over-predictions produce loss ≈ `large / 1e-6`. No training instability guard (gradient clipping, loss clamping) exists. Will only manifest at training time. | 2/5 |
| C6 | MEDIUM | Symmetry comparison | No symmetry comparison possible (no training). No model-with-symmetry vs model-without-symmetry code. Consequence of C1, but flagged separately since it requires separate design effort beyond just adding Step 7. | 2/5 |
| C7 | MEDIUM | Loss epsilon dimensionless | Loss operates on normalised `q/v0` labels. With `v0 = ΔP·ΔA/(μ·L)` varying per sample, `q_norm + ε` ≠ `q + ε` scaled by 1/v0. For samples with large v0, ε is negligible; for small v0, ε dominates. Numerically non-identical to Kaggle evaluation formula. | 2/5 |
| C8 | MEDIUM | Teaching — receptive field | Step 5 markdown describes layer shapes but never computes receptive field growth across the 3 encoder blocks. Rubric B.2 explicitly requires receptive field numbers; the notebook teaching cell should include or reference this. | 1/5 (singleton) |
| C9 | LOW | ML hygiene — comment | `model.eval()` in smoke test (cell 21) has comment "important once BN/Dropout layers are added" — current architecture has neither, making the comment misleading about current functional state. | 1/5 (singleton) |
| C10 | LOW | Architecture fragility | `nn.Flatten(start_dim=1, end_dim=2)` assumes dim-1 has size 1. Correct for current 1×1 final conv, but fragile if channel count changes. No comment explaining this assumption. | 1/5 (singleton) |

---

## Rubric Coverage (Steps 5–7)

| Section | Sub-point | Status |
|---------|-----------|--------|
| C.1 | Working CNN — architecture defined | PARTIAL — defined and smoke-tested, not trained |
| C.1 | Baseline VGG-like CNN adapted from lab7 | DONE |
| C.1 | Physics mask (q=0 at closed pixels) | DONE — `MaskedCNN` wrapper correct |
| C.1 | Output shape (N,1,32,64) | DONE — verified by assertion |
| C.2 | Code snippets of key elements | DONE — architecture shown in full |
| C.3 | Training visualization (loss curves, axis labels) | MISSING — Step 7 absent |
| C.3 | At least one anti-overfitting strategy shown working | MISSING — Step 7 absent |
| C.4 | Symmetry comparison — quantitative metric | MISSING — no training |
| C.5 | CNN vs U-Net parameter efficiency | MISSING — no U-Net, no training |
| D (bonus) | ≤120,000 params evidenced with `num_params()` | PARTIAL — ~18,600 at C=16 but cell not executed in saved state |
| D | `save_predictions_to_csv()` called | MISSING |
| Step 5 | `create_model()` adapted, source cited | DONE |
| Step 5 | `num_params()` called | DONE |
| Step 6 | `kaggle_loss()` matches Kaggle E formula | DONE |
| Step 6 | ε included, source adaptation cited | DONE |
| Step 6 | Sanity checks (3 test cases) | DONE |
| Step 7 | `train_model()` adapted from lab6 | MISSING |
| Step 7 | `model.train()` / `model.eval()` | MISSING |
| Step 7 | Checkpoint saved to `experiments/checkpoints/` | MISSING |
| Step 7 | JSON log saved to `experiments/logs/` | MISSING |
| Step 7 | Loss curve saved to `experiments/plots/` | MISSING |
| Step 7 | `run_id` naming convention | MISSING |

---

## Recommended Next Steps

### Must-fix (grade-blocking):
1. **Implement Step 7** — adapt `train_model()` from lab6; add `model.train()`/`model.eval()`, checkpoint saving, JSON log, `run_id` naming. This unblocks everything else.
2. **Execute the training run** — only after Step 7 exists can C3 (Kaggle), C4 (overfitting), C6 (symmetry comparison) be addressed.
3. **Run `save_predictions_to_csv()`** — generate at least one Kaggle submission CSV.

### Should-fix (grade-affecting):
4. **Add gradient clipping or loss clamping** — guard against C5 loss spikes during early training.
5. **Execute `num_params()` cell** — persist the output in the saved notebook to evidence the bonus.
6. **Add Softplus output activation** (or deferral explanation in training cell) — address C4 non-physical outputs.
7. **Document epsilon choice** in Step 6 markdown — why 1e-6 relative to typical q_norm scale.

### Nice-to-fix (teaching quality):
8. **Add receptive field calculation** to Step 5 markdown — 3 lines of arithmetic, directly addresses rubric B.2.
9. **Fix misleading `model.eval()` comment** (C9).
10. **Add fragility comment** to `Flatten` call (C10).

---

## Rating

**Score: 2/5**
**Stars:** ⭐⭐

| Score | Meaning |
|-------|---------|
| 5/5 | All steps complete, no significant issues |
| 4/5 | Minor gaps only |
| 3/5 | One step with issues, core functionality present |
| 2/5 | One full step missing, core deliverable incomplete |
| 1/5 | Multiple steps missing or broken |

**Justification:** Steps 5 (Baseline CNN) and 6 (Loss function) are solidly implemented — correct physics mask, properly adapted loss formula with citation, equivariant V4 augmentation, ~18,600 params well within the bonus limit, and thorough seeds/device handling. However, Step 7 (the training loop) is entirely absent from the notebook, and this is the step that gates all core rubric C deliverables: training visualization, overfitting prevention, symmetry comparison, and Kaggle submission. The consensus across all 5 passes is unanimous. Two of three in-scope steps are done; one is completely missing.

---

## Commit Message

`feat(notebook): implement step-7 training loop with run_id tracking, model.train/eval, JSON log, checkpoint, and loss-curve plot`
