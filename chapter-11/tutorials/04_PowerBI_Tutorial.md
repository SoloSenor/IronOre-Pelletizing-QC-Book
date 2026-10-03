# راهنمای پیاده‌سازی داشبورد مدیریت ریسک کیفی در Power BI

این داشبورد خروجی مدل پیش‌بین فصل ۱۱ را به یک لایه عملیاتی برای پایش کیفیت گندله تبدیل می‌کند.

هدف داشبورد:

```text
Process Data
      ↓
Predicted CCS Distribution
      ↓
P10 / LSL Risk
      ↓
Black Core Risk
      ↓
Operational Monitoring
```

---

# گام ۱: مدل داده

دو جدول اصلی را وارد Power BI کنید:

```text
Shift_Data
Pellet_CCS
```

کلید مشترک:

```text
Lot_ID
```

رابطه پیشنهادی:

```text
Shift_Data 1 ───── * Pellet_CCS
```

مشروط بر اینکه `Shift_Data[Lot_ID]` واقعاً یکتا باشد.

اگر `Lot_ID` در `Shift_Data` تکراری است، ابتدا یک جدول Dimension/Lookup یکتا برای Lot ایجاد کنید.

---

# گام ۲: شاخص میانگین سه شیفت

اگر منظور واقعاً سه **رکورد شیفت اخیر** است، از `TOPN` استفاده کنید.

```dax
CCS_Moving_Avg_3_Shift =
VAR CurrentTime =
    MAX('Shift_Data'[DateTime_End])

VAR Last3Shifts =
    TOPN(
        3,
        FILTER(
            ALL('Shift_Data'),
            'Shift_Data'[DateTime_End] <= CurrentTime
        ),
        'Shift_Data'[DateTime_End],
        DESC
    )

RETURN
    AVERAGEX(
        Last3Shifts,
        'Shift_Data'[CCS_mean]
    )
```

`TOPN` در DAX برای استخراج N رکورد برتر از یک جدول استفاده می‌شود.

> اگر هدف «میانگین متحرک 24 ساعته» است، نام و منطق Measure باید به `CCS_Moving_Avg_24h` تغییر کند؛ میانگین سه شیفت و میانگین 24 ساعته یک مفهوم واحد نیستند.

---

# گام ۳: نرخ گندله‌های زیر LSL

اگر `LSL = 2000 N` به‌عنوان مشخصات محصول تعریف شده باشد:

```dax
Fragile_Pellet_Rate =
DIVIDE(
    CALCULATE(
        COUNTROWS('Pellet_CCS'),
        'Pellet_CCS'[CCS_N] < 2000
    ),
    COUNTROWS('Pellet_CCS'),
    0
)
```

این Measure باید فقط روی داده‌هایی محاسبه شود که نمونه‌برداری و Lot آنها معتبر است.

---

# گام ۴: Black Core Fraction

اگر `Has_BlackCore` در سطح تک‌گندله‌ای وجود داشته باشد:

```dax
BlackCore_Fraction =
DIVIDE(
    CALCULATE(
        COUNTROWS('Pellet_CCS'),
        'Pellet_CCS'[Has_BlackCore] = 1
    ),
    COUNTROWS('Pellet_CCS'),
    0
)
```

این شاخص با `BlackCore_frac` ذخیره‌شده در `Shift_Data` تفاوت دارد.

اگر هر دو وجود داشته باشند، باید مشخص شود که:

```text
BlackCore_Fraction
```

از داده خام محاسبه می‌شود و:

```text
BlackCore_frac
```

شاخص تجمیعی ثبت‌شده در سطح Lot است.

---

# گام ۵: آخرین مقدار CCS Prediction

اگر ستون‌های زیر در `Shift_Data` ذخیره شده باشند:

```text
CCS_mean_pred
CCS_std_pred
CCS_P10_pred
Risk_P_below_LSL
```

می‌توان آخرین مقدار را با زمان استخراج کرد.

### Latest predicted mean

```dax
Latest CCS Mean Prediction =
VAR LatestTime =
    MAX('Shift_Data'[DateTime_End])

RETURN
    CALCULATE(
        MAX('Shift_Data'[CCS_mean_pred]),
        'Shift_Data'[DateTime_End] = LatestTime
    )
```

### Latest P10

```dax
Latest CCS P10 =
VAR LatestTime =
    MAX('Shift_Data'[DateTime_End])

RETURN
    CALCULATE(
        MAX('Shift_Data'[CCS_P10_pred]),
        'Shift_Data'[DateTime_End] = LatestTime
    )
```

---

# گام ۶: آخرین ریسک زیر LSL

```dax
Latest CCS Risk =
VAR LatestTime =
    MAX('Shift_Data'[DateTime_End])

RETURN
    CALCULATE(
        MAX('Shift_Data'[Risk_P_below_LSL]),
        'Shift_Data'[DateTime_End] = LatestTime
    )
```

---

# گام ۷: وضعیت ریسک

اگر `5%` آستانه آموزشی باشد:

```dax
CCS Risk Status =
VAR RiskValue =
    [Latest CCS Risk]

RETURN
    SWITCH(
        TRUE(),
        ISBLANK(RiskValue), "No Data",
        RiskValue >= 0.05, "Investigate",
        "Monitor"
    )
```

> `5%` باید در پروژه واقعی با specification و هزینه‌های خطا کالیبره شود.

---

# گام ۸: شاخص شرایط کوره

از `SELECTEDVALUE` برای یک کارت چندشیفته‌ای استفاده نکنید؛ چون اگر context شامل چند رکورد باشد، ممکن است مقدار واحدی وجود نداشته باشد.

