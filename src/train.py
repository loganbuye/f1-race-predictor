import pandas as pd
import pickle
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
from src.features import build_features

MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

FEATURE_COLS = [
    "grid_position",
    "driver_avg_finish_last5",
    "constructor_avg_finish_last5",
    "driver_circuit_avg_finish",
    "championship_position"
]
LABEL_COL = "top10"

def train():
    print("Building features...")
    df = build_features(years=(2023, 2024))

    train_df = df[df["year"] == 2023]
    test_df = df[df["year"] == 2024]

    x_train = train_df[FEATURE_COLS]
    y_train = train_df[LABEL_COL]
    x_test = test_df[FEATURE_COLS]
    y_test = test_df[LABEL_COL]

    print(f"Training rows: {len(train_df)} | Test rows: {len(test_df)}")

    print("Training random forest...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=6,
        min_samples_leaf=5,
        random_state=42,
        class_weight="balanced"
    )
    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)

    print("\nEvaluation on 2024 season:")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")
    print(f"Precision: {precision_score(y_test, y_pred):.3f}")
    print(f"Recall: {recall_score(y_test, y_pred):.3f}")
    print(f"F1 Score: {f1_score(y_test, y_pred):.3f}")

    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"True Negatives (Correctly predicted not top 10): {cm[0][0]}")
    print(f"False Positives (Incorrectly predicted top 10): {cm[0][1]}")
    print(f"False Negatives (Incorrectly predicted not top 10): {cm[1][0]}")
    print(f"True Positives (Correctly predicted top 10): {cm[1][1]}")

    print("\nFeature Importances:")
    for col, importance in sorted(
        zip(FEATURE_COLS, model.feature_importances_),
        key=lambda x: -x[1]
    ):
        bar = "#" * int(importance * 40)
        print(f"{col:<35} | {importance:.3f} {bar}")

    model_path = MODELS_DIR / "rf_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump({"model": model, "feature_cols": FEATURE_COLS}, f)
        print(f"\nModel saved to {model_path}")

if __name__ == "__main__":
    train()
