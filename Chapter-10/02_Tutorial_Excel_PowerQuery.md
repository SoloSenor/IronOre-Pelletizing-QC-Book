# Tutorial 02 — Excel & Power Query: Machine-Vision Pelletizing QC Workbook

**Dataset:** `data/Chapter10_MachineVision_Pelletizing_Dataset.xlsx`
**Sheets:** `data_dictionary`, `size_distribution_hourly`, `pellet_features_sample`, `liner_roi_weekly`, `validation_lab_vs_vision`, `gage_rr_study`

---

## 1. Load and Shape the Data with Power Query

### 1.1 Import (Data → Get Data → From File → From Workbook)
1. Open a blank workbook. **Data ▸ Get Data ▸ From File ▸ From Workbook**.
2. Select `Chapter10_MachineVision_Pelletizing_Dataset.xlsx`.
3. In Navigator, tick all six sheets (select each, click **Transform Data**, they accumulate in the Queries pane).

### 1.2 Clean `size_distribution_hourly` (M code)

Open **Advanced Editor** and paste:

```m
let
    Source      = Excel.Workbook(File.Contents("C:\QC\Chapter10_MachineVision_Pelletizing_Dataset.xlsx"), null, true),
    sz_Sheet    = Source{[Item="size_distribution_hourly", Kind="Sheet"]}[Data],
    Promoted    = Table.PromoteHeaders(sz_Sheet, [PromoteAllScalars=true]),
    Typed       = Table.TransformColumnTypes(Promoted, {
        {"timestamp", type datetime},
        {"disc_id", type text},
        {"exposure_time_us", Int64.Type},
        {"air_knife_pressure_bar", type number},
        {"ambient_dust_index", type number},
        {"d10_mm", type number}, {"d50_mm", type number}, {"d90_mm", type number},
        {"pct_fines_under9mm", type number},
        {"pct_normal_9_16mm", type number},
        {"pct_oversize_over16mm", type number},
        {"pellet_count_per_frame", Int64.Type},
        {"avg_circularity", type number},
        {"process_state", type text},
        {"special_cause_annotation", type text}
    }),
    // Consistency check: the three size fractions must sum to 100
    AddCheck    = Table.AddColumn(Typed, "fraction_check",
        each Number.Round([pct_fines_under9mm]+[pct_normal_9_16mm]+[pct_oversize_over16mm],1),
        type number),
    AddFlag     = Table.AddColumn(AddCheck, "data_flag",
        each if [fraction_check] < 99.9 or [fraction_check] > 100.1 then "CHECK" else "OK",
        type text),
    AddMonth    = Table.AddColumn(AddFlag, "month", each Date.Month([timestamp]), Int64.Type),
    AddHour     = Table.AddColumn(AddMonth, "hour", each Date.Hour([timestamp]), Int64.Type),
    // 24-row rolling average of d50 (sort first!)
    Sorted      = Table.Sort(AddHour, {{"timestamp", Order.Ascending}}),
    Buffered    = Table.Buffer(Sorted),
    D50_MA24    = List.Accumulate({0..Table.RowCount(Buffered)-1}, {}, (acc,i) =>
                    acc & {Number.Round(List.Average(
                        List.LastN(List.FirstN(Buffered[d50_mm], i+1), 24)), 3)}),
    AddMA       = Table.FromColumns(Table.ToColumns(Buffered) & {D50_MA24},
                    Table.ColumnNames(Buffered) & {"d50_MA24"}),
    Renamed     = Table.RenameColumns(AddMA, {{"data_flag","Data Quality Flag"}})
in
    Renamed
```

### 1.3 Clean `pellet_features_sample`

```m
let
    Source   = Excel.Workbook(File.Contents("C:\QC\Chapter10_MachineVision_Pelletizing_Dataset.xlsx"), null, true),
    pf       = Source{[Item="pellet_features_sample", Kind="Sheet"]}[Data],
    Promoted = Table.PromoteHeaders(pf, [PromoteAllScalars=true]),
    Typed    = Table.TransformColumnTypes(Promoted, {
        {"pellet_id", type text}, {"frame_id", type text},
        {"area_mm2", type number}, {"perimeter_mm", type number},
        {"equivalent_diameter_Deq_mm", type number},
        {"feret_max_mm", type number}, {"feret_min_mm", type number},
        {"circularity", type number},
        {"classification_label", type text},
        {"segmentation_anomaly_flag", Int64.Type}
    }),
    // Circularity consistency: C = 4πA / P²  (≈1 for a perfect circle)
    AddCalcC = Table.AddColumn(Typed, "circularity_calc",
        each Number.Round(4*Number.PI*[area_mm2]/Number.Power([perimeter_mm],2),3), type number),
    AddDiff  = Table.AddColumn(AddCalcC, "circ_diff",
        each Number.Abs([circularity]-[circularity_calc]), type number),
    Filter   = Table.SelectRows(AddDiff, each [circ_diff] < 0.05 and [segmentation_anomaly_flag] = 0),
    AddElon  = Table.AddColumn(Filter, "elongation_ratio",
        each Number.Round([feret_max_mm]/[feret_min_mm],3), type number)
in
    AddElon
```

