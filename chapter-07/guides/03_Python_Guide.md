# راهنمای پیاده‌سازی EWMA، CUSUM و تحلیل Lag در Python

> **فایل داده:** [`Process_Data_Chapter7_EWMA_CUSUM.xlsx`](../Process_Data_Chapter7_EWMA_CUSUM.xlsx)

---

# ۱. نصب کتابخانه‌ها

```bash
pip install pandas numpy matplotlib statsmodels openpyxl
```

---

# ۲. بارگذاری داده

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from statsmodels.graphics.tsaplots import plot_acf


FILE_PATH = "../Process_Data_Chapter7_EWMA_CUSUM.xlsx"

df = pd.read_excel(
    FILE_PATH,
    sheet_name="Data"
)

required_columns = [
    "P80_Micron",
    "FeO_Percent",
    "BurnerZoneTemp_C",
    "O2_Percent",
    "SpecificPower_kWht",
    "ReturnLoad_th",
    "FeedHardness_Index",
    "FeedRate_th",
]

missing = [
    col for col in required_columns
    if col not in df.columns
]

if missing:
    raise ValueError(
        f"Missing columns: {missing}"
    )

print(df.head())
print(df[required_columns].describe())
```

---

# ۳. تابع EWMA

```python
def calculate_ewma(
    data,
    lam=0.20,
    mu0=75.0,
    sigma0=2.0,
    L=3.0
):
    data = np.asarray(data, dtype=float)

    n = len(data)

    z = np.zeros(n)
    ucl = np.zeros(n)
    lcl = np.zeros(n)

    z_prev = mu0

    for t in range(n):
        z[t] = (
            lam * data[t]
            + (1 - lam) * z_prev
        )

        z_prev = z[t]

        time_index = t + 1

        variance_factor = (
            lam / (2 - lam)
        ) * (
            1 - (1 - lam) ** (2 * time_index)
        )

        ewma_sigma = sigma0 * np.sqrt(
            variance_factor
        )

        ucl[t] = mu0 + L * ewma_sigma
        lcl[t] = mu0 - L * ewma_sigma

    return z, ucl, lcl
```

---

# ۴. تابع CUSUM

```python
def calculate_cusum(
    data,
    mu0=1.50,
    sigma0=0.08,
    k=0.25,
    h=5.0
):
    data = np.asarray(data, dtype=float)

    y = (
        data - mu0
    ) / sigma0

    n = len(data)

    c_plus = np.zeros(n)
    c_minus = np.zeros(n)

    for t in range(1, n):
        c_plus[t] = max(
            0.0,
            c_plus[t - 1] + y[t] - k
        )

        c_minus[t] = max(
            0.0,
            c_minus[t - 1] - y[t] - k
        )

    alarm_plus = c_plus >= h
    alarm_minus = c_minus >= h

    return (
        c_plus,
        c_minus,
        alarm_plus,
        alarm_minus
    )
```

---

# ۵. اجرای EWMA

```python
z_p80, ucl_p80, lcl_p80 = calculate_ewma(
    df["P80_Micron"].values,
    lam=0.20,
    mu0=75.0,
    sigma0=2.0,
    L=3.0
)
```

---

# ۶. اجرای CUSUM

```python
(
    cusum_plus,
    cusum_minus,
    alarm_plus,
    alarm_minus
) = calculate_cusum(
    df["FeO_Percent"].values,
    mu0=1.50,
    sigma0=0.08,
    k=0.25,
    h=5.0
)
```

---

# ۷. پیدا کردن اولین سیگنال

```python
plus_indices = np.where(alarm_plus)[0]
minus_indices = np.where(alarm_minus)[0]

if len(plus_indices) > 0:
    print(
        "First positive CUSUM signal:",
        plus_indices[0] + 1
    )
else:
    print("No positive CUSUM signal.")

if len(minus_indices) > 0:
    print(
        "First negative CUSUM signal:",
        minus_indices[0] + 1
    )
else:
    print("No negative CUSUM signal.")
```

---

# ۸. تحلیل Lag مشعل و FeO

برای بررسی Lagهای مختلف:

```python
max_lag = 14

lag_results = []

