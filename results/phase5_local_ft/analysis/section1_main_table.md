## Section 1 — Exact numbers: F1/P/R/TP/FP/FN/TN per target x model x split

Mean +/- population-std over 3 seeds unless noted. `test_pos` < 30 is flagged with **(thin, n<30)**.

Note: S1/S2 reshuffle the WHOLE partition per seed (train/val/test all vary) -- verse/poem counts below are the mean across the 3 seeds' own (different) splits. S3 keeps TEST fixed across all 3 seeds (same 327-verse/25-poem pool every time).


### Split S1

| Level (subtype) | Model | train pos/neg verses (poems) | val pos/neg verses (poems) | test pos/neg verses (poems) | TP/FP/FN/TN (sum over seeds) | Precision | Recall | F1 mean+-std | threshold | best epoch |
|---|---|---|---|---|---|---|---|---|---|---|
| very_easy (تشبيه مطول) | camelbert_ca | 151/2326.7 (60/120 poems) | 21.7/267 (6.7/13 poems) | 44.3/659.3 (18.3/33 poems) | 18/166/115/1812 | 0.100 | 0.137 | 0.115+-0.046 | 0.62+-0.09 | 2.7+-0.5 |
| very_easy (تشبيه مطول) | arabert_v2 | 151/2326.7 (60/120 poems) | 21.7/267 (6.7/13 poems) | 44.3/659.3 (18.3/33 poems) | 23/213/110/1765 | 0.070 | 0.171 | 0.099+-0.083 | 0.50+-0.05 | 2.7+-1.2 |
| very_easy (تشبيه مطول) | marbert | 151/2326.7 (60/120 poems) | 21.7/267 (6.7/13 poems) | 44.3/659.3 (18.3/33 poems) | 58/140/75/1838 | 0.311 | 0.437 | 0.359+-0.059 | 0.48+-0.32 | 2.7+-0.9 |
| very_easy | baseline: majority | - | - | - | 0/0/133/1978 | 0.000 | 0.000 | 0.000+-0.000 | - | - |
| very_easy | baseline: always-positive | - | - | - | 133/1978/0/0 | 0.063 | 1.000 | 0.119+-0.009 | - | - |
| very_easy | baseline: TF-IDF+LR | - | - | - | 56/198/77/1780 | 0.240 | 0.422 | 0.296+-0.032 | - | - |
| very_easy | **LLM evidence** | LLM span-level strict RECALL (not F1): gemini=0.833, gpt=0.667, n=30 | Phase1 parent-level (not subtype) span-F1 avg 3 LLMs=0.700 | | | | | | | | |
| easy (استعارة تمثيلية) | camelbert_ca | 200/2277.7 (65.3/120 poems) | 27.7/261 (8.3/13 poems) | 59.3/644.3 (20.3/33 poems) | 93/1165/85/768 | 0.050 | 0.574 | 0.092+-0.065 | 0.49+-0.05 | 2.3+-1.2 |
| easy (استعارة تمثيلية) | arabert_v2 | 200/2277.7 (65.3/120 poems) | 27.7/261 (8.3/13 poems) | 59.3/644.3 (20.3/33 poems) | 91/1150/87/783 | 0.065 | 0.559 | 0.103+-0.048 | 0.43+-0.14 | 3.0+-2.8 |
| easy (استعارة تمثيلية) | marbert | 200/2277.7 (65.3/120 poems) | 27.7/261 (8.3/13 poems) | 59.3/644.3 (20.3/33 poems) | 78/455/100/1478 | 0.162 | 0.449 | 0.225+-0.041 | 0.58+-0.29 | 3.3+-1.2 |
| easy | baseline: majority | - | - | - | 0/0/178/1933 | 0.000 | 0.000 | 0.000+-0.000 | - | - |
| easy | baseline: always-positive | - | - | - | 178/1933/0/0 | 0.085 | 1.000 | 0.156+-0.023 | - | - |
| easy | baseline: TF-IDF+LR | - | - | - | 94/721/84/1212 | 0.112 | 0.514 | 0.184+-0.028 | - | - |
| easy | **LLM evidence** | LLM span-level strict RECALL (not F1): gemini=0.143, gpt=0.571, n=28 | Phase1 TEST subtype %%missed: baseline=0.33, v4=0.29, n=24 | | | | | | | | |
| medium (استعارة فعل) | camelbert_ca | 890.7/1587 (112/120 poems) | 107.7/181 (12.7/13 poems) | 259.7/444 (31.3/33 poems) | 748/1272/31/60 | 0.371 | 0.960 | 0.535+-0.029 | 0.48+-0.07 | 2.3+-1.2 |
| medium (استعارة فعل) | arabert_v2 | 890.7/1587 (112/120 poems) | 107.7/181 (12.7/13 poems) | 259.7/444 (31.3/33 poems) | 737/1232/42/100 | 0.376 | 0.947 | 0.538+-0.027 | 0.47+-0.05 | 4.0+-2.4 |
| medium (استعارة فعل) | marbert | 890.7/1587 (112/120 poems) | 107.7/181 (12.7/13 poems) | 259.7/444 (31.3/33 poems) | 623/859/156/473 | 0.421 | 0.800 | 0.549+-0.034 | 0.17+-0.09 | 3.0+-1.4 |
| medium | baseline: majority | - | - | - | 0/0/779/1332 | 0.000 | 0.000 | 0.000+-0.000 | - | - |
| medium | baseline: always-positive | - | - | - | 779/1332/0/0 | 0.370 | 1.000 | 0.540+-0.024 | - | - |
| medium | baseline: TF-IDF+LR | - | - | - | 775/1313/4/19 | 0.372 | 0.995 | 0.541+-0.026 | - | - |
| medium | **LLM evidence** | LLM verse-F1 best-single=0.576, ensemble=0.568, zero-shot range=[0.377, 0.549] | LLM span-level strict RECALL (not F1): gemini=0.264, gpt=0.155, n=110 | Phase1 TEST subtype %%missed: baseline=0.83, v4=0.62, n=76 | | | | | | | | |
| hard (طباق إيجاب) | camelbert_ca | 327.3/2150.3 (81/120 poems) | 38.7/250 (10/13 poems) | 90/613.7 (23/33 poems) | 153/1019/117/822 | 0.127 | 0.541 | 0.200+-0.031 | 0.53+-0.04 | 3.7+-1.7 |
| hard (طباق إيجاب) | arabert_v2 | 327.3/2150.3 (81/120 poems) | 38.7/250 (10/13 poems) | 90/613.7 (23/33 poems) | 221/1455/49/386 | 0.130 | 0.798 | 0.222+-0.019 | 0.50+-0.05 | 2.7+-0.5 |
| hard (طباق إيجاب) | marbert | 327.3/2150.3 (81/120 poems) | 38.7/250 (10/13 poems) | 90/613.7 (23/33 poems) | 84/242/186/1599 | 0.248 | 0.326 | 0.254+-0.103 | 0.75+-0.14 | 4.0+-1.4 |
| hard | baseline: majority | - | - | - | 0/0/270/1841 | 0.000 | 0.000 | 0.000+-0.000 | - | - |
| hard | baseline: always-positive | - | - | - | 270/1841/0/0 | 0.128 | 1.000 | 0.226+-0.015 | - | - |
| hard | baseline: TF-IDF+LR | - | - | - | 132/739/138/1102 | 0.163 | 0.497 | 0.235+-0.015 | - | - |
| hard | **LLM evidence** | LLM span-level strict RECALL (not F1): gemini=0.237, gpt=0.053, n=38 | Phase1 parent-level (not subtype) span-F1 avg 3 LLMs=0.165 | | | | | | | | |
| very_hard (كناية عن فعل) | camelbert_ca | 203/2274.7 (64.3/120 poems) | 27.7/261 (8.7/13 poems) | 49.3/654.3 (17/33 poems) | 101/1379/47/584 | 0.070 | 0.691 | 0.125+-0.017 | 0.36+-0.14 | 4.7+-1.2 |
| very_hard (كناية عن فعل) | arabert_v2 | 203/2274.7 (64.3/120 poems) | 27.7/261 (8.7/13 poems) | 49.3/654.3 (17/33 poems) | 110/1257/38/706 | 0.082 | 0.739 | 0.146+-0.014 | 0.48+-0.11 | 5.7+-4.6 |
| very_hard (كناية عن فعل) | marbert | 203/2274.7 (64.3/120 poems) | 27.7/261 (8.7/13 poems) | 49.3/654.3 (17/33 poems) | 17/145/131/1818 | 0.108 | 0.114 | 0.110+-0.001 | 0.67+-0.11 | 3.7+-0.9 |
| very_hard | baseline: majority | - | - | - | 0/0/148/1963 | 0.000 | 0.000 | 0.000+-0.000 | - | - |
| very_hard | baseline: always-positive | - | - | - | 148/1963/0/0 | 0.070 | 1.000 | 0.132+-0.012 | - | - |
| very_hard | baseline: TF-IDF+LR | - | - | - | 137/1661/11/302 | 0.079 | 0.929 | 0.145+-0.021 | - | - |
| very_hard | **LLM evidence** | LLM span-level strict RECALL (not F1): gemini=0.333, gpt=0.148, n=27 | Phase1 parent-level (not subtype) span-F1 avg 3 LLMs=0.109 | | | | | | | | |

