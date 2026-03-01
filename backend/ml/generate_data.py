"""Generate 1000 realistic synthetic training rows for price/duration ML."""
import pandas as pd
import numpy as np
import random
from pathlib import Path

OUTPUT_PATH = Path(__file__).resolve().parent / "training_data.csv"

problem_types = ["zlayji", "sebbagh", "gebbas", "plombier", "electricien"]
locations = [
    ("agadir", 30.4278, -9.5981),
    ("inezgane", 30.3567, -9.5369),
    ("ait_melloul", 30.3333, -9.5000),
    ("tiznit", 29.6974, -9.7316),
    ("taroudant", 30.4727, -8.8772),
    ("biougra", 30.2167, -9.3667),
    ("chtouka", 30.0833, -9.4667),
    ("massa", 30.0667, -9.6500),
    ("drarga", 30.4833, -9.7167),
    ("dcheira", 30.3833, -9.5167),
]
complexities = ["simple", "moyenne", "complexe"]

base_prices = {
    "zlayji": {"simple": (200, 400), "moyenne": (500, 900), "complexe": (1000, 2500)},
    "sebbagh": {"simple": (150, 300), "moyenne": (400, 800), "complexe": (900, 2000)},
    "gebbas": {"simple": (100, 250), "moyenne": (300, 700), "complexe": (800, 1800)},
    "plombier": {"simple": (150, 350), "moyenne": (400, 900), "complexe": (1000, 3000)},
    "electricien": {"simple": (200, 400), "moyenne": (500, 1000), "complexe": (1200, 3500)},
}

base_durations = {
    "zlayji": {"simple": (2, 4), "moyenne": (4, 8), "complexe": (8, 20)},
    "sebbagh": {"simple": (2, 5), "moyenne": (5, 10), "complexe": (10, 24)},
    "gebbas": {"simple": (1, 3), "moyenne": (3, 6), "complexe": (6, 16)},
    "plombier": {"simple": (1, 3), "moyenne": (3, 7), "complexe": (7, 20)},
    "electricien": {"simple": (1, 2), "moyenne": (2, 6), "complexe": (6, 18)},
}


def main():
    rows = []
    n = 1000
    random.seed(42)
    np.random.seed(42)
    for _ in range(n):
        problem_type = random.choice(problem_types)
        severity = random.randint(1, 5)
        surface_area_m2 = round(random.uniform(0.5, 50), 2)
        complexity = random.choice(complexities)
        nb_elements_affected = random.randint(1, 10)
        city = random.choice(locations)[0]

        price_lo, price_hi = base_prices[problem_type][complexity]
        base_price = random.uniform(price_lo, price_hi)
        price_mad = base_price + (severity * 0.15 * base_price) + (surface_area_m2 * 0.08 * base_price / 10)
        price_mad += random.uniform(-0.05 * price_mad, 0.05 * price_mad)
        price_mad = max(50, round(price_mad, 2))

        dur_lo, dur_hi = base_durations[problem_type][complexity]
        base_dur = random.uniform(dur_lo, dur_hi)
        duration_hours = base_dur + (severity * 0.15 * base_dur) + (surface_area_m2 * 0.08 * base_dur / 20)
        duration_hours += random.uniform(-0.1 * duration_hours, 0.1 * duration_hours)
        duration_hours = max(0.5, round(duration_hours, 2))

        rows.append({
            "problem_type": problem_type,
            "severity": severity,
            "surface_area_m2": surface_area_m2,
            "complexity": complexity,
            "nb_elements_affected": nb_elements_affected,
            "city": city,
            "price_mad": price_mad,
            "duration_hours": duration_hours,
        })
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