### 1.4 Merge lab validation against the hourly feed (relationship in M)

```m
let
    Source  = Excel.Workbook(File.Contents("C:\QC\Chapter10_MachineVision_Pelletizing_Dataset.xlsx"), null, true),
    val     = Table.PromoteHeaders(Source{[Item="validation_lab_vs_vision", Kind="Sheet"]}[Data], true),
    Typed   = Table.TransformColumnTypes(val, {{"sampling_timestamp", type datetime}}),
    // Round to the hour so we can join to size_distribution_hourly
    Hr      = Table.AddColumn(Typed, "hour_key", each DateTime.Date([sampling_timestamp]) & #time(Time.Hour([sampling_timestamp]),0,0), type datetime),
    Merged  = Table.NestedJoin(Hr, {"hour_key"}, sz_typed, {"timestamp"}, "HourRow", JoinKind.LeftOuter),
    Exp     = Table.ExpandTableColumn(Merged, "HourRow", {"disc_id","ambient_dust_index"}, {"disc_id","dust_index"})
in
    Exp
```
*(`sz_typed` = the typed query from §1.2; reference it via right-click ▸ Reference.)*

**Close & Load To…** ▸ Only Create Connection + add to Data Model (needed for pivot tables/DAX-free modeling).

---

## 2. Excel Formulas (Analysis sheet)

Assume hourly data lands in `Hourly` (table name `tblHourly`) starting A1.

| Purpose | Formula |
|---|---|
| Mean d50 | `=AVERAGE(tblHourly[d50_mm])` |
| Std dev d50 | `=STDEV.S(tblHourly[d50_mm])` |
| Control limits (I-chart) | `CL: =AVERAGE(tblHourly[d50_mm])` `UCL: =CL+2.66*MR_bar` `LCL: =CL-2.66*MR_bar` |
| Moving range | `=ABS(D3-D2)` (fill down), `MR_bar: =AVERAGE(MR range starting row 3)` |
| Cp (spec 9–16 mm) | `= (16-9)/(6*STDEV.S(tblHourly[d50_mm]))` |
| Cpk | `= MIN(16-d50bar, d50bar-9)/(3*STDEV.S(tblHourly[d50_mm]))` |
| % fines trend (7-day) | `=SLOPE(tblHourly[pct_fines_under9mm], tblHourly[timestamp])` (positive slope ⇒ degrading size control) |
| Out-of-spec count/day | `=COUNTIFS(tblHourly[timestamp],">="&A2,tblHourly[timestamp],"<"&A3,tblHourly[pct_oversize_over16mm],">5")` |
| Pelt count correlation w/ dust | `=CORREL(tblHourly[pellet_count_per_frame], tblHourly[ambient_dust_index])` |
| Granulometric span | `=(d90-d10)/d50` → `=( [@[d90_mm]]-[@[d10_mm]] )/[@[d50_mm]]` |
| Calibrated d50 (linear lab model) | `=FORECAST.LINEAR([@lab_rotap_d50_mm], [@vision_raw_d50_mm], ...)` — see §5 |
| Gage R&R σ_repeatability | `=STDEV.S(range of (measured − part mean) per operator)` |
| Reproducibility σ | `=STDEV.S( operator means per part ) / SQRT(operators)` |

**Named cells:** create `Spec_LSL = 9`, `Spec_USL = 16`, `Target_d50 = 12.5` on a `Settings` sheet — formulas referencing names are self-documenting.

---

## 3. Conditional Formatting Rules

Select the `pct_oversize_over16mm` column in the Excel table:

1. **Rule 1 — Oversize alarm:** Highlight Cells ▸ Greater Than ▸ `5` → red fill.
2. **Rule 2 — Warning:** Between `4` and `5` → amber fill (put above Rule 1, check *Stop If True* off).
3. **Rule 3 — Formula rule on whole rows** (Apply to `=$A$2:$O$2001`):
   `=$M2="Special Cause"` (process_state) → purple border + light purple fill.
