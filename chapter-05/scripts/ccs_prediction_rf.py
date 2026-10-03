#!/usr/bin/env python3
"""Train a time-ordered Random Forest CCS example on the Chapter 5 workbook.
Run from this directory or pass workbook path: python ccs_prediction_rf.py [workbook.xlsx]
Outputs: ccs_predictions_test.csv and ccs_model_metrics.txt in current directory.
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline

DEFAULT = Path(__file__).resolve().parents[1] / "data" / "Pellet_Induration_QC_Chapter5_Dataset.xlsx"
path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
p = pd.read_excel(path, sheet_name="Fact_Process_Hourly", parse_dates=["Timestamp"])
q = pd.read_excel(path, sheet_name="Fact_QC_Samples", parse_dates=["Sample_Timestamp"])
p = p.sort_values("Timestamp").set_index("Timestamp")

# Associate each QC observation with the hourly process record two hours earlier.
# Dataset convention should be verified before production use.
q["Process_Anchor_Timestamp"] = q["Sample_Timestamp"] - pd.Timedelta(hours=2)
process_cols = ["Temp_UDD_C", "Temp_DDD_C", "Temp_PH_C", "Temp_Firing_C",
                "Temp_AfterFiring_C", "Temp_Cooling_C", "Windbox_Avg_DP_kPa",
                "O2_Firing_pct", "Bed_Height_mm", "Pallet_Speed_mpm"]
proc = p[process_cols].copy()
proc.index = pd.to_datetime(proc.index)
q = q.sort_values("Process_Anchor_Timestamp")
proc_reset = proc.reset_index().rename(columns={"Timestamp": "Process_Anchor_Timestamp"})
joined = pd.merge_asof(q, proc_reset, on="Process_Anchor_Timestamp", direction="backward", tolerance=pd.Timedelta(minutes=60))
feed_cols = [c for c in ["Feed_Fe_pct", "Feed_FeO_pct", "Feed_SiO2_pct", "Feed_Al2O3_pct",
                         "Feed_CaO_pct", "Feed_MgO_pct", "Basicity_B2", "Basicity_B4",
                         "Blaine_cm2g", "Green_Moisture_pct"] if c in joined.columns]
feature_cols = process_cols + feed_cols
joined = joined.dropna(subset=["CCS_Mean_daN", "Sample_Timestamp"])
joined = joined.sort_values("Sample_Timestamp").reset_index(drop=True)
if len(joined) < 10:
    raise ValueError(f"Too few joined rows ({len(joined)}). Check timestamps and two-hour lag convention.")

cut = int(len(joined) * 0.8)
train, test = joined.iloc[:cut], joined.iloc[cut:]
X_train, X_test = train[feature_cols], test[feature_cols]
y_train, y_test = train["CCS_Mean_daN"], test["CCS_Mean_daN"]
model = make_pipeline(SimpleImputer(strategy="median"),
    RandomForestRegressor(n_estimators=300, min_samples_leaf=3, random_state=42, n_jobs=-1))
model.fit(X_train, y_train)
pred = model.predict(X_test)
rmse = mean_squared_error(y_test, pred) ** 0.5
baseline = np.repeat(y_train.mean(), len(y_test))
metrics = {
    "rows_joined": len(joined), "train_rows": len(train), "test_rows": len(test),
    "test_MAE": mean_absolute_error(y_test, pred), "test_RMSE": rmse,
    "test_R2": r2_score(y_test, pred), "baseline_mean_MAE": mean_absolute_error(y_test, baseline),
}
result = test[["Sample_ID", "Sample_Timestamp", "CCS_Mean_daN"]].copy()
result["CCS_Predicted_daN"] = pred
result.to_csv("ccs_predictions_test.csv", index=False)
Path("ccs_model_metrics.txt").write_text("\n".join(f"{k}: {v}" for k, v in metrics.items()) + "\n", encoding="utf-8")
print("Features:", feature_cols)
print("Metrics:", metrics)
print("Wrote ccs_predictions_test.csv and ccs_model_metrics.txt")
