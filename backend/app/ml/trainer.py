"""
LandSense AI — ML Model Trainer.

Trains multiple ML models with stratified k-fold cross-validation,
evaluates performance, selects the best model, and persists artefacts.
"""
from __future__ import annotations
import json
import logging
import time
from pathlib import Path
from typing import Any, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix,
)
from sklearn.preprocessing import LabelEncoder, StandardScaler

from app.config import settings

logger = logging.getLogger("landsense.ml.trainer")

# ── Model registry ────────────────────────────────────────────────────────────
MODEL_FACTORY: dict[str, Any] = {
    "logistic_regression": lambda seed: LogisticRegression(
        max_iter=1000, class_weight="balanced", random_state=seed
    ),
    "decision_tree": lambda seed: DecisionTreeClassifier(
        max_depth=10, class_weight="balanced", random_state=seed
    ),
    "random_forest": lambda seed: RandomForestClassifier(
        n_estimators=200, max_depth=15, class_weight="balanced",
        random_state=seed, n_jobs=-1
    ),
}

# Optional boosting models — imported lazily to handle missing deps
def _make_xgboost(seed: int):
    from xgboost import XGBClassifier
    return XGBClassifier(
        n_estimators=200, max_depth=6, learning_rate=0.1,
        use_label_encoder=False, eval_metric="logloss",
        random_state=seed, n_jobs=-1,
    )

def _make_catboost(seed: int):
    from catboost import CatBoostClassifier
    return CatBoostClassifier(
        iterations=200, depth=6, learning_rate=0.1,
        random_seed=seed, verbose=0,
    )

MODEL_FACTORY["xgboost"] = _make_xgboost
MODEL_FACTORY["catboost"] = _make_catboost


def _preprocess(
    df: pd.DataFrame,
    selected_features: Optional[list[str]] = None,
) -> tuple[pd.DataFrame, pd.Series, list[str], StandardScaler, dict]:
    """Clean and prepare data for training.

    Returns: (X, y, feature_names, scaler, preprocessing_summary)
    """
    drop_cols = {"latitude", "longitude", "id"}
    label_col = "label"

    if label_col not in df.columns:
        raise ValueError("Dataset must have a 'label' column")

    # Select features
    available = [c for c in df.columns if c not in drop_cols and c != label_col]
    if selected_features:
        feature_cols = [c for c in selected_features if c in available]
    else:
        feature_cols = available

    # Build summary
    n_before = len(df)
    missing_before = int(df[feature_cols].isna().sum().sum())

    # Drop rows with excessive missing values (> 50% of features missing)
    threshold = len(feature_cols) * 0.5
    df = df.dropna(subset=feature_cols, thresh=int(threshold))

    # Drop duplicates
    n_dupes = int(df.duplicated(subset=feature_cols).sum())
    df = df.drop_duplicates(subset=feature_cols)

    # Encode categoricals
    cat_cols = df[feature_cols].select_dtypes(include=["object"]).columns.tolist()
    encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

    # Fill remaining NaN with column median
    for col in feature_cols:
        if df[col].isna().any():
            df[col] = df[col].fillna(df[col].median())

    X = df[feature_cols].values.astype(np.float64)
    y = df[label_col].values.astype(int)

    # Scale numerical features
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # Features dropped due to missing threshold
    dropped = [c for c in available if c not in feature_cols]

    summary = {
        "total_samples_before": n_before,
        "total_samples_after": len(df),
        "missing_values_removed": missing_before,
        "duplicate_rows_removed": n_dupes,
        "features_before": len(available),
        "features_after": len(feature_cols),
        "features_dropped": dropped,
        "class_distribution": {
            "landslide": int((y == 1).sum()),
            "non_landslide": int((y == 0).sum()),
        },
    }

    return pd.DataFrame(X, columns=feature_cols), pd.Series(y), feature_cols, scaler, summary


