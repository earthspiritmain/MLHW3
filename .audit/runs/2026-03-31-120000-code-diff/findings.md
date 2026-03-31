---
run_id: 2026-03-31-120000-code-diff
tool: mlhw3-code-diff-audit-ensemble
passes: 5
created: 2026-03-31T12:00:00Z
---

# Ensemble Code Audit — Merged Findings

## Executive Summary

**The notebook is at Step 4 of 13 in the coding workflow.** All of rubric C and D are unimplemented. The foundation (Steps 1–4: data exploration, preprocessing, dimensional analysis, equivariant augmentation) is solid and physically correct. However, every deliverable that will be graded under rubric C and D is entirely absent.

Top risks:
- No CNN model, training loop, or loss function exists — rubric C.1, C.2, C.3 fully unmet
- No Kaggle submission generated — rubric D (1.5/10) entirely at risk
- `num_params()` never called — low-complexity bonus (0.5/10) cannot be claimed
- Kaggle loss E formula with ε not implemented anywhere
- No symmetry comparison (with/without hardwired symmetries) — rubric C.4 unmet
- No U-Net implementation — rubric C.5 unmet
- No experiment tracking (no run_id logs, no checkpoints, no loss plots)

Consistently found across all 5 passes: C1–C7 (see table). Singletons/minority: C11–C17.

Parameter count status: **Unknown** — no model defined yet.

---

## Merged Findings Table

| ID | Severity | Category | Finding | Consensus |
|----|----------|----------|---------|-----------|
| C1 | CRITICAL | Missing implementation | Steps 5–13 entirely absent. No CNN, no training loop, no loss function, no evaluation, no symmetry hardwiring, no U-Net, no parameter count, no submission. Notebook ends at Step 4 of 13. | 5/5 (strong) |
| C2 | CRITICAL | RubricD — Submission | `save_predictions_to_csv()` is never called. `submissions/` directory is empty. Rubric D requires ≥1 Kaggle submission — currently 0. | 5/5 (strong) |
| C3 | CRITICAL | RubricD — Bonus | `num_params()` is never called. Low-complexity bonus (0.5/10, requires ≤120,000 params evidenced) cannot be claimed. | 5/5 (strong) |
| C4 | CRITICAL | RubricC-1/Loss | Kaggle loss E formula (`mean(|pred − truth| / (truth + ε))`) is not implemented anywhere. No ε is defined. `rmsre()` from lab7 has not been adapted. | 4/5 (strong) |
| C5 | CRITICAL | RubricC-3 | No training visualization exists. No train/val loss curves plotted. No anti-overfitting strategy (dropout, weight decay, early stopping) is implemented in code. | 4/5 (strong) |
| C6 | CRITICAL | RubricC-4 | No symmetry comparison. No model with hardwired symmetries exists. No `GroupAvgModel` adapted from lab7. No symmetry metric computed or compared quantitatively. | 4/5 (strong) |
| C7 | CRITICAL | ExpTracking | No experiment tracking: no `run_id` constructed, no `experiments/logs/{run_id}.json` written, no `experiments/checkpoints/{run_id}_best.pt` saved, no `{run_id}_loss.png` in plots. Directories exist but are empty. | 3/5 (majority) |
| C8 | HIGH | Physics | No masking of non-physical outputs at closed pixels (input=0). Cell 13 identifies "multiply output by input mask" but the code never implements it. Model will predict non-zero flow at impermeable pixels. | 3/5 (majority) |
| C9 | HIGH | Reusable | None of the HIGH-PRIORITY reusable functions (Steps 5–13) have been adapted: `train_model()` from lab6, `rmsre()` from lab7, `create_model()` from lab7, `GroupAvgModel` from lab7, `plot_losses()` from lab6 are all absent. | 4/5 (strong) |
| C10 | HIGH | RubricC-5 | No U-Net implemented. No CNN vs U-Net parameter efficiency comparison. Rubric C.5 fully unmet. | 4/5 (strong) |
| C11 | MEDIUM | Attribution | `flip_v()` and `flip_hv()` lack source attribution comments (`# adapted from lab7: flip()`). Only `flip_h()` has it. | 2/5 (minority) |
| C12 | MEDIUM | Code quality | `make_dim_hom()` is defined redundantly in two cells (15 and 17) with slightly different forms. Increases maintenance risk and confuses readers. | 1/5 (singleton) |
| C13 | MEDIUM | Physics | The Buckingham group π₂ = ΔA/L² CV check is computed but only printed — its constancy is not asserted at runtime. If π₂ is NOT constant in the actual dataset, the planned input representation is incomplete. | 1/5 (singleton) |
| C14 | MEDIUM | MLHygiene | Device handling is deferred: cell 15 has a comment `# to device in the training loop` but no `.to(device)` calls exist anywhere. Risk of CPU/GPU mismatch when training loop is added. | 1/5 (singleton) |
| C15 | LOW | Submission | Cell 0 has placeholder text: `[Your name here]`, `[Your ID here]`, `[Your Kaggle username here]` — must be filled before final submission. | 1/5 (singleton) |
| C16 | LOW | MLHygiene | `torch.backends.cudnn.deterministic = True` not set. For full GPU reproducibility, this flag is needed alongside `torch.manual_seed()`. | 1/5 (singleton) |
| C17 | LOW | Physics | Augmentation is applied offline (pre-generated 4× dataset). This means each epoch sees the same 4,800 samples with no randomness in augmentation selection. Stochastic online augmentation would provide more variance. Minor design choice, not a correctness error. | 1/5 (singleton) |