### Split S2

| Level (subtype) | Model | train pos/neg verses (poems) | val pos/neg verses (poems) | test pos/neg verses (poems) | TP/FP/FN/TN (sum over seeds) | Precision | Recall | F1 mean+-std | threshold | best epoch |
|---|---|---|---|---|---|---|---|---|---|---|
| very_easy (تشبيه مطول) | camelbert_ca | 160.7/2300.3 (59/116 poems) | 23.7/476.3 (11.3/25 poems) | 32.7/476.3 (14.7/25 poems) | 32/421/66/1008 | 0.073 | 0.418 | 0.096+-0.049 | 0.55+-0.07 | 2.0+-0.0 |
| very_easy (تشبيه مطول) | arabert_v2 | 160.7/2300.3 (59/116 poems) | 23.7/476.3 (11.3/25 poems) | 32.7/476.3 (14.7/25 poems) | 34/594/64/835 | 0.056 | 0.397 | 0.097+-0.026 | 0.50+-0.05 | 2.0+-0.8 |
| very_easy (تشبيه مطول) | marbert | 160.7/2300.3 (59/116 poems) | 23.7/476.3 (11.3/25 poems) | 32.7/476.3 (14.7/25 poems) | 27/67/71/1362 | 0.296 | 0.285 | 0.282+-0.090 | 0.79+-0.12 | 2.7+-0.5 |
| very_easy | baseline: majority | - | - | - | 0/0/98/1429 | 0.000 | 0.000 | 0.000+-0.000 | - | - |
| very_easy | baseline: always-positive | - | - | - | 98/1429/0/0 | 0.063 | 1.000 | 0.118+-0.022 | - | - |
| very_easy | baseline: TF-IDF+LR | - | - | - | 37/143/61/1286 | 0.236 | 0.422 | 0.268+-0.020 | - | - |
| very_easy | **LLM evidence** | LLM span-level strict RECALL (not F1): gemini=0.833, gpt=0.667, n=30 | Phase1 parent-level (not subtype) span-F1 avg 3 LLMs=0.700 | | | | | | | | |
| easy (استعارة تمثيلية) | camelbert_ca | 207.3/2253.7 (64.3/116 poems) | 37.3/462.7 (14.3/25 poems) | 42.3/466.7 (15.3/25 poems) | 42/476/85/924 | 0.075 | 0.354 | 0.120+-0.038 | 0.53+-0.04 | 2.0+-1.4 |
| easy (استعارة تمثيلية) | arabert_v2 | 207.3/2253.7 (64.3/116 poems) | 37.3/462.7 (14.3/25 poems) | 42.3/466.7 (15.3/25 poems) | 75/752/52/648 | 0.087 | 0.570 | 0.148+-0.034 | 0.56+-0.04 | 3.0+-0.8 |
| easy (استعارة تمثيلية) | marbert | 207.3/2253.7 (64.3/116 poems) | 37.3/462.7 (14.3/25 poems) | 42.3/466.7 (15.3/25 poems) | 54/400/73/1000 | 0.139 | 0.401 | 0.189+-0.023 | 0.40+-0.12 | 3.0+-2.2 |
| easy | baseline: majority | - | - | - | 0/0/127/1400 | 0.000 | 0.000 | 0.000+-0.000 | - | - |
| easy | baseline: always-positive | - | - | - | 127/1400/0/0 | 0.084 | 1.000 | 0.155+-0.016 | - | - |
| easy | baseline: TF-IDF+LR | - | - | - | 80/730/47/670 | 0.097 | 0.622 | 0.166+-0.018 | - | - |
| easy | **LLM evidence** | LLM span-level strict RECALL (not F1): gemini=0.143, gpt=0.571, n=28 | Phase1 TEST subtype %%missed: baseline=0.33, v4=0.29, n=24 | | | | | | | | |
| medium (استعارة فعل) | camelbert_ca | 896/1565 (108.7/116 poems) | 169.7/330.3 (23/25 poems) | 192.3/316.7 (24.3/25 poems) | 561/915/16/35 | 0.380 | 0.969 | 0.546+-0.006 | 0.47+-0.06 | 3.3+-2.6 |
| medium (استعارة فعل) | arabert_v2 | 896/1565 (108.7/116 poems) | 169.7/330.3 (23/25 poems) | 192.3/316.7 (24.3/25 poems) | 560/927/17/23 | 0.376 | 0.968 | 0.542+-0.006 | 0.43+-0.03 | 3.0+-0.8 |
| medium (استعارة فعل) | marbert | 896/1565 (108.7/116 poems) | 169.7/330.3 (23/25 poems) | 192.3/316.7 (24.3/25 poems) | 532/787/45/163 | 0.405 | 0.919 | 0.562+-0.008 | 0.26+-0.09 | 2.0+-0.8 |
| medium | baseline: majority | - | - | - | 0/0/577/950 | 0.000 | 0.000 | 0.000+-0.000 | - | - |
| medium | baseline: always-positive | - | - | - | 577/950/0/0 | 0.378 | 1.000 | 0.548+-0.002 | - | - |
| medium | baseline: TF-IDF+LR | - | - | - | 500/759/77/191 | 0.399 | 0.858 | 0.543+-0.011 | - | - |
| medium | **LLM evidence** | LLM verse-F1 best-single=0.576, ensemble=0.568, zero-shot range=[0.377, 0.549] | LLM span-level strict RECALL (not F1): gemini=0.264, gpt=0.155, n=110 | Phase1 TEST subtype %%missed: baseline=0.83, v4=0.62, n=76 | | | | | | | | |
| hard (طباق إيجاب) | camelbert_ca | 322.3/2138.7 (80/116 poems) | 58.7/441.3 (16.7/25 poems) | 75/434 (17.3/25 poems) | 108/732/117/570 | 0.119 | 0.584 | 0.175+-0.072 | 0.47+-0.06 | 3.3+-0.9 |
| hard (طباق إيجاب) | arabert_v2 | 322.3/2138.7 (80/116 poems) | 58.7/441.3 (16.7/25 poems) | 75/434 (17.3/25 poems) | 207/1212/18/90 | 0.143 | 0.911 | 0.246+-0.027 | 0.42+-0.03 | 3.7+-2.5 |
| hard (طباق إيجاب) | marbert | 322.3/2138.7 (80/116 poems) | 58.7/441.3 (16.7/25 poems) | 75/434 (17.3/25 poems) | 88/272/137/1030 | 0.246 | 0.351 | 0.275+-0.053 | 0.80+-0.12 | 5.3+-2.1 |
| hard | baseline: majority | - | - | - | 0/0/225/1302 | 0.000 | 0.000 | 0.000+-0.000 | - | - |
| hard | baseline: always-positive | - | - | - | 225/1302/0/0 | 0.145 | 1.000 | 0.252+-0.027 | - | - |
| hard | baseline: TF-IDF+LR | - | - | - | 50/172/175/1130 | 0.225 | 0.242 | 0.227+-0.033 | - | - |
| hard | **LLM evidence** | LLM span-level strict RECALL (not F1): gemini=0.237, gpt=0.053, n=38 | Phase1 parent-level (not subtype) span-F1 avg 3 LLMs=0.165 | | | | | | | | |
| very_hard (كناية عن فعل) | camelbert_ca | 195.7/2265.3 (62/116 poems) | 30.3/469.7 (11/25 poems) | 54/455 (17/25 poems) | 107/698/55/667 | 0.131 | 0.661 | 0.217+-0.020 | 0.56+-0.02 | 2.3+-1.2 |
| very_hard (كناية عن فعل) | arabert_v2 | 195.7/2265.3 (62/116 poems) | 30.3/469.7 (11/25 poems) | 54/455 (17/25 poems) | 67/549/95/816 | 0.108 | 0.422 | 0.172+-0.015 | 0.56+-0.09 | 3.0+-2.8 |
| very_hard (كناية عن فعل) | marbert | 195.7/2265.3 (62/116 poems) | 30.3/469.7 (11/25 poems) | 54/455 (17/25 poems) | 45/333/117/1032 | 0.149 | 0.272 | 0.164+-0.007 | 0.51+-0.30 | 2.7+-0.5 |
| very_hard | baseline: majority | - | - | - | 0/0/162/1365 | 0.000 | 0.000 | 0.000+-0.000 | - | - |
| very_hard | baseline: always-positive | - | - | - | 162/1365/0/0 | 0.107 | 1.000 | 0.193+-0.015 | - | - |
| very_hard | baseline: TF-IDF+LR | - | - | - | 28/161/134/1204 | 0.148 | 0.175 | 0.158+-0.024 | - | - |
| very_hard | **LLM evidence** | LLM span-level strict RECALL (not F1): gemini=0.333, gpt=0.148, n=27 | Phase1 parent-level (not subtype) span-F1 avg 3 LLMs=0.109 | | | | | | | | |

