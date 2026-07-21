import os
import pandas as pd
import numpy as np
import json
import joblib
from pathlib import Path
from tqdm.auto import tqdm
from huggingface_hub import login, whoami
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from tabpfn import TabPFNClassifier
from sklearn.metrics import accuracy_score, roc_auc_score

# 1. Setup
os.environ["HF_TOKEN"] = "REPLACE_WITH_YOUR_OWN_KEY"
login(token=os.environ["HF_TOKEN"])

# 2. Data Loading
DATA_PATH = r"embeddings_out/dataset_with_embeddings.parquet"
df = pd.read_parquet(DATA_PATH)
if df["embedding"].dtype == object and isinstance(df["embedding"].iloc[0], str):
    df["embedding"] = df["embedding"].apply(json.loads)

X = np.vstack(df["embedding"].values).astype(np.float32)
y = df["label_majaz"].astype(int).values

X_train_raw, X_test_raw, y_train, y_test = train_test_split(
    X, y, test_size=0.30, random_state=42, stratify=y
)

# Scaling
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train_raw)
X_test_s = scaler.transform(X_test_raw)

# 3. Define Experiment Parameters
pca_sizes = [64, 128, 512, None]  # None means "No PCA"
results_list = []

# Loop over PCA settings
for pca_dim in pca_sizes:
    print(f"\n{'='*20} TESTING PCA DIM: {pca_dim if pca_dim else 'FULL (3072)'} {'='*20}")
    
    if pca_dim:
        pca = PCA(n_components=pca_dim, random_state=42)
        X_train_work = pca.fit_transform(X_train_s)
        X_test_work = pca.transform(X_test_s)
    else:
        X_train_work = X_train_s
        X_test_work = X_test_s
        pca = None

    # Define Models for this dimension
    # Note: TabPFN is excluded from "None" PCA because it crashes above 2000 features
    current_models = {
        "LogisticRegression": LogisticRegression(max_iter=1000, class_weight='balanced'),
        "XGBoost": XGBClassifier(n_estimators=100, learning_rate=0.1, use_label_encoder=False, eval_metric='logloss'),
        "RandomForest": RandomForestClassifier(n_estimators=100, n_jobs=-1)
    }
    
    # Only add TabPFN if features < 2000
    # if pca_dim and pca_dim <= 2000:
    #     current_models["TabPFN"] = TabPFNClassifier(device='cpu')

    for name, model in current_models.items():
        print(f"Running {name}...")
        try:
            model.fit(X_train_work, y_train)
            
            # Prediction handling
            if name == "TabPFN":
                # Batched prediction for memory safety
                batch_size = 32
                probs = np.concatenate([model.predict_proba(X_test_work[i:i+batch_size]) 
                                        for i in range(0, X_test_work.shape[0], batch_size)])
            else:
                probs = model.predict_proba(X_test_work)
            
            preds = np.argmax(probs, axis=1)
            acc = accuracy_score(y_test, preds)
            auc = roc_auc_score(y_test, probs[:, 1])
            
            results_list.append({
                "Model": name,
                "PCA_Dim": pca_dim if pca_dim else 3072,
                "Accuracy": acc,
                "ROC_AUC": auc
            })
            
            # Save the best version (optional: add logic to only save if it's the top performer)
            save_path = Path(f"models/exp_{name}_{pca_dim}")
            save_path.mkdir(parents=True, exist_ok=True)
            joblib.dump(model, save_path / "model.joblib")
            if pca: joblib.dump(pca, save_path / "pca.joblib")

        except Exception as e:
            print(f"Failed {name} at dim {pca_dim}: {e}")

# 4. Final Summary Table
summary_df = pd.DataFrame(results_list)
print("\n--- Final Experiment Results ---")
print(summary_df.sort_values(by="ROC_AUC", ascending=False))