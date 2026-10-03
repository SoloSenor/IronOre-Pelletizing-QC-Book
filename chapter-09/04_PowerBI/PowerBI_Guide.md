# راهنمای ساخت داشبورد سنسور نرم در Power BI

## ۱. هدف داشبورد
ارائه مانیتورینگ بلادرنگ برای اتاق کنترل خردایش به همراه نمایش وضعیت کیفیت (Advisory Mode).

## ۲. گام‌های پیاده‌سازی مدل در Power BI

### گام اول: وارد کردن دیتاست
1. نرم‌افزار Power BI Desktop را باز کنید.
2. گزینه **Get Data > Excel workbook** را انتخاب کرده و فایل `Chapter09_SoftSensor_Grinding_Quality_Dataset.xlsx` را بارگذاری کنید.
3. برگه `SCADA_1min_Telemetry` را انتخاب و دکمه **Load** را بزنید.

### گام دوم: فرمول‌های سنجه‌ای (DAX Measures)
یک جدول برای Measures بسازید و فرمول‌های زیر را تعریف کنید:

```dax
// میانگین سطح ویژه بلین تخمینی سنسور نرم
Avg_Predicted_Blaine = AVERAGE(SCADA_1min_Telemetry[True_Blaine_Target_cm2g])
```

```dax
// میانگین بلین اندازه‌گیری‌شده در آزمایشگاه سنتی
Avg_Lab_Blaine = AVERAGE(SCADA_1min_Telemetry[Lab_Blaine_LIMS])
```

```dax
// وضعیت کیفیت جهت صدور آلارم اپراتور اتاق کنترل
QC_Advisory_Status = 
VAR BlaineVal = [Avg_Predicted_Blaine]
RETURN
IF(ISBLANK(BlaineVal), "No Data",
    IF(BlaineVal >= 1750 && BlaineVal <= 1850, "🟢 در محدوده بهینه (1800±50)",
    IF(BlaineVal < 1750, "🟡 دانه‌بندی درشت (Coarse Grind)", "🔴 سایش بیش از حد (Overgrinding)")
    )
)
```

```dax
// شاخص توان ویژه خردایش
Specific_Energy_kWh_t = 
DIVIDE(
    AVERAGE(SCADA_1min_Telemetry[Mill_Power_kW]),
    (AVERAGE(SCADA_1min_Telemetry[Feed_Flow_m3h]) * (AVERAGE(SCADA_1min_Telemetry[Slurry_Density_kgm3]) / 1000.0)),
    0
)
```

### گام سوم: طراحی ویژوال‌ها در گزارش
1. **گیج وضعیت بلین (Gauge):** نمایش `Avg_Predicted_Blaine` با مقدار هدف ۱۸۰۰ و حدود کنترلی ۱۷۵۰ تا ۱۸۵۰.
2. **کارت وضعیت هشدار (Card Visual):** اتصال سنجه `QC_Advisory_Status` با فرمت‌بندی شرطی رنگی.
3. **نمودار روند زمانی (Line and Clustered Column Chart):**
   * محور X: ستون `Timestamp`
   * خط اول: `Avg_Predicted_Blaine` (پیوسته و دقیقه‌ای)
   * نقاط گسسته: `Avg_Lab_Blaine` (نقاط پراکنده هر ۲ ساعت جهت صحه‌گذاری آنلاین سنسور نرم)
