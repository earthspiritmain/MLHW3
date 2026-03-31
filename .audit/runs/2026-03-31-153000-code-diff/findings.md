# Ensemble Code Audit — Steps 1–4 (Scoped)
**Run ID:** 2026-03-31-153000-code-diff
**Tool:** mlhw3-code-diff-audit-ensemble (N=5)
**Scope:** steps-1-4
**Date:** 2026-03-31

---

## Executive Summary

**Top risks (within steps 1–4 scope):**
- **C1 (HIGH):** `make_dim_hom()` is defined in Step 3 and attributed correctly, but the DataLoaders built in Step 2 use an inline `v0` — the function is decorative and does not drive the pipeline.
- **C2 (MEDIUM):** The π₂ = ΔA/L² branch is print-only. If CV ≥ 1% at runtime, no code path injects π₂ as a network input; the warning is silent and the pipeline continues unchanged.
- **C3 (MEDIUM):** `train_loader` and `train_dataset` are rebound in-place in cell 19. No naming guard or assertion protects against out-of-order cell execution.
- **C4 (MEDIUM):** Offline augmentation pre-generates all 4 group elements for all 1200 training samples. A mini-batch can contain all four orientations of the same original sample simultaneously, reducing effective within-batch diversity.
- **C5 (MEDIUM):** 90-degree rotations are excluded (physics correct, grid non-square) but the explanation understates the consequence: only the Klein four-group V₄ is used; the Z₄ rotation subgroup is entirely omitted without quantifying coverage loss.
- **C9 (LOW):** Steps 2, 3, and 4 markdown cells contain no explicit rubric sub-point reference, preventing a reader from mapping code to assessment criteria.
- **C10 (LOW):** Step 4 explanation is silent on disambiguation (how symmetry ties in labels are broken), which is a required component of rubric B.1.

**Consistently found (≥ 2 passes):** C1, C2, C4, C5, C9, C10
**Singletons (need confirmation before acting):** C3, C6, C7, C8

**Parameter count status:** Not yet applicable — no model implemented in steps 1–4.

---

## Merged Findings Table

| ID | Severity | Category | Finding | Consensus |
|----|----------|----------|---------|-----------|
| C1 | HIGH | Reusable functions / pipeline | `make_dim_hom()` is defined in Step 3 with correct formula and lab4 attribution, but the DataLoaders created in Step 2 use an inline `v0` computed before the function exists. A cross-check assertion confirms the values match, but the function never replaces the inline value as the pipeline driver. A reader tracing DataLoader → normalization will find the function is decorative. | 2/5 (Majority) |
| C2 | MEDIUM | Physics — dimensional analysis | π₂ = ΔA/L² is computed and its CV is checked. The `if pi2_cv < 1.0` branch only prints a decision; it does not programmatically modify the pipeline. If CV ≥ 1% on a different dataset, the notebook silently continues with the same input representation as if π₂ were constant. | 3/5 (Majority) |
| C3 | MEDIUM | ML hygiene — reproducibility | Cell 19 rebinds `train_loader` and `train_dataset` in-place, overwriting the non-augmented objects from cell 15. No naming distinction (e.g., `train_loader_aug`) and no assertion guard against out-of-order execution. | 1/5 (Singleton) |
| C4 | MEDIUM | Augmentation design | Offline pre-generation concatenates all 4 group elements per training sample into a flat (4800,…) tensor before training. A mini-batch can contain all four orientations of the same original sample simultaneously, providing no within-batch diversity for that sample. Online stochastic augmentation (random group element per sample per epoch inside `__getitem__`) avoids this. | 2/5 (Majority) |
| C5 | MEDIUM | Physics — symmetry coverage | 90-degree rotations are excluded because `torch.rot90` on a 32×64 tensor produces a 64×32 tensor incompatible with the fixed CNN input. This is physically justified and documented. However, the markdown does not state which subgroup is covered (V₄ ≅ Z₂×Z₂) nor what fraction of the full symmetry group is used, leaving a reader without a clear picture of coverage. | 2/5 (Majority) |
| C6 | MEDIUM | Physics — Stokes assumption | `v0 = ΔP·ΔA/(μ·L)` is presented as the unique degree-1 combination in [m/s]. The derivation is correct but does not state the physical assumption it encodes: that q is linear in ΔP/L and ΔA/μ (Stokes/Darcy regime). The argument is presented as purely dimensional, overstating its generality. | 1/5 (Singleton) |
| C7 | MEDIUM | ML hygiene — seeds | `np.random.seed(SEED)` is re-called inline in cells 6 and 19 for visualization reproducibility. These mid-notebook re-calls reset the global NumPy random state and can mask reproducibility issues in later training steps. The top-of-notebook seed should be sufficient. | 1/5 (Singleton) |
| C8 | LOW | Teaching mode — redundancy | The Buckingham π derivation (v0 formula + dimensional verification) appears in full in both Step 2 markdown (cell 14) and Step 3 markdown (cell 16). The second occurrence should reference the first or be condensed. | 1/5 (Singleton) |
| C9 | LOW | Teaching mode — rubric references | Steps 2, 3, and 4 markdown cells do not name the rubric sub-point they satisfy. Step 3 satisfies rubric A.1 (dimensionless form); Step 4 satisfies rubric B.1 (augmentation). A reader cannot map code sections to assessment criteria without these labels. | 3/5 (Majority) |
| C10 | LOW | Teaching mode — disambiguation gap | Step 4 explains equivariant augmentation with the Klein four-group but makes no mention of disambiguation — how to break symmetry ties in labels during training. Rubric B.1 requires both augmentation AND disambiguation. The notebook is silent on whether it is needed here and why. | 2/5 (Majority) |

