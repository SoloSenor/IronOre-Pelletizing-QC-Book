# آموزش عملیاتی Power BI برای داشبوردهای QC فصل ۱۴

> داده آموزشی: `QC_Ch13_Ch14_Synthetic_Dataset.xlsx` (در همین پوشه). پیش‌زمینه: [متن فصل ۱۴](CHAPTER_14_TEXT.md).
> سایر مسیرها: [Excel Power Pivot](EXCEL_POWER_PIVOT_TUTORIAL.md) | [Python](PYTHON_TUTORIAL.md) | [Minitab](MINITAB_TUTORIAL.md)

## ۱. اتصال داده و Power Query
1. Power BI Desktop → **Get Data → Excel** → شیت‌های `Fact_QC_Result`، `Fact_Process_Tag`، `Fact_Monthly_KPI` و تمام شیت‌های `Dim_*` را وارد کنید.
2. در **Transform Data (Power Query)**:
   - نوع داده ستون‌های زمانی (`SampleDateTime`, `ReceiveDateTime`, `ResultDateTime`, `IngestionDateTime`) را `Date/Time` و `IsConform` را `Whole Number` کنید.
   - ستون `Value` را `Decimal` و ستون‌های ID را `Text` کنید.
   - رکوردهایی با `DataQualityFlag <> "OK"` را حذف نکنید؛ به جدول جداگانه برای پایش کیفیت داده ببرید.
3. یک جدول تقویم بسازید: `Dim_DateTime` موجود است؛ در Power Query کپی یکتای `ShiftKey` بگیرید و به‌عنوان Date dimension استفاده کنید (**Mark as Date Table** روی ستون `Date`).

## ۲. مدل ستاره‌ای و روابط
مدل را یک‌به‌چند از ابعاد به Fact ببندید (هر دو ستون Text):

| رابطه | از (Dimension) | به (Fact) | کاردینالیتی |
|---|---|---|---|
| 1 | `Dim_DateTime[ShiftKey]` | `Fact_QC_Result[ShiftKey]` | Many-to-One |
| 2 | `Dim_Shift[ShiftID]` | `Fact_QC_Result[Shift]` | Many-to-One |
| 3 | `Dim_PlantArea[PlantAreaID]` | `Fact_QC_Result[PlantAreaID]` | Many-to-One |
| 4 | `Dim_Material[MaterialID]` | `Fact_QC_Result[MaterialID]` | Many-to-One |
| 5 | `Dim_TestType[TestTypeID]` | `Fact_QC_Result[TestTypeID]` | Many-to-One |
| 6 | `Dim_Operator[OperatorID]` | `Fact_QC_Result[OperatorID]` | Many-to-One |
| 7 | `Dim_DateTime[ShiftKey]` | `Fact_Process_Tag[ShiftKey]` | Many-to-One |
| 8 | `Dim_Parameter[Parameter]` | `Fact_QC_Result[Parameter]` | Many-to-One |
| 9 | `Dim_KPI_Target[KPI]` | (در برچسب‌های کارت استفاده می‌شود) | بدون رابطه مستقیم |

قواعد کلیدی:
- دو `Fact` هرگز مستقیماً به هم وصل نشوند؛ ارتباط از طریق ابعاد مشترک انجام می‌شود.
- جهت فیلتر را یک‌طرفه نگه دارید؛ در صورت نیاز به فیلتر معکوس فقط با توجیه از `Both` استفاده کنید.
- رابطه `Dim_Parameter` به `Fact_QC_Result` چندبه‌چند نیست چون `Parameter` در ابعاد یکتاست.

## ۳. Measureهای DAX (کپی‌آماده)

```DAX
-- شمارش و انطباق
Total Results   = COUNTROWS ( Fact_QC_Result )
OOS Results     = CALCULATE ( COUNTROWS ( Fact_QC_Result ), Fact_QC_Result[IsConform] = 0 )
Conformance %   = DIVIDE ( [Total Results] - [OOS Results], [Total Results], 0 )
OOS %           = 1 - [Conformance %]

-- آماره‌های مقدار
Avg Value       = AVERAGE ( Fact_QC_Result[Value] )
StdDev Value    = STDEV.S ( Fact_QC_Result[Value] )
Median Value    = MEDIAN ( Fact_QC_Result[Value] )
P95 Value       = PERCENTILEX.INC ( Fact_QC_Result, Fact_QC_Result[Value], 0.95 )

-- TAT آزمایشگاه (دقیقه)
TAT Avg (min)   = AVERAGEX ( Fact_QC_Result,
                    DATEDIFF ( Fact_QC_Result[SampleDateTime], Fact_QC_Result[ResultDateTime], MINUTE ) )

-- تازگی داده (Freshness) بر مبنای آخرین ورود معتبر
Last Ingestion  = CALCULATE ( MAX ( Fact_QC_Result[IngestionDateTime] ), Fact_QC_Result[DataQualityFlag] = "OK" )
Data Age (min)  = DATEDIFF ( [Last Ingestion], NOW (), MINUTE )
Freshness Flag  = IF ( [Data Age (min)] <= 120, "OK", "STALE" )

-- تازه‌سازی ماهانه برای نمای استراتژیک
MoM Conformance Δ =
VAR Cur = [Conformance %]
VAR Prev = CALCULATE ( [Conformance %], DATEADD ( Dim_DateTime[Date], -1, MONTH ) )
RETURN Cur - Prev
```

دسته‌بندی OOS نسبت به Spec (برای پارتو و مسیر اقدام):

