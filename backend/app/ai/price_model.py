"""ML price and duration prediction — load joblib models and predict."""
import os
from pathlib import Path
from typing import Any

try:
    import joblib
    import numpy as np
except ImportError:
    joblib = None
    np = None

# Paths: backend/ml/price_model.pkl and duration_model.pkl
ML_DIR = Path(__file__).resolve().parent.parent.parent / "ml"
PRICE_MODEL_PATH = ML_DIR / "price_model.pkl"
DURATION_MODEL_PATH = ML_DIR / "duration_model.pkl"

_price_model = None
_duration_model = None
_encoders = None  # dict of label encoders for categoricals


def _load_models() -> None:
    global _price_model, _duration_model, _encoders
    if _price_model is not None and _duration_model is not None:
        return
    if joblib is None:
        return
    if PRICE_MODEL_PATH.exists():
        try:
            data = joblib.load(PRICE_MODEL_PATH)
            if isinstance(data, dict):
                _price_model = data.get("model")
                _encoders = data.get("encoders", {})
            else:
                _price_model = data
        except Exception:
            pass
    if DURATION_MODEL_PATH.exists():
        try:
            data = joblib.load(DURATION_MODEL_PATH)
            if isinstance(data, dict):
                _duration_model = data.get("model")
                if _encoders is None:
                    _encoders = data.get("encoders", {})
            else:
                _duration_model = data
        except Exception:
            pass


def predict(
    problem_type: str,
    severity: int,
    surface_area_m2: float,
    complexity: str,
    nb_elements_affected: int,
    city: str,
) -> dict[str, float]:
    """
    Returns {"price": float, "duration_hours": float}.
    Blends ML model output with calibrated Moroccan market rates.
    """
    # Normalize noisy AI values so predictions stay realistic.
    severity = max(1, min(5, int(severity)))
    surface_area_m2 = max(0.2, min(25.0, float(surface_area_m2)))
    nb_elements_affected = max(1, min(20, int(nb_elements_affected)))

    # ── Moroccan market reference rates (realistic 2024 prices in MAD) ──────
    # (price_per_m2_base, min_price, max_price, hours_per_m2, min_hours)
    MARKET_RATES = {
        "zlayji":      {"per_m2": 180, "min": 120,  "max": 1200, "h_per_m2": 1.3, "min_h": 1.0},
        "sebbagh":     {"per_m2": 45,  "min": 90,   "max": 700,  "h_per_m2": 0.7, "min_h": 1.0},
        "gebbas":      {"per_m2": 55,  "min": 100,  "max": 850,  "h_per_m2": 0.9, "min_h": 1.0},
        "plombier":    {"per_m2": 0,   "min": 130,  "max": 950,  "h_per_m2": 0,   "min_h": 1.0},
        "electricien": {"per_m2": 0,   "min": 110,  "max": 900,  "h_per_m2": 0,   "min_h": 1.0},
    }
    # Complexity multipliers
    COMPLEXITY_MUL = {"simple": 0.8, "moyenne": 1.0, "complexe": 1.4}
    # Severity multipliers (1-5 → 0.7 to 1.5)
    sev_mul = 0.6 + severity * 0.18

    pt = problem_type.lower()
    rates = MARKET_RATES.get(pt, MARKET_RATES["gebbas"])
    comp_mul = COMPLEXITY_MUL.get(complexity.lower(), 1.0)

    # Market-based estimate
    surf = surface_area_m2
    if rates["per_m2"] > 0:
        market_price = rates["per_m2"] * surf * sev_mul * comp_mul
        market_hours = rates["h_per_m2"] * surf * comp_mul
    else:
        # For plombier/electricien: nb_elements drives price
        nb = nb_elements_affected
        base_per_element = {"plombier": 250, "electricien": 200}.get(pt, 250)
        market_price = base_per_element * nb * sev_mul * comp_mul
        market_hours = 1.5 * nb * comp_mul

    market_hours = max(rates["min_h"], market_hours)

    # Try ML model prediction
    ml_price = market_price   # default to market if ML unavailable
    ml_hours = market_hours
    _load_models()
    if np is not None:
        if _encoders:
            try:
                pt_enc  = _encoders["problem_type"].transform([pt])[0]
                comp_enc = _encoders["complexity"].transform([complexity.lower()])[0]
                city_enc = _encoders["city"].transform([city.lower()])[0]
            except Exception:
                pt_enc = comp_enc = city_enc = 0
        else:
            problem_types = ["zlayji", "sebbagh", "gebbas", "plombier", "electricien"]
            complexities  = ["simple", "moyenne", "complexe"]
            cities = ["agadir", "inezgane", "ait_melloul", "tiznit", "taroudant",
                      "biougra", "chtouka", "massa", "drarga", "dcheira"]
            pt_enc   = problem_types.index(pt) if pt in problem_types else 0
            comp_enc = complexities.index(complexity.lower()) if complexity.lower() in complexities else 1
            city_enc = cities.index(city.lower()) if city.lower() in cities else 0

        X = np.array([[pt_enc, severity, surf, comp_enc, nb_elements_affected, city_enc]], dtype=float)
        if _price_model is not None:
            try:
                ml_price = float(_price_model.predict(X)[0])
            except Exception:
                pass
        if _duration_model is not None:
            try:
                ml_hours = float(_duration_model.predict(X)[0])
            except Exception:
                pass

    # Blend: 40% ML + 60% market (market is more reliable for small jobs)
    blended_price = 0.4 * ml_price + 0.6 * market_price
    blended_hours = 0.4 * ml_hours + 0.6 * market_hours

    # Clamp to realistic per-type bounds
    final_price = max(rates["min"], min(rates["max"], blended_price))
    final_hours = max(rates["min_h"], min(16.0, blended_hours))

    return {
        "price": round(final_price),
        "duration_hours": round(final_hours, 1),
    }

