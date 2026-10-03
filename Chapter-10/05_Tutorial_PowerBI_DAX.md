# Tutorial 05 — Power BI & DAX: Machine-Vision Pelletizing Quality & Condition-Based Maintenance
**Dataset:** `data/Chapter10_MachineVision_Pelletizing_Dataset.xlsx`

## 1. Get Data & Transform
1. **Home ▸ Get Data ▸ Excel workbook** → select the dataset.
2. In Navigator, select all sheets except `data_dictionary` → **Transform Data** (opens Power Query).
3. Per query: promote headers (auto), set types:
   - `timestamp` / `sampling_timestamp` / `inspection_date` → **Date/Time** (or **Date** for liner).
   - `disc_id`, `process_state`, `special_cause_annotation`, `classification_label`, `operator`, `part_sample_id`, `roi_zone_id`, `liner_material`, `maintenance_recommendation`, `calibration_valid_flag` → **Text**.
   - Add column **Custom Column** in `size_distribution_hourly`:
     `fraction_check = [pct_fines_under9mm] + [pct_normal_9_16mm] + [pct_oversize_over16mm]`
   - Add column **Custom Column** `quality_flag`:
     `if [fraction_check] < 99.9 or [fraction_check] > 100.1 then "CHECK" else "OK"`
   - Add **Date** and **Hour** columns: `Date.ToText(Date.From([timestamp]),"yyyy-MM-dd")` and `Time.Hour([timestamp])`.
4. **Home ▸ Close & Apply**.

## 2. Star Schema Data Model
Open **Model view** and build:

**Fact tables (fact = event grain):**
- `Fact_Hourly` (size_distribution_hourly) — grain: 1 hour × 1 disc
- `Fact_Pellets` (pellet_features_sample) — grain: 1 pellet
- `Fact_Liner` (liner_roi_weekly) — grain: week × zone
- `Fact_Validation` (validation_lab_vs_vision)
- `Fact_GageRR` (gage_rr_study)

**Dimensions:** create with **Table view ▸ New Table** (DAX):
```dax
Dim_Date =
ADDCOLUMNS(
    CALENDAR(DATE(2024,1,1), DATE(2024,12,31)),
    "Year", YEAR([Date]),
    "Month", FORMAT([Date], "YYYY-MM"),
    "MonthNum", MONTH([Date]),
    "Week", WEEKNUM([Date]),
    "Weekday", FORMAT([Date], "ddd")
)
Dim_Disc = DISTINCT(VALUES(Fact_Hourly[disc_id]))
Dim_Hour = SELECTCOLUMNS(GENERATESERIES(0,23,1), "Hour", [Value])
Dim_Zone = DISTINCT(VALUES(Fact_Liner[roi_zone_id]))
Dim_Material = DISTINCT(VALUES(Fact_Liner[liner_material]))
```

**Relationships (1 → many, single direction):**
| From (1) | To (*) |
|---|---|
| Dim_Date[Date] | Fact_Hourly[date_key] (add in PQ), Fact_Validation[date_key], Fact_Liner[inspection_date] |
| Dim_Disc[disc_id] | Fact_Hourly[disc_id] |
| Dim_Hour[Hour] | Fact_Hourly[hour] |
| Dim_Zone[roi_zone_id] | Fact_Liner[roi_zone_id] |
| Dim_Material[liner_material] | Fact_Liner[liner_material] |

`Fact_Pellets` is a factless detail table (no date) — relate via `frame_id` only if a frame dimension exists; otherwise leave standalone with slicers.
Best practice: hide all foreign keys (right-click ▸ Hide in report view); keep only dimension attributes and measures visible.

## 3. Explicit DAX Measures (create in a `_Measures` table: **Enter data** → one empty column)

### Core size-quality measures
```dax
d50 Mean = AVERAGE(Fact_Hourly[d50_mm])
d10 Mean = AVERAGE(Fact_Hourly[d10_mm])
d90 Mean = AVERAGE(Fact_Hourly[d90_mm])
Granulometric Span = DIVIDE([d90 Mean] - [d10 Mean], [d50 Mean])

% Fines = AVERAGE(Fact_Hourly[pct_fines_under9mm])
% Normal 9-16 = AVERAGE(Fact_Hourly[pct_normal_9_16mm])
% Oversize = AVERAGE(Fact_Hourly[pct_oversize_over16mm])
```

