# راهنمای عملی فصل ۱۳ در پایتون (Python)

## ۱. هدف
بارگذاری داده‌های چندجدوله، هم‌ترازی زمانی با `pd.merge_asof` و محاسبه ویژگی‌های پنجره غلطان.

## ۲. کد نمونه
```python
import pandas as pd
excel_path = "../data/ch13_factory_data_architecture_training.xlsx"
df_proc = pd.read_excel(excel_path, sheet_name="process_timeseries")
df_qc = pd.read_excel(excel_path, sheet_name="qc_lab_results")
df_proc["timestamp"] = pd.to_datetime(df_proc["timestamp"])
df_qc["sample_time"] = pd.to_datetime(df_qc["sample_time"])
good_proc = df_proc[df_proc["Quality_DiscMoisture"] == "Good"].sort_values("timestamp").copy()
good_proc["rolling_moisture_pv"] = good_proc["DiscMoisture_PV"].rolling(window=60, min_periods=30).mean()
aligned_df = pd.merge_asof(
    df_qc.sort_values("sample_time"),
    good_proc[["timestamp", "rolling_moisture_pv", "BallingDisc_Speed_PV"]],
    left_on="sample_time", right_on="timestamp", direction="backward"
)
print(aligned_df[["SampleID", "sample_time", "Lab_Moisture_Pct", "rolling_moisture_pv"]].head())
```
