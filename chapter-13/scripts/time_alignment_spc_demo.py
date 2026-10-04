# scripts/time_alignment_spc_demo.py
import pandas as pd

def run_alignment_demo():
    excel_path = "data/ch13_factory_data_architecture_training.xlsx"
    print(f"Loading data from {excel_path}...")
    df_proc = pd.read_excel(excel_path, sheet_name="process_timeseries")
    df_qc = pd.read_excel(excel_path, sheet_name="qc_lab_results")
    df_proc["timestamp"] = pd.to_datetime(df_proc["timestamp"])
    df_qc["sample_time"] = pd.to_datetime(df_qc["sample_time"])
    valid_proc = df_proc[df_proc["Quality_DiscMoisture"] == "Good"].sort_values("timestamp").copy()
    valid_proc["moisture_60m_mean"] = valid_proc["DiscMoisture_PV"].rolling(60, min_periods=30).mean()
    aligned = pd.merge_asof(
        df_qc.sort_values("sample_time"),
        valid_proc[["timestamp", "moisture_60m_mean"]],
        left_on="sample_time", right_on="timestamp", direction="backward"
    )
    print("Time Alignment completed successfully.")
    sub = aligned.dropna(subset=["moisture_60m_mean", "Lab_Moisture_Pct"])
    corr = sub["moisture_60m_mean"].corr(sub["Lab_Moisture_Pct"])
    print(f"Pearson Correlation: {corr:.3f}")

if __name__ == "__main__":
    run_alignment_demo()
