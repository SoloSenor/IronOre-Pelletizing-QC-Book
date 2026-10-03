# 🟣 آموزش تحلیل دیتاست فصل ۵ در **Minitab**

[⬅ بازگشت به README](../README.md) | [دانلود دیتاست](../data/Pellet_Induration_QC_Chapter5_Dataset.xlsx)

## ۱- آماده‌سازی داده
1. فایل Excel را در Minitab باز کنید: **File → Open → Worksheet →** فایل [دیتاست فصل ۵](../data/Pellet_Induration_QC_Chapter5_Dataset.xlsx).
2. هر شیت به‌صورت یک Worksheet جداگانه وارد می‌شود.

## ۲- آمار توصیفی و بررسی نرمال بودن
- **Stat → Basic Statistics → Display Descriptive Statistics** → Variables: `Temp_Firing_C`, By: `Campaign`.
- **Stat → Basic Statistics → Normality Test (Anderson-Darling)** روی `CCS_Mean_daN`.

## ۳- نمودارهای کنترل (SPC)
- **I-MR Chart**: `Stat → Control Charts → Variables Charts for Individuals → I-MR` → Variables: `Temp_Firing_C`.
- **X̄-R Chart**: ابتدا داده‌ها را بر اساس شیفت زیرگروه کنید (`Data → Stack/Unstack` یا از ستون `Shift` به‌عنوان Subgroup) سپس `Xbar-R`.
- **EWMA/CUSUM** برای تشخیص شیفت‌های کوچک در `Windbox_Avg_DP_kPa`.

## ۴- توانایی فرایند (Process Capability)
- **Stat → Quality Tools → Capability Analysis (Normal)**:
  - Variables: `CCS_Mean_daN`
  - Subgroup size: 1
  - Lower spec: از شیت `Dim_Zones_Campaigns` (مثلاً Camp_A: 280 daN)
- گزارش Cp, Cpk, Pp, Ppk را تفسیر کنید (Cpk ≥ 1.33 مطلوب).

## ۵- رگرسیون و همبستگی
- **Stat → Regression → Regression → Fit Regression Model**:
  - Response: `CCS_Mean_daN`
  - Predictors: `Linked_Temp_Firing_C`, `Linked_Pallet_Speed_mpm`, `Linked_Bed_Height_mm`
- **Stat → Basic Statistics → Correlation** برای بررسی روابط FeO / Black_Core با شرایط زون پخت.

## ۶- ANOVA (مقایسه کمپین‌ها)
- **Stat → ANOVA → One-Way**: Response `CCS_Mean_daN`، Factor `Campaign` (بر اساس شیت Dim).
- بررسی فرض نرمال بودن باقیمانده‌ها.

## ۷- نمودار پارتو و اهمیت عوامل
- **Stat → Quality Tools → Pareto Chart** روی شمارش ناهنجاری‌ها (مانند Black_Core_pct بالاتر از حد).

---
[⬅ بازگشت به README](../README.md) | [فصل ۵](../chapter/Chapter05_Text.md)
