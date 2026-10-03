# راهنمای ساخت داشبورد پایش فرآیند فصل ۳ در Power BI

این راهنما نحوه بارگذاری داده‌های فصل ۳ و ایجاد شاخص‌های کلیدی در Power BI را تشریح می‌کند.

فایل داده:

[`Chapter03_QC_Separation_Dewatering_Data.xlsx`](../datasets/Chapter03_QC_Separation_Dewatering_Data.xlsx)

---

## ۱. مدل‌سازی داده

شیت‌های زیر را وارد Power BI کنید:

* `Process_Data`
* `Dashboard_Data`

نوع داده `DateTime` را روی **Date/Time** تنظیم کنید.

اگر `Dashboard_Data` دارای یک ستون تاریخ روزانه باشد، بهتر است یک جدول Calendar مستقل ایجاد و ارتباط آن با جداول عملیاتی از طریق تاریخ برقرار شود.

> ارتباط مستقیم `Date` با `DateTime` در Power BI فقط زمانی مناسب است که نوع و دانه‌بندی کلیدها به‌درستی مدیریت شده باشد.

---

## ۲. Measures اصلی DAX

### میانگین بازیابی آهن

```dax
Avg_Fe_Recovery =
AVERAGE(
    Process_Data[Fe_Recovery_pct]
)
```

### انحراف معیار رطوبت کیک

```dax
Moisture_StdDev =
STDEV.P(
    Process_Data[Filter_Cake_Moisture_pct]
)
```

### نرخ خارج از مشخصات رطوبت

```dax
Moisture_OOS_Rate =
DIVIDE(
    CALCULATE(
        COUNTROWS(Process_Data),
        Process_Data[Filter_Cake_Moisture_pct] > 10.5
    ),
    COUNTROWS(Process_Data),
    0
) * 100
```

### وضعیت موازنه آهن

```dax
Balance_Health_Flag =
IF(
    ABS(
        AVERAGE(
            Process_Data[Fe_Balance_Error_pct]
        )
    ) <= 3.0,
    "Healthy",
    "Investigate"
)
```

> برای تصمیم‌گیری عملیاتی بهتر است علاوه بر میانگین خطا، **میانگین قدرمطلق خطا** یا درصد رکوردهای خارج از محدوده نیز محاسبه شود؛ زیرا میانگین می‌تواند خطاهای مثبت و منفی را خنثی کند.

### درصد رکوردهای دارای خطای موازنه بالا

```dax
Balance_OOS_Rate =
DIVIDE(
    CALCULATE(
        COUNTROWS(Process_Data),
        ABS(Process_Data[Fe_Balance_Error_pct]) > 5
    ),
    COUNTROWS(Process_Data),
    0
) * 100
```

---

## ۳. کارت‌های KPI

برای Dashboard می‌توان کارت‌های زیر را ایجاد کرد:

### عیار آهن کنسانتره

```text
Target: ≥ 67.0%
```

### بازیابی آهن

```text
Target: ≥ 83.5%
```

### رطوبت کیک

```text
Target: 9.5%
Educational range: 8.5–10.5%
```

### کدورت سرریز تیکنر

```text
Educational reference: < 35 NTU
```

> مقادیر فوق حدود نمونه Dataset هستند و نباید بدون اعتبارسنجی با مشخصات محصول، طراحی تجهیزات و شرایط واقعی کارخانه به‌عنوان حدود عمومی صنعت استفاده شوند.

---

## ۴. نمودار ارتباط تیکنر و فیلتراسیون

از **Line and Clustered Column Chart** استفاده کنید.

### محور X

`DateTime`

### Column Y-axis

`Thickener_Overflow_Turbidity_NTU`

### Line Y-axis

`Filter_Cake_Moisture_pct`

هدف این نمودار بررسی هم‌زمانی تغییرات کدورت آب سرریز و رطوبت کیک است.

وجود هم‌زمانی آماری به‌تنهایی به معنی اثبات رابطه علّی نیست.

---

## ۵. Slicerها

Slicerهای پیشنهادی:

* `Circuit_Mode`
* `Ore_Blend`
* `Date`
* `Shift`

برای `Date` از یک Date Table استاندارد استفاده کنید.

---

## ۶. داشبورد پیشنهادی

### ردیف اول — KPI

* Concentrate Fe
* Fe Recovery
* Cake Moisture
* Overflow Turbidity
* Fe Balance Error

### ردیف دوم — فرآیند

* روند رطوبت کیک
* روند کدورت سرریز
* روند بازیابی آهن

### ردیف سوم — تحلیل علل

* Slimes vs Cake Moisture
* Vacuum vs Cake Moisture
* Fe Grade vs Fe Recovery
* Balance Error by Shift

### ردیف چهارم — وضعیت QC

* تعداد رکوردهای OOS
* درصد موازنه‌های نامعتبر
* تعداد سیگنال‌های SPC
* آخرین وضعیت فرآیند

این ساختار Dashboard را از یک صفحه نمایش KPI به یک ابزار **Process Diagnosis** نزدیک می‌کند.