```DAX
OOS Direction =
VAR v = MAX ( Fact_QC_Result[Value] )
VAR p = SELECTEDVALUE ( Dim_Parameter[Parameter] )
RETURN
IF ( NOT ISBLANK ( SELECTEDVALUE ( Fact_QC_Result[SampleID] ) ),
    SWITCH ( TRUE (),
        v < LOOKUPVALUE ( Dim_Parameter[LSL], Dim_Parameter[Parameter], p ), "Low",
        v > LOOKUPVALUE ( Dim_Parameter[USL], Dim_Parameter[Parameter], p ), "High",
        "In-Spec" ) )
```

## ۴. صفحه Operational (عملیاتی)
- **کارت‌ها:** `Avg Value`، `OOS %`، `TAT Avg`، `Data Age` با قالب‌بندی شرطی (سبز ≤ حد، قرمز تخلف).
- **نمودار خطی:** `Value` در برابر `SampleDateTime` برای پارامتر انتخابی + خطوط ثابت `LSL`/`USL` (از `Dim_Parameter`) و `Target`.
- **جدول هشدار:** آخرین نتایج ناهمخوان با ستون‌های Parameter, Value, LSL, USL, SampleDateTime و `OOS Direction`؛ اتصال به `Dim_ActionRule[SuggestedAction]` با LOOKUPVALUE.
- **Slicer:** PlantArea, Line, Parameter, Shift — حداکثر ۴ slicer؛ بقیه به Drill-through منتقل شود.
- **Drill-through:** صفحه «جزئیات نمونه» با فیلد `SampleID`؛ کلیک راست روی هر نقطه → جزئیات رکورد، آزمون، اپراتور، Batch.

## ۵. صفحه Tactical (مقایسه شیفت‌ها)
- **Box and Whisker** (visual بازار یا Boxplotwhisker chart) برای `Value` برحسب `Dim_Shift[ShiftName]` به تفکیک `Dim_Parameter[Parameter]`.
- ماتریس: ردیف = Shift، ستون = Parameter، مقدار = `Avg Value` و `OOS %` (دو Measure کنار هم).
- حداقل حجم نمونه را نمایش دهید تا مقایسه گمراه‌کننده نباشد:
```DAX
Sample Size = COUNTROWS ( Fact_QC_Result )
Small Sample Warn = IF ( [Sample Size] < 30, "⚠ نمونه کم", "" )
```
- برای اثبات معناداری تفاوت شیفت‌ها به [PYTHON_TUTORIAL.md](PYTHON_TUTORIAL.md) (ANOVA/Kruskal) و [MINITAB_TUTORIAL.md](MINITAB_TUTORIAL.md) ارجاع دهید؛ تفاوت میانگین به‌تنهایی کافی نیست.

## ۶. صفحه Strategic (استراتژیک)
- جدول `Fact_Monthly_KPI`: نمودار خطی `ConformancePct` و `Cpk_Fe` در برابر `YearMonth`، همراه با خطوط هدف از `Dim_KPI_Target`.
- **Pareto OOS:** Bar chart تعداد `OOS_Count` به تفکیک Parameter + Measure تجمعی:
```DAX
OOS Cumulative % =
VAR t = ADDCOLUMNS ( ALLSELECTED ( Dim_Parameter[Parameter] ), "@oos", [OOS Results] )
VAR cur = [OOS Results]
RETURN DIVIDE ( cur, SUMX ( FILTER ( t, [@oos] >= cur ), [@oos] ) )
```
- KPI Cards در برابر `Dim_KPI_Target[TargetValue]` با فلش روند (`MoM Conformance Δ`).
- Cp/Cpk را در Power BI به‌صورت Measure ساده محاسبه نکنید مگر فرض نرمال و پایداری بررسی شده باشد؛ روش صحیح در [PYTHON_TUTORIAL.md](PYTHON_TUTORIAL.md) و [MINITAB_TUTORIAL.md](MINITAB_TUTORIAL.md).

## ۷. RLS (Row-Level Security)
1. Modeling → **Manage Roles** → نقش `Plant_Concentrator1`:
```DAX
-- روی Dim_PlantArea
[PlantAreaID] = 1
```
2. نقش `Lab_ReadOnly` بدون محدودیت ردیفی، فقط اجازه View.
3. Testing: Modeling → **View as** → نقش را شبیه‌سازی و نتایج را بررسی کنید.
4. در Power BI Service: Secutiry دیتاست → کاربران/گروه‌ها را به نقش اضافه کنید؛ RLS رویmemberهای Admin اثر ندارد.

## ۸. رفرش و انتشار
- Gateway: برای فایل محلی (آزمایشی) از Personal Gateway یا برای محیط واقعی On-Premises Data Gateway روی مسیر LIMS/SQL.
- Schedule refresh: روزانه 06:00 (قبل از شیفت A) + Refresh در صورت انتشار نسخه جدید Spec.
- Incremental refresh (اختیاری): RangeStart/RangeEnd روی `SampleDateTime`، پارتیشن ۱ ماهه، نگهداری ۱۳ ماه.
- خطای رفرش: هشدار ایمیل + Measure `Freshness Flag` روی صفحه عملیاتی به‌عنوان لایه دوم نظارت.

## ۹. چک‌لیست انتشار
- [ ] واحدها و روش آزمون در Tooltips مشخص است.
- [ ] مبنای زمانی (Sample/Result/Ingestion) در هر صفحه ذکر شده.
- [ ] رنگ معنایی ثابت (سبز/زرد/قرمز) در همه صفحات.
- [ ] Drill-through تا سطح SampleID کار می‌کند.
- [ ] RLS با دو نقش آزمون شده.
- [ ] پیوند به [README.md](README.md) و [متن فصل](CHAPTER_14_TEXT.md) در توضیحات گزارش.
