# آموزش Excel Power Query و Power Pivot برای داشبورد QC

> فایل تمرین: [دیتاست مصنوعی فصل](QC_Ch13_Ch14_Synthetic_Dataset.xlsx) | [متن فصل ۱۴](CHAPTER_14_TEXT.md) | [Power BI](POWER_BI_TUTORIAL.md) | [Python](PYTHON_TUTORIAL.md) | [Minitab](MINITAB_TUTORIAL.md)

## پیش‌نیاز
Excel 2016 یا جدیدتر با Power Query و Data Model؛ در برخی نسخه‌ها Power Pivot باید از File → Options → Add-ins → COM Add-ins فعال شود. نسخه Mac ممکن است Power Pivot نداشته باشد.

## ۱. وارد کردن جدول‌ها با Power Query
1. Data → Get Data → From File → From Workbook؛ فایل همین پوشه را انتخاب کنید.
2. در Navigator برگه‌های `Fact_QC_Result`, `Fact_Process_Tag`, `Fact_Monthly_KPI` و `Dim_*` لازم را **Transform Data** کنید.
3. در Power Query نوع ستون‌ها را تنظیم کنید: زمان‌ها Date/Time، `Value` Decimal Number، پرچم‌ها Whole Number، کلیدهای متنی Text.
4. Factها را به Long format نگه دارید (هر ردیف یک نمونه-پارامتر). روی کلیدها Trim/Clean انجام دهید. ردیف‌های خطادار را حذف نکنید؛ فیلتر `DataQualityFlag` را به‌صورت انتخابی به گزارش اضافه کنید.
5. برای هر Query گزینه **Close & Load To… → Only Create Connection** و **Add this data to the Data Model** را تیک بزنید. همه جدول‌های مرجع لازم را نیز به Data Model اضافه کنید.

## ۲. ساخت روابط در Data Model
Power Pivot → Manage → Diagram View. روابط یک‌به‌چند از ابعاد به Factها بسازید:
- `Dim_DateTime[ShiftKey]` → `Fact_QC_Result[ShiftKey]` و `Fact_Process_Tag[ShiftKey]`
- `Dim_PlantArea[PlantAreaID]` → `Fact_QC_Result[PlantAreaID]`
- `Dim_Material[MaterialID]` → `Fact_QC_Result[MaterialID]`
- `Dim_Shift[ShiftID]` → `Fact_QC_Result[Shift]` (در صورت هم‌نوع بودن مقادیر؛ فایل از A/B/C در Fact و Shift A/B/C در Dimension استفاده می‌کند، پس ستون `ShiftCode` مشتق‌شده A/B/C در Dim_Shift بسازید و آن را وصل کنید.)
- `Dim_Parameter[Parameter]` → `Fact_QC_Result[Parameter]`
- `Dim_TestType[TestTypeID]` → `Fact_QC_Result[TestTypeID]`
- `Dim_Operator[OperatorID]` → `Fact_QC_Result[OperatorID]`

در Power Query برای `Dim_Shift` ستون `ShiftCode` بسازید (Extract متن بعد از فاصله) تا کلید A/B/C با Fact سازگار شود. Factها را مستقیماً به هم متصل نکنید. برای `Fact_Monthly_KPI` از `YearMonth` در Pivot یا از تقویم ماهانه مناسب استفاده کنید؛ با Fact ردیفی رابطه مستقیم ندهید.

## ۳. Measureها در Power Pivot
Power Pivot → Manage → Fact_QC_Result → Calculation Area. Measureهای زیر را به‌عنوان Measure بسازید (نه calculated column)؛ جداکننده آرگومان ممکن است در Excel محلی `;` باشد.

```DAX
Total Results := COUNTROWS ( Fact_QC_Result )
OOS Results := CALCULATE ( [Total Results], Fact_QC_Result[IsConform] = 0 )
Conformance % := DIVIDE ( [Total Results] - [OOS Results], [Total Results], 0 )
OOS % := DIVIDE ( [OOS Results], [Total Results], 0 )
Avg Value := AVERAGE ( Fact_QC_Result[Value] )
StdDev Value := STDEV.S ( Fact_QC_Result[Value] )
Median Value := MEDIAN ( Fact_QC_Result[Value] )

TAT Avg (min) :=
AVERAGEX ( Fact_QC_Result,
 DATEDIFF ( Fact_QC_Result[SampleDateTime], Fact_QC_Result[ResultDateTime], MINUTE ) )

Valid Results := CALCULATE ( [Total Results], Fact_QC_Result[DataQualityFlag] = "OK" )
Data Quality % := DIVIDE ( [Valid Results], [Total Results], 0 )
```

Number Format را برای انطباق/OOS/Data Quality به Percentage و Avg Value به تعداد اعشار متناسب با واحد پارامتر تنظیم کنید. توجه: Average Value در حضور چند Parameter معنا ندارد؛ حتماً پارامتر را در Rows یا Slicer محدود کنید.

## ۴. PivotTable و PivotChart
1. Insert → PivotTable → **Use this workbook’s Data Model**.
2. Pivot عملیاتی:
   - Rows: `Fact_QC_Result[Parameter]`
   - Values: `Avg Value`, `OOS Results`, `Conformance %`, `TAT Avg (min)`
   - Filters: PlantArea, Material, Shift
3. برای روند: Rows = `Dim_DateTime[Date]` و Values = `Avg Value`; یک PivotChart خطی بسازید. SampleDateTime در Fact و ShiftKey در تقویم می‌توانند نقش‌های زمانی متفاوت داشته باشند؛ نمودار را با مبنای زمانی اعلام‌شده برچسب بزنید.
4. برای شاخص‌های ماهانه، Pivot جداگانه بر پایه `Fact_Monthly_KPI` بسازید: `YearMonth` در Rows، `ConformancePct`, `OOS_Count`, `Cpk_Fe` در Values. این مقادیر درصدی ممکن است در دیتاست به شکل 91.37 (نه 0.9137) ذخیره شده باشند؛ قبل از قالب‌بندی Percentage مقیاس را بررسی کنید.

## ۵. Slicer، داشبورد و اتصال گزارش‌ها
- PivotTable Analyze → Insert Slicer: `PlantArea`, `Material`, `Shift`, `Parameter`؛ Insert Timeline برای تاریخ.
- هر Slicer → Report Connections / PivotTable Connections و تمام Pivotهای قابل‌اشتراک را تیک بزنید. Factهای جدا (ردیفی/ماهانه) ممکن است با یک Slicer قابل اتصال نباشند؛ داشبورد را به دو بلوک جدا تقسیم کنید.
- صفحه `Dashboard`: بالای صفحه 4 کارت (انطباق، OOS، تعداد نمونه، TAT)، پایین آن روند زمانی، مقایسه شیفت و جدول موارد خارج از مشخصات قرار دهید. عنوان، واحد، محدوده تاریخ و زمان آخرین Refresh را درج کنید.
- از رنگ‌های ثابت سبز/زرد/قرمز و Conditional Formatting استفاده کنید؛ نمودار سه‌بعدی و تعداد زیاد Slicer را کنار بگذارید.

## ۶. رفرش و کنترل کیفیت
Data → Refresh All؛ Query Properties → Refresh data when opening the file (در صورت مجاز بودن) و Refresh every … minutes برای منبعی که واقعاً به‌روز می‌شود. فایل محلی Excel «لحظه‌ای» نیست مگر منبع و زمان‌بندی refresh چنین باشند. قبل از انتشار تعداد رکوردها، تاریخ آخرین نتیجه، واحدها، Spec و پایداری KPI را کنترل کنید.

## محدودیت و ارجاع
Excel Data Model جایگزین RLS سازمانی Power BI نیست؛ برای دسترسی ردیفی حساس، کنترل مجوز فایل/منبع و گزارش سرویس لازم است. تحلیل اختلاف شیفت‌ها را با [ANOVA/Kruskal در Python](PYTHON_TUTORIAL.md) یا [Minitab](MINITAB_TUTORIAL.md) تکمیل کنید. تعریف قابلیت Cp/Cpk و محدودیت‌های آن در متن فصل و آموزش‌های آماری شرح داده شده است.
