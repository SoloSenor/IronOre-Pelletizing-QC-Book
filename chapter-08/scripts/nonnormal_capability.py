# -*- coding: utf-8 -*-
"""
Chapter 8: Non-Normal Process Capability Analysis for Iron Ore Pellets (CCS & Porosity)
Author: Amin - Quality Control Department
Reference: ISO 4700 / Montgomery SQC
"""

import os
import numpy as np
import pandas as pd
from scipy import stats

def load_data(file_path):
    df_long = pd.read_excel(file_path, sheet_name="data_long")
    df_100 = pd.read_excel(file_path, sheet_name="chapter8_ccs_100")
    df_specs = pd.read_excel(file_path, sheet_name="specs")
    return df_long, df_100, df_specs

def descriptive_analysis(data, col_name="CCS_kg"):
    x = data[col_name].dropna().values
    n = len(x)
    mean_val = np.mean(x)
    std_val = np.std(x, ddof=1)
    median_val = np.median(x)
    skew_val = stats.skew(x, bias=False)
    kurt_excess = stats.kurtosis(x, fisher=True, bias=False)

    print("=" * 55)
    print(f"DESCRIPTIVE STATISTICS FOR: {col_name}")
    print("=" * 55)
    print(f"Sample Size (n)   : {n}")
    print(f"Mean              : {mean_val:.3f}")
    print(f"Std Deviation (s) : {std_val:.3f}")
    print(f"Median            : {median_val:.3f}")
    print(f"Skewness          : {skew_val:.3f}")
    print(f"Excess Kurtosis   : {kurt_excess:.3f} (Standard Kurtosis = {kurt_excess + 3:.3f})")

    ad_res = stats.anderson(x, dist="norm")
    print(f"Anderson-Darling  : A2 = {ad_res.statistic:.3f}")
    print(f"Normal Reject (5%): {ad_res.statistic > ad_res.critical_values[2]}")

    return {
        "n": n, "mean": mean_val, "std": std_val, "median": median_val,
        "skewness": skew_val, "kurtosis": kurt_excess, "ad_stat": ad_res.statistic
    }

def capability_normal_unilateral(mean_val, std_val, lsl):
    cpl = (mean_val - lsl) / (3.0 * std_val)
    theo_defect_rate = stats.norm.cdf(lsl, loc=mean_val, scale=std_val)
    return cpl, theo_defect_rate

def boxcox_capability(x, lsl):
    x_clean = x[~np.isnan(x)]
    y, lam = stats.boxcox(x_clean)
    mean_y = np.mean(y)
    std_y = np.std(y, ddof=1)

    if abs(lam) < 1e-12:
        lsl_y = np.log(lsl)
    else:
        lsl_y = (lsl ** lam - 1.0) / lam

    cpl_bc = (mean_y - lsl_y) / (3.0 * std_y)
    theo_defect_bc = stats.norm.cdf(lsl_y, loc=mean_y, scale=std_y)

    return {
        "lambda": lam,
        "mean_y": mean_y,
        "std_y": std_y,
        "lsl_y": lsl_y,
        "cpl_boxcox": cpl_bc,
        "defect_rate_boxcox": theo_defect_bc
    }

def empirical_percentiles_capability(x, lsl):
    x_clean = x[~np.isnan(x)]
    m = np.median(x_clean)
    p_00135 = np.percentile(x_clean, 0.135)
    cpl_emp = (m - lsl) / (m - p_00135)
    observed_defect = np.mean(x_clean < lsl)
    return cpl_emp, observed_defect

def weibull_capability(x, lsl):
    x_clean = x[~np.isnan(x)]
    shape, loc, scale = stats.weibull_min.fit(x_clean, floc=0)
    p_below_lsl = stats.weibull_min.cdf(lsl, shape, loc=loc, scale=scale)
    equivalent_z = stats.norm.ppf(1.0 - p_below_lsl)
    cpl_weibull = equivalent_z / 3.0
    return {
        "shape": shape, "scale": scale,
        "p_below_lsl": p_below_lsl,
        "cpl_equivalent": cpl_weibull
    }

if __name__ == "__main__":
    excel_path = "../data/Chapter08_Pellet_Nonnormal_Capability_Dataset.xlsx"
    if not os.path.exists(excel_path):
        excel_path = "data/Chapter08_Pellet_Nonnormal_Capability_Dataset.xlsx"

    df_long, df_100, df_specs = load_data(excel_path)
    ccs_data = df_100["CCS_kg"].values
    LSL = 250.0

    stats_summary = descriptive_analysis(df_100, "CCS_kg")
    cpl_norm, theo_def = capability_normal_unilateral(stats_summary["mean"], stats_summary["std"], LSL)
    obs_def = np.mean(ccs_data < LSL)

    print("-" * 55)
    print("CAPABILITY EVALUATION COMPARISON")
    print("-" * 55)
    print(f"Normal Cpl Assumption : {cpl_norm:.4f}")
    print(f"Normal Expected Defect: {theo_def * 100:.2f}% ({theo_def * 1e6:.0f} PPM)")
    print(f"Observed Sample Defect: {obs_def * 100:.2f}% ({obs_def * 1e6:.0f} PPM)")

    bc_res = boxcox_capability(ccs_data, LSL)
    print(f"Box-Cox Lambda (MLE)  : {bc_res['lambda']:.4f}")
    print(f"Box-Cox Cpl           : {bc_res['cpl_boxcox']:.4f}")
    print(f"Box-Cox Defect Rate   : {bc_res['defect_rate_boxcox'] * 100:.2f}%")

    wb_res = weibull_capability(ccs_data, LSL)
    print(f"Weibull Fit Defect    : {wb_res['p_below_lsl'] * 100:.2f}%")
    print(f"Weibull Eq. Cpl       : {wb_res['cpl_equivalent']:.4f}")
    print("=" * 55)
