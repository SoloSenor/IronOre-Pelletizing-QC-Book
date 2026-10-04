# راهنمای عملی فصل ۱۳ در مینی‌تب (Minitab)

## ۱. هدف
رسم نمودارهای کنترل کیفیت (I-MR و Xbar-S) با حذف داده‌های توقف یا خطای سنسور و فازبندی بر اساس رخدادها و کمپین‌های تولید.

## ۲. گام‌های اجرایی
1. فایل اکسل را باز کرده و شیت‌های `process_timeseries` و `qc_lab_results` را وارد کنید.
2. از `Data > Subset Worksheet` برای شرط `Quality = "Good" AND Equipment_State = "Running"` استفاده کنید.
3. از `Stat > Control Charts > Variables Charts for Individuals > I-MR` نمودار را رسم کنید. در **I-MR Options > Stages** متغیر `BatchID` یا `Campaign` را برای محاسبه جداگانه حدود کنترل انتخاب کنید.