def run_training_pipeline(
    training_run_id: int,
    dataset_path: str,
    model_names: list[str],
    cv_folds: int = 5,
    random_seed: int = 42,
    balancing_method: Optional[str] = "class_weight",
    selected_features: Optional[list[str]] = None,
    db=None,
) -> dict[str, Any]:
    """Execute the full training pipeline.

    1. Load CSV  →  2. Preprocess  →  3. Train each model with stratified CV
    4. Evaluate  →  5. Select best  →  6. Save artefacts
    """
    from app.models import ModelResult

    df = pd.read_csv(dataset_path)
    X_df, y, feature_names, scaler, prep_summary = _preprocess(
        df, selected_features
    )
    X = X_df.values

    logger.info(
        "Preprocessed: %d samples, %d features, class dist: %s",
        len(X), len(feature_names), prep_summary["class_distribution"],
    )

    # Save scaler and feature config
    store = Path(settings.model_store_dir) / f"run_{training_run_id}"
    store.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, store / "scaler.joblib")
    with open(store / "feature_config.json", "w") as f:
        json.dump({"features": feature_names}, f)

    skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_seed)

    best_roc = -1.0
    best_model_id = None
    best_model_name = None
    results_list = []

    for name in model_names:
        if name not in MODEL_FACTORY:
            logger.warning("Unknown model: %s — skipping", name)
            continue

        logger.info("Training model: %s", name)
        t0 = time.time()

        try:
            model = MODEL_FACTORY[name](random_seed)

            # Cross-validate
            cv_results = cross_validate(
                model, X, y, cv=skf,
                scoring=["accuracy", "precision", "recall", "f1", "roc_auc"],
                return_train_score=False,
            )

            # Fit on full data for final model
            model.fit(X, y)
            train_time = round(time.time() - t0, 2)

            # Metrics (CV means)
            acc = round(float(np.mean(cv_results["test_accuracy"])), 4)
            prec = round(float(np.mean(cv_results["test_precision"])), 4)
            rec = round(float(np.mean(cv_results["test_recall"])), 4)
            f1 = round(float(np.mean(cv_results["test_f1"])), 4)
            auc = round(float(np.mean(cv_results["test_roc_auc"])), 4)
            auc_std = round(float(np.std(cv_results["test_roc_auc"])), 4)

            # Confusion matrix on full training set (for display)
            y_pred = model.predict(X)
            cm = confusion_matrix(y, y_pred).tolist()

            # Feature importance
            fi = _extract_importance(model, feature_names)

            # Save model
            model_path = store / f"{name}.joblib"
            joblib.dump(model, model_path)

            mr = ModelResult(
                training_run_id=training_run_id,
                model_name=name,
                accuracy=acc,
                precision_score=prec,
                recall=rec,
                f1_score=f1,
                roc_auc=auc,
                roc_auc_std=auc_std,
                training_time_s=train_time,
                model_file_path=str(model_path),
                confusion_matrix=json.dumps(cm),
                feature_importance=json.dumps(fi),
                is_best=False,
            )
            db.add(mr)
            db.commit()
            db.refresh(mr)

            results_list.append(mr)

            if auc > best_roc:
                best_roc = auc
                best_model_id = mr.id
                best_model_name = name

            logger.info(
                "Model %s: AUC=%.4f ± %.4f, F1=%.4f, time=%.1fs",
                name, auc, auc_std, f1, train_time,
            )

        except Exception as exc:
            logger.error("Failed to train %s: %s", name, exc, exc_info=True)

    # Mark best model
    if best_model_id:
        for mr in results_list:
            if mr.id == best_model_id:
                mr.is_best = True
            else:
                mr.is_best = False
        db.commit()

    # Save preprocessing summary
    with open(store / "preprocessing_summary.json", "w") as f:
        json.dump(prep_summary, f, indent=2)

    return {
        "n_features": len(feature_names),
        "n_samples": len(X),
        "features_used": feature_names,
        "n_models": len(results_list),
        "best_model_id": best_model_id,
        "best_model_name": best_model_name,
        "best_roc_auc": best_roc,
    }


def _extract_importance(model, feature_names: list[str]) -> list[dict]:
    """Extract feature importance from a trained model."""
    importances = None

    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_[0]) if model.coef_.ndim > 1 else np.abs(model.coef_)

    if importances is None:
        return []

    total = float(np.sum(importances)) or 1.0
    items = [
        {"feature": name, "importance": round(float(imp / total), 4)}
        for name, imp in zip(feature_names, importances)
    ]
    items.sort(key=lambda x: x["importance"], reverse=True)
    return items
