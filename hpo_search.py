#!/usr/bin/env python3
"""
hpo_search.py — hyperparameter search for MLHW3 porous media flow.

Architecture: 2-conv U-Net (2 convs per encoder/decoder level) only.
  - 459C²+50C params. C range 12–16 all fit under 120k.
  - Smoke-tested to reach val E=4.5e-3 at 50 epochs vs 1.2e-2 for 1-conv.

Strategy:
  - Train base model with Z2xZ2 data augmentation (fast, same symmetry signal)
  - Evaluate with GroupAvgModel wrapping (equivariant inference, val set only)
  - Optuna TPE + MedianPruner, persisted to SQLite — resumes across runs

Run:
  python3 hpo_search.py           # normal 55-min run
  python3 hpo_search.py --smoke   # 2 trials x 5 epochs to verify db persistence
"""

import sys, json, time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)

# ── Config ─────────────────────────────────────────────────────────────────
SMOKE      = "--smoke" in sys.argv
ROOT       = Path("/home/fricis/Desktop/MLHW3")
DATA_DIR   = ROOT / "flow-field-through-a-porous-media-25-26"
OUT_PATH   = ROOT / "hpo_results.json"
DB_PATH    = ROOT / "hpo_study.db"          # persistent across runs
STUDY_NAME = "mlhw3_unet2conv"
SEED       = 42
TIMEOUT    = (2 * 60) if SMOKE else (55 * 60)
MAX_EPOCHS = 5  if SMOKE else 60
PRUNE_WARMUP   = 2  if SMOKE else 25
PRUNE_INTERVAL = 1  if SMOKE else 4
PARAM_CAP  = 120_000

torch.manual_seed(SEED)
np.random.seed(SEED)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}  |  {'SMOKE TEST MODE' if SMOKE else 'full search'}")

# ── Data ───────────────────────────────────────────────────────────────────
train_inputs = np.load(DATA_DIR / "train_inputs.npy")
train_labels = np.load(DATA_DIR / "train_labels.npy")
train_params = pd.read_csv(DATA_DIR / "train_params.csv")

v0     = (train_params['delta_p'].values * train_params['delta_A'].values
          / (train_params['visc'].values * train_params['L'].values))
q_norm = train_labels / v0[:, None, None]

torch.manual_seed(SEED)
perm = torch.randperm(1500).numpy()
train_idx, val_idx = perm[:1200], perm[1200:]

X = torch.tensor(train_inputs, dtype=torch.float32).unsqueeze(1)
y = torch.tensor(q_norm,       dtype=torch.float32)
X_tr, y_tr = X[train_idx], y[train_idx]
X_vl, y_vl = X[val_idx],   y[val_idx]

# ── Datasets ───────────────────────────────────────────────────────────────
class AugDataset(Dataset):
    def __init__(self, X, y): self.X, self.y = X, y
    def __len__(self): return len(self.X)
    def __getitem__(self, i):
        x, y = self.X[i], self.y[i]
        r = torch.randint(4, (1,)).item()
        if r == 1:   x = torch.flip(x,[-1]);    y = torch.flip(y,[-1])
        elif r == 2: x = torch.flip(x,[-2]);    y = torch.flip(y,[-2])
        elif r == 3: x = torch.flip(x,[-2,-1]); y = torch.flip(y,[-2,-1])
        return x, y

class PlainDataset(Dataset):
    def __init__(self, X, y): self.X, self.y = X, y
    def __len__(self): return len(self.X)
    def __getitem__(self, i): return self.X[i], self.y[i]

# ── Loss ───────────────────────────────────────────────────────────────────
def kaggle_loss(pred, truth, eps=1e-6):
    return ((pred - truth).abs() / (truth + eps)).mean()

# ── Symmetry ───────────────────────────────────────────────────────────────
def hflip(x):  return torch.flip(x, [-1])
def vflip(x):  return torch.flip(x, [-2])
def rot180(x): return torch.flip(x, [-2,-1])
GROUP = [(lambda x:x, lambda x:x), (hflip,hflip), (vflip,vflip), (rot180,rot180)]

# ── Model: 2-conv U-Net ────────────────────────────────────────────────────
# Param formula: 459C² + 50C
# C=12 → 66,696  C=14 → 90,664  C=15 → 104,025  C=16 → 118,304  (all ≤ 120k)

class UNet2Conv(nn.Module):
    """2 convs per level — more expressive per parameter than 1-conv design."""
    def __init__(self, C):
        super().__init__()
        def cb(ic, oc):
            return nn.Sequential(
                nn.Conv2d(ic, oc, 3, padding=1, bias=False), nn.BatchNorm2d(oc), nn.ReLU(),
                nn.Conv2d(oc, oc, 3, padding=1, bias=False), nn.BatchNorm2d(oc), nn.ReLU(),
            )
        self.e1, self.p1 = cb(1, C),    nn.MaxPool2d(2, 2)
        self.e2, self.p2 = cb(C, 2*C),  nn.MaxPool2d(2, 2)
        self.bn           = cb(2*C, 4*C)
        self.u2           = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False)
        self.d2           = cb(6*C, 2*C)
        self.u1           = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False)
        self.d1           = cb(3*C, C)
        self.head         = nn.Conv2d(C, 1, 1, bias=True)

    def forward(self, x):
        e1 = self.e1(x)
        e2 = self.e2(self.p1(e1))
        b  = self.bn(self.p2(e2))
        d2 = self.d2(torch.cat([self.u2(b), e2], 1))
        return self.head(self.d1(torch.cat([self.u1(d2), e1], 1)))

