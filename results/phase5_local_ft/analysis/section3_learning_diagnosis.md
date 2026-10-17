## Section 3 — Is the model learning at all? (S2, per target x model)

`val loss` was never recorded by `train.py` (only val F1, via best-threshold search) -- curve summaries below use train loss + val F1 only. `best-threshold F1` is a **diagnostic-only** number that picks the threshold maximizing F1 on the TEST set itself -- it is never a valid reported result, only a ceiling to compare the real (val-tuned) F1 against.


### very_easy

| Model | best_epoch (mean) | n_epochs_run (mean) | train_loss first->last | val_f1 first->max->last | AUC-ROC (test) | AP (test) | real F1 (val-tuned) | best-possible F1 (test-tuned, diagnostic) | pred_rate | true_rate |
|---|---|---|---|---|---|---|---|---|---|---|
| camelbert_ca | 2.0 | 5.0 | 1.321->1.268 | 0.094->0.143->0.125 | 0.569 | 0.079 | 0.116 | 0.144 (thr=0.58) | 0.297 | 0.064 |
| arabert_v2 | 2.0 | 5.0 | 1.311->1.235 | 0.114->0.132->0.107 | 0.473 | 0.058 | 0.094 | 0.128 (thr=0.41) | 0.411 | 0.064 |
| marbert | 2.7 | 5.7 | 1.207->0.148 | 0.319->0.394->0.340 | 0.790 | 0.287 | 0.281 | 0.378 (thr=0.45) | 0.062 | 0.064 |

### easy

| Model | best_epoch (mean) | n_epochs_run (mean) | train_loss first->last | val_f1 first->max->last | AUC-ROC (test) | AP (test) | real F1 (val-tuned) | best-possible F1 (test-tuned, diagnostic) | pred_rate | true_rate |
|---|---|---|---|---|---|---|---|---|---|---|
| camelbert_ca | 2.0 | 5.0 | 1.302->1.268 | 0.191->0.192->0.175 | 0.492 | 0.083 | 0.130 | 0.162 (thr=0.55) | 0.339 | 0.083 |
| arabert_v2 | 3.0 | 6.0 | 1.290->1.269 | 0.143->0.177->0.151 | 0.534 | 0.100 | 0.157 | 0.160 (thr=0.52) | 0.542 | 0.083 |
| marbert | 3.0 | 6.0 | 1.275->0.227 | 0.185->0.214->0.181 | 0.562 | 0.121 | 0.186 | 0.174 (thr=0.17) | 0.297 | 0.083 |

### medium

| Model | best_epoch (mean) | n_epochs_run (mean) | train_loss first->last | val_f1 first->max->last | AUC-ROC (test) | AP (test) | real F1 (val-tuned) | best-possible F1 (test-tuned, diagnostic) | pred_rate | true_rate |
|---|---|---|---|---|---|---|---|---|---|---|
| camelbert_ca | 3.3 | 6.3 | 0.893->0.834 | 0.518->0.521->0.512 | 0.511 | 0.395 | 0.547 | 0.548 (thr=0.05) | 0.967 | 0.378 |
| arabert_v2 | 3.0 | 6.0 | 0.889->0.841 | 0.512->0.515->0.512 | 0.517 | 0.399 | 0.543 | 0.548 (thr=0.05) | 0.974 | 0.378 |
| marbert | 2.0 | 5.0 | 0.880->0.123 | 0.527->0.529->0.496 | 0.619 | 0.494 | 0.561 | 0.566 (thr=0.29) | 0.864 | 0.378 |

### hard

| Model | best_epoch (mean) | n_epochs_run (mean) | train_loss first->last | val_f1 first->max->last | AUC-ROC (test) | AP (test) | real F1 (val-tuned) | best-possible F1 (test-tuned, diagnostic) | pred_rate | true_rate |
|---|---|---|---|---|---|---|---|---|---|---|
| camelbert_ca | 3.3 | 6.3 | 1.230->1.091 | 0.215->0.239->0.217 | 0.462 | 0.135 | 0.203 | 0.258 (thr=0.38) | 0.550 | 0.147 |
| arabert_v2 | 3.7 | 6.7 | 1.224->1.168 | 0.211->0.222->0.211 | 0.507 | 0.152 | 0.252 | 0.260 (thr=0.36) | 0.929 | 0.147 |
| marbert | 5.3 | 8.3 | 1.205->0.046 | 0.267->0.334->0.287 | 0.650 | 0.256 | 0.301 | 0.325 (thr=0.77) | 0.236 | 0.147 |

### very_hard

| Model | best_epoch (mean) | n_epochs_run (mean) | train_loss first->last | val_f1 first->max->last | AUC-ROC (test) | AP (test) | real F1 (val-tuned) | best-possible F1 (test-tuned, diagnostic) | pred_rate | true_rate |
|---|---|---|---|---|---|---|---|---|---|---|
| camelbert_ca | 2.3 | 5.3 | 1.294->1.252 | 0.154->0.161->0.142 | 0.543 | 0.120 | 0.221 | 0.202 (thr=0.54) | 0.527 | 0.106 |
| arabert_v2 | 3.0 | 6.0 | 1.294->1.178 | 0.159->0.163->0.156 | 0.525 | 0.112 | 0.172 | 0.200 (thr=0.37) | 0.403 | 0.106 |
| marbert | 2.7 | 5.7 | 1.282->0.124 | 0.144->0.181->0.128 | 0.586 | 0.134 | 0.167 | 0.237 (thr=0.37) | 0.248 | 0.106 |