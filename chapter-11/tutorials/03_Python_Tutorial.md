# خط لوله پیش‌بینی توزیعی و مدل‌سازی ریسک با Python

این اسکریپت یک Pipeline آموزشی برای:

1. پاکسازی داده؛
2. پیش‌بینی `CCS_mean`؛
3. پیش‌بینی `CCS_std`؛
4. محاسبه `P10` و `P(CCS < LSL)` تحت فرض Normal؛
5. مدل‌سازی `Has_BlackCore`؛
6. تحلیل اهمیت متغیرها با SHAP

ارائه می‌کند.

> **نکته روش‌شناختی:** این یک مدل توزیعی آموزشی است. پیش‌بینی جداگانه `μ` و `σ` و سپس استفاده از Normal distribution فقط در صورتی معتبر است که توزیع شرطی CCS و کالیبراسیون ریسک در داده واقعی قابل قبول باشند.

---

# 1. نصب کتابخانه‌ها

```bash
pip install pandas numpy scipy scikit-learn matplotlib shap openpyxl
```

---

# 2. بارگذاری داده

```python
import numpy as np
import pandas as pd

from scipy.stats import norm

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

import matplotlib.pyplot as plt
```

```python
FILE_PATH = "../data/ch11_ccs_blackcore_training_dataset.xlsx"

shift = pd.read_excel(
    FILE_PATH,
    sheet_name="Shift_Data"
)

pellet = pd.read_excel(
    FILE_PATH,
    sheet_name="Pellet_CCS"
)

print("Shift rows:", len(shift))
print("Pellet rows:", len(pellet))
```

---

# 3. پاکسازی رژیم فرایندی

```python
df = shift.copy()

df = df.loc[
    df["Process_Stability"].eq("Stable")
].copy()
```

رکوردهای ناپایدار حذف فیزیکی نمی‌شوند؛ برای تحلیل جداگانه باید نگهداری شوند.

---

# 4. تعریف predictors

```python
features = [
    "TFe",
    "FeO",
    "SiO2",
    "Al2O3",
    "CaO",
    "MgO",
    "LOI",
    "Moisture",
    "Bentonite_pct",
    "Lime_pct",
    "Gangue_SiAl",
    "Basicity_B2",
    "Basicity_B4",
    "T_preheat_avg",
    "T_firing_avg",
    "T_firing_peak",
    "TimeAbove1200_min",
    "TimeAbove1250_min",
    "HeatingRate_C_min",
    "CoolingRate_C_min",
    "Temp_Uniformity_Std",
    "O2_avg_pct",
]

missing_features = [
    c for c in features
    if c not in df.columns
]

if missing_features:
    raise ValueError(
        f"Missing feature columns: {missing_features}"
    )
```

---

# 5. تعریف Targetها

```python
required_targets = [
    "CCS_mean",
    "CCS_std",
]

missing_targets = [
    c for c in required_targets
    if c not in df.columns
]

if missing_targets:
    raise ValueError(
        f"Missing target columns: {missing_targets}"
    )

df["CCS_std"] = pd.to_numeric(
    df["CCS_std"],
    errors="coerce"
)

df["CCS_mean"] = pd.to_numeric(
    df["CCS_mean"],
    errors="coerce"
)

df = df[
    df["CCS_mean"].notna()
    & df["CCS_std"].gt(0)
].copy()

X = df[features].copy()

y_mu = df["CCS_mean"].copy()

y_log_sigma = np.log(
    df["CCS_std"].clip(lower=1e-3)
)
```

---

# 6. تقسیم آموزش و آزمون

برای اینکه مدل μ و σ دقیقاً روی نمونه‌های یکسان آموزش و آزمون شوند، split فقط یک بار انجام می‌شود.

```python
(
    X_train,
    X_test,
    ymu_train,
    ymu_test,
    yls_train,
    yls_test,
) = train_test_split(
    X,
    y_mu,
    y_log_sigma,
    test_size=0.20,
    random_state=42,
)
```

> اگر داده‌ها چند رکورد برای هر `Lot_ID` دارند، تقسیم تصادفی ساده می‌تواند باعث leakage بین train و test شود. در چنین شرایطی باید از Group Split بر اساس `Lot_ID` استفاده شود.

---

# 7. Preprocessing

