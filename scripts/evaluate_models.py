import os
import sys

# Add backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.ml.evaluator import GroundTruthEvaluator

def main():
    print("================================================================")
    print("  VARUNA Ground Truth ML Model Evaluation Dashboard")
    print("================================================================")
    
    result = GroundTruthEvaluator.evaluate_all_models()
    
    print("\nEvaluated Models:")
    for m in result.models:
        print(f"\n- Model: {m.model_name} ({m.task})")
        print(f"  Accuracy:  {m.accuracy * 100:.2f}%")
        print(f"  Precision: {m.precision * 100:.2f}%")
        print(f"  Recall:    {m.recall * 100:.2f}%")
        print(f"  F1-Score:  {m.f1_score * 100:.2f}%")
        print(f"  ROC-AUC:   {m.roc_auc:.4f}")
        print(f"  MAE:       {m.mae:.2f}")
        print(f"  RMSE:      {m.rmse:.2f}")

    print("\nConfusion Matrix:")
    print("Labels:", result.confusion_matrix.get("labels"))
    for row in result.confusion_matrix.get("matrix", []):
        print(" ", row)

    print(f"\nGround Truth Sample Count: {result.ground_truth_sample_count}")
    print(f"Evaluation Note: {result.evaluation_note}")
    print("================================================================")

if __name__ == "__main__":
    main()
