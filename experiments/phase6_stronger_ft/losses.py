"""L2 lever: loss function variants. `bce_pos_weight` reproduces Phase 5's loss
exactly (BCEWithLogitsLoss(pos_weight=neg/pos) computed from the run's own
TRAIN split); `focal` is the new alternative this phase tests."""
import torch
import torch.nn as nn
import torch.nn.functional as F


class FocalLoss(nn.Module):
    """Binary focal loss on logits (Lin et al. 2017), with the same per-run
    pos_weight Phase 5 already computes (neg/pos on TRAIN) folded in as an
    alpha-style class weight, so focal and bce_pos_weight differ only in the
    (1-p_t)^gamma down-weighting of easy examples, not in class balancing."""

    def __init__(self, pos_weight: float, gamma: float = 2.0):
        super().__init__()
        self.pos_weight = pos_weight
        self.gamma = gamma

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        p = torch.sigmoid(logits)
        p_t = p * targets + (1 - p) * (1 - targets)
        alpha_t = self.pos_weight * targets + (1 - targets)
        bce = F.binary_cross_entropy_with_logits(logits, targets, reduction="none")
        loss = alpha_t * ((1 - p_t) ** self.gamma) * bce
        return loss.mean()


def build_loss(loss_type: str, pos_weight_value: float, device) -> nn.Module:
    if loss_type == "bce_pos_weight":
        pos_weight_t = torch.tensor([pos_weight_value], device=device)
        return nn.BCEWithLogitsLoss(pos_weight=pos_weight_t)
    if loss_type == "focal":
        return FocalLoss(pos_weight=pos_weight_value, gamma=2.0).to(device)
    raise ValueError(f"unknown loss_type: {loss_type}")
