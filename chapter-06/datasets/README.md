# datasets — دادهٔ آموزشی فصل ۶

فایل: **CH06_SPC_autocorr_training_data.xlsx** (برگهٔ `raw_5s`، 4320 رکورد)

این مجموعهٔ دادهٔ آموزشی (سنتتیک) برای تمرین کنترل فرآیند آماری روی داده‌های خودهمبستهٔ یک فرآیند پیوستهٔ صنعتی (شبیه‌سازی خط کنترل کیفیت گندله/پودر) تولید شده است.

## ستون‌های فایل

| ستون | توضیح |
|---|---|
| `Timestamp` | ... |
| `Elapsed_min` | ... |
| `OperatingRegime` | ... |
| `Shift` | ... |
| `MoistureSetpoint_pct` | ... |
| `FilterCakeMoisture` | ... |
| `Vacuum` | ... |
| `FeedSolids` | ... |
| `FeedPressure` | ... |
| `MotorCurrent` | ... |
| `FlowRate` | ... |
| `FurnaceTemp` | ... |
| `FilterCakeMoistureQualityFlag` | ... |
| `VacuumQualityFlag` | ... |
| `FeedSolidsQualityFlag` | ... |
| `FeedPressureQualityFlag` | ... |
| `MotorCurrentQualityFlag` | ... |
| `FlowRateQualityFlag` | ... |
| `FurnaceTempQualityFlag` | ... |
| `AnyBadQuality` | ... |

> برای دیدن کاربرد هر ستون در تحلیل، بخش مربوطه در [متن فصل ۶](../text_chapter_06.md) را ببینید.

## نکتهٔ مهم دربارهٔ خودهمبستگی

چون این داده‌ها از یک فرآیند پیوستهٔ واقع‌گرایانه شبیه‌سازی شده‌اند، مشاهدات متوالی همبستگی خودی معنادار (تقریباً AR(1) با φ حدود ۰٫۶ تا ۰٫۸) دارند. پیش از رسم هر نمودار کنترل، حتماً بخش «اثر خودهمبستگی بر حدود کنترل» در متن فصل را مطالعه کنید.

## نحوهٔ استفاده در آموزش‌ها

- [Excel](../tutorials/excel_tutorial.md)
- [Minitab](../tutorials/minitab_tutorial.md)
- [Python](../tutorials/python_tutorial.md)
- [Power BI](../tutorials/powerbi_tutorial.md)
