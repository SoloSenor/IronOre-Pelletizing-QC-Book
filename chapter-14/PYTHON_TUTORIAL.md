# آموزش گام‌به‌گام Python برای تحلیل QC فصل ۱۴

> ورودی: [QC_Ch13_Ch14_Synthetic_Dataset.xlsx](QC_Ch13_Ch14_Synthetic_Dataset.xlsx) | [متن فصل](CHAPTER_14_TEXT.md) | [Power BI](POWER_BI_TUTORIAL.md) | [Excel](EXCEL_POWER_PIVOT_TUTORIAL.md) | [Minitab](MINITAB_TUTORIAL.md)

## ۱. نصب و اجرا
Python 3.10+؛ از ترمینال در پوشه این فایل:
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate   | macOS/Linux: source .venv/bin/activate
pip install pandas openpyxl numpy scipy seaborn matplotlib plotly
python qc_ch14_analysis.py
```
اسکریپت را با نام `qc_ch14_analysis.py` کنار فایل Excel ذخیره کنید. خروجی نمودارها در `outputs/` ذخیره می‌شود.

## ۲. اسکریپت کامل
این نمونه روی دیتاست مصنوعی اجرا می‌شود؛ پیش از تصمیم کارخانه‌ای، نام ستون‌ها، واحد، شیفت، Spec نسخه‌دار، کیفیت داده و طرح نمونه‌گیری را تأیید کنید.

```python
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats

FILE = Path(__file__).with_name("QC_Ch13_Ch14_Synthetic_Dataset.xlsx")
OUT = Path(__file__).with_name("outputs")
OUT.mkdir(exist_ok=True)

# برگه‌ها
qc = pd.read_excel(FILE, sheet_name="Fact_QC_Result")
params = pd.read_excel(FILE, sheet_name="Dim_Parameter")
monthly = pd.read_excel(FILE, sheet_name="Fact_Monthly_KPI")
for c in ["SampleDateTime", "ResultDateTime", "IngestionDateTime"]:
    qc[c] = pd.to_datetime(qc[c], errors="coerce")
qc["Value"] = pd.to_numeric(qc["Value"], errors="coerce")
qc["Shift"] = qc["Shift"].astype(str).str.strip().str.upper()
qc = qc.dropna(subset=["SampleDateTime", "Value", "Parameter", "Shift"])

# انتخاب تحلیل روی یک Parameter و Material مشخص؛ قابل تغییر با پارامتر خط فرمان/کد
PARAMETER = "Fe"
MATERIAL_ID = 2                 # در فایل: 2 = Concentrate
SPEC = params.loc[params["Parameter"].eq(PARAMETER)].iloc[0]
LSL, USL = float(SPEC["LSL"]), float(SPEC["USL"])
d = qc.loc[(qc["Parameter"] == PARAMETER) &
           (qc["MaterialID"] == MATERIAL_ID)].copy()
if d.empty:
    raise ValueError("رکوردی برای Parameter/Material انتخاب‌شده یافت نشد")
d = d.sort_values("SampleDateTime")
# مقدار انطباق را از حدود همین ردیف پارامتر بازسازی می‌کنیم (Spec آموزشی)
d["IsOOS"] = (d["Value"] < LSL) | (d["Value"] > USL)
print(f"{PARAMETER}: n={len(d)}, LSL={LSL:g}, USL={USL:g}, "
      f"mean={d.Value.mean():.4f}, OOS={d.IsOOS.mean():.1%}")

# ۳. نمای لحظه‌ای/تازه‌ترین رکورد + روند آخرین 24 ساعت
now = d["SampleDateTime"].max()
recent = d[d["SampleDateTime"] >= now - pd.Timedelta(hours=24)].copy()
latest = d.iloc[-1]
print("Latest sample:", latest["SampleDateTime"], "value=", latest["Value"],
      "shift=", latest["Shift"], "OOS=", bool(latest["IsOOS"]))
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(recent["SampleDateTime"], recent["Value"], marker="o", ms=3, lw=1)
ax.axhline(LSL, color="red", ls="--", label="LSL")
ax.axhline(USL, color="red", ls="--", label="USL")
ax.axhline(SPEC["Target"], color="green", ls=":", label="Target")
ax.set(title=f"{PARAMETER} — last 24h", ylabel=str(SPEC["Unit"]))
ax.legend(); fig.autofmt_xdate(); fig.tight_layout()
fig.savefig(OUT / "operational_24h.png", dpi=150); plt.close(fig)

# ۴. مقایسه سه شیفت: یک‌طرفه ANOVA و Kruskal–Wallis
# آزمون فرض: H0 توزیع/میانگین گروه‌ها برابر؛ استقلال مشاهده‌ها باید توجیه شود.
groups = [g["Value"].dropna().to_numpy()
          for _, g in d.groupby("Shift") if len(g) > 0]
labels = [s for s, g in d.groupby("Shift") if g["Value"].notna().any()]
print("Shift n/mean/std:")
print(d.groupby("Shift")["Value"].agg(["count", "mean", "std"]).to_string())
if len(groups) >= 2 and all(len(x) >= 2 for x in groups):
    a = stats.f_oneway(*groups)
    k = stats.kruskal(*groups)
    print(f"ANOVA: F={a.statistic:.4g}, p={a.pvalue:.5g}; "
          f"Kruskal: H={k.statistic:.4g}, p={k.pvalue:.5g}")
    print("p<0.05 فقط نشانه شواهد اختلاف است؛ اندازه اثر، چندمقایسه‌ای، "
          "مخدوش‌گرها و استقلال را بررسی کنید.")
