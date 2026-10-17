## Step 2 evaluation -- TEST only

### S2 (primary split)

| Target | Config | n_seeds | F1 mean+-std | P | R | TP/FP/FN | AUC-ROC | AP | bootstrap 95% CI | test_pos (mean) | flag |
|---|---|---|---|---|---|---|---|---|---|---|---|
| very_easy | L2a_focal (marbert/ctx0_focal_constant) | 3 | 0.350+-0.077 | 0.314 | 0.439 | 43/94/55 | 0.776 | 0.199 | [0.244,0.463] | 33 |  |
| very_easy | phase5_baseline (marbert/ctx0_bce_pos_weight_constant) | 3 | 0.282+-0.090 | 0.287 | 0.276 | 27/67/71 | 0.790 | 0.287 | [0.177,0.371] | 33 |  |
| easy | L1_context (marbert/ctx1_bce_pos_weight_constant) | 3 | 0.175+-0.092 | 0.145 | 0.268 | 34/201/93 | 0.617 | 0.130 | [0.107,0.257] | 42 |  |
| easy | phase5_baseline (marbert/ctx0_bce_pos_weight_constant) | 3 | 0.189+-0.023 | 0.119 | 0.425 | 54/400/73 | 0.562 | 0.121 | [0.119,0.253] | 42 |  |
| medium | phase5_baseline (marbert/ctx0_bce_pos_weight_constant) | 3 | 0.562+-0.008 | 0.403 | 0.922 | 532/787/45 | 0.619 | 0.494 | [0.508,0.606] | 192 |  |
| medium | L2a_focal (marbert/ctx0_focal_constant) | 3 | 0.556+-0.012 | 0.422 | 0.816 | 471/645/106 | 0.595 | 0.453 | [0.499,0.603] | 192 |  |
| medium | L2b_cosine_llrd (marbert/ctx0_bce_pos_weight_cosine_llrd) | 3 | 0.558+-0.008 | 0.426 | 0.811 | 468/630/109 | 0.625 | 0.494 | [0.502,0.606] | 192 |  |
| hard | L1_context (marbert/ctx1_bce_pos_weight_constant) | 3 | 0.347+-0.007 | 0.258 | 0.547 | 123/353/102 | 0.667 | 0.244 | [0.284,0.403] | 75 |  |
| hard | phase5_baseline (marbert/ctx0_bce_pos_weight_constant) | 3 | 0.275+-0.053 | 0.244 | 0.391 | 88/272/137 | 0.650 | 0.256 | [0.229,0.358] | 75 |  |
| very_hard | phase5_baseline (camelbert_ca/ctx0_bce_pos_weight_constant) | 3 | 0.217+-0.020 | 0.133 | 0.660 | 107/698/55 | 0.543 | 0.120 | [0.148,0.300] | 54 |  |
| very_hard | L3_arabert_large (arabert_large/ctx0_bce_pos_weight_constant) | 3 | 0.137+-0.051 | 0.119 | 0.253 | 41/303/121 | 0.528 | 0.122 | [0.096,0.232] | 54 |  |
| very_hard | L1_context (camelbert_ca/ctx1_bce_pos_weight_constant) | 3 | 0.152+-0.050 | 0.125 | 0.259 | 42/294/120 | 0.537 | 0.118 | [0.105,0.233] | 54 |  |

### S3 (استعارة فعل only, fixed 25-poem/327-verse TEST pool)

| Target | Config | n_seeds | F1 mean+-std | P | R | TP/FP/FN | AUC-ROC | AP | bootstrap 95% CI | test_pos (mean) | flag |
|---|---|---|---|---|---|---|---|---|---|---|---|
| medium | phase5_baseline (marbert/ctx0_bce_pos_weight_constant) | 3 | 0.570+-0.005 | 0.420 | 0.887 | 338/467/43 | 0.623 | 0.494 | [0.495,0.635] | 127 |  |
| medium | L2a_focal (marbert/ctx0_focal_constant) | 3 | 0.567+-0.009 | 0.416 | 0.890 | 339/475/42 | 0.618 | 0.489 | [0.491,0.634] | 127 |  |
| medium | L2b_cosine_llrd (marbert/ctx0_bce_pos_weight_cosine_llrd) | 3 | 0.573+-0.006 | 0.435 | 0.845 | 322/419/59 | 0.612 | 0.492 | [0.502,0.636] | 127 |  |

### S3 vs LLM evidence (same test pool, docs/phase5/LOCAL_FT_RESULTS.md section 8)

| Source | F1 |
|---|---|
| Best single LLM (Claude Sonnet 4.6, set A) | 0.576 |
| LLM ensemble (3-model ensemble, set A) | 0.568 |
| LLM zero-shot range | 0.377-0.549 |
| Phase 6 phase5_baseline (marbert) | 0.570+-0.005 |
| Phase 6 L2a_focal (marbert) | 0.567+-0.009 |
| Phase 6 L2b_cosine_llrd (marbert) | 0.573+-0.006 |