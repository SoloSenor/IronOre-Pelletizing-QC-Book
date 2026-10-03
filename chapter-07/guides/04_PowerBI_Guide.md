# معماری و پیاده‌سازی داشبورد EWMA و CUSUM در Power BI

> **هدف:** نمایش وضعیت آماری فرآیند، سیگنال‌های EWMA/CUSUM و داده‌های تشخیصی در یک داشبورد مدیریتی.
>
> محاسبات انباشتی سری زمانی بهتر است در Python/SQL یا لایه پردازش داده انجام شوند و Power BI بیشتر برای مدل‌سازی، فیلتر، بصری‌سازی و ارائه هشدار استفاده شود.

---

# ۱. ساختار داده

جدول `Process_Data` بهتر است شامل ستون‌های محاسبه‌شده زیر باشد:

* `Timestamp`
* `P80_Micron`
* `EWMA_P80_lam0_2`
* `UCL_P80`
* `LCL_P80`
* `FeO_Percent`
* `CUSUM_FeO_plus`
* `CUSUM_FeO_minus`
* `SpecificPower_kWht`
* `ReturnLoad_th`
* `FeedHardness_Index`
* `FeedRate_th`

> بهتر است در نام ستون‌های داده از `.` استفاده نشود؛ برای مثال `EWMA_P80_lam0_2` نسبت به نام‌هایی مانند `EWMA_P80_lam0.2` برای نگهداری و استفاده در ابزارهای مختلف مناسب‌تر است.

---

# ۲. سنجه آخرین EWMA

برای داشبوردی که بر اساس آخرین Timestamp وضعیت را نشان می‌دهد:

```dax
Latest EWMA P80 =
VAR LatestTime =
    MAX(Process_Data[Timestamp])
RETURN
    CALCULATE(
        MAX(Process_Data[EWMA_P80_lam0_2]),
        Process_Data[Timestamp] = LatestTime
    )
```

---

# ۳. آخرین UCL

```dax
Latest UCL P80 =
VAR LatestTime =
    MAX(Process_Data[Timestamp])
RETURN
    CALCULATE(
        MAX(Process_Data[UCL_P80]),
        Process_Data[Timestamp] = LatestTime
    )
```

---

# ۴. وضعیت EWMA

```dax
P80 EWMA Status =
VAR EWMAValue =
    [Latest EWMA P80]

VAR UCLValue =
    [Latest UCL P80]

RETURN
SWITCH(
    TRUE(),
    ISBLANK(EWMAValue), "No Data",
    ISBLANK(UCLValue), "No Limit",
    EWMAValue > UCLValue, "Investigate",
    "Within Control Limits"
)
```

این سنجه نمی‌گوید لاینر حتماً ساییده شده است.

فقط مشخص می‌کند که EWMA نسبت به حد کنترل محاسبه‌شده سیگنال داده است.

---

# ۵. آخرین CUSUM مثبت

```dax
Latest CUSUM Plus =
VAR LatestTime =
    MAX(Process_Data[Timestamp])
RETURN
    CALCULATE(
        MAX(Process_Data[CUSUM_FeO_plus]),
        Process_Data[Timestamp] = LatestTime
    )
```

---

# ۶. وضعیت CUSUM

```dax
FeO CUSUM Status =
VAR CUSUMValue =
    [Latest CUSUM Plus]

RETURN
SWITCH(
    TRUE(),
    ISBLANK(CUSUMValue), "No Data",
    CUSUMValue >= 5.0, "Investigate",
    "Normal"
)
```

---

# ۷. تعداد سیگنال‌های EWMA

```dax
P80 EWMA Signal Count =
COUNTROWS(
    FILTER(
        Process_Data,
        Process_Data[EWMA_P80_lam0_2]
            > Process_Data[UCL_P80]
        ||
        Process_Data[EWMA_P80_lam0_2]
            < Process_Data[LCL_P80]
    )
)
```

---

# ۸. تعداد سیگنال‌های CUSUM

```dax
FeO CUSUM Signal Count =
COUNTROWS(
    FILTER(
        Process_Data,
        Process_Data[CUSUM_FeO_plus] >= 5
        ||
        Process_Data[CUSUM_FeO_minus] >= 5
    )
)
```

---

# ۹. معماری پیشنهادی داشبورد

## ردیف اول — KPI

### Card 1

`Latest EWMA P80`

### Card 2

`P80 EWMA Status`

### Card 3

`Latest CUSUM Plus`

### Card 4

`FeO CUSUM Status`

---

# ۱۰. نمودار EWMA

Line Chart:

### X-axis

`Timestamp`

### Values

* `P80_Micron`
* `EWMA_P80_lam0_2`
* `UCL_P80`
* `LCL_P80`

این نمودار وضعیت خام و وضعیت هموارشده را هم‌زمان نمایش می‌دهد.

---

# ۱۱. نمودار CUSUM

Line Chart:

### X-axis

`Timestamp`

### Values

* `CUSUM_FeO_plus`
* `CUSUM_FeO_minus`

همچنین یک Reference Line:

`5.0`

اضافه شود.

---

# ۱۲. پنل تشخیصی سایش آسیاب

برای بررسی فرضیه سایش لاینر:

### نمودار اول

`P80_Micron` در طول زمان

### نمودار دوم

`SpecificPower_kWht`

### نمودار سوم

`ReturnLoad_th`

### نمودار چهارم

`FeedHardness_Index`

این چیدمان امکان مقایسه هم‌زمان تغییرات متغیرهای مرتبط را فراهم می‌کند.

> افزایش P80 به‌تنهایی اثبات‌کننده سایش لاینر نیست؛ تغییرات سختی خوراک، نرخ خوراک، شرایط طبقه‌بندی و سایر عوامل نیز باید بررسی شوند.

---

# ۱۳. پنل تشخیصی مشعل

متغیرهای زیر نمایش داده شوند:

* `BurnerZoneTemp_C`
* `O2_Percent`
* `FeO_Percent`
* `CUSUM_FeO_plus`

در صورت وجود Lag فرآیندی، نمودارها باید به‌گونه‌ای تنظیم شوند که مقایسه زمانی صحیح انجام شود.

---

# ۱۴. Drill-through

با انتخاب یک سیگنال، صفحه Drill-through می‌تواند موارد زیر را نمایش دهد:

* Timestamp
* مقدار متغیر اصلی
* EWMA/CUSUM
* Feed Rate
* Feed Hardness
* Specific Power
* Return Load
* Burner Temperature
* O₂
* FeO

هدف Drill-through، فراهم‌کردن شواهد لازم برای **تحلیل علت** است.

---

# ۱۵. معماری تصمیم

ساختار پیشنهادی:

**Monitoring**

↓

**Statistical Signal**

↓

**Verification**

↓

**Diagnostic Evidence**

↓

**Engineering Inspection**

↓

**Corrective Action**

↓

**Post-Action Verification**

این ساختار از تبدیل یک آلارم آماری به یک تشخیص فیزیکی بدون بررسی میدانی جلوگیری می‌کند.

---

# ۱۶. نکته مهم درباره CBM

داشبورد می‌تواند یک سیگنال را برای بررسی نگهداری ایجاد کند؛ اما ایجاد خودکار Work Order بهتر است به یک Rule Engine یا CMMS متصل شود که علاوه بر SPC Signal، شرایط تأییدکننده دیگری را نیز بررسی کند.

برای مثال:

**EWMA Signal + Persistent Trend + Diagnostic Evidence → Inspection Request**

این رویکرد نسبت به:

**EWMA Signal → Immediate Failure Diagnosis**

از نظر طراحی سیستم پایش قابل‌دفاع‌تر است.
