# راهنمای گام‌به‌گام پیاده‌سازی تحلیل قابلیت غیرنرمال در Minitab
## فصل ۸: ارزیابی قابلیت مقاومت فشاری سرد (CCS) و تخلخل

پایگاه داده ورودی: شیت `data_long` از فایل [`Chapter08_Pellet_Nonnormal_Capability_Dataset.xlsx`](../data/Chapter08_Pellet_Nonnormal_Capability_Dataset.xlsx)

---

### مرحله ۱: آزمون شناسایی توزیع (Individual Distribution Identification)
1. مسیر منو: `Stat > Quality Tools > Individual Distribution Identification`
2. متغیر پاسخ: `Single column: CCS_kg`
3. سایز زیرگروه: `Subgroup size: 1`
4. کلیک بر روی **OK**.

**تفسیر خروجی مینی‌تب:**
* مقادیر **p-value** و آماره **Anderson-Darling (AD)** را در جدول خروجی بررسی کنید.
* اگر p-value < 0.05 باشد، فرض آن توزیع رد می‌شود (توزیع نرمال با p < 0.005 رد می‌گردد).
* توزیع‌های **Weibull** (با ۲ پارامتر) یا تبدیل **Box-Cox** کمترین مقدار AD و بالاترین انطباق بصری را در Probability Plot نشان می‌دهند.

---

### مرحله ۲: ارزیابی قابلیت با تبدیل باکس-کاکس (Box-Cox Capability)
1. مسیر منو: `Stat > Quality Tools > Capability Analysis > Normal`
2. انتخاب متغیر: `Single column: CCS_kg`
3. تنظیمات مشخصات:
   - در باکس **Lower spec**: عدد `250` را وارد کنید.
   - باکس **Upper spec** را خالی بگذارید (چون CCS حد بالایی ندارد).
4. کلیک بر روی دکمه **Transform**:
   - گزینه **Box-Cox power transformation** را فعال کنید.
   - زیرگزینه: `Estimate lambda (from 0.5 to 2.0 or unrestricted)`
5. کلیک بر روی **OK** در تمام پنجره‌ها.

**خروجی گرافیکی:**
* مینی‌تب نمودار توزیع را در مقیاس تبدیل‌شده همراه با شاخص‌های قابلیت کلی (Ppk و Ppl) رسم می‌کند و نرخ عدم انطباق را به فرمت **Observed PPM** و **Expected PPM** گزارش می‌دهد.

---

### مرحله ۳: ارزیابی قابلیت با تحلیل توزیع‌های غیرنرمال (Nonnormal Capability Analysis)
اگر ترجیح می‌دهید مقیاس فیزیکی داده‌ها (kg/pellet) بدون تبدیل حفظ شود:
1. مسیر منو: `Stat > Quality Tools > Capability Analysis > Nonnormal`
2. انتخاب ستون: `CCS_kg`
3. انتخاب توزیع برازش‌شده: `Fit distribution: Weibull` (یا `Lognormal`)
4. مقدار حد پایینی: `Lower spec: 250`
5. کلیک بر روی **OK**.

**تفسیر صنعتی:**
* مینی‌تب شاخص Ppk معادل صدکی و درصد محصولات کمتر از ۲۵۰ کیلوگرم را مستقیماً از منحنی کاندید محاسبه می‌کند.

---

### مرحله ۴: تحلیل تخلخل (Porosity) با سیستم جانسون (Johnson Transformation)
با توجه به اینکه تخلخل بین ۲۲ تا ۳۰ درصد محدود و مقداری چوله است:
1. مسیر منو: `Stat > Quality Tools > Capability Analysis > Normal`
2. متغیر: `Porosity_pct`
3. در بخش **Transform**: گزینه **Johnson transformation** را انتخاب کنید.
4. حدود: `Lower spec: 22` و `Upper spec: 30`.
5. مینی‌تب به صورت خودکار از میان خانواده‌های S_B (کراندار)، S_U (بی‌کران) و S_L، بهترین تابع انتقال را انتخاب می‌کند.