for lag in range(max_lag + 1):

    shifted_temp = (
        df["BurnerZoneTemp_C"]
        .shift(lag)
    )

    correlation = (
        shifted_temp
        .corr(df["FeO_Percent"])
    )

    lag_results.append({
        "Lag_Hours": lag,
        "Correlation": correlation
    })

lag_df = pd.DataFrame(lag_results)

print(lag_df)
```

برای پیدا کردن بیشترین قدر مطلق correlation:

```python
valid_lags = lag_df.dropna(
    subset=["Correlation"]
)

best_row = valid_lags.loc[
    valid_lags["Correlation"].abs().idxmax()
]

print(
    "Lag with maximum absolute correlation:",
    int(best_row["Lag_Hours"])
)

print(
    "Correlation:",
    best_row["Correlation"]
)
```

> این مقدار فقط Lag دارای بیشترین همبستگی در محدوده بررسی‌شده است و به‌تنهایی اثبات‌کننده رابطه علّی نیست.

---

# ۹. بررسی خودهمبستگی P80

```python
fig, ax = plt.subplots(
    figsize=(10, 5)
)

plot_acf(
    df["P80_Micron"].dropna(),
    lags=30,
    ax=ax
)

ax.set_title(
    "ACF of P80_Micron"
)

plt.tight_layout()
plt.show()
```

اگر خودهمبستگی قابل توجه باشد، فرض استقلال مشاهدات برای برخی روش‌های ساده SPC ممکن است مناسب نباشد.

در این شرایط می‌توان مدل زمانی مناسب‌تری ایجاد کرد و residualها را برای پایش SPC بررسی کرد.

---

# ۱۰. نمودار EWMA

```python
fig, ax = plt.subplots(
    figsize=(12, 6)
)

ax.plot(
    df["P80_Micron"],
    linewidth=1,
    alpha=0.5,
    label="P80"
)

ax.plot(
    z_p80,
    linewidth=2,
    label="EWMA"
)

ax.plot(
    ucl_p80,
    linestyle="--",
    label="UCL"
)

ax.plot(
    lcl_p80,
    linestyle="--",
    label="LCL"
)

ax.axvline(
    99,
    linestyle=":",
    label="Phase I / Phase II"
)

ax.set_title(
    "P80 EWMA Control Chart"
)

ax.set_xlabel(
    "Observation"
)

ax.set_ylabel(
    "P80 (µm)"
)

ax.grid(
    True,
    alpha=0.3
)

ax.legend()

plt.tight_layout()
plt.show()
```

---

# ۱۱. نمودار CUSUM

```python
fig, ax = plt.subplots(
    figsize=(12, 6)
)

ax.plot(
    cusum_plus,
    linewidth=2,
    label="CUSUM+"
)

ax.plot(
    cusum_minus,
    linewidth=2,
    label="CUSUM-"
)

ax.axhline(
    5.0,
    linestyle="--",
    label="H = 5"
)

ax.axvline(
    99,
    linestyle=":",
    label="Phase I / Phase II"
)

ax.set_title(
    "FeO CUSUM Control Chart"
)

ax.set_xlabel(
    "Observation"
)

ax.set_ylabel(
    "CUSUM"
)

ax.grid(
    True,
    alpha=0.3
)

ax.legend()

plt.tight_layout()
plt.show()
```

---

# ۱۲. تحلیل هم‌زمان شواهد

پس از مشاهده یک سیگنال SPC، می‌توان متغیرهای زیر را بررسی کرد:

```python
diagnostic_columns = [
    "P80_Micron",
    "SpecificPower_kWht",
    "ReturnLoad_th",
    "FeedHardness_Index",
    "FeedRate_th",
]

print(
    df[diagnostic_columns]
    .tail(30)
    .describe()
)
```

هدف این مرحله، **تشخیص شواهد سازگار با یک فرضیه فیزیکی** است؛ نه تبدیل خودکار سیگنال آماری به علت قطعی.

---

# ۱۳. اصل مهم

فرآیند تحلیل باید به شکل زیر باشد:

**SPC Signal → Temporal Verification → Process Evidence → Physical Inspection → Root Cause**

بنابراین:

`CUSUM Alarm ≠ Burner Failure`

و:

`EWMA Alarm ≠ Liner Failure`

این نمودارها ابزار تشخیص تغییر آماری هستند؛ تشخیص علت نیازمند شواهد فرآیندی و مهندسی مکمل است.
