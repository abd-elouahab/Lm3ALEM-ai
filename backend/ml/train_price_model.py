"""Train price and duration models with RandomForestRegressor; save with joblib."""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

ML_DIR = Path(__file__).resolve().parent
DATA_PATH = ML_DIR / "training_data.csv"
PRICE_MODEL_PATH = ML_DIR / "price_model.pkl"
DURATION_MODEL_PATH = ML_DIR / "duration_model.pkl"


def main():
    if not DATA_PATH.exists():
        print(f"Run generate_data.py first to create {DATA_PATH}")
        return
    df = pd.read_csv(DATA_PATH)
    # Encode categoricals
    le_pt = LabelEncoder()
    le_comp = LabelEncoder()
    le_city = LabelEncoder()
    df["problem_type_enc"] = le_pt.fit_transform(df["problem_type"])
    df["complexity_enc"] = le_comp.fit_transform(df["complexity"])
    df["city_enc"] = le_city.fit_transform(df["city"])
    feature_cols = ["problem_type_enc", "severity", "surface_area_m2", "complexity_enc", "nb_elements_affected", "city_enc"]
    X = df[feature_cols].values
    y_price = df["price_mad"].values
    y_duration = df["duration_hours"].values

    encoders = {"problem_type": le_pt, "complexity": le_comp, "city": le_city}

    # Model 1: price
    model_price = RandomForestRegressor(n_estimators=100, random_state=42)
    model_price.fit(X, y_price)
    pred_price = model_price.predict(X)
    print("Price model — MAE:", mean_absolute_error(y_price, pred_price), "R²:", r2_score(y_price, pred_price))
    joblib.dump({"model": model_price, "encoders": encoders, "feature_cols": feature_cols}, PRICE_MODEL_PATH)
    print(f"Saved {PRICE_MODEL_PATH}")

    # Model 2: duration
    model_duration = RandomForestRegressor(n_estimators=100, random_state=42)
    model_duration.fit(X, y_duration)
    pred_duration = model_duration.predict(X)
    print("Duration model — MAE:", mean_absolute_error(y_duration, pred_duration), "R²:", r2_score(y_duration, pred_duration))
    joblib.dump({"model": model_duration, "encoders": encoders, "feature_cols": feature_cols}, DURATION_MODEL_PATH)
    print(f"Saved {DURATION_MODEL_PATH}")


if __name__ == "__main__":
    main()
