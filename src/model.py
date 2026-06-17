from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.config import RANDOM_STATE, TEST_SIZE


DROP_FROM_FEATURES = {
    "risco_alto",
    "nivel_risco",
    "data",
    "hora",
    "data_hora",
    "classificacao",
    "mortos",
    "feridos_graves",
    "feridos_leves",
    "feridos",
    "ilesos",
    "ignorados",
    "pessoas",
}


def train_risk_model(df: pd.DataFrame, reports_dir: str | Path) -> dict[str, Path] | None:
    if "risco_alto" not in df.columns:
        return None

    model_df = df.copy()
    model_df = model_df.dropna(subset=["risco_alto"])
    if model_df["risco_alto"].nunique() < 2 or len(model_df) < 30:
        return None

    y = model_df["risco_alto"].astype(int)
    X = model_df.drop(columns=[column for column in DROP_FROM_FEATURES if column in model_df.columns])

    usable_columns = [
        column
        for column in X.columns
        if X[column].nunique(dropna=True) > 1 and not column.lower().startswith("id")
    ]
    X = X[usable_columns]

    numeric_features = X.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_features = X.select_dtypes(exclude=["number", "bool"]).columns.tolist()

    if not numeric_features and not categorical_features:
        return None

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="median"), numeric_features),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore", min_frequency=5)),
                    ]
                ),
                categorical_features,
            ),
        ]
    )

    classifier = RandomForestClassifier(
        n_estimators=250,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=1,
    )

    pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("classifier", classifier)])
    stratify = y if y.value_counts().min() >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=stratify,
    )

    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)

    reports_path = Path(reports_dir)
    reports_path.mkdir(parents=True, exist_ok=True)
    metrics_path = reports_path / "metricas_modelo.txt"
    model_path = reports_path / "modelo_risco_acidentes.joblib"

    metrics = [
        "Modelo: RandomForestClassifier",
        f"Registros treino: {len(X_train)}",
        f"Registros teste: {len(X_test)}",
        "",
        "Matriz de confusao:",
        str(confusion_matrix(y_test, predictions)),
        "",
        "Relatorio de classificacao:",
        classification_report(y_test, predictions, zero_division=0),
    ]
    metrics_path.write_text("\n".join(metrics), encoding="utf-8")
    joblib.dump(pipeline, model_path)

    return {"metrics": metrics_path, "model": model_path}