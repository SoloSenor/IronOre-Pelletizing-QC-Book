# راهنمای تحلیل آماری فرآیند فصل ۳ در Minitab

از شیت `Minitab_Import` در فایل [`Chapter03_QC_Separation_Dewatering_Data.xlsx`](../datasets/Chapter03_QC_Separation_Dewatering_Data.xlsx) استفاده کنید.

---

## ۱. نمودار کنترل I-MR برای رطوبت کیک فیلتر

رطوبت کیک یک متغیر پیوسته است و در این Dataset به‌صورت مشاهدات منفرد در هر زمان ثبت شده است.

مسیر:

`Stat → Control Charts → Variables Charts for Individuals → I-MR`

در بخش **Variables**:

`Filter_Cake_Moisture_pct`

را وارد کنید.

در **I-MR Options → Tests**:

* گزینه **Perform all tests for special causes** را فعال کنید.

### تفسیر

در Dataset آموزشی، در برخی بازه‌ها ممکن است نقاط خارج از حدود کنترل مشاهده شوند.

این وضعیت باید به‌عنوان **سیگنال علت ویژه** تفسیر شود، نه به‌عنوان اثبات قطعی خرابی فیلتر.

برای بررسی علت باید متغیرهایی مانند:

* `Filter_Vacuum_kPa`
* `Filter_Cloth_Condition_pct`
* `Filter_Feed_Solids_pct`
* `Feed_Slimes_pct`
* `Thickener_Underflow_Solids_pct`

نیز بررسی شوند.

---

## ۲. ارزیابی قابلیت فرآیند با Cpk

برای بررسی قابلیت فرآیند:

`Stat → Quality Tools → Capability Analysis → Normal`

تنظیمات:

* **Single column:** `Filter_Cake_Moisture_pct`
* **Subgroup size:** `1`
* **LSL:** `8.5`
* **Target:** `9.5`
* **USL:** `10.5`

### نکته آماری مهم

شاخص $C_{pk}$ قابلیت فرآیند را نسبت به حدود مشخصات ارزیابی می‌کند؛ اما قبل از تفسیر قابلیت، باید پایداری فرآیند نیز بررسی شود.

به‌صورت مفهومی:

$$
C_{pk}
=
\min
\left(
\frac{USL-\mu}{3\sigma},
\frac{\mu-LSL}{3\sigma}
\right)
$$

مقدار کمتر از 1 در این Dataset به‌عنوان نشانه فاصله قابل توجه فرآیند از محدوده مشخصات تفسیر می‌شود، اما این مقدار به‌تنهایی علت مشکل را مشخص نمی‌کند.

همچنین آستانه‌هایی مانند 1.00 یا 1.33 باید متناسب با سیاست کیفیت و ریسک محصول تفسیر شوند.

---

## ۳. رگرسیون چندگانه: اثر ریزدانه‌ها بر رطوبت کیک

مسیر:

`Stat → Regression → Regression → Fit Regression Model`

### Response

`Filter_Cake_Moisture_pct`

### Continuous Predictors

* `Feed_Slimes_pct`
* `Filter_Vacuum_kPa`
* `Filter_Cloth_Condition_pct`
* `Filter_Feed_Solids_pct`

### تحلیل

هدف، بررسی سهم آماری متغیرهای بالادست و شرایط فیلتر در تغییرات رطوبت کیک است.

در صورت مشاهده ضریب مثبت و معنادار برای `Feed_Slimes_pct`، می‌توان گفت در Dataset مورد مطالعه، افزایش اسلایم با افزایش رطوبت کیک همراه است.

> **هشدار:** مقدار $P < 0.001$ فقط در صورتی باید گزارش شود که واقعاً از خروجی Minitab به‌دست آمده باشد. این مقدار را نباید به‌عنوان نتیجه از پیش تضمین‌شده در متن آموزشی معرفی کرد.

همچنین در تفسیر رگرسیون باید به:

* $R^2$
* $R^2_{adj}$
* معنی‌داری ضرایب
* VIF
* باقیمانده‌ها
* نرمال بودن واریانس باقیمانده‌ها
* استقلال مشاهدات

توجه شود.
