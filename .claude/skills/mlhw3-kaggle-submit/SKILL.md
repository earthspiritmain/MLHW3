---
name: mlhw3-kaggle-submit
description: Generates and validates a Kaggle submission CSV for the porous media flow competition. Verifies correct format (id column as integer, 2048 prediction columns, 500 rows), saves to submissions/ with timestamp. Does NOT push to Kaggle API.
argument-hint: "[model=<checkpoint_name>]"
---

# Kaggle Submission Generator — MLHW3

**Purpose:** Generate a Kaggle submission CSV from the current best model, validate its format, and save it to `submissions/`.

**Read-only on model checkpoint. Writes one CSV to `submissions/`.**

## Step 0 — Read these files first (mandatory)

1. `assignment3.tex` — submission format section (flattening logic, id format, shape requirements)
2. `Assignement_3_helper_functions.ipynb` — `save_predictions_to_csv()` implementation reference

## Parse `$ARGUMENTS`

- **`model=`** — checkpoint filename under `experiments/checkpoints/` (without path). If omitted, use the most recently modified `.pt` file.

## Step 1 — Locate checkpoint

```python
import os, glob
if model_arg:
    ckpt = f"experiments/checkpoints/{model_arg}"
else:
    files = sorted(glob.glob("experiments/checkpoints/*.pt"), key=os.path.getmtime)
    ckpt = files[-1]
print(f"Using checkpoint: {ckpt}")
```

If no checkpoint found, stop and tell the user to train a model first.

## Step 2 — Load model and generate predictions

The orchestrator (or user) must ensure the model architecture is defined in the notebook. This skill generates a cell that:

1. Loads the checkpoint
2. Loads `flow-field-through-a-porous-media-25-26/hidden_test_inputs.npy` and `hidden_test_params.csv`
3. Applies the same preprocessing as training (normalization, dimensionless variables)
4. Runs inference on all 500 test samples with `model.eval()` and `torch.no_grad()`
5. Calls `save_predictions_to_csv(predictions, csv_path)` from `Assignement_3_helper_functions.ipynb`

## Step 3 — Validate submission format

After generating, validate:

```python
import pandas as pd
df = pd.read_csv(csv_path)

# Check shape
assert df.shape == (500, 2049), f"Expected (500, 2049), got {df.shape}"

# Check id column
assert 'id' in df.columns, "Missing 'id' column"
assert df['id'].dtype == int or df['id'].dtype == 'int64', f"id must be integer, got {df['id'].dtype}"
assert list(df['id']) == list(range(500)), "id column must be 0..499"

# Check prediction columns
pred_cols = [str(i) for i in range(2048)]
assert list(df.columns[1:]) == pred_cols, "Prediction columns must be '0', '1', ..., '2047'"

# Check no NaN or Inf
assert not df.iloc[:,1:].isnull().any().any(), "NaN values found in predictions"
assert not (df.iloc[:,1:].abs() == float('inf')).any().any(), "Inf values found"

# Check physical sanity: predictions should be >= 0 (flow rates)
neg_count = (df.iloc[:,1:] < 0).sum().sum()
if neg_count > 0:
    print(f"WARNING: {neg_count} negative predictions found. Check masking.")

print("Validation passed.")
print(f"Prediction range: [{df.iloc[:,1:].min().min():.4e}, {df.iloc[:,1:].max().max():.4e}]")
```

## Step 4 — Save with timestamp

```python
import time
run_id = time.strftime('%Y%m%d_%H%M%S')
model_name = os.path.basename(ckpt).replace('.pt', '')
csv_path = f"submissions/{model_name}_{run_id}.csv"
```

## Step 5 — Output summary

Report:
- Checkpoint used
- CSV path saved
- Shape: (500, 2049)
- id format: integer ✓ or ✗
- NaN/Inf: none found ✓ or issues found ✗
- Negative predictions: count (flag if >0)
- Prediction value range
- **Next step:** Upload `submissions/<filename>.csv` to the Kaggle competition manually

## What this skill does NOT do

- Does not push to the Kaggle API
- Does not modify the model
- Does not retrain anything
- Does not guarantee a good Kaggle score — that depends on model quality

## Reference: submission format

From `assignment3.tex`:
- Shape: [500, 2048] predictions + 1 id column = 2049 columns
- id must be integer (1, not 1.0)
- Flattening: row-major (q[1,1], q[1,2], ..., q[1,64], q[2,1], ..., q[32,64])
- The helper function `save_predictions_to_csv(predictions, csv_save_path)` from `Assignement_3_helper_functions.ipynb` handles this correctly. Input shape must be [N, 1, 32, 64].