---

## Rubric Coverage (Steps 1–4)

| Section | Sub-point | Status |
|---------|-----------|--------|
| A.1 — Dimensional analysis | v0 = ΔP·ΔA/(μ·L) derived and verified | PASS |
| A.1 — Dimensional analysis | Second π group (ΔA/L²) verified as near-constant | PASS (latent gap: no code fallback — C2) |
| A.1 — Dimensional analysis | `make_dim_hom()` adapted from lab4 and attributed | PARTIAL — function exists but doesn't drive pipeline (C1) |
| A.2 — Symmetries (observation) | Equivariance noted in Step 1; Klein four-group applied in Step 4 | PASS (C5: Z₄ rotations underdiscussed) |
| A.3 — Dataset characterisation | Load + visualise cross-sections, flow fields, parameter distributions, porosity | PASS |
| B.1 — Data augmentation | Equivariant flip applied to both input AND label | PASS |
| B.1 — Disambiguation | How symmetry ties in labels are broken | MISSING (C10) |
| Step 2 — Preprocessing | 80/20 train/val split with seed; no data leakage | PASS |
| Step 2 — Preprocessing | PyTorch TensorData Dataset + DataLoader | PASS |
| Step 2 — Preprocessing | Val set excluded from augmentation | PASS |
| Step 4 — Augmentation | Visual equivariance verification plot with axis labels | PASS |
| Step 4 — Augmentation | 90-degree rotations | PARTIAL — excluded with physics justification (C5) |
| Rubric E — Seeds | `torch.manual_seed()` + `np.random.seed()` at notebook top | PASS |
| Rubric E — Device | `device = torch.device(…)` set at top | PASS |
| Experiment tracking | Exploration and analysis plots saved to `experiments/plots/` | PASS |
| Experiment tracking | Timestamped run-ID naming | N/A — no training runs in steps 1–4 |
| Experiment tracking | JSON logs, checkpoints | N/A — no training runs in steps 1–4 |

---

## Recommended Next Steps

### Must-fix (grade impact, ordered)
1. **C1** — Wire `make_dim_hom()` into the Step 2 pipeline: recompute `v0` using the function after it is defined, then rebuild the tensors and DataLoaders. This ensures the catalog's reusable function actually drives the normalization.
2. **C10** — Add a paragraph in Step 4 markdown explaining disambiguation: since `q(flip(x)) = flip(q(x))`, the flipped label is unambiguous and no disambiguation is needed. State this explicitly to satisfy rubric B.1.
3. **C9** — Add a one-line rubric reference to Steps 2, 3, and 4 markdown cells (e.g., `→ Satisfies rubric A.1` or `→ Report Section B`).

### Should-fix (quality / robustness)
4. **C2** — Add a code path that raises an error (or explicitly flags) if CV ≥ 1%, not just a print statement. The warning must alter the pipeline or at minimum halt execution.
5. **C3** — Rename augmented objects to `train_loader_aug` / `train_dataset_aug`, or add an assertion early in any downstream cell that depends on augmentation being active.
6. **C4** — Consider switching to online augmentation inside `TensorData.__getitem__`. If offline pre-generation is kept, add a comment explaining the trade-off (batch diversity vs. memory simplicity).
7. **C5** — Add one sentence to Step 4 markdown naming the symmetry group used (V₄ ≅ Z₂×Z₂) and the subgroup excluded (Z₄ rotations), with a brief note on why grid shape prevents its inclusion.

### Nice-to-have
8. **C6** — Add one sentence to Step 3 justifying the linearity assumption (Stokes/Darcy regime) that makes v0 the correct scaling.
9. **C7** — Remove mid-notebook `np.random.seed(SEED)` re-calls in cells 6 and 19.
10. **C8** — Condense the duplicate Buckingham π derivation in Step 3 to a cross-reference to Step 2.

---

## Rating

- **Score: 4/5**
- **Stars:** ⭐⭐⭐⭐

| Score | Meaning |
|-------|---------|
| 5/5 | All steps correct, clean ML hygiene, full teaching mode, all rubric sub-points addressed |
| 4/5 | All steps present and physically correct; minor structural or teaching-mode gaps |
| 3/5 | Steps present but with significant physics or hygiene errors |
| 2/5 | One or more steps missing or fundamentally incorrect |
| 1/5 | Fewer than two steps completed |

**Justification:** All five passes converged at 4/5. Steps 1–4 are all implemented with correct physics: equivariant flips are applied identically to both input and label, the v0 normalisation formula is dimensionally correct, the 80/20 split has no data leakage, plots are saved to `experiments/plots/`, and source attribution is present on all adapted functions. The one-star deduction comes from two actionable structural issues found by majority consensus — `make_dim_hom()` not driving the pipeline (C1, HIGH) and the missing disambiguation discussion in Step 4 (C10, LOW) — plus the consistent rubric-reference gap (C9) across three passes. No critical correctness errors exist within the steps-1-4 scope.

---

## Commit Message

`feat(notebook): implement steps 1-4 — data exploration, preprocessing, dimensional analysis, equivariant augmentation`
