# backend/scoring.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import shap # type: ignore

class ScoringEngine:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=200, random_state=42)
        self.scaler = StandardScaler()
        self.model_version = "rf-1.0"

    def fit_if_needed(self, X: pd.DataFrame, y: pd.Series):
        # Train a quick baseline if model not fitted
        self.scaler.fit(X)
        Xs = self.scaler.transform(X)
        self.model.fit(Xs, y)

    def score(self, X: pd.DataFrame) -> np.ndarray:
        Xs = self.scaler.transform(X)
        return self.model.predict(Xs)

    def explain(self, X: pd.DataFrame) -> pd.DataFrame:
        Xs = self.scaler.transform(X)
        explainer = shap.TreeExplainer(self.model)
        shap_vals = explainer.shap_values(Xs)
        # Return per-sample, per-feature SHAP
        return pd.DataFrame(shap_vals, columns=X.columns)

# Simple heuristic target for demo (replace with historical defaults, PD, etc.)
def synth_target(df: pd.DataFrame) -> pd.Series:
    # Lower debt_to_revenue, higher cash_ratio, higher sentiment → higher score
    base = 700 \
        - 200*df["debt_to_revenue"] \
        + 150*df["cash_ratio"] \
        + 50*df["news_sentiment"] \
        + 0.05*(df["revenue"] - df["debt"]).clip(lower=-500, upper=1500) / 10
    # Clamp to 300-900
    return base.clip(lower=300, upper=900)
