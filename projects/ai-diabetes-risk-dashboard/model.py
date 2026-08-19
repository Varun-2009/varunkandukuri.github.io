from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


FEATURES = ["age", "bmi", "glucose", "blood_pressure", "activity_minutes", "family_history"]


def generate_synthetic_data(rows: int = 2500, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    frame = pd.DataFrame({
        "age": rng.integers(18, 81, rows),
        "bmi": np.clip(rng.normal(28, 6, rows), 16, 55),
        "glucose": np.clip(rng.normal(108, 25, rows), 55, 240),
        "blood_pressure": np.clip(rng.normal(78, 13, rows), 45, 140),
        "activity_minutes": np.clip(rng.normal(145, 80, rows), 0, 500),
        "family_history": rng.binomial(1, 0.32, rows),
    })
    logit = (
        -8.1 + 0.035 * frame["age"] + 0.075 * frame["bmi"]
        + 0.032 * frame["glucose"] + 0.55 * frame["family_history"]
        - 0.003 * frame["activity_minutes"]
    )
    probability = 1 / (1 + np.exp(-logit))
    frame["diabetes_risk_label"] = rng.binomial(1, probability)
    for column in ["bmi", "glucose", "blood_pressure"]:
        frame.loc[rng.random(rows) < 0.04, column] = np.nan
    return frame


@dataclass
class ModelBundle:
    pipeline: Pipeline
    x_test: pd.DataFrame
    y_test: pd.Series
    probabilities: np.ndarray
    auc: float


def train_model(frame: pd.DataFrame) -> ModelBundle:
    x = frame[FEATURES]
    y = frame["diabetes_risk_label"]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.25, random_state=42, stratify=y
    )
    preprocess = ColumnTransformer([
        ("numeric", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), FEATURES)
    ])
    pipeline = Pipeline([
        ("preprocess", preprocess),
        ("model", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)),
    ])
    pipeline.fit(x_train, y_train)
    probabilities = pipeline.predict_proba(x_test)[:, 1]
    return ModelBundle(pipeline, x_test, y_test, probabilities, roc_auc_score(y_test, probabilities))