ابتدا آخرین زمان را پیدا کنید:

```dax
Latest O2 =
VAR LatestTime =
    MAX('Shift_Data'[DateTime_End])

RETURN
    CALCULATE(
        MAX('Shift_Data'[O2_avg_pct]),
        'Shift_Data'[DateTime_End] = LatestTime
    )
```

برای FeO:

```dax
Latest FeO =
VAR LatestTime =
    MAX('Shift_Data'[DateTime_End])

RETURN
    CALCULATE(
        MAX('Shift_Data'[FeO]),
        'Shift_Data'[DateTime_End] = LatestTime
    )
```

---

# گام ۹: Furnace Quality Monitoring Flag

آستانه‌های زیر فقط نمونه آموزشی هستند:

```dax
Furnace_Quality_Flag =
VAR O2Value =
    [Latest O2]

VAR FeOValue =
    [Latest FeO]

RETURN
    SWITCH(
        TRUE(),
        ISBLANK(O2Value) || ISBLANK(FeOValue),
            "No Data",

        O2Value < 7.0
            && FeOValue > 1.2,
            "Investigate",

        "Monitor"
    )
```

این Measure نباید با عبارت‌هایی مانند:

```text
"قطعاً مغز سیاه ایجاد شده"
```

تفسیر شود.

این فقط یک **شرایط هشدار چندمتغیره** است.

مقادیر `7.0` و `1.2` باید با داده واقعی، specification و دانش فرایند کالیبره شوند.

---

# گام ۱۰: شمارش ریسک‌های تاریخی

```dax
CCS Risk Event Count =
CALCULATE(
    COUNTROWS('Shift_Data'),
    'Shift_Data'[Risk_P_below_LSL] >= 0.05
)
```

و برای Black Core:

```dax
BlackCore Event Count =
CALCULATE(
    COUNTROWS('Pellet_CCS'),
    'Pellet_CCS'[Has_BlackCore] = 1
)
```

---

# گام ۱۱: معماری داشبورد

## ردیف اول — KPI

پیشنهاد:

```text
Latest CCS Mean
Latest CCS P10
Latest CCS Risk
Black Core Fraction
Process Stability
```

---

## ردیف دوم — روند CCS

Line Chart:

```text
X = DateTime / Lot_ID
Y1 = CCS_mean
Y2 = CCS_P10
```

در صورت وجود Prediction Interval یا P90:

```text
P10
P50
P90
```

را به‌صورت band یا خطوط جداگانه نمایش دهید.

---

## ردیف سوم — ریسک

نمودار:

```text
Risk P(CCS < LSL)
```

در طول زمان.

خط آستانه آموزشی:

```text
5%
```

در صورت استفاده از آستانه عملیاتی واقعی، مقدار آن باید از جدول Configuration خوانده شود، نه اینکه داخل DAX hard-code شود.

---

# گام ۱۲: پنل Black Core

شاخص‌های پیشنهادی:

```text
Black Core Fraction
Black Core Event Count
Black Core Probability
```

و نمودار:

```text
Black Core Probability vs Time
```

در کنار:

```text
O2
FeO
T_firing_peak
TimeAbove1200_min
```

قرار گیرد.

---

# گام ۱۳: فیلترها

Slicerهای پیشنهادی:

* Date
* Shift
* Lot
* Process Stability
* Product Grade
* Furnace regime

---

# گام ۱۴: Drill-through

برای هر `Lot_ID` یک صفحه Drill-through بسازید.

نمایش:

```text
Lot ID
CCS Mean
CCS Std
CCS P10
Risk P(CCS < LSL)
Black Core Fraction
T_firing_peak
TimeAbove1200_min
O2
FeO
Basicity
```

این صفحه باید امکان ارتباط بین:

```text
Risk Signal
      ↓
Process Variables
      ↓
Laboratory Evidence
```

را فراهم کند.

---

# گام ۱۵: اصل مهم در داشبورد

Power BI نباید از یک شاخص آماری مستقیماً به یک علت فیزیکی برسد.

مثلاً:

```text
Risk > 5%
```

نباید مستقیماً تبدیل شود به:

```text
Burner Failure
```

یا:

```text
Liner Failure
```

بلکه:

```text
Statistical Signal
        ↓
Verification
        ↓
Process Evidence
        ↓
Laboratory Evidence
        ↓
Inspection
        ↓
Action
```

باید حفظ شود.

---

# گام ۱۶: تفکیک Specification و Risk Threshold

سه مفهوم را جدا نگه دارید:

### Specification Limit

مثلاً:

```text
LSL = 2000 N
```

حد مشخصات محصول است.

### Statistical Risk Threshold

مثلاً:

```text
P(CCS < LSL) = 5%
```

آستانه تصمیم‌گیری مدل است.

### Control Limit

در صورت استفاده از SPC، حد آماری کنترل فرایند است.

این سه مقدار از نظر مفهومی یکسان نیستند.

---

# خروجی نهایی داشبورد

داشبورد باید پاسخ چهار سؤال را فراهم کند:

```text
1. کیفیت فعلی چگونه است؟
2. دُم چپ توزیع چه وضعیتی دارد؟
3. احتمال عبور از Specification چقدر است؟
4. برای بررسی علت، کدام متغیرهای فرایندی باید بررسی شوند؟
```

نه اینکه صرفاً یک کارت قرمز/سبز تولید کند.

👉 [بازگشت به فهرست آموزش‌ها](../README.md)
