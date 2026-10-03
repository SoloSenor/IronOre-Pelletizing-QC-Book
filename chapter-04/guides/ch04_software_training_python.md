# اسکریپت‌های تحلیلی گندله خام در Python

> **فایل داده مرجع:** [`Green_Pellet_QC_Training_Data4.xlsx`](../Green_Pellet_QC_Training_Data4.xlsx)
> **مرجع تئوری:** [فصل ۴ — بخش‌های ۴-۴ و ۴-۶](../ch04_green_pellet_text.md)

## نصب کتابخانه‌ها

```bash
pip install pandas numpy matplotlib openpyxl scipy
```

---

## ۱. بارگذاری و کنترل اولیه داده‌ها

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit


file_path = "../Green_Pellet_QC_Training_Data4.xlsx"

df = pd.read_excel(file_path)

required_cols = [
    "Moisture_Pct",
    "Bentonite_Pct",
    "Wet_Strength_N",
    "Drop_Number",
    "Dry_Strength_N",
    "Target_Size_Pct",
    "Fines_Pct",
    "Feed_Rate_tph",
]

missing_cols = [c for c in required_cols if c not in df.columns]

if missing_cols:
    raise ValueError(f"Missing columns: {missing_cols}")

print(df[required_cols].describe())
print("\nMissing values:")
print(df[required_cols].isna().sum())
```

---

## ۲. ماتریس همبستگی پیرسون

```python
corr_cols = [
    "Moisture_Pct",
    "Bentonite_Pct",
    "Wet_Strength_N",
    "Drop_Number",
    "Dry_Strength_N",
    "Target_Size_Pct",
    "Fines_Pct",
]

corr = df[corr_cols].corr(method="pearson")

fig, ax = plt.subplots(figsize=(10, 8))

im = ax.imshow(corr.values, vmin=-1, vmax=1)

ax.set_xticks(range(len(corr.columns)))
ax.set_yticks(range(len(corr.columns)))

ax.set_xticklabels(corr.columns, rotation=45, ha="right")
ax.set_yticklabels(corr.columns)

for i in range(len(corr.columns)):
    for j in range(len(corr.columns)):
        ax.text(
            j,
            i,
            f"{corr.iloc[i, j]:.2f}",
            ha="center",
            va="center"
        )

ax.set_title("Pearson Correlation Matrix - Green Pellet QC")
fig.colorbar(im, ax=ax, label="Correlation")

plt.tight_layout()
plt.savefig("correlation_matrix.png", dpi=200)
plt.show()
```

> همبستگی فقط شدت و جهت رابطه خطی را نشان می‌دهد و به‌تنهایی بیانگر رابطه علّی نیست.

---

## ۳. بررسی پنجره آموزشی رطوبت

```python
lower_moisture = 8.5
upper_moisture = 9.1

plt.figure(figsize=(9, 5))

plt.scatter(
    df["Moisture_Pct"],
    df["Wet_Strength_N"],
    alpha=0.65
)

plt.axvline(
    lower_moisture,
    linestyle="--",
    label="Lower educational boundary"
)

plt.axvline(
    upper_moisture,
    linestyle="--",
    label="Upper educational boundary"
)

plt.xlabel("Moisture (%)")
plt.ylabel("Wet Strength (N/pellet)")
plt.title("Moisture Window vs Wet Strength")

plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()
plt.savefig("moisture_window.png", dpi=200)
plt.show()
```

این نمودار برای بررسی رفتار داده‌ها در اطراف پنجره آموزشی استفاده می‌شود و نباید به‌تنهایی برای تعیین optimum عملیاتی کارخانه استفاده شود.

---

## ۴. برازش مدل غیرخطی آموزشی

برای بررسی احتمال وجود رابطه خمیده بین رطوبت و استحکام تر می‌توان مدل درجه دوم را آزمایش کرد:

\(W = \beta_0+\beta_1M+\beta_2M^2\)

در کد، از یک تابع ساده برای برازش استفاده می‌کنیم:

```python
model_df = df[
    ["Moisture_Pct", "Wet_Strength_N"]
].dropna()

x = model_df["Moisture_Pct"].to_numpy()
y = model_df["Wet_Strength_N"].to_numpy()


def quadratic_model(x, b0, b1, b2):
    return b0 + b1 * x + b2 * x**2


params, covariance = curve_fit(
    quadratic_model,
    x,
    y
)

b0, b1, b2 = params

print("Model coefficients:")
print(f"b0 = {b0:.4f}")
print(f"b1 = {b1:.4f}")
print(f"b2 = {b2:.4f}")


x_fit = np.linspace(x.min(), x.max(), 200)
y_fit = quadratic_model(x_fit, *params)


plt.figure(figsize=(9, 5))

plt.scatter(
    x,
    y,
    alpha=0.5,
    label="Observed data"
)

plt.plot(
    x_fit,
    y_fit,
    linewidth=2,
    label="Quadratic fit"
)

plt.xlabel("Moisture (%)")
plt.ylabel("Wet Strength (N/pellet)")
plt.title("Nonlinear Educational Model")

plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()
plt.savefig("moisture_nonlinear_model.png", dpi=200)
plt.show()
```

### تفسیر مدل

اگر جمله درجه دوم معنی‌دار یا از نظر مهندسی قابل توجه باشد، ممکن است داده‌ها با یک رابطه خطی ساده به‌خوبی توصیف نشوند.

اما:

**مدل آماری ≠ مکانیزم فیزیکی**

برای تأیید پنجره عملیاتی باید مدل با داده مستقل، شرایط مختلف خوراک و آزمون‌های صنعتی اعتبارسنجی شود.

---

## ۵. بررسی داده‌های غیرعادی

```python
numeric_cols = [
    "Moisture_Pct",
    "Bentonite_Pct",
    "Wet_Strength_N",
    "Drop_Number",
    "Dry_Strength_N",
    "Target_Size_Pct",
    "Fines_Pct",
]

for col in numeric_cols:
    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)

    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outliers = df[
        (df[col] < lower) |
        (df[col] > upper)
    ]

    print(
        f"{col}: "
        f"{len(outliers)} potential statistical outliers"
    )
```

> Outlier آماری الزاماً خطای داده نیست. قبل از حذف، علت فرآیندی، شرایط عملیاتی، خرابی تجهیز یا خطای اندازه‌گیری بررسی شود.