---

## Rubric Coverage (Merged)

| Section | Sub-point | Status |
|---------|-----------|--------|
| C.1 | Working CNN trained, valid predictions | NOT PRESENT |
| C.2 | Code snippets of key architectural elements | NOT PRESENT |
| C.3 | Train+val loss curves; anti-overfitting strategy shown working | NOT PRESENT |
| C.4 | Symmetry comparison with/without hardwiring (quantitative) | NOT PRESENT |
| C.5 | CNN vs U-Net parameter efficiency comparison | NOT PRESENT |
| D | Kaggle submission CSV generated via `save_predictions_to_csv()` | NOT PRESENT |
| D-bonus | `num_params()` called, ≤120,000 evidenced | NOT PRESENT |
| Physics preprocessing | v₀ = ΔP·ΔA/(μ·L) normalisation | PRESENT AND CORRECT |
| Physics augmentation | Equivariant flip (G = Z2×Z2) applied to both input and label | PRESENT AND CORRECT |
| Seeds | `torch.manual_seed()` and `np.random.seed()` at notebook top | PRESENT AND CORRECT |
| Train/val split | Done before preprocessing, no data leakage | PRESENT AND CORRECT |
| DataLoaders | shuffle=True train, shuffle=False val | PRESENT AND CORRECT |
| Masking | Closed-pixel output masking | IDENTIFIED IN COMMENT, NOT IMPLEMENTED |
| Kaggle loss | E formula with ε | NOT PRESENT |
| Experiment dirs | `experiments/logs/`, `plots/`, `checkpoints/` created | PRESENT (directories only, empty) |

---

## Recommended Next Steps

### Must-fix (ordered by grade impact)

1. **C1 — Implement CNN (Step 5):** Adapt `create_model()` from lab7 for 32×64 grid. Add markdown explaining architecture choices (why these filter sizes, receptive fields). _Blocks everything else._
2. **C4 — Implement Kaggle loss E (Step 6):** Adapt `rmsre()` from lab7; formula is `mean(|pred − truth| / (truth + ε))` with ε in denominator added to ground truth.
3. **C5 — Implement training loop (Step 7):** Adapt `train_model()` from lab6; keep `model.train()/eval()`; add run_id, JSON log, checkpoint saving, `plot_losses()` with `plt.savefig`.
4. **C8 — Add output masking (Step 5 or forward pass):** Multiply model output by binary input cross-section to enforce q=0 at closed pixels.
5. **C5 (training viz) — Show overfitting + prevention (Step 9):** Implement one anti-overfitting strategy (dropout/weight decay/early stopping) and show it working in loss curves.
6. **C6 — Symmetry comparison (Step 10):** Adapt `GroupAvgModel` from lab7 for 32×64; train with/without; compare using symmetry metric.
7. **C10 — U-Net (Step 11):** Implement U-Net; compare parameter count and performance vs CNN.
8. **C3 — num_params() + bonus check (Step 12):** Run `num_params()` on submitted model; verify ≤120,000.
9. **C2 — Kaggle submission (Step 13):** Call `save_predictions_to_csv()` on hidden test predictions.

### Should-fix

10. **C11 — Add attribution comments** to `flip_v()` and `flip_hv()`.
11. **C12 — Remove duplicate `make_dim_hom()`** definition from cell 15; use only the function defined in cell 17.
12. **C15 — Fill student name/ID** placeholders in Cell 0.
13. **C14 — Add `.to(device)` calls** explicitly in the training loop when written (don't rely on the comment).

---

## Rating (Merged)

**Score: 2/5**

| Score | Meaning |
|-------|---------|
| 5 | Excellent — all rubric C/D deliverables present and correct |
| 4 | Good — most deliverables present, minor gaps |
| 3 | Adequate — working model exists, key comparisons missing |
| 2 | Poor — strong foundation but model implementation absent |
| 1 | Failing — little to no rubric content present |

**Justification:** All 5 passes independently scored 1–2/5. The notebook's foundation (Steps 1–4) is well-implemented and physically correct — seeds set, v₀ normalisation correct, equivariant augmentation applied to both input and label, no data leakage in the train/val split. However, the notebook is at Step 4 of 13 and the entire graded implementation section (rubric C and D) is absent. With 11 days until the deadline, Steps 5–13 must be completed. The 5-pass ensemble found unanimous agreement (5/5) on the three most critical gaps (C1–C3) and strong consensus (4/5) on four more (C4–C6, C9, C10).

---

## Commit Message

`feat(notebook): implement steps 5-13 — CNN, loss fn E with epsilon, training loop, overfitting prevention, symmetry hardwiring, U-Net, num_params, Kaggle submission`
