# Tutorial 03 — Minitab: Gage R&R, Control Charts, Nelson Rules & Regression
**Dataset:** `data/Chapter10_MachineVision_Pelletizing_Dataset.xlsx`

## 0. Import the Data
1. **File ▸ Open ▸ Worksheet…** → change file type to *Excel (*.xlsx)* → open the dataset.
2. Minitab creates one worksheet per Excel sheet. Rename them: right-click worksheet tab ▸ Rename (e.g., `Hourly`, `Pellets`, `Liner`, `Validation`, `GRR`).
3. For the tutorial, activate the `GRR` worksheet for §1 and `Hourly` for §2–§4.

---

## 1. Gage R&R (Crossed, ANOVA Method) — `GRR` sheet
Columns: `part_sample_id` (C1-T), `operator` (C2-T), `replicate` (C3), `vision_measured_d50_mm` (C4), `part_reference_d50_mm` (C5).

### Menu path
**Stat ▸ Quality Tools ▸ Gage Study ▸ Gage R&R Study (Crossed)…**

Dialog settings:
- **Part numbers:** `part_sample_id`
- **Operators:** `operator`
- **Measurement data:** `vision_measured_d50_mm`
- **Method of Analysis:** ● ANOVA
- **Options…** ▸ Study variation: `6` (default σ multiplier); Process tolerance: ▸ *Upper spec − Lower spec* = **16 − 9 = 7 mm** (from the size spec 9–16 mm); Alpha to remove interaction term = 0.05; Tick **Display confidence intervals**.

### Equivalent session commands
```
GageRR;
  Parts   'part_sample_id';
  Ops     'operator';
  Response 'vision_measured_d50_mm';
  ANOVA;
  Tolerance 7;
  ConfLevel 95;
  GageName "Vision d50 System";
  Report 1.
```
(Type `RTM` or use **Editor ▸ Command Line** to enable session commands.)

### Interpreting the output (what you should see & how to read it)
1. **%Contribution and %Study Var (%GRR):**
   - %Study Var (Total Gage R&R) = 6·σ_GRR / 7 mm × 100.
   - **< 10%** → measurement system acceptable; **10–30%** → may be acceptable based on criticality/cost; **> 30%** → unacceptable.
2. **Repeatability (Equipment variation):** driven by segmentation noise (edge pixels on dusty frames). If %Study Var for Repeatability dominates, tighten `exposure_time_us` and lighting.
3. **Reproducibility (Appraiser variation):** check the **R chart by operator** and the **“X̄ by operator”** panel — parallel lines = no operator bias; different slopes/offsets = Operator_B (shift tech) may outline fewer boundary pellets than Operator_A (expert).
4. **ANOVA table:** Two-way ANOVA without interaction (Minitab pools the Part×Operator term if its p > 0.05 at α = 0.05).
   - Part p-value < 0.05 is *desired* (parts truly differ).
   - Operator p-value < 0.05 is *not desired* (operator bias).
5. **Number of Distinct Categories (ndc):** must be **≥ 5**. ndc = 1.41 × (7 / σ_GRR).
6. **%Tolerance vs %Process:** %Tolerance compares against spec (7 mm); %Process Var compares against actual part variation — report both.
7. **Action:** if %GRR > 30%, retrain the outlining SOP, fix illumination, and re-run the study after recalibration (see Excel tutorial §5).

### Type 1 Gage (bias/linearity check) — optional
**Stat ▸ Quality Tools ▸ Gage Study ▸ Type 1 Gage Study** using `part_reference_d50_mm` as the reference for a master part:
```
Type1Gage 'vision_measured_d50_mm';
  Reference 10.5;
  Tolerance 7.
```
Accept: |bias| ≤ 10% of tolerance, Cg/Cgk ≥ 1.33.

---

## 2. I-MR Chart on d50 — `Hourly` sheet

### Menu path
**Stat ▸ Control Charts ▸ Variables Charts for Individuals ▸ I-MR…**

Dialog:
- **Variables:** `d50_mm`
- **Scale ▸ Stamp:** `timestamp`
- **I-MR Options… ▸ Estimate:** ● *Average moving range*, length = 2; uncheck *use Barletts/normal* defaults as needed.
- **I-MR Options… ▸ Tests:** ● *Perform all tests for special causes* (Nelson rules 1–8).
- **I-MR Options… ▸ Limits:** optionally estimate σ from an in-control baseline only (e.g., first 200 rows where `process_state = "In-Control"`): use **Options ▸ Estimate ▸ Omit** or `stamp` subsetting.

