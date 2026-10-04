# Tutorial 04 — Building the Chapter 15 Dashboard in Power BI

Dataset: `chapter15_clqc_training_data.xlsx` (7 sheets, 240 samples at
15-min intervals).

## 1. Get data
1. **Home > Get Data > Excel workbook** -> select
   `chapter15_clqc_training_data.xlsx`.
2. Load sheets `01_Process_Data`, `02_MSPC_Monitoring`,
   `03_Control_Loop_Log`, `04_Data_Validation`.
3. In Power Query, set the `timestamp` column type to **Date/Time** and the
   numeric columns to **Decimal Number**.

## 2. Data model
- Create a Date table (`CALENDAR(MIN(timestamp), MAX(timestamp))`) and relate
  it to `timestamp` on each fact table (1:*).
- Mark the date table as the official date table for time intelligence.

## 3. Key DAX measures
```DAX
Sulfur Mean = AVERAGE('01_Process_Data'[soft_sensor_sulfur_pct])

EWMA =
VAR lambda = 0.2
RETURN
    SUMX(
        FILTER('01_Process_Data',
            '01_Process_Data'[timestamp] <= MAX('01_Process_Data'[timestamp])),
        0) * 0 -- placeholder: use a calculated column instead

-- Recommended: compute EWMA and T2/Q as calculated columns in Power Query/DAX:
EWMA_col =
VAR lam = 0.2
VAR prev =
    CALCULATE(MAX([ewma_running]),
        FILTER('01_Process_Data', [timestamp] < EARLIER([timestamp])))
RETURN IF(ISBLANK(prev), [soft_sensor_sulfur_pct],
          lam*[soft_sensor_sulfur_pct] + (1-lam)*prev)
```
Simpler approach: import the precomputed `ewma_stat`, `T2_stat`, `Q_stat`
columns from sheet `02_MSPC_Monitoring` and add limit measures:
```DAX
T2 UCL = MAX('02_MSPC_Monitoring'[T2_UCL])
Alarm Rate % =
DIVIDE(CALCULATE(COUNTROWS('02_MSPC_Monitoring'), '02_MSPC_Monitoring'[T2_stat] > '02_MSPC_Monitoring'[T2_UCL]),
       COUNTROWS('02_MSPC_Monitoring'))
```

## 4. Visuals
1. **Line chart**: timestamp vs soft-sensor sulfur + lab sulfur (markers only)
   — shows the 120-min dead time visually.
2. **Line chart** of EWMA with a constant line at `mu0 + L*sigma*sqrt(lam/(2-lam))`.
3. **Scatter/line** of T2 and Q statistics with UCL constant lines; use
   conditional formatting to color out-of-control points red.
4. **KPI cards**: current sulfur, alarm rate %, delay Td, % lab coverage.
5. **Table** from `03_Control_Loop_Log` for the closed-loop action history.
6. Slicer on `data_source` (LIMS_lab / SoftSensor_online).

## 5. Publishing
- Save as `chapter15_clqc_dashboard.pbix`.
- Publish to Power BI Service and set a **scheduled refresh** if the Excel
  file lives on OneDrive/SharePoint.