### Split S3

| Level (subtype) | Model | train pos/neg verses (poems) | val pos/neg verses (poems) | test pos/neg verses (poems) | TP/FP/FN/TN (sum over seeds) | Precision | Recall | F1 mean+-std | threshold | best epoch |
|---|---|---|---|---|---|---|---|---|---|---|
| medium (استعارة فعل) | camelbert_ca | 1014.7/1817 (118.3/127 poems) | 116.3/195 (13.7/14 poems) | 127/200 (24/25 poems) | 379/584/2/16 | 0.394 | 0.995 | 0.564+-0.003 | 0.41+-0.00 | 1.7+-0.9 |
| medium (استعارة فعل) | arabert_v2 | 1014.7/1817 (118.3/127 poems) | 116.3/195 (13.7/14 poems) | 127/200 (24/25 poems) | 375/564/6/36 | 0.400 | 0.984 | 0.568+-0.012 | 0.42+-0.04 | 3.7+-2.1 |
| medium (استعارة فعل) | marbert | 1014.7/1817 (118.3/127 poems) | 116.3/195 (13.7/14 poems) | 127/200 (24/25 poems) | 338/467/43/133 | 0.427 | 0.887 | 0.570+-0.005 | 0.29+-0.11 | 2.3+-1.2 |
| medium | baseline: majority | - | - | - | 0/0/381/600 | 0.000 | 0.000 | 0.000+-0.000 | - | - |
| medium | baseline: always-positive | - | - | - | 381/600/0/0 | 0.388 | 1.000 | 0.559+-0.000 | - | - |
| medium | baseline: TF-IDF+LR | - | - | - | 359/558/22/42 | 0.392 | 0.942 | 0.553+-0.004 | - | - |
| medium | **LLM evidence** | LLM verse-F1 best-single=0.576, ensemble=0.568, zero-shot range=[0.377, 0.549] | LLM span-level strict RECALL (not F1): gemini=0.264, gpt=0.155, n=110 | Phase1 TEST subtype %%missed: baseline=0.83, v4=0.62, n=76 | | | | | | | | |