# 🟡 کارگاه ۴ — Power BI: مدل ستاره‌ای و داشبورد کیفیت کوره

> 📥 پیش‌نیاز: [Pellet_Induration_QC_Chapter5_Dataset.xlsx](../data/Pellet_Induration_QC_Chapter5_Dataset.xlsx)

## هدف
ساخت مدل تحلیلی قابل فیلتر بر اساس زمان، شیفت، کمپین و زون و نمایش روندهای حرارتی، CCS، Black Core و قابلیت فرایند.

## گام ۱ — بارگذاری و تمیزکاری
Get Data ▸ Excel Workbook. بارگذاری `Fact_Process_Hourly` و `Fact_QC_Samples`؛ شیت‌های `Ergun_Equation_Lab` و `Dim_Zones_Campaigns` فقط در صورت نیاز به تحلیل اضافه شوند. انواع داده Timestamp را Date/Time و مقادیر اندازه‌گیری را Decimal Number تنظیم کنید.

## گام ۲ — Lag Alignment و مدل داده
Power Query: به QC ستون `Process_Anchor_Timestamp = Sample_Timestamp - #duration(0,2,0,0)` اضافه کنید. سپس Merge با جدول ساعتی روی زمان anchor (پس از گرد کردن/تطبیق ساعتی و تأیید تعریف زمان در دیتاست) انجام دهید. QC Fact را به Process Fact از طریق کلید زمانی پیوند دهید؛ رابطه many-to-many نسازید. راه بهتر برای مدل پایدار: جدول زمان یکتا و ابعاد `Dim_Date`, `Dim_Campaign`, `Dim_Shift`, `Dim_Zone`؛ Factها روابط یک‌به‌چند از ابعاد بگیرند. دقت کنید فرآیند ساعتی و QC با نرخ نمونه‌برداری متفاوت‌اند و Join نباید ردیف‌های QC را تکثیر کند.

## گام ۳ — سنجه‌های DAX
نمونه سنجه‌های پایه (نام جدول‌ها را با نام واقعی مدل جایگزین کنید):

```DAX
Avg CCS = AVERAGE(Fact_QC_Samples[CCS_Mean_daN])
CCS Below LSL =
    CALCULATE(COUNTROWS(Fact_QC_Samples), Fact_QC_Samples[CCS_Mean_daN] < 250)
CCS N = COUNT(Fact_QC_Samples[CCS_Mean_daN])
Pct Below LSL = DIVIDE([CCS Below LSL], [CCS N])

Moving Cpk CCS =
VAR CurrentDate = MAX(Dim_Date[Date])
VAR WindowRows =
    CALCULATETABLE(Fact_QC_Samples,
        DATESINPERIOD(Dim_Date[Date], CurrentDate, -30, DAY))
VAR Mu = AVERAGEX(WindowRows, Fact_QC_Samples[CCS_Mean_daN])
VAR Sigma = STDEVX.S(WindowRows, Fact_QC_Samples[CCS_Mean_daN])
RETURN IF(Sigma > 0, DIVIDE(Mu - 250, 3 * Sigma))
```

`Moving Cpk CCS` در این نمونه **فقط شاخص یک‌طرفه بر مبنای انحراف معیار نمونه‌ای** است؛ برای گزارش رسمی قابلیت، ابتدا پایداری فرایند، توزیع/خودهمبستگی و تعریف σ درون‌گروهی را ارزیابی کنید. به پنجره‌ای با تعداد نمونه کافی (مثلاً ۳۰) فیلتر اضافه کنید.

## گام ۴ — چیدمان داشبورد چهارپنله
1. **Thermal Profile:** خط دمای UDD/DDD/PH/Firing در زمان + خطوط حدود عملیاتی.
2. **Hydrodynamics:** روند `Windbox_Avg_DP_kPa` و رابطه آن با ارتفاع بستر/سرعت پالت.
3. **Product Quality:** روند CCS، LSL=250، تامبل و درصد Black Core.
4. **Campaign & Capability:** کارت‌های میانگین CCS، درصد زیر LSL، Moving Cpk و اسلایسرهای Campaign/Shift/Date.

## گام ۵ — کنترل‌های اعتبار
- یک ردیف هر Timestamp در Fact ساعتی و یک ردیف هر Sample_ID در QC.
- پس از اعمال فیلتر کمپین، جمع تعداد نمونه‌ها با رکوردهای منبع کنترل شود.
- سنجه CCS از QC Fact و سنجه‌های دما از Process Fact خوانده شوند؛ رابطه‌های مبهم غیرفعال/اصلاح شوند.

## تحویل
فایل `.pbix` به‌همراه تصویر داشبورد و یادداشت تعریف lag و محاسبه Moving Cpk.
