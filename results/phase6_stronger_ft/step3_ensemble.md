## Step 3 -- cheap ensemble (avg probs, threshold tuned on VAL) of the selected configs

- **very_easy**: skipped (only 1 model(s) with val_predictions available)
- **easy**: skipped (only 1 model(s) with val_predictions available)
- **medium**: ensemble of ['L2a_focal', 'L2b_cosine_llrd'] -> F1=0.546 (TP=416 FP=643 FN=48), AUC=0.611, AP=0.487, CI=[0.498,0.590]
  - S3 (استعارة فعل fixed test pool): F1=0.564 (TP=127 FP=196 FN=0), AUC=0.647
- **hard**: skipped (only 1 model(s) with val_predictions available)
- **very_hard**: ensemble of ['L3_arabert_large', 'L1_context'] -> F1=0.169 (TP=41 FP=319 FN=85), AUC=0.561, AP=0.124, CI=[0.111,0.222]