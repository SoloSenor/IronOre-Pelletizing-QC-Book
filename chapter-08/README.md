# فصل ۸ — تحلیل قابلیت فرآیندهای غیرنرمال در تولید گندله (CCS و Porosity)

بسته آموزشی گیت‌هاب شامل متن کامل فصل و راهنمای پیاده‌سازی در چهار نرم‌افزار (Python، Excel، Minitab، Power BI).

## ساختار پکیج

| مسیر | توضیح |
| :--- | :--- |
| [chapter08_text.md](chapter08_text.md) | متن کامل فصل ۸ کتاب |
| [tutorials/python_capability_analysis.ipynb](tutorials/python_capability_analysis.ipynb) | نوت‌بوک پایتون (آمار توصیفی، Anderson-Darling، Box-Cox، Weibull، نمودارها) |
| [tutorials/excel_capability_guide.md](tutorials/excel_capability_guide.md) | راهنمای گام‌به‌گام Excel با فرمول‌ها |
| [tutorials/minitab_capability_guide.md](tutorials/minitab_capability_guide.md) | راهنمای Minitab (شناسایی توزیع، Box-Cox، Nonnormal Capability، Johnson) |
| [tutorials/powerbi_dashboard_guide.md](tutorials/powerbi_dashboard_guide.md) | راهنمای داشبورد Power BI با فرمول‌های DAX |
| [scripts/nonnormal_capability.py](scripts/nonnormal_capability.py) | اسکریپت کامل تحلیل قابلیت غیرنرمال |
| [data/Chapter08_Pellet_Nonnormal_Capability_Dataset.xlsx](data/Chapter08_Pellet_Nonnormal_Capability_Dataset.xlsx) | دیتاست آموزشی فصل ۸ |

## دیتاست
فایل [Chapter08_Pellet_Nonnormal_Capability_Dataset.xlsx](data/Chapter08_Pellet_Nonnormal_Capability_Dataset.xlsx) شامل شیت‌های `data_long` (۴۸۰ رکورد فرایندی)، `chapter8_ccs_100` (۱۰۰ نمونه CCS)، `specs` (حدود مشخصات)، `capability_calc` و `README` است.

## خلاصه نتایج کلیدی تحلیل (n=100، LSL=250 kg)
- فرض نرمال: Cpl ≈ 0.43 و نرخ عدم انطباق تخمینی ≈ 9.9٪
- مشاهده واقعی: 5.0٪ (۵ گندله از ۱۰۰)
- Box-Cox (λ ≈ −1.02): Cpl ≈ 0.50
- توزیع Weibull: نرخ عدم انطباق و Cpl معادل مطابق خروجی اسکریپت
