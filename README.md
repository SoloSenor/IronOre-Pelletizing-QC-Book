# فصل ۵ — کنترل کیفیت فرایندندuration گلوله‌ها (Straight Grate Induration)

> **فصل ۵ کتاب:** کنترل کیفیت در صنایع فولاد و گندله‌سازی
> این مخزن شامل **متن کامل فصل ۵**، **داده‌های آموزشی** و **آموزش تحلیل داده با ۴ نرم‌افزار** است.

---

## 📁 ساختار مخزن

| مسیر | توضیح |
|------|-------|
| [`chapter/Chapter05_Text.md`](chapter/Chapter05_Text.md) | **متن کامل فصل ۵** (بخش‌بندی‌شده با لینک‌های پرش) |
| [`data/Pellet_Induration_QC_Chapter5_Dataset.xlsx`](data/Pellet_Induration_QC_Chapter5_Dataset.xlsx) | **دیتاست اصلی فصل ۵** (۴ شیت: فرایند ساعتی، نمونه‌های QC، آزمایش ارگون، ابعاد/کمپین‌ها) |
| [`tutorials/Excel_Tutorial.md`](tutorials/Excel_Tutorial.md) | 🟢 آموزش تحلیل با **Microsoft Excel** |
| [`tutorials/Minitab_Tutorial.md`](tutorials/Minitab_Tutorial.md) | 🟣 آموزش تحلیل با **Minitab** |
| [`tutorials/Python_Tutorial.md`](tutorials/Python_Tutorial.md) | 🐍 آموزش تحلیل با **Python (Pandas/Matplotlib/Statsmodels)** |
| [`tutorials/R_Tutorial.md`](tutorials/R_Tutorial.md) | 🔵 آموزش تحلیل با **R (tidyverse/ggplot2)** |
| [`scripts/analyze_chapter5.py`](scripts/analyze_chapter5.py) | اسکریپت آماده تحلیل کامل (Python) |
| [`scripts/analyze_chapter5.R`](scripts/analyze_chapter5.R) | اسکریپت آماده تحلیل کامل (R) |

---

## 🚀 شروع سریع

1. متن فصل را از [`chapter/Chapter05_Text.md`](chapter/Chapter05_Text.md) بخوانید.
2. دیتاست [`data/Pellet_Induration_QC_Chapter5_Dataset.xlsx`](data/Pellet_Induration_QC_Chapter5_Dataset.xlsx) را دانلود کنید.
3. بسته به نرم‌افزار مورد علاقه، یکی از آموزش‌های زیر را دنبال کنید:

| نرم‌افزار | آموزش | سطح |
|-----------|--------|------|
| Excel | [Excel_Tutorial.md](tutorials/Excel_Tutorial.md) | مقدماتی |
| Minitab | [Minitab_Tutorial.md](tutorials/Minitab_Tutorial.md) | مقدماتی–متوسط |
| Python | [Python_Tutorial.md](tutorials/Python_Tutorial.md) | متوسط |
| R | [R_Tutorial.md](tutorials/R_Tutorial.md) | متوسط |

---

## 📊 شرح دیتاست

| شیت | محتوا | ابعاد |
|-----|--------|-------|
| `Fact_Process_Hourly` | داده‌های ساعتی فرایند (دماها، سرعت پالت، ارتفاع بستر، دبی گاز، O₂، ΔP وینباکس) | ۷۲۰ رکورد × ۱۵ ستون |
| `Fact_QC_Samples` | نمونه‌های کنترل کیفیت (شیمی خوراک، بلاین، CCS، تامبل، سایش، تخلخل، FeO، هسته سیاه + لینک به فرایند) | ۱۸۰ رکورد × ۲۵ ستون |
| `Ergun_Equation_Lab` | آزمایشگاه معادله ارگون (افت فشار در ۷ زون + ۵ سناریو) با فرمول‌های Excel زنده | ۱۵ ردیف |
| `Dim_Zones_Campaigns` | ابعاد: زون‌های حرارتی Straight Grate + کمپین‌های تولید با حدود مشخصات | ۲ جدول |

---

## 🔗 لینک‌های مرتبط در متن فصل

- بخش «مدل هیدرودینامیک ارگون» → [Ergun_Equation_Lab در دیتاست](data/Pellet_Induration_QC_Chapter5_Dataset.xlsx) و [آموزش Excel](tutorials/Excel_Tutorial.md#۲-بازسازی-معادله-ارگون-در-excel)
- بخش «کنترل کیفیت گندله» → [Fact_QC_Samples در دیتاست](data/Pellet_Induration_QC_Chapter5_Dataset.xlsx) و [آموزش Minitab](tutorials/Minitab_Tutorial.md)
- بخش «پایش آماری فرایند» → [Fact_Process_Hourly در دیتاست](data/Pellet_Induration_QC_Chapter5_Dataset.xlsx) و [آموزش Python](tutorials/Python_Tutorial.md)
- بخش «تحلیل آماری با R» → [آموزش R](tutorials/R_Tutorial.md)

---
*Lایسنس: استفاده آموزشی.*
