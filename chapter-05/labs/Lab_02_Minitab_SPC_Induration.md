# 📘 کارگاه ۲ — مینی‌تب: کنترل آماری فرایند پخت (I-MR، Xbar-R و Cpk)

> 📥 پیش‌نیاز: [Pellet_Induration_QC_Chapter5_Dataset.xlsx](../data/Pellet_Induration_QC_Chapter5_Dataset.xlsx) — شیت‌های `Fact_Process_Hourly` و `Fact_QC_Samples`

## هدف
ارزیابی پایداری حرارتی کوره و تحلیل قابلیت فرایند برای مقاومت فشاری سرد (CCS) با حد فنی LSL = ۲۵۰ daN.

## گام ۱ — ایمپورت داده
File ▸ Open ▸ فایل اکسل ▸ انتخاب شیت `Fact_Process_Hourly`. ستون‌های کلیدی:
`Temp_UDD_C, Temp_DDD_C, Temp_PH_C, Temp_Firing_C, Windbox_Avg_DP_kPa, O2_Firing_pct`.

## گام ۲ — نمودار I-MR برای دمای زون‌ها
Stat ▸ Control Charts ▸ Variables Charts for Individuals ▸ **I-MR**:
- Variables: `Temp_Firing_C`
- I-MR Options ▸ Tests: اجرای هر چهار آزمون نلسون (به‌ویژه Test 5 و 6 — مهم برای کوره پیوسته با تغییر کمپین).

**تفسیر:** نقاط خارج حدود در دمای Firing معمولاً با تعویض مشعل یا تغییر کمپین هم‌زمان است؛ با Assistant ▸ Capability مقدمه‌ای برای برآورد σ بین‌درون‌سری بگیرید.

## گام ۳ — نمودار Xbar-R برای CCS
Stat ▸ Control Charts ▸ Variables Charts for Subgroups ▸ **Xbar-R**:
- Variables: `CCS_Mean_daN` — Subgroup sizes: 4 (چهار نمونه هر شیفت).

اگر خودهمبستگی معنادار بود (ACF lag-1 > 0.3)، بجای Xbar از **I-MR با underestimated σ** پرهیز کنید و از MVChart یا فاصله‌دهی زیرگروه‌ها استفاده کنید.

## گام ۴ — قابلیت فرایند CCS
Stat ▸ Quality Tools ▸ **Capability Analysis (Normal)**:
- Single column: `CCS_Mean_daN` — Subgroup size: 4
- Lower spec: **۲۵۰** — Target: ۲۸۰
- Options ▸ Target (adds Cpm) و گزینه Include confidence intervals.

**خروجی مورد انتظار برای تفسیر:**
| شاخص | حد پذیرش QC |
|---|---|
| Cp / Cpk | ≥ ۱٫۳۳ |
| Ppk (کلی) | ≥ ۱٫۰ حداقل |
| %Out of Spec | < ۱۰۰ ppm هدف |
| Z.Bench | ≥ ۴ |

## گام ۵ — تحلیل چندمتغیره سریع
از Graph ▸ Matrix Plot، همبستگی `Temp_Firing_C` × `Pellets_FeO_pct` × `Black_Core_pct` × `CCS_Mean_daN` را بررسی کنید؛ FeO بالا همراه Black Core بالا نشانه اکسیداسیون ناقص در PH/Firing است.

## تحویل خروجی
فایل پروژه Minitab شامل: (۱) I-MR دو زون اصلی، (۲) Xbar-R باس، (۳) گزارش Capability با CI، (۴) جدول نقاط خارج از کنترل با تاریخ/شیفت.
