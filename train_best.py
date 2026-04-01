#!/usr/bin/env python3
"""
train_best.py — final training run with best HPO params for 200 epochs.

Best params (trial 14):
  C=12, lr=4.155e-03, weight_decay=4.023e-06, batch_size=16

Architecture: UNet2Conv + MaskedSoftplus backbone, GroupAvgModel for eval.
Saves best checkpoint to experiments/checkpoints/unet_best_200ep.pt
Logs val E every 10 epochs.
"""

import json, time
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# ── Config ─────────────────────────────────────────────────────────────────
C            = 12
LR           = 4.1549324409165065e-03
WEIGHT_DECAY = 4.0234933894050666e-06
BATCH_SIZE   = 16
EPOCHS       = 200
SEED         = 42
LOG_EVERY    = 10

ROOT      = Path("/home/fricis/Desktop/MLHW3")
DATA_DIR  = ROOT / "flow-field-through-a-porous-media-25-26"
CKPT_DIR  = ROOT / "experiments" / "checkpoints"
LOG_DIR   = ROOT / "experiments" / "logs"
CKPT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

torch.manual_seed(SEED)
np.random.seed(SEED)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}")

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
        if r == 1:   x = torch.flip(x, [-1]);    y = torch.flip(y, [-1])
        elif r == 2: x = torch.flip(x, [-2]);    y = torch.flip(y, [-2])
        elif r == 3: x = torch.flip(x, [-2,-1]); y = torch.flip(y, [-2,-1])
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
GROUP = [(lambda x: x, lambda x: x), (hflip, hflip), (vflip, vflip), (rot180, rot180)]

# ── Model ──────────────────────────────────────────────────────────────────
class UNet2Conv(nn.Module):
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
    def __init__(self, bb): super().__init__(); self.backbone = bb; self.sp = nn.Softplus()
    def forward(self, x): return self.sp(self.backbone(x)).squeeze(1) * x.squeeze(1)

class GroupAvgModel(nn.Module):
    def __init__(self, m): super().__init__(); self.model = m
    def forward(self, x):
        out = None
        for g, gi in GROUP:
            y = gi(self.model(g(x)))
            out = y if out is None else out + y
        return out / 4

# ── Train ──────────────────────────────────────────────────────────────────
base_model = MaskedSoftplus(UNet2Conv(C)).to(device)
eval_model = GroupAvgModel(base_model).to(device)
n_params   = sum(p.numel() for p in base_model.parameters())
print(f"Params: {n_params:,}  (≤120k: {n_params <= 120_000})")
print(f"C={C}, lr={LR:.3e}, wd={WEIGHT_DECAY:.3e}, bs={BATCH_SIZE}, epochs={EPOCHS}\n")

train_loader = DataLoader(AugDataset(X_tr, y_tr), batch_size=BATCH_SIZE, shuffle=True,
                          generator=torch.Generator().manual_seed(SEED))
val_loader   = DataLoader(PlainDataset(X_vl, y_vl), batch_size=128, shuffle=False)

opt       = torch.optim.Adam(base_model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=EPOCHS)

run_id   = datetime.now().strftime("%Y%m%d_%H%M%S")
ckpt_path = CKPT_DIR / f"unet_best_200ep_{run_id}.pt"
log       = {"train_loss": [], "val_loss": []}
best_val  = float('inf')
t0        = time.time()

for epoch in range(1, EPOCHS + 1):
    base_model.train()
    train_losses = []
    for xb, yb in train_loader:
        xb, yb = xb.to(device), yb.to(device)
        opt.zero_grad()
        loss = kaggle_loss(base_model(xb), yb)
        loss.backward()
        opt.step()
        train_losses.append(loss.item())
    scheduler.step()

    eval_model.eval()
    with torch.no_grad():
        val_e = float(np.mean([
            kaggle_loss(eval_model(xb.to(device)), yb.to(device)).item()
            for xb, yb in val_loader
        ]))

    train_e = float(np.mean(train_losses))
    log["train_loss"].append(train_e)
    log["val_loss"].append(val_e)

    if val_e < best_val:
        best_val = val_e
        torch.save(base_model.state_dict(), ckpt_path)

    if epoch % LOG_EVERY == 0 or epoch == 1:
        elapsed = (time.time() - t0) / 60
        print(f"  Epoch {epoch:3d}/{EPOCHS} | train={train_e:.5e} | val={val_e:.5e} "
              f"| best={best_val:.5e} | {elapsed:.1f}min")

# ── Save log ───────────────────────────────────────────────────────────────
log_path = LOG_DIR / f"unet_best_200ep_{run_id}.json"
with open(log_path, 'w') as f:
    json.dump({"params": {"C": C, "lr": LR, "weight_decay": WEIGHT_DECAY,
                          "batch_size": BATCH_SIZE, "epochs": EPOCHS},
               "best_val_E": best_val,
               "n_params": n_params,
               **log}, f, indent=2)

total_min = (time.time() - t0) / 60
print(f"\nDone in {total_min:.1f} min")
print(f"Best val E : {best_val:.6e}")
print(f"Checkpoint : {ckpt_path}")
print(f"Log        : {log_path}")
