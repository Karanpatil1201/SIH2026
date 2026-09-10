import os
import sys

# Add project root and backend directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_path = os.path.join(project_root, "backend")
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from scripts.preprocess import generate_and_preprocess_dataset
from scripts.train_risk_model import train_xgboost_risk
from scripts.train_anomaly_model import train_isolation_forest
from scripts.train_fisheries_model import train_fisheries_model
from scripts.train_ecosystem_model import train_ecosystem_model

def main():
    print("================================================================")
    print("  VARUNA Marine Intelligence ML Training Pipeline")
    print("================================================================")
    
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "processed", "marine_training_data.csv"))
    print("\n[Step 1] Preprocessing and aligning multi-source training data...")
    generate_and_preprocess_dataset(n_samples=3000, save_path=data_path)

    print("\n[Step 2] Training XGBoost Risk Scoring Regressor...")
    train_xgboost_risk()

    print("\n[Step 3] Training Isolation Forest Environmental Outlier Detector...")
    train_isolation_forest()

    print("\n[Step 4] Training Fisheries Catch Quantity Model...")
    train_fisheries_model()

    print("\n[Step 5] Training Ecosystem Bleaching Severity Model...")
    train_ecosystem_model()

    print("\n[VARUNA ML Pipeline] Complete! All models trained and saved to models/ directory.")
    print("================================================================")

if __name__ == "__main__":
    main()
