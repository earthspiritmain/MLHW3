# Ensemble Code Audit — Steps 1 & 2
**Run ID:** 2026-03-30-120000-code-diff
**Tool:** mlhw3-code-diff-audit-ensemble
**Passes:** 5 (Physics | Rubric C/D | ML Hygiene | Teaching Mode | Experiment Tracking)
**Scope:** assignment3.ipynb Steps 1–2 only

---

## Executive Summary

Top risks:
- **[C1 CRITICAL]** `TensorData` adaptation drops the `device` parameter from lab6 but `# changes:` comment falsely says "no change to interface" — latent GPU training crash
- **[C2 CRITICAL]** v₀ = ΔP·ΔA/(μ·L) as a collapsing scale is asserted without Buckingham-π derivation or O(1) empirical check — if q/v₀ doesn't actually collapse, all training suffers
- **[C3 MAJOR]** `torch.manual_seed(SEED)` called a second time inside the split cell — mid-notebook RNG reset makes model init seed execution-path dependent
- **[C4 MAJOR]** "q scales linearly with ΔA" stated as fact in markdown without derivation
- **[C5 MAJOR]** Labels are (N,32,64); network will output (N,1,32,64) — shape mismatch in loss unless handled explicitly
- **[C6 MINOR]** Missing `# changes:` line in TensorData adaptation (confirmed by 2 passes)
- **[C7 MINOR]** `np.random.seed(SEED)` re-called mid-notebook in Step 1 visualization cell (confirmed by 2 passes)

**Consistently found (≥2 passes):** C1 (device drop), C6 (missing changes comment), C7 (mid-notebook reseed)
**Singletons needing confirmation:** C2 (v₀ collapse), C3 (double manual_seed), C4 (ΔA scaling claim), C5 (label shape)

**Parameter count status:** No model yet — N/A.

---

## Merged Findings Table

| ID | Severity | Category | Finding | Consensus |
|----|----------|----------|---------|-----------|
| C1 | CRITICAL | Reusable function adaptation | `TensorData` in cell-15 drops the `device` parameter present in the lab6 original. The `# changes:` comment reads "no change to interface" — factually incorrect. When GPU training is introduced in Step 7, all DataLoader batches will be on CPU unless `.to(device)` is added manually in the training loop. Comment mismatch is also a rubric-E reproducibility concern. | 2/5 — Majority |
| C2 | CRITICAL | Physics validation | v₀ = ΔP·ΔA/(μ·L) is dimensionally correct [m/s] but the claim that q/v₀ is O(1) across all 1500 samples is asserted without a Buckingham-π derivation or an empirical printout confirming the range is tight. If the normalisation doesn't collapse the data, all downstream training is poorly scaled. | 1/5 — Singleton |
| C3 | MAJOR | ML hygiene | `torch.manual_seed(SEED)` is called again inside cell-15 immediately before `torch.randperm`. This re-pins the PyTorch RNG mid-notebook. The split is reproducible, but model weight initialisation (Step 5) will start from the RNG state produced by `randperm` operations, not from a clean top-of-notebook state. Reproducibility depends on execution path. | 1/5 — Singleton |
| C4 | MAJOR | Physics explanation | Markdown cell-14 states "q scales linearly with … ΔA" as a fact derived from Darcy's law. The assignment tex does not state this functional form — it only lists ΔA as a parameter. The claim needs a derivation or citation. | 1/5 — Singleton |
| C5 | MAJOR | Shape mismatch risk | Labels tensor is `(N, 32, 64)` (no channel dim). The CNN will output `(N, 1, 32, 64)`. Unless the loss function or training loop explicitly squeezes the prediction, a shape broadcast error will occur in Step 6. Should be documented in the Step 2 markdown or handled in Step 6. | 1/5 — Singleton |
| C6 | MINOR | Attribution comment | `TensorData` adaptation comment is `# adapted from lab6: TensorData` but is missing the required `# changes:` line. The template in `docs/reusable-functions.md` explicitly requires it even if there are no changes. | 2/5 — Majority |
| C7 | MINOR | Reproducibility | `np.random.seed(SEED)` is re-called in cell-6 before `np.random.choice`. This is intentional (pin display samples) but re-sets the global NumPy RNG mid-notebook. Comment explaining the intent is missing. | 2/5 — Majority |
| C8 | MINOR | Teaching mode | Magic numbers with no prose justification: `BATCH_SIZE = 32` (no explanation of batch size trade-off), `0.8` split ratio (no justification vs 90/10), histogram bin counts `bins=40/80/60/50`. | 1/5 — Singleton |
| C9 | MINOR | Style | Bold mid-sentence in running prose in cell-5: "The flow field is **zero wherever the pixel is closed**". CLAUDE.md bans bold inside running paragraphs. | 1/5 — Singleton |
| C10 | MINOR | Physics / future bug | No mask tensor (`inputs == 1`) is created and stored alongside training data. The masking of closed pixels will need to happen in the model (Step 5) — should be flagged in the Step 2 summary for continuity. | 1/5 — Singleton |

