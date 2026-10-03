# 🐍 آموزش تحلیل دیتاست فصل ۵ در **Python**

[⬅ بازگشت به README](../README.md) | [دانلود دیتاست](../data/Pellet_Induration_QC_Chapter5_Dataset.xlsx)

## ۰- نصب پیش‌نیازها
```bash
pip install pandas numpy matplotlib openpyxl statsmodels scipy
```

## ۱- بارگذاری دیتاست
```python
import pandas as pd
f = "../data/Pellet_Induration_QC_Chapter5_Dataset.xlsx"
proc = pd.read_excel(f, sheet_name="Fact_Process_Hourly", parse_dates=["Timestamp"])
qc   = pd.read_excel(f, sheet_name="Fact_QC_Samples",  parse_dates=["Sample_Timestamp"])
erg  = pd.read_excel(f, sheet_name="Ergun_Equation_Lab", header=2)
dim  = pd.read_excel(f, sheet_name="Dim_Zones_Campaigns")
proc.head(), qc.head()
```

## ۲- آمار توصیفی و روند زمانی
```python
print(proc.describe())
print(proc.groupby("Campaign")[["Temp_Firing_C","Windbox_Avg_DP_kPa"]].agg(["mean","std"]))

import matplotlib.pyplot as plt
proc.set_index("Timestamp")[["Temp_UDD_C","Temp_DDD_C","Temp_PH_C","Temp_Firing_C"]].plot(subplots=True, figsize=(10,8))
plt.tight_layout(); plt.show()
```

## ۳- تحلیل معادله ارگون
```python
import numpy as np
def ergun_dp_kPa(L, dp_mm, eps, mu, rho, vs):
    dp = dp_mm/1000
    viscous = 150*((1-eps)**2/eps**3)*(mu*vs/dp**2)
    inertial=1.75*((1-eps)/eps**3)*(rho*vs**2/dp)
    return (viscous+inertial)*L/1000  # kPa

# سناریو زون پخت
print(ergun_dp_kPa(L=0.42, dp_mm=12.5, eps=0.365, mu=5.35e-5, rho=0.222, vs=1.8))
# حساسیت به قطر و تخلخل
for dp in [10,12.5,14]:
    for eps in [0.33,0.365,0.39]:
        print(dp, eps, round(ergun_dp_kPa(0.42,dp,eps,5.35e-5,0.222,1.8),2), "kPa")
```

## ۴- نمودار کنترل I-MR
```python
from statsmodels.tsa.stattools import acf
x = proc["Temp_Firing_C"]
mr = x.diff().abs()
UCL, LCL = x.mean()+3*x.std(), x.mean()-3*x.std()
fig, ax = plt.subplots(figsize=(12,4))
ax.plot(x.index, x, marker='o', ms=2); ax.axhline(UCL, c='r'); ax.axhline(LCL, c='r'); ax.axhline(x.mean(), c='g')
ax.set_title("I-Chart: Temp_Firing_C"); plt.show()
```

## ۵- توانایی فرایند (Cp/Cpk)
```python
def cpk(data, lsl=None, usl=None):
    m, s = data.mean(), data.std(ddof=1)
    cpk = min((usl-m)/3*s if usl else np.inf, (m-lsl)/3*s if lsl else np.inf)
    return (usl-lsl)/(6*s) if usl and lsl else None, cpk

for camp, grp in qc.groupby(qc["Sample_ID"].str[:7].repeat(1).index if False else qc.index):
    pass

qc["Campaign"] = pd.cut(qc.index, bins=[0,60,120,180], labels=["Camp_A","Camp_B","Camp_C"])
for c,g in qc.groupby("Campaign"):
    print(c, cpk(g["CCS_Mean_daN"], lsl=280))  # LSL کمپین را از شیت Dim بردارید
```

## ۶- رگرسیون فرایند ← کیفیت
```python
import statsmodels.api as sm
df = qc.dropna(subset=["Linked_Temp_Firing_C","Linked_O2_Firing_pct","Pellets_FeO_pct"])
X = sm.add_constant(df[["Linked_Temp_Firing_C","Linked_O2_Firing_pct"]])
model = sm.OLS(df["Pellets_FeO_pct"], X).fit()
print(model.summary())
```

## ۷- همبستگی و نقشه حرارتی
```python
cols = ["CCS_Mean_daN","ISO_Tumble_pct","Porosity_pct","Pellets_FeO_pct","Black_Core_pct",
        "Linked_Temp_Firing_C","Linked_O2_Firing_pct","Linked_Pallet_Speed_mpm"]
corr = qc[cols].corr()
fig, ax = plt.subplots(figsize=(8,6))
im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols, rotation=90)
ax.set_yticks(range(len(cols))); ax.set_yticklabels(cols)
plt.colorbar(im); plt.title("Correlation Matrix"); plt.tight_layout(); plt.show()
```

---
[⬅ بازگشت به README](../README.md) | [فصل ۵](../chapter/Chapter05_Text.md) | [اسکریپت کامل آماده](../scripts/analyze_chapter5.py)
