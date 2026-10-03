# طراحی داشبورد مانیتورینگ کیفی گندله خام در Power BI

> **فایل داده مرجع:** [`Green_Pellet_QC_Training_Data4.xlsx`](../Green_Pellet_QC_Training_Data4.xlsx)
> **مرجع تئوری:** [فصل ۴ — بخش ۴-۱۰](../ch04_green_pellet_text.md)

## سناریو

هدف داشبورد، ایجاد یک نمای مدیریتی از:

* رطوبت گندله خام؛
* انطباق اندازه گندله؛
* استحکام تر؛
* ریزدانه‌ها؛
* و وضعیت کلی فرآیند

است.

> حدود عددی این مثال آموزشی هستند و باید با specification و operating window واقعی کارخانه جایگزین شوند.

---

## ۱. میانگین رطوبت

```dax
Avg Moisture =
AVERAGE('Green_Pellet_QC'[Moisture_Pct])
```

---

## ۲. درصد رکوردهای داخل پنجره آموزشی رطوبت

```dax
Moisture In Window Rate =
DIVIDE(
    CALCULATE(
        COUNTROWS('Green_Pellet_QC'),
        'Green_Pellet_QC'[Moisture_Pct] >= 8.5,
        'Green_Pellet_QC'[Moisture_Pct] <= 9.1
    ),
    COUNTROWS('Green_Pellet_QC),
    0
) * 100
```

> در صورتی که نام Query یا Table متفاوت است، نام `'Green_Pellet_QC'` را با نام واقعی جدول جایگزین کنید.

---

## ۳. درصد انطباق اندازه هدف

در این مثال آموزشی، 75% به‌عنوان حد یک‌طرفه نمونه استفاده می‌شود:

```dax
Target Size Compliance =
DIVIDE(
    CALCULATE(
        COUNTROWS('Green_Pellet_QC'),
        'Green_Pellet_QC'[Target_Size_Pct] >= 75
    ),
    COUNTROWS('Green_Pellet_QC'),
    0
) * 100
```

این مقدار **specification عمومی صنعت نیست** و صرفاً یک threshold آموزشی برای دیتاست است.

---

## ۴. نرخ رطوبت خارج از پنجره

```dax
Moisture OOS Rate =
DIVIDE(
    CALCULATE(
        COUNTROWS('Green_Pellet_QC'),
        FILTER(
            'Green_Pellet_QC',
            'Green_Pellet_QC'[Moisture_Pct] < 8.5
                ||
            'Green_Pellet_QC'[Moisture_Pct] > 9.1
        )
    ),
    COUNTROWS('Green_Pellet_QC'),
    0
) * 100
```

---

## ۵. شاخص وضعیت فرآیند

برای جلوگیری از وابستگی وضعیت به `SELECTEDVALUE` یک رکورد منفرد، وضعیت را بر اساس میانگین رطوبت در context فعلی محاسبه می‌کنیم:

```dax
QC Status Flag =
VAR MoistureValue =
    [Avg Moisture]

RETURN
SWITCH(
    TRUE(),
    ISBLANK(MoistureValue), "No Data",
    MoistureValue < 8.5, "Below Educational Window",
    MoistureValue > 9.1, "Above Educational Window",
    "Within Educational Window"
)
```

این شاخص صرفاً وضعیت رطوبت را نشان می‌دهد و **علت انحراف را تعیین نمی‌کند**.

---

## ۶. ویژوال‌های پیشنهادی

### KPI Cards

* `Avg Moisture`
* `Moisture In Window Rate`
* `Moisture OOS Rate`
* `Target Size Compliance`

### Run/Line Chart

محور X:

`Timestamp`

محور Y:

`Moisture_Pct`

در صورت نیاز خطوط مرجع 8.5 و 9.1 نیز اضافه شوند.

### Scatter Plot

X:

`Moisture_Pct`

Y:

`Wet_Strength_N`

Legend یا grouping:

`Shift`

در صورت مناسب بودن ساختار داده.

### Clustered Column Chart

مقایسه شیفت‌ها برای:

* `Fines_Pct`
* `Oversize_Pct`
* `Target_Size_Pct`

### Process Relationship View

در صورت وجود داده کافی، روابط زیر بررسی شوند:

**Feed Rate → Moisture → Wet Strength → Size Distribution**

این نمودارها برای **تشخیص و پایش** هستند و به‌تنهایی اثبات‌کننده رابطه علّی نیستند.

---

## ۷. تفکیک سه نوع حد

در داشبورد حتماً میان این سه مفهوم تفاوت گذاشته شود:

### Specification Limit

حد قراردادی/کیفی محصول.

### Operating Window

محدوده‌ای که بر اساس تجربه، آزمایش یا داده فرآیندی برای بهره‌برداری مناسب تعریف شده است.

### Control Limit

حد آماری استخراج‌شده از رفتار فرآیند برای تشخیص تغییرات غیرعادی.

این سه مفهوم نباید در داشبورد با یکدیگر جایگزین شوند.
