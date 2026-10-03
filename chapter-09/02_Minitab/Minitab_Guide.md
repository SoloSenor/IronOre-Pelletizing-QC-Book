# راهنمای پیاده‌سازی و تحلیل آماری سنسور نرم در مینی‌تب (Minitab)

## ۱. هدف آموزشی
* ارزیابی هم‌خطی چندگانه (Multicollinearity) با شاخص VIF
* برازش رگرسیون چندگانه خطی (Multiple Linear Regression)
* تحلیل نمودارهای مانده (Residuals Diagnostics)

## ۲. مراحل گام‌به‌گام در Minitab

### گام ۱: فراخوانی دیتاست
1. فایل `Chapter09_SoftSensor_Grinding_Quality_Dataset.xlsx` را باز کرده و شیت `Lab_Paired_Calibration` را وارد ورک‌شیت مینی‌تب کنید.

### گام ۲: برازش مدل رگرسیون (Fit Regression Model)
1. به مسیر زیر بروید:
   `Stat > Regression > Regression > Fit Regression Model`
2. تنظیمات زیر را وارد کنید:
   * **Responses:** `Lab_Blaine_LIMS`
   * **Continuous Predictors:**
     `Mill_Power_Lag8` `Feed_Flow_Lag8` `Cyclone_Pressure_Lag2` `Slurry_Density_Lag1` `Circulating_Load_Pct`
3. بر روی دکمه **Options** کلیک کرده و اطمینان حاصل کنید سطح اطمینان روی ۹۵٪ باشد.
4. بر روی دکمه **Graphs** کلیک کرده و گزینه **Four in one** را انتخاب کنید.
5. روی **OK** کلیک کنید.

### گام ۳: تفسیر نتایج و شاخص‌های آماری
* **ضریب تعیین ($R^2$ و $R^2_{\text{adj}}$):** مقادیر بالای ۸۰٪ نشان‌دهنده برازش مطلوب مدل سنسور نرم خطی است.
* **شاخص VIF (Variance Inflation Factor):** در جدول ضرایب، شاخص VIF برای هر متغیر نمایش داده می‌شود. اگر متغیری دارای $\text{VIF} > 5$ باشد، نشان‌دهنده هم‌خطی شدید است که نیازمند تکنیک‌های Stepwise یا استفاده از الگوریتم PLSR در پایتون می‌باشد.
* **نمودار ۴ در ۱ مانده‌ها:** بررسی کنید مانده‌ها دارای توزیع نرمال بوده و پدیده قیفی‌شدن (Heteroscedasticity) نداشته باشند.
