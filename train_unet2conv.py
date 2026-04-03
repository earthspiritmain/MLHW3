"""
Standalone UNet2Conv trainer — identical setup to assignment3.ipynb.
Trains N runs of 1000 epochs each, saves the best 2 submissions by val loss.

Usage:
    python train_unet2conv.py            # 5 runs, keep best 2
    python train_unet2conv.py --runs 3   # 3 runs, keep best 2
"""

import argparse, datetime, json, os, time
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SEED      = 42
EPOCHS    = 1000
LR        = 0.0018473155281687995   # best Optuna trial (same as notebook)
WD        = 2.0366442026830878e-07  # best Optuna trial
PATIENCE  = 200
BATCH     = 32
C         = 16
KEEP_BEST = 2

DATA_DIR  = ('/kaggle/input/datasets/pastors/mlass4/flow-field-through-a-porous-media-25-26'
             if os.path.exists('/kaggle/input/datasets/pastors/mlass4/flow-field-through-a-porous-media-25-26')
             else 'flow-field-through-a-porous-media-25-26')

for d in ('experiments/logs', 'experiments/checkpoints', 'submissions'):
    os.makedirs(d, exist_ok=True)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Device: {device}")

# ---------------------------------------------------------------------------
# Data loading + preprocessing  (identical to notebook cells 5, 14)
# ---------------------------------------------------------------------------
def make_dim_hom(delta_p, L, mu, delta_A):
    """v0 = ΔP·ΔA / (μ·L)  [m/s]"""
    return np.asarray(delta_p) * np.asarray(delta_A) / (np.asarray(mu) * np.asarray(L))

train_inputs = np.load(f'{DATA_DIR}/train_inputs.npy')
train_labels = np.load(f'{DATA_DIR}/train_labels.npy')
train_params = pd.read_csv(f'{DATA_DIR}/train_params.csv')

v0 = make_dim_hom(train_params['delta_p'].values, train_params['L'].values,
                  train_params['visc'].values,     train_params['delta_A'].values)
q_norm = train_labels / v0[:, None, None]   # dimensionless q/v0

torch.manual_seed(SEED)
np.random.seed(SEED)
perm    = torch.randperm(len(train_inputs)).numpy()
n_train = int(0.8 * len(train_inputs))
train_idx, val_idx = perm[:n_train], perm[n_train:]

inputs_t = torch.tensor(train_inputs, dtype=torch.float32).unsqueeze(1)
labels_t = torch.tensor(q_norm,       dtype=torch.float32)

X_train, y_train = inputs_t[train_idx], labels_t[train_idx]
X_val,   y_val   = inputs_t[val_idx],   labels_t[val_idx]

# ---------------------------------------------------------------------------
# Augmentation  (identical to notebook cell 18 — V4 group: id + hflip + vflip + rot180)
# ---------------------------------------------------------------------------
def augment(X, y):
    Xh,  yh  = torch.flip(X, [-1]),    torch.flip(y, [-1])
    Xv,  yv  = torch.flip(X, [-2]),    torch.flip(y, [-2])
    Xhv, yhv = torch.flip(X, [-2,-1]), torch.flip(y, [-2,-1])
    return (torch.cat([X, Xh, Xv, Xhv]),
            torch.cat([y, yh, yv, yhv]))

X_aug, y_aug = augment(X_train, y_train)

class TensorData(Dataset):
    def __init__(self, x, y): self.x, self.y = x, y
    def __len__(self): return len(self.x)
    def __getitem__(self, i): return self.x[i], self.y[i]

train_loader = DataLoader(TensorData(X_aug, y_aug), batch_size=BATCH, shuffle=True,
                          generator=torch.Generator().manual_seed(SEED))
val_loader   = DataLoader(TensorData(X_val, y_val), batch_size=BATCH, shuffle=False)

print(f"Train batches: {len(train_loader)} ({len(X_aug)} samples aug)")
print(f"Val   batches: {len(val_loader)}  ({len(X_val)} samples)")

