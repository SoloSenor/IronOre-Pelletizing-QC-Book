# راهنمای تحلیل آماری، شناسایی توزیع و رگرسیون در Minitab

این راهنما به تحلیل توزیع CCS تک‌گندله‌ای، مدل‌سازی صدک پایین و احتمال تشکیل Black Core می‌پردازد.

داده‌ها از شیت‌های:

* `Pellet_CCS`
* `Shift_Data`

فایل فصل ۱۱ گرفته می‌شوند.

---

# گام ۱: شناسایی توزیع CCS

## 1.1 ورود داده

ستون:

```text
CCS_N
```

را از شیت `Pellet_CCS` وارد Minitab کنید.

اگر داده‌ها مربوط به چند Lot هستند، بهتر است ابتدا تحلیل را برای:

* کل جمعیت
* هر رژیم فرایندی
* یا هر Lot

به‌صورت مناسب تفکیک کنید.

---

## 1.2 Individual Distribution Identification

مسیر:

```text
Stat > Quality Tools > Individual Distribution Identification
```

Minitab در این تحلیل Probability Plot و Goodness-of-Fit را برای توزیع‌های مختلف ارائه می‌کند.

توزیع‌های قابل بررسی شامل:

* Normal
* Weibull
* Lognormal
* Gamma
* سایر توزیع‌های مناسب

هستند.

---

## 1.3 تفسیر نتایج

برای هر توزیع موارد زیر بررسی شود:

* Probability Plot
* Anderson–Darling statistic
* P-value
* در مدل‌های چندپارامتری، LRT P-value
* شکل دُم توزیع
* دانش فرایند

Anderson–Darling برای مقایسه برازش توزیع‌ها مفید است، اما اگر مقادیر AD نزدیک باشند، نباید صرفاً بر اساس اختلاف کوچک آنها یک توزیع را انتخاب کرد. Minitab توصیه می‌کند Probability Plot، p-value و دانش فرایند نیز در انتخاب دخالت داده شوند.

### قانون مهم

این عبارت نادرست است:

```text
Normal P-value < 0.05 → Weibull
```

قاعده صحیح:

```text
Normal fit
      ↓
Goodness-of-Fit
      ↓
Comparison with candidate distributions
      ↓
Process knowledge
      ↓
Selected distribution
```

بنابراین رد شدن Normal به‌تنهایی Weibull را اثبات نمی‌کند.

---

# گام ۲: تحلیل صدک پایین CCS

فرض کنید داده‌های لات به‌صورت زیر آماده شده‌اند:

```text
Lot_ID
CCS_mean
CCS_std
CCS_P10
```

هدف این مرحله بررسی این است که آیا شرایط فرایندی با `CCS_P10` ارتباط دارند یا خیر.

---

# گام ۳: Regression Model برای CCS_P10

مسیر:

```text
Stat > Regression > Regression > Fit Regression Model
```

### Response

```text
CCS_P10
```

### Continuous Predictors

نمونه:

```text
T_firing_peak
TimeAbove1200_min
Temp_Uniformity_Std
Basicity_B2
Gangue_SiAl
FeO
O2_avg_pct
```

---

# گام ۴: Stepwise Regression

در صورت استفاده از Stepwise:

```text
Model Selection Method = Stepwise
```

و مثلاً:

```text
Alpha to Enter = 0.10
Alpha to Remove = 0.10
```

را می‌توان برای **تحلیل اکتشافی آموزشی** استفاده کرد.

اما خروجی Stepwise نباید به‌عنوان مدل نهایی بدون اعتبارسنجی تلقی شود.

موارد زیر بررسی شوند:

* Residual plots
* Normality of residuals
* Constant variance
* Multicollinearity
* Prediction error
* Validation data

اگر `Temp_Uniformity_Std` وارد مدل شود و ضریب آن منفی باشد، می‌توان گفت در چارچوب مدل و داده مورد بررسی، افزایش آن با کاهش `CCS_P10` همراه است.

این نتیجه با «اثبات علت فیزیکی» یکسان نیست.

---

# گام ۵: Binary Logistic Regression برای Black Core

برای Logistic Regression باید متغیر پاسخ دودویی وجود داشته باشد:

```text
Has_BlackCore
```

تعریف:

```text
0 = Black Core مشاهده نشده
1 = Black Core مشاهده شده
```

این متغیر با `BlackCore_frac` یکسان نیست.

* `Has_BlackCore` → سطح تک‌گندله، دودویی
* `BlackCore_frac` → سطح لات، نسبت/کسر

---

## 5.1 آماده‌سازی داده

اگر `Pellet_CCS` فقط شامل `CCS_N` و `Has_BlackCore` باشد ولی predictors در `Shift_Data` قرار داشته باشند، ابتدا آنها را با `Lot_ID` به جدول مدل منتقل کنید.

جدول نهایی می‌تواند شامل:

```text
Lot_ID
CCS_N
Has_BlackCore
Pellet_Size_mm
FeO
O2_avg_pct
TimeAbove1200_min
T_firing_peak
```

باشد.

---

## 5.2 اجرای مدل

مسیر Minitab ممکن است بسته به نسخه کمی متفاوت باشد، اما ساختار تحلیل:

```text
Stat > Regression > Binary Logistic Regression > Fit Binary Logistic Model
```

است.

### Response

```text
Has_BlackCore
```

### Predictors

مثلاً:

```text
Pellet_Size_mm
FeO
O2_avg_pct
TimeAbove1200_min
T_firing_peak
```

---

# گام ۶: تفسیر Odds Ratio

مدل Logistic:

$$
\log
\left(
\frac{p}{1-p}
\right)
=
\beta_0+\beta_1X_1+\cdots+\beta_kX_k
$$

است.

برای هر predictor:

$$
OR=e^\beta
$$

### تفسیر

اگر:

```text
OR > 1
```

باشد، افزایش predictor در چارچوب مدل با افزایش odds رویداد همراه است.

اگر:

```text
OR < 1
```

باشد، افزایش predictor در چارچوب مدل با کاهش odds رویداد همراه است.

اما باید همزمان بررسی شود:

* Confidence Interval
* P-value
* Model fit
* Sampling design
* Confounding
* Class imbalance

بنابراین نباید از قبل اعلام کرد که افزایش FeO یا اندازه گندله حتماً احتمال Black Core را افزایش می‌دهد؛ جهت و شدت رابطه باید از داده استخراج شود.

---

# گام ۷: بررسی عدم توازن کلاس‌ها

اگر:

```text
Has_BlackCore = 1
```

بسیار کم باشد، Accuracy می‌تواند معیار گمراه‌کننده‌ای باشد.

معیارهای مناسب‌تر:

* Sensitivity
* Specificity
* Precision
* Recall
* ROC-AUC
* PR-AUC

و در کاربرد صنعتی:

* False Negative Cost
* False Positive Cost

نیز باید بررسی شوند.

---

# گام ۸: اعتبارسنجی

مدل نهایی باید روی داده‌ای جدا از داده آموزش ارزیابی شود.

برای مدل CCS:

```text
RMSE
MAE
R²
Prediction Interval
Calibration
```

برای مدل Black Core:

```text
ROC-AUC
PR-AUC
Sensitivity
Specificity
Calibration
```

پیشنهاد می‌شود اگر داده زمانی است، تقسیم آموزش/آزمون نیز زمان را رعایت کند تا اطلاعات آینده وارد آموزش نشود.

---

# گام ۹: خروجی نهایی

خروجی تحلیلی این فصل در Minitab باید شامل:

```text
Selected Distribution
CCS_P10 Model
Regression Diagnostics
Black Core Logistic Model
Odds Ratios
Confidence Intervals
Model Validation
```

باشد.

👉 [بازگشت به فهرست آموزش‌ها](../README.md)
