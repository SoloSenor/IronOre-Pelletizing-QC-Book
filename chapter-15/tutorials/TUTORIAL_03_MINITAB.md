# Tutorial 03 — Building the Chapter 15 Charts in Minitab

Dataset: `chapter15_clqc_training_data.xlsx` (7 sheets). Import via
**File > Open > Worksheet** or copy/paste from Excel.

## 1. SPC chart for delayed lab measurements
1. Open sheet `01_Process_Data`.
2. **Stat > Control Charts > Variables Charts for Individuals > I-MR**.
3. Variable: `lab_sulfur_pct`. Minitab ignores missing values in individuals charts;
   for a continuous time axis use **I-MR of soft_sensor_sulfur_pct** instead.
4. Under **I-MR Options > Limits**, set the center line to the target
   (e.g., 0.20 % S) and enter spec limits if available.

## 2. EWMA chart (early-warning layer)
1. **Stat > Control Charts > Time-Weighted Charts > EWMA**.
2. Variable: `soft_sensor_sulfur_pct`; Weight of EWMA (lambda) = **0.2**.
3. Set sigma of individual observations to 0.018 (from the calibration data)
   and check the moving-range estimate box. The L=3 limits in the workbook
   correspond to the 3-sigma EWMA limits Minitab plots.

## 3. Multivariate monitoring (T^2)
1. Use sheet `02_MSPC_Monitoring`, or the 5 process variables from
   `01_Process_Data`.
2. **Stat > Multivariate > Hotelling T^2 (individuals)** — Minitab computes
   T^2, its 95 %/99 % limits, and a two-dimensional plot of T^2 vs
   sample number.
3. For the Q (SPE) statistic Minitab does not offer a native chart; import
   the precomputed `Q_stat` column and chart it with **I-MR**.

## 4. Dead-time / cross-correlation analysis
1. **Stat > Time Series > Cross Correlation** with the soft-sensor series
   and the lab series. The peak at lag +8 confirms Td = 120 min (8 x 15 min).

## 5. Regression soft-sensor check
1. **Stat > Regression > Regression > Fit Regression Model**.
2. Response: `lab_sulfur_pct` (use rows where it is present).
3. Predictors: the 5 process variables. Compare predicted values against
   `soft_sensor_sulfur_pct`; they should agree within ~1.5 sigma.

## Tips
- Always exclude the first 120 rows (calibration/in-control period) from
  phase-I limit estimation using **Data > Subset Worksheet**.
- Use **Graph > Probability Plot** to confirm near-normality before I-MR.