### SPC control limits (I-chart, d2 = 1.128)
```dax
d50 Prev Hour =
VAR t = MAX(Fact_Hourly[timestamp])
RETURN CALCULATE([d50 Mean], REMOVEFILTERS(), Fact_Hourly[timestamp] = t - TIME(1,0,0))

d50 MR =
ABS([d50 Mean] - [d50 Prev Hour])

MR Bar =
AVERAGEX(
    SUMMARIZE(Fact_Hourly, Fact_Hourly[timestamp]),
    VAR t = Fact_Hourly[timestamp]
    VAR cur = CALCULATE([d50 Mean])
    VAR prev = CALCULATE([d50 Mean], Fact_Hourly[timestamp] = t - TIME(1,0,0))
    RETURN IF(ISBLANK(prev), BLANK(), ABS(cur - prev))
)

d50 Sigma = DIVIDE([MR Bar], 1.128)
d50 CL = CALCULATE([d50 Mean], REMOVEFILTERS(Fact_Hourly[timestamp]))
d50 UCL = [d50 CL] + 3 * [d50 Sigma]
d50 LCL = [d50 CL] - 3 * [d50 Sigma]

Out of Control Hours =
SUMX(
    SUMMARIZE(Fact_Hourly, Fact_Hourly[timestamp]),
    VAR v = CALCULATE([d50 Mean])
    RETURN IF(v > [d50 UCL] || v < [d50 LCL], 1, 0)
)
```

### Process capability (spec 9–16 mm)
```dax
d50 Sigma All = STDEV.P(Fact_Hourly[d50_mm])
Cp = DIVIDE(16 - 9, 6 * [d50 Sigma All])
Cpk = DIVIDE(
    MIN(16 - [d50 Mean], [d50 Mean] - 9),
    3 * [d50 Sigma All])
Spec Violations = 
CALCULATE(COUNTROWS(Fact_Hourly),
    Fact_Hourly[d50_mm] < 9 || Fact_Hourly[d50_mm] > 16)
```

### Vision-system health & lab calibration
```dax
Mean Circularity = AVERAGE(Fact_Hourly[avg_circularity])
Circ Drift = [Mean Circularity] - 
    CALCULATE([Mean Circularity], KEEPFILTERS(Fact_Hourly[process_state] = "In-Control"))

Calibration Error = AVERAGE(Fact_Validation[d50_absolute_error_mm])
Calibration R2 =
VAR mx = AVERAGEX(Fact_Validation, Fact_Validation[vision_raw_d50_mm])
VAR my = AVERAGEX(Fact_Validation, Fact_Validation[lab_rotap_d50_mm])
VAR sxy = SUMX(Fact_Validation, (Fact_Validation[vision_raw_d50_mm]-mx)*(Fact_Validation[lab_rotap_d50_mm]-my))
VAR sxx = SUMX(Fact_Validation, (Fact_Validation[vision_raw_d50_mm]-mx)^2)
VAR syy = SUMX(Fact_Validation, (Fact_Validation[lab_rotap_d50_mm]-my)^2)
RETURN DIVIDE(sxy^2, sxx * syy)
Calibration Status = IF([Calibration R2] >= 0.95 && [Calibration Error] <= 0.5, "VALID", "RECALIBRATE")
```

### Gage R&R
```dax
GRR Measurement Mean = AVERAGE(Fact_GageRR[vision_measured_d50_mm])
GRR Reference Mean = AVERAGE(Fact_GageRR[part_reference_d50_mm])
GRR Repeatability Sigma =
AVERAGEX(
    SUMMARIZE(Fact_GageRR, Fact_GageRR[part_sample_id], Fact_GageRR[operator]),
    STDEV.P(Fact_GageRR[vision_measured_d50_mm])
) ^ 0 * STDEV.P(           -- simple pooled within-cell proxy:
    CALCULATE(STDEV.P(Fact_GageRR[vision_measured_d50_mm])))
GRR %Tolerance =
DIVIDE(6 * [GRR Repeatability Sigma], 7) * 100   -- tolerance = 16 - 9 = 7 mm
```
*(For production, compute the full crossed ANOVA in R/Python/Minitab and load the results table instead of replicating ANOVA in DAX.)*

### CBM — liner degradation & remaining useful life (core of this chapter)
```dax
Corrosion Now =
CALCULATE(AVERAGE(Fact_Liner[corrosion_rust_area_ratio_pct]),
    Fact_Liner[inspection_week] = MAX(Fact_Liner[inspection_week]))

Degradation Velocity =
AVERAGE(Fact_Liner[degradation_velocity_pct_per_week])

Redness a* = AVERAGE(Fact_Liner[mean_redness_a_star_Lab])
Seg IoU = AVERAGE(Fact_Liner[segmentation_IoU])
Seg Dice = AVERAGE(Fact_Liner[segmentation_Dice])

-- Linear RUL: weeks until corrosion crosses the 20% replacement threshold
Remaining Useful Life (weeks) =
VAR thr = 20
VAR cur = [Corrosion Now]
VAR vel = [Degradation Velocity]
RETURN IF(vel <= 0, BLANK(), DIVIDE(thr - cur, vel))

-- CBM alert chain
CBM Status =
SWITCH(TRUE(),
    [Corrosion Now] >= 15 || [Remaining Useful Life (weeks)] <= 4, "CRITICAL",
    [Corrosion Now] >= 8  || [Remaining Useful Life (weeks)] <= 8, "WARNING",
    "MONITOR")

Segmentation Trust = IF([Seg IoU] >= 0.85, "TRUST", "RESEGMENT")
```