4. **Rule 4 — Circularity drift:** on `avg_circularity`: Formula `=OR($M2<0.85,$M2>0.97)` → blue fill (segmentation/exposure suspect).
5. **Rule 5 — 3-color scale** on `d50_mm`: min `9`, midpoint (percentile 50) `12.5`, max `16`.
6. **Rule 6 — Data bars** on `degradation_velocity_pct_per_week` in `liner_roi_weekly`.
7. **Rule 7 — Icon set** on `calibration_valid_flag` in the validation sheet: PASS = green check, FAIL = red cross (use formula `=$K2="FAIL"` → red fill, first rule).

**Camera-health dashboard rule:** on `exposure_time_us` — Formula `=OR($C2<200,$C2>500)` → orange (exposure drift = blurred frames ⇒ bad segmentation).

---

## 4. Pivot Tables

**PT1 — Size distribution by disc and state**
Rows: `disc_id`, `process_state`; Values: Average of `d50_mm`, Average of `pct_fines_under9mm`, Count of `timestamp`. Format values to 2 decimals. Insert slicer on `month` and `hour`.

**PT2 — Special-cause Pareto**
Rows: `special_cause_annotation`; Values: Count. Sort descending; add a running % column: `=SUM($B$2:B2)/SUM($B:$B)` in an adjacent cell.

**PT3 — Hourly pattern (shift diagnostics)**
Rows: `hour`; Values: Average `d50_mm`, Average `ambient_dust_index`. Shows whether dust load at shift change drives oversize.

**PT4 — Liner degradation**
From `liner_roi_weekly`: Rows `inspection_week`, Columns `roi_zone_id`, Values Sum/Avg `corrosion_rust_area_ratio_pct`. Insert **PivotChart (Line)** → wear curves per zone.

**PT5 — Gage R&R summary**
From `gage_rr_study`: Rows `part_sample_id`, Columns `operator`, Values Average `vision_measured_d50_mm`. Compute cell-by-cell (measured − reference) in a helper pivot or GETPIVOTDATA formulas for the ANOVA check in §6.

**PT6 — Calibration performance**
From `validation_lab_vs_vision`: Rows `calibration_valid_flag`; Values Count + Average `d50_absolute_error_mm`. Target: ≥95% PASS, mean error < 0.5 mm.

---

## 5. Vision-System Calibration Workflow

1. **Regression model (lab → vision):** on the validation sheet compute
   `slope: =SLOPE(lab_rotap_d50_mm, vision_raw_d50_mm)`, `intercept: =INTERCEPT(...)`, `R²: =RSQ(...)`.
   New calibrated value: `= slope*vision_raw + intercept`.
2. **Acceptance criteria:** R² ≥ 0.95, mean |error| ≤ 0.5 mm, PASS rate ≥ 95%.
3. **Daily verification:** every shift, log one Rotap sample; if `d50_absolute_error_mm > 0.5` flag the hour in Power Query (conditional column) and trigger recalibration.
4. **Recalibrate when:** drift in `exposure_time_us` > 10% of nominal, `avg_circularity` baseline shifts, or R² falls below 0.95.
5. Track calibration validity over time with PT6 and the icon-set rule from §3.

---

## 6. Verify the Gage R&R in Excel (cross-check to Minitab)

With 10 parts × 3 operators × 2 replicates, use two-way ANOVA without interaction (Minitab default for crossed Gage R&R) — approximate in Excel via **Data ▸ Data Analysis ▸ Anova: Two-Factor Without Replication** on the pivot from PT5:
- MS_Repeatability = MS Within → σ_E = √MS_E
- MS_Operator → reproducibility component = max(0,(MS_Op − MS_E)/n_reps)
- %GRR = 6·√(σ²_E + σ²_R&R) / (Tolerance = 16 − 9) × 100
- Rule: %GRR < 10% acceptable; 10–30% conditionally; > 30% reject.
- **ndc** = 1.41 · (Tolerance / σ_GRR) — must be ≥ 5.

---

## 7. Deliverables Checklist
- [ ] All 6 sheets loaded, typed, and loaded to the Data Model
- [ ] Fraction-sum check column shows "OK" for ≥99% of rows
- [ ] Conditional formatting: 7 rules active
- [ ] 6 pivot tables + 2 slicers
- [ ] Calibration regression R² documented on `Settings`
- [ ] Workbook saved as `Chapter10_Excel_Tutorial_Completed.xlsx`