```python
preprocessor = ColumnTransformer(
    transformers=[
        (
            "num",
            SimpleImputer(strategy="median"),
            features,
        )
    ],
    remainder="drop",
)
```

استفاده از Pipeline باعث می‌شود preprocessing به‌صورت منظم همراه مدل اجرا شود. در scikit-learn، Pipeline برای زنجیره‌کردن transformerها و estimator استفاده می‌شود.

---

# 8. مدل پیش‌بینی μ

```python
model_mu = Pipeline(
    steps=[
        ("prep", preprocessor),
        (
            "rf",
            RandomForestRegressor(
                n_estimators=300,
                random_state=42,
                n_jobs=-1,
            ),
        ),
    ]
)

model_mu.fit(
    X_train,
    ymu_train,
)

mu_pred = model_mu.predict(
    X_test
)
```

---

# 9. مدل پیش‌بینی σ

به‌جای پیش‌بینی مستقیم `σ`، لگاریتم آن پیش‌بینی می‌شود تا خروجی مثبت بماند.

```python
model_sigma = Pipeline(
    steps=[
        ("prep", preprocessor),
        (
            "rf",
            RandomForestRegressor(
                n_estimators=300,
                random_state=42,
                n_jobs=-1,
            ),
        ),
    ]
)

model_sigma.fit(
    X_train,
    yls_train,
)

log_sigma_pred = model_sigma.predict(
    X_test
)

sigma_pred = np.exp(
    log_sigma_pred
)

sigma_pred = np.maximum(
    sigma_pred,
    1e-6,
)
```

---

# 10. ارزیابی مدل μ

```python
mae_mu = mean_absolute_error(
    ymu_test,
    mu_pred,
)

rmse_mu = np.sqrt(
    mean_squared_error(
        ymu_test,
        mu_pred,
    )
)

r2_mu = r2_score(
    ymu_test,
    mu_pred,
)

print(
    f"MAE (CCS mean): {mae_mu:.2f} N"
)

print(
    f"RMSE (CCS mean): {rmse_mu:.2f} N"
)

print(
    f"R2 (CCS mean): {r2_mu:.3f}"
)
```

---

# 11. برآورد ریسک زیر LSL

در این مثال آموزشی:

```python
LSL = 2000.0
```

است.

این مقدار **حد مشخصات آموزشی** است و نباید به‌عنوان حد عمومی ISO تلقی شود. ISO 4700:2015 روش آزمون crushing strength را تعریف می‌کند.

اگر فرض Normal قابل قبول باشد:

```python
prob_risk = norm.cdf(
    LSL,
    loc=mu_pred,
    scale=sigma_pred,
)
```

---

# 12. محاسبه P10

```python
p10_pred = norm.ppf(
    0.10,
    loc=mu_pred,
    scale=sigma_pred,
)
```

و جدول خروجی:

```python
results_df = X_test.copy()

results_df["CCS_mean_pred"] = mu_pred

results_df["CCS_std_pred"] = sigma_pred

results_df["Predicted_P10"] = p10_pred

results_df["Risk_P_below_LSL"] = prob_risk

results_df["Risk_Flag"] = np.where(
    results_df["Risk_P_below_LSL"] > 0.05,
    "Investigate",
    "Monitor",
)

print(
    results_df[
        [
            "CCS_mean_pred",
            "CCS_std_pred",
            "Predicted_P10",
            "Risk_P_below_LSL",
            "Risk_Flag",
        ]
    ].head()
)
```

`5%` در اینجا آستانه آموزشی است و باید در پروژه واقعی با Loss Function و الزامات محصول کالیبره شود.

---

# 13. تحلیل Black Core

ابتدا باید مشخص کنیم که `Has_BlackCore` در سطح Pellet موجود است.

```python
required_blackcore_columns = [
    "Has_BlackCore",
    "Lot_ID",
]

missing_blackcore = [
    c for c in required_blackcore_columns
    if c not in pellet.columns
]

if missing_blackcore:
    raise ValueError(
        f"Missing Black Core columns: {missing_blackcore}"
    )
```

برای ساخت جدول مدل، predictors مربوط به Lot را از `Shift_Data` به داده تک‌گندله‌ای متصل می‌کنیم:

```python
lot_features = (
    shift[
        ["Lot_ID"]
        + [
            c for c in [
                "FeO",
                "O2_avg_pct",
                "TimeAbove1200_min",
                "T_firing_peak",
                "Basicity_B2",
                "Temp_Uniformity_Std",
            ]
            if c in shift.columns
        ]
    ]
    .drop_duplicates("Lot_ID")
)

blackcore_df = pellet.merge(
    lot_features,
    on="Lot_ID",
    how="left",
)

blackcore_df = blackcore_df[
    blackcore_df["Has_BlackCore"].isin([0, 1])
].copy()
```

---

# 14. مدل Random Forest برای Black Core

```python
black_features = [
    c for c in [
        "Pellet_Size_mm",
        "FeO",
        "O2_avg_pct",
        "TimeAbove1200_min",
        "T_firing_peak",
        "Basicity_B2",
        "Temp_Uniformity_Std",
    ]
    if c in blackcore_df.columns
]

X_black = blackcore_df[black_features].copy()

y_black = (
    blackcore_df["Has_BlackCore"]
    .astype(int)
)

Xb_train, Xb_test, yb_train, yb_test = train_test_split(
    X_black,
    y_black,
    test_size=0.20,
    random_state=42,
    stratify=y_black,
)

black_preprocessor = ColumnTransformer(
    transformers=[
        (
            "num",
            SimpleImputer(strategy="median"),
            black_features,
        )
    ],
    remainder="drop",
)

model_black = Pipeline(
    steps=[
        ("prep", black_preprocessor),
        (
            "rf",
            RandomForestClassifier(
                n_estimators=300,
                random_state=42,
                class_weight="balanced",
                n_jobs=-1,
            ),
        ),
    ]
)

model_black.fit(
    Xb_train,
    yb_train,
)

black_prob = model_black.predict_proba(
    Xb_test
)[:, 1]

black_pred = (
    black_prob >= 0.50
).astype(int)
```

---

# 15. ارزیابی مدل Black Core

```python
if yb_test.nunique() == 2:
    auc = roc_auc_score(
        yb_test,
        black_prob,
    )

    print(
        f"Black Core ROC-AUC: {auc:.3f}"
    )
else:
    print(
        "ROC-AUC cannot be calculated: "
        "test set contains only one class."
    )
```

آستانه `0.50` نیز یک انتخاب آموزشی است و در کاربرد عملی باید بر اساس هزینه False Positive و False Negative تنظیم شود.

---

# 16. SHAP برای مدل μ

`preprocessor` مستقل را نباید برای SHAP استفاده کرد، زیرا نسخه fit‌شده آن داخل Pipeline قرار دارد.

نسخه صحیح:

```python
import shap

prep_mu = model_mu.named_steps["prep"]

rf_mu = model_mu.named_steps["rf"]

X_test_trans = prep_mu.transform(
    X_test
)

feature_names = (
    prep_mu
    .get_feature_names_out()
)

explainer = shap.TreeExplainer(
    rf_mu
)

shap_values = explainer.shap_values(
    X_test_trans
)

shap.summary_plot(
    shap_values,
    X_test_trans,
    feature_names=feature_names,
)
```

این روش، داده‌ای را که واقعاً به Random Forest داده شده است با همان فضای ویژگی تحلیل می‌کند. Pipeline در scikit-learn preprocessing و predictor را به‌صورت یک زنجیره مدل نگه می‌دارد.

---

# 17. کنترل فرض توزیع

قبل از استفاده عملی از:

```python
norm.cdf(...)
```

و:

```python
norm.ppf(...)
```

باید توزیع واقعی `CCS_N` بررسی شود.

در صورت رد Normal:

```text
Normal
   ↓
Alternative distribution
   ↓
Refit / Calibration
   ↓
P10
   ↓
P(CCS < LSL)
```

نباید صرفاً برای راحتی محاسبات، Normal انتخاب شود.

---

# 18. تفسیر نهایی

مدل این فصل باید به این شکل تفسیر شود:

```text
Model Signal
     ↓
Statistical Evidence
     ↓
Process Verification
     ↓
Metallurgical Interpretation
     ↓
Physical Inspection
     ↓
Corrective Action
```

بنابراین:

```text
Predicted CCS Risk ≠ Guaranteed Product Failure
```

و:

```text
Black Core Probability ≠ Proven Root Cause
```

👉 [بازگشت به فهرست آموزش‌ها](../README.md)
