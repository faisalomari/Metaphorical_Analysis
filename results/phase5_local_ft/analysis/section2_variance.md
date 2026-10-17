## Section 2 — Variance: bootstrap 95% CI (over poems) and seed-to-seed std


### S2 — per model

| Level | Model | point F1 (pooled 3 seeds) | 95% CI | n_poems (pooled, w/ repeats across seeds) | seed-to-seed F1 std |
|---|---|---|---|---|---|
| very_easy | camelbert_ca | 0.116 | [0.076,0.155] | 62 | 0.049 |
| very_easy | arabert_v2 | 0.094 | [0.054,0.131] | 62 | 0.026 |
| very_easy | marbert | 0.281 | [0.177,0.371] | 62 | 0.090 |
| easy | camelbert_ca | 0.130 | [0.065,0.220] | 62 | 0.038 |
| easy | arabert_v2 | 0.157 | [0.100,0.218] | 62 | 0.034 |
| easy | marbert | 0.186 | [0.119,0.253] | 62 | 0.023 |
| medium | camelbert_ca | 0.547 | [0.493,0.592] | 62 | 0.006 |
| medium | arabert_v2 | 0.543 | [0.487,0.592] | 62 | 0.006 |
| medium | marbert | 0.561 | [0.508,0.606] | 62 | 0.008 |
| hard | camelbert_ca | 0.203 | [0.152,0.252] | 62 | 0.072 |
| hard | arabert_v2 | 0.252 | [0.197,0.306] | 62 | 0.027 |
| hard | marbert | 0.301 | [0.229,0.358] | 62 | 0.053 |
| very_hard | camelbert_ca | 0.221 | [0.148,0.300] | 62 | 0.020 |
| very_hard | arabert_v2 | 0.172 | [0.096,0.248] | 62 | 0.015 |
| very_hard | marbert | 0.167 | [0.121,0.213] | 62 | 0.007 |

### S2 — pooled across all 3 models (per-target overall picture)

| Level (subtype) | point F1 | 95% CI |
|---|---|---|
| very_easy (تشبيه مطول) | 0.127 | [0.086,0.166] |
| easy (استعارة تمثيلية) | 0.157 | [0.099,0.219] |
| medium (استعارة فعل) | 0.550 | [0.496,0.596] |
| hard (طباق إيجاب) | 0.245 | [0.197,0.291] |
| very_hard (كناية عن فعل) | 0.192 | [0.131,0.252] |

### S2 — pairwise target comparisons: CI overlap = NOT statistically distinguishable

| Target A | Target B | A CI | B CI | Overlap? |
|---|---|---|---|---|
| very_easy | easy | [0.086,0.166] | [0.099,0.219] | YES -- overlap |
| very_easy | medium | [0.086,0.166] | [0.496,0.596] | no overlap |
| very_easy | hard | [0.086,0.166] | [0.197,0.291] | no overlap |
| very_easy | very_hard | [0.086,0.166] | [0.131,0.252] | YES -- overlap |
| easy | medium | [0.099,0.219] | [0.496,0.596] | no overlap |
| easy | hard | [0.099,0.219] | [0.197,0.291] | YES -- overlap |
| easy | very_hard | [0.099,0.219] | [0.131,0.252] | YES -- overlap |
| medium | hard | [0.496,0.596] | [0.197,0.291] | no overlap |
| medium | very_hard | [0.496,0.596] | [0.131,0.252] | no overlap |
| hard | very_hard | [0.197,0.291] | [0.131,0.252] | YES -- overlap |

### S3 — per model

| Level | Model | point F1 (pooled 3 seeds) | 95% CI | n_poems (pooled, w/ repeats across seeds) | seed-to-seed F1 std |
|---|---|---|---|---|---|
| medium | camelbert_ca | 0.564 | [0.485,0.634] | 25 | 0.003 |
| medium | arabert_v2 | 0.568 | [0.487,0.639] | 25 | 0.012 |
| medium | marbert | 0.570 | [0.495,0.635] | 25 | 0.005 |

### S3 — pooled across all 3 models (per-target overall picture)

| Level (subtype) | point F1 | 95% CI |
|---|---|---|
| medium (استعارة فعل) | 0.567 | [0.489,0.636] |