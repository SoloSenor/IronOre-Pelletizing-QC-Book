"""اسکریپت تحلیل کامل دیتاست فصل ۵ — کنترل کیفیت اندوراسیون گندله (Straight Grate)
نحوه اجرا: python analyze_chapter5.py
"""
import os
import pandas as pd, numpy as np, matplotlib.pyplot as plt

DATA = os.path.join(os.path.dirname(__file__), "..", "data",
                    "Pellet_Induration_QC_Chapter5_Dataset.xlsx") if False else \
       "../data/Pellet_Induration_QC_Chapter5_Dataset.xlsx"

proc = pd.read_excel(DATA, sheet_name="Fact_Process_Hourly", parse_dates=["Timestamp"])
qc   = pd.read_excel(DATA, sheet_name="Fact_QC_Samples",  parse_dates=["Sample_Timestamp"])

# 1) آمار توصیفی
print(proc.groupby("Campaign")["Temp_Firing_C"].agg(["mean","std","min","max"]))

# 2) روند دمایی
proc.set_index("Timestamp")[["Temp_UDD_C","Temp_DDD_C","Temp_PH_C",
                             "Temp_Firing_C","Temp_AfterFiring_C"]].plot(
    subplots=True, figsize=(10,9), title="Straight Grate Zone Temperatures")
plt.tight_layout(); plt.savefig("zone_temps.png", dpi=150); plt.close()

# 3) معادله ارگون
def ergun_dp_kPa(L, dp_mm, eps, mu, rho, vs):
    dp = dp_mm/1000
    visc = 150*((1-eps)**2/(eps**3))*(mu*vs/(dp**2))
    inert = 1.75*((1-eps)/(eps**3))*(rho*vs**2/(dp))
    return (visc+inert)*L/1000

print("DP_Firing =", round(ergun_dp_kPa(0.42,12.5,0.365,5.35e-5,0.222,1.8),3), "kPa")
print("DP_Firing_dp10 =", round(ergun_dp_kPa(0.42,10,0.365,5.35e-5,0.222,1.8),3), "kPa")

# 4) نمودار کنترل I-Chart
x = proc["Temp_Firing_C"].values
m, s = x.mean(), x.std(ddof=1)
fig, ax = plt.subplots(figsize=(12,4))
ax.plot(x, marker="o", ms=2); ax.axhline(m, c="g"); ax.axhline(m+3*s, c="r"); ax.axhline(m-3*s, c="r")
ax.set_title("I-Chart: Temp_Firing_C"); plt.tight_layout(); plt.savefig("ichart_firing.png", dpi=150); plt.close()

# 5) Cpk برای CCS (حد فاصل Camp_A: 280 daN)
def cpk(d, lsl=None, usl=None):
    mu, sd = d.mean(), d.std(ddof=1)
    v = min(((usl-mu)/sd) if usl else np.inf, ((mu-lsl)/sd) if lsl else np.inf)/3
    return v
print("Cpk CCS (LSL=280) =", round(cpk(qc["CCS_Mean_daN"].dropna(), lsl=280),3))

# 6) رگرسیون FeO ← دمای پخت و O2
from numpy.polynomial import polynomial as P
df = qc.dropna(subset=["Linked_Temp_Firing_C","Linked_O2_Firing_pct","Pellets_FeO_pct"])
coef = np.polyfit(df["Linked_Temp_Firing_C"], df["Pellets_FeO_pct"], 1)
print("FeO vs FiringTemp slope =", round(coef[0],6))
print("Corr matrix:")
print(qc[["CCS_Mean_daN","ISO_Tumble_pct","Porosity_pct","Pellets_FeO_pct",
          "Black_Core_pct","Linked_Temp_Firing_C","Linked_O2_Firing_pct"]].corr().round(3))
