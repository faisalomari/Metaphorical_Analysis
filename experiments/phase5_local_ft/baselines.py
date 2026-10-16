"""Non-neural baselines per target x split x seed: majority, always-positive,
TF-IDF char n-gram + logistic regression. No GPU needed."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from metrics_utils import best_threshold, prf
import phase5_config as config


def majority_baseline(train_labels: list, test_labels: list) -> dict:
    majority_class = 1 if sum(train_labels) > len(train_labels) / 2 else 0
    y_pred = [majority_class] * len(test_labels)
    return {"majority_class": majority_class, **prf(test_labels, y_pred)}


def always_positive_baseline(test_labels: list) -> dict:
    y_pred = [1] * len(test_labels)
    return prf(test_labels, y_pred)


def tfidf_logreg_baseline(train_texts, train_labels, val_texts, val_labels, test_texts, test_labels) -> dict:
    vec = TfidfVectorizer(analyzer="char", ngram_range=(2, 4), min_df=2)
    X_train = vec.fit_transform(train_texts)
    X_val = vec.transform(val_texts)
    X_test = vec.transform(test_texts)

    clf = LogisticRegression(class_weight="balanced", max_iter=2000)
    clf.fit(X_train, train_labels)

    val_probs = clf.predict_proba(X_val)[:, 1].tolist()
    val_best = best_threshold(val_labels, val_probs, config.THRESHOLD_GRID)
    thr = val_best["threshold"]

    test_probs = clf.predict_proba(X_test)[:, 1].tolist()
    y_pred = [1 if p >= thr else 0 for p in test_probs]
    test_metrics = prf(test_labels, y_pred)
    return {"threshold": thr, "val_f1": val_best["f1"], "test": test_metrics}
