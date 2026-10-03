# 🟢 آموزش تحلیل دیتاست فصل ۵ در **Microsoft Excel**

[⬅ بازگشت به README](../README.md) | [دانلود دیتاست](../data/Pellet_Induration_QC_Chapter5_Dataset.xlsx)

## ۱- بارگذاری دیتاست
1. فایل [`data/Pellet_Induration_QC_Chapter5_Dataset.xlsx`](../data/Pellet_Induration_QC_Chapter5_Dataset.xlsx) را باز کنید.
2. چهار شیت دارید: `Fact_Process_Hourly`، `Fact_QC_Samples`، `Ergun_Equation_Lab`، `Dim_Zones_Campaigns`.

## ۲- بازسازی معادله ارگون در Excel
شیت `Ergun_Equation_Lab` از قبل فرمول‌های زنده دارد:
- ستون `Viscous_Term`: `=150*((1-eps)^2/(eps^3))*(mu*vs/(dp/1000)^2)`
- ستون `Inertial_Term`: `=1.75*((1-eps)/(eps^3))*(rho*vs^2/(dp/1000))`
- ستون `Total_DP_kPa`: `=(Viscous+Inertial)*L/1000`

**تمرین:** با تغییر `dp` و `eps` در سناریوها، اثر آن‌ها را بر ΔP بررسی کنید.

## ۳- آمار توصیفی
- انتخاب ستون `Temp_Firing_C` → **Insert → PivotTable** → میانگین/انحراف معیار بر اساس `Campaign` و `Shift`.
- یا **Data → Data Analysis → Descriptive Statistics** (در صورت فعال نبودن: File → Options → Add-ins → Analysis ToolPak).

## ۴- نمودار کنترل (SPC) در Excel
1. در شیت `Fact_Process_Hourly` ستون `Temp_Firing_C` را انتخاب کنید.
2. یک ستون کمکی `Mean` با `=AVERAGE($N$2:$N$721)` و ستون‌های `UCL = Mean+3*STDEV.S(...)` و `LCL = Mean-3*STDEV.S(...)`.
3. **Insert → Line Chart** → سه سری (Data, UCL, LCL) رسم کنید.

## ۵- توانایی فرایند
- با استفاده از Data Analysis → Histogram روی `CCS_Mean_daN` در شیت `Fact_QC_Samples`، توزیع را رسم کنید.
- Cp/Cpk را با فرمول بسازید:
  - `Cp = (USL-LSL)/(6*STDEV.S)`
  - `Cpk = MIN(USL-mean, mean-LSL)/(3*STDEV.S)`
- حدود مشخصات را از شیت `Dim_Zones_Campaigns` بردارید (مثلاً Camp_A: CCS≥280).

## ۶- تحلیل همبستگی
- **Data → Data Analysis → Correlation** روی ستون‌های `Linked_Temp_Firing_C`، `Linked_O2_Firing_pct`، `Pellets_FeO_pct`، `Black_Core_pct` در شیت `Fact_QC_Samples`.
- رسم **Scatter** با خط روند: Insert → Scatter → Add Trendline → Display Equation و R².

---
[⬅ بازگشت به README](../README.md) | [فصل ۵](../chapter/Chapter05_Text.md)