# ---------------------------------------------------------------------------
# Loss  (identical to notebook cell 22)
# ---------------------------------------------------------------------------
EPSILON = 1e-6

def kaggle_loss(pred, truth, eps=EPSILON):
    return ((pred - truth).abs() / (truth + eps)).mean()

# ---------------------------------------------------------------------------
# Model  (identical to notebook cell 46)
# ---------------------------------------------------------------------------
class UNet2ConvBackbone(nn.Module):
    def __init__(self, C=16, use_batchnorm=True):
        super().__init__()
        def conv_block(in_ch, out_ch):
            layers = [nn.Conv2d(in_ch, out_ch, 3, padding=1, bias=False)]
            if use_batchnorm: layers.append(nn.BatchNorm2d(out_ch))
            layers += [nn.ReLU(),
                       nn.Conv2d(out_ch, out_ch, 3, padding=1, bias=False)]
            if use_batchnorm: layers.append(nn.BatchNorm2d(out_ch))
            layers.append(nn.ReLU())
            return nn.Sequential(*layers)
        self.enc1, self.pool1 = conv_block(1,   C),   nn.MaxPool2d(2, 2)
        self.enc2, self.pool2 = conv_block(C,   2*C), nn.MaxPool2d(2, 2)
        self.bottleneck       = conv_block(2*C, 4*C)
        self.up2  = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False)
        self.dec2 = conv_block(4*C+2*C, 2*C)
        self.up1  = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False)
        self.dec1 = conv_block(2*C+C, C)
        self.head = nn.Conv2d(C, 1, 1, bias=True)

    def forward(self, x):
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool1(e1))
        b  = self.bottleneck(self.pool2(e2))
        d2 = self.dec2(torch.cat([self.up2(b),  e2], dim=1))
        d1 = self.dec1(torch.cat([self.up1(d2), e1], dim=1))
        return self.head(d1)   # (B, 1, 32, 64)

class MaskedUNet(nn.Module):
    def __init__(self, backbone):
        super().__init__()
        self.backbone = backbone
        self.softplus = nn.Softplus()

    def forward(self, x):
        out  = self.backbone(x)    # (B, 1, 32, 64)
        out  = self.softplus(out)
        out  = out.squeeze(1)      # (B, 32, 64)
        mask = x.squeeze(1)        # (B, 32, 64)
        return out * mask          # q=0 at closed pixels