### Session commands
```
IMRChart 'd50_mm';
  Stamp 'timestamp';
  MRLength 2;
  Test 1 2 3 4 5 6 7 8;
  Sigma 'Average moving range';
  Label "d50 Individuals & Moving Range".
```

### Interpretation
- **I chart:** CL = x̄ of d50; UCL/LCL = x̄ ± 2.66·MR̄ (2.66 = 3/d2, d2 = 1.128 for MR length 2). Watch for shifts after dust storms (`ambient_dust_index` spikes) — compare with the stamp axis.
- **MR chart:** CL = MR̄ = 1.128σ̂; UCL = 3.267·MR̄. Points above UCL = hour-to-hour jitter (air-knife pulsing, disc speed changes).

## 3. Nelson Rules (the 8 tests Minitab runs)
| # | Rule | Detects |
|---|---|---|
| 1 | 1 point > 3σ from CL | Gross shift / special cause |
| 2 | 9 points in a row same side of CL | Sustained mean shift |
| 3 | 6 points in a row steadily ↑ or ↓ | Trend (liner wear, disc pan build-up) |
| 4 | 14 points alternating up/down | Over-adjustment / oscillation |
| 5 | 2 of 3 points > 2σ (same side) | Small persistent shift |
| 6 | 4 of 5 points > 1σ (same side) | Small persistent shift |
| 7 | 15 points within 1σ of CL | Stratification / mixture (rule-out bad subgrouping) |
| 8 | 8 points in a row > 1σ (either side) | Mixture of two populations (e.g., two discs merged) |

When a test fails, Minitab marks the point red and prints the test number in the Session window. Cross-reference failed points with `special_cause_annotation` — this is your ground-truth validation of chart sensitivity.

## 4. Complementary Charts
- **p-chart for oversize fraction:** **Stat ▸ Control Charts ▸ Attribute Charts ▸ P…**, Variables `pct_oversize_over16mm` converted to counts (or use **Laney P′** if overdispersed — check with the P chart diagnostic).
- **EWMA/CUSUM** for small shifts: **Stat ▸ Control Charts ▸ Time Weighted ▸ EWMA** (weight 0.2) / **CUSUM** (h=4, k=0.5) on `d50_MA` equivalents.

---

## 5. Linear Regression — does dust drive size drift?

### Menu path
**Stat ▸ Regression ▸ Regression ▸ Fit Regression Model…**

- **Responses:** `d50_mm`
- **Continuous predictors:** `ambient_dust_index`, `air_knife_pressure_bar`, `exposure_time_us`
- **Categorical predictors:** `disc_id`
- **Model…:** add `ambient_dust_index*air_knife_pressure_bar` interaction; set degrees for dust to 2 (curvature).
- **Graphs…:** Four-in-one residuals; residual vs order.
- **Results…:** tick *Include expanded table*.

### Session commands
```
Regression 'd50_mm';
  Predictors 'ambient_dust_index' 'air_knife_pressure_bar' 'exposure_time_us' 'disc_id';
  Model 'ambient_dust_index' 'air_knife_pressure_bar' 'exposure_time_us' 'disc_id'
        'ambient_dust_index'*'air_knife_pressure_bar';
  RSmandE;
  Fits;
  DW.
```

### Interpretation checklist
1. **R²(adj):** model utility for the hourly size drift.
2. **Coefficients:** sign of `ambient_dust_index` — positive ⇒ dust thickens apparent edges → biased segmentation (visual particle mis-sizing), not a physical change.
3. **p-values (α = 0.05):** keep only significant predictors; compare AICc across nested models (**Results ▸ Model selection**).
4. **VIF > 5:** collinearity (exposure vs dust often correlated with shift schedule) — drop one predictor or standardize.
5. **Residual four-in-one:** normality (Anderson–Darling p > 0.05), no funnel in *Versus Fits*, no pattern in *Versus Order* (if patterned → use time-series terms or EWMA on residuals).
6. **Prediction:** **Stat ▸ Regression ▸ Regression ▸ Predict…** — predict d50 at dust index = 60 vs 20 to quantify the vision bias.

## 6. Packaging Results
1. Right-click each graph ▸ **Copy** → paste into `Minitab_Report.docx` (use **Edit ▸ Copy Graph**, not the whole pane).
2. **File ▸ Save Project As…** `Chapter10_Minitab_Analysis.mpj` + **File ▸ Save Current Worksheet As…** `Chapter10_Minitab_Analysis.mpx`.
3. Export the Gage R&R report: right-click the Gage R&R graph ▸ Save As → `gage_rr_report.png`.