### Not-yet-implemented gaps (expected, not bugs)
These are rubric C/D requirements that are pending future steps — not defects in what is currently implemented:
- CNN baseline (Step 5), loss function (Step 6), training loop (Step 7), overfitting prevention (Step 9), symmetry comparison (Step 10), U-Net (Step 11), param count (Step 12), Kaggle submission (Step 13)
- Hidden test v₀ computation (needed at Step 13)

---

## Rubric Coverage (merged)

| Section | Sub-point | Status |
|---------|-----------|--------|
| A.1 | Dimensional analysis — SI units, dimensionless form, homogeneous form | Partial — v₀ formula present in code (Step 2), full derivation pending Step 3 |
| A.2 | Symmetries identified | Mentioned in markdown (cell-5, cell-13) — formal treatment pending Step 4 |
| A.3 | Dataset characterisation — distributions, example plots | **Done** — Steps 1.1–1.4 complete |
| A.4 | ≥3 loss functions with physical criticism | Not yet |
| A.5 | Symmetry-penalizing loss | Not yet |
| B.1 | Data augmentation strategy | Not yet (Step 4) |
| B.2–7 | CNN/U-Net design, diagrams, symmetry hardwiring | Not yet |
| C.1 | Working CNN | Not yet (Step 5) |
| C.2 | Code snippets in report | Not yet |
| C.3 | Training viz + anti-overfitting | Not yet (Steps 7–9) |
| C.4 | Symmetry comparison | Not yet (Step 10) |
| C.5 | Parameter efficiency comparison | Not yet (Step 11–12) |
| D | Kaggle submission | Not yet (Step 13) |
| E | Seeds set | **Done** ✓ |
| E | Experiment dirs created | **Done** ✓ |
| E | Plots saved with axis labels | **Done** ✓ |

---

## Recommended Next Steps

### Must-fix before Step 3
1. **[C1]** Fix `TensorData` `# changes:` comment — change to `# changes: removed device param — tensors moved to device in training loop` (or restore device param)
2. **[C2]** Add empirical O(1) check: after printing `q/v0` stats, assert or comment that the range is tight (e.g. `[0, ~1]`). Or add a Buckingham-π note to the Step 3 dimensional analysis cell.
3. **[C6]** Add `# changes:` line to `TensorData` adaptation.

### Should-fix before Step 5 (training)
4. **[C3]** Remove or justify the second `torch.manual_seed(SEED)` in the split cell — use a comment if intentional, or remove it and rely on the top-of-notebook seed.
5. **[C5]** Add one sentence in cell-14 markdown explaining the label shape convention (3D vs 4D) and how the training loop will handle the mismatch.
6. **[C4]** Add derivation or citation for "q scales linearly with ΔA" in the Step 2 markdown.

### Nice-to-fix
7. **[C7]** Add comment to cell-6: `# re-seed here to pin display samples to same 6 indices every run`
8. **[C8]** Add one-sentence justifications for `BATCH_SIZE=32` and `0.8` split ratio in cell-14 prose.
9. **[C9]** Remove bold from mid-sentence in cell-5.
10. **[C10]** Add note in Step 1.5 summary about mask tensor strategy for Step 5.

---

## Rating (merged)

**Score: 3/5** ⭐⭐⭐

| Score | Meaning |
|-------|---------|
| 5 | No issues |
| 4 | Minor issues only |
| 3 | 1–2 major issues or 1 critical |
| 2 | Multiple major issues |
| 1 | Critical failure in multiple areas |

**Justification:** Across 5 passes (Physics 3/5, Rubric C/D 3/5, ML Hygiene 3/5, Teaching Mode 4/5, Experiment Tracking 3/5), the aggregate score is 3.2/5 → 3/5. Steps 1 and 2 are structurally sound: data loading is correct, per-sample v₀ normalisation avoids leakage, the train/val split is reproducible, DataLoader shapes are correct, and all 4 exploration plots are saved with axis labels. The score is held at 3 by one confirmed critical bug (C1: device parameter dropped with wrong comment) and a plausible-but-unverified critical physics claim (C2: v₀ collapse). The two major hygiene issues (C3 double-reseed, C5 label shape mismatch) are latent bugs that will surface in Steps 5–7 if not addressed now.

---

## Commit Message

`feat(notebook): add Steps 1-2 — data exploration and v0-normalised preprocessing pipeline`
