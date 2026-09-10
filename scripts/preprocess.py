import os
import sys
import numpy as np
import pandas as pd

# Add backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

def generate_and_preprocess_dataset(n_samples: int = 2500, save_path: str = None) -> pd.DataFrame:
    """
    Simulates / processes historical multi-source marine dataset
    aligning ocean dynamics, meteorological parameters, and satellite indicators.
    """
    np.random.seed(42)

    # Physical Ocean Features
    sst = np.random.uniform(22.0, 32.5, n_samples)
    wave_h = np.random.exponential(scale=1.6, size=n_samples) + 0.4
    wave_h = np.clip(wave_h, 0.4, 7.5)
    wave_p = np.clip(wave_h * 1.8 + np.random.normal(5.0, 1.5, n_samples), 3.5, 16.0)
    swell_h = wave_h * np.random.uniform(0.45, 0.85, n_samples)
    current_v = np.random.exponential(scale=0.45, size=n_samples) + 0.1
    current_v = np.clip(current_v, 0.1, 2.8)

    # Meteorological Features
    wind_s = np.random.exponential(scale=14.0, size=n_samples) + 5.0
    wind_s = np.clip(wind_s, 5.0, 85.0)
    pressure = 1014.0 - (wind_s / 85.0) * 35.0 + np.random.normal(0, 3.0, n_samples)
    pressure = np.clip(pressure, 965.0, 1025.0)
    precip = np.maximum(0.0, (1005.0 - pressure) * 1.5 + np.random.exponential(scale=3.0, size=n_samples))
    precip = np.clip(precip, 0.0, 80.0)

    # Biogeochemical & Satellite Features
    salinity = np.random.uniform(32.5, 36.8, n_samples)
    chlorophyll = np.random.exponential(scale=0.6, size=n_samples) + 0.1
    chlorophyll = np.clip(chlorophyll, 0.05, 6.0)
    sea_level = np.random.normal(0.05, 0.35, n_samples)

    # Ground-truth physics risk scoring target
    # Higher wave height, strong winds, low cyclonic pressure, high currents drive severe risk
    risk_target = (
        (wave_h / 6.0) * 35.0 +
        (wind_s / 80.0) * 35.0 +
        (np.maximum(0.0, 1013.0 - pressure) / 40.0) * 20.0 +
        (current_v / 2.5) * 10.0
    ) + np.random.normal(0, 1.8, n_samples)

    risk_target = np.clip(risk_target, 0.0, 100.0)

    df = pd.DataFrame({
        "sst": sst,
        "wave_height": wave_h,
        "wave_period": wave_p,
        "swell_height": swell_h,
        "current_velocity": current_v,
        "wind_speed": wind_s,
        "pressure": pressure,
        "precipitation": precip,
        "salinity": salinity,
        "chlorophyll": chlorophyll,
        "sea_level": sea_level,
        "risk_target": risk_target
    })

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        df.to_csv(save_path, index=False)
        print(f"[Preprocess] Preprocessed dataset saved to {save_path} ({len(df)} records)")

    return df

if __name__ == "__main__":
    out = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "processed", "marine_training_data.csv"))
    generate_and_preprocess_dataset(n_samples=3000, save_path=out)
