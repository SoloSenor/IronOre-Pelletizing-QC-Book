# راهنمای عملی فصل ۱۳ در پاور بی‌آی (Power BI)

## ۱. مدل‌سازی داده
شیت‌های `process_timeseries` (Fact)، `asset_hierarchy` و `shifts` (Dimension) و `event_log` را وارد کنید. روابط: `process_timeseries[ShiftID]` به `shifts[ShiftID]` و `event_log[AssetID]` به `asset_hierarchy[AssetID]` (چندبه‌یک).

## ۲. فرمول‌های کلیدی DAX
```dax
Avg_Clean_Moisture =
CALCULATE(
    AVERAGE(process_timeseries[DiscMoisture_PV]),
    process_timeseries[Quality_DiscMoisture] = "Good"
)
```
```dax
Downtime_Events_Count =
CALCULATE(
    COUNTROWS(event_log),
    event_log[EventType] = "DowntimeStart"
)
```
