# Coding Workflow

## Step-by-step order

Each step = one approval cycle: explain → student says go → implement → verify output → next step.

1. **Data exploration** — load and visualize cross-sections and flow fields, print dataset statistics
2. **Preprocessing pipeline** — load npy + csv, normalize, train/val split, PyTorch Datasets and DataLoaders
3. **Dimensional analysis** — compute dimensionless/scaling variables from (ΔP, L, μ, ΔA); adapt `make_dim_hom()` from lab4
4. **Data augmentation** — equivariant flip and rotation (apply to input AND label); adapt `flip()`, `rot()` from lab7
5. **Baseline CNN** — adapt `create_model()` from lab7 for 32×64 grid
6. **Loss function** — implement Kaggle's E formula with ε; adapt `rmsre()` from lab7
7. **Training loop** — adapt `train_model()` from lab6; add checkpoint + JSON log saving
8. **Evaluation and plotting** — loss curves saved to `experiments/plots/`; prediction visualizations
9. **Overfitting prevention** — implement and demonstrate at least one strategy
10. **Symmetry enforcement** — adapt `GroupAvgModel` from lab7 for 32×64; compare with/without
11. **U-Net design** — design and implement two variants: 1-conv U-Net (C=16, ~58k params) and 2-conv U-Net (C=16, ~118k params). Compare all three models (CNN, UNet1, UNet2) in a single 1×2 figure (val loss curves + param scatter). Both UNet training runs use `save_plot=False`; combined figure is the report figure.
12. **Parameter count** — run `num_params()`; verify ≤120,000 for bonus
13. **Kaggle submission** — run `/mlhw3-kaggle-submit`

---

## Experiment tracking convention

Every training run must save:

```python
import json, os, time

run_id = f"{model_name}_{time.strftime('%Y%m%d_%H%M%S')}"
log_path    = f"experiments/logs/{run_id}.json"
plot_path   = f"experiments/plots/{run_id}_loss.png"
ckpt_path   = f"experiments/checkpoints/{run_id}_best.pt"

# After training:
with open(log_path, 'w') as f:
    json.dump(loss_dict, f)
plt.savefig(plot_path, dpi=150, bbox_inches='tight')
torch.save(model.state_dict(), ckpt_path)
```

Naming: `{model_name}_{YYYYMMDD_HHMMSS}` — e.g. `cnn_baseline_20260330_143022`

---

## Notation reference (from lecture notes.latex)

Use these in ALL report writing:

- **Homogeneous of degree 1:** f(λx₁,...,λxₙ) = λ f(x₁,...,xₙ) for all λ > 0
- **Scaling function:** S(·) — degree-1 homogeneous function
- **ReLU:** g(x) = max(x, 0) — not "relu" or "σ"
- **Invariance:** scalar output unchanged under transformation T
- **Equivariance:** field output transforms with input under T (applies here — q(x,y) is a field)
- **SI units:** [m/s], [Pa], [Pa·s], [m²] — always include units with variables

---

## Dev docs system

For tasks spanning >1 session or involving non-trivial design decisions:

1. Create `dev/active/<task-name>/`
2. Write `<task>-plan.md`, `<task>-context.md`, `<task>-tasks.md`
3. Run `/mlhw3-plan-audit <task>` before implementing
4. Check off tasks immediately when done
5. After completion: move to `dev/archive/`

See `dev/active/README.md` for templates.