else:
    print("برای آزمون، حداقل دو گروه با n>=2 لازم است.")
fig, ax = plt.subplots(figsize=(7, 4))
sns.boxplot(data=d, x="Shift", y="Value", order=[s for s in ["A", "B", "C"] if s in d.Shift.unique()], ax=ax)
ax.axhline(LSL, color="red", ls="--"); ax.axhline(USL, color="red", ls="--")
ax.set_title(f"{PARAMETER} by shift"); fig.tight_layout()
fig.savefig(OUT / "shift_boxplot.png", dpi=150); plt.close(fig)

# ۵. هیت‌مپ نرخ OOS برحسب ماه و شیفت
# تاریخ نمونه (نه تاریخ ورود نتیجه) برای دسته‌بندی زمانی انتخاب شده است.
d["Month"] = d["SampleDateTime"].dt.to_period("M").astype(str)
heat = d.pivot_table(index="Month", columns="Shift", values="IsOOS", aggfunc="mean")
fig, ax = plt.subplots(figsize=(8, max(4, 0.35 * len(heat))))
sns.heatmap(heat, annot=True, fmt=".0%", cmap="YlOrRd", vmin=0, vmax=1,
            cbar_kws={"label": "OOS rate"}, ax=ax)
ax.set_title(f"OOS heatmap — {PARAMETER}"); fig.tight_layout()
fig.savefig(OUT / "oos_heatmap.png", dpi=150); plt.close(fig)

# ۶. پارتو علل OOS؛ دسته‌بندی علت بر اساس پارامتر و جهت نقض
bad = qc.loc[qc["IsConform"].eq(0)].copy()
lookup = params.set_index("Parameter")[["LSL", "USL"]]
bad = bad.join(lookup, on="Parameter")
bad["Direction"] = np.select([bad["Value"] < bad["LSL"], bad["Value"] > bad["USL"]],
                              ["Low", "High"], default="Other")
pareto = bad.groupby(["Parameter", "Direction"]).size().sort_values(ascending=False)
pareto.to_csv(OUT / "oos_pareto.csv", header=["Count"])
fig, ax = plt.subplots(figsize=(10, 5))
pareto.head(15).plot(kind="bar", color="steelblue", ax=ax)
ax.set(title="Pareto of OOS parameter/direction", ylabel="OOS count", xlabel="Cause")
fig.tight_layout(); fig.savefig(OUT / "oos_pareto.png", dpi=150); plt.close(fig)

# ۷. قابلیت فرایند Cp/Cpk (برآورد within از زیرگروه‌های متوالی)
# فقط وقتی فرایند پایدار، داده نماینده و حدود واقعی مشخصات‌اند؛
# برای زیرگروه‌های n=5 برآورد sigma_within = Rbar/d2, d2=2.326.
# اگر شیفت/بچ رونددار است، اول نمودار کنترل و علت ویژه بررسی شود.
values = d["Value"].dropna().to_numpy()
subgroup_size = 5
d2 = {2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326, 6: 2.534}.get(subgroup_size)
usable = values[: (len(values) // subgroup_size) * subgroup_size]
if d2 and len(usable) >= subgroup_size * 10:
    sub = usable.reshape(-1, subgroup_size)
    rbar = np.ptp(sub, axis=1).mean()
    sigma_within = rbar / d2
    mean = usable.mean()
    cp = (USL - LSL) / (6 * sigma_within)
    cpk = min((USL - mean) / (3 * sigma_within),
              (mean - LSL) / (3 * sigma_within))
    print(f"Capability (n={len(usable)}, subgroup={subgroup_size}): "
          f"mean={mean:.4f}, sigma_within={sigma_within:.5f}, Cp={cp:.3f}, Cpk={cpk:.3f}")
else:
    print("Cp/Cpk نامحاسبه: برای برآورد within حداقل 10 زیرگروه لازم است.")

# خروجی جدول قابل بازبینی
summary = d.groupby("Shift").agg(n=("Value", "size"), mean=("Value", "mean"),
                                 sd=("Value", "std"), oos_rate=("IsOOS", "mean"))
summary.to_csv(OUT / "shift_summary.csv")
print("Outputs saved under", OUT.resolve())
```

## ۳. تفسیر محتاطانه
- **لحظه‌ای:** تازه‌ترین نتیجه الزاماً آخرین اندازه‌گیری فرایند نیست؛ `SampleDateTime`, `ResultDateTime` و `IngestionDateTime` را جدا گزارش کنید.
- **ANOVA:** استقلال، نرمال‌بودن باقیمانده و همگنی واریانس را بسنجید؛ در صورت نقض توزیع/پرت‌ها، Kruskal-Wallis گزینه رتبه‌ای است. چندمقایسه‌ای پس از آزمون کلی با اصلاح (مثلاً Holm) انجام شود.
- **هیت‌مپ/پارتو:** نشان‌دهنده اولویت مشاهده است، نه علت ریشه‌ای.
- **Cp/Cpk:** کد از R-bar/d2 برای زیرگروه‌های ۵تایی متوالی استفاده می‌کند؛ زیرگروه واقعی و اندازه مناسب را با مهندس فرآیند تعیین کنید. اگر داده فردی/غیرنرمال/ناپایدار است، این برآورد را گزارش نکنید و روش جایگزین را مستند کنید.
- تفسیر نمودارهای کنترل و قابلیت در [Minitab](MINITAB_TUTORIAL.md)، ساخت داشبورد در [Power BI](POWER_BI_TUTORIAL.md)، و مفاهیم طراحی در [CHAPTER_14_TEXT.md](CHAPTER_14_TEXT.md).