class MaskedSoftplus(nn.Module):
    def __init__(self, bb): super().__init__(); self.backbone=bb; self.sp=nn.Softplus()
    def forward(self, x): return self.sp(self.backbone(x)).squeeze(1) * x.squeeze(1)

class GroupAvgModel(nn.Module):
    def __init__(self, m): super().__init__(); self.model=m
    def forward(self, x):
        out = None
        for g, gi in GROUP:
            y = gi(self.model(g(x)))
            out = y if out is None else out + y
        return out / 4

def build_model(C):
    return MaskedSoftplus(UNet2Conv(C))

def n_params(m): return sum(p.numel() for p in m.parameters())

# ── Objective ──────────────────────────────────────────────────────────────
def objective(trial):
    # 459C²+50C ≤ 120k → C ≤ 16
    C  = trial.suggest_int('C', 12, 16)
    lr = trial.suggest_float('lr', 1e-3, 8e-3, log=True)
    wd = trial.suggest_float('weight_decay', 1e-7, 1e-3, log=True)
    bs = trial.suggest_categorical('batch_size', [16, 32, 64])

    base_model = build_model(C).to(device)
    eval_model = GroupAvgModel(base_model).to(device)

    train_loader = DataLoader(AugDataset(X_tr, y_tr), batch_size=bs, shuffle=True,
                              generator=torch.Generator().manual_seed(SEED + trial.number))
    val_loader   = DataLoader(PlainDataset(X_vl, y_vl), batch_size=128, shuffle=False)

    opt       = torch.optim.Adam(base_model.parameters(), lr=lr, weight_decay=wd)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=MAX_EPOCHS)

    best_val = float('inf')
    for epoch in range(MAX_EPOCHS):
        base_model.train()
        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad()
            kaggle_loss(base_model(xb), yb).backward()
            opt.step()
        scheduler.step()

        eval_model.eval()
        with torch.no_grad():
            val_e = float(np.mean([
                kaggle_loss(eval_model(xb.to(device)), yb.to(device)).item()
                for xb, yb in val_loader
            ]))
        best_val = min(best_val, val_e)

        trial.report(val_e, epoch)
        if trial.should_prune():
            raise optuna.exceptions.TrialPruned()

    return best_val

# ── Run ────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    storage = f"sqlite:///{DB_PATH}"

    study = optuna.create_study(
        study_name=STUDY_NAME,
        storage=storage,
        load_if_exists=True,        # resumes from previous runs
        direction='minimize',
        sampler=optuna.samplers.TPESampler(seed=SEED),
        pruner=optuna.pruners.MedianPruner(
            n_startup_trials=6,
            n_warmup_steps=PRUNE_WARMUP,
            interval_steps=PRUNE_INTERVAL,
        ),
    )

    prev = len(study.trials)
    print(f"Study '{STUDY_NAME}' — {prev} trials already in db")
    print(f"Timeout: {TIMEOUT//60} min  |  Max epochs/trial: {MAX_EPOCHS}\n")

    def print_callback(study, trial):
        if trial.state.name == 'COMPLETE':
            print(f"  Trial {trial.number:3d} COMPLETE | val E={trial.value:.5e} | {trial.params}")
        elif trial.state.name == 'PRUNED':
            print(f"  Trial {trial.number:3d} PRUNED   | {trial.params}")

    t0 = time.time()
    study.optimize(objective, timeout=TIMEOUT, callbacks=[print_callback])
    elapsed = time.time() - t0

    best    = study.best_trial
    np_best = n_params(build_model(best.params['C']))

    results = {
        'best_val_E':        best.value,
        'best_params':       best.params,
        'n_params':          np_best,
        'under_120k':        np_best <= PARAM_CAP,
        'n_trials_total':    len(study.trials),
        'n_trials_complete': len([t for t in study.trials if t.state.name == 'COMPLETE']),
        'n_trials_pruned':   len([t for t in study.trials if t.state.name == 'PRUNED']),
        'elapsed_seconds':   round(elapsed),
    }
    with open(OUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*60)
    print(f"BEST val E : {best.value:.6e}  (target: < 1.00e-03)")
    print(f"Best params: {best.params}")
    print(f"#params    : {np_best:,}  (≤120k: {results['under_120k']})")
    print(f"Trials     : {results['n_trials_complete']} complete, "
          f"{results['n_trials_pruned']} pruned  ({len(study.trials)} total in db)")
    print(f"Elapsed    : {elapsed/60:.1f} min")
    print(f"DB         : {DB_PATH}")
    print("="*60)
    p = best.params
    print(f"\nApply to notebook:")
    print(f"  C={p['C']}, lr={p['lr']:.3e}, weight_decay={p['wd'] if 'wd' in p else p['weight_decay']:.3e}, batch_size={p['batch_size']}")

    if SMOKE:
        print("\n── Smoke test: verifying db persistence ──")
        study2 = optuna.load_study(study_name=STUDY_NAME, storage=storage)
        assert len(study2.trials) == len(study.trials), "DB load mismatch!"
        print(f"  DB contains {len(study2.trials)} trials — persistence OK ✓")