# ---------------------------------------------------------------------------
# Training loop  (identical to notebook cell 24)
# ---------------------------------------------------------------------------
def train_model(model, train_loader, val_loader, loss_fn,
                model_name, epochs=EPOCHS, lr=LR, weight_decay=WD, patience=PATIENCE):
    run_id    = f"{model_name}_{time.strftime('%Y%m%d_%H%M%S')}"
    log_path  = f"experiments/logs/{run_id}.json"
    ckpt_path = f"experiments/checkpoints/{run_id}_best.pt"

    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)

    loss_dict         = {"train": [], "val": []}
    best_val          = float("inf")
    epochs_no_improve = 0

    print(f"\n{'Epoch':<8}{'Train loss':<18}{'Val loss':<18}")

    for epoch in range(epochs):
        model.train()
        train_sum = 0.0
        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)
            optimizer.zero_grad()
            loss = loss_fn(model(xb), yb)
            loss.backward()
            optimizer.step()
            train_sum += loss.item()
        train_loss = train_sum / len(train_loader)
        loss_dict["train"].append(train_loss)

        model.eval()
        with torch.no_grad():
            val_sum = sum(loss_fn(model(xv.to(device)), yv.to(device)).item()
                         for xv, yv in val_loader)
        val_loss = val_sum / len(val_loader)
        loss_dict["val"].append(val_loss)

        if val_loss < best_val:
            best_val          = val_loss
            epochs_no_improve = 0
            torch.save(model.state_dict(), ckpt_path)
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                print(f"{epoch+1:<8}{train_loss:<18.6e}{val_loss:<18.6e}  [early stop]")
                break

        scheduler.step()

        if (epoch + 1) % max(1, epochs // 10) == 0:
            print(f"{epoch+1:<8}{train_loss:<18.6e}{val_loss:<18.6e}")

    model.load_state_dict(torch.load(ckpt_path, map_location=device, weights_only=True))
    model.eval()

    with open(log_path, 'w') as f:
        json.dump(loss_dict, f)
    print(f"Log  saved -> {log_path}")
    print(f"Ckpt saved -> {ckpt_path}")

    return model, best_val, run_id

# ---------------------------------------------------------------------------
# Submission helper
# ---------------------------------------------------------------------------
def generate_submission(model, run_id):
    test_inputs = np.load(f'{DATA_DIR}/hidden_test_inputs.npy')
    test_params = pd.read_csv(f'{DATA_DIR}/hidden_test_params.csv')
    v0_test = make_dim_hom(test_params['delta_p'].values, test_params['L'].values,
                           test_params['visc'].values,    test_params['delta_A'].values)

    X_test = torch.tensor(test_inputs, dtype=torch.float32).unsqueeze(1)
    model.eval()
    with torch.no_grad():
        preds_norm = model(X_test.to(device)).cpu()   # (500, 32, 64)

    preds_np = preds_norm.numpy().squeeze()            # (500, 32, 64)
    assert preds_np.shape == (500, 32, 64), f"Unexpected shape: {preds_np.shape}"
    preds_phys = preds_np * v0_test[:, None, None]     # de-normalise to [m/s]

    flat   = preds_phys.reshape(500, -1)               # (500, 2048)
    df_sub = pd.DataFrame(flat, columns=[str(i) for i in range(2048)])
    df_sub.insert(0, 'id', range(500))

    path = f'submissions/unet2conv_{run_id}.csv'
    df_sub.to_csv(path, index=False)

    size_mb = os.path.getsize(path) / 1e6
    print(f"Submission saved -> {path}  ({size_mb:.1f} MB, shape {df_sub.shape})")
    return path

# ---------------------------------------------------------------------------
# Main: N runs, keep best KEEP_BEST
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--runs',   type=int,   default=5,    help='Number of training runs')
    parser.add_argument('--epochs', type=int,   default=1000, help='Epochs per run')
    parser.add_argument('--lr',     type=float, default=LR,   help='Learning rate')
    args, _ = parser.parse_known_args()  # ignore Kaggle kernel args
    EPOCHS = args.epochs

    results = []   # list of (best_val, run_id, model_state_dict)

    for run_num in range(1, args.runs + 1):
        print(f"\n{'='*60}")
        print(f"RUN {run_num}/{args.runs}")
        print(f"{'='*60}")

        seed = SEED + run_num   # different init per run, reproducible
        torch.manual_seed(seed)
        np.random.seed(seed)

        model = MaskedUNet(UNet2ConvBackbone(C=C, use_batchnorm=True)).to(device)
        model, best_val, run_id = train_model(
            model, train_loader, val_loader, kaggle_loss,
            model_name="unet2conv",
            epochs=EPOCHS,
            lr=args.lr,
        )
        results.append((best_val, run_id, model))
        print(f"Run {run_num} best val E = {best_val:.6e}")

    # Sort by val loss, keep best KEEP_BEST
    results.sort(key=lambda x: x[0])
    print(f"\n{'='*60}")
    print(f"All runs summary:")
    for i, (val, rid, _) in enumerate(results):
        mark = '<-- saved' if i < KEEP_BEST else ''
        print(f"  #{i+1}  val E={val:.6e}  {rid}  {mark}")

    print(f"\nGenerating submissions for top {KEEP_BEST} runs...")
    for val, run_id, model in results[:KEEP_BEST]:
        generate_submission(model, run_id)

    print("\nDone.")