## 4. Report Page Layouts

### Page 1 — Process Quality Overview (1600×900)
- Top: 5 KPI cards — `d50 Mean`, `Cpk`, `% Oversize`, `Out of Control Hours`, `Calibration Status`.
- Center-left: **Line chart** X = `Dim_Date[Date]`, Y = `d50 Mean`, plus constants `d50 UCL/LCL` — the I-chart.
- Center-right: **Stacked area chart** X = Date, Y = `% Fines`, `% Normal 9-16`, `% Oversize`.
- Bottom-left: **Scatter** X = `ambient_dust_index`, Y = `d50_mm`, size = `pellet_count_per_frame`, legend = `disc_id`.
- Bottom-right: **Matrix** rows = `special_cause_annotation`, values = count of hours (Pareto; sort descending).
- Slicers: `Dim_Disc[disc_id]`, `Dim_Hour[Hour]`, `Dim_Date[Month]`.

### Page 2 — Vision System Health
- KPI cards: `Mean Circularity`, `Calibration R2`, `Calibration Error`, `Calibration Status` (conditional format green/red).
- **Column chart** `exposure_time_us` daily average with constant line at 350 (band 200–500 via "Constant line" in analytics pane).
- **Table** validation samples: `sample_id`, lab vs vision calibrated d50, error, `calibration_valid_flag`, conditional formatting databars on error.

### Page 3 — CBM Liner Degradation (alerts)
- KPI cards: `Corrosion Now`, `Degradation Velocity`, `Remaining Useful Life (weeks)`, `CBM Status`.
- **Line chart** X = `inspection_week`, Y = `corrosion_rust_area_ratio_pct`, legend = `Dim_Zone`, constant line at 20%.
- **Matrix** rows = `roi_zone_id` → values: corrosion, velocity, RUL, `CBM Status`, `Seg IoU`; background color by CBM Status (red/amber/green).
- **Card** `CBM Status` formatted with conditional formatting rule: CRITICAL = red fill.
- Drill-through page "Zone Detail": RUL trend, redness `a*` trend, recommendation table.

## 5. CBM Degradation Alerts

1. **Visual-level alert (Power BI Service):** pin the `CBM Status` card to a dashboard → **Pin tile ▸ Customize** → tile alert when value equals "CRITICAL" (use a numeric mirror measure):
   ```dax
   CBM Alert Code =
   SWITCH([CBM Status], "CRITICAL", 2, "WARNING", 1, 0)
   ```
   Set dashboard alert: *Alert when value ≥ 2*.
2. **Data alerts via email:** Power BI Service ▸ dashboard tile ▸ bell icon ▸ set threshold + recipients.
3. **Power Automate flow:** trigger on data-driven alert → Teams/Email message to maintenance planner with zone ID, RUL, and `maintenance_recommendation`.
4. **Escalation logic (DAX):**
   ```dax
   Maintenance Action =
   IF([CBM Status] = "CRITICAL",
      "Schedule liner replacement within " & ROUND([Remaining Useful Life (weeks)],1) & " weeks",
      IF([CBM Status] = "WARNING", "Increase inspection frequency to weekly", "Routine monitoring"))
   ```
5. **Governance:** refresh the semantic model daily at 06:00 (Service ▸ Semantic model ▸ Scheduled refresh); keep alert thresholds (corrosion 15%, RUL 4 weeks) in a `Settings` table so they are editable without editing measures.

## 6. QA Checklist Before Publishing
- [ ] Star schema: all relationships single-direction, dimension PKs unique
- [ ] All measures explicit (no implicit aggregations in visuals)
- [ ] `fraction_check` = OK on ≥99% rows (add a card: `Rows CHECK = CALCULATE(COUNTROWS(Fact_Hourly), Fact_Hourly[quality_flag]="CHECK")`)
- [ ] Cpk card shows value in [0, 2]; investigate > 2 or < 1
- [ ] Calibration Status = VALID with R² ≥ 0.95
- [ ] CBM alert tested end-to-end (threshold → dashboard alert → email)
- [ ] Publish: File ▸ Publish → workspace `Pelletizing-QC`
