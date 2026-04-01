#!/usr/bin/env python3
"""
unet2_smoketest.py — compare 1-conv vs 2-conv U-Net for 50 epochs.

1-conv U-Net C=22: ~109k params  (current best in hpo_search)
2-conv U-Net C=16: ~118k params  (full budget, more expressive per level)

Both wrapped in GroupAvgModel at eval time.
Same training setup as hpo_search: augmentation, lr=1e-3, wd=1e-4, bs=64.
"""

import time
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from pathlib import Path

ROOT     = Path("/home/fricis/Desktop/MLHW3")
DATA_DIR = ROOT / "flow-field-through-a-porous-media-25-26"
SEED     = 42
EPOCHS   = 50
LR       = 4.611e-3    # best from HPO trial 11
WD       = 1.358e-6    # best from HPO trial 11
BS       = 32          # best from HPO trial 11

torch.manual_seed(SEED)
np.random.seed(SEED)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}\n")

# ── Data ───────────────────────────────────────────────────────────────────
train_inputs = np.load(DATA_DIR / "train_inputs.npy")
train_labels = np.load(DATA_DIR / "train_labels.npy")
train_params = pd.read_csv(DATA_DIR / "train_params.csv")

v0     = (train_params['delta_p'].values * train_params['delta_A'].values
          / (train_params['visc'].values * train_params['L'].values))
q_norm = train_labels / v0[:, None, None]

torch.manual_seed(SEED)
perm = torch.randperm(1500).numpy()
tr_idx, vl_idx = perm[:1200], perm[1200:]

X = torch.tensor(train_inputs, dtype=torch.float32).unsqueeze(1)
y = torch.tensor(q_norm,       dtype=torch.float32)
X_tr, y_tr = X[tr_idx], y[tr_idx]
X_vl, y_vl = X[vl_idx], y[vl_idx]

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

def kaggle_loss(pred, truth, eps=1e-6):
    return ((pred - truth).abs() / (truth + eps)).mean()

def hflip(x):  return torch.flip(x, [-1])
def vflip(x):  return torch.flip(x, [-2])
def rot180(x): return torch.flip(x, [-2,-1])
GROUP = [(lambda x:x, lambda x:x), (hflip,hflip), (vflip,vflip), (rot180,rot180)]

# ── Architectures ──────────────────────────────────────────────────────────
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

class UNet1Conv(nn.Module):
    """1 conv per level — current design. C=22 → ~109k params."""
    def __init__(self, C):
        super().__init__()
        def cb(ic, oc):
            return nn.Sequential(nn.Conv2d(ic,oc,3,padding=1,bias=False),
                                 nn.BatchNorm2d(oc), nn.ReLU())
        self.e1, self.p1 = cb(1,C),   nn.MaxPool2d(2,2)
        self.e2, self.p2 = cb(C,2*C), nn.MaxPool2d(2,2)
        self.bn           = cb(2*C,4*C)
        self.u2, self.d2  = nn.Upsample(scale_factor=2,mode='bilinear',align_corners=False), cb(6*C,2*C)
        self.u1, self.d1  = nn.Upsample(scale_factor=2,mode='bilinear',align_corners=False), cb(3*C,C)
        self.head         = nn.Conv2d(C,1,1,bias=True)
    def forward(self, x):
        e1 = self.e1(x)
        e2 = self.e2(self.p1(e1))
        b  = self.bn(self.p2(e2))
        d2 = self.d2(torch.cat([self.u2(b), e2], 1))
        return self.head(self.d1(torch.cat([self.u1(d2), e1], 1)))

class UNet2Conv(nn.Module):
    """2 convs per level — more expressive. C=16 → ~118k params."""
    def __init__(self, C):
        super().__init__()
        def cb(ic, oc):
            # two sequential convs: first aggregates context, second refines
            return nn.Sequential(
                nn.Conv2d(ic,oc,3,padding=1,bias=False), nn.BatchNorm2d(oc), nn.ReLU(),
                nn.Conv2d(oc,oc,3,padding=1,bias=False), nn.BatchNorm2d(oc), nn.ReLU(),
            )
        self.e1, self.p1 = cb(1,C),   nn.MaxPool2d(2,2)
        self.e2, self.p2 = cb(C,2*C), nn.MaxPool2d(2,2)
        self.bn           = cb(2*C,4*C)
        self.u2, self.d2  = nn.Upsample(scale_factor=2,mode='bilinear',align_corners=False), cb(6*C,2*C)
        self.u1, self.d1  = nn.Upsample(scale_factor=2,mode='bilinear',align_corners=False), cb(3*C,C)
        self.head         = nn.Conv2d(C,1,1,bias=True)
    def forward(self, x):
        e1 = self.e1(x)
        e2 = self.e2(self.p1(e1))
        b  = self.bn(self.p2(e2))
        d2 = self.d2(torch.cat([self.u2(b), e2], 1))
        return self.head(self.d1(torch.cat([self.u1(d2), e1], 1)))

def n_params(m): return sum(p.numel() for p in m.parameters())

# ── Training loop ──────────────────────────────────────────────────────────
def train_and_eval(base_model, name):
    eval_model = GroupAvgModel(base_model).to(device)

    train_loader = DataLoader(AugDataset(X_tr, y_tr), batch_size=BS, shuffle=True,
                              generator=torch.Generator().manual_seed(SEED))
    val_loader   = DataLoader(PlainDataset(X_vl, y_vl), batch_size=128, shuffle=False)

    opt       = torch.optim.Adam(base_model.parameters(), lr=LR, weight_decay=WD)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=EPOCHS)

    best_val = float('inf')
    t0 = time.time()

    print(f"\n{'─'*55}")
    print(f"  {name}  ({n_params(base_model):,} params)")
    print(f"{'─'*55}")

    for epoch in range(1, EPOCHS + 1):
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

        if epoch % 10 == 0:
            elapsed = time.time() - t0
            print(f"  Epoch {epoch:3d}/{EPOCHS}  val E={val_e:.5e}  best={best_val:.5e}  "
                  f"({elapsed:.0f}s elapsed)")

    total_time = time.time() - t0
    print(f"\n  Best val E : {best_val:.6e}")
    print(f"  Time       : {total_time:.0f}s  ({total_time/EPOCHS:.1f}s/epoch)")
    return best_val, total_time

# ── Run comparison ─────────────────────────────────────────────────────────
models = [
    (MaskedSoftplus(UNet1Conv(C=20)), "1-conv U-Net  C=20"),  # best HPO config
    (MaskedSoftplus(UNet2Conv(C=16)), "2-conv U-Net  C=16"),  # 2-conv at ~120k budget
]

results = []
for base, name in models:
    base = base.to(device)
    torch.manual_seed(SEED)   # same init seed for fair comparison
    best_e, t = train_and_eval(base, name)
    results.append((name, n_params(base), best_e, t))

print(f"\n{'='*55}")
print(f"  {'Model':<22} {'Params':>8}  {'Best val E':>12}  {'Time':>6}")
print(f"{'─'*55}")
for name, np_, e, t in results:
    print(f"  {name:<22} {np_:>8,}  {e:>12.6e}  {t:>5.0f}s")
print(f"{'='*55}")

winner = min(results, key=lambda r: r[2])
print(f"\n  Winner: {winner[0].strip()}  (val E={winner[2]:.6e})")
print(f"  Target: < 1.00e-03")
