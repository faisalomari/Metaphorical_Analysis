"""L2 lever: layer-wise learning-rate decay (LLRD) for BERT-style encoders.
Standard scheme: the classifier head gets the full lr; each transformer layer
gets lr * decay^(depth_from_top), so deeper (earlier) layers train slower;
embeddings get one decay step below the first transformer layer."""


def llrd_param_groups(model, base_lr: float, decay: float, weight_decay: float):
    named = list(model.named_parameters())
    layer_ids = []
    for name, _ in named:
        if "encoder.layer." in name:
            layer_ids.append(int(name.split("encoder.layer.")[1].split(".")[0]))
    num_layers = (max(layer_ids) + 1) if layer_ids else 0

    groups = {}  # depth -> {"params": [...], "lr": ...}

    def _bucket(name: str) -> int:
        """Returns a 'depth from top' index: 0 = classifier head (full lr),
        1 = last transformer layer, ..., num_layers = first transformer layer,
        num_layers+1 = embeddings."""
        if "encoder.layer." in name:
            layer_idx = int(name.split("encoder.layer.")[1].split(".")[0])
            return num_layers - layer_idx
        if "embeddings" in name:
            return num_layers + 1
        return 0  # pooler / classifier / anything else -> full lr

    for name, param in named:
        if not param.requires_grad:
            continue
        depth = _bucket(name)
        lr = base_lr * (decay ** depth)
        no_decay = any(nd in name for nd in ("bias", "LayerNorm.weight", "layer_norm.weight"))
        key = (depth, no_decay)
        if key not in groups:
            groups[key] = {"params": [], "lr": lr, "weight_decay": 0.0 if no_decay else weight_decay}
        groups[key]["params"].append(param)

    return list(groups.values())
