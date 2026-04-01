# Ensemble Code Audit — Steps 9–11 (POST-2-CONV-UNET-ADDITION)
**run_id:** 2026-04-01-120000-code-diff
**Scope:** steps 9–11 | **Passes:** 5 (physics, rubric, hygiene, teaching, tracking)

---

## Executive Summary

- **Root cause of all HIGH findings:** Cells 44–49 were just updated to add `UNet2ConvBackbone` and have not been executed. `ld_unet2`, `model_unet2`, `run_id_unet2` are undefined at runtime; `step11_reg_comparison.png` is absent. Cell 49 will crash with `NameError`. **Fix = run the notebook.**
- **One factual typo:** Cell 33 says "10 consecutive epochs" but `patience=20`. Two passes found this.
- **One silent API bug:** `UNet2ConvBackbone.__init__` accepts `use_batchnorm` but ignores it — BN always applied regardless. Low risk (both training calls use default `True`) but breaks the API contract.
- **Step 9 overfitting demo thin:** Neither model shows val divergence in current logs; early stopping never fires. Singleton finding but grade-relevant for rubric C.3.
- **Teaching mode gap:** No rubric citation (C.5) in cell 46; `# adapted from` absent at `MaskedUNet` class level.
- Parameter count status: CNN ~116k, UNet 1-conv ~58k, UNet 2-conv ~118k — **all under 120k cap** (architecture-verified).

---

## Merged Findings Table

| ID | Severity | Category | Finding | Consensus |
|----|----------|----------|---------|-----------|
| C1 | HIGH | Execution | Cells 44–49 unexecuted — `ld_unet2`/`model_unet2`/`run_id_unet2` undefined; cell 49 crashes with `NameError`; `step11_reg_comparison.png` absent on disk | 5/5 strong |
| C2 | MEDIUM | Rubric C.3 | Step 9 overfitting demo weak: neither `model_reg` nor `model_noreg` shows val divergence in logs; early stopping with `patience=20` never fires; "showcase effectiveness" claim is thin | 1/5 singleton |
| C3 | LOW | Bug | `UNet2ConvBackbone.__init__` accepts `use_batchnorm` parameter but `conv_block` hard-codes `nn.BatchNorm2d` unconditionally — flag silently ignored | 1/5 singleton |
| C4 | LOW | Documentation | Cell 33 markdown: `patience=20` described as "10 consecutive epochs" — factual error | 2/5 majority |
| C5 | LOW | Teaching mode | Cell 46 markdown (introduces UNet training runs) has no rubric citation for C.5 | 1/5 singleton |
| C6 | LOW | Teaching mode | `MaskedUNet` class in cell 45 missing `# adapted from MaskedCNNSoftplus (Step 9.2)` header comment; training call-site cells (36, 41, 47) have no `# adapted from lab6: train_model()` provenance comment | 2/5 majority |
| C7 | LOW | ML hygiene | `GroupAvgModel` training updates BatchNorm running stats 4× per real batch (once per group element) — mildly confounds the "identical conditions except GroupAvg" ablation claim in Step 10 | 1/5 singleton |

---

## Rubric Coverage (merged)

| Section | Sub-point | Status |
|---------|-----------|--------|
| C.3 | Training visualization + overfitting comment | PARTIAL — curves present, but no visible overfitting divergence; early stopping never fires |
| C.3 | At least one anti-overfitting strategy shown working | PARTIAL — L2 reg shows ~0.75% improvement but val never diverges |
| C.4 | Symmetry comparison quantitative (with vs without) | PASS — GroupAvg improves val 21%; SV metric present |
| C.5 | Parameter efficiency: CNN vs U-Net | BLOCKED by C1 — code correct but unexecuted |
| C.5 | Case made that U-Net is more efficient | BLOCKED by C1 |
| D bonus | num_params() output ≤120k evidenced | PARTIAL — CNN shown; UNet counts exist in code but cells unexecuted |

---

## Recommended Next Steps

### Must-fix (grade impact)
1. **[C1] Run the notebook** — execute cells 44–49. Once run, C1 resolves entirely and C.5 + D-bonus become PASS.
2. **[C4] Fix patience typo** — cell 33: change "10 consecutive" → "20 consecutive".

### Should-fix
3. **[C3] Fix `use_batchnorm` in `UNet2ConvBackbone`** — forward the flag to `conv_block` as `UNetBackbone` does.
4. **[C6] Add `# adapted from` comment** — add `# adapted from MaskedCNNSoftplus (Step 9.2)` before `MaskedUNet` class definition in cell 45.
5. **[C5] Add rubric citation to cell 46** — append "→ Satisfies rubric C.5 (parameter efficiency comparison)" to cell 46 heading.

### Accept / low priority
6. **[C2]** Step 9 overfitting demo — the data simply doesn't overfit strongly; the 0.75% improvement + train/val gap discussion is acceptable evidence. Consider mentioning in prose that the model capacity is well-matched to the dataset size, so strong overfitting is not observed.
7. **[C7]** BN 4× updates — cosmetic ablation confound; add a one-line comment in cell 41 if desired.

---

## Rating (merged)

**Score: 3.5/5** ⭐⭐⭐⭐

| Score | Meaning |
|-------|---------|
| 5/5 | No findings; cells executed end-to-end; all rubric points evidenced |
| 4/5 | Only LOW findings; cells executed |
| 3/5 | MEDIUM findings or unexecuted cells |
| 2/5 | HIGH findings in executed code |
| 1/5 | Multiple HIGH findings, broken execution |

**Justification:** The code architecture is correct and complete — skip connections, physics masking, GroupAvg, and 2-conv UNet are all implemented properly with no physics errors. The sole HIGH finding is that the notebook simply needs to be run; once executed, the rating immediately rises to 4–4.5/5. The MEDIUM finding (overfitting demo weakness) is a persistent structural concern since the dataset doesn't strongly overfit at C=40. Two LOW findings (patience typo, use_batchnorm silent ignore) require quick edits.

---

## Commit Message
`feat(notebook): steps 9-11 complete — UNet2Conv added, needs full re-run to produce step11_reg_comparison.png and all outputs`
