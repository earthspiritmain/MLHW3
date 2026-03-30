---
name: mlhw3-report-diff-audit
description: Single-pass read-only audit of changes to assignment3.tex. Checks rubric A–E coverage, lecture notes notation, figure quality, page limit, and language. Outputs structured review with star rating and suggested commit message. Use for pre-commit review or as subagent in ensemble.
argument-hint: "[optional focus notes] [Pass ID: k/N] [Lens: name]"
---

# Report Diff Audit — MLHW3

Audit the **current changes to `assignment3.tex`** and produce a structured review.

**Read-only — no writes.**

## Step 0 — Read these files first (mandatory, before getting the diff)

1. `assignment3.tex` — **every sentence**; this is what the report must satisfy
2. `docs/rubric.md` — structured A–E checklist; use it as your audit grid
3. `lecture notes.latex` — notation authority; check every formula against this
4. `template.tex` — IEEE structure reference
5. `CLAUDE.md` — hard constraints (page limit, figure rules)

## Safety

- Do not modify any file.
- Do not commit or stage anything.
- If fixes are needed, describe them and ask for permission.

## Get the changes

1. `git diff HEAD -- assignment3.tex` — staged and unstaged changes
2. If no git: read `assignment3.tex` in full and treat entire file as in scope.

## Read every file (mandatory)

- Read `assignment3.tex` in **full** (not diff-only). Every sentence matters.
- Read `assignment3.tex` (primary source — rubric and requirements) — always re-read.
- Read `lecture notes.latex` relevant sections (dimensional homogeneity, diagrammatic notation, CNNs, hydraulic cross-section review problem).
- Read `CLAUDE.md` notation reference and rubric summary for quick lookup.
- Read `template.tex` for IEEE structure reference.

## Audit checklist

Use `report-reviewer` agent logic. Check:

**Rubric A (physics):**
- [ ] Dimensional analysis with SI units for all variables (ΔP [Pa], L [m], μ [Pa·s], ΔA [m²], q [m/s])
- [ ] At least one learning problem in dimensionless form
- [ ] At least one learning problem in degree-1 homogeneous (scaling) form
- [ ] ALL symmetries identified (reflections left-right, up-down; rotations)
- [ ] Invariance vs equivariance distinction made correctly (q is a field → equivariance)
- [ ] Statistical dataset characterization with plots
- [ ] At least 3 loss functions, each criticized in physical terms
- [ ] At least 1 symmetry-penalizing loss function explicitly formulated

**Rubric B (network design):**
- [ ] Data augmentation strategy described using symmetries
- [ ] Disambiguation of symmetries addressed
- [ ] CNN/VGG design with receptive field computation (numbers)
- [ ] Limitations of CNN/VGG identified
- [ ] Fully convolutional NN considered and criticized
- [ ] U-Net considered and criticized, skip connections explained
- [ ] Architecture diagrams for each network
- [ ] Mathematical formalism for hardwiring finite symmetry groups
- [ ] Non-physical outputs identified and prevention strategies proposed

**Rubric C (implementation — in report context):**
- [ ] Code snippets for key architectural elements in `\lstlisting`
- [ ] Training loss curves present with axis labels
- [ ] Overfitting prevention strategy shown working
- [ ] Quantitative symmetry comparison (with vs without)
- [ ] Parameter efficiency comparison CNNs vs U-Nets

**Rubric D (Kaggle):**
- [ ] Kaggle score stated
- [ ] If claiming bonus: `num_params()` output shown, ≤120,000 confirmed

**Rubric E (quality):**
- [ ] Page limit ≤7 IEEE pages (count columns/pages)
- [ ] Section lengths are proportional to their score weight (see Page Budget below)
- [ ] Every figure has axis labels AND caption
- [ ] Introduction present (problem overview + performance)
- [ ] Conclusion present (sums up results)
- [ ] Language is scientific and grammatically correct
- [ ] Reproducibility: peer could reproduce results from report alone
- [ ] Bibliography present

**Notation (lecture notes compliance):**
- [ ] Homogeneous of degree 1: f(λx₁,...,λxₙ) = λ f(x₁,...,xₙ)
- [ ] Scaling function notation: S(·)
- [ ] ReLU: g(x) = max(x, 0)
- [ ] Equivariance and invariance used with correct definitions
- [ ] SI units correct ([m/s], [Pa], [Pa·s], [m²])
- [ ] Kaggle loss E formula matches assignment3.tex exactly

## Page Budget

The report must stay within **7 IEEE pages** (two-column format). IEEE two-column = ~2 columns per page = 14 columns total.

Reserve ~2 columns for overhead (title, abstract, intro, conclusion, references). That leaves **12 content columns** for sections A–D. Section E is a quality criterion, not a separate section.

Target allocation based on score weight (A:B:C:D = 2:2.5:2.5:2 = 9 rubric points):

| Section | Score | Weight | Target columns | Target pages |
|---------|-------|--------|---------------|--------------|
| A | 2/10 | 22% | ~2.7 col | ~1.3 pages |
| B | 2.5/10 | 28% | ~3.3 col | ~1.7 pages |
| C | 2.5/10 | 28% | ~3.3 col | ~1.7 pages |
| D | 2/10 | 22% | ~2.7 col | ~1.3 pages |

**Check each section:** estimate its actual column count (count text blocks + figures), compare to target. Flag any section that is >50% over budget (bloated) or <50% of budget (too thin). A section that is thin but hits all rubric points is acceptable; flag it as a space opportunity.

## Output format

### Change Summary
[What changed in the report]

### Analysis
[Detailed breakdown — which rubric points now pass/fail, notation issues found]

### Bugs Found
[Factual errors, wrong formulas, wrong physics — or **None.** if clean]

### Rubric Coverage
| Section | Sub-point | Status |
|---------|-----------|--------|

### Notation Issues
[List deviations with suggested fix — or **None.**]

### Figure Issues
[Missing axis labels or captions — or **None.**]

### Section Length vs Budget
| Section | Score | Target cols | Estimated cols | Status |
|---------|-------|-------------|---------------|--------|
| A | 2/10 | ~2.7 | ? | OVER/OK/THIN |
| B | 2.5/10 | ~3.3 | ? | OVER/OK/THIN |
| C | 2.5/10 | ~3.3 | ? | OVER/OK/THIN |
| D | 2/10 | ~2.7 | ? | OVER/OK/THIN |
| Overhead (intro/concl/refs) | — | ~2.0 | ? | — |
| **Total** | — | **≤14** | ? | PASS/FAIL |

Flag OVER if estimated > 1.5× target. Flag THIN if estimated < 0.5× target AND rubric points are missing.

---

## Rating (mandatory)

**Score: X/5**  **Stars:** [⭐ glyphs, e.g. ⭐⭐⭐⭐☆ for 4/5]

**Justification:** [1–4 sentences tying score to rubric coverage]

| Score | Meaning |
|-------|--------|
| ⭐⭐⭐⭐⭐ 5/5 | Perfect — all rubric points, notation exact, no issues |
| ⭐⭐⭐⭐ 4/5 | Good — minor gaps or notation deviations |
| ⭐⭐⭐ 3/5 | Acceptable — some rubric points missing |
| ⭐⭐ 2/5 | Needs work — significant rubric misses |
| ⭐ 1/5 | Major issues — multiple required sections missing |
| 0/5 | Do not submit — broken, major physics errors |

---

## Commit Message

```text
docs(report): description
```

Single line, conventional commits format. Do not actually commit.

---

## Ensemble / Pass ID

If Pass ID / Lens was given, echo at the top. Use issue IDs R1, R2, … in findings.
